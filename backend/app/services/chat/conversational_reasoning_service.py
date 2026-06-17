import json
import logging
from typing import List, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.services.llm_service import llm_service_instance
from app.services.chat.response_type_classifier import response_type_classifier
from app.services.chat.semantic_retrieval_service import semantic_retrieval_service
from app.services.chat.dynamic_context_builder import dynamic_context_builder
from app.services.chat.seriousness_chat_service import seriousness_chat_service
from app.services.chat.causality_chat_service import causality_chat_service
from app.services.chat.fda_signal_chat_service import fda_signal_chat_service
from app.services.chat.regulatory_chat_service import regulatory_chat_service
from app.services.chat.timeline_chat_service import timeline_chat_service
from app.services.chat.safety_recommendation_service import safety_recommendation_service
from app.services.chat.response_scope_controller import response_scope_controller

from app.services.chat.question_aware_summary_service import question_aware_summary_service

from app.services.chat.question_domain_classifier import question_domain_classifier

logger = logging.getLogger(__name__)

class ConversationalReasoningService:
    def reason_chat_turn(self, question: str, case_data: Dict[str, Any], history: List[Dict[str, str]], analysis_id: str) -> str:
        """
        Orchestrates classification, domain validation, dynamic retrieval,
        and delegates LLM reasoning to the QuestionAwareSummaryService.
        """
        # 1. Classify the question domain
        domain = question_domain_classifier.classify_domain(question)
        
        if domain == "irrelevant_question":
            return "The question appears to be unrelated to the analyzed pharmacovigilance report or available medical evidence sources. Please ask questions related to the uploaded case, FDA evidence, safety signals, adverse events, or regulatory intelligence."
            
        if domain in ["greeting", "capability_question"]:
            system_prompt = (
                "You are the Enterprise AI Pharmacovigilance Safety Copilot. "
                "Answer the user's greeting or capability onboarding question naturally, professionally, and conversationally. "
                "Explain that you are an AI Pharmacovigilance Safety Copilot designed to analyze adverse drug reaction reports, "
                "retrieve FDA and FAERS evidence, explain safety signals, and provide evidence-grounded insights. "
                "Highlight key features like seriousness criteria assessment, causality analysis, regulatory intelligence warning scans, "
                "and visual safety trend interpretability. Keep the tone warm, highly professional, concise, and medically focused."
            )
            messages = [SystemMessage(content=system_prompt)]
            for turn in history:
                if turn["role"] == "user":
                    messages.append(HumanMessage(content=turn["content"]))
                elif turn["role"] == "assistant":
                    messages.append(AIMessage(content=turn["content"]))
            messages.append(HumanMessage(content=question))
            try:
                response = llm_service_instance.llm.invoke(messages)
                return response.content.strip()
            except Exception as e:
                logger.error(f"Error invoking LLM for general conversation: {e}")
                raise e

        # Proceed to domain specific RAG pipeline for pharmacovigilance questions
        response_type = response_type_classifier.classify_question(question)
        
        # 2. Extract drug names and symptoms
        drugs = case_data.get("drugs", [])
        ai_summary = case_data.get("ai_summary", "")
        report_data = {}
        if ai_summary:
            try:
                report_data = json.loads(ai_summary)
            except Exception:
                pass
        if not drugs and report_data:
            drug_name = report_data.get("drug_information", {}).get("product_active_ingredient") or \
                        report_data.get("suspected_drug_information", {}).get("drug_name")
            if drug_name:
                drugs = [drug_name]
        primary_drug = drugs[0] if drugs else "Unknown Drug"
        symptoms = case_data.get("symptoms", [])

        # 3. Retrieve dynamic evidence
        retrieved_data = semantic_retrieval_service.retrieve_evidence_context(primary_drug, symptoms, analysis_id)
        
        # 4. Filter prompt context dynamically via the scope controller
        scoped_case_data, scoped_retrieved_data = response_scope_controller.filter_context(
            response_type=response_type,
            case_data=case_data,
            retrieved_data=retrieved_data
        )
        
        # 4.5. Build context block using the scoped data
        context_block = dynamic_context_builder.build_context_block(scoped_case_data, scoped_retrieved_data, analysis_id)
        
        # 5. Delegate explanation summary generation to QuestionAwareSummaryService
        try:
            bot_reply = question_aware_summary_service.generate_question_aware_explanation(
                user_question=question,
                retrieved_context=context_block,
                report_context=scoped_case_data,
                evidence=scoped_retrieved_data,
                history=history
            )
            return bot_reply
        except Exception as e:
            logger.error(f"Error delegating to question aware summary service: {e}")
            raise e

conversational_reasoning_service = ConversationalReasoningService()
