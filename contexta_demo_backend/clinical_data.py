"""Static clinical template seed data, in-memory (no DB)."""

# template_id -> display name, for ids that are valid `base_template` selections
# (i.e. NOT variant/override sub-ids like "ORT-TKR-RX-PF" or "DIA-T2DM-RX-SGLT2",
# which only exist to be swapped in via override_section()). Single source of
# truth for "is_base" -- used by llm_service.py to build the identifier list and
# per-template slot catalog it injects into the extraction prompt.
BASE_TEMPLATES = {
    "ORT-TKR": "Total Knee Replacement",
    "ORT-THR": "Total Hip Replacement",
    "ORT-CSPN": "Cervical Spondylosis",
    "ORT-LSPN": "Lumbar Spondylosis / Low Back Pain",
    "ORT-ACLR": "ACL Reconstruction",
    "ORT-MENI": "Meniscus Tear",
    "ORT-RCUF": "Rotator Cuff Tear",
    "ORT-ANKS": "Ankle Sprain",
    "ORT-FSF": "Fracture Shaft of Femur",
    "ORT-FDR": "Fracture Distal Radius (Colles' Fracture)",
    "ORT-FNF": "Fracture Neck of Femur",
    "ORT-PIVD": "Lumbar Disc Prolapse (PIVD) with Sciatica",
    "ORT-FRSH": "Frozen Shoulder (Adhesive Capsulitis)",
    "ORT-CTS": "Carpal Tunnel Syndrome",
    "ORT-PLFA": "Plantar Fasciitis",
    "DIA-T2DM": "Type 2 Diabetes Mellitus",
    "PUL-ASTHMA": "Bronchial Asthma",
    "PED-ARI": "Acute Respiratory Infection (Pediatric)",
}

# ==========================================================================
# ORTHOPEDICS -- transcribed verbatim from "ortho templates_6699.md".
#
# Sections mirror the source doc's own structure and order exactly:
#   Chief Complaint -> Diagnosis (ICD-10) -> History & Complaints ->
#   Examination & Findings -> Impression/Diagnosis -> Management Plan ->
#   Prescriptions -> Lab Orders -> Imaging Orders -> Follow-up Plan
# (The source has no "Plan" section, so these templates define none.)
#
# Every line is verbatim -- nothing merged, deduplicated, or reworded. The
# only edit: where a line carries a variable clinical value (a duration,
# degree, distance, count or grade), that value is replaced with a "___"
# blank + slot_key. The line ALWAYS renders; the blank stays empty and
# editable unless the doctor dictates the value. No example values from the
# source are carried over as defaults.
#
# Prescriptions keep all six source columns: drug / composition / dosage /
# frequency / duration / instructions.
#
# Where the source states the same fact in two sections (e.g. a review
# timeframe in both Management Plan and Follow-up Plan), both lines are kept
# and share one slot_key, so a single dictated value fills both.
# ==========================================================================

