"""
Clinical note -> PDF, in English, Telugu or Hindi.

Indic scripts need two things that are easy to get wrong:

1. Fonts with the right glyphs. The stock fpdf2 font (Helvetica) has no Telugu
   or Devanagari glyphs at all, so the old version of this file simply stripped
   every non-ASCII character -- a Telugu note would have come out blank.
   Noto Sans (Latin), Noto Sans Telugu and Noto Sans Devanagari are bundled in
   ./fonts and registered below.

2. Text shaping. Telugu and Devanagari need conjuncts formed and vowel marks
   reordered; without shaping you get disconnected glyph soup. fpdf2 does this
   via HarfBuzz, which is why `uharfbuzz` is a hard requirement, and why
   set_text_shaping(True) is set on every page.

Latin is the PRIMARY font with the Indic fonts as fallbacks, so a line like
"Tab Etoricoxib 90mg - 1 మాత్ర, భోజనం తర్వాత" renders the drug name in Latin and
the rest in Telugu, in one run. Drug names and compositions are deliberately
never translated -- a pharmacist has to read them.
"""

import os
from datetime import datetime

from fpdf import FPDF
from fpdf.enums import XPos, YPos

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

# Placeholder branding -- swap for the real clinic details before any real use.
CLINIC = {
    "name": "CONTEXTA HOSPITALS",
    "tagline": "Multi-Speciality Hospital  |  Hyderabad",
    "address": "Plot 42, Road No. 12, Banjara Hills, Hyderabad, Telangana 500034",
    "contact": "+91 40 6789 0000   |   care@contextahealth.com   |   www.contextaemr.com",
}

TEAL = (0, 135, 138)
INK = (33, 37, 41)
MUTED = (110, 118, 129)
RULE = (222, 226, 230)
BAND = (244, 248, 248)

LANGUAGES = ("en", "te", "hi")

# Section order = the order the note is laid out in, matching the on-screen document.
SECTION_ORDER = [
    "chief_complaint", "diagnosis", "history_complaints", "examination_findings",
    "impression", "management_plan", "complaints", "advice",
    "prescription", "lab_orders", "imaging_orders", "plan", "follow_up_plan",
]

SECTION_TITLES = {
    "en": {
        "chief_complaint": "Chief Complaint",
        "diagnosis": "Diagnosis (ICD-10)",
        "history_complaints": "History & Complaints",
        "examination_findings": "Examination & Findings",
        "impression": "Impression / Diagnosis",
        "management_plan": "Management Plan",
        "complaints": "Complaints",
        "advice": "Advice",
        "prescription": "Prescription (Rx)",
        "lab_orders": "Lab Orders",
        "imaging_orders": "Imaging Orders",
        "plan": "Plan",
        "follow_up_plan": "Follow-up Plan",
    },
    "te": {
        "chief_complaint": "ప్రధాన ఫిర్యాదు",
        "diagnosis": "వ్యాధి నిర్ధారణ (ICD-10)",
        "history_complaints": "చరిత్ర & ఫిర్యాదులు",
        "examination_findings": "పరీక్ష & పరిశీలనలు",
        "impression": "అభిప్రాయం / నిర్ధారణ",
        "management_plan": "చికిత్స ప్రణాళిక",
        "complaints": "ఫిర్యాదులు",
        "advice": "సలహా",
        "prescription": "మందుల చీటీ (Rx)",
        "lab_orders": "ల్యాబ్ పరీక్షలు",
        "imaging_orders": "స్కాన్ / ఎక్స్-రే",
        "plan": "ప్రణాళిక",
        "follow_up_plan": "తదుపరి సమీక్ష",
    },
    "hi": {
        "chief_complaint": "मुख्य शिकायत",
        "diagnosis": "निदान (ICD-10)",
        "history_complaints": "इतिहास एवं शिकायतें",
        "examination_findings": "जाँच एवं निष्कर्ष",
        "impression": "राय / निदान",
        "management_plan": "उपचार योजना",
        "complaints": "शिकायतें",
        "advice": "सलाह",
        "prescription": "दवा पर्ची (Rx)",
        "lab_orders": "लैब जाँच",
        "imaging_orders": "स्कैन / एक्स-रे",
        "plan": "योजना",
        "follow_up_plan": "अगली समीक्षा",
    },
}

