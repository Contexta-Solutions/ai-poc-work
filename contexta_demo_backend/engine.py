import copy
from typing import Dict, Any, List

from clinical_data import TEMPLATE_SECTIONS

class ClinicalTemplate:
    def __init__(self, template_id: str):
        self.template_id = template_id if template_id else "Generic Consultation"
        self.sections: Dict[str, List[Dict[str, Any]]] = {
            "diagnosis": [{"line": self.template_id, "type": "fixed"}],
            "complaints": [],
            "advice": [],
            "prescription": [],
            "plan": [],
            "follow_up_plan": []
        }

        if template_id:
            self._load_base_template()

    def _load_base_template(self):
        for sec_name, items in TEMPLATE_SECTIONS.get(self.template_id, {}).items():
            if sec_name in ("complaints",):
                continue
            if sec_name in self.sections:
                self.sections[sec_name] = copy.deepcopy(items)

    def set_complaints(self, complaints: List[str]):
        """Populate complaints section entirely from LLM-extracted dictation data."""
        self.sections["complaints"] = [
            {"line": c, "type": "extracted", "rendered_line": c}
            for c in complaints if c.strip()
        ]

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
                    pass 
                
                # 1. Standard Template Sentences with Blanks
                elif item.get("type") == "slot":
                    val = item.get("value")
                    if not val:
                        continue 
                    item["rendered_line"] = item["line"].replace("___", str(val))
                
                # 2. Fixed Sentences
                elif item.get("type") == "fixed":
                    item["rendered_line"] = item["line"]
                
                # 3. Rx Table: Fixed Drugs
                elif item.get("type") == "rx_fixed":
                    item["rendered_line"] = f"{item['drug']} | {item['dose']} | {item['notes']}"
                
                # 4. Rx Table: Slots for Doses
                elif item.get("type") == "rx_slot":
                    val = item.get("value")
                    if not val:
                        continue
                    filled_dose = item["dose"].replace("___", str(val))
                    item["rendered_line"] = f"{item['drug']} | {filled_dose} | {item['notes']}"
                
                # 5. Gap Detection (Extensions)
                elif item.get("type") == "extended":
                    item["rendered_line"] = f"{item['name']}: {item['value']}"
                    
                valid_items.append(item)
            cleaned_sections[sec_name] = valid_items

        return {
            "template_id": self.template_id,
            "document": cleaned_sections
        }