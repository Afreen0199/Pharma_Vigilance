import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DynamicContextBuilder:
    def build_context_block(self, case_data: Dict[str, Any], retrieved_data: Dict[str, Any], analysis_id: str) -> str:
        """
        Synthesizes the safety report context and dynamic evidence into a formatted markdown text block.
        """
        # Parse safety report if available
        report_data = {}
        ai_summary = case_data.get("ai_summary", "")
        if ai_summary:
            try:
                report_data = json.loads(ai_summary)
            except Exception:
                pass

        # Primary suspect drug & symptoms
        drugs = case_data.get("drugs", [])
        if not drugs and report_data:
            drug_name = report_data.get("drug_information", {}).get("product_active_ingredient") or \
                        report_data.get("suspected_drug_information", {}).get("drug_name")
            if drug_name:
                drugs = [drug_name]
        primary_drug = drugs[0] if drugs else "Unknown Drug"

        symptoms = case_data.get("symptoms", [])
        adverse_events_text = ", ".join(symptoms) if symptoms else "Unknown Adverse Effect"

        # Seriousness assessment
        seriousness = case_data.get("seriousness") or \
                      report_data.get("case_information", {}).get("seriousness") or \
                      "Serious"

        # Missing information review
        missing_fields = case_data.get("missing_information") or \
                         case_data.get("missing_data") or \
                         report_data.get("missing_information") or []

        # Chronological timeline
        timeline = case_data.get("timeline") or report_data.get("timeline") or []
        timeline_bullets = []
        for item in timeline:
            ts = item.get("timestamp") or item.get("date") or "Unknown Date"
            ev = item.get("event") or item.get("description") or "Unknown Event"
            timeline_bullets.append(f"- [{ts}]: {ev}")
        timeline_str = "\n".join(timeline_bullets) if timeline_bullets else "No chronology available."

        # Compile RAG and verification findings
        verified_claims = retrieved_data.get("verified_claims", [])
        claims_str = json.dumps(verified_claims, indent=2) if verified_claims else "No claims verified."

        # Compile Milvus KB Warning guidances
        kb_chunks = retrieved_data.get("kb_evidence", [])
        kb_bullets = []
        for i, chunk in enumerate(kb_chunks):
            doc = chunk.get("document_source", "Regulatory Guide")
            txt = chunk.get("retrieved_chunk", "")
            if len(txt) > 300:
                txt = txt[:300] + "..."
            kb_bullets.append(f"[{i+1}] Source: {doc} | Text: {txt}")
        kb_str = "\n".join(kb_bullets) if kb_bullets else "No warning guidelines found."

        # Compile FDA / FAERS stats
        fda_ev = retrieved_data.get("fda_evidence", {})
        local_faers = retrieved_data.get("local_faers", [])
        similar_cases = retrieved_data.get("similar_cases", [])

        context_lines = [
            f"### CLINICAL CASE IDENTIFIER: {analysis_id}",
            f"- Primary Suspect Drug: {primary_drug.upper()}",
            f"- Extracted Symptoms / Reactions: {adverse_events_text}",
            f"- Seriousness Assessment: {seriousness}",
            "",
            "### EXTRACTED PATIENT CASE NARRATIVE",
            f"{case_data.get('extracted_text', 'No raw narrative text available.')}",
            "",
            "### CLINICAL TIMELINE (CHRONOLOGY)",
            timeline_str,
            "",
            "### MISSING DATA GAPS & COMPLETE INFORMATION",
            f"- Missing Fields: {', '.join(missing_fields) if missing_fields else 'None (Complete Case Report)'}",
            "",
            "### FDA OPENFDA EVENT DATABASE SIGNALS",
            f"- Total FAERS cases matching drug: {fda_ev.get('total_cases', 0)}",
            f"- Serious case subsets: {fda_ev.get('serious_cases', 0)}",
            f"- Hospitalization subsets: {fda_ev.get('hospitalizations', 0)}",
            f"- FDA Signal Score: {case_data.get('fda_signal', {}).get('fda_signal_score') or report_data.get('fda_signal', {}).get('fda_signal_score') or 'Low'}",
            "",
            "### LOCAL FAERS DATASET COUNTS",
            json.dumps(local_faers[:5], indent=2),
            "",
            "### SEMANTIC KNOWLEDGE BASE REGULATORY GUIDANCES",
            kb_str,
            "",
            "### EXPLAINABLE AI VERIFIED CLINICAL CLAIMS",
            claims_str,
            "",
            "### SIMILAR FAERS PATIENT CASES",
            json.dumps(similar_cases[:3], indent=2)
        ]

        return "\n".join(context_lines)

dynamic_context_builder = DynamicContextBuilder()