LABELS = {
    "en": {
        "title": "CLINICAL ENCOUNTER RECORD",
        "patient": "Patient", "doctor": "Consulting Doctor",
        "date": "Date of Visit", "template": "Template",
        "signed": "Signature", "page": "Page",
        "generated": "Generated", "none": "Not recorded",
        "disclaimer": "This is a computer-generated clinical record. Verify all medication before dispensing.",
        "rx_cols": ["#", "Drug", "Composition", "Dosage", "Frequency", "Duration", "Instructions"],
    },
    "te": {
        "title": "వైద్య సంప్రదింపు నివేదిక",
        "patient": "రోగి", "doctor": "సంప్రదించిన వైద్యులు",
        "date": "సందర్శన తేదీ", "template": "టెంప్లేట్",
        "signed": "సంతకం", "page": "పేజీ",
        "generated": "రూపొందించినది", "none": "నమోదు కాలేదు",
        "disclaimer": "ఇది కంప్యూటర్ ద్వారా రూపొందించిన వైద్య నివేదిక. మందులు ఇచ్చే ముందు పరిశీలించండి.",
        "rx_cols": ["#", "మందు", "కూర్పు", "మోతాదు", "ఎప్పుడు", "కాలం", "సూచనలు"],
    },
    "hi": {
        "title": "चिकित्सकीय परामर्श रिकॉर्ड",
        "patient": "रोगी", "doctor": "परामर्श चिकित्सक",
        "date": "भेंट की तिथि", "template": "टेम्पलेट",
        "signed": "हस्ताक्षर", "page": "पृष्ठ",
        "generated": "निर्मित", "none": "दर्ज नहीं",
        "disclaimer": "यह कंप्यूटर द्वारा निर्मित चिकित्सा रिकॉर्ड है। दवा देने से पहले जाँच करें।",
        "rx_cols": ["#", "दवा", "संघटन", "मात्रा", "कब", "अवधि", "निर्देश"],
    },
}

# Prescription column widths (mm), summing to the 190mm content width.
RX_WIDTHS = [8, 36, 40, 22, 34, 20, 30]


