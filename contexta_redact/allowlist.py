"""
Clinical terms that must never be redacted.

Presidio's `allow_list` drops any detection whose matched text appears here. It
treats the symptom, not the cause: spaCy will keep guessing PERSON on every
assay method it has not seen, and this list only covers what you enumerate.
The cure is a clinical NER model (see engine.py, --nlp-engine transformers).

Seed the drug and condition sections from your own tables:

    SELECT DISTINCT drug_name FROM core.patient_medications;
    SELECT DISTINCT condition_name FROM core.patient_conditions;

A term here is a term that will NEVER be redacted. Do not add anything that
could also be a patient's name -- "Mercy", "Grace" and "Sunitha" are all real
Indian given names as well as plausible hospital or drug names.
"""

# Units of measure. Closed set, safe to allow wholesale.
UNITS = [
    "mg/dL", "g/dL", "mg/L", "g/L", "ng/mL", "pg/mL", "ug/dL", "mcg/dL",
    "U/L", "IU/L", "mIU/L", "mIU/mL", "mmol/L", "umol/L", "mEq/L", "nmol/L",
    "cells/cumm", "cells/uL", "million/cumm", "lakhs/cumm", "/cumm", "/uL",
    "fL", "pg", "mm/hr", "mg", "ml", "mL", "mcg", "gm", "kg", "cm", "mmHg",
    "%", "ratio", "Ratio", "sec", "INR",
]

# Lab test and panel names. The LFT/KFT/CBC/lipid/thyroid core.
LAB_TESTS = [
    "Total Bilirubin", "Direct Bilirubin", "Indirect Bilirubin",
    "Alanine Aminotransferase", "Aspartate Aminotransferase",
    "ALT", "SGPT", "AST", "SGOT", "ALT/SGPT", "AST/SGOT", "AST/ALT Ratio",
    "Alkaline Phosphatase", "ALP", "Gamma GT", "GGT",
    "Total Protein", "Albumin", "Globulin", "A/G Ratio", "A/GRatio",
    "Liver Function Test", "LFT", "Kidney Function Test", "KFT",
    "Urea", "Creatinine", "Uric Acid", "BUN", "eGFR",
    "Sodium", "Potassium", "Chloride", "Bicarbonate", "Calcium", "Phosphorus",
    "Magnesium", "Iron", "Ferritin", "Transferrin",
    "Haemoglobin", "Hemoglobin", "Hb", "HbA1c", "Glycated Haemoglobin",
    "Total Leucocyte Count", "TLC", "Differential Leucocyte Count", "DLC",
    "Platelet Count", "RBC Count", "PCV", "MCV", "MCH", "MCHC", "RDW",
    "Neutrophils", "Lymphocytes", "Monocytes", "Eosinophils", "Basophils",
    "Erythrocyte Sedimentation Rate", "ESR",
    "Total Cholesterol", "Triglycerides", "HDL Cholesterol", "LDL Cholesterol",
    "VLDL Cholesterol", "Lipid Profile",
    "Thyroid Stimulating Hormone", "TSH", "T3", "T4", "Free T3", "Free T4",
    "Fasting Blood Sugar", "FBS", "Post Prandial Blood Sugar", "PPBS",
    "Random Blood Sugar", "RBS", "Vitamin D", "Vitamin B12",
    "C Reactive Protein", "CRP", "Prothrombin Time", "PT", "APTT",
]

# Assay methods. These are the worst offenders -- proper-noun shaped and
# entirely absent from general-purpose NER training data.
LAB_METHODS = [
    "Diazo", "Diazo Method", "Biuret", "Bromocresol Green", "BCG",
    "PNPP", "PNPP-AMP", "PNPP-AMP Buffer", "AMP Buffer", "GCNA",
    "Calculated", "Colorimetric", "Enzymatic", "Kinetic", "Turbidimetric",
    "Immunoturbidimetry", "Nephelometry", "Chemiluminescence", "CLIA",
    "ELISA", "HPLC", "Photometric", "Potentiometric", "ISE",
    "UV wtihout P5P", "UV without P5P", "P5P", "Jaffe", "Jaffe Method",
    # "wtihout" is a real typo in the Tenet reports, tagged PERSON at 0.43.
    # Listed because the enclosing token IS the misspelling -- widening the span
    # cannot reach a longer allowed term. Both spellings, since the lab may fix it.
    "wtihout", "without",
    "Urease", "GOD-POD", "Hexokinase", "Flow Cytometry", "Impedance",
    "Westergren", "Sysmex", "Modified Westergren",
]

# Report furniture: section headers and form labels that NER reads as orgs.
REPORT_TERMS = [
    "DEPARTMENT OF CLINICAL CHEMISTRY", "DEPARTMENT OF BIOCHEMISTRY",
    "DEPARTMENT OF HAEMATOLOGY", "DEPARTMENT OF PATHOLOGY",
    "DEPARTMENT OF MICROBIOLOGY", "CLINICAL CHEMISTRY", "BIOCHEMISTRY",
    "HAEMATOLOGY", "HEMATOLOGY", "PATHOLOGY", "SEROLOGY", "MICROBIOLOGY",
    "Investigation", "Observed Value", "Biological Reference Interval",
    "Reference Range", "Result", "Units", "Method", "Interpretation",
    "Note", "Comments", "Specimen", "Sample Type", "Consultant Biochemist",
    "Consultant Pathologist", "End of Report", "Kindly correlate clinically",
]

# Abbreviations Presidio's URL recognizer reads as domains (.no = Norway).
FORM_ABBREVIATIONS = [
    "Reg.No", "Req.No", "Ref.By", "Sr.No", "S.No", "Sl.No", "Reg.no", "Req.no",
    "Dept.No", "Bill.No", "Lab.No", "Acc.No",
]

# Starter drug list. REPLACE from core.patient_medications -- this is a
# placeholder, not a formulary.
COMMON_DRUGS = [
    "Metformin", "Telmisartan", "Amlodipine", "Atorvastatin", "Rosuvastatin",
    "Losartan", "Ramipril", "Glimepiride", "Sitagliptin", "Insulin",
    "Levothyroxine", "Pantoprazole", "Omeprazole", "Aspirin", "Clopidogrel",
    "Paracetamol", "Ibuprofen", "Amoxicillin", "Azithromycin", "Cefixime",
    "Dolo", "Shelcal", "Augmentin", "Pan-D", "Ecosprin", "Thyronorm",
]


def clinical_allow_list(extra: list = None) -> list:
    """
    Everything above, de-duplicated, longest-first.

    Longest-first matters: Presidio compares against detected span text, so
    "Aspartate Aminotransferase" must be tried before "Aspartate".
    """
    terms = (
        UNITS + LAB_TESTS + LAB_METHODS + REPORT_TERMS
        + FORM_ABBREVIATIONS + COMMON_DRUGS + list(extra or [])
    )
    return sorted(set(terms), key=len, reverse=True)


def load_extra_terms(path: str) -> list:
    """One term per line; blank lines and `#` comments ignored."""
    with open(path, encoding="utf-8") as fh:
        return [
            line.strip()
            for line in fh
            if line.strip() and not line.lstrip().startswith("#")
        ]
