import logging

logger = logging.getLogger(__name__)

class ResponseTypeClassifier:
    def classify_question(self, question: str) -> str:
        """
        Dynamically classifies the user's question into one of the 13 supported response types.
        """
        q_lower = question.lower().strip()
        
        # 1. Seriousness Explanation
        if any(w in q_lower for w in ["serious", "seriousness", "severity", "hospital", "life-threatening", "death", "outcome", "seriousness criteria"]):
            return "seriousness_explanation"
            
        # 2. Causality Explanation
        if any(w in q_lower for w in ["causal", "causality", "relationship", "why suspect", "link", "association", "cause", "related", "dechallenge", "rechallenge", "temporal"]):
            return "causality_explanation"
            
        # 3. FDA Signal Summary
        if any(w in q_lower for w in ["fda", "signal", "faers", "cases", "reported", "signal score", "reporting frequency", "stats", "statistics"]):
            return "fda_signal_summary"
            
        # 4. Timeline Explanation
        if any(w in q_lower for w in ["timeline", "chronology", "sequence", "order", "onset", "duration", "history", "date"]):
            return "timeline_explanation"
            
        # 5. Missing Information Review
        if any(w in q_lower for w in ["missing", "incomplete", "gaps", "what else", "need", "completeness", "unspecified", "not specified"]):
            return "missing_information_review"
            
        # 6. Regulatory Intelligence
        if any(w in q_lower for w in ["banned", "restricted", "cdsco", "warning", "un list", "ban", "regulation", "regulatory", "warnings"]):
            return "regulatory_intelligence"
            
        # 7. Organ System Analysis
        if any(w in q_lower for w in ["organ", "system", "affected", "hepatotoxicity", "nephrotoxicity", "cardiac", "dermatological", "hematological", "renal", "liver", "kidney", "lung", "pulmonary"]):
            return "organ_system_analysis"
            
        # 8. Confidence Explanation
        if any(w in q_lower for w in ["confidence", "confidence score", "why 0.", "why 1.", "score reasoning"]):
            return "confidence_explanation"
            
        # 9. Similar Case Retrieval
        if any(w in q_lower for w in ["similar cases", "have similar", "other cases", "similar patients", "faers database similar", "same reaction"]):
            return "similar_case_retrieval"
            
        # 10. Safety Recommendation
        if any(w in q_lower for w in ["monitor", "monitoring", "recommend", "recommendation", "guideline", "care", "ecg", "lab", "laboratory", "follow-up"]):
            return "safety_recommendation"
            
        # 11. Chart Interpretation
        if any(w in q_lower for w in ["chart", "trend", "visualization", "pie chart", "bar chart", "explain the chart", "explain the trend"]):
            return "chart_interpretation"
            
        # 12. Interaction Analysis
        if any(w in q_lower for w in ["interaction", "multiple drugs", "combined", "overlap", "overlapping", "drug-drug", "synergy", "co-administered"]):
            return "interaction_analysis"
            
        # 13. Open-ended Clinical Reasoning (default fallback)
        return "dynamic_contextual_reasoning"

response_type_classifier = ResponseTypeClassifier()