class EMRPdf(FPDF):
    def __init__(self, lang: str):
        super().__init__(format="A4")
        self.lang = lang
        self.L = LABELS[lang]
        self.set_auto_page_break(auto=True, margin=22)
        self.set_margins(10, 10, 10)

        self.add_font("noto", "", os.path.join(FONT_DIR, "NotoSans-Regular.ttf"))
        self.add_font("noto", "B", os.path.join(FONT_DIR, "NotoSans-Bold.ttf"))
        self.add_font("telugu", "", os.path.join(FONT_DIR, "NotoSansTelugu-Regular.ttf"))
        self.add_font("telugu", "B", os.path.join(FONT_DIR, "NotoSansTelugu-Bold.ttf"))
        self.add_font("deva", "", os.path.join(FONT_DIR, "NotoSansDevanagari-Regular.ttf"))
        self.add_font("deva", "B", os.path.join(FONT_DIR, "NotoSansDevanagari-Bold.ttf"))
        # Latin drives the layout; Indic glyphs are pulled in as needed.
        self.set_fallback_fonts(["telugu", "deva"])

    def header(self):
        # HarfBuzz shaping -- without this Telugu/Devanagari conjuncts break apart.
        self.set_text_shaping(True)

        self.set_font("noto", "B", 17)
        self.set_text_color(*TEAL)
        self.cell(0, 8, CLINIC["name"], align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font("noto", "", 8.5)
        self.set_text_color(*MUTED)
        self.cell(0, 4.5, CLINIC["tagline"], align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 4.5, CLINIC["address"], align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 4.5, CLINIC["contact"], align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.ln(2)
        self.set_draw_color(*TEAL)
        self.set_line_width(0.7)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

        self.set_font("noto", "B", 10.5)
        self.set_text_color(*INK)
        self.cell(0, 6, self.L["title"], align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def footer(self):
        self.set_y(-18)
        self.set_text_shaping(True)
        self.set_draw_color(*RULE)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(1.5)

        self.set_font("noto", "", 7)
        self.set_text_color(*MUTED)
        self.cell(0, 4, self.L["disclaimer"], align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Numeric date on purpose. An English month abbreviation ("Jul") has no
        # business in a Telugu or Hindi note, and digits are the one thing all
        # three fonts render identically.
        stamp = datetime.now().strftime("%d-%m-%Y  %H:%M")
        self.set_font("noto", "", 7)
        self.cell(95, 4, f"{self.L['generated']}: {stamp}", align="L")
        self.set_font("noto", "", 7)
        self.cell(95, 4, f"{self.L['page']} {self.page_no()}/{{nb}}", align="R")


def _meta_box(pdf: EMRPdf, patient: str, doctor: str, visit_date: str, template_id: str):
    """Patient / doctor / date / template band under the header."""
    L = pdf.L
    pairs = [
        (L["patient"], patient or L["none"]),
        (L["doctor"], doctor or L["none"]),
        (L["date"], visit_date or L["none"]),
        (L["template"], template_id or L["none"]),
    ]
    pdf.set_fill_color(*BAND)
    pdf.set_draw_color(*RULE)
    pdf.set_line_width(0.2)

    top = pdf.get_y()
    pdf.rect(10, top, 190, 16, style="DF")

    col_w = 190 / 4
    for i, (label, value) in enumerate(pairs):
        x = 10 + i * col_w
        pdf.set_xy(x + 3, top + 2.5)
        pdf.set_font("noto", "", 7)
        pdf.set_text_color(*MUTED)
        pdf.cell(col_w - 6, 4, label.upper(), new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.set_x(x + 3)
        pdf.set_font("noto", "B", 9.5)
        pdf.set_text_color(*INK)
        pdf.cell(col_w - 6, 5.5, str(value))
    pdf.set_y(top + 16)
    pdf.ln(5)


def _section_heading(pdf: EMRPdf, title: str):
    if pdf.get_y() > 250:
        pdf.add_page()
    pdf.set_font("noto", "B", 10)
    pdf.set_text_color(*TEAL)
    pdf.cell(0, 6, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(*TEAL)
    pdf.set_line_width(0.3)
    y = pdf.get_y()
    pdf.line(10, y, 200, y)
    pdf.ln(2)


def _bullets(pdf: EMRPdf, lines: list):
    pdf.set_font("noto", "", 9.5)
    pdf.set_text_color(*INK)
    for line in lines:
        if not line:
            continue
        pdf.set_x(12)
        pdf.multi_cell(186, 5.2, f"•  {line}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)


def _rx_table(pdf: EMRPdf, rows: list):
    """The prescription table, six source columns wide."""
    cols = pdf.L["rx_cols"]

    def head():
        pdf.set_font("noto", "B", 7.5)
        pdf.set_fill_color(*TEAL)
        pdf.set_text_color(255, 255, 255)
        pdf.set_x(10)
        for w, c in zip(RX_WIDTHS, cols):
            pdf.cell(w, 7, f" {c}", border=0, fill=True)
        pdf.ln(7)

    head()
    pdf.set_font("noto", "", 7.5)
    pdf.set_text_color(*INK)
    pdf.set_draw_color(*RULE)

    for i, r in enumerate(rows, 1):
        cells = [
            str(i), r.get("drug", ""), r.get("composition", ""), r.get("dosage", ""),
            r.get("frequency", ""), r.get("duration", ""), r.get("instructions", ""),
        ]
        # How tall does this row need to be? Take the tallest wrapped cell.
        lines_needed = 1
        for w, txt in zip(RX_WIDTHS, cells):
            if txt:
                lines_needed = max(lines_needed, len(pdf.multi_cell(w - 2, 4, txt, dry_run=True, output="LINES")))
        h = max(6.5, lines_needed * 4 + 2.5)

        if pdf.get_y() + h > 265:
            pdf.add_page()
            head()
            pdf.set_font("noto", "", 7.5)
            pdf.set_text_color(*INK)

        y0 = pdf.get_y()
        x = 10
        if i % 2 == 0:
            pdf.set_fill_color(250, 252, 252)
            pdf.rect(10, y0, sum(RX_WIDTHS), h, style="F")

        for w, txt in zip(RX_WIDTHS, cells):
            pdf.set_xy(x, y0 + 1.2)
            pdf.multi_cell(w, 4, txt, align="L")
            x += w

        pdf.set_y(y0 + h)
        pdf.set_draw_color(*RULE)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())

    pdf.ln(4)


def _signature(pdf: EMRPdf, doctor: str):
    if pdf.get_y() > 225:
        pdf.add_page()
    pdf.ln(10)
    y = pdf.get_y()
    pdf.set_draw_color(*INK)
    pdf.set_line_width(0.3)
    pdf.line(140, y, 200, y)

    pdf.set_xy(140, y + 1)
    pdf.set_font("noto", "B", 9)
    pdf.set_text_color(*INK)
    pdf.cell(60, 5, doctor or "", align="C", new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.set_x(140)
    pdf.set_font("noto", "", 7.5)
    pdf.set_text_color(*MUTED)
    pdf.cell(60, 4, pdf.L["signed"], align="C")


def create_emr_pdf(data: dict) -> bytes:
    """
    data = {
        visit_date, doctor, patient, template_id, language ("en"|"te"|"hi"),
        clinical_data: { section_name: [ {rendered_line|drug,...}, ... ] }
    }
    `clinical_data` is whatever the doctor currently has on screen, edits and
    all -- the caller sends the live document, so the PDF always matches it.
    """
    lang = data.get("language", "en")
    if lang not in LANGUAGES:
        lang = "en"

    titles = SECTION_TITLES[lang]
    doc = data.get("clinical_data") or {}

    pdf = EMRPdf(lang)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_text_shaping(True)

    _meta_box(
        pdf,
        patient=str(data.get("patient", "")).strip(),
        doctor=str(data.get("doctor", "")).strip(),
        visit_date=str(data.get("visit_date", "")).strip(),
        template_id=str(data.get("template_id", "")).strip(),
    )

    for section in SECTION_ORDER:
        items = doc.get(section)
        if not items:
            continue

        _section_heading(pdf, titles.get(section, section))

        if section == "prescription":
            _rx_table(pdf, items)
        else:
            _bullets(pdf, [str(it.get("rendered_line", "")).strip() for it in items])

    _signature(pdf, str(data.get("doctor", "")).strip())

    return bytes(pdf.output())
