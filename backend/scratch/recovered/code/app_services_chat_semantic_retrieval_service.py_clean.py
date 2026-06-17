import logging
from typing import Dict, Any, List
from app.services.verification.evidence_service import evidence_service
from app.services.verification.verification_service import verification_service
from app.services.verification.traceability_service import traceability_service
from app.services.fda_service import fda_service_instance

logger = logging.getLogger(__name__)

class SemanticRetrievalService:
    def retrieve_evidence_context(self, primary_drug: str, symptoms: List[str], analysis_id: str) -> Dict[str, Any]:
        """
        Dynamically retrieves clinical signals and reference database evidence for a suspect drug.
        """
        logger.info(f"Dynamically retrieving semantic safety evidence for '{primary_drug}' (symptoms: {symptoms})...")
        
        # 1. Fetch live FDA openFDA summary stats
        fda_ev = evidence_service.get_fda_evidence(primary_drug)
        
        # 2. Fetch local FAERS CSV counts
        local_faers = evidence_service.get_local_faers_evidence(primary_drug)
        
        # 3. Fetch warning guideline chunks from Milvus collection 'knowledge_base'
        kb_ev = evidence_service.get_knowledge_base_evidence(primary_drug)
        
        # 4. Run explainability verification claims
        claims = verification_service.verify_case_claims(primary_drug, symptoms)
        
        # 5. Fetch semantic traceable chunks for the specific file analysis
        chunks = traceability_service.get_traceable_chunks(primary_drug, analysis_id=analysis_id, limit=3)
        
        # 6. Fetch similar case IDs and outcomes from local FAERS
        similar_cases = evidence_service.get_supporting_cases(primary_drug)

        return {
            "fda_evidence": fda_ev,
            "local_faers": local_faers,
            "kb_evidence": kb_ev,
            "verified_claims": claims,
            "traceable_chunks": chunks,
            "similar_cases": similar_cases
        }

semantic_retrieval_service = SemanticRetrievalService()
