from fpdf import FPDF
from datetime import datetime

def clean_text(text_input) -> str:
    if not text_input:
        return "N/A"
    
    text_str = str(text_input).strip()
    
    replacements = {
        "•": "-", "·": "-", "◦": "-", "▪": "-", "●": "-",
        "—": "-", "–": "-", "“": '"', "”": '"', 
        "‘": "'", "’": "'", "…": "..."
    }
    for bad_char, good_char in replacements.items():
        text_str = text_str.replace(bad_char, good_char)
        
    # This line guarantees FPDF will never crash. It violently strips any non-ASCII character.
    return text_str.encode('ascii', errors='ignore').decode('ascii')

class SimpleEMRPDF(FPDF):
    def header(self):
        self.set_font("helvetica", style="B", size=16)
        self.set_text_color(13, 148, 136) 
        self.cell(0, 8, text=clean_text("CLINICAL ENCOUNTER RECORD"), align="C", ln=True)
        
        self.set_font("helvetica", style="I", size=9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, text=clean_text("Confidential Electronic Medical Record"), align="C", ln=True)
        
        self.set_line_width(0.5)
        self.set_draw_color(200, 200, 200)
        self.line(10, 25, 200, 25)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", style="I", size=8)
        self.set_text_color(128, 128, 128)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.set_x(10)
        self.cell(0, 10, text=clean_text(f"Generated securely on: {timestamp}"), align="L")
        self.set_x(0)
        self.cell(200, 10, text=clean_text(f"Page {self.page_no()}"), align="R")

def create_emr_pdf(data: dict) -> bytes:
    pdf = SimpleEMRPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    def add_section(title, content):
        if not content or str(content).strip() in ["", "N/A", "[]", "{}"]:
            return
        
        pdf.set_x(10)
        pdf.set_font("helvetica", style="B", size=11)
        pdf.set_text_color(13, 148, 136)
        pdf.cell(0, 8, text=clean_text(title), ln=True)
        
        pdf.set_font("helvetica", size=10)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 6, text=clean_text(content))
        pdf.ln(3)

    pdf.set_x(10)
    pdf.set_font("helvetica", style="B", size=10)
    pdf.set_fill_color(245, 247, 250)
    pdf.set_draw_color(220, 226, 230)
    
    visit_date = clean_text(data.get('visit_date', ''))
    doctor = clean_text(data.get('doctor', ''))
    
    pdf.cell(95, 10, text=f" Date of Service: {visit_date}", border=1, fill=True)
    pdf.cell(95, 10, text=f" Attending Provider: {doctor}", border=1, fill=True, ln=True)
    pdf.ln(6)

    add_section("Chief Complaint", data.get("chief_complaint"))
    add_section("Primary Diagnosis", data.get("diagnosis"))

    vitals = data.get("vitals", {})
    if isinstance(vitals, dict) and any(vitals.values()):
        def get_v(key):
            val = vitals.get(key)
            return str(val).strip() if val and str(val).strip() else "-"
        
        v_str = f"BP: {get_v('bp')} | Pulse: {get_v('pulse')} | SpO2: {get_v('spo2')} | Temp: {get_v('temp')} | Wt: {get_v('weight')} | Ht: {get_v('height')}"
        add_section("Vital Signs", v_str)

    add_section("Subjective (S)", data.get("subjective"))
    add_section("Objective (O)", data.get("objective"))
    add_section("Assessment (A)", data.get("assessment"))
    add_section("Plan (P)", data.get("plan"))

    pdf.set_x(10)
    pdf.set_font("helvetica", style="B", size=11)
    pdf.set_text_color(13, 148, 136)
    pdf.cell(0, 8, text=clean_text("Prescriptions (Rx)"), ln=True)
    
    pdf.set_font("helvetica", size=10)
    pdf.set_text_color(50, 50, 50)
    
    rx_list = data.get("rx_plan", [])
    
    if not rx_list:
        pdf.set_x(10)
        pdf.cell(0, 6, text="N/A", ln=True)
    else:
        for idx, rx in enumerate(rx_list, 1):
            if isinstance(rx, str):
                rx_str = f"  {idx}. {rx}"
            elif isinstance(rx, dict):
                drug = rx.get('drug', '')
                dose = rx.get('dose', '')
                timing = rx.get('timing', '')
                duration = rx.get('duration', '')
                parts = [p for p in [drug, dose, timing, duration] if p and p != 'N/A']
                rx_str = f"  {idx}. " + " | ".join(parts) if parts else f"  {idx}. {str(rx)}"
            else:
                rx_str = f"  {idx}. {str(rx)}"
            
            pdf.set_x(10)
            pdf.multi_cell(0, 6, text=clean_text(rx_str))

    pdf.ln(25)
    pdf.set_x(120)
    pdf.set_draw_color(100, 100, 100)
    pdf.line(120, pdf.get_y(), 190, pdf.get_y())
    
    pdf.set_x(120)
    pdf.set_font("helvetica", style="B", size=10)
    pdf.cell(70, 6, text="Electronically Signed By:", align="C", ln=True)
    
    pdf.set_x(120)
    pdf.set_font("helvetica", style="I", size=10)
    pdf.cell(70, 6, text=doctor, align="C", ln=True)

    return bytes(pdf.output())