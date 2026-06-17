import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ConfidenceService:
    def calculate_confidence(self, case_data: Dict[str, Any], verified_claims: List[Dict[str, Any]]) -> float:
        """
        Calculates an evidence-backed confidence score between 0.1 and 1.0.
        Factors:
        - Base confidence: 0.5
        - Verification sources: +0.1 per unique verification source across claims (max +0.3)
        - Data completeness: +0.15 if no missing data fields, -0.04 per missing field (min adjustment 0)
        - High-similarity retrieval: +0.1 if any retrieved chunk score exceeds 0.75
        """
        confidence = 0.5
        
        # 1. Verification sources check
        unique_sources = set()
        for claim in verified_claims:
            for source in claim.get("verified_from", []):
                unique_sources.add(source)
                
        confidence += min(0.3, len(unique_sources) * 0.1)

        # 2. Completeness check
        missing_fields = case_data.get("missing_data") or case_data.get("missing_information") or []
        if not missing_fields:
            confidence += 0.15
        else:
            deduction = len(missing_fields) * 0.04
            # Keep a positive contribution or neutral if many fields are missing
            completeness_contrib = max(0.0, 0.15 - deduction)
            confidence += completeness_contrib

        # 3. High-similarity retrieval check
        # Look for custom retrieved score or similar
        high_sim = False
        timeline = case_data.get("timeline", [])
        # We also query Milvus chunks or check existing scores if any
        if any(item.get("retrieval_score", 0) > 0.75 for item in case_data.get("retrieved_chunks", [])):
            high_sim = True
            
        if high_sim:
            confidence += 0.10

        # Round and bound
        final_score = round(max(0.1, min(1.0, confidence)), 2)
        return final_score

confidence_service = ConfidenceService()
