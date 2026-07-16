from fastapi import APIRouter, HTTPException
import traceback
import re
from datetime import datetime
from schemas import ChatRequest, ChatResponse
from ortho_clinic_data import DOCTORS, LOCATIONS
from chat_crud import (
    get_booking_context, book_appointment, cancel_appointment,
    reschedule_appointment, get_next_available, get_patient_bookings_context,
)
from chat_service import generate_claude_response

router = APIRouter()

# The demo has a single patient identity (see chat_service.py); their bookings
# and cancel/reschedule actions are all keyed to this name.
PATIENT_NAME = "Jay"

# Telugu block in Unicode. Used to decide which language the system's own
# booking confirmation should be written in, so a Telugu conversation doesn't
# end with an English receipt stapled to it.
_TELUGU_SCRIPT = re.compile(r'[ఀ-౿]')

# 5-field tag: Doctor | Location | Date | Time | Patient
_BOOK_TAG = re.compile(r'<BOOK>(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)</BOOK>')
_ANY_BOOK_TAG = re.compile(r'<BOOK>.*?</BOOK>', re.DOTALL)

# <CANCEL>Token</CANCEL>
_CANCEL_TAG = re.compile(r'<CANCEL>(.*?)</CANCEL>')
_ANY_CANCEL_TAG = re.compile(r'<CANCEL>.*?</CANCEL>', re.DOTALL)

# <RESCHEDULE>OldToken | Doctor | Location | Date | Time | Patient</RESCHEDULE>
_RESCHED_TAG = re.compile(r'<RESCHEDULE>(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)</RESCHEDULE>')
_ANY_RESCHED_TAG = re.compile(r'<RESCHEDULE>.*?</RESCHEDULE>', re.DOTALL)


def _detect_doctor(full_text: str):
    """Longest doctor-name mention in the conversation, or None."""
    text = full_text.lower()
    found = [d["name"] for d in DOCTORS if d["name"].lower() in text]
    return max(found, key=len) if found else None


def _detect_location(full_text: str):
    text = full_text.lower()
    for name in LOCATIONS:
        if name.lower() in text:
            return name
    return None


# ── confirmation / edge messages (bilingual) ──────────────────────────────────

def _confirmation_message(r: dict, in_telugu: bool) -> str:
    if in_telugu:
        return (
            f"\n\n✅ **అపాయింట్‌మెంట్ ఖరారు అయ్యింది!**"
            f"\nడాక్టర్: **{r['doctor']}** ({r['specialty']})"
            f"\nబ్రాంచ్: **{r['location']}** — {r['address']}"
            f"\nతేదీ: **{r['date']}** ({r['day_telugu']})"
            f"\nసమయం: **{r['time']}**"
            f"\nటోకెన్ నంబర్: **{r['token']}**"
            f"\n\nదయచేసి 10 నిమిషాలు ముందుగా రండి. ఏదైనా మార్పు కోసం {r['contact_person']} — {r['phone']} కు కాల్ చేయండి."
        )
    return (
        f"\n\n✅ **Appointment Confirmed!**"
        f"\nDoctor: **{r['doctor']}** ({r['specialty']})"
        f"\nBranch: **{r['location']}** — {r['address']}"
        f"\nDate: **{r['date']}** ({r['day']})"
        f"\nTime: **{r['time']}**"
        f"\nToken: **{r['token']}**"
        f"\n\nPlease arrive 10 minutes early. For any changes, call {r['contact_person']} at {r['phone']}."
    )


def _already_booked_message(r: dict, in_telugu: bool) -> str:
    if in_telugu:
        return (
            f"\n\n మీ అపాయింట్‌మెంట్ ఇప్పటికే బుక్ అయ్యింది — టోకెన్ నంబర్: **{r['token']}** "
            f"(డాక్టర్: **{r['doctor']}**, బ్రాంచ్: **{r['location']}**, తేదీ: **{r['date']}**, సమయం: **{r['time']}**)."
        )
    return (
        f"\n\n You're already booked — Token: **{r['token']}** "
        f"(Doctor: **{r['doctor']}**, Branch: **{r['location']}**, Date: **{r['date']}**, Time: **{r['time']}**)."
    )


def _sunday_message(r: dict, in_telugu: bool) -> str:
    if in_telugu:
        return ("\n\n క్షమించండి, ఆదివారం అన్ని బ్రాంచ్‌లు మూసివేయబడతాయి (అత్యవసర కేసులు మాత్రమే). "
                "దయచేసి సోమవారం–శనివారం మధ్య ఒక రోజు ఎంచుకోండి.")
    return ("\n\n Sorry — all branches are closed on Sundays (emergency cases only). "
            "Please pick a day between Monday and Saturday.")


