"""Static clinical template seed data, in-memory (no DB)."""

# 1. ORTHOPEDICS: TKR
_tkr_cc = [
    {"line": "Patient cannot walk more than ___ steps without pain", "type": "slot", "slot_key": "steps", "value": None},
    {"line": "Patient is unable to climb stairs", "type": "fixed"},
    {"line": "Range of motion (ROM) limited to ___ degrees", "type": "slot", "slot_key": "rom", "value": None},
    {"line": "Patient requires support / walking aid", "type": "fixed"},
    {"line": "Pain persisting for ___", "type": "slot", "slot_key": "pain_dur", "value": None},
    {"line": "Pain at night affecting sleep", "type": "fixed"},
    {"line": "Swelling over the knee joint", "type": "fixed"},
    {"line": "Pain score ___ / 10 on VAS scale", "type": "slot", "slot_key": "vas", "value": None}
]
_tkr_adv = [
    {"line": "Avoid sitting cross-legged for 6 weeks", "type": "fixed"},
    {"line": "Physiotherapy to begin from day ___", "type": "slot", "slot_key": "pt_day", "value": None},
    {"line": "Use walker for ___ weeks", "type": "slot", "slot_key": "walker_wks", "value": None}
]
_tkr_rx_std = [
    {"drug": "Tab Celecoxib 200mg", "dose": "BD × 5 days", "notes": "After food", "type": "rx_fixed"},
    {"drug": "Tab Pantoprazole 40mg", "dose": "OD", "notes": "Gastro-protection, Before food", "type": "rx_fixed"},
    {"drug": "Tab Calcium + Vit D3", "dose": "OD", "notes": "Bone support", "type": "rx_fixed"}
]
_tkr_rx_pf = [
    {"drug": "Tab Naproxen 500mg", "dose": "BD × 7 days", "notes": "After food", "type": "rx_fixed"},
    {"drug": "Tab Methocarbamol 750mg", "dose": "TDS", "notes": "Muscle relaxant", "type": "rx_fixed"},
    {"drug": "Heel cushion insole", "dose": "Bilateral", "notes": "Footwear advice", "type": "rx_fixed"}
]
_tkr_rx_high = [
    {"drug": "Tab Tramadol 50mg", "dose": "TDS × 3 days", "notes": "Short course only", "type": "rx_fixed"},
    {"drug": "Tab Etoricoxib 90mg", "dose": "OD × 5 days", "notes": "Strong NSAID", "type": "rx_fixed"},
    {"drug": "Inj Methylprednisolone", "dose": "Intra-articular", "notes": "Single shot, Clinic procedure", "type": "rx_fixed"}
]
_tkr_plan = [{"line": "Baseline diagnostic workup required.", "type": "fixed"}]
_tkr_fu_std = [
    {"line": "Wound review at ___ days", "type": "slot", "slot_key": "wound_days", "value": None},
    {"line": "X-ray knee AP/Lateral at ___ weeks", "type": "slot", "slot_key": "xray_wks", "value": None},
    {"line": "Physiotherapy review at 6 weeks", "type": "fixed"}
]

# 2. DIABETOLOGY: T2DM
_dia_cc = [
    {"line": "Fasting blood sugar ___ mg/dL", "type": "slot", "slot_key": "fbs", "value": None},
    {"line": "Post-prandial sugar ___ mg/dL", "type": "slot", "slot_key": "ppbs", "value": None},
    {"line": "HbA1c ___ %", "type": "slot", "slot_key": "hba1c", "value": None},
    {"line": "Excessive thirst and frequent urination", "type": "fixed"},
    {"line": "Fatigue and generalised weakness for ___ weeks", "type": "slot", "slot_key": "fatigue", "value": None},
    {"line": "Tingling / numbness in feet", "type": "fixed"},
    {"line": "Blurring of vision", "type": "fixed"}
]
_dia_adv = [
    {"line": "Low glycemic index diet, avoid refined carbohydrates", "type": "fixed"},
    {"line": "Brisk walk for 30 minutes daily", "type": "fixed"},
    {"line": "Self-monitor blood glucose twice daily", "type": "fixed"},
    {"line": "Annual eye check for diabetic retinopathy", "type": "fixed"},
    {"line": "Foot examination at every visit", "type": "fixed"},
    {"line": "Urine microalbumin every 6 months", "type": "fixed"}
]
_dia_rx_1 = [
    {"drug": "Tab Metformin 500mg", "dose": "BD", "notes": "With meals (First line)", "type": "rx_fixed"},
    {"drug": "Tab Glimepiride 1mg", "dose": "OD", "notes": "Before breakfast", "type": "rx_fixed"}
]
_dia_rx_2 = [
    {"drug": "Tab Metformin 1000mg", "dose": "BD", "notes": "Increased dose", "type": "rx_fixed"},
    {"drug": "Tab Empagliflozin 10mg", "dose": "OD", "notes": "Morning (Cardio-protective)", "type": "rx_fixed"}
]
_dia_rx_3 = [
    {"drug": "Inj Insulin Glargine", "dose": "___ units", "notes": "At bedtime", "type": "rx_slot", "slot_key": "insulin"},
    {"drug": "Oral agents", "dose": "Reduce dose by 50%", "notes": "Adjust existing Rx", "type": "rx_fixed"}
]
_dia_plan = [{"line": "Metabolic panel screening", "type": "fixed"}]
_dia_fu_1 = [
    {"line": "Review with HbA1c at 3 months", "type": "fixed"},
    {"line": "Fasting blood sugar before next visit", "type": "fixed"}
]
_dia_fu_2 = [
    {"line": "Review in ___ weeks with sugar diary", "type": "slot", "slot_key": "fu_wks", "value": None},
    {"line": "Repeat lipid profile and kidney function tests", "type": "fixed"}
]

