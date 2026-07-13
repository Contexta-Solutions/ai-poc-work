from fastapi import APIRouter, HTTPException
import traceback
import re
from datetime import datetime
from schemas import ChatRequest, ChatResponse
from doctors_data import DOCTORS
from chat_crud import get_all_doctors, get_slot_availability, book_appointment
from chat_service import generate_claude_response

router = APIRouter()

def _get_doctor_names():
    """Doctor names for mention-detection."""
    return [d["name"] for d in DOCTORS]

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
        
        reply_text = generate_claude_response(request.message, db_state, request.history, slot_availability)
        
        match = re.search(r'<BOOK>(.*?)\|(.*?)\|(.*?)\|(.*?)</BOOK>', reply_text)
        if match:
            doc_name = match.group(1).strip()
            slot = match.group(2).strip()
            date_str = match.group(3).strip()
            patient_name = match.group(4).strip()
            
            # Calling CRUD to generate token
            result = book_appointment(doc_name, slot, date_str, patient_name)
            
            if result["status"] == "success":
                remaining = result.get("remaining", 0)
                slot_name = result.get("slot", slot)
                success_msg = f"\n\n **Appointment Confirmed!**\nDoctor: **{doc_name}**\nPatient: **{result['patient']}**\nDate: **{result['date']}**\nSlot: **{slot_name}** (9:00 AM – 12:00 PM / 1:00 PM – 4:00 PM / 6:00 PM – 9:00 PM)\nExact Time: **{result['time']}**\nToken: **{result['token']}**\nRemaining slots in {slot_name}: **{remaining}**\n\nPlease arrive 10 minutes early."
                slot_times = {"Morning": "6:00 AM – 1:00 PM", "Afternoon": "2:00 PM – 7:00 PM", "Evening": "7:00 PM – 12:00 AM", "Midnight": "12:00 AM – 6:00 AM"}
                slot_time = slot_times.get(slot_name, "")
                success_msg = f"\n\n **Appointment Confirmed!**\nDoctor: **{doc_name}**\nPatient: **{result['patient']}**\nDate: **{result['date']}**\nSlot: **{slot_name}** ({slot_time})\nExact Time: **{result['time']}**\nToken: **{result['token']}**\nRemaining slots in {slot_name}: **{remaining}**\n\nPlease arrive 10 minutes early."
                reply_text = re.sub(r'<BOOK>.*?</BOOK>', success_msg, reply_text)
            else:
                error_msg = f"\n\n **Slot Full:** I apologize, but the **{slot}** slot on that date is fully booked for this doctor. Could you please select a different slot?\n\n{result.get('availability', '')}"
                reply_text = re.sub(r'<BOOK>.*?</BOOK>', error_msg, reply_text)

        return ChatResponse(reply=reply_text)
        
    except Exception as e:
        print("\n===  BACKEND ERROR  ===")
        traceback.print_exc()
        print("===========================\n")
        raise HTTPException(status_code=500, detail=str(e))
