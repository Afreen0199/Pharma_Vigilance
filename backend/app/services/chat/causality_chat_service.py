import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CausalityChatService:
    def get_causality_guidelines(self, case_data: Dict[str, Any]) -> str:
        """
        Formulates clinical guidelines explaining causality marking (temporal, dechallenge, rechallenge) based on case data.
        """
        causality_info = case_data.get("causality_assessment", {}) or {}
        relationship = causality_info.get("suspected_relationship") or "Possible"
        confidence = causality_info.get("confidence_score") or 0.5
        
        guidelines = [
            "### CLINICAL CAUSALITY ASSESSMENT RULES",
            f"- Suspected relationship strength: {relationship}.",
            f"- Base verification confidence: {confidence}.",
            "Guidelines to incorporate into the clinical response:",
            "  * Detail the temporal association: did symptoms appear after starting therapy?",
            "  * Detail dechallenge: did symptoms improve or stabilize upon drug withdrawal/reduction?",
            "  * Detail rechallenge: was the drug reintroduced, and did symptoms reappear? Indicate if rechallenge was not performed or is contraindicated."
        ]
        
        # Check dechallenge/rechallenge info from adverse events
        events = case_data.get("adverse_events", {}) or {}
        drug_recur = events.get("drug_recur_action", "")
        if drug_recur:
            guidelines.append(f"  * Rechallenge details: {drug_recur}")
            
        return "\n".join(guidelines)

causality_chat_service = CausalityChatService()
