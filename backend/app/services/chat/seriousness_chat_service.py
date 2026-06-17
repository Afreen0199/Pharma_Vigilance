import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SeriousnessChatService:
    def get_seriousness_guidelines(self, case_data: Dict[str, Any]) -> str:
        """
        Formulates clinical guidelines explaining seriousness classification reasoning based on case details.
        """
        seriousness_ass = case_data.get("seriousness_assessment", {}) or {}
        case_info = case_data.get("case_information", {}) or {}
        seriousness_val = case_info.get("seriousness") or seriousness_ass.get("is_serious") or "Serious"
        
        guidelines = [
            "### CLINICAL SERIOUSNESS ASSESSMENT RULES",
            f"- The case is classified overall as: {seriousness_val}.",
            "Guidelines to incorporate into the clinical response:"
        ]
        
        hosp = seriousness_ass.get("hospitalization") or seriousness_ass.get("hospitalized")
        if hosp and str(hosp).lower() in ["yes", "true", "1", "serious"]:
            guidelines.append("  * Hospitalization occurred, satisfying critical regulatory criteria.")
            
        lt = seriousness_ass.get("life_threatening") or seriousness_ass.get("is_life_threatening")
        if lt and str(lt).lower() in ["yes", "true", "1", "serious"]:
            guidelines.append("  * Life-threatening condition was reported, which warrants ICU or immediate clinical attention.")
            
        death = seriousness_ass.get("death") or seriousness_ass.get("died")
        if death and str(death).lower() in ["yes", "true", "1", "serious"]:
            guidelines.append("  * Fatal outcome was documented. Standard emergency reports and regulatory alerts must be highlighted.")
            
        disabling = seriousness_ass.get("disabling") or seriousness_ass.get("disability")
        if disabling and str(disabling).lower() in ["yes", "true", "1", "serious"]:
            guidelines.append("  * Disabling or incapacitating condition occurred.")
            
        congenital = seriousness_ass.get("congenital_anomaly")
        if congenital and str(congenital).lower() in ["yes", "true", "1", "serious"]:
            guidelines.append("  * Congenital anomaly or birth defect criteria met.")
            
        if len(guidelines) == 3:
            guidelines.append("  * Clinically significant event without standard death/hospitalization flags; evaluated under medical review criteria.")
            
        return "\n".join(guidelines)

seriousness_chat_service = SeriousnessChatService()
