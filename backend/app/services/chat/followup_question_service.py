import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class FollowupQuestionService:
    def generate_suggested_questions(self, case_data: Dict[str, Any], question: str) -> List[str]:
        """
        Dynamically recommends follow-up questions based on the active case details and conversation context.
        """
        questions = []
        
        # 1. Parse symptoms and context
        symptoms = [s.lower() for s in case_data.get("symptoms", [])]
        narrative = case_data.get("extracted_text", "").lower()
        
        # 2. Check if renal or hepatic or cardiac organ systems are impacted
        is_renal = any(w in narrative or any(w in sym for sym in symptoms) for w in ["renal", "kidney", "nephro", "creatinine", "dialysis", "egfr"])
        is_hepatic = any(w in narrative or any(w in sym for sym in symptoms) for w in ["liver", "hepatic", "lft", "jaundice", "bilirubin", "hepatitis"])
        is_cardiac = any(w in narrative or any(w in sym for sym in symptoms) for w in ["cardiac", "heart", "ecg", "qtc", "arrhythmia", "infarction"])

        # 3. Dynamic generation based on case details
        # Always suggest explanation of causality if not recently asked
        if "causal" not in question.lower():
            questions.append("Explain causality reasoning")

        if is_renal:
            questions.append("Explain renal safety risk")
        if is_hepatic:
            questions.append("Explain liver function safety risk")
        if is_cardiac:
            questions.append("Explain cardiac safety monitoring recommendations")

        # Missing information check
        missing = case_data.get("missing_information") or case_data.get("missing_data") or []
        if missing and len(questions) < 4:
            questions.append("What information is missing?")
            
        # FDA signal checks
        fda_sig = case_data.get("fda_signal", {}) or {}
        if fda_sig.get("total_cases", 0) > 0 and len(questions) < 4:
            questions.append("Show FDA signal trends")
            
        # Regulatory check
        if len(questions) < 4:
            questions.append("Is this drug banned anywhere?")
            
        # Timeline check
        if case_data.get("timeline") and len(questions) < 4:
            questions.append("Show ADR timeline")

        # Similar cases check
        if len(questions) < 5:
            questions.append("Have similar cases been reported?")
            
        # safety recommendations
        if len(questions) < 5:
            questions.append("What monitoring is recommended?")

        # Deduplicate and limit to 5
        seen = set()
        final_questions = []
        for q in questions:
            if q not in seen:
                seen.add(q)
                final_questions.append(q)
                
        return final_questions[:5]

followup_question_service = FollowupQuestionService()
