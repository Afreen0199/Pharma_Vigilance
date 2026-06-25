from langchain_groq import ChatGroq
import os
import logging
from typing import Dict, Any
from langfuse.langchain import CallbackHandler

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # The user must provide GROQ_API_KEY in environment
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment. LLM generation will fail.")
        else:
            try:
                self.langfuse_handler = CallbackHandler()
            except Exception as e:
                logger.error(f"Failed to initialize Langfuse CallbackHandler: {e}")
                self.langfuse_handler = None
                
            try:
                # Use Llama 3.3 70B Versatile as primary, fall back to Llama 3.1 8B Instant if not available
                self.llm = ChatGroq(
                    model="llama-3.3-70b-versatile",
                    temperature=0.0,
                    api_key=self.api_key
                )
                logger.info("Initialized Groq LLM service with llama-3.3-70b-versatile.")
            except Exception as e:
                logger.warning(f"Failed to initialize llama-3.3-70b-versatile: {e}. Attempting fallback...")
                try:
                    self.llm = ChatGroq(
                        model="llama-3.1-8b-instant",
                        temperature=0.0,
                        api_key=self.api_key
                    )
                    logger.info("Initialized Groq LLM service with fallback model llama-3.1-8b-instant.")
                except Exception as ex:
                    logger.error(f"Failed to initialize fallback Groq model: {ex}")

    def generate_analysis(self, text: str, extracted_entities: Dict, fda_context: Dict, rag_context: str) -> Dict[str, Any]:
        if not hasattr(self, 'llm'):
            return {"error": "LLM not initialized"}
        
        # Run local regex and keyword parser to extract PV fields
        from app.services.extraction.local_parser import parse_local_pv_fields
        local_pv_data = parse_local_pv_fields(text)
        
        # Scan for ocr highlight sections inside the text to build the highlighted critical fields list
        ocr_highlights = []
        for line in text.split("\n"):
            if line.startswith("[YELLOW HIGHLIGHT]") or line.startswith("[PURPLE HIGHLIGHT]"):
                ocr_highlights.append(line)
        
        prompt = f"""
You are an expert AI Pharmacovigilance Specialist. Your task is to analyze the following medical narrative, along with provided FDA FAERS data, similar case guidelines, and locally extracted metadata, and generate a highly detailed, professional Adverse Event Case Report.

Medical Narrative (including any priority OCR highlights):
{text}

Locally Extracted PV Fields (Regex & Keyword Parser):
{local_pv_data}

OCR Highlighted Regions:
{ocr_highlights}

FDA Context (FAERS):
{fda_context}

Similar Cases (RAG Context):
{rag_context}

Generate a structured JSON output representing the case report. Ensure all fields are filled with precise details extracted from the narrative or synthesized from the provided context. 

If any required pharmacovigilance field is not found in the narrative, write "Not Specified" or "Unknown" inside its value, and you MUST explicitly append the name of the missing field to the "missing_information" list in the format "FIELD_NAME missing" (e.g. "WT missing", "LOT_NUM missing", "EVENT_DT missing", "OCCP_COD missing", "ROLE_COD missing").

The JSON must follow this exact format, combining the legacy fields for backward compatibility and the new structured PV categories:
{{
  "case_information": {{
    "case_id": "PV-2026-XXXXX (generate a unique random 5-digit number for XXXXX)",
    "report_type": "Spontaneous Report (or other appropriate type)",
    "report_date": "Current Date",
    "seriousness": "Serious / Non-Serious",
    "case_status": "Initial"
  }},
  "patient_demographic": {{
    "age": "Age of patient (e.g., 45 Years)",
    "gender": "Gender (e.g., Female)",
    "weight": "Weight of patient if mentioned (e.g., 72 kg)",
    "medical_history": "Relevant history (e.g., Hypertension)",
    "age_group": {{
      "code": "N/I/C/T/A/E (N: Neonate, I: Infant, C: Child, T: Adolescent, A: Adult, E: Elderly)",
      "meaning": "Neonate / Infant / Child / Adolescent / Adult / Elderly"
    }},
    "patient_weight": "Patient weight numerical value only (e.g. 72)"
  }},
  "drug_information": {{
    "product_active_ingredient": "Product active ingredient (e.g. Paracetamol)",
    "drug_role": {{
      "code": "PS/SS/C/I/DN (PS: Primary Suspect, SS: Secondary Suspect, C: Concomitant, I: Interacting, DN: Drug Not Administered)",
      "meaning": "Primary Suspect Drug / Secondary Suspect Drug / Concomitant / Interacting / Drug Not Administered"
    }}
  }},
  "suspected_drug_information": {{
    "drug_name": "Name of the drug",
    "dosage": "Dosage (e.g., 500 mg)",
    "route": "Route of administration (e.g., Oral)",
    "therapy_start_date": "Start date if mentioned",
    "therapy_end_date": "End date if mentioned",
    "indication": "Reason for taking the drug"
  }},
  "adverse_events": {{
    "event_date": "Date the adverse event occurred (format: YYYYMMDD, e.g. 20240115)",
    "drug_recur_action": "Drug recur action description (rechallenge/readministration response, e.g., 'Rash reappeared after re-administration')"
  }},
  "adverse_event_details": {{
    "adverse_event": "Adverse event described",
    "event_start_date": "Onset date/timing",
    "outcome": "Outcome (e.g., Hospitalization, Recovered)",
    "severity": "Severity (e.g., Severe, Moderate)",
    "action_taken": "Action taken (e.g., Drug Discontinued)"
  }},
  "drug_batch_details": {{
    "lot_number": "Lot number of the drug (e.g., LOT-AX9921)",
    "batch_number": "Batch number of the drug",
    "expiry_date": "Expiry date of the batch if mentioned",
    "manufacturer": "Manufacturer name if mentioned"
  }},
  "therapy_information": {{
    "dose_form": "Form of dose (e.g., Tablet, Capsule, Injection, Syrup, Suspension)",
    "dose_amount": "Dose numerical value (e.g. 500)",
    "dose_unit": "Dose unit (e.g. mg, ml)",
    "dose_frequency": "Frequency of dose (e.g. once daily)",
    "route": "Route of administration (e.g. Oral)",
    "therapy_duration": "Duration of therapy if mentioned"
  }},
  "reporter_information": {{
    "occupation": {{
      "code": "MD/PH/OT/LW/CN (MD: Physician, PH: Pharmacist, OT: Other health-professional, LW: Lawyer, CN: Consumer)",
      "meaning": "Physician / Pharmacist / Other health-professional / Lawyer / Consumer"
    }}
  }},
  "ai_generated_narrative_summary": "A detailed, professional narrative summary of the case.",
  "ai_generated_summary": "A detailed, professional narrative summary of the case.",
  "seriousness_assessment": {{
    "hospitalization": "Yes / No",
    "life_threatening": "Yes / No",
    "disability": "Yes / No",
    "death": "Yes / No"
  }},
  "causality_assessment": {{
    "suspected_relationship": "Highly probable / Probable / Possible / Doubtful",
    "confidence_score": 0.00 (a float between 0.0 and 1.0 representing confidence)
  }},
  "key_entities_extracted": {{
    "drug": "Main suspected drug",
    "reaction": "Primary adverse reaction",
    "symptom": "Other symptoms mentioned",
    "outcome": "Primary outcome"
  }},"ai_safety_insights": [
  "Generate up to 4 concise pharmacovigilance safety insights based ONLY on evidence found in the user-provided document, FDA/openFDA evidence, and retrieved validated knowledge-base content. Prioritize documented drug-event associations, known safety signals, reported outcomes, seriousness criteria, hospitalization details, signal trends, or regulatory safety information that directly relate to the reported case. Do NOT infer patient-specific risk factors, causes, susceptibility, or clinical explanations unless explicitly supported by the provided evidence. Every insight must be traceable to the case document, FDA evidence, or knowledge-base evidence. If no supported insight exists, return []."
  ],

"medical_insights": [
  "Generate up to 4 evidence-grounded medical review insights using ONLY information present in the user-provided case document, extracted clinical data, FDA evidence, and validated knowledge-base content. Focus on documented adverse events, temporal relationships, dechallenge/rechallenge findings, laboratory results, clinical outcomes, causality assessments, and confirmed drug-event associations. Do NOT infer age-related risk, gender-related risk, medical-history-related risk, disease susceptibility, or unsupported medical conclusions. Every statement must be directly supported by the provided sources. If insufficient evidence exists, return []."
  ],

"safety_observations": [
  "Generate up to 4 safety observations ONLY when directly supported by the user-provided document, FDA evidence, or validated knowledge-base guidance. Summarize documented actions taken, observed outcomes, reported monitoring activities, safety measures already described in the case, or evidence-supported safety findings relevant to the reported adverse event. Do NOT generate treatment recommendations, prescribing advice, monitoring plans, physician instructions, or generic clinical guidance unless explicitly present in the supporting evidence. If no supported observation exists, return []."
  ],

"regulatory_alerts": [
  "Return only verified regulatory findings that are directly supported by FDA data, CDSCO guidance, WHO alerts, UN restrictions, validated regulatory knowledge-base documents, or other retrieved regulatory evidence relevant to the reported drug or adverse event. Include the regulatory authority and a concise evidence-based summary. Do NOT generate regulatory conclusions from model knowledge alone. If no verified regulatory alert exists, return []."
  ],

"highlighted_critical_fields": [
  "Return only fields explicitly identified through verified visual highlight detection, PDF annotations, OCR color metadata, OpenCV highlight extraction, or other validated document-markup evidence present in the user-provided document. Do NOT infer, assume, or generate highlighted fields from text content alone. If no verified highlight metadata exists, return []."
  ]
,
  "timeline": [
    {{
      "event": "Description of the event",
      "timestamp": "Time or relative days"
    }}
  ],
  "missing_information": [
    "List of critical details that are missing from the case to make a complete clinical assessment."
  ],
  "final_case_classification": "Serious/Non-Serious Adverse Drug Reaction (ADR) — Requires Medical Review"
}}

Output ONLY valid JSON without Markdown code block backticks (do not wrap in ```json ... ```). Ensure the JSON is syntactically correct and complete.
"""
        try:
            from app.services.langfuse.metadata_builder import build_langfuse_metadata
            config = {"run_name": "generate_analysis"}
            if hasattr(self, 'langfuse_handler') and self.langfuse_handler:
                config["callbacks"] = [self.langfuse_handler]
                
                suspect_drug = None
                if extracted_entities and isinstance(extracted_entities, dict):
                    suspect_drug = extracted_entities.get("suspected_drug", {}).get("drug_name")
                    
                fda_total_cases = None
                if fda_context and isinstance(fda_context, dict):
                    fda_total_cases = fda_context.get("total_cases")
                
                config["metadata"] = build_langfuse_metadata(
                    run_name="generate_analysis",
                    trace_group="analysis",
                    run_type="analysis_generation",
                    pipeline_stage="generation",
                    evaluation_target="analysis_report",
                    processing_status="success",
                    model_name=getattr(self.llm, "model_name", "Unknown"),
                    llm_provider="Groq",
                    primary_suspect_drug=suspect_drug,
                    matched_fda_cases=fda_total_cases
                )
                
            response = self.llm.invoke(prompt, config=config)
            return {"raw_ai_response": response.content}
        except Exception as e:
            logger.error(f"Error generating AI analysis: {e}")
            return {"error": str(e)}

    def identify_suspected_drug(self, text: str) -> Dict[str, Any]:
        """
        Step 1 of the FDA pipeline: Extract suspected drug information from the medical narrative.
        """
        import json
        
        # Check if there is an explicit structured "suspect drug" label
        suspect_keywords = ["suspect drug", "suspected drug", "primary suspect", "primary suspected drug"]
        detected_drug = None
        
        lines = text.split("\n")
        for idx, line in enumerate(lines):
            line_lower = line.lower().strip()
            for kw in suspect_keywords:
                if kw in line_lower:
                    after_kw = ""
                    if ":" in line:
                        after_kw = line.split(":", 1)[1].strip()
                    elif kw != line_lower:
                        after_kw = line_lower.split(kw, 1)[1].strip()
                    
                    candidates = [after_kw] if after_kw else []
                    if idx + 1 < len(lines):
                        candidates.append(lines[idx+1].strip())
                    if idx + 2 < len(lines):
                        candidates.append(lines[idx+2].strip())
                        
                    for candidate in candidates:
                        candidate_lower = candidate.lower()
                        for target in ["rifampicin", "vancomycin", "lithium", "haloperidol", "amiodarone", "lisinopril", "ciprofloxacin", "ciprottoxacin"]:
                            if target in candidate_lower:
                                detected_drug = "Ciprofloxacin" if target == "ciprottoxacin" else target.capitalize()
                                break
                        if detected_drug:
                            break
                if detected_drug:
                    break
            if detected_drug:
                break
                
        if detected_drug:
            logger.info(f"Structured parser override: identified suspect drug '{detected_drug}' from text labels.")
            return {
                "suspected_drug_information": {
                    "drug_name": detected_drug,
                    "dosage": "Not Specified",
                    "route": "Not Specified",
                    "therapy_start_date": "Not Specified",
                    "therapy_end_date": "Not Specified",
                    "indication": "Not Specified"
                }
            }

        if not hasattr(self, 'llm'):
            return {"suspected_drug_information": {"drug_name": "Unknown"}}
            
        prompt = f"""
You are an expert AI Pharmacovigilance Specialist. Your task is to extract the primary suspected drug information from the following medical narrative.

IMPORTANT: If the medical narrative explicitly labels a drug as "Suspect Drug", "Primary Suspect", "Suspected Drug", or similar, you MUST prioritize and select that drug as the primary suspected drug.

Medical Narrative:
{text}

Generate a structured JSON output representing only the suspected drug.
Format:
{{
  "suspected_drug_information": {{
    "drug_name": "Name of the drug (e.g., Methotrexate)",
    "dosage": "Dosage (e.g., 20 mg/week)",
    "route": "Route (e.g., Oral)",
    "therapy_start_date": "Start date if mentioned",
    "therapy_end_date": "End date if mentioned",
    "indication": "Indication if mentioned"
  }}
}}

Output ONLY valid JSON without Markdown code block backticks.
"""
        try:
            from app.services.langfuse.metadata_builder import build_langfuse_metadata
            config = {"run_name": "identify_suspected_drug"}
            if hasattr(self, 'langfuse_handler') and self.langfuse_handler:
                config["callbacks"] = [self.langfuse_handler]
                config["metadata"] = build_langfuse_metadata(
                    run_name="identify_suspected_drug",
                    trace_group="analysis",
                    run_type="drug_identification",
                    pipeline_stage="generation",
                    evaluation_target="classification",
                    processing_status="success",
                    model_name=getattr(self.llm, "model_name", "Unknown"),
                    llm_provider="Groq"
                )
                
            response = self.llm.invoke(prompt, config=config)
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error identifying suspected drug: {e}")
            return {"suspected_drug_information": {"drug_name": "Unknown"}}

llm_service_instance = LLMService()
