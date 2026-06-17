import json
import logging
from typing import Dict, List, Any, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.services.database_service import db_service
from app.services.llm_service import llm_service_instance
from app.services.verification.evidence_service import evidence_service
from app.services.verification.verification_service import verification_service
from app.services.verification.traceability_service import traceability_service
from app.services.verification.reasoning_service import reasoning_service
from app.services.verification.confidence_service import confidence_service
from app.services.chat.response_formatter_service import response_formatter_service
from app.services.chat.conversational_reasoning_service import conversational_reasoning_service

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        # Maps analysis_id -> list of turns: [{"role": "user"/"assistant", "content": "..."}]
        self.memory_store: Dict[str, List[Dict[str, str]]] = {}

    def get_memory(self, analysis_id: str) -> List[Dict[str, str]]:
        """
        Retrieves memory turns for the specified analysis session.
        """
        if analysis_id not in self.memory_store:
            self.memory_store[analysis_id] = []
        return self.memory_store[analysis_id]

    def clear_memory(self, analysis_id: str):
        """
        Clears the conversational memory for the specified session.
        """
        if analysis_id in self.memory_store:
            self.memory_store[analysis_id] = []
            logger.info(f"Cleared memory store for session '{analysis_id}'.")

    def generate_chat_response(self, analysis_id: str, question: str) -> Dict[str, Any]:
        """
        Loads report context, conversational history, and executes
        conversational safety reasoning using conversational_reasoning_service.
        """
        try:
            # 1. Fetch case from Supabase
            case_data = db_service.get_case_analysis(analysis_id)
            if not case_data:
                raise ValueError(f"Case analysis record '{analysis_id}' not found.")

            # 2. Retrieve conversation memory history
            history = self.get_memory(analysis_id)

            # 3. Execute LLM call via clinical safety reasoning service
            bot_reply = conversational_reasoning_service.reason_chat_turn(
                question=question,
                case_data=case_data,
                history=history,
                analysis_id=analysis_id
            )

            # 4. Save raw text turn to conversational history memory
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": bot_reply})

            # 5. Format response into Structured Enterprise Conversational Cards
            formatted_response = response_formatter_service.format_response(
                bot_reply=bot_reply,
                question=question,
                case_data=case_data,
                analysis_id=analysis_id
            )
            return formatted_response
        except Exception as e:
            logger.error(f"Error executing chat session for '{analysis_id}': {e}")
            raise e

chat_service = ChatService()