def _unavailable_message(r: dict, in_telugu: bool) -> str:
    if in_telugu:
        return (f"\n\n క్షమించండి, **{r['doctor']}** {r['day']} రోజున **{r['location']}** బ్రాంచ్‌లో అందుబాటులో లేరు. "
                f"వారి షెడ్యూల్: {r['availability']}. దయచేసి వీటిలో ఒకటి ఎంచుకోండి.")
    return (f"\n\n Sorry — **{r['doctor']}** isn't available at **{r['location']}** on {r['day']}. "
            f"Their schedule: {r['availability']}. Please pick one of these.")


def _bad_time_message(r: dict, in_telugu: bool) -> str:
    if in_telugu:
        return (f"\n\n ఆ సమయం సరిపోలడం లేదు. **{r['doctor']}** {r['location']} లో {r['date']} ({r['day']}) రోజున "
                f"సమయం: {r['window']}. అందుబాటులో ఉన్న సమయాలు: {r['open_times']}. దయచేసి వీటిలో ఒకటి ఎంచుకోండి.")
    return (f"\n\n That time doesn't work. **{r['doctor']}** at {r['location']} on {r['date']} ({r['day']}): "
            f"{r['window']}. Open times: {r['open_times']}. Please pick one of these.")


def _slot_taken_message(r: dict, in_telugu: bool) -> str:
    if in_telugu:
        return (f"\n\n క్షమించండి, **{r['time']}** సమయం ఇప్పటికే బుక్ అయ్యింది. "
                f"అందుబాటులో ఉన్న సమయాలు: {r['open_times']}. వేరే సమయం ఎంచుకోండి.")
    return (f"\n\n Sorry — the **{r['time']}** slot is already taken. "
            f"Open times: {r['open_times']}. Please pick another.")


def _past_date_message(r: dict, in_telugu: bool) -> str:
    if in_telugu:
        return ("\n\n ఆ తేదీ గతంలో ఉంది. దయచేసి ఈరోజు లేదా తర్వాతి తేదీ (సోమవారం–శనివారం) ఎంచుకోండి.")
    return ("\n\n That date is in the past. Please pick today or a later Monday–Saturday date.")


def _cancelled_message(r: dict, in_telugu: bool) -> str:
    if in_telugu:
        return (
            f"\n\n🗑️ **అపాయింట్‌మెంట్ రద్దు చేయబడింది.**"
            f"\nటోకెన్: **{r['token']}** — {r['doctor']}, {r['location']}, {r['date']} ({r['day_telugu']}), {r['time']}."
            f"\nకొత్త అపాయింట్‌మెంట్ కావాలంటే చెప్పండి, Jay!"
        )
    return (
        f"\n\n🗑️ **Appointment Cancelled.**"
        f"\nToken: **{r['token']}** — {r['doctor']}, {r['location']}, {r['date']} ({r['day']}), {r['time']}."
        f"\nLet me know if you'd like to book a new one, Jay!"
    )


def _cancel_not_found_message(r: dict, in_telugu: bool) -> str:
    if in_telugu:
        return ("\n\n ఆ టోకెన్‌తో అపాయింట్‌మెంట్ కనబడలేదు. దయచేసి టోకెన్ నంబర్ మరోసారి చెక్ చేయండి.")
    return ("\n\n I couldn't find an appointment with that token. Please double-check the token number.")


def _rescheduled_message(r: dict, in_telugu: bool) -> str:
    old = r.get("old", {})
    if in_telugu:
        return (
            f"\n\n🔄 **అపాయింట్‌మెంట్ రీషెడ్యూల్ అయ్యింది!**"
            f"\nపాత: {old.get('date','')} {old.get('time','')} (టోకెన్ {old.get('token','')}) — రద్దు చేయబడింది."
            f"\nకొత్తది: **{r['doctor']}** ({r['specialty']})"
            f"\nబ్రాంచ్: **{r['location']}** — {r['address']}"
            f"\nతేదీ: **{r['date']}** ({r['day_telugu']}), సమయం: **{r['time']}**"
            f"\nకొత్త టోకెన్: **{r['token']}**"
            f"\n\nదయచేసి 10 నిమిషాలు ముందుగా రండి."
        )
    return (
        f"\n\n🔄 **Appointment Rescheduled!**"
        f"\nPrevious: {old.get('date','')} {old.get('time','')} (Token {old.get('token','')}) — cancelled."
        f"\nNew: **{r['doctor']}** ({r['specialty']})"
        f"\nBranch: **{r['location']}** — {r['address']}"
        f"\nDate: **{r['date']}** ({r['day']}), Time: **{r['time']}**"
        f"\nNew Token: **{r['token']}**"
        f"\n\nPlease arrive 10 minutes early."
    )