# 1. Total Knee Replacement (TKR)
_tkr_chief_complaint = [
    {"line": "Bilateral knee pain for ___", "type": "slot", "slot_key": "tkr_pain_dur", "value": None},
    {"line": "Difficulty climbing stairs", "type": "fixed"},
    {"line": "Morning stiffness > ___ minutes", "type": "slot", "slot_key": "tkr_stiffness_min", "value": None},
    {"line": "Deformity (varus/bow-leg)", "type": "fixed"},
]
_tkr_diag = [
    {"line": "M17.9 – Osteoarthritis of knee, unspecified", "type": "fixed"},
]
_tkr_history = [
    {"line": "Progressive knee pain, worse with activity", "type": "fixed"},
    {"line": "Pain not relieved with oral analgesics", "type": "fixed"},
    {"line": "Reduced walking distance (< ___ m)", "type": "slot", "slot_key": "tkr_walk_dist_m", "value": None},
    {"line": "No h/o trauma or fever", "type": "fixed"},
]
_tkr_exam = [
    {"line": "Varus deformity both knees, fixed flexion ___°", "type": "slot", "slot_key": "tkr_flexion_deg", "value": None},
    {"line": "Crepitus on movement, ROM ___", "type": "slot", "slot_key": "tkr_rom", "value": None},
    {"line": "Tenderness medial joint line", "type": "fixed"},
    {"line": "X-ray: Grade ___ OA, joint space loss, osteophytes", "type": "slot", "slot_key": "tkr_oa_grade", "value": None},
]
_tkr_impr = [
    {"line": "Bilateral primary osteoarthritis knee, Kellgren-Lawrence Grade ___", "type": "slot", "slot_key": "tkr_oa_grade", "value": None},
    {"line": "Candidate for Total Knee Replacement", "type": "fixed"},
]
_tkr_mgmt = [
    {"line": "Elective admission for TKR", "type": "fixed"},
    {"line": "Pre-anaesthetic checkup and fitness", "type": "fixed"},
    {"line": "Post-op physiotherapy and mobilization", "type": "fixed"},
    {"line": "Review with X-ray at ___ weeks", "type": "slot", "slot_key": "tkr_review_wks", "value": None},
]
_tkr_rx = [
    {"drug": "Tab Etoricoxib 90mg", "composition": "Etoricoxib 90mg", "dosage": "1 tablet", "frequency": "1-0-0-0 (Morning only)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Tab Ultracet", "composition": "Tramadol 37.5mg + Paracetamol 325mg", "dosage": "1 tablet", "frequency": "1-0-1-0 (Morning & Evening)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Tab Pantoprazole 40mg", "composition": "Pantoprazole 40mg", "dosage": "1 tablet", "frequency": "1-0-0-0 (Morning only)", "duration": "5 Days", "instructions": "Before food", "type": "rx_fixed"},
    {"drug": "Tab Ondansetron 4mg", "composition": "Ondansetron 4mg", "dosage": "1 tablet", "frequency": "SOS (As needed)", "duration": "5 Days", "instructions": "For post-op nausea/vomiting, max 3/day", "type": "rx_fixed"},
    {"drug": "Tab Vitamin D3 60000 IU", "composition": "Cholecalciferol 60000 IU", "dosage": "1 tablet", "frequency": "Weekly (Once a week)", "duration": "8 Weeks", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Cap Calcium + Vit D3", "composition": "Calcium Citrate 500mg + Vit D3 250IU", "dosage": "1 capsule", "frequency": "1-0-0-0 (Morning only)", "duration": "30 Days", "instructions": "After food", "type": "rx_fixed"},
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
_tkr_lab = [
    {"line": "Complete Blood Count", "type": "fixed"},
    {"line": "Random Blood Sugar", "type": "fixed"},
    {"line": "Serum Creatinine", "type": "fixed"},
    {"line": "PT/INR & APTT", "type": "fixed"},
    {"line": "HbA1c", "type": "fixed"},
]
_tkr_img = [
    {"line": "X-Ray Knee AP/Lateral (weight-bearing)", "type": "fixed"},
    {"line": "X-Ray Knee Post-op check", "type": "fixed"},
]
_tkr_fu = [
    {"line": "Suture removal at ___ weeks", "type": "slot", "slot_key": "tkr_suture_wks", "value": None},
    {"line": "Review at ___ weeks with X-ray and physiotherapy assessment", "type": "slot", "slot_key": "tkr_review_wks", "value": None},
]

# 2. Total Hip Replacement (THR)
_thr_chief_complaint = [
    {"line": "Right hip pain radiating to groin for ___", "type": "slot", "slot_key": "thr_pain_dur", "value": None},
    {"line": "Limp while walking", "type": "fixed"},
    {"line": "Pain on weight bearing", "type": "fixed"},
    {"line": "Restricted hip movement", "type": "fixed"},
]
_thr_diag = [
    {"line": "M16.9 – Osteoarthritis of hip, unspecified", "type": "fixed"},
]
_thr_history = [
    {"line": "Progressive hip pain, worse on standing/walking", "type": "fixed"},
    {"line": "Difficulty wearing socks/shoes", "type": "fixed"},
    {"line": "No relief with NSAIDs and physiotherapy", "type": "fixed"},
    {"line": "No h/o trauma or steroid use", "type": "fixed"},
]
_thr_exam = [
    {"line": "Antalgic gait, positive Trendelenburg sign", "type": "fixed"},
    {"line": "Restricted internal rotation and abduction", "type": "fixed"},
    {"line": "Fixed flexion deformity ___°", "type": "slot", "slot_key": "thr_flexion_deg", "value": None},
    {"line": "X-ray: Joint space loss, femoral head collapse", "type": "fixed"},
]
_thr_impr = [
    {"line": "Right hip osteoarthritis, advanced grade", "type": "fixed"},
    {"line": "Candidate for Total Hip Replacement", "type": "fixed"},
]
_thr_mgmt = [
    {"line": "Elective admission for THR", "type": "fixed"},
    {"line": "Pre-anaesthetic fitness workup", "type": "fixed"},
    {"line": "Post-op mobilization with walker", "type": "fixed"},
    {"line": "Review with X-ray at ___ weeks", "type": "slot", "slot_key": "thr_review_wks", "value": None},
]
_thr_rx = [
    {"drug": "Tab Etoricoxib 90mg", "composition": "Etoricoxib 90mg", "dosage": "1 tablet", "frequency": "1-0-0-0 (Morning only)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Tab Ultracet", "composition": "Tramadol 37.5mg + Paracetamol 325mg", "dosage": "1 tablet", "frequency": "1-0-1-0 (Morning & Evening)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Tab Rivaroxaban 10mg", "composition": "Rivaroxaban 10mg", "dosage": "1 tablet", "frequency": "1-0-0-0 (Morning only)", "duration": "14 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Tab Vitamin D3 60000 IU", "composition": "Cholecalciferol 60000 IU", "dosage": "1 tablet", "frequency": "Weekly (Once a week)", "duration": "8 Weeks", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Cap Calcium + Vit D3", "composition": "Calcium Citrate 500mg + Vit D3 250IU", "dosage": "1 capsule", "frequency": "1-0-0-0 (Morning only)", "duration": "30 Days", "instructions": "After food", "type": "rx_fixed"},
]
_thr_lab = [
    {"line": "Complete Blood Count", "type": "fixed"},
    {"line": "Blood Grouping & Crossmatch", "type": "fixed"},
    {"line": "Coagulation Profile", "type": "fixed"},
    {"line": "Random Blood Sugar", "type": "fixed"},
    {"line": "Serum Creatinine", "type": "fixed"},
]
_thr_img = [
    {"line": "X-Ray Pelvis with Both Hips AP", "type": "fixed"},
    {"line": "X-Ray Hip Lateral", "type": "fixed"},
]
_thr_fu = [
    {"line": "Suture removal at ___ weeks", "type": "slot", "slot_key": "thr_suture_wks", "value": None},
    {"line": "Review at ___ weeks with X-ray and gait assessment", "type": "slot", "slot_key": "thr_review_wks", "value": None},
]

# 3. Cervical Spondylosis (CSPN)
_cspn_chief_complaint = [
    {"line": "Neck pain for ___", "type": "slot", "slot_key": "cspn_pain_dur", "value": None},
    {"line": "Stiffness on movement", "type": "fixed"},
    {"line": "Radiating pain to right arm", "type": "fixed"},
    {"line": "Tingling in fingers", "type": "fixed"},
]
_cspn_diag = [
    {"line": "M47.812 – Spondylosis without myelopathy or radiculopathy, cervical region", "type": "fixed"},
]
_cspn_history = [
    {"line": "Chronic neck pain, aggravated by prolonged desk work", "type": "fixed"},
    {"line": "Occasional radiating pain to right forearm", "type": "fixed"},
    {"line": "No h/o trauma", "type": "fixed"},
    {"line": "No bladder/bowel involvement", "type": "fixed"},
]
_cspn_exam = [
    {"line": "Restricted neck rotation and lateral flexion", "type": "fixed"},
    {"line": "Tenderness over paraspinal muscles C5-C6", "type": "fixed"},
    {"line": "Spurling's test positive on right side", "type": "fixed"},
    {"line": "X-ray: Disc space narrowing, osteophyte formation", "type": "fixed"},
]
_cspn_impr = [
    {"line": "Cervical spondylosis with early radiculopathy", "type": "fixed"},
]
_cspn_mgmt = [
    {"line": "Cervical collar for symptomatic relief", "type": "fixed"},
    {"line": "Physiotherapy and isometric neck exercises", "type": "fixed"},
    {"line": "Ergonomic advice for desk posture", "type": "fixed"},
    {"line": "Review in ___ weeks if no improvement", "type": "slot", "slot_key": "cspn_review_wks", "value": None},
]
_cspn_lspn_rx = [
    {"drug": "Tab Aceclofenac + Paracetamol", "composition": "Aceclofenac 100mg + Paracetamol 325mg", "dosage": "1 tablet", "frequency": "1-0-1-0 (Morning & Evening)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Tab Thiocolchicoside 4mg", "composition": "Thiocolchicoside 4mg", "dosage": "1 tablet", "frequency": "1-0-1-0 (Morning & Evening)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Cap Methylcobalamin 1500mcg", "composition": "Methylcobalamin 1500mcg", "dosage": "1 capsule", "frequency": "1-0-0-0 (Morning only)", "duration": "30 Days", "instructions": "After food", "type": "rx_fixed"},
]
_cspn_lab = [
    {"line": "Complete Blood Count", "type": "fixed"},
    {"line": "ESR", "type": "fixed"},
    {"line": "CRP", "type": "fixed"},
    {"line": "Vitamin D", "type": "fixed"},
]
_cspn_img = [
    {"line": "X-Ray Cervical Spine AP/Lateral/Flexion-Extension", "type": "fixed"},
    {"line": "MRI Cervical Spine (if radiculopathy persists)", "type": "fixed"},
]
_cspn_fu = [
    {"line": "Review in ___ weeks if no improvement", "type": "slot", "slot_key": "cspn_review_wks", "value": None},
    {"line": "MRI-based surgical opinion if symptoms worsen", "type": "fixed"},
]

# 4. Lumbar Spondylosis / Low Back Pain (LSPN)
_lspn_chief_complaint = [
    {"line": "Low back pain for ___", "type": "slot", "slot_key": "lspn_pain_dur", "value": None},
    {"line": "Stiffness on bending forward", "type": "fixed"},
    {"line": "Pain worse with prolonged sitting", "type": "fixed"},
    {"line": "No radiation to legs", "type": "fixed"},
]
_lspn_diag = [
    {"line": "M47.816 – Spondylosis without myelopathy or radiculopathy, lumbar region", "type": "fixed"},
]
_lspn_history = [
    {"line": "Chronic dull aching low back pain", "type": "fixed"},
    {"line": "Aggravated by sitting, relieved by rest", "type": "fixed"},
    {"line": "No h/o trauma or fever", "type": "fixed"},
    {"line": "No radicular symptoms", "type": "fixed"},
]
_lspn_exam = [
    {"line": "Restricted lumbar flexion and extension", "type": "fixed"},
    {"line": "Paraspinal muscle tenderness and spasm", "type": "fixed"},
    {"line": "Straight Leg Raise test negative bilaterally", "type": "fixed"},
    {"line": "X-ray: Disc space narrowing, marginal osteophytes", "type": "fixed"},
]
_lspn_impr = [
    {"line": "Lumbar spondylosis, mechanical low back pain", "type": "fixed"},
]
_lspn_mgmt = [
    {"line": "Lumbosacral belt for symptomatic support", "type": "fixed"},
    {"line": "Core strengthening physiotherapy", "type": "fixed"},
    {"line": "Posture and lifestyle advice", "type": "fixed"},
    {"line": "Review in ___ weeks if no improvement", "type": "slot", "slot_key": "lspn_review_wks", "value": None},
]
_lspn_lab = [
    {"line": "Complete Blood Count", "type": "fixed"},
    {"line": "ESR", "type": "fixed"},
    {"line": "Vitamin D", "type": "fixed"},
]
_lspn_img = [
    {"line": "X-Ray Lumbosacral Spine AP/Lateral", "type": "fixed"},
]
_lspn_fu = [
    {"line": "Review in ___ weeks if no improvement", "type": "slot", "slot_key": "lspn_review_wks", "value": None},
    {"line": "MRI advised if symptoms persist beyond ___ weeks", "type": "slot", "slot_key": "lspn_mri_wks", "value": None},
]

# 5. ACL Reconstruction (ACLR)
_aclr_chief_complaint = [
    {"line": "Right knee instability for ___", "type": "slot", "slot_key": "aclr_instab_dur", "value": None},
    {"line": "Giving-way sensation while walking", "type": "fixed"},
    {"line": "Swelling after sports injury", "type": "fixed"},
    {"line": "Difficulty running and pivoting", "type": "fixed"},
]
_aclr_diag = [
    {"line": "S83.511A – Sprain of anterior cruciate ligament, right knee (chronic ACL deficiency)", "type": "fixed"},
]
_aclr_history = [
    {"line": "H/o twisting injury during sports ___ back", "type": "slot", "slot_key": "aclr_injury_ago", "value": None},
    {"line": "Recurrent episodes of knee giving way", "type": "fixed"},
    {"line": "Mild intermittent swelling", "type": "fixed"},
    {"line": "No locking symptoms", "type": "fixed"},
]
_aclr_exam = [
    {"line": "Positive Lachman test, right knee", "type": "fixed"},
    {"line": "Positive anterior drawer test", "type": "fixed"},
    {"line": "Mild effusion, quadriceps wasting", "type": "fixed"},
    {"line": "MRI: Complete ACL tear", "type": "fixed"},
]
_aclr_impr = [
    {"line": "Chronic ACL deficiency, right knee", "type": "fixed"},
    {"line": "Candidate for arthroscopic ACL reconstruction", "type": "fixed"},
]
_aclr_mgmt = [
    {"line": "Elective admission for arthroscopic ACL reconstruction", "type": "fixed"},
    {"line": "Pre-op fitness and MRI review", "type": "fixed"},
    {"line": "Structured post-op rehabilitation", "type": "fixed"},
    {"line": "Review at ___ weeks with clinical assessment", "type": "slot", "slot_key": "aclr_review_wks", "value": None},
]
_aclr_rx = [
    {"drug": "Tab Etoricoxib 90mg", "composition": "Etoricoxib 90mg", "dosage": "1 tablet", "frequency": "1-0-0-0 (Morning only)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Tab Ultracet", "composition": "Tramadol 37.5mg + Paracetamol 325mg", "dosage": "1 tablet", "frequency": "1-0-1-0 (Morning & Evening)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Tab Pantoprazole 40mg", "composition": "Pantoprazole 40mg", "dosage": "1 tablet", "frequency": "1-0-0-0 (Morning only)", "duration": "5 Days", "instructions": "Before food", "type": "rx_fixed"},
    {"drug": "Cap Calcium + Vit D3", "composition": "Calcium Citrate 500mg + Vit D3 250IU", "dosage": "1 capsule", "frequency": "1-0-0-0 (Morning only)", "duration": "30 Days", "instructions": "After food", "type": "rx_fixed"},
]
_aclr_lab = [
    {"line": "Complete Blood Count", "type": "fixed"},
    {"line": "Coagulation Profile", "type": "fixed"},
    {"line": "Random Blood Sugar", "type": "fixed"},
]
_aclr_img = [
    {"line": "MRI Knee (pre-op)", "type": "fixed"},
    {"line": "X-Ray Knee AP/Lateral", "type": "fixed"},
]
_aclr_fu = [
    {"line": "Suture removal at ___ weeks", "type": "slot", "slot_key": "aclr_suture_wks", "value": None},
    {"line": "Review at ___ weeks for rehabilitation progress", "type": "slot", "slot_key": "aclr_review_wks", "value": None},
]

# 6. Meniscus Tear (MENI)
_meni_chief_complaint = [
    {"line": "Left knee pain for ___", "type": "slot", "slot_key": "meni_pain_dur", "value": None},
    {"line": "Clicking sound on movement", "type": "fixed"},
    {"line": "Occasional locking of knee", "type": "fixed"},
    {"line": "Swelling after prolonged activity", "type": "fixed"},
]
_meni_diag = [
    {"line": "S83.209A – Tear of meniscus, current injury, left knee", "type": "fixed"},
]
_meni_history = [
    {"line": "H/o twisting injury while squatting", "type": "fixed"},
    {"line": "Intermittent locking and clicking", "type": "fixed"},
    {"line": "Pain aggravated on stairs", "type": "fixed"},
    {"line": "No instability symptoms", "type": "fixed"},
]
_meni_exam = [
    {"line": "Joint line tenderness, medial side", "type": "fixed"},
    {"line": "Positive McMurray's test", "type": "fixed"},
    {"line": "Mild effusion present", "type": "fixed"},
    {"line": "MRI: Medial meniscus tear", "type": "fixed"},
]
_meni_impr = [
    {"line": "Medial meniscus tear, left knee", "type": "fixed"},
]
_meni_mgmt = [
    {"line": "Arthroscopic meniscectomy/repair advised", "type": "fixed"},
    {"line": "Pre-op fitness assessment", "type": "fixed"},
    {"line": "Post-op quadriceps strengthening", "type": "fixed"},
    {"line": "Review at ___ weeks post-procedure", "type": "slot", "slot_key": "meni_review_wks", "value": None},
]
_meni_rx = [
    {"drug": "Tab Aceclofenac + Paracetamol", "composition": "Aceclofenac 100mg + Paracetamol 325mg", "dosage": "1 tablet", "frequency": "1-0-1-0 (Morning & Evening)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Tab Pantoprazole 40mg", "composition": "Pantoprazole 40mg", "dosage": "1 tablet", "frequency": "1-0-0-0 (Morning only)", "duration": "5 Days", "instructions": "Before food", "type": "rx_fixed"},
    {"drug": "Cap Calcium + Vit D3", "composition": "Calcium Citrate 500mg + Vit D3 250IU", "dosage": "1 capsule", "frequency": "1-0-0-0 (Morning only)", "duration": "30 Days", "instructions": "After food", "type": "rx_fixed"},
]
_meni_lab = [
    {"line": "Complete Blood Count", "type": "fixed"},
    {"line": "Random Blood Sugar", "type": "fixed"},
]
_meni_img = [
    {"line": "MRI Knee", "type": "fixed"},
    {"line": "X-Ray Knee AP/Lateral", "type": "fixed"},
]
_meni_fu = [
    {"line": "Review at ___ weeks post-procedure", "type": "slot", "slot_key": "meni_review_wks", "value": None},
    {"line": "Physiotherapy progress review at ___ weeks", "type": "slot", "slot_key": "meni_pt_review_wks", "value": None},
]

# 7. Rotator Cuff Tear (RCUF)
_rcuf_chief_complaint = [
    {"line": "Right shoulder pain for ___", "type": "slot", "slot_key": "rcuf_pain_dur", "value": None},
    {"line": "Pain worse with overhead activity", "type": "fixed"},
    {"line": "Night pain disturbing sleep", "type": "fixed"},
    {"line": "Weakness in arm", "type": "fixed"},
]
_rcuf_diag = [
    {"line": "M75.100 – Rotator cuff tear or rupture, not specified as traumatic", "type": "fixed"},
]
_rcuf_history = [
    {"line": "Gradual onset shoulder pain", "type": "fixed"},
    {"line": "Difficulty combing hair and reaching overhead", "type": "fixed"},
    {"line": "No h/o trauma", "type": "fixed"},
    {"line": "Failed conservative treatment for ___", "type": "slot", "slot_key": "rcuf_conservative_dur", "value": None},
]
_rcuf_exam = [
    {"line": "Positive painful arc test", "type": "fixed"},
    {"line": "Positive Jobe's (empty can) test", "type": "fixed"},
    {"line": "Weakness in abduction and external rotation", "type": "fixed"},
    {"line": "MRI: Full-thickness supraspinatus tear", "type": "fixed"},
]
_rcuf_impr = [
    {"line": "Full-thickness rotator cuff tear, right shoulder", "type": "fixed"},
]
_rcuf_mgmt = [
    {"line": "Arthroscopic rotator cuff repair advised", "type": "fixed"},
    {"line": "Pre-op fitness assessment", "type": "fixed"},
    {"line": "Structured shoulder rehabilitation post-op", "type": "fixed"},
    {"line": "Review at ___ weeks post-procedure", "type": "slot", "slot_key": "rcuf_review_wks", "value": None},
]
_rcuf_rx = [
    {"drug": "Tab Etoricoxib 90mg", "composition": "Etoricoxib 90mg", "dosage": "1 tablet", "frequency": "1-0-0-0 (Morning only)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Tab Ultracet", "composition": "Tramadol 37.5mg + Paracetamol 325mg", "dosage": "1 tablet", "frequency": "1-0-1-0 (Morning & Evening)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Cap Calcium + Vit D3", "composition": "Calcium Citrate 500mg + Vit D3 250IU", "dosage": "1 capsule", "frequency": "1-0-0-0 (Morning only)", "duration": "30 Days", "instructions": "After food", "type": "rx_fixed"},
]
_rcuf_lab = [
    {"line": "Complete Blood Count", "type": "fixed"},
    {"line": "Random Blood Sugar", "type": "fixed"},
]
_rcuf_img = [
    {"line": "MRI Shoulder", "type": "fixed"},
    {"line": "X-Ray Shoulder AP", "type": "fixed"},
]
_rcuf_fu = [
    {"line": "Review at ___ weeks post-procedure", "type": "slot", "slot_key": "rcuf_review_wks", "value": None},
    {"line": "Physiotherapy milestone review at ___ weeks", "type": "slot", "slot_key": "rcuf_pt_review_wks", "value": None},
]

# 8. Ankle Sprain (ANKS)
_anks_chief_complaint = [
    {"line": "Right ankle pain and swelling after twisting injury", "type": "fixed"},
    {"line": "Difficulty bearing weight", "type": "fixed"},
    {"line": "Bruising over lateral ankle", "type": "fixed"},
    {"line": "Pain on movement", "type": "fixed"},
]
_anks_diag = [
    {"line": "S93.401A – Sprain of unspecified ligament of right ankle, initial encounter", "type": "fixed"},
]
_anks_history = [
    {"line": "H/o inversion injury while walking on uneven ground", "type": "fixed"},
    {"line": "Immediate swelling and pain", "type": "fixed"},
    {"line": "Unable to bear full weight", "type": "fixed"},
    {"line": "No prior ankle injuries", "type": "fixed"},
]
_anks_exam = [
    {"line": "Swelling and tenderness over lateral malleolus", "type": "fixed"},
    {"line": "Positive anterior drawer test, ankle", "type": "fixed"},
    {"line": "Restricted dorsiflexion due to pain", "type": "fixed"},
    {"line": "X-ray: No fracture seen (Ottawa rules negative)", "type": "fixed"},
]
_anks_impr = [
    {"line": "Grade ___ lateral ankle ligament sprain", "type": "slot", "slot_key": "anks_sprain_grade", "value": None},
]
_anks_mgmt = [
    {"line": "RICE protocol (Rest, Ice, Compression, Elevation)", "type": "fixed"},
    {"line": "Ankle brace/support for ___ weeks", "type": "slot", "slot_key": "anks_brace_wks", "value": None},
    {"line": "Gradual weight-bearing as tolerated", "type": "fixed"},
    {"line": "Review in ___ week if pain persists", "type": "slot", "slot_key": "anks_review_wks", "value": None},
]
_anks_rx = [
    {"drug": "Tab Aceclofenac + Paracetamol", "composition": "Aceclofenac 100mg + Paracetamol 325mg", "dosage": "1 tablet", "frequency": "1-0-1-0 (Morning & Evening)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Diclofenac Gel 1%", "composition": "Diclofenac Diethylamine 1.16%", "dosage": "Local application", "frequency": "1-1-1-0 (Morning, Afternoon & Evening)", "duration": "7 Days", "instructions": "Apply locally over ankle", "type": "rx_fixed"},
    {"drug": "Tab Paracetamol 650mg", "composition": "Paracetamol 650mg", "dosage": "1 tablet", "frequency": "SOS (As needed)", "duration": "7 Days", "instructions": "For breakthrough pain, max 3/day", "type": "rx_fixed"},
]
_anks_lab = [
    {"line": "None routinely required", "type": "fixed"},
]
_anks_img = [
    {"line": "X-Ray Ankle AP/Lateral", "type": "fixed"},
    {"line": "MRI Ankle (if no improvement in 2 weeks)", "type": "fixed"},
]
_anks_fu = [
    {"line": "Review in ___ week if pain persists", "type": "slot", "slot_key": "anks_review_wks", "value": None},
    {"line": "MRI advised if instability continues beyond ___ weeks", "type": "slot", "slot_key": "anks_instability_wks", "value": None},
]

# 9. Fracture Shaft of Femur (FSF)
_fsf_chief_complaint = [
    {"line": "Severe left thigh pain after road traffic accident", "type": "fixed"},
    {"line": "Inability to bear weight", "type": "fixed"},
    {"line": "Visible deformity of thigh", "type": "fixed"},
    {"line": "Swelling over thigh", "type": "fixed"},
]
_fsf_diag = [
    {"line": "S72.301A – Unspecified fracture of shaft of left femur, initial encounter", "type": "fixed"},
]
_fsf_history = [
    {"line": "H/o road traffic accident ___ back", "type": "slot", "slot_key": "fsf_injury_ago", "value": None},
    {"line": "Severe pain and deformity of left thigh", "type": "fixed"},
    {"line": "No loss of consciousness", "type": "fixed"},
    {"line": "No other associated injuries reported", "type": "fixed"},
]
_fsf_exam = [
    {"line": "Gross deformity and swelling, left thigh", "type": "fixed"},
    {"line": "Tenderness and abnormal mobility at fracture site", "type": "fixed"},
    {"line": "Distal neurovascular status intact", "type": "fixed"},
    {"line": "X-ray: Comminuted fracture shaft of femur", "type": "fixed"},
]
_fsf_impr = [
    {"line": "Closed fracture shaft of left femur", "type": "fixed"},
    {"line": "Planned for ORIF with intramedullary nailing", "type": "fixed"},
]
_fsf_mgmt = [
    {"line": "Admission and limb immobilization", "type": "fixed"},
    {"line": "Pre-op fitness workup", "type": "fixed"},
    {"line": "ORIF with intramedullary nail", "type": "fixed"},
    {"line": "Post-op mobilization and physiotherapy", "type": "fixed"},
]
_fsf_rx = [
    {"drug": "Tab Etoricoxib 90mg", "composition": "Etoricoxib 90mg", "dosage": "1 tablet", "frequency": "1-0-0-0 (Morning only)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Tab Ultracet", "composition": "Tramadol 37.5mg + Paracetamol 325mg", "dosage": "1 tablet", "frequency": "1-0-1-0 (Morning & Evening)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Tab Rivaroxaban 10mg", "composition": "Rivaroxaban 10mg", "dosage": "1 tablet", "frequency": "1-0-0-0 (Morning only)", "duration": "14 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Cap Calcium + Vit D3", "composition": "Calcium Citrate 500mg + Vit D3 250IU", "dosage": "1 capsule", "frequency": "1-0-0-0 (Morning only)", "duration": "30 Days", "instructions": "After food", "type": "rx_fixed"},
]
_fsf_lab = [
    {"line": "Complete Blood Count", "type": "fixed"},
    {"line": "Blood Grouping & Crossmatch", "type": "fixed"},
    {"line": "Coagulation Profile", "type": "fixed"},
    {"line": "Random Blood Sugar", "type": "fixed"},
    {"line": "Serum Creatinine", "type": "fixed"},
]
_fsf_img = [
    {"line": "X-Ray Femur AP/Lateral with Hip and Knee Joint", "type": "fixed"},
]
_fsf_fu = [
    {"line": "Review at ___ weeks with X-ray for union check", "type": "slot", "slot_key": "fsf_review_wks", "value": None},
    {"line": "Implant removal discussion at ___ year if indicated", "type": "slot", "slot_key": "fsf_implant_yr", "value": None},
]

# 10. Fracture Distal Radius / Colles' Fracture (FDR)
_fdr_chief_complaint = [
    {"line": "Right wrist pain and swelling after fall", "type": "fixed"},
    {"line": "Deformity of wrist (\"dinner-fork\" appearance)", "type": "fixed"},
    {"line": "Inability to move wrist", "type": "fixed"},
    {"line": "Pain on gripping", "type": "fixed"},
]
_fdr_diag = [
    {"line": "S52.531A – Colles' fracture of right radius, initial encounter", "type": "fixed"},
]
_fdr_history = [
    {"line": "H/o fall on outstretched hand", "type": "fixed"},
    {"line": "Immediate wrist pain and swelling", "type": "fixed"},
    {"line": "Visible deformity noted by patient", "type": "fixed"},
    {"line": "No other injuries", "type": "fixed"},
]
_fdr_exam = [
    {"line": "Dinner-fork deformity, right wrist", "type": "fixed"},
    {"line": "Tenderness and swelling over distal radius", "type": "fixed"},
    {"line": "Restricted wrist movement due to pain", "type": "fixed"},
    {"line": "X-ray: Dorsally angulated distal radius fracture", "type": "fixed"},
]
_fdr_impr = [
    {"line": "Closed Colles' fracture, right distal radius", "type": "fixed"},
]
_fdr_mgmt = [
    {"line": "Closed reduction and below-elbow cast application", "type": "fixed"},
    {"line": "Limb elevation and finger movement exercises", "type": "fixed"},
    {"line": "Cast check at ___ week", "type": "slot", "slot_key": "fdr_cast_check_wk", "value": None},
    {"line": "Review with X-ray at ___ weeks", "type": "slot", "slot_key": "fdr_review_wks", "value": None},
]
_fdr_rx = [
    {"drug": "Tab Aceclofenac + Paracetamol", "composition": "Aceclofenac 100mg + Paracetamol 325mg", "dosage": "1 tablet", "frequency": "1-0-1-0 (Morning & Evening)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Cap Calcium + Vit D3", "composition": "Calcium Citrate 500mg + Vit D3 250IU", "dosage": "1 capsule", "frequency": "1-0-0-0 (Morning only)", "duration": "30 Days", "instructions": "After food", "type": "rx_fixed"},
]
_fdr_lab = [
    {"line": "Complete Blood Count", "type": "fixed"},
    {"line": "Random Blood Sugar", "type": "fixed"},
]
_fdr_img = [
    {"line": "X-Ray Wrist AP/Lateral", "type": "fixed"},
]
_fdr_fu = [
    {"line": "Cast check at ___ week", "type": "slot", "slot_key": "fdr_cast_check_wk", "value": None},
    {"line": "Cast removal and review with X-ray at ___ weeks", "type": "slot", "slot_key": "fdr_review_wks", "value": None},
]

# 11. Fracture Neck of Femur (FNF)
_fnf_chief_complaint = [
    {"line": "Right hip pain after fall at home (elderly patient)", "type": "fixed"},
    {"line": "Inability to walk or bear weight", "type": "fixed"},
    {"line": "Shortening of right limb", "type": "fixed"},
    {"line": "Limb in external rotation", "type": "fixed"},
]
_fnf_diag = [
    {"line": "S72.001A – Fracture of unspecified part of neck of right femur, initial encounter", "type": "fixed"},
]
_fnf_history = [
    {"line": "H/o fall at home ___ back", "type": "slot", "slot_key": "fnf_injury_ago", "value": None},
    {"line": "Immediate hip pain and inability to stand", "type": "fixed"},
    {"line": "Known case of osteoporosis", "type": "fixed"},
    {"line": "No other comorbid symptoms reported", "type": "fixed"},
]
_fnf_exam = [
    {"line": "Shortened and externally rotated right limb", "type": "fixed"},
    {"line": "Tenderness over right hip, groin pain on movement", "type": "fixed"},
    {"line": "Distal neurovascular status intact", "type": "fixed"},
    {"line": "X-ray: Displaced fracture neck of femur", "type": "fixed"},
]
_fnf_impr = [
    {"line": "Displaced fracture neck of right femur (elderly)", "type": "fixed"},
    {"line": "Planned for hemiarthroplasty", "type": "fixed"},
]
_fnf_mgmt = [
    {"line": "Admission and pre-op fitness workup (cardiology clearance)", "type": "fixed"},
    {"line": "Hemiarthroplasty/THR as per fitness and age", "type": "fixed"},
    {"line": "Early post-op mobilization to prevent complications", "type": "fixed"},
    {"line": "DVT prophylaxis and physiotherapy", "type": "fixed"},
]
_fnf_rx = [
    {"drug": "Tab Etoricoxib 90mg", "composition": "Etoricoxib 90mg", "dosage": "1 tablet", "frequency": "1-0-0-0 (Morning only)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Tab Ultracet", "composition": "Tramadol 37.5mg + Paracetamol 325mg", "dosage": "1 tablet", "frequency": "1-0-1-0 (Morning & Evening)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Tab Rivaroxaban 10mg", "composition": "Rivaroxaban 10mg", "dosage": "1 tablet", "frequency": "1-0-0-0 (Morning only)", "duration": "28 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Tab Ondansetron 4mg", "composition": "Ondansetron 4mg", "dosage": "1 tablet", "frequency": "SOS (As needed)", "duration": "5 Days", "instructions": "For post-op nausea/vomiting, max 3/day", "type": "rx_fixed"},
    {"drug": "Tab Alendronate 70mg", "composition": "Alendronate Sodium 70mg", "dosage": "1 tablet", "frequency": "Weekly (Once a week)", "duration": "12 Weeks", "instructions": "Empty stomach, with water, remain upright 30 min", "type": "rx_fixed"},
    {"drug": "Cap Calcium + Vit D3", "composition": "Calcium Citrate 500mg + Vit D3 250IU", "dosage": "1 capsule", "frequency": "1-0-0-0 (Morning only)", "duration": "30 Days", "instructions": "After food", "type": "rx_fixed"},
]
_fnf_lab = [
    {"line": "Complete Blood Count", "type": "fixed"},
    {"line": "Blood Grouping & Crossmatch", "type": "fixed"},
    {"line": "Coagulation Profile", "type": "fixed"},
    {"line": "Random Blood Sugar", "type": "fixed"},
    {"line": "Serum Creatinine", "type": "fixed"},
    {"line": "ECG", "type": "fixed"},
    {"line": "2D Echo", "type": "fixed"},
]
_fnf_img = [
    {"line": "X-Ray Pelvis with Both Hips AP", "type": "fixed"},
    {"line": "X-Ray Hip Lateral", "type": "fixed"},
]
_fnf_fu = [
    {"line": "Review at ___ weeks with X-ray and mobility assessment", "type": "slot", "slot_key": "fnf_review_wks", "value": None},
    {"line": "Bone health/osteoporosis review at ___ months", "type": "slot", "slot_key": "fnf_bone_review_mo", "value": None},
]

# 12. Lumbar Disc Prolapse (PIVD) with Sciatica
_pivd_chief_complaint = [
    {"line": "Low back pain radiating to left leg for ___", "type": "slot", "slot_key": "pivd_pain_dur", "value": None},
    {"line": "Numbness and tingling in leg", "type": "fixed"},
    {"line": "Weakness while walking on toes", "type": "fixed"},
    {"line": "Pain worse on sitting and bending", "type": "fixed"},
]
_pivd_diag = [
    {"line": "M51.16 – Intervertebral disc disorders with radiculopathy, lumbar region", "type": "fixed"},
]
_pivd_history = [
    {"line": "Chronic low back pain with radiation below knee", "type": "fixed"},
    {"line": "Aggravated by sitting, coughing, sneezing", "type": "fixed"},
    {"line": "No bladder/bowel involvement", "type": "fixed"},
    {"line": "Failed conservative treatment for ___", "type": "slot", "slot_key": "pivd_failed_tx_wks", "value": None},
]
_pivd_exam = [
    {"line": "Positive Straight Leg Raise test, left side at ___°", "type": "slot", "slot_key": "pivd_slr_deg", "value": None},
    {"line": "Diminished ankle reflex, left side", "type": "fixed"},
    {"line": "Sensory loss over L5-S1 dermatome", "type": "fixed"},
    {"line": "MRI: L4-L5 disc prolapse with nerve root compression", "type": "fixed"},
]
_pivd_impr = [
    {"line": "Lumbar disc prolapse (L4-L5) with left-sided sciatica", "type": "fixed"},
]
_pivd_mgmt = [
    {"line": "Conservative management with physiotherapy", "type": "fixed"},
    {"line": "Activity modification advice", "type": "fixed"},
    {"line": "Surgical opinion if no improvement in ___ weeks", "type": "slot", "slot_key": "pivd_surg_opinion_wks", "value": None},
    {"line": "Review in ___ weeks", "type": "slot", "slot_key": "pivd_review_wks", "value": None},
]
_pivd_rx = [
    {"drug": "Tab Aceclofenac + Paracetamol", "composition": "Aceclofenac 100mg + Paracetamol 325mg", "dosage": "1 tablet", "frequency": "1-0-1-0 (Morning & Evening)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Cap Pregabalin 75mg", "composition": "Pregabalin 75mg", "dosage": "1 capsule", "frequency": "0-0-0-1 (Night only)", "duration": "14 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Tab Thiocolchicoside 4mg", "composition": "Thiocolchicoside 4mg", "dosage": "1 tablet", "frequency": "1-0-1-0 (Morning & Evening)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Cap Methylcobalamin 1500mcg", "composition": "Methylcobalamin 1500mcg", "dosage": "1 capsule", "frequency": "1-0-0-0 (Morning only)", "duration": "30 Days", "instructions": "After food", "type": "rx_fixed"},
]
_pivd_lab = [
    {"line": "Complete Blood Count", "type": "fixed"},
    {"line": "ESR", "type": "fixed"},
]
_pivd_img = [
    {"line": "MRI Lumbosacral Spine", "type": "fixed"},
    {"line": "X-Ray Lumbosacral Spine AP/Lateral", "type": "fixed"},
]
_pivd_fu = [
    {"line": "Review in ___ weeks for symptom progress", "type": "slot", "slot_key": "pivd_review_wks", "value": None},
    {"line": "Surgical opinion if no improvement in ___ weeks", "type": "slot", "slot_key": "pivd_surg_opinion_wks", "value": None},
]

# 13. Frozen Shoulder / Adhesive Capsulitis (FRSH)
_frsh_chief_complaint = [
    {"line": "Progressive right shoulder stiffness for ___", "type": "slot", "slot_key": "frsh_stiff_dur", "value": None},
    {"line": "Pain worse at night", "type": "fixed"},
    {"line": "Difficulty reaching overhead and behind back", "type": "fixed"},
    {"line": "Known diabetic patient", "type": "fixed"},
]
_frsh_diag = [
    {"line": "M75.00 – Adhesive capsulitis of unspecified shoulder", "type": "fixed"},
]
_frsh_history = [
    {"line": "Gradual onset shoulder stiffness without trauma", "type": "fixed"},
    {"line": "Painful restriction in all directions", "type": "fixed"},
    {"line": "Known type 2 diabetes mellitus for ___", "type": "slot", "slot_key": "frsh_dm_dur", "value": None},
    {"line": "No improvement with home exercises", "type": "fixed"},
]
_frsh_exam = [
    {"line": "Global restriction of active and passive ROM", "type": "fixed"},
    {"line": "Painful restriction of external rotation", "type": "fixed"},
    {"line": "No signs of instability or weakness", "type": "fixed"},
    {"line": "X-ray shoulder: Normal study", "type": "fixed"},
]
_frsh_impr = [
    {"line": "Adhesive capsulitis (frozen shoulder), right shoulder, freezing stage", "type": "fixed"},
]
_frsh_mgmt = [
    {"line": "Structured physiotherapy and shoulder mobilization", "type": "fixed"},
    {"line": "Intra-articular steroid injection if pain persists", "type": "fixed"},
    {"line": "Diabetes control optimization", "type": "fixed"},
    {"line": "Review in ___ weeks", "type": "slot", "slot_key": "frsh_review_wks", "value": None},
]
_frsh_rx = [
    {"drug": "Tab Aceclofenac + Paracetamol", "composition": "Aceclofenac 100mg + Paracetamol 325mg", "dosage": "1 tablet", "frequency": "1-0-1-0 (Morning & Evening)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Tab Paracetamol 650mg", "composition": "Paracetamol 650mg", "dosage": "1 tablet", "frequency": "SOS (As needed)", "duration": "14 Days", "instructions": "For breakthrough night pain, max 3/day", "type": "rx_fixed"},
    {"drug": "Cap Calcium + Vit D3", "composition": "Calcium Citrate 500mg + Vit D3 250IU", "dosage": "1 capsule", "frequency": "1-0-0-0 (Morning only)", "duration": "30 Days", "instructions": "After food", "type": "rx_fixed"},
]
_frsh_lab = [
    {"line": "Random Blood Sugar", "type": "fixed"},
    {"line": "HbA1c", "type": "fixed"},
    {"line": "Thyroid Profile", "type": "fixed"},
]
_frsh_img = [
    {"line": "X-Ray Shoulder AP", "type": "fixed"},
    {"line": "USG Shoulder", "type": "fixed"},
]
_frsh_fu = [
    {"line": "Review in ___ weeks for ROM progress", "type": "slot", "slot_key": "frsh_review_wks", "value": None},
    {"line": "Consider intra-articular injection if no improvement", "type": "fixed"},
]

# 14. Carpal Tunnel Syndrome (CTS)
_cts_chief_complaint = [
    {"line": "Numbness and tingling in right thumb, index and middle finger", "type": "fixed"},
    {"line": "Night-time hand pain disturbing sleep", "type": "fixed"},
    {"line": "Weakness of grip", "type": "fixed"},
    {"line": "Symptoms worse with repetitive wrist activity", "type": "fixed"},
]
_cts_diag = [
    {"line": "G56.00 – Carpal tunnel syndrome, unspecified upper limb", "type": "fixed"},
]
_cts_history = [
    {"line": "Gradual onset hand numbness over ___", "type": "slot", "slot_key": "cts_numbness_dur", "value": None},
    {"line": "Symptoms worse at night, relieved by shaking hand", "type": "fixed"},
    {"line": "Occupation involves repetitive wrist movements", "type": "fixed"},
    {"line": "No h/o trauma or diabetes", "type": "fixed"},
]
_cts_exam = [
    {"line": "Positive Tinel's sign at wrist", "type": "fixed"},
    {"line": "Positive Phalen's test", "type": "fixed"},
    {"line": "Thenar muscle wasting in advanced cases", "type": "fixed"},
    {"line": "NCV: Prolonged median nerve latency", "type": "fixed"},
]
_cts_impr = [
    {"line": "Carpal tunnel syndrome, right wrist, moderate severity", "type": "fixed"},
]
_cts_mgmt = [
    {"line": "Night wrist splinting", "type": "fixed"},
    {"line": "Activity modification advice", "type": "fixed"},
    {"line": "Surgical release if no improvement in ___ weeks", "type": "slot", "slot_key": "cts_surg_release_wks", "value": None},
    {"line": "Review in ___ weeks", "type": "slot", "slot_key": "cts_review_wks", "value": None},
]
_cts_rx = [
    {"drug": "Tab Aceclofenac + Paracetamol", "composition": "Aceclofenac 100mg + Paracetamol 325mg", "dosage": "1 tablet", "frequency": "1-0-1-0 (Morning & Evening)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Cap Methylcobalamin 1500mcg", "composition": "Methylcobalamin 1500mcg", "dosage": "1 capsule", "frequency": "1-0-0-0 (Morning only)", "duration": "30 Days", "instructions": "After food", "type": "rx_fixed"},
]
_cts_lab = [
    {"line": "Random Blood Sugar", "type": "fixed"},
    {"line": "HbA1c", "type": "fixed"},
    {"line": "Thyroid Profile", "type": "fixed"},
]
_cts_img = [
    {"line": "Nerve Conduction Study (NCV)", "type": "fixed"},
    {"line": "X-Ray Wrist (if indicated)", "type": "fixed"},
]
_cts_fu = [
    {"line": "Review in ___ weeks for symptom progress", "type": "slot", "slot_key": "cts_review_wks", "value": None},
    {"line": "Surgical opinion if NCV worsens or no improvement", "type": "fixed"},
]

# 15. Plantar Fasciitis (PLFA)
_plfa_chief_complaint = [
    {"line": "Right heel pain worse with first steps in morning", "type": "fixed"},
    {"line": "Pain after prolonged standing", "type": "fixed"},
    {"line": "Tenderness at heel", "type": "fixed"},
    {"line": "Symptoms for ___", "type": "slot", "slot_key": "plfa_symptom_dur", "value": None},
]
_plfa_diag = [
    {"line": "M72.2 – Plantar fascial fibromatosis (Plantar Fasciitis)", "type": "fixed"},
]
_plfa_history = [
    {"line": "Gradual onset heel pain, worse on waking", "type": "fixed"},
    {"line": "Pain reduces with activity then worsens by evening", "type": "fixed"},
    {"line": "Occupation involves prolonged standing", "type": "fixed"},
    {"line": "No h/o trauma", "type": "fixed"},
]
_plfa_exam = [
    {"line": "Tenderness over medial calcaneal tubercle", "type": "fixed"},
    {"line": "Pain on passive dorsiflexion of toes", "type": "fixed"},
    {"line": "No swelling or deformity", "type": "fixed"},
    {"line": "X-ray: Calcaneal spur noted", "type": "fixed"},
]
_plfa_impr = [
    {"line": "Plantar fasciitis, right foot, with calcaneal spur", "type": "fixed"},
]
_plfa_mgmt = [
    {"line": "Stretching exercises for plantar fascia and calf", "type": "fixed"},
    {"line": "Silicone heel cushion/orthotic insole", "type": "fixed"},
    {"line": "Activity modification advice", "type": "fixed"},
    {"line": "Review in ___ weeks if no improvement", "type": "slot", "slot_key": "plfa_review_wks", "value": None},
]
_plfa_rx = [
    {"drug": "Tab Aceclofenac + Paracetamol", "composition": "Aceclofenac 100mg + Paracetamol 325mg", "dosage": "1 tablet", "frequency": "1-0-1-0 (Morning & Evening)", "duration": "5 Days", "instructions": "After food", "type": "rx_fixed"},
    {"drug": "Diclofenac Gel 1%", "composition": "Diclofenac Diethylamine 1.16%", "dosage": "Local application", "frequency": "1-1-1-0 (Morning, Afternoon & Evening)", "duration": "7 Days", "instructions": "Apply locally over heel", "type": "rx_fixed"},
]
_plfa_lab = [
    {"line": "Serum Uric Acid", "type": "fixed"},
    {"line": "Vitamin D", "type": "fixed"},
]
_plfa_img = [
    {"line": "X-Ray Foot Lateral (heel spur view)", "type": "fixed"},
    {"line": "USG Plantar Fascia", "type": "fixed"},
]
_plfa_fu = [
    {"line": "Review in ___ weeks if no improvement", "type": "slot", "slot_key": "plfa_review_wks", "value": None},
    {"line": "Consider local steroid injection if pain persists", "type": "fixed"},
]

# ==========================================================================
# DIABETOLOGY / PULMONOLOGY / PEDIATRICS -- not from ortho templates_6699.md.
# Unrelated content, left untouched: these keep the older/simpler section set
# (complaints / advice / prescription / plan / follow_up_plan) and the 3-field
# prescription schema (drug / dose / notes).
# ==========================================================================

# DIABETOLOGY: T2DM
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

# PULMONOLOGY: ASTHMA
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

# PEDIATRICS: ARI
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
        "chief_complaint": _tkr_chief_complaint, "diagnosis": _tkr_diag,
        "history_complaints": _tkr_history, "examination_findings": _tkr_exam,
        "impression": _tkr_impr, "management_plan": _tkr_mgmt,
        "prescription": _tkr_rx, "lab_orders": _tkr_lab,
        "imaging_orders": _tkr_img, "follow_up_plan": _tkr_fu,
    },
    "ORT-TKR-RX-PF": {"prescription": _tkr_rx_pf},
    "ORT-TKR-RX-HIGH": {"prescription": _tkr_rx_high},

    "ORT-THR": {
        "chief_complaint": _thr_chief_complaint, "diagnosis": _thr_diag,
        "history_complaints": _thr_history, "examination_findings": _thr_exam,
        "impression": _thr_impr, "management_plan": _thr_mgmt,
        "prescription": _thr_rx, "lab_orders": _thr_lab,
        "imaging_orders": _thr_img, "follow_up_plan": _thr_fu,
    },
    "ORT-CSPN": {
        "chief_complaint": _cspn_chief_complaint, "diagnosis": _cspn_diag,
        "history_complaints": _cspn_history, "examination_findings": _cspn_exam,
        "impression": _cspn_impr, "management_plan": _cspn_mgmt,
        "prescription": _cspn_lspn_rx, "lab_orders": _cspn_lab,
        "imaging_orders": _cspn_img, "follow_up_plan": _cspn_fu,
    },
    "ORT-LSPN": {
        "chief_complaint": _lspn_chief_complaint, "diagnosis": _lspn_diag,
        "history_complaints": _lspn_history, "examination_findings": _lspn_exam,
        "impression": _lspn_impr, "management_plan": _lspn_mgmt,
        "prescription": _cspn_lspn_rx, "lab_orders": _lspn_lab,
        "imaging_orders": _lspn_img, "follow_up_plan": _lspn_fu,
    },
    "ORT-ACLR": {
        "chief_complaint": _aclr_chief_complaint, "diagnosis": _aclr_diag,
        "history_complaints": _aclr_history, "examination_findings": _aclr_exam,
        "impression": _aclr_impr, "management_plan": _aclr_mgmt,
        "prescription": _aclr_rx, "lab_orders": _aclr_lab,
        "imaging_orders": _aclr_img, "follow_up_plan": _aclr_fu,
    },
    "ORT-MENI": {
        "chief_complaint": _meni_chief_complaint, "diagnosis": _meni_diag,
        "history_complaints": _meni_history, "examination_findings": _meni_exam,
        "impression": _meni_impr, "management_plan": _meni_mgmt,
        "prescription": _meni_rx, "lab_orders": _meni_lab,
        "imaging_orders": _meni_img, "follow_up_plan": _meni_fu,
    },
    "ORT-RCUF": {
        "chief_complaint": _rcuf_chief_complaint, "diagnosis": _rcuf_diag,
        "history_complaints": _rcuf_history, "examination_findings": _rcuf_exam,
        "impression": _rcuf_impr, "management_plan": _rcuf_mgmt,
        "prescription": _rcuf_rx, "lab_orders": _rcuf_lab,
        "imaging_orders": _rcuf_img, "follow_up_plan": _rcuf_fu,
    },
    "ORT-ANKS": {
        "chief_complaint": _anks_chief_complaint, "diagnosis": _anks_diag,
        "history_complaints": _anks_history, "examination_findings": _anks_exam,
        "impression": _anks_impr, "management_plan": _anks_mgmt,
        "prescription": _anks_rx, "lab_orders": _anks_lab,
        "imaging_orders": _anks_img, "follow_up_plan": _anks_fu,
    },
    "ORT-FSF": {
        "chief_complaint": _fsf_chief_complaint, "diagnosis": _fsf_diag,
        "history_complaints": _fsf_history, "examination_findings": _fsf_exam,
        "impression": _fsf_impr, "management_plan": _fsf_mgmt,
        "prescription": _fsf_rx, "lab_orders": _fsf_lab,
        "imaging_orders": _fsf_img, "follow_up_plan": _fsf_fu,
    },
    "ORT-FDR": {
        "chief_complaint": _fdr_chief_complaint, "diagnosis": _fdr_diag,
        "history_complaints": _fdr_history, "examination_findings": _fdr_exam,
        "impression": _fdr_impr, "management_plan": _fdr_mgmt,
        "prescription": _fdr_rx, "lab_orders": _fdr_lab,
        "imaging_orders": _fdr_img, "follow_up_plan": _fdr_fu,
    },
    "ORT-FNF": {
        "chief_complaint": _fnf_chief_complaint, "diagnosis": _fnf_diag,
        "history_complaints": _fnf_history, "examination_findings": _fnf_exam,
        "impression": _fnf_impr, "management_plan": _fnf_mgmt,
        "prescription": _fnf_rx, "lab_orders": _fnf_lab,
        "imaging_orders": _fnf_img, "follow_up_plan": _fnf_fu,
    },
    "ORT-PIVD": {
        "chief_complaint": _pivd_chief_complaint, "diagnosis": _pivd_diag,
        "history_complaints": _pivd_history, "examination_findings": _pivd_exam,
        "impression": _pivd_impr, "management_plan": _pivd_mgmt,
        "prescription": _pivd_rx, "lab_orders": _pivd_lab,
        "imaging_orders": _pivd_img, "follow_up_plan": _pivd_fu,
    },
    "ORT-FRSH": {
        "chief_complaint": _frsh_chief_complaint, "diagnosis": _frsh_diag,
        "history_complaints": _frsh_history, "examination_findings": _frsh_exam,
        "impression": _frsh_impr, "management_plan": _frsh_mgmt,
        "prescription": _frsh_rx, "lab_orders": _frsh_lab,
        "imaging_orders": _frsh_img, "follow_up_plan": _frsh_fu,
    },
    "ORT-CTS": {
        "chief_complaint": _cts_chief_complaint, "diagnosis": _cts_diag,
        "history_complaints": _cts_history, "examination_findings": _cts_exam,
        "impression": _cts_impr, "management_plan": _cts_mgmt,
        "prescription": _cts_rx, "lab_orders": _cts_lab,
        "imaging_orders": _cts_img, "follow_up_plan": _cts_fu,
    },
    "ORT-PLFA": {
        "chief_complaint": _plfa_chief_complaint, "diagnosis": _plfa_diag,
        "history_complaints": _plfa_history, "examination_findings": _plfa_exam,
        "impression": _plfa_impr, "management_plan": _plfa_mgmt,
        "prescription": _plfa_rx, "lab_orders": _plfa_lab,
        "imaging_orders": _plfa_img, "follow_up_plan": _plfa_fu,
    },

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
