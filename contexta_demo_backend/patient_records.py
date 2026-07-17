"""Static patient records for the internal Doctor Assistant (/doctor) ONLY.

GENERATED FILE -- do not edit by hand. Run `python gen_patient_records.py` instead;
the source of truth is the markdown at the repo root.

Kept separate from ortho_clinic_data.py (ChatBot) and doctors_data.py (Visit
Notes) so changes here can never touch either shipped feature. Read-only.

This is the raw chart -- three patients' visit histories plus the surgical
schedule. There is no answer key and no retrieval step: the whole thing is ~1% of
Sonnet's 1M window, so it goes into the cached system prompt verbatim and the
model derives each answer by reading it. See doctor_service.py.
"""

# Reference "today" for every relative query ("last week", "next week").
# Deliberately frozen rather than a live clock: the records describe a fixed
# window (surgeries Jan-Aug 2026), so a real clock would drift out of them and
# make "next week" empty. It also keeps the prompt byte-stable, which is what
# lets the whole thing cache.
REFERENCE_DATE = "Thursday, 16 July 2026"

RECORDS_MD = r'''
# Internal Doctor Chatbot — Context File (Sample/POC)

> **This is a separate product from the WhatsApp patient chatbot** (covered in `ortho_clinic_chatbot_context.md` and related files). That one is patient-facing, on WhatsApp, for booking/timings/directions. **This one is an internal widget docked at the bottom of the EMR screen, for doctors only** — built to demo at the summit stall, showing visiting doctors what the system can answer about their own patients and their own surgical schedule via natural-language query. Reference "today" = **Thursday, 16-Jul-2026**.

---

# PART A — Patient Records

## A1. Patient Master Records

| Attribute | Patient 1 | Patient 2 | Patient 3 |
|---|---|---|---|
| Name | Venkata Ramana | Lakshmi Devi | Ganesan Pillai |
| Age | 58 | 52 | 64 |
| Sex | Male | Female | Male |
| Date of Birth | 14-Mar-1968 | 22-Jul-1974 | 05-Nov-1961 |
| Height | 168 cm | 155 cm | 165 cm |
| Weight (latest) | 82 kg | 68 kg | 71 kg |
| BMI (latest) | 29.1 | 28.3 | 26.1 |
| Primary Condition | Hypertension | Type 2 Diabetes Mellitus | Chronic Kidney Disease (Stage 3) |
| Known Allergies | None reported | Penicillin — rash | None reported |
| Next Appointment | 15-Aug-2026 | 20-Sep-2026 | 05-Aug-2026 |

## A2. Visit History — Venkata Ramana (Hypertension)

**Visit 1 — 12-Aug-2024**
- Weight: 85 kg | BMI: 30.1 | BP: 152/96 mmHg
- Hemoglobin: 14.2 g/dL | WBC: 7200/uL | Platelets: 2.4 lakh/uL
- Total Cholesterol: 210 mg/dL | LDL: 138 mg/dL | HDL: 42 mg/dL | Triglycerides: 165 mg/dL
- Serum Creatinine: 1.0 mg/dL
- Medications: Tab Amlodipine 5mg OD, Tab Atorvastatin 10mg OD (night)
- Doctor's Note: Newly diagnosed hypertension; lifestyle advice given

**Visit 2 — 15-Feb-2025**
- Weight: 84 kg | BMI: 29.8 | BP: 144/90 mmHg
- Hemoglobin: 14.0 g/dL | WBC: 7500/uL | Platelets: 2.5 lakh/uL
- Serum Creatinine: 1.0 mg/dL
- Medications: Continue Amlodipine 5mg OD, Atorvastatin 10mg OD
- Doctor's Note: BP improving, continue same regimen

**Visit 3 — 20-Aug-2025**
- Weight: 83 kg | BMI: 29.4 | BP: 138/88 mmHg
- Hemoglobin: 14.1 g/dL | WBC: 7100/uL | Platelets: 2.6 lakh/uL
- Total Cholesterol: 195 mg/dL | LDL: 122 mg/dL | HDL: 45 mg/dL | Triglycerides: 148 mg/dL
- Thyroid (TSH): 2.8 uIU/mL (normal)
- Serum Creatinine: 1.1 mg/dL
- Medications: Amlodipine increased to 10mg OD; continue Atorvastatin 10mg OD
- Doctor's Note: BP still mildly elevated, dose increased

**Visit 4 — 10-Feb-2026**
- Weight: 82 kg | BMI: 29.1 | BP: 130/84 mmHg
- Hemoglobin: 14.3 g/dL | WBC: 6900/uL | Platelets: 2.5 lakh/uL
- Serum Creatinine: 1.0 mg/dL
- Medications: Continue Amlodipine 10mg OD, Atorvastatin 10mg OD
- Doctor's Note: BP well controlled, continue current regimen

## A3. Visit History — Lakshmi Devi (Type 2 Diabetes)

**Visit 1 — 05-Sep-2024**
- Weight: 72 kg | BMI: 30.0 | BP: 128/82 mmHg
- Hemoglobin: 12.8 g/dL | WBC: 6800/uL | Platelets: 2.7 lakh/uL
- Fasting Blood Sugar: 168 mg/dL | HbA1c: 8.2%
- Total Cholesterol: 220 mg/dL | LDL: 145 mg/dL | HDL: 38 mg/dL | Triglycerides: 210 mg/dL
- Serum Creatinine: 0.8 mg/dL
- Allergy noted this visit: Penicillin — rash
- Medications: Tab Metformin 500mg BD
- Doctor's Note: Newly diagnosed Type 2 DM; dietary counseling given

**Visit 2 — 18-Mar-2025**
- Weight: 70 kg | BMI: 29.1 | BP: 126/80 mmHg
- HbA1c: 7.6%
- Hemoglobin: 12.9 g/dL | WBC: 7000/uL | Platelets: 2.6 lakh/uL
- Serum Creatinine: 0.8 mg/dL
- Medications: Continue Metformin 500mg BD; added Tab Glimepiride 1mg OD
- Doctor's Note: Sugar still above target, added second agent

**Visit 3 — 25-Sep-2025**
- Weight: 69 kg | BMI: 28.7 | BP: 124/78 mmHg
- HbA1c: 7.1%
- Hemoglobin: 13.0 g/dL | WBC: 6700/uL | Platelets: 2.8 lakh/uL
- Total Cholesterol: 198 mg/dL | LDL: 118 mg/dL | HDL: 42 mg/dL | Triglycerides: 165 mg/dL
- Thyroid (TSH): 3.4 uIU/mL (normal)
- Serum Creatinine: 0.9 mg/dL
- Medications: Continue Metformin 500mg BD + Glimepiride 1mg OD
- Doctor's Note: Improving steadily, continue

**Visit 4 — 12-Mar-2026**
- Weight: 68 kg | BMI: 28.3 | BP: 122/78 mmHg
- HbA1c: 6.8%
- Hemoglobin: 13.1 g/dL | WBC: 6900/uL | Platelets: 2.7 lakh/uL
- Serum Creatinine: 0.8 mg/dL
- Medications: Continue Metformin 500mg BD + Glimepiride 1mg OD
- Doctor's Note: Good glycemic control achieved

## A4. Visit History — Ganesan Pillai (Chronic Kidney Disease)

**Visit 1 — 20-Jul-2024**
- Weight: 74 kg | BMI: 27.2 | BP: 148/92 mmHg
- Hemoglobin: 11.2 g/dL | WBC: 7300/uL | Platelets: 2.3 lakh/uL
- Serum Creatinine: 1.8 mg/dL | eGFR: 42 mL/min/1.73m² (Stage 3 CKD)
- Serum Urea: 48 mg/dL
- Total Cholesterol: 205 mg/dL | LDL: 130 mg/dL | HDL: 40 mg/dL | Triglycerides: 178 mg/dL
- Medications: Tab Telmisartan 40mg OD, Tab Sodium Bicarbonate 500mg BD
- Doctor's Note: CKD Stage 3, secondary to long-standing hypertension; nephrology referral given

**Visit 2 — 05-Jan-2025**
- Weight: 73 kg | BMI: 26.8 | BP: 142/88 mmHg
- Hemoglobin: 11.0 g/dL | WBC: 7100/uL | Platelets: 2.4 lakh/uL
- Serum Creatinine: 1.9 mg/dL | eGFR: 40 mL/min/1.73m²
- Serum Urea: 50 mg/dL
- Medications: Continue Telmisartan 40mg OD, Sodium Bicarbonate 500mg BD
- Doctor's Note: Stable, continue monitoring

**Visit 3 — 15-Jul-2025**
- Weight: 72 kg | BMI: 26.4 | BP: 136/86 mmHg
- Hemoglobin: 10.8 g/dL | WBC: 7200/uL | Platelets: 2.5 lakh/uL
- Serum Creatinine: 2.0 mg/dL | eGFR: 38 mL/min/1.73m²
- Thyroid (TSH): 4.1 uIU/mL (borderline)
- Medications: Telmisartan increased to 80mg OD; continue Sodium Bicarbonate 500mg BD; added Tab Ferrous Ascorbate + Folic Acid OD (mild anemia)
- Doctor's Note: Creatinine trending up slowly, mild anemia noted, iron supplementation started

**Visit 4 — 28-Jan-2026**
- Weight: 71 kg | BMI: 26.1 | BP: 132/84 mmHg
- Hemoglobin: 11.1 g/dL | WBC: 6900/uL | Platelets: 2.4 lakh/uL
- Serum Creatinine: 1.9 mg/dL | eGFR: 41 mL/min/1.73m²
- Medications: Continue Telmisartan 80mg OD, Sodium Bicarbonate 500mg BD, Ferrous Ascorbate + Folic Acid OD
- Doctor's Note: Creatinine stable, anemia improving, continue current management

---

# PART B — Surgery Schedule (Dr. Suresh Kumar Nair)

> Dr. Suresh Kumar Nair — Joint Replacement & Sports Injury Surgeon. Surgery types: **TKR, THR, ACL Reconstruction, Meniscus Repair**.

## B1. Monthly Summary — Last 6 Months

| Month | TKR | THR | ACL Reconstruction | Meniscus Repair | Total |
|---|---|---|---|---|---|
| Jan 2026 | 2 | 2 | 0 | 1 | 5 |
| Feb 2026 | 3 | 1 | 1 | 0 | 5 |
| Mar 2026 | 2 | 2 | 1 | 1 | 6 |
| Apr 2026 | 3 | 2 | 1 | 1 | 7 |
| May 2026 | 2 | 3 | 1 | 1 | 7 |
| Jun 2026 | 4 | 2 | 1 | 1 | 8 |
| **Last 3 months (Apr–Jun)** | **9** | **7** | **3** | **3** | **22** |
| **Last 6 months (Jan–Jun)** | **16** | **12** | **5** | **5** | **38** |

## B2. Last Month Detail — June 2026 (patient-level)

| Date | Patient | Surgery |
|---|---|---|
| 03-Jun-2026 (Wed) | Nagendra Prasad | TKR — left knee |
| 05-Jun-2026 (Fri) | Vijayalakshmi Rao | THR — right hip |
| 10-Jun-2026 (Wed) | Chandrasekhar Reddy | TKR — right knee |
| 12-Jun-2026 (Fri) | Anitha Krishnan | ACL Reconstruction — left knee |
| 17-Jun-2026 (Wed) | Ramachandra Murthy | TKR — left knee (staged bilateral, right knee planned later) |
| 19-Jun-2026 (Fri) | Saraswati Iyengar | THR — left hip |
| 24-Jun-2026 (Wed) | Bhaskar Naidu | Meniscus Repair — right knee |
| 26-Jun-2026 (Fri) | Padma Priya | TKR — left knee |

*TKRs last month: Nagendra Prasad, Chandrasekhar Reddy, Ramachandra Murthy, Padma Priya — 4 total.*

## B3. Last Week Detail — 06-Jul-2026 to 12-Jul-2026

| Date | Patient | Surgery |
|---|---|---|
| 07-Jul-2026 (Tue) | Srinivasan Nair | TKR — right knee |
| 09-Jul-2026 (Thu) | Kamala Bhat | THR — right hip |
| 11-Jul-2026 (Sat) | Devika Menon | ACL Reconstruction — right knee |

Total last week: **3 surgeries** (TKR 1, THR 1, ACL 1)

## B4. Upcoming Schedule — Next 2 Weeks (17-Jul-2026 to 30-Jul-2026)

**Next week (20-Jul to 26-Jul-2026):**
| Date | Patient | Surgery | Status |
|---|---|---|---|
| 21-Jul-2026 (Tue) | Raghunath Chowdary | TKR — left knee | Pre-op clearance done |
| 23-Jul-2026 (Thu) | Meenakshi Sundaram | THR — left hip | Pre-op clearance pending |
| 25-Jul-2026 (Sat) | Harish Gowda | Meniscus Repair — left knee | Scheduled |

**Week after (27-Jul to 02-Aug-2026):**
| Date | Patient | Surgery | Status |
|---|---|---|---|
| 28-Jul-2026 (Tue) | Lakshmana Rao | TKR — right knee | Scheduled |
| 30-Jul-2026 (Thu) | Sowmya Iyer | ACL Reconstruction — left knee | Pre-op clearance pending |

**Next 2 weeks total: 5 surgeries** (TKR 2, THR 1, ACL 1, Meniscus 1)

## B5. Further Ahead (for "next month" style queries — Aug 2026)

| Date | Patient | Surgery | Status |
|---|---|---|---|
| 04-Aug-2026 (Tue) | Krishnamurthy Achar | THR — right hip | Scheduled |
| 06-Aug-2026 (Thu) | Deepa Rajan | TKR — left knee | Scheduled |
| 08-Aug-2026 (Sat) | Mohan Das | TKR — right knee | Scheduled |
| 11-Aug-2026 (Tue) | Vasantha Kumari | THR — left hip | Scheduled |
| 18-Aug-2026 (Tue) | Ravindranath Pillai | TKR — right knee | Scheduled |
| 20-Aug-2026 (Thu) | Anjali Subramaniam | Meniscus Repair — right knee | Scheduled |
| 25-Aug-2026 (Tue) | Srikanth Reddy | THR — right hip | Scheduled |
| 27-Aug-2026 (Thu) | Padmini Venkatesh | TKR — left knee | Scheduled |

**August 2026 total: 8 surgeries** (TKR 4, THR 3, ACL 0, Meniscus 1)

## B6. Dr. Suresh Kumar Nair's Appointments (OPD, next 2 weeks)

| Date | Location | Timings |
|---|---|---|
| 20-Jul-2026 (Mon) | Gachibowli | 12:00 PM – 3:00 PM |
| 21-Jul-2026 (Tue) | KPHB | 11:00 AM – 2:00 PM (surgery day — OPD slot before/after) |
| 24-Jul-2026 (Fri) | KPHB | 11:00 AM – 2:00 PM |
| 25-Jul-2026 (Sat) | Dilsukhnagar | 1:00 PM – 4:00 PM (surgery day) |
| 27-Jul-2026 (Mon) | Gachibowli | 12:00 PM – 3:00 PM |

*(Pulled from the OrthoCare clinic visiting-specialist schedule — same doctor, same recurring weekly pattern.)*

---

# PART C — Sample NLP Queries & Expected Output Format

| Doctor asks | Expected response format |
|---|---|
| "How has Venkata Ramana's weight changed over his last few visits?" | Table: Visit Date, Weight, BMI |
| "How is Lakshmi Devi's lipid profile trending?" | Table: Visit Date, Total Cholesterol, LDL, HDL, Triglycerides |
| "How is the serum creatinine changing for Ganesan Pillai?" | Table: Visit Date, Serum Creatinine, eGFR |
| "Give me a detailed review of the CBC for Venkata Ramana" | Table: Visit Date, Hemoglobin, WBC, Platelets |
| "How is serum creatinine changing over time for Ganesan Pillai, and what medications were used during this time?" | Combined table: Visit Date, Serum Creatinine, Medications that visit |
| "Does Lakshmi Devi have any allergies?" | Direct answer: "Penicillin — rash, noted on 05-Sep-2024" |
| "When is Venkata Ramana visiting next?" | Direct answer: next appointment date |
| "Summarize Lakshmi Devi's diabetes control over the past year" | Table: Visit Date, HbA1c, Medications |
| "How's my next week looking?" | Day-by-day agenda: surgeries (Section B4) + OPD appointments (Section B6) combined |
| "How many surgeries do I have next week?" | Count + breakdown by type |
| "How many surgeries do I have in the next 2 weeks?" | Count + breakdown (Section B4 total) |
| "How many surgeries did I perform last week?" | Count + breakdown (Section B3) |
| "How many surgeries did I perform last month?" | Count + breakdown (Section B2) |
| "How many surgeries have I done in the last 3 months?" | Monthly trend table (Section B1) |
| "List the TKRs I did last month, with patient names" | Patient-level list, filtered (Section B2) |
| "How many ACL reconstructions have I done in the last 6 months?" | Filtered count, summed from Section B1 |
'''