def _reschedule_not_found_message(r: dict, in_telugu: bool) -> str:
    if in_telugu:
        return ("\n\n రీషెడ్యూల్ చేయడానికి ఆ టోకెన్‌తో అపాయింట్‌మెంట్ కనబడలేదు. టోకెన్ నంబర్ చెక్ చేయండి.")
    return ("\n\n I couldn't find an appointment with that token to reschedule. Please check the token number.")


def _booking_failed_message(in_telugu: bool) -> str:
    if in_telugu:
        return ("\n\n క్షమించండి, ఈ బుకింగ్ పూర్తి చేయలేకపోయాను. "
                "దయచేసి డాక్టర్ పేరు, బ్రాంచ్, తేదీ మరియు సమయం మరోసారి చెప్పండి.")
    return ("\n\n Sorry — I couldn't complete that booking. "
            "Could you please confirm the doctor, branch, date and time once more?")


def _build_replacement(result: dict, in_telugu: bool) -> str:
    status = result["status"]
    if status == "success":
        return _confirmation_message(result, in_telugu)
    if status == "already_booked":
        return _already_booked_message(result, in_telugu)
    if status == "closed_sunday":
        return _sunday_message(result, in_telugu)
    if status == "unavailable":
        return _unavailable_message(result, in_telugu)
    if status == "bad_time":
        return _bad_time_message(result, in_telugu)
    if status == "slot_taken":
        return _slot_taken_message(result, in_telugu)
    if status == "past_date":
        return _past_date_message(result, in_telugu)
    # invalid_doctor / invalid_location / invalid_date -- untrustworthy tag.
    print(f"\n=== REJECTED BOOKING TAG ({status}) === {result}\n")
    return _booking_failed_message(in_telugu)


def _build_cancel_replacement(result: dict, in_telugu: bool) -> str:
    if result["status"] == "cancelled":
        return _cancelled_message(result, in_telugu)
    return _cancel_not_found_message(result, in_telugu)


def _build_reschedule_replacement(result: dict, in_telugu: bool) -> str:
    status = result["status"]
    if status == "rescheduled":
        return _rescheduled_message(result, in_telugu)
    if status == "reschedule_not_found":
        return _reschedule_not_found_message(result, in_telugu)
    # The new slot couldn't be booked -- reuse the booking-failure messages.
    return _build_replacement(result, in_telugu)


@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        full_text = " ".join([h.content for h in request.history] + [request.message])

        confirmed_doctor = _detect_doctor(full_text)
        location = _detect_location(full_text)
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', full_text)
        target_date = date_match.group(1) if date_match else None

        # Availability context: exact open slots when we have a doctor + date;
        # otherwise the doctor's next-available slot so the bot can offer it.
        booking_context = ""
        if confirmed_doctor and target_date:
            booking_context = get_booking_context(confirmed_doctor, location, target_date)
        elif confirmed_doctor:
            booking_context = get_next_available(confirmed_doctor, location)

        patient_bookings = get_patient_bookings_context(PATIENT_NAME)

        reply_text = generate_claude_response(
            request.message, request.history, booking_context,
            request.language, patient_bookings,
        )

        # Write the system's own confirmation in whatever language the assistant
        # just replied in.
        in_telugu = bool(_TELUGU_SCRIPT.search(reply_text))

        # At most one action per reply. Reschedule is checked first (it is the
        # most specific tag), then cancel, then a plain booking.
        resched = _RESCHED_TAG.search(reply_text)
        cancel = _CANCEL_TAG.search(reply_text)
        book = _BOOK_TAG.search(reply_text)

        if resched:
            old_token, doc, loc, date_str, time_str, patient = (g.strip() for g in resched.groups())
            result = reschedule_appointment(old_token, doc, loc, date_str, time_str, patient)
            reply_text = _ANY_RESCHED_TAG.sub(_build_reschedule_replacement(result, in_telugu), reply_text)
        elif cancel:
            token = cancel.group(1).strip()
            result = cancel_appointment(token)
            reply_text = _ANY_CANCEL_TAG.sub(_build_cancel_replacement(result, in_telugu), reply_text)
        elif book:
            doc, loc, date_str, time_str, patient = (g.strip() for g in book.groups())
            result = book_appointment(doc, loc, date_str, time_str, patient)
            reply_text = _ANY_BOOK_TAG.sub(_build_replacement(result, in_telugu), reply_text)

        return ChatResponse(reply=reply_text)

    except Exception as e:
        print("\n===  BACKEND ERROR  ===")
        traceback.print_exc()
        print("===========================\n")
        raise HTTPException(status_code=500, detail=str(e))
