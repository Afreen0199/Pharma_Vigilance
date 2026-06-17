import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chat_service import chat_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Case-Aware Chat Copilot"])

class ChatRequest(BaseModel):
    question: str

@router.post("/{analysis_id}")
async def chat_with_case(analysis_id: str, request: ChatRequest):
    """
    POST /chat/{analysis_id}
    Executes a case-aware chat session conversation step for a specific analysis_id.
    Accepts follow-up questions from the user and returns an evidence-grounded response.
    """
    if not analysis_id:
        raise HTTPException(status_code=400, detail="Analysis ID parameter is required.")
    if not request.question:
        raise HTTPException(status_code=400, detail="Question is required in body.")

    try:
        reply = chat_service.generate_chat_response(analysis_id, request.question)
        return reply
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error handling chat request for '{analysis_id}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {e}")

@router.delete("/{analysis_id}")
async def reset_chat(analysis_id: str):
    """
    DELETE /chat/{analysis_id}
    Resets the conversational memory store for the specific case analysis_id session.
    """
    if not analysis_id:
        raise HTTPException(status_code=400, detail="Analysis ID parameter is required.")

    chat_service.clear_memory(analysis_id)
    return {
        "message": f"Conversational chat history for session '{analysis_id}' has been successfully reset.",
        "analysis_id": analysis_id
    }
