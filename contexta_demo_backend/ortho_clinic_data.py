"""Static OrthoCare Clinic data for the ChatBot ONLY.

This is intentionally separate from doctors_data.py (which feeds the Visit Notes
doctor picker). The ChatBot is the OrthoCare booking assistant; Visit Notes is a
different feature and must not be affected by changes here. Keep this roster in
sync with the frontend's RightSidebar.jsx.

Sample/POC data -- names, numbers, addresses and schedules are fictional
placeholders. Replace with real clinic data before production use.
"""

# Python's date.weekday(): Monday=0 ... Sunday=6. The clinic is closed on
# Sundays at every location (emergency cases only).
MON, TUE, WED, THU, FRI, SAT, SUN = 0, 1, 2, 3, 4, 5, 6

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Telugu names for the weekdays (for confirmations / availability quoted in Telugu).
DAY_TELUGU = {
    "Monday": "సోమవారం",
    "Tuesday": "మంగళవారం",
    "Wednesday": "బుధవారం",
    "Thursday": "గురువారం",
    "Friday": "శుక్రవారం",
    "Saturday": "శనివారం",
    "Sunday": "ఆదివారం",
}

# ── The three OrthoCare locations in Hyderabad ────────────────────────────────
# `open`/`close` are the clinic's own hours (24h "HH:MM"); individual doctors keep
# their own narrower windows in DOCTORS below. MRI/CT live only at Gachibowli.
LOCATIONS = {
    "KPHB": {
        "name": "KPHB",
        "timings": "9:00 AM – 5:00 PM",
        "open": "09:00",
        "close": "17:00",
        "address": "OrthoCare Clinic, Plot No. 24, KPHB Colony Main Road, Near KPHB Bus Stop, Kukatpally, Hyderabad – 500072",
        "contact_person": "Mr. Bhanu Chandra",
        "phone": "9988661122",
    },
    "Gachibowli": {
        "name": "Gachibowli",
        "timings": "10:00 AM – 8:00 PM",
        "open": "10:00",
        "close": "20:00",
        "address": "OrthoCare Clinic, 2nd Floor, Gachibowli Main Road, Near DLF Cyber City, Hyderabad – 500032",
        "contact_person": "Ms. Swathi Reddy",
        "phone": "9988662233",
    },
    "Dilsukhnagar": {
        "name": "Dilsukhnagar",
        "timings": "11:00 AM – 6:00 PM",
        "open": "11:00",
        "close": "18:00",
        "address": "OrthoCare Clinic, Dilsukhnagar Main Road, Near Chaitanyapuri Metro Station, Hyderabad – 500060",
        "contact_person": "Mr. Ravi Teja",
        "phone": "9988663344",
    },
}

# ── Doctor roster ─────────────────────────────────────────────────────────────
# `availability` is a list of consulting blocks. Each block ties the doctor to a
# specific location, a set of weekdays, and a start/end window (24h "HH:MM").
# Primary doctors have a single block at their home location (with a lunch break);
# visiting specialists have one block per location they rotate through.
DOCTORS = [
    {
        "name": "Dr. Srinivasa Rao",
        "qualification": "MBBS, MS (Ortho)",
        "specialty": "General Orthopaedics & Trauma",
        "type": "Primary",
        "home_location": "KPHB",
        "availability": [
            {"location": "KPHB", "days": [MON, TUE, WED, THU, FRI, SAT],
             "start": "09:00", "end": "17:00", "lunch": ["13:00", "14:00"]},
        ],
    },
    {
        "name": "Dr. Ramesh Babu",
        "qualification": "MBBS, D. Ortho",
        "specialty": "General Orthopaedics & Joint Care",
        "type": "Primary",
        "home_location": "Gachibowli",
        "availability": [
            {"location": "Gachibowli", "days": [MON, TUE, WED, THU, FRI, SAT],
             "start": "10:00", "end": "20:00", "lunch": ["14:00", "15:00"]},
        ],
    },
    {
        "name": "Dr. Padmaja Reddy",
        "qualification": "MBBS, MS (Ortho)",
        "specialty": "General Orthopaedics & Sports Injury",
        "type": "Primary",
        "home_location": "Dilsukhnagar",
        "availability": [
            {"location": "Dilsukhnagar", "days": [MON, TUE, WED, THU, FRI, SAT],
             "start": "11:00", "end": "18:00", "lunch": ["14:00", "15:00"]},
        ],
    },
    {
        "name": "Dr. Suresh Kumar Nair",
        "qualification": "MBBS, MS, DNB (Ortho)",
        "specialty": "Joint Replacement Surgeon (Knee & Hip)",
        "type": "Visiting Specialist",
        "home_location": None,
        "availability": [
            {"location": "Gachibowli", "days": [MON, THU], "start": "12:00", "end": "15:00"},
            {"location": "KPHB", "days": [TUE, FRI], "start": "11:00", "end": "14:00"},
            {"location": "Dilsukhnagar", "days": [WED, SAT], "start": "13:00", "end": "16:00"},
        ],
    },
    {
        "name": "Dr. Kavitha Subramaniam",
        "qualification": "MBBS, MS (Ortho), Fellowship Spine",
        "specialty": "Spine Surgeon",
        "type": "Visiting Specialist",
        "home_location": None,
        "availability": [
            {"location": "KPHB", "days": [MON, THU], "start": "10:00", "end": "13:00"},
            {"location": "Dilsukhnagar", "days": [TUE, FRI], "start": "12:00", "end": "15:00"},
            {"location": "Gachibowli", "days": [WED, SAT], "start": "11:00", "end": "14:00"},
        ],
    },
]

# ── Diagnostic services (NOT bookable by the bot -- patient must call the
# location's contact person). Static reference text for the system prompt. ──────
DIAGNOSTICS_TEXT = """X-RAY (all 3 locations, walk-in during clinic hours):
  KPHB — Mr. Bhaskar Reddy, Mon–Sat 9:00 AM – 5:00 PM
  Gachibowli — Mr. Naveen Kumar, Mon–Sat 10:00 AM – 8:00 PM
  Dilsukhnagar — Mr. Prasad Rao, Mon–Sat 11:00 AM – 6:00 PM

BLOOD WORK / LAB SAMPLE COLLECTION (all 3 locations):
  KPHB — Ms. Divya Sree, Mon–Sat 9:00 AM – 5:00 PM
  Gachibowli — Mr. Kiran Kumar, Mon–Sat 10:00 AM – 8:00 PM
  Dilsukhnagar — Ms. Anitha Rani, Mon–Sat 11:00 AM – 6:00 PM

ULTRASOUND (visiting sonologist Dr. Ganesh Iyer, rotates across locations):
  KPHB — Monday & Thursday, 11:00 AM – 3:00 PM
  Gachibowli — Tuesday & Friday, 12:00 PM – 6:00 PM
  Dilsukhnagar — Wednesday & Saturday, 1:00 PM – 5:00 PM

MRI & CT SCAN (GACHIBOWLI ONLY — technician Mr. Arjun Menon):
  MRI — Mon–Sat, 10:00 AM – 4:00 PM
  CT Scan — Mon–Sat, 10:00 AM – 8:00 PM
  Patients at KPHB or Dilsukhnagar who need MRI/CT must be sent to Gachibowli."""
