"""Availability-aware booking logic for the OrthoCare ChatBot.

Doctors are tied to specific locations, weekdays and time windows (see
ortho_clinic_data.py). A booking must land on a real, open time slot inside the
doctor's window for that location and day -- anything else is rejected rather
than silently coerced, so a mis-worded <BOOK> tag can never write a corrupt
appointment.
"""

from datetime import datetime, timedelta

import appointments_store
from ortho_clinic_data import DOCTORS, LOCATIONS, DAY_NAMES, DAY_TELUGU

# Length of one consultation slot, in minutes. Windows are sliced into slots of
# this size (skipping the lunch break) and each slot holds one patient.
SLOT_MINUTES = 30

# Short codes used to build a readable token, e.g. KPH07 1603.
_LOC_CODE = {"KPHB": "KPH", "Gachibowli": "GCB", "Dilsukhnagar": "DSN"}

_DOCTORS_BY_NAME = {d["name"].strip().lower(): d for d in DOCTORS}
_LOCATIONS_BY_NAME = {name.lower(): name for name in LOCATIONS}


# ── small time helpers ────────────────────────────────────────────────────────

def _to12(hhmm: str) -> str:
    """'14:30' -> '02:30 PM'."""
    return datetime.strptime(hhmm, "%H:%M").strftime("%I:%M %p")


def _window_text(block: dict) -> str:
    """Human-readable window for a block, e.g. '10:00 AM – 8:00 PM (lunch 2:00 PM – 3:00 PM)'."""
    text = f"{_to12(block['start'])} – {_to12(block['end'])}"
    lunch = block.get("lunch")
    if lunch:
        text += f" (lunch break {_to12(lunch[0])} – {_to12(lunch[1])}, no appointments then)"
    return text


def normalize_time(raw: str):
    """Canonical 24h 'HH:MM', or None. Accepts '14:30', '2:30 PM', '2 PM', '2pm'."""
    if not raw:
        return None
    raw = raw.strip().upper().replace(".", "")
    for fmt in ("%H:%M", "%I:%M %p", "%I %p", "%I:%M%p", "%I%p"):
        try:
            return datetime.strptime(raw, fmt).strftime("%H:%M")
        except ValueError:
            continue
    return None


def normalize_doctor(raw: str):
    """Canonical doctor dict as listed in DOCTORS, or None if no such doctor."""
    if not raw:
        return None
    key = raw.strip().lower()
    if key in _DOCTORS_BY_NAME:
        return _DOCTORS_BY_NAME[key]

    def _bare(name: str) -> str:
        return name.replace("dr.", "").replace("dr ", "").strip()

    bare_key = _bare(key)
    for name_lower, doc in _DOCTORS_BY_NAME.items():
        if _bare(name_lower) == bare_key:
            return doc
    return None


def normalize_location(raw: str):
    """Canonical location name, or None if it isn't one of the three."""
    if not raw:
        return None
    return _LOCATIONS_BY_NAME.get(raw.strip().lower())


# ── availability ──────────────────────────────────────────────────────────────

def _block_for(doctor: dict, location: str, weekday: int):
    """The consulting block that has the doctor at `location` on `weekday`, or None."""
    for block in doctor["availability"]:
        if block["location"] == location and weekday in block["days"]:
            return block
    return None


def _slots_in_block(block: dict):
    """All slot start times ('HH:MM') in a block, skipping the lunch break."""
    start = datetime.strptime(block["start"], "%H:%M")
    end = datetime.strptime(block["end"], "%H:%M")
    lunch = block.get("lunch")
    ls = datetime.strptime(lunch[0], "%H:%M") if lunch else None
    le = datetime.strptime(lunch[1], "%H:%M") if lunch else None

    slots, t = [], start
    while t < end:
        if not (ls and ls <= t < le):
            slots.append(t.strftime("%H:%M"))
        t += timedelta(minutes=SLOT_MINUTES)
    return slots


