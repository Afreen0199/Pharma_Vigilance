import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RegulatoryChatService:
    def get_regulatory_guidelines(self, case_data: Dict[str, Any]) -> str:
        """
        Formulates clinical guidelines detailing CDSCO, UN Banned, or FDA warning restrictions.
        """
        reg_alerts = case_data.get("regulatory_alerts", [])
        
        guidelines = [
            "### REGULATORY INTELLIGENCE RULES",
            "Guidelines to incorporate into the clinical response:",
            "  * State whether this drug has warnings or bans in major databases (CDSCO, FDA warnings, UN restricted list).",
            "  * If restrictions exist, state the reasons (e.g. hepatotoxicity, cardiovascular risk) and countries/regions where restricted."
        ]
        
        if reg_alerts:
            guidelines.append("  * Note the following specific alerts matched for this case:")
            for alert in reg_alerts:
                drug = alert.get("drug_name", "Suspect")
                reason = alert.get("ban_reason", "Safety reasons")
                country = alert.get("ban_country", "Global")
                guidelines.append(f"    - Drug: {drug} | Reason: {reason} | Location: {country}")
        else:
            guidelines.append("  * Note that no CDSCO or UN ban restrictions were explicitly triggered for the suspect drug in current local lists; continue monitoring.")
            
        return "\n".join(guidelines)

regulatory_chat_service = RegulatoryChatService()
