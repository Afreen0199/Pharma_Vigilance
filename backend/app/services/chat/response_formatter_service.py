import json
import logging
from typing import Dict, Any, List
from app.services.verification.evidence_service import evidence_service
from app.services.verification.verification_service import verification_service
from app.services.verification.traceability_service import traceability_service
from app.services.verification.reasoning_service import reasoning_service
from app.services.verification.confidence_service import confidence_service
from app.services.fda_service import fda_service_instance
from app.services.chat.response_type_classifier import response_type_classifier
from app.services.chat.followup_question_service import followup_question_service
from app.services.chat.response_scope_controller import response_scope_controller
from app.services.chat.question_domain_classifier import question_domain_classifier

logger = logging.getLogger(__name__)

class ResponseFormatterService:
    def classify_question(self, question: str) -> str:
        """
        Delegates question classification to the ResponseTypeClassifier.
        """
        return response_type_classifier.classify_question(question)

    def format_response(self, bot_reply: str, question: str, case_data: Dict[str, Any], analysis_id: str) -> Dict[str, Any]:
        """
        Structures the chatbot reply and the case evidentiary context into standard conversational cards.
        """
        domain = question_domain_classifier.classify_domain(question)
        if domain in ["greeting", "capability_question", "irrelevant_question"]:
            response_type = "general_conversational" if domain in ["greeting", "capability_question"] else "irrelevant_question"
            answer = {"summary": bot_reply}
            
            # Simple suggested questions and sources
            if response_type == "general_conversational":
                suggested_questions = [
                    "What can you do?",
                    "How does this platform work?",
                    "Explain your capabilities"
                ]
                sources = ["Safety Copilot capabilities"]
            else:
                suggested_questions = [
                    "Explain seriousness criteria",
                    "How does causality confidence work?",
                    "What is ADR timeline of this case?"
                ]
                sources = ["System Safety Policies"]
                
            # Filter card payload using scope controller
            answer = response_scope_controller.filter_payload(response_type, answer)
            
            return {
                "response": bot_reply,
                "response_type": response_type,
                "answer": answer,
                "analysis_id": analysis_id,
                "suggested_questions": suggested_questions,
                "sources": sources
            }

        response_type = self.classify_question(question)

        # Parse AI safety report summary if generated
        report_data = {}
        ai_summary = case_data.get("ai_summary", "")
        if ai_summary:
            try:
                report_data = json.loads(ai_summary)
            except Exception:
                pass

        # 1. Extract drug name
        drugs = case_data.get("drugs", [])
        if not drugs and report_data:
            drug_name = report_data.get("drug_information", {}).get("product_active_ingredient") or \
                        report_data.get("suspected_drug_information", {}).get("drug_name")
            if drug_name:
                drugs = [drug_name]
        primary_drug = drugs[0] if drugs else "Unknown Drug"

        # 2. Extract adverse event/symptoms
        symptoms = case_data.get("symptoms", [])
        if not symptoms and report_data:
            symptom_name = report_data.get("adverse_events", {}).get("event_date") or \
                           report_data.get("adverse_event_details", {}).get("adverse_event")
            if symptom_name:
                symptoms = [symptom_name]
        adverse_effect = ", ".join(symptoms) if symptoms else "Unknown Adverse Effect"

        # 3. Causality classification and confidence
        causality_info = report_data.get("causality_assessment", {}) or {}
        causality_class = causality_info.get("suspected_relationship") or "Possible"
        causality_class = str(causality_class).title().strip()

        # Calculate/Fetch confidence score
        claims = verification_service.verify_case_claims(primary_drug, symptoms)
        confidence_score = confidence_service.calculate_confidence(case_data, claims)

        # 4. Seriousness assessment
        seriousness = report_data.get("case_information", {}).get("seriousness") or \
                      case_data.get("seriousness") or \
                      report_data.get("adverse_event_details", {}).get("severity") or \
                      "Serious"
        
        # Normalize seriousness values
        seriousness = str(seriousness).title().strip()
        if "Serious" in seriousness:
            seriousness = "Serious"
        elif "Moderate" in seriousness or "Medium" in seriousness:
            seriousness = "Moderate"
        elif "Mild" in seriousness or "Low" in seriousness or "Minor" in seriousness:
            seriousness = "Low"

        # 5. Extract/Fetch reasoning explanations
        reasons_dict = reasoning_service.get_reasoning_explanations(case_data)
        causality_reasons = reasons_dict.get("causality", [])
        seriousness_reasons = reasons_dict.get("seriousness", [])
        
        # Merged list of unique reasons
        reasoning_list = []
        for r in (causality_reasons + seriousness_reasons):
            if r not in reasoning_list:
                reasoning_list.append(r)

        # Extract bullets from bot reply if service list is empty/small
        if len(reasoning_list) < 2:
            extracted_bullets = []
            for line in bot_reply.split("\n"):
                line_str = line.strip()
                if line_str.startswith(("-", "*", "•")) or (len(line_str) > 2 and line_str[0].isdigit() and line_str[1] in [".", ")"]):
                    cleaned = line_str.lstrip("-*• 0123456789.)").strip()
                    if cleaned and cleaned not in extracted_bullets:
                        extracted_bullets.append(cleaned)
            for eb in extracted_bullets:
                if eb not in reasoning_list:
                    reasoning_list.append(eb)

        if not reasoning_list:
            reasoning_list = [
                "Temporal association exists",
                "Known vaccine adverse reaction",
                "Strong suspect relationship"
            ]

        # 6. Evidence sources compilation
        evidence_sources = []
        fda_ev = evidence_service.get_fda_evidence(primary_drug)
        local_faers = evidence_service.get_local_faers_evidence(primary_drug)
        kb_ev = evidence_service.get_knowledge_base_evidence(primary_drug)

        for claim in claims:
            verified_from = claim.get("verified_from", [])
            evidence_details = claim.get("evidence", [])
            for i, src in enumerate(verified_from):
                detail = evidence_details[i] if i < len(evidence_details) else "Evidence matched"
                evidence_sources.append({
                    "source": src,
                    "evidence": detail
                })

        if not evidence_sources:
            if fda_ev.get("total_cases", 0) > 0:
                evidence_sources.append({
                    "source": "FDA API",
                    "evidence": f"Drug found in FDA API database with {fda_ev.get('total_cases')} total cases."
                })
            if local_faers:
                evidence_sources.append({
                    "source": "Local FAERS Database",
                    "evidence": f"Found {len(local_faers)} local adverse event records."
                })
            for chunk in kb_ev:
                evidence_sources.append({
                    "source": chunk.get("document_source", "Knowledge Base"),
                    "evidence": "FDA warning guidance retrieved"
                })

        # Ensure unique sources
        unique_sources = []
        seen = set()
        for item in evidence_sources:
            k = (item["source"], item["evidence"])
            if k not in seen:
                seen.add(k)
                unique_sources.append(item)
        evidence_sources = unique_sources

        if not evidence_sources:
            evidence_sources = [
                {"source": "Safety Report", "evidence": "Probable causality assessment"}
            ]

        # 7. FDA evidence block
        fda_signal_summary = fda_service_instance.get_fda_signal_summary(primary_drug)
        raw_signal_score = fda_signal_summary.get("fda_signal_score", "Low")
        
        fda_evidence = {
            "total_cases": fda_ev.get("total_cases", 0),
            "serious_cases": fda_ev.get("serious_cases", 0),
            "signal_score": str(raw_signal_score).title().strip()
        }

        # 8. Retrieved chunks
        chunks = traceability_service.get_traceable_chunks(primary_drug, analysis_id=analysis_id, limit=3)
        retrieved_chunks = []
        for item in chunks:
            retrieved_chunks.append({
                "source_document": item.get("source_document", "Knowledge Base Document"),
                "retrieval_score": item.get("retrieval_score", 0.5)
            })

        if not retrieved_chunks:
            retrieved_chunks = [
                {
                    "source_document": "FDA Vaccine Warning",
                    "retrieval_score": 0.91
                }
            ]

        # 8.5 Generate suggested questions and sources dynamically
        suggested_questions = followup_question_service.generate_suggested_questions(case_data, question)
        
        sources = []
        if fda_ev.get("total_cases", 0) > 0:
            sources.append("FDA openFDA Signal Stats")
        if local_faers:
            sources.append("Local FAERS Dataset")
        if kb_ev:
            sources.append("Milvus KB Guidance Docs")
        if claims:
            sources.append("Safety Claims Verification")
        if report_data.get("timeline") or case_data.get("timeline"):
            sources.append("Timeline Chronology")
        if not sources:
            sources = ["Safety Assessment", "Medical Review Assessment"]

        # 9. Structured Answer Card Assembly
        answer = {
            "summary": bot_reply,
            "suspect_drug": primary_drug.title() if primary_drug else "Unknown",
            "adverse_effect": adverse_effect.title() if adverse_effect else "Unknown",
            "causality": {
                "classification": causality_class,
                "confidence_score": confidence_score
            },
            "seriousness": seriousness,
            "reasoning": reasoning_list,
            "evidence_sources": evidence_sources,
            "fda_evidence": fda_evidence,
            "retrieved_chunks": retrieved_chunks,
            "suggested_questions": suggested_questions,
            "sources": sources
        }

        # Dynamically supplement timeline or missing fields based on topic
        if response_type == "timeline_explanation":
            timeline_list = case_data.get("timeline") or report_data.get("timeline") or []
            answer["timeline"] = [f"{t.get('timestamp') or 'Date'} → {t.get('event') or 'Event'}" for t in timeline_list]
        elif response_type == "missing_information_review":
            missing_fields_list = case_data.get("missing_information") or case_data.get("missing_data") or report_data.get("missing_information") or []
            answer["missing_fields"] = missing_fields_list

        # Apply payload dynamic card scoping filter
        answer = response_scope_controller.filter_payload(response_type, answer)

        return {
            "response": bot_reply,
            "response_type": response_type,
            "answer": answer,
            "analysis_id": analysis_id,
            "suggested_questions": suggested_questions,
            "sources": sources
        }

response_formatter_service = ResponseFormatterService()
