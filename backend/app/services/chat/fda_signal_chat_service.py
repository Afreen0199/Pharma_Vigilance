import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FdaSignalChatService:
    def get_signal_guidelines(self, case_data: Dict[str, Any]) -> str:
        """
        Formulates clinical guidelines explaining FDA signal trends, seriousness ratios, and reaction distributions.
        """
        fda_sig = case_data.get("fda_signal", {}) or {}
        signal_score = fda_sig.get("fda_signal_score") or "Low"
        total_cases = fda_sig.get("total_cases") or 0
        serious_cases = fda_sig.get("serious_cases") or 0
        hospitalizations = fda_sig.get("hospitalizations") or 0
        
        guidelines = [
            "### FDA SIGNAL INTERPRETATION RULES",
            f"- FDA Signal Score: {signal_score}.",
            f"- FAERS Global Total Cases: {total_cases}.",
            f"- Serious case subset count: {serious_cases}.",
            f"- Hospitalization subset count: {hospitalizations}.",
            "Guidelines to incorporate into the clinical response:",
            "  * Interpret the reporting volume: describe the statistical risk.",
            "  * List top reactions reported in openFDA for this suspect drug.",
            "  * Detail global seriousness ratio (% of serious cases out of total)."
        ]
        
        if total_cases > 0:
            ratio = round((serious_cases / total_cases) * 100, 1)
            guidelines.append(f"  * Note that {ratio}% of reported FAERS cases for this drug are classified as serious.")
            
        return "\n".join(guidelines)

fda_signal_chat_service = FdaSignalChatService()
