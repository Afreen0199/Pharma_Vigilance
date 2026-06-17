import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TimelineChatService:
    def get_timeline_guidelines(self, case_data: Dict[str, Any]) -> str:
        """
        Formulates clinical guidelines explaining chronological timelines of events.
        """
        timeline = case_data.get("timeline", [])
        
        guidelines = [
            "### CLINICAL TIMELINE INTERPRETATION RULES",
            "Guidelines to incorporate into the clinical response:",
            "  * Translate the timeline dates/timestamps into a human-readable clinical sequence.",
            "  * Identify and explain: therapy initiation, onset of adverse drug reactions, hospitalization sequence, and drug dechallenge/discontinuation events."
        ]
        
        if timeline:
            guidelines.append("  * Reference this timeline event sequence:")
            for item in timeline:
                guidelines.append(f"    - {item.get('timestamp') or 'Date'}: {item.get('event') or 'Adverse event sequence'}")
        else:
            guidelines.append("  * Note that no chronological timeline is explicitly mapped in the structured database; extract time milestones directly from the raw case narrative text.")
            
        return "\n".join(guidelines)

timeline_chat_service = TimelineChatService()