# 3. PULMONOLOGY: ASTHMA
_pul_cc = [
    {"line": "Wheezing and breathlessness for ___ days", "type": "slot", "slot_key": "wheeze_days", "value": None},
    {"line": "Cough predominantly at night / early morning", "type": "fixed"},
    {"line": "Breathlessness on exertion — MMRC grade ___", "type": "slot", "slot_key": "mmrc", "value": None},
    {"line": "Triggered by dust / smoke / cold air", "type": "fixed"},
    {"line": "Exercise-induced bronchospasm", "type": "fixed"},
    {"line": "Peak flow rate ___ L/min", "type": "slot", "slot_key": "pefr", "value": None}
]
_pul_adv = [
    {"line": "Avoid known allergens and smoke exposure", "type": "fixed"},
    {"line": "Use peak flow meter daily, maintain diary", "type": "fixed"},
    {"line": "Rinse mouth after using inhaler", "type": "fixed"},
    {"line": "Use rescue inhaler if breathless — max 4 puffs", "type": "fixed"},
    {"line": "Visit ER if no relief within 20 minutes", "type": "fixed"}
]
_pul_rx_1 = [
    {"drug": "Salbutamol MDI 100mcg", "dose": "2 puffs SOS", "notes": "Rescue bronchodilator", "type": "rx_fixed"},
    {"drug": "Montelukast 10mg", "dose": "OD at night", "notes": "Leukotriene antagonist", "type": "rx_fixed"}
]
_pul_rx_2 = [
    {"drug": "Budesonide + Formoterol MDI", "dose": "BD", "notes": "ICS + LABA combo", "type": "rx_fixed"},
    {"drug": "Salbutamol MDI", "dose": "2 puffs SOS", "notes": "Rescue", "type": "rx_fixed"},
    {"drug": "Montelukast 10mg", "dose": "OD", "notes": "Add-on", "type": "rx_fixed"}
]
_pul_rx_3 = [
    {"drug": "Nebulisation Salbutamol 2.5mg", "dose": "stat", "notes": "Clinic nebuliser", "type": "rx_fixed"},
    {"drug": "Tab Prednisolone 40mg", "dose": "OD × ___ days", "notes": "Steroid", "type": "rx_slot", "slot_key": "pred_days"},
    {"drug": "Oxygen supplementation", "dose": "If SpO2 < 92%", "notes": "Clinical decision", "type": "rx_fixed"}
]
_pul_plan = [{"line": "Spirometry testing", "type": "fixed"}]
_pul_fu_1 = [
    {"line": "Review in ___ months with PFT", "type": "slot", "slot_key": "fu_months", "value": None},
    {"line": "Bring peak flow diary to next visit", "type": "fixed"}
]
_pul_fu_2 = [
    {"line": "Review in 1 week — assess steroid response", "type": "fixed"},
    {"line": "Chest X-ray before next visit", "type": "fixed"}
]

