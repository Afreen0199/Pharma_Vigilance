from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.fda_service import fda_service_instance

router = APIRouter(prefix="/fda", tags=["FDA Intelligence"])

class DrugSearchRequest(BaseModel):
    drug_name: str

class ReactionSearchRequest(BaseModel):
    reaction: str

@router.post("/drug-search")
async def search_drug(request: DrugSearchRequest):
    """Search for adverse events by drug name."""
    if not request.drug_name:
        raise HTTPException(status_code=400, detail="Drug name is required.")
    
    result = fda_service_instance.search_by_drug(request.drug_name)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to query FDA Intelligence Layer.")
    return result

@router.post("/reaction-search")
async def search_reaction(request: ReactionSearchRequest):
    """Search for adverse events by reaction."""
    if not request.reaction:
        raise HTTPException(status_code=400, detail="Reaction is required.")
    
    result = fda_service_instance.search_by_reaction(request.reaction)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to query FDA Intelligence Layer.")
    return result

@router.post("/signal-summary")
async def signal_summary(request: DrugSearchRequest):
    """Generate FDA signal intelligence summary for a drug."""
    if not request.drug_name:
        raise HTTPException(status_code=400, detail="Drug name is required.")
    
    summary = fda_service_instance.get_fda_signal_summary(request.drug_name)
    if not summary:
        raise HTTPException(status_code=500, detail="Failed to generate FDA signal summary.")
    return summary
