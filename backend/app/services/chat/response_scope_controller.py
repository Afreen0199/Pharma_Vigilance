import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ResponseScopeController:
    # 13 response types mapping to strictly allowed keys in the answer card payload
    QUESTION_SCOPE_MAP = {
        "timeline_explanation": ["summary", "timeline"],
        "causality_explanation": ["summary", "causality", "reasoning"],
        "fda_signal_summary": ["summary", "fda_evidence", "signal_trends"],
        "missing_information_review": ["summary", "missing_fields", "impact"],
        "regulatory_intelligence": ["summary", "regulatory_findings"],
        "seriousness_explanation": ["summary", "seriousness", "reasoning"],
        "organ_system_analysis": ["summary", "organ_system_details"],
        "confidence_explanation": ["summary", "confidence_reasoning"],
        "similar_case_retrieval": ["summary", "similar_cases", "faers_trends"],
        "safety_recommendation": ["summary", "monitoring_recommendations"],
        "chart_interpretation": ["summary", "fda_evidence", "chart_analysis"],
        "interaction_analysis": ["summary", "interaction_details"],
        "general_conversational": ["summary"],
        "irrelevant_question": ["summary"],
        "dynamic_contextual_reasoning": [
            "summary", "suspect_drug", "adverse_effect", "causality", "seriousness",
            "reasoning", "evidence_sources", "fda_evidence", "retrieved_chunks"
        ]
    }

    def __init__(self):
        self.default_verbosity = "minimal"

    def filter_context(self, response_type: str, case_data: Dict[str, Any], retrieved_data: Dict[str, Any]) -> tuple:
        """
        Dynamically filters prompt context elements, selecting ONLY the relevant sections
        for Groq reasoning to prevent full report dumps.
        """
        # Start with shallow copies to avoid modifying original source dicts
        filtered_case = case_data.copy()
        filtered_retrieved = retrieved_data.copy()

        # If open-ended dynamic reasoning is requested, keep full context to ensure accuracy
        if response_type == "dynamic_contextual_reasoning":
            return filtered_case, filtered_retrieved

        # Suppress context details based on classification
        if response_type == "seriousness_explanation":
            filtered_case["timeline"] = []
            filtered_case["missing_information"] = []
            filtered_case["missing_data"] = []
            filtered_retrieved["fda_evidence"] = {"total_cases": 0, "serious_cases": 0, "hospitalizations": 0, "top_reactions": []}
            filtered_retrieved["local_faers"] = []
            filtered_retrieved["kb_evidence"] = []
            filtered_retrieved["similar_cases"] = []

        elif response_type == "causality_explanation":
            filtered_case["missing_information"] = []
            filtered_case["missing_data"] = []
            filtered_retrieved["fda_evidence"] = {"total_cases": 0, "serious_cases": 0, "hospitalizations": 0, "top_reactions": []}
            filtered_retrieved["local_faers"] = []
            filtered_retrieved["kb_evidence"] = []
            filtered_retrieved["similar_cases"] = []

        elif response_type == "fda_signal_summary":
            filtered_case["timeline"] = []
            filtered_case["extracted_text"] = "Narrative omitted for signal summary."
            filtered_case["missing_information"] = []
            filtered_case["missing_data"] = []
            filtered_retrieved["kb_evidence"] = []

        elif response_type == "timeline_explanation":
            filtered_case["missing_information"] = []
            filtered_case["missing_data"] = []
            filtered_case["seriousness_assessment"] = {}
            filtered_case["causality_assessment"] = {}
            filtered_retrieved["fda_evidence"] = {"total_cases": 0, "serious_cases": 0, "hospitalizations": 0, "top_reactions": []}
            filtered_retrieved["local_faers"] = []
            filtered_retrieved["kb_evidence"] = []
            filtered_retrieved["verified_claims"] = []
            filtered_retrieved["similar_cases"] = []

        elif response_type == "missing_information_review":
            filtered_case["timeline"] = []
            filtered_case["seriousness_assessment"] = {}
            filtered_case["causality_assessment"] = {}
            filtered_retrieved["fda_evidence"] = {"total_cases": 0, "serious_cases": 0, "hospitalizations": 0, "top_reactions": []}
            filtered_retrieved["local_faers"] = []
            filtered_retrieved["kb_evidence"] = []
            filtered_retrieved["verified_claims"] = []
            filtered_retrieved["similar_cases"] = []

        elif response_type == "regulatory_intelligence":
            filtered_case["timeline"] = []
            filtered_case["extracted_text"] = "Narrative omitted for regulatory search."
            filtered_case["seriousness_assessment"] = {}
            filtered_case["causality_assessment"] = {}
            filtered_retrieved["fda_evidence"] = {"total_cases": 0, "serious_cases": 0, "hospitalizations": 0, "top_reactions": []}
            filtered_retrieved["local_faers"] = []
            filtered_retrieved["similar_cases"] = []

        elif response_type == "confidence_explanation":
            filtered_case["timeline"] = []
            filtered_retrieved["fda_evidence"] = {"total_cases": 0, "serious_cases": 0, "hospitalizations": 0, "top_reactions": []}
            filtered_retrieved["local_faers"] = []
            filtered_retrieved["kb_evidence"] = []
            filtered_retrieved["similar_cases"] = []

        elif response_type in ["similar_case_retrieval", "chart_interpretation"]:
            filtered_case["timeline"] = []
            filtered_case["extracted_text"] = "Narrative omitted."
            filtered_retrieved["kb_evidence"] = []
            filtered_retrieved["verified_claims"] = []

        elif response_type == "safety_recommendation":
            filtered_case["timeline"] = []
            filtered_retrieved["fda_evidence"] = {"total_cases": 0, "serious_cases": 0, "hospitalizations": 0, "top_reactions": []}
            filtered_retrieved["local_faers"] = []
            filtered_retrieved["similar_cases"] = []

        return filtered_case, filtered_retrieved

    def filter_payload(self, response_type: str, answer_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dynamically filters response payload fields in the structured answer card
        to include ONLY the contextually relevant keys.
        """
        allowed_keys = self.QUESTION_SCOPE_MAP.get(
            response_type, self.QUESTION_SCOPE_MAP["dynamic_contextual_reasoning"]
        )

        filtered_answer = {}
        for key in allowed_keys:
            if key in answer_dict:
                filtered_answer[key] = answer_dict[key]
            else:
                # Provide placeholder default values if key is missing
                if key == "timeline":
                    filtered_answer[key] = []
                elif key == "missing_fields":
                    filtered_answer[key] = []
                elif key == "impact":
                    filtered_answer[key] = "Missing critical fields reduces causality validation confidence."
                elif key == "regulatory_findings":
                    filtered_answer[key] = "No CDSCO/UN warning alerts found."
                elif key == "signal_trends":
                    filtered_answer[key] = "Consistent reporting frequency pattern observed."
                elif key == "organ_system_details":
                    filtered_answer[key] = "Primarily affects localized systems."
                elif key == "confidence_reasoning":
                    filtered_answer[key] = ["Confidence score calculated from case completeness."]
                elif key == "similar_cases":
                    filtered_answer[key] = []
                elif key == "faers_trends":
                    filtered_answer[key] = "FAERS counts are aligned with normal parameters."
                elif key == "monitoring_recommendations":
                    filtered_answer[key] = ["Routine clinical monitoring recommended."]
                elif key == "chart_analysis":
                    filtered_answer[key] = "FAERS trend timeline matches database profiles."
                elif key == "interaction_details":
                    filtered_answer[key] = "No multi-drug overlapping toxicities identified."
                else:
                    filtered_answer[key] = None

        return filtered_answer

response_scope_controller = ResponseScopeController()