def doctor_availability_text(doctor: dict) -> str:
    """Every location/day/window a doctor works, e.g. for 'when is Dr X available?'."""
    lines = []
    for block in doctor["availability"]:
        days = ", ".join(DAY_NAMES[d] for d in block["days"])
        lines.append(f"{block['location']}: {days} — {_window_text(block)}")
    return "; ".join(lines)


# ── context strings for the system prompt ─────────────────────────────────────

def get_locations_context() -> str:
    lines = []
    for loc in LOCATIONS.values():
        lines.append(
            f"{loc['name']} — Timings: {loc['timings']} (Mon–Sat, closed Sunday) | "
            f"Address: {loc['address']} | Contact: {loc['contact_person']} — {loc['phone']}"
        )
    return "\n".join(lines)


def get_all_doctors() -> str:
    lines = []
    for doc in DOCTORS:
        lines.append(
            f"{doc['name']} ({doc['qualification']}) — {doc['specialty']} "
            f"[{doc['type']}]\n    Availability: {doctor_availability_text(doc)}"
        )
    return "\n".join(lines)


def get_booking_context(doctor_name: str, location_name: str, date_str: str) -> str:
    """
    A precise, LLM-facing description of which slots are open for a given
    doctor + location + date. Returns "" when there isn't enough concrete
    information yet (e.g. no date), so the assistant just keeps collecting it.
    """
    doctor = normalize_doctor(doctor_name)
    if not doctor or not date_str:
        return ""

    try:
        date_obj = datetime.strptime(date_str.strip(), "%Y-%m-%d")
    except (ValueError, AttributeError):
        return ""

    weekday = date_obj.weekday()
    day_name = DAY_NAMES[weekday]

    if date_obj.date() < datetime.now().date():
        return (f"BOOKING CHECK — {date_str} ({day_name}) is in the PAST. Ask the patient for a "
                f"future date (today is {datetime.now().strftime('%Y-%m-%d')}).")

    if weekday == 6:  # Sunday
        return (f"BOOKING CHECK — {doctor['name']} on {date_str} ({day_name}): the clinic is "
                f"CLOSED on Sundays at every location. Ask the patient to pick Mon–Sat instead.")

    location = normalize_location(location_name)
    if not location:
        # No location fixed yet. For a primary doctor we can still show their home
        # location; for a visiting specialist, spell out where they are that day.
        if doctor["type"] == "Primary":
            location = doctor["home_location"]
        else:
            options = [b["location"] for b in doctor["availability"] if weekday in b["days"]]
            if options:
                return (f"BOOKING CHECK — {doctor['name']} on {date_str} ({day_name}) visits: "
                        f"{', '.join(options)}. Confirm which location the patient wants.")
            return (f"BOOKING CHECK — {doctor['name']} does NOT visit any location on "
                    f"{day_name}. Their schedule: {doctor_availability_text(doctor)}. "
                    f"Suggest one of their actual days.")

    block = _block_for(doctor, location, weekday)
    if not block:
        return (f"BOOKING CHECK — {doctor['name']} is NOT available at {location} on {date_str} "
                f"({day_name}). Their actual schedule: {doctor_availability_text(doctor)}. "
                f"Offer a day/location where they actually consult.")

    all_slots = _slots_in_block(block)
    taken = set(appointments_store.booked_times(doctor['name'], location, date_str))
    open_slots = [s for s in all_slots if s not in taken]

    open_disp = ", ".join(_to12(s) for s in open_slots) if open_slots else "NONE (fully booked)"
    header = (f"BOOKING CHECK — {doctor['name']} at {location} on {date_str} ({day_name}).\n"
              f"    Consulting window: {_window_text(block)}.\n"
              f"    OPEN times (offer these, patient must pick exactly one): {open_disp}")
    if taken:
        header += f"\n    Already booked (do NOT offer): {', '.join(_to12(s) for s in sorted(taken))}"
    return header


# ── booking ───────────────────────────────────────────────────────────────────

def _make_token(location: str, date_obj: datetime, doctor_name: str) -> str:
    seq = appointments_store.count_for(doctor_name, location, date_obj.strftime("%Y-%m-%d")) + 1
    return f"{_LOC_CODE[location]}{date_obj.strftime('%d%m')}{seq:02d}"


