"""In-memory appointment booking store for the OrthoCare ChatBot.

Resets on server restart (no DB by design). A booking is one exact time slot for
one doctor at one location on one date (capacity 1 per time), so `time` here is a
24h "HH:MM" string.
"""

from typing import List, Dict, Optional

_appointments: List[Dict] = []


def find_appointment(doctor_name: str, patient_name: str, date_str: str,
                     location: str, time_str: str) -> Optional[Dict]:
    """
    The existing appointment for this exact doctor + patient + location + date +
    time, if there is one. Used to keep booking idempotent: the assistant
    sometimes emits its booking tag a second time on a harmless follow-up ("ok",
    "thanks"), and without this check that minted a brand new token for an
    appointment the patient already had.
    """
    for a in _appointments:
        if (
            a["doctor_name"] == doctor_name
            and a["patient_name"] == patient_name
            and a["date"] == date_str
            and a["location"] == location
            and a["time"] == time_str
        ):
            return a
    return None


def is_time_taken(doctor_name: str, location: str, date_str: str, time_str: str) -> bool:
    """True if that exact time slot for the doctor/location/date is already held."""
    return any(
        a["doctor_name"] == doctor_name
        and a["location"] == location
        and a["date"] == date_str
        and a["time"] == time_str
        for a in _appointments
    )


def booked_times(doctor_name: str, location: str, date_str: str) -> List[str]:
    """All taken "HH:MM" times for a doctor at a location on a date."""
    return [
        a["time"] for a in _appointments
        if a["doctor_name"] == doctor_name
        and a["location"] == location
        and a["date"] == date_str
    ]


def count_for(doctor_name: str, location: str, date_str: str) -> int:
    return len(booked_times(doctor_name, location, date_str))


def add_appointment(doctor_name: str, patient_name: str, date_str: str,
                    location: str, time_str: str, token: str) -> None:
    _appointments.append({
        "doctor_name": doctor_name,
        "patient_name": patient_name,
        "date": date_str,
        "location": location,
        "time": time_str,
        "token": token,
    })


def find_by_token(token: str) -> Optional[Dict]:
    """The appointment with this token, if any (tokens are unique per booking)."""
    token = (token or "").strip()
    for a in _appointments:
        if a["token"] == token:
            return a
    return None


def remove_by_token(token: str) -> bool:
    """Delete the appointment with this token, freeing its slot. True if removed."""
    token = (token or "").strip()
    for i, a in enumerate(_appointments):
        if a["token"] == token:
            _appointments.pop(i)
            return True
    return False


def list_for_patient(patient_name: str) -> List[Dict]:
    """All current appointments held by a patient, sorted by date then time."""
    appts = [a for a in _appointments if a["patient_name"] == patient_name]
    return sorted(appts, key=lambda a: (a["date"], a["time"]))
