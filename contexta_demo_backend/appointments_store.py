"""In-memory appointment booking store. Resets on server restart (no DB by design)."""

from typing import List, Dict

_appointments: List[Dict] = []


def count_booked(doctor_name: str, date_str: str, slot: str) -> int:
    return sum(
        1 for a in _appointments
        if a["doctor_name"] == doctor_name and a["date"] == date_str and a["slot"] == slot
    )


def add_appointment(doctor_name: str, patient_name: str, date_str: str, slot: str, queue_num: int, token: str) -> None:
    _appointments.append({
        "doctor_name": doctor_name,
        "patient_name": patient_name,
        "date": date_str,
        "slot": slot,
        "queue_num": queue_num,
        "token": token,
    })
