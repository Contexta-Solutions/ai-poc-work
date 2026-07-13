import copy
from typing import Dict, Any, List

from clinical_data import TEMPLATE_SECTIONS

class ClinicalTemplate:
    def __init__(self, template_id: str):
        self.template_id = template_id if template_id else "Generic Consultation"
        self.sections: Dict[str, List[Dict[str, Any]]] = {
            "chief_complaint": [],
            "diagnosis": [{"line": self.template_id, "type": "fixed"}],
            "history_complaints": [],
            "examination_findings": [],
            "impression": [],
            "management_plan": [],
            "complaints": [],
            "advice": [],
            "prescription": [],
            "lab_orders": [],
            "imaging_orders": [],
            "plan": [],
            "follow_up_plan": []
        }

        if template_id:
            self._load_base_template()

    def _load_base_template(self):
        for sec_name, items in TEMPLATE_SECTIONS.get(self.template_id, {}).items():
            if sec_name in self.sections:
                self.sections[sec_name] = copy.deepcopy(items)

    def set_prescriptions(self, prescriptions: List[Dict[str, str]]):
        """Append LLM-extracted prescriptions to existing template defaults."""
        for rx in prescriptions:
            drug = rx.get("drug", "").strip()
            dose = rx.get("dose", "").strip()
            notes = rx.get("notes", "").strip()
            if not drug:
                continue
            rendered = drug
            if dose:
                rendered += f" | {dose}"
            if notes:
                rendered += f" | {notes}"
            self.sections["prescription"].append({
                "drug": drug,
                "dose": dose,
                "notes": notes,
                "type": "extracted",
                "rendered_line": rendered
            })

    def override_section(self, variant_id: str, section_name: str):
        if not variant_id or section_name not in self.sections:
            return
        items = TEMPLATE_SECTIONS.get(variant_id, {}).get(section_name)
        if items is not None:
            self.sections[section_name] = copy.deepcopy(items)

    def extend_section(self, section_name: str, new_item: Dict[str, Any]):
        if section_name in self.sections:
            self.sections[section_name].append({
                "name": new_item.get("item_name", "Clinical Delta"),
                "value": new_item.get("value", ""),
                "type": "extended"
            })

    def fill_slots(self, extracted_entities: Dict[str, Any]):
        if not extracted_entities:
            return
        for section, items in self.sections.items():
            for item in items:
                if item.get("type") in ["slot", "rx_slot"]:
                    slot_key = item.get("slot_key")
                    if slot_key in extracted_entities and extracted_entities[slot_key] is not None:
                        item["value"] = str(extracted_entities[slot_key])

    def export(self) -> Dict[str, Any]:
        cleaned_sections = {}
        for sec_name, items in self.sections.items():
            valid_items = []
            for item in items:
                if item.get("type") == "extracted":
                    # Doctor-dictated medicine, appended via set_prescriptions() --
                    # only has drug/dose/notes. Backfill the 6-column Rx schema so
                    # the frontend table can render it alongside rx_fixed rows.
                    item.setdefault("composition", "")
                    item["dosage"] = item.get("dosage") or item.get("dose", "")
                    item.setdefault("frequency", "")
                    item.setdefault("duration", "")
                    item["instructions"] = item.get("instructions") or item.get("notes", "")

                # 1. Standard Template Sentences with Blanks. The line ALWAYS
                # renders -- the template loads whole. If the dictation supplied
                # the value it's filled in; otherwise the "___" blank stays put
                # for the doctor to fill in by hand in the UI.
                elif item.get("type") == "slot":
                    val = item.get("value")
                    item["rendered_line"] = item["line"].replace("___", str(val)) if val else item["line"]

                # 2. Fixed Sentences
                elif item.get("type") == "fixed":
                    item["rendered_line"] = item["line"]

                # 3. Rx Table: Fixed Drugs -- 6-column schema (composition/dosage/
                # frequency/duration/instructions) for the ortho templates, or the
                # legacy 3-field schema (dose/notes) for DIA-T2DM/PUL-ASTHMA/PED-ARI.
                elif item.get("type") == "rx_fixed":
                    composition = item.get("composition", "")
                    dosage = item.get("dosage", item.get("dose", ""))
                    frequency = item.get("frequency", "")
                    duration = item.get("duration", "")
                    instructions = item.get("instructions", item.get("notes", ""))
                    item["composition"] = composition
                    item["dosage"] = dosage
                    item["frequency"] = frequency
                    item["duration"] = duration
                    item["instructions"] = instructions
                    summary_bits = [b for b in [dosage, frequency, duration] if b]
                    item["rendered_line"] = " | ".join([item["drug"]] + summary_bits + ([instructions] if instructions else []))

                # 4. Rx Table: Slots for Doses (legacy schema only -- no ortho
                # template has a variable-dose prescription). Same rule as slot:
                # the row always renders, blank dose and all.
                elif item.get("type") == "rx_slot":
                    val = item.get("value")
                    filled_dose = item["dose"].replace("___", str(val)) if val else item["dose"]
                    item["composition"] = item.get("composition", "")
                    item["dosage"] = filled_dose
                    item["frequency"] = item.get("frequency", "")
                    item["duration"] = item.get("duration", "")
                    item["instructions"] = item.get("instructions", item.get("notes", ""))
                    item["rendered_line"] = f"{item['drug']} | {filled_dose} | {item['instructions']}"

                # 5. Gap Detection (Extensions)
                elif item.get("type") == "extended":
                    item["rendered_line"] = f"{item['name']}: {item['value']}"

                valid_items.append(item)
            cleaned_sections[sec_name] = valid_items

        return {
            "template_id": self.template_id,
            "document": cleaned_sections
        }