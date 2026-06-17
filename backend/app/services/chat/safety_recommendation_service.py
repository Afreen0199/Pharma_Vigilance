import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SafetyRecommendationService:
    def get_recommendation_guidelines(self, case_data: Dict[str, Any]) -> str:
        """
        Formulates clinical safety guidelines and monitoring recommendations.
        """
        symptoms = [s.lower() for s in case_data.get("symptoms", [])]
        narrative = case_data.get("extracted_text", "").lower()
        
        is_renal = any(w in narrative or any(w in sym for sym in symptoms) for w in ["renal", "kidney", "creatinine", "nephro"])
        is_hepatic = any(w in narrative or any(w in sym for sym in symptoms) for w in ["liver", "hepatic", "lft", "bilirubin"])
        is_cardiac = any(w in narrative or any(w in sym for sym in symptoms) for w in ["cardiac", "heart", "ecg", "qtc", "arrhythmia"])
        
        guidelines = [
            "### CLINICAL MONITORING RECOMMENDATION RULES",
            "Guidelines to incorporate into the clinical response:",
            "  * Recommendations must remain: evidence-based, cautious, non-diagnostic, and retrieval-backed.",
            "  * Always add a disclaimer: advice does not replace formal medical practitioner review."
        ]
        
        if is_renal:
            guidelines.append("  * Renal Impairment suspected: recommend renal function monitoring (e.g. serum creatinine, eGFR, fluid balance).")
        if is_hepatic:
            guidelines.append("  * Hepatic Impairment suspected: recommend liver function monitoring (e.g. AST, ALT, bilirubin, LFT trends).")
        if is_cardiac:
            guidelines.append("  * Cardiac involvement suspected: recommend cardiac monitoring (e.g. ECG monitoring, QT interval tracking, electrolytes).")
            
        if len(guidelines) == 4:
            guidelines.append("  * Suggest baseline organ function tracking, medication reconciliation, and adverse reaction symptom logging.")
            
        return "\n".join(guidelines)

safety_recommendation_service = SafetyRecommendationService()
