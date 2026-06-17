import json
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from app.services.database_service import db_service
from app.services.verification.evidence_service import evidence_service
from app.services.verification.verification_service import verification_service
from app.services.verification.traceability_service import traceability_service
from app.services.verification.reasoning_service import reasoning_service
from app.services.verification.confidence_service import confidence_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Explainable AI & Verification"])

@router.get("/verify-drug/{drug_name}")
async def verify_drug(drug_name: str):
    """
    GET /verify-drug/{drug_name}
    Retrieves OpenFDA, local FAERS, and Knowledge Base evidence for a drug name,
    along with matching individual cases and verification status.
    """
    if not drug_name:
        raise HTTPException(status_code=400, detail="Drug name parameter is required.")

    # Gather evidence sources
    fda_ev = evidence_service.get_fda_evidence(drug_name)
    local_faers = evidence_service.get_local_faers_evidence(drug_name)
    kb_ev = evidence_service.get_knowledge_base_evidence(drug_name)

    # Determine first matching reaction to filter individual cases
    primary_reaction = None
    if local_faers:
        primary_reaction = local_faers[0].get("reaction")
    elif fda_ev.get("top_reactions"):
        primary_reaction = fda_ev["top_reactions"][0]

    supporting_cases = evidence_service.get_supporting_cases(drug_name, primary_reaction)
    
    # Calculate claims and verification status
    symptoms = [primary_reaction] if primary_reaction else ["toxicity"]
    claims = verification_service.verify_case_claims(drug_name, symptoms)
    status = verification_service.get_verification_status(claims)

    return {
        "drug_name": drug_name,
        "fda_evidence": fda_ev,
        "local_faers_evidence": local_faers,
        "knowledge_base_evidence": kb_ev,
        "supporting_cases": supporting_cases,
        "verification_status": status
    }

@router.get("/verify-analysis/{analysis_id}")
async def verify_analysis(analysis_id: str):
    if not analysis_id:
        raise HTTPException(status_code=400, detail="Analysis ID is required.")

    case_data = db_service.get_case_analysis(analysis_id)
    if not case_data:
        raise HTTPException(status_code=404, detail=f"Case analysis record '{analysis_id}' not found.")

    drugs = case_data.get("drugs", [])
    primary_drug = drugs[0] if drugs else "Unknown Drug"
    symptoms = case_data.get("symptoms", [])

    verified_claims = verification_service.verify_case_claims(primary_drug, symptoms)
    confidence = confidence_service.calculate_confidence(case_data, verified_claims)
    reasons = reasoning_service.get_reasoning_explanations(case_data)

    return {
        "analysis_id": analysis_id,
        "verified_claims": verified_claims,
        "causality_reasoning": reasons.get("causality", []),
        "seriousness_reasoning": reasons.get("seriousness", []),
        "confidence_score": confidence
    }

@router.get("/evidence/{analysis_id}")
async def get_evidence(analysis_id: str):
    """
    GET /evidence/{analysis_id}
    Returns full supporting evidence details (semantic vector chunks, FDA signal totals,
    FAERS local listings, and knowledge base references) for a case analysis.
    """
    if not analysis_id:
        raise HTTPException(status_code=400, detail="Analysis ID is required.")

    # Retrieve case record from Supabase
    case_data = db_service.get_case_analysis(analysis_id)
    if not case_data:
        raise HTTPException(status_code=404, detail=f"Case analysis record '{analysis_id}' not found.")

    # Extract suspect drug
    drugs = case_data.get("drugs", [])
    primary_drug = drugs[0] if drugs else "Unknown Drug"

    # 1. Retrieve traceable semantic chunks from Milvus collections
    retrieved_chunks = traceability_service.get_traceable_chunks(primary_drug, analysis_id=analysis_id, limit=5)

    # 2. Get FDA signal summary evidence
    fda_ev = evidence_service.get_fda_evidence(primary_drug)

    # 3. Get local FAERS reactions counts
    faers_ev = evidence_service.get_local_faers_evidence(primary_drug)

    # 4. Get Knowledge Base warning document chunks
    kb_ev = evidence_service.get_knowledge_base_evidence(primary_drug)

    return {
        "analysis_id": analysis_id,
        "retrieved_chunks": retrieved_chunks,
        "fda_evidence": fda_ev,
        "faers_evidence": faers_ev,
        "kb_references": kb_ev
    }