# 4. PEDIATRICS: ARI
_ped_cc = [
    {"line": "Cough and cold for ___ days", "type": "slot", "slot_key": "cough_days", "value": None},
    {"line": "Fever with temperature ___ °F", "type": "slot", "slot_key": "fever", "value": None},
    {"line": "Nasal congestion and runny nose", "type": "fixed"},
    {"line": "Throat pain / difficulty swallowing", "type": "fixed"},
    {"line": "Poor feeding / appetite since ___ days", "type": "slot", "slot_key": "feeding_days", "value": None},
    {"line": "Child is irritable and restless", "type": "fixed"},
    {"line": "SpO2 ___ % on room air", "type": "slot", "slot_key": "spo2", "value": None}
]
_ped_adv = [
    {"line": "Adequate fluids and rest", "type": "fixed"},
    {"line": "Steam inhalation twice daily", "type": "fixed"},
    {"line": "Saline nasal drops — 2 drops each nostril TDS", "type": "fixed"},
    {"line": "Return immediately if breathing is fast or laboured", "type": "fixed"},
    {"line": "Return if fever persists beyond 3 days on medication", "type": "fixed"},
    {"line": "Do not give aspirin — risk of Reye's syndrome", "type": "fixed"}
]
_ped_rx_1 = [
    {"drug": "Syrup Paracetamol", "dose": "___ ml TDS SOS", "notes": "Weight-based", "type": "rx_slot", "slot_key": "rx_pcm"},
    {"drug": "Syrup Cetirizine", "dose": "___ ml OD at night", "notes": "Weight-based", "type": "rx_slot", "slot_key": "rx_cet"},
    {"drug": "Syrup Ambroxol + Guaifenesin", "dose": "TDS", "notes": "Mucolytic", "type": "rx_fixed"}
]
_ped_rx_2 = [
    {"drug": "Syrup Amoxicillin", "dose": "___ mg/day in 3 doses x 5 days", "notes": "Antibiotic", "type": "rx_slot", "slot_key": "rx_amox"},
    {"drug": "Syrup Paracetamol", "dose": "TDS SOS", "notes": "Weight-based", "type": "rx_fixed"},
    {"drug": "Syrup Cetirizine", "dose": "OD at night", "notes": "Weight-based", "type": "rx_fixed"}
]
_ped_rx_3 = [
    {"drug": "Salbutamol nebulisation", "dose": "___ mg TDS", "notes": "Weight-based", "type": "rx_slot", "slot_key": "rx_sal"},
    {"drug": "Syrup Prednisolone", "dose": "___ mg OD x 3 days", "notes": "Steroid", "type": "rx_slot", "slot_key": "rx_pred"},
    {"drug": "Syrup Paracetamol", "dose": "TDS SOS", "notes": "Fever management", "type": "rx_fixed"}
]
_ped_plan = [{"line": "Supportive care monitoring", "type": "fixed"}]
_ped_fu_1 = [
    {"line": "Review in 3 days if not improving", "type": "fixed"},
    {"line": "CBC if fever persists more than 3 days", "type": "fixed"}
]
_ped_fu_2 = [
    {"line": "Review in 24-48 hours — check SpO2", "type": "fixed"},
    {"line": "Chest X-ray if bronchospasm continues", "type": "fixed"}
]

# template_id -> {section_name: [items]}
TEMPLATE_SECTIONS = {
    "ORT-TKR": {
        "complaints": _tkr_cc,
        "advice": _tkr_adv,
        "prescription": _tkr_rx_std,
        "plan": _tkr_plan,
        "follow_up_plan": _tkr_fu_std,
    },
    "ORT-TKR-RX-PF": {"prescription": _tkr_rx_pf},
    "ORT-TKR-RX-HIGH": {"prescription": _tkr_rx_high},

    "DIA-T2DM": {
        "complaints": _dia_cc,
        "advice": _dia_adv,
        "prescription": _dia_rx_1,
        "plan": _dia_plan,
        "follow_up_plan": _dia_fu_1,
    },
    "DIA-T2DM-RX-SGLT2": {"prescription": _dia_rx_2},
    "DIA-T2DM-RX-INSULIN": {"prescription": _dia_rx_3},
    "DIA-T2DM-FU-INTENSIVE": {"follow_up_plan": _dia_fu_2},

    "PUL-ASTHMA": {
        "complaints": _pul_cc,
        "advice": _pul_adv,
        "prescription": _pul_rx_1,
        "plan": _pul_plan,
        "follow_up_plan": _pul_fu_1,
    },
    "PUL-ASTHMA-RX-MODERATE": {"prescription": _pul_rx_2},
    "PUL-ASTHMA-RX-ACUTE": {"prescription": _pul_rx_3},
    "PUL-ASTHMA-FU-POST": {"follow_up_plan": _pul_fu_2},

    "PED-ARI": {
        "complaints": _ped_cc,
        "advice": _ped_adv,
        "prescription": _ped_rx_1,
        "plan": _ped_plan,
        "follow_up_plan": _ped_fu_1,
    },
    "PED-ARI-RX-BACTERIAL": {"prescription": _ped_rx_2},
    "PED-ARI-RX-BRONCHO": {"prescription": _ped_rx_3},
    "PED-ARI-FU-CONCERN": {"follow_up_plan": _ped_fu_2},
}
