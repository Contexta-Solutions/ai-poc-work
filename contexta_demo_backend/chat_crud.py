from datetime import datetime

import appointments_store
from doctors_data import DOCTORS

MAX_PER_SLOT = 5  # each doctor can see at most 5 patients per slot

SLOT_CODE = {"Morning": "1", "Afternoon": "2", "Evening": "3"}
SLOT_START_HOURS = {"Morning": 9, "Afternoon": 13, "Evening": 18}

def get_all_doctors() -> str:
    doc_strings = [f"{doc['name']} ({doc['specialty']} — {doc['sub_specialty']}) | Status: {doc['status']} | Schedule: {doc['schedule']}" for doc in DOCTORS]
    return "\n".join(doc_strings)


def get_slot_availability(doctor_name: str, date_str: str) -> str:
    """Return a human-readable string showing remaining slots for each session."""
    lines = []
    for slot_name in ["Morning", "Afternoon", "Evening"]:
        booked = appointments_store.count_booked(doctor_name, date_str, slot_name)
        remaining = max(0, MAX_PER_SLOT - booked)
        status = f"{remaining} slots available" if remaining > 0 else "FULL"
        lines.append(f"  {slot_name} (9–12 PM / 1–4 PM / 6–9 PM): {status}".replace(
            "9–12 PM / 1–4 PM / 6–9 PM",
            {"Morning": "9:00 AM – 12:00 PM", "Afternoon": "1:00 PM – 4:00 PM", "Evening": "6:00 PM – 9:00 PM"}[slot_name]
        ))
    return "\n".join(lines)


def book_appointment(doctor_name: str, slot_str: str, date_str: str, patient_name: str) -> dict:
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        day_num = date_obj.strftime("%d")
    except ValueError:
        day_num = datetime.now().strftime("%d")
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    slot_key = slot_str.strip().capitalize()

    count = appointments_store.count_booked(doctor_name, date_str, slot_key)

    if count >= MAX_PER_SLOT:
        remaining_info = get_slot_availability(doctor_name, date_str)
        return {"status": "full", "message": "This slot is fully booked.", "availability": remaining_info}
        
    queue_num = count + 1
    
    # Token format: DD + slot_code + queue (e.g., 15102 = day 15, Morning(1), patient 02)
    code = SLOT_CODE.get(slot_key, "0")
    token = f"{day_num}{code}{queue_num:02d}"
    
    start_hour = SLOT_START_HOURS.get(slot_key, 9)
    
    total_mins = (queue_num - 1) * 20
    add_hours = total_mins // 60
    add_mins = total_mins % 60
    
    app_hour = start_hour + add_hours
    period = "AM" if app_hour < 12 else "PM"
    display_hour = app_hour if app_hour <= 12 else app_hour - 12
    if display_hour == 0:
        display_hour = 12
    
    exact_time = f"{display_hour:02d}:{add_mins:02d} {period}"
    
    # Remaining slots after this booking
    remaining = MAX_PER_SLOT - queue_num
    
    appointments_store.add_appointment(doctor_name, patient_name, date_str, slot_key, queue_num, token)


    return {
        "status": "success", 
        "token": token, 
        "time": exact_time, 
        "date": date_str, 
        "patient": patient_name,
        "slot": slot_key,
        "remaining": remaining
    }
