from datetime import datetime

import appointments_store
from doctors_data import DOCTORS

MAX_PER_SLOT = 5  # each doctor can see at most 5 patients per slot

# Canonical slot definitions. Single source of truth -- chat_service.py puts
# these in the prompt and chat_routes.py puts them in the confirmation message,
# so the patient can never be quoted two different time ranges for one slot.
SLOTS = ["Morning", "Afternoon", "Evening"]
SLOT_TIMES = {
    "Morning": "9:00 AM – 12:00 PM",
    "Afternoon": "1:00 PM – 4:00 PM",
    "Evening": "6:00 PM – 9:00 PM",
}
SLOT_CODE = {"Morning": "1", "Afternoon": "2", "Evening": "3"}
SLOT_START_HOURS = {"Morning": 9, "Afternoon": 13, "Evening": 18}

# Telugu names for the slots. The <BOOK> tag and the store always use the English
# name; this is only for what the patient reads.
SLOT_TELUGU = {
    "Morning": "ఉదయం",
    "Afternoon": "మధ్యాహ్నం",
    "Evening": "సాయంత్రం",
}

# The assistant replies in Telugu when the patient speaks Telugu, so the model
# can emit a Telugu (or romanized Telugu) slot name in the <BOOK> tag. Map those
# back onto the canonical English name. Anything unrecognised is REJECTED rather
# than silently defaulting -- an unmapped slot used to get token code "0" and a
# 9 AM start time, so an Evening booking was confirmed for 9 in the morning and
# never counted against the Evening slot's capacity.
SLOT_ALIASES = {
    # English
    "morning": "Morning",
    "afternoon": "Afternoon",
    "evening": "Evening",
    # Telugu script
    "ఉదయం": "Morning",
    "పొద్దున": "Morning",
    "మధ్యాహ్నం": "Afternoon",
    "మధ్యాహ్నము": "Afternoon",
    "సాయంత్రం": "Evening",
    "సాయంకాలం": "Evening",
    # Romanized Telugu ("Tenglish")
    "udayam": "Morning",
    "poddun": "Morning",
    "poddunna": "Morning",
    "madhyahnam": "Afternoon",
    "madhyanam": "Afternoon",
    "sayantram": "Evening",
    "sayankalam": "Evening",
}

_DOCTORS_BY_NAME = {doc["name"].strip().lower(): doc["name"] for doc in DOCTORS}


def normalize_slot(raw: str) -> str | None:
    """Canonical slot name, or None if it isn't a real bookable slot."""
    if not raw:
        return None
    return SLOT_ALIASES.get(raw.strip().lower())


def normalize_doctor(raw: str) -> str | None:
    """Canonical doctor name as spelled in DOCTORS, or None if no such doctor."""
    if not raw:
        return None
    key = raw.strip().lower()
    if key in _DOCTORS_BY_NAME:
        return _DOCTORS_BY_NAME[key]

    # Tolerate a missing or differently-punctuated "Dr." prefix.
    def _bare(name: str) -> str:
        return name.replace("dr.", "").replace("dr ", "").strip()

    bare_key = _bare(key)
    for name_lower, name in _DOCTORS_BY_NAME.items():
        if _bare(name_lower) == bare_key:
            return name
    return None


def get_all_doctors() -> str:
    doc_strings = [f"{doc['name']} ({doc['specialty']} — {doc['sub_specialty']}) | Status: {doc['status']} | Schedule: {doc['schedule']}" for doc in DOCTORS]
    return "\n".join(doc_strings)


def get_slot_availability(doctor_name: str, date_str: str) -> str:
    """Return a human-readable string showing remaining slots for each session."""
    lines = []
    for slot_name in SLOTS:
        booked = appointments_store.count_booked(doctor_name, date_str, slot_name)
        remaining = max(0, MAX_PER_SLOT - booked)
        status = f"{remaining} slots available" if remaining > 0 else "FULL"
        lines.append(f"  {slot_name} ({SLOT_TIMES[slot_name]}): {status}")
    return "\n".join(lines)


def _exact_time(slot_key: str, queue_num: int) -> str:
    """Each patient in a slot gets a 20-minute window from the slot's start."""
    total_mins = (queue_num - 1) * 20
    app_hour = SLOT_START_HOURS[slot_key] + total_mins // 60
    add_mins = total_mins % 60

    period = "AM" if app_hour < 12 else "PM"
    display_hour = app_hour if app_hour <= 12 else app_hour - 12
    if display_hour == 0:
        display_hour = 12

    return f"{display_hour:02d}:{add_mins:02d} {period}"


def _appointment_result(status: str, doctor: str, patient_name: str, date_str: str,
                        slot_key: str, queue_num: int, token: str) -> dict:
    return {
        "status": status,
        "token": token,
        "time": _exact_time(slot_key, queue_num),
        "date": date_str,
        "patient": patient_name,
        "doctor": doctor,
        "slot": slot_key,
        "slot_telugu": SLOT_TELUGU[slot_key],
        "slot_time": SLOT_TIMES[slot_key],
        "remaining": max(0, MAX_PER_SLOT - appointments_store.count_booked(doctor, date_str, slot_key)),
    }


def book_appointment(doctor_name: str, slot_str: str, date_str: str, patient_name: str) -> dict:
    """
    Book a slot. Every input is validated against the canonical data -- an
    unrecognised doctor, slot or date is reported back as an error instead of
    being silently coerced, so a mis-worded <BOOK> tag can never write a
    corrupt appointment.

    Booking is IDEMPOTENT. The assistant is not reliable about emitting its
    booking tag exactly once -- a harmless follow-up like "ok" or "thanks" can
    make it fire the tag again -- and that used to create a second appointment
    with a brand new token for a slot the patient already held. Re-booking the
    same doctor + patient + date + slot now returns the appointment that already
    exists, with its original token, and writes nothing.
    """
    doctor = normalize_doctor(doctor_name)
    if not doctor:
        return {"status": "invalid_doctor", "requested": doctor_name}

    slot_key = normalize_slot(slot_str)
    if not slot_key:
        return {"status": "invalid_slot", "requested": slot_str, "valid_slots": SLOTS}

    try:
        date_obj = datetime.strptime((date_str or "").strip(), "%Y-%m-%d")
    except ValueError:
        return {"status": "invalid_date", "requested": date_str}

    date_str = date_obj.strftime("%Y-%m-%d")
    day_num = date_obj.strftime("%d")

    existing = appointments_store.find_appointment(doctor, patient_name, date_str, slot_key)
    if existing:
        return _appointment_result(
            "already_booked", doctor, patient_name, date_str, slot_key,
            existing["queue_num"], existing["token"],
        )

    count = appointments_store.count_booked(doctor, date_str, slot_key)
    if count >= MAX_PER_SLOT:
        return {
            "status": "full",
            "slot": slot_key,
            "slot_telugu": SLOT_TELUGU[slot_key],
            "message": "This slot is fully booked.",
            "availability": get_slot_availability(doctor, date_str),
        }

    queue_num = count + 1

    # Token format: DD + slot_code + queue (e.g., 15102 = day 15, Morning(1), patient 02)
    token = f"{day_num}{SLOT_CODE[slot_key]}{queue_num:02d}"

    appointments_store.add_appointment(doctor, patient_name, date_str, slot_key, queue_num, token)

    return _appointment_result(
        "success", doctor, patient_name, date_str, slot_key, queue_num, token
    )
