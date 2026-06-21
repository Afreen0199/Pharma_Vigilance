import logging
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.services.llm_service import llm_service_instance
from app.services.chat.response_type_classifier import response_type_classifier
from app.services.chat.seriousness_chat_service import seriousness_chat_service
from app.services.chat.causality_chat_service import causality_chat_service
from app.services.chat.fda_signal_chat_service import fda_signal_chat_service
from app.services.chat.regulatory_chat_service import regulatory_chat_service
from app.services.chat.timeline_chat_service import timeline_chat_service
from app.services.chat.safety_recommendation_service import safety_recommendation_service

logger = logging.getLogger(__name__)

class QuestionAwareSummaryService:
    def generate_question_aware_explanation(
        self,
        user_question: str,
        retrieved_context: str,
        report_context: Dict[str, Any],
        evidence: Dict[str, Any],
        history: List[Dict[str, str]] = None
    ) -> str:
        """
        Generates a natural, question-aware clinical safety explanation summary using LLM reasoning.
        """
        if history is None:
            history = []

        # 1. Classify the user question to fetch response type guidelines
        response_type = response_type_classifier.classify_question(user_question)

        # Extract primary drug and symptoms for guidelines and metadata
        primary_drug = "Unknown Drug"
        drugs = report_context.get("drugs", [])
        if not drugs:
            # Fallback to parsing from ai_summary
            import json
            ai_summary = report_context.get("ai_summary", "")
            if ai_summary:
                try:
                    rep_data = json.loads(ai_summary)
                    drug_name = rep_data.get("drug_information", {}).get("product_active_ingredient") or \
                                rep_data.get("suspected_drug_information", {}).get("drug_name")
                    if drug_name:
                        primary_drug = drug_name
                except Exception:
                    pass
        else:
            primary_drug = drugs[0]
            
        symptoms = report_context.get("symptoms", [])

        # 2. Compile specific sub-service clinical reasoning guidelines
        extra_guidelines = ""
        if response_type == "seriousness_explanation":
            extra_guidelines = seriousness_chat_service.get_seriousness_guidelines(report_context)
        elif response_type == "causality_explanation":
            extra_guidelines = causality_chat_service.get_causality_guidelines(report_context)
        elif response_type == "fda_signal_summary":
            extra_guidelines = fda_signal_chat_service.get_signal_guidelines(report_context)
        elif response_type == "regulatory_intelligence":
            extra_guidelines = regulatory_chat_service.get_regulatory_guidelines(report_context)
        elif response_type == "timeline_explanation":
            extra_guidelines = timeline_chat_service.get_timeline_guidelines(report_context)
        elif response_type == "safety_recommendation":
            extra_guidelines = safety_recommendation_service.get_recommendation_guidelines(report_context)
        else:
            extra_guidelines = f"""### PHARMACOVIGILANCE CLINICAL REASONING RULES
- Analyze the user question: "{user_question}" relative to the suspect drug "{primary_drug}" and symptom profile "{symptoms}".
- Ground your response in the provided database totals, verified claims, and warning guidance texts.
"""

        # 3. Formulate the system prompt instructing Llama to be question-aware and clinical
        system_prompt = f"""You are the Enterprise AI Pharmacovigilance Safety Copilot, an expert clinical reviewer explaining safety findings to a panel.
Your role is to generate a natural, context-aware, and question-aware clinical safety explanation.

DO NOT output simple entity extractions, robotic NLP outputs, or raw report snippets. Instead, write a conversational narrative explanation that directly answers the user's question, explains context/significance, and provides clinical interpretation of the findings based on the safety report context and retrieved evidence.

---
### GOOD VS BAD CLINICAL EXPLANATIONS (FEW-SHOT EXAMPLES)

Example 1 (Timeline):
- USER QUESTION: "What is ADR timeline of this case?"
- BAD EXPLANATION: "The patient developed Grade 4 febrile neutropenia 7 days after R-CHOP Cycle 3 containing Cyclophosphamide."
- GOOD EXPLANATION: "The adverse reaction began 7 days after the patient received R-CHOP chemotherapy containing Cyclophosphamide. The patient developed severe febrile neutropenia requiring hospitalization and later recovered after supportive treatment with antibiotics and G-CSF."

Example 2 (Seriousness):
- USER QUESTION: "Why is this case serious?"
- BAD EXPLANATION: "Hospitalization occurred."
- GOOD EXPLANATION: "The case was classified as serious because the patient developed life-threatening febrile neutropenia that required hospitalization and intensive supportive treatment."

Example 3 (Missing Info):
- USER QUESTION: "What information is missing?"
- BAD EXPLANATION: "Weight missing."
- GOOD EXPLANATION: "Important clinical details such as patient weight, therapy end date, and follow-up laboratory values are missing, which reduces confidence in the causality assessment."
---

Here is the exact safety report context and retrieved safety evidence:
{retrieved_context}

{extra_guidelines}

Operational Rules for the response:
1. Directly answer the user's question: "{user_question}".
2. Explain clinical context, significance, and reasoning. Make it sound conversational, professional, and clinically intelligent.
3. Ground every statement strictly and ONLY in the provided safety report details, FDA evidence, local FAERS cases, or warning guidelines.
4. STRICT AI GOVERNANCE RULE: Do NOT formulate unsupported assumptions, invent clinical facts, or generate clinical interpretations that are not backed by evidence.
5. If the retrieved context/evidence is insufficient or does not contain the information needed to answer the question, state explicitly and clearly: "There is insufficient evidence in the provided safety report or retrieved FDA/FAERS databases to address this question." rather than speculating.
6. Do not write in generic ChatGPT-like casual chat style. Frame yourself as a pharmacovigilance reviewer.
7. Be concise and professional.
"""

        # 4. Compile messages with history context
        messages = [SystemMessage(content=system_prompt)]
        
        for turn in history:
            if turn["role"] == "user":
                messages.append(HumanMessage(content=turn["content"]))
            elif turn["role"] == "assistant":
                messages.append(AIMessage(content=turn["content"]))
                
        messages.append(HumanMessage(content=user_question))

        # 5. Execute LLM call
        try:
            from app.services.langfuse.metadata_builder import build_langfuse_metadata
            config = {"run_name": "question_aware_summary"}
            if hasattr(llm_service_instance, 'langfuse_handler') and llm_service_instance.langfuse_handler:
                config["callbacks"] = [llm_service_instance.langfuse_handler]
                
                analysis_id = report_context.get("analysis_id")
                analysis_mode = report_context.get("analysis_mode", "single_case")
                retrieved_chunk_count = len(evidence.get("retrieved_chunks", [])) if evidence and "retrieved_chunks" in evidence else 0
                
                config["metadata"] = build_langfuse_metadata(
                    analysis_id=analysis_id,
                    analysis_mode=analysis_mode,
                    run_name="question_aware_summary",
                    trace_group="summary",
                    run_type="summary_generation",
                    pipeline_stage="chat",
                    evaluation_target="summary",
                    processing_status="success",
                    model_name=getattr(llm_service_instance.llm, "model_name", "Unknown"),
                    llm_provider="Groq",
                    question_type="pharmacovigilance",
                    response_type=response_type,
                    retrieved_chunk_count=retrieved_chunk_count,
                    primary_suspect_drug=primary_drug
                )
                
            response = llm_service_instance.llm.invoke(messages, config=config)
            return response.content.strip()
        except Exception as e:
            logger.error(f"Error invoking Groq LLM in question-aware summary service: {e}")
            raise e

question_aware_summary_service = QuestionAwareSummaryService()