def _result(status: str, doctor: dict, location: str, date_str: str,
            time_norm: str, patient_name: str, token: str, weekday: int) -> dict:
    loc = LOCATIONS[location]
    day_name = DAY_NAMES[weekday]
    return {
        "status": status,
        "token": token,
        "doctor": doctor["name"],
        "specialty": doctor["specialty"],
        "location": location,
        "address": loc["address"],
        "contact_person": loc["contact_person"],
        "phone": loc["phone"],
        "date": date_str,
        "day": day_name,
        "day_telugu": DAY_TELUGU[day_name],
        "time": _to12(time_norm),
        "patient": patient_name,
    }


def book_appointment(doctor_name: str, location_name: str, date_str: str,
                     time_str: str, patient_name: str) -> dict:
    """
    Book one time slot. Every field is validated against the canonical data:
    an unknown doctor/location, a day/location the doctor doesn't work, a time
    outside their window (or during lunch), or an already-taken slot are all
    reported back as errors instead of being written.

    Booking is IDEMPOTENT: re-booking the exact same doctor + location + date +
    time + patient returns the existing token and writes nothing (the assistant
    is not reliable about emitting its <BOOK> tag exactly once).
    """
    doctor = normalize_doctor(doctor_name)
    if not doctor:
        return {"status": "invalid_doctor", "requested": doctor_name}

    location = normalize_location(location_name)
    if not location:
        return {"status": "invalid_location", "requested": location_name}

    try:
        date_obj = datetime.strptime((date_str or "").strip(), "%Y-%m-%d")
    except ValueError:
        return {"status": "invalid_date", "requested": date_str}
    date_str = date_obj.strftime("%Y-%m-%d")
    weekday = date_obj.weekday()

    if date_obj.date() < datetime.now().date():
        return {"status": "past_date", "requested": date_str}

    if weekday == 6:
        return {"status": "closed_sunday", "doctor": doctor["name"], "date": date_str}

    block = _block_for(doctor, location, weekday)
    if not block:
        return {
            "status": "unavailable",
            "doctor": doctor["name"],
            "location": location,
            "day": DAY_NAMES[weekday],
            "availability": doctor_availability_text(doctor),
        }

    time_norm = normalize_time(time_str)
    all_slots = _slots_in_block(block)
    if not time_norm or time_norm not in all_slots:
        taken = set(appointments_store.booked_times(doctor["name"], location, date_str))
        open_slots = [_to12(s) for s in all_slots if s not in taken]
        return {
            "status": "bad_time",
            "doctor": doctor["name"],
            "location": location,
            "date": date_str,
            "day": DAY_NAMES[weekday],
            "window": _window_text(block),
            "open_times": ", ".join(open_slots) if open_slots else "none — fully booked",
            "requested": time_str,
        }

    existing = appointments_store.find_appointment(
        doctor["name"], patient_name, date_str, location, time_norm)
    if existing:
        return _result("already_booked", doctor, location, date_str,
                       time_norm, patient_name, existing["token"], weekday)

    if appointments_store.is_time_taken(doctor["name"], location, date_str, time_norm):
        taken = set(appointments_store.booked_times(doctor["name"], location, date_str))
        open_slots = [_to12(s) for s in all_slots if s not in taken]
        return {
            "status": "slot_taken",
            "doctor": doctor["name"],
            "location": location,
            "date": date_str,
            "day": DAY_NAMES[weekday],
            "time": _to12(time_norm),
            "open_times": ", ".join(open_slots) if open_slots else "none — fully booked",
        }

    token = _make_token(location, date_obj, doctor["name"])
    appointments_store.add_appointment(
        doctor["name"], patient_name, date_str, location, time_norm, token)

    return _result("success", doctor, location, date_str,
                   time_norm, patient_name, token, weekday)


# ── cancel / reschedule / lookups ─────────────────────────────────────────────

