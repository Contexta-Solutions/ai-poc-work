from fastapi import APIRouter, HTTPException
import traceback
import re
from datetime import datetime
from schemas import ChatRequest, ChatResponse
from doctors_data import DOCTORS
from chat_crud import get_all_doctors, get_slot_availability, book_appointment
from chat_service import generate_claude_response

router = APIRouter()

# Telugu block in Unicode. Used to decide which language the system's own
# booking confirmation should be written in, so a Telugu conversation doesn't
# end with an English receipt stapled to it.
_TELUGU_SCRIPT = re.compile(r'[ఀ-౿]')

_BOOK_TAG = re.compile(r'<BOOK>(.*?)\|(.*?)\|(.*?)\|(.*?)</BOOK>')
_ANY_BOOK_TAG = re.compile(r'<BOOK>.*?</BOOK>', re.DOTALL)


def _get_doctor_names():
    """Doctor names for mention-detection."""
    return [d["name"] for d in DOCTORS]


def _confirmation_message(result: dict, in_telugu: bool) -> str:
    if in_telugu:
        # Everything in Telugu script except the things the system reads back:
        # doctor name, date, clock time, token number.
        return (
            f"\n\n **అపాయింట్‌మెంట్ ఖరారు అయ్యింది!**"
            f"\nడాక్టర్: **{result['doctor']}**"
            f"\nపేషెంట్: **{result['patient']}**"
            f"\nతేదీ: **{result['date']}**"
            f"\nసమయ విభాగం: **{result['slot_telugu']}** ({result['slot_time']})"
            f"\nసమయం: **{result['time']}**"
            f"\nటోకెన్ నంబర్: **{result['token']}**"
            f"\n{result['slot_telugu']} లో మిగిలిన స్థానాలు: **{result['remaining']}**"
            f"\n\nదయచేసి 10 నిమిషాలు ముందుగా రండి."
        )
    return (
        f"\n\n **Appointment Confirmed!**"
        f"\nDoctor: **{result['doctor']}**"
        f"\nPatient: **{result['patient']}**"
        f"\nDate: **{result['date']}**"
        f"\nSlot: **{result['slot']}** ({result['slot_time']})"
        f"\nExact Time: **{result['time']}**"
        f"\nToken: **{result['token']}**"
        f"\nRemaining slots in {result['slot']}: **{result['remaining']}**"
        f"\n\nPlease arrive 10 minutes early."
    )


def _already_booked_message(result: dict, in_telugu: bool) -> str:
    """The assistant fired its booking tag again for an appointment the patient
    already holds. Nothing was written -- show them the token they already have
    instead of a second confirmation with a new number."""
    if in_telugu:
        return (
            f"\n\n మీ అపాయింట్‌మెంట్ ఇప్పటికే బుక్ అయ్యింది — "
            f"టోకెన్ నంబర్: **{result['token']}** "
            f"(డాక్టర్: **{result['doctor']}**, తేదీ: **{result['date']}**, "
            f"**{result['slot_telugu']}**, సమయం: **{result['time']}**)."
        )
    return (
        f"\n\n You're already booked — Token: **{result['token']}** "
        f"(Doctor: **{result['doctor']}**, Date: **{result['date']}**, "
        f"**{result['slot']}**, Time: **{result['time']}**)."
    )


def _slot_full_message(result: dict, in_telugu: bool) -> str:
    availability = result.get("availability", "")
    if in_telugu:
        return (
            f"\n\n **స్థానాలు నిండిపోయాయి:** క్షమించండి, ఆ తేదీన **{result.get('slot_telugu', '')}** "
            f"సమయ విభాగం పూర్తిగా బుక్ అయ్యింది. దయచేసి వేరే సమయం ఎంచుకోండి.\n\n{availability}"
        )
    return (
        f"\n\n **Slot Full:** I apologize, but the **{result.get('slot', '')}** slot on that date is fully booked "
        f"for this doctor. Could you please select a different slot?\n\n{availability}"
    )


def _booking_failed_message(in_telugu: bool) -> str:
    """The model emitted a <BOOK> tag we couldn't trust (bad doctor/slot/date).
    Never book on a guess -- ask the patient to restate it."""
    if in_telugu:
        return (
            "\n\n క్షమించండి, ఈ బుకింగ్ పూర్తి చేయలేకపోయాను. "
            "దయచేసి డాక్టర్ పేరు, తేదీ మరియు స్లాట్ మరోసారి చెప్పండి."
        )
    return (
        "\n\n Sorry — I couldn't complete that booking. "
        "Could you please confirm the doctor, the date and the slot once more?"
    )


@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        db_state = get_all_doctors()

        doctor_names = _get_doctor_names()
        full_text = " ".join([h.content for h in request.history] + [request.message])

        confirmed_doctor = None
        for doc_name in doctor_names:
            if doc_name.lower() in full_text.lower():
                confirmed_doctor = doc_name

        slot_availability = ""
        if confirmed_doctor:
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', full_text)
            target_date = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")
            slot_availability = f"Doctor: {confirmed_doctor} | Date: {target_date}\n"
            slot_availability += get_slot_availability(confirmed_doctor, target_date)

        reply_text = generate_claude_response(
            request.message, db_state, request.history, slot_availability, request.language
        )

        # Write the system's own confirmation in whatever language the assistant
        # just replied in.
        in_telugu = bool(_TELUGU_SCRIPT.search(reply_text))

        match = _BOOK_TAG.search(reply_text)
        if match:
            doc_name, slot, date_str, patient_name = (g.strip() for g in match.groups())

            result = book_appointment(doc_name, slot, date_str, patient_name)
            status = result["status"]

            if status == "success":
                replacement = _confirmation_message(result, in_telugu)
            elif status == "already_booked":
                # Idempotent: nothing was written, the original token stands.
                replacement = _already_booked_message(result, in_telugu)
            elif status == "full":
                replacement = _slot_full_message(result, in_telugu)
            else:
                # invalid_doctor / invalid_slot / invalid_date -- the model wrote a
                # tag we can't trust. Log it, and don't book anything.
                print(f"\n=== REJECTED BOOKING TAG ({status}) ===")
                print(f"    doctor={doc_name!r} slot={slot!r} date={date_str!r} patient={patient_name!r}")
                print("=======================================\n")
                replacement = _booking_failed_message(in_telugu)

            reply_text = _ANY_BOOK_TAG.sub(replacement, reply_text)

        return ChatResponse(reply=reply_text)

    except Exception as e:
        print("\n===  BACKEND ERROR  ===")
        traceback.print_exc()
        print("===========================\n")
        raise HTTPException(status_code=500, detail=str(e))