def _appt_details(appt: dict) -> dict:
    """Enrich a stored appointment (24h time) into display fields."""
    date_obj = datetime.strptime(appt["date"], "%Y-%m-%d")
    day_name = DAY_NAMES[date_obj.weekday()]
    loc = LOCATIONS.get(appt["location"], {})
    doc = normalize_doctor(appt["doctor_name"])
    return {
        "token": appt["token"],
        "doctor": appt["doctor_name"],
        "specialty": doc["specialty"] if doc else "",
        "location": appt["location"],
        "address": loc.get("address", ""),
        "contact_person": loc.get("contact_person", ""),
        "phone": loc.get("phone", ""),
        "date": appt["date"],
        "day": day_name,
        "day_telugu": DAY_TELUGU[day_name],
        "time": _to12(appt["time"]),
        "patient": appt["patient_name"],
    }


def cancel_appointment(token: str) -> dict:
    """Cancel by token, freeing the slot. Returns the cancelled details, or a
    not-found status if no such token exists (never guesses)."""
    appt = appointments_store.find_by_token(token)
    if not appt:
        return {"status": "cancel_not_found", "token": (token or "").strip()}
    details = _appt_details(appt)
    appointments_store.remove_by_token(appt["token"])
    details["status"] = "cancelled"
    return details


def reschedule_appointment(old_token: str, doctor_name: str, location_name: str,
                           date_str: str, time_str: str, patient_name: str) -> dict:
    """
    Move an existing appointment to a new slot. The NEW slot is booked and
    validated first (same rules as book_appointment); only if that succeeds is
    the old one removed. If the new slot is invalid/taken/past, nothing changes
    and the failure is returned so the patient can pick again.
    """
    old = appointments_store.find_by_token(old_token)
    if not old:
        return {"status": "reschedule_not_found", "token": (old_token or "").strip()}

    old_details = _appt_details(old)
    result = book_appointment(doctor_name, location_name, date_str, time_str, patient_name)

    if result["status"] in ("success", "already_booked"):
        if result["token"] != old["token"]:
            appointments_store.remove_by_token(old["token"])
        result["status"] = "rescheduled"
        result["old"] = old_details
        return result

    # New slot couldn't be booked -- leave the original appointment untouched.
    return result


def get_next_available(doctor_name: str, location_name: str | None = None) -> str:
    """Scan forward up to ~3 weeks for the doctor's earliest open slot, so the
    bot can answer 'when's the next appointment with Dr X?'. Returns "" if the
    doctor isn't recognised."""
    doctor = normalize_doctor(doctor_name)
    if not doctor:
        return ""
    location = normalize_location(location_name) if location_name else None
    today = datetime.now().date()

    for i in range(0, 21):
        d = today + timedelta(days=i)
        weekday = d.weekday()
        if weekday == 6:
            continue
        locations = [location] if location else [b["location"] for b in doctor["availability"]]
        for loc in locations:
            block = _block_for(doctor, loc, weekday)
            if not block:
                continue
            date_s = d.strftime("%Y-%m-%d")
            taken = set(appointments_store.booked_times(doctor["name"], loc, date_s))
            open_slots = [s for s in _slots_in_block(block) if s not in taken]
            if open_slots:
                return (f"NEXT AVAILABLE — {doctor['name']} at {loc}: {DAY_NAMES[weekday]} {date_s}, "
                        f"earliest open slot {_to12(open_slots[0])} (window {_window_text(block)}). "
                        f"Offer this if the patient asks for the earliest/next appointment.")
    return f"NEXT AVAILABLE — {doctor['name']} has no open slots in the next 3 weeks."


def get_patient_bookings_context(patient_name: str) -> str:
    """The patient's current appointments (with tokens) for the prompt, so the
    bot can answer 'what's my appointment?' and cancel/reschedule by token."""
    appts = appointments_store.list_for_patient(patient_name)
    if not appts:
        return ""
    lines = []
    for a in appts:
        dt = _appt_details(a)
        lines.append(
            f"Token {dt['token']}: {dt['doctor']} at {dt['location']}, "
            f"{dt['date']} ({dt['day']}) {dt['time']}"
        )
    return "\n".join(lines)
