
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.services.report_service import report_service_instance
from app.services.database_service import db_service
from app.services.fda_service import fda_service_instance
from app.services.regulatory_service import regulatory_service_instance
from app.services.rag_service import rag_service_instance
from app.services.llm_service import llm_service_instance
from typing import Optional
import os
import json
import logging

from app.services.verification.evidence_service import evidence_service
from app.services.verification.reasoning_service import reasoning_service

logger = logging.getLogger(__name__)

def normalize_report_data(report_data: dict, ocr_metadata: Optional[dict] = None) -> dict:
    # If it is a parent multi-case report, skip single-case schema normalization
    if "cases" in report_data and isinstance(report_data["cases"], list):
        return report_data

    # Ensure all required sections exist in the JSON
    for section in [
        "patient_demographic", "patient_information", "patient_details",
        "drug_information", "adverse_events",
        "drug_batch_details", "therapy_information", "reporter_information"
    ]:
        if section not in report_data or not isinstance(report_data[section], dict):
            report_data[section] = {}

    p_demo = report_data["patient_demographic"]
    p_info = rep
    p_details = report_data["patient_details"]

    # Fill patient_demographic fields from legacy nodes if missing or empty
    for k in ["age", "gender", "weight", "medical_history"]:
        if k not in p_demo or not p_demo[k]:
            p_demo[k] = p_info.get(k) or ""

    if "age_group" not in p_demo or not isinstance(p_demo["age_group"], dict):
        p_demo["age_group"] = p_details.get("age_group") or {"code": "", "meaning": ""}
    for k in ["code", "meaning"]:
        if k not in p_demo["age_group"]:
            p_demo["age_group"][k] = ""

    if "patient_weight" not in p_demo or not p_demo["patient_weight"]:
        p_demo["patient_weight"] = p_details.get("patient_weight") or p_info.g
            report_service_instance.generate_json_report(report_data, analysis_id)
            report_service_instance.generate_excel_report(report_data, analysis_id)
            report_service_instance.generate_pdf_report(report_data, analysis_id)
            
            return response_data
        except Exception:
            # Fallback to older format structure
            fda_signals_data = case_data.get("fda_signals", {})
            visualizations_data = {}
            if isinstance(fda_signals_data, dict):

            ocr_metadata = None
            if case_data.get("ai_summary"):
                try:
                    ocr_metadata = json.loads(case_data.get("ai_summary")).get("ocr_metadata")
                except Exception:
                    pass

            report_data = {
                "summary": ai_summary_text,
                "seriousness_assessment": case_data.get("seriousness_assessment", {}),
                "causality_assessment": case_data.get("causality_assessment", {}),
                "timeline": case_data.get("timeline", []),
                "missing_data": case_data.get("missing_data", [])
            }
            try:
                report_service_instance.generate_json_report(report_data, 
                "report_id": analysis_id,
        if k not in report_data["therapy_information"]:
            report_data["therapy_information"][k] = ""
            
    if "occupation" not in report_data["reporter_information"] or not isinstance(report_data["reporter_information"]["occupation"], dict):
        report_data["reporter_information"]["occupation"] = {"code": "", "meaning": ""}
    else:
        for k in ["code", "meaning"]:
            if k not in report_data["reporter_information"]["occupation"]:
                report_data["reporter_information"]["occupation"][k] = ""

    # Ensure list fields exist
    for lst in ["regulatory_alerts", "highlighted_critical_fields", "missing_information", "medical_insights", "safety_observations"]:
        if lst not in report_data or not isinstance(report_data[lst], list):
            report_data[lst] = []

    # Ensure dict fields exist
    for dct in ["causality_assessment", "seriousness_assessment"]:
        if dct not in report_data or not isinstance(report_data[dct], dict):
            report_data[dct] = {}

    if "ai_generated_summary" not in report_data:
        report_data["ai_generated_summary"] = report_data.get("ai_generated_narrative_summary") or report_data.get("summary") or ""

    # Merge OCR highlighted critical fields if any
    if ocr_metadata and isinstance(ocr_metadata, dict):
        ocr_highlights = ocr_metadata.get("highlighted_critical_fields", [])
        for h in ocr_highlights:
            if h not in report_data["highlighted_critical_fields"]:
                report_data["highlighted_critical_fields"].append(h)

    # Rebuild missing_information
    missing_fields = []
    
    def is_missing(val):
        if val is None:
            return True
        if isinstance(val, str):
            v = val.strip().lower()
            return v in ["", "unknown", "not specified", "n/a", "missing", "none", "null"]
        if isinstance(val, dict):
            code = val.get("code")
            return is_missing(code)
        return False

    if is_missing(report_data.get("adverse_events", {}).get("event_date")):
        missing_fields.append("EVENT_DT missing")
        
    if is_missing(report_data.get("patient_details", {}).get("age_group", {}).get("code")):
        missing_fields.append("AGE_GRP missing")
        
    if is_missing(report_data.get("patient_details", {}).get("patient_weight")):
        missing_fields.append("WT missing")
        
    if is_missing(report_data.get("reporter_information", {}).get("occupation", {}).get("code")):
        missing_fields.append("OCCP_COD missing")
        
    if is_missing(report_data.get("drug_information", {}).get("drug_role", {}).get("code")):
        missing_fields.append("ROLE_COD missing")
        
    if is_missing(report_data.get("drug_information", {}).get("product_active_ingredient")):
        missing_fields.append("PROD_AI missing")
        
    if is_missing(report_data.get("drug_batch_details", {}).get("lot_number")):
        missing_fields.append("LOT_NUM missing")
        
    if is_missing(report_data.get("therapy_information", {}).get("dose_form")):
        missing_fields.append("DOSE_FORM missing")
        
    if is_missing(report_data.get("adverse_events", {}).get("drug_recur_action")):
        missing_fields.append("DRUG_REC_ACT missing")

    # Filter out LLM-generated redundant/verbose descriptions of our 9 critical fields
    cleaned_existing = []
    for item in report_data.get("missing_information", []):
        if not isinstance(item, str):
            continue
        item_lower = item.lower()
        if any(f.lower() in item_lower or f.replace("_", "").lower() in item_lower.replace("_", "") for f in ["WT", "OCCP_COD", "ROLE_COD", "EVENT_DT", "LOT_NUM", "DOSE_FORM", "PROD_AI", "AGE_GRP", "DRUG_REC_ACT", "LOT"]):
            continue
        cleaned_existing.append(item)

    report_data["missing_information"] = missing_fields + cleaned_existing
    report_data["missing_data"] = report_data["missing_information"]

    return report_data

router = APIRouter(prefix="/report", tags=["Report Generation"])

class ReportGenerateRequest(BaseModel):
    analysis_id: str
    force: Optional[bool] = False

@router.post("/generate")
async def generate_report(request: ReportGenerateRequest):
    analysis_id = request.analysis_id
    if not analysis_id:
        raise HTTPException(status_code=400, detail="analysis_id is required.")
    
    # 1. Fetch case from Supabase
    case_data = db_service.get_case_analysis(analysis_id)
    if not case_data:
        raise HTTPException(status_code=404, detail=f"Case analysis record '{analysis_id}' not found.")
    
    # 2. Check if the report has already been completed
    if case_data.get("status") == "completed" and not request.force:
        logger.info(f"Report '{analysis_id}' is already completed. Returning cached details.")

        
        ai_summary_text = case_data.get("ai_summary", "")
        try:
            report_data = json.loads(ai_summary_text)
            
            # Normalize report data on the fly to ensure consistent schema and missing fields formatting
            report_data = normalize_report_data(report_data, report_data.get("ocr_metadata"))
            
            response_data = report_data.copy()
            response_data["report_id"] = analysis_id
            response_data["json_url"] = f"/report/download/{analysis_id}?format=json"
            response_data["excel_url"] = f"/report/download/{analysis_id}?format=xlsx"
            response_data["pdf_url"] = f"/report/download/{analysis_id}?format=pdf"
            response_data["status"] = "success"
            response_data["cached"] = True
            
            # Regenerate on-disk files if missing
            report_service_instance.generate_json_report(report_data, analysis_id)
            report_service_instance.generate_excel_report(report_data, analysis_id)
            report_service_instance.generate_pdf_report(report_data, analysis_id)
            
            return response_data
        except Exception:
            # Fallback to older format structure
            fda_signals_data = case_data.get("fda_signals", {})
            visualizations_data = {}
            if isinstance(fda_signals_data, dict):
                visualizations_data = fda_signals_data.pop("visualizations", {})

            ocr_metadata = None
            if case_data.get("ai_summary"):
                try:
                    ocr_metadata = json.loads(case_data.get("ai_summary")).get("ocr_metadata")
                except Exception:
                    pass

            report_data = {
                "summary": ai_summary_text,
                "drug_entities": case_data.get("drugs", []),
                "symptoms": case_data.get("symptoms", []),
                "conditions": case_data.get("conditions", []),
                "regulatory_alerts": case_data.get("regulatory_alerts", []),
                "fda_signal": fda_signals_data,
                "visualizations": visualizations_data,
                "seriousness_assessment": case_data.get("seriousness_assessment", {}),
                "causality_assessment": case_data.get("causality_assessment", {}),
                "timeline": case_data.get("timeline", []),
                "missing_data": case_data.get("missing_data", [])
            }
        
        ai_summary_text = case_data.get("ai_summary", "")
        try:
            report_data = json.loads(ai_summary_text)
            
                report_service_instance.generate_excel_report(report_data, analysis_id)
                report_service_instance.generate_pdf_report(report_data, analysis_id)
            except Exception as e:
                logger.warning(f"Error compiling downloadable files for cached report: {e}")
                
            res_dict = {
                "report_id": analysis_id,
                "json_url": f"/report/download/{analysis_id}?format=json",
                "excel_url": f"/report/download/{analysis_id}?format=xlsx",
                "pdf_url": f"/report/download/{analysis_id}?format=pdf",
                "status": "success",
                "cached": True,
                "drug_entities": case_data.get("drugs", []),
                "symptoms": case_data.get("symptoms", []),
                "regulatory_alerts": case_data.get("regulatory_alerts", []),
                "fda_signal": fda_signals_data,
                "visualizations": visualizations_data,
                "summary": ai_summary_text,
                "seriousness_assessment": case_data.get("seriousness_assessment", {}),
                "causality_assessment": case_data.get("causality_assessment", {}),
                "timeline": case_data.get("timeline", []),
                "missing_data": case_data.get("missing_data", [])
            }
            if ocr_metadata:
                res_dict["ocr_metadata"] = ocr_metadata
            return res_dict
    # 2.5. Check if it is a multi-case parent document
    is_parent = False
    child_ids = []
    
    ai_summary_text = case_data.get("ai_summary", "")
    if ai_summary_text:
        try:
            summary_json = json.loads(ai_summary_text)
            if isinstance(summary_json, dict):
                if summary_json.get("is_parent") or summary_json.get("ocr_metadata", {}).get("is_parent"):
                    is_parent = True
                    child_ids = summary_json.get("child_ids") or summary_json.get("ocr_metadata", {}).get("child_ids", [])
        except Exception:
            pass
            
    if is_parent and child_ids:
        logger.info(f"Report Route: Processing parent multi-case report '{analysis_id}' with {len(child_ids)} children.")
        child_reports = []
        try:
            # Generate reports for each child case independently
            for child_id in child_ids:
                child_report = await generate_report(ReportGenerateRequest(analysis_id=child_id, force=request.force))
                child_reports.append(child_report)
                
                report_service_instance.generate_pdf_report(report_data, analysis_id)
            except Exception as e:
                logger.warning(f"Error compiling downloadable files for cached report: {e}")
                
            res_dict = {
                "report_id": analysis_id,
                "json_url": f"/report/download/{analysis_id}?format=json",
                "excel_url": f"/report/download/{analysis_id}?format=xlsx",
                "pdf_url": f"/report/download/{analysis_id}?format=pdf",
                "status": "success",
                "cached": True,
                "drug_entities": case_data.get("drugs", []),
                "symptoms": case_data.get("symptoms", []),
                "regulatory_alerts": case_data.get("regulatory_alerts", []),
                "fda_signal": fda_signals_data,
                "visualizations": visualizations_data,
                "summary": ai_summary_text,
                "seriousness_assessment": case_data.get("seriousness_assessment", {}),
                "causality_assessment": case_data.get("causality_assessment", {}),
                "timeline": case_data.get("timeline", []),
                "missing_data": case_data.get("missing_data", [])
            }
            if ocr_metadata:
                res_dict["ocr_metadata"] = ocr_metadata
            return res_dict
    # 2.5. Check if it is a multi-case parent document
    is_parent = False
                    
                    if os.path.exists(src_pdf):
                        zipf.write(src_pdf, f"case_{p_idx}_report.pdf")
                    if os.path.exists(src_pdf):
                        zipf.write(src_pdf, f"case_{p_idx}_report.pdf")
                    if os.path.exists(src_json):
                        zipf.write(src_json, f"case_{p_idx}_report.json")
                    if os.path.exists(src_xlsx):
                        zipf.write(src_xlsx, f"case_{p_idx}_report.xlsx")
                        
            parent_report_data = {
                "total_cases_detected": len(child_ids),
                "cases": cases_payload,
                "bundle_url": f"/report/download/{analysis_id}?format=zip",
                "status": "success",
                "cached": False,
                "report_id": analysis_id
            }
            
            # Save parent completed state to Supabase
            db_service.update_case_analysis_results(
                analysis_id=analysis_id,
                ai_summary=json.dumps(parent_report_data),
                seriousness_assessment={},
            # Compile consolidated response
            cases_payload = []
            for child_idx, child_rep in enumerate(child_reports):
                child_id = child_ids[child_idx]
                cases_payload.append({
                    "analysis_id": child_id,
                    "case_id": f"PV-2026-000{child_idx + 1}",
                    "patient_details": child_rep.get("patient_details", {}),
                    "drug_information": child_rep.get("drug_information", {}),
                    "adverse_events": child_rep.get("adverse_events", {}),
                    "seriousness_assessment": child_rep.get("seriousness_assessment", {}),
                    "causality_assessment": child_rep.get("causality_assessment", {}),
                    "summary": child_rep.get("ai_generated_summary") or child_rep.get("ai_generated_narrative_summary") or "",
                    "report_file": f"/report/download/{child_id}?format=pdf"
                })
                
            # Create a single ZIP bundle containing all child reports
            import zipfile
            from app.services.report_service import REPORTS_DIR
            zip_filename = f"{analysis_id}.zip"
    conditions = case_data.get("conditions", [])
    
    try:
        # A. Regulatory alerts lookup
        regulatory_alerts = regulatory_service_instance.check_banned_drugs(drugs)
        
        # B. Step 1 of FDA Pipeline: Identify suspect drug using Structured PV Object logic
        structured_drug_info = llm_service_instance.identify_suspected_drug(extracted_text)
        suspected_drug = structured_drug_info.get("suspected_drug_information", {}).get("drug_name", "Unknown")
            report_service_instance.generate_json_report(parent_report_data, analysis_id)
            report_service_instance.generate_excel_report(parent_report_data, analysis_id)
            
            return parent_report_data
        except Exception as e:
                        
            parent_report_data = {
                "total_cases_detected": len(child_ids),
                "cases": cases_payload,
                "bundle_url": f"/report/download/{analysis_id}?format=zip",
                "status": "success",
                "cached": False,
                "report_id": analysis_id
            }
            
            # Save parent completed state to Supabase
            db_service.update_case_analysis_results(
                analysis_id=analysis_id,
                ai_summary=json.dumps(parent_report_data),
                seriousness_assessment={},
                causality_assessment={},
                timeline=[],
                missing_data=[],
                regulatory_alerts=[],
                fda_signals={}
            )
            
            # Write parent JSON and Excel downloads on disk
            report_service_instance.generate_json_report(parent_report_data, analysis_id)
            report_service_instance.generate_excel_report(parent_report_data, analysis_id)
            
            return parent_report_data
        except Exception as e:
            logger.error(f"Failed to generate parent multi-case report '{analysis_id}': {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process multi-case report: {e}")

        
        # D. LLM generation of the final detailed safety report
        entities_payload = {
            "drugs": [suspected_drug],
            "symptoms": symptoms,
            "conditions": conditions
        }
        ai_analysis = llm_service_instance.generate_analysis(extracted_text, entities_payload, fda_signals, rag_context)
        
        # E. Parse the LLM response safely
        raw_summary = ai_analysis.get("raw_ai_response", "Summary pending...")
        
        parsed_ai = {}
        try:

        # Build full report data to store
        report_data = parsed_ai.copy() if isinstance(parsed_ai, dict) else {}
        report_data["regulatory_alerts"] = regulatory_alerts
        report_data["fda_signal"] = fda_signals
        report_data["visualizations"] = visualizations
        
        # Get existing ocr_metadata if any from the pending case_data
        ocr_metadata = None
        existing_ai_summary = case_data.get("ai_summary")
        if existing_ai_summary:
            try:
                existing_json = json.loads(existing_ai_summary)
                ocr_metadata = existing_json.get("ocr_metadata")
            except Exception:
        # D. LLM generation of the final detailed safety report
        entities_payload = {
            "drugs": [suspected_drug],
            "symptoms": symptoms,
            "conditions": conditions
        }
        ai_analysis = llm_service_instance.generate_analysis(extracted_text, entities_payload, fda_signals, rag_context)
        
        # E. Parse the LLM response safely
        raw_summary = ai_analysis.get("raw_ai_response", "Summary pending...")
        
        parsed_ai = {}
        try:
            clean_json = raw_summary.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            clean_json = clean_json.strip()
            parsed_ai = json.loads(clean_json)
        except Exception as parse_err:
            logger.warning(f"Could not parse raw AI response as JSON: {parse_err}")
            
        # Map values to the appropriate fields or use full report object
        ai_summary_text = parsed_ai.get("ai_generated_narrative_summary") or parsed_ai.get("summary") or raw_summary
        seriousness = parsed_ai.get("seriousness_assessment", {})
        causality = parsed_ai.get("causality_assessment", {})
        timeline = parsed_ai.get("timeline", [])
        missing_data = parsed_ai.get("missing_information") or parsed_ai.get("missing_data") or []
        
       
        report_data = normalize_report_data(report_data, ocr_metadata)
        
        # Compute evidence sources dynamically
        evidence_sources = []
        if normalized_drug and normalized_drug != "Unknown":
            fda_ev = evidence_service.get_fda_evidence(normalized_drug)
            if fda_ev.get("total_cases", 0) > 0:
                evidence_sources.append({
                    "evidence": "FDA warning document retrieved"
                })

        report_data["evidence_sources"] = evidence_sources

        # Compute reasoning explanations
        if "symptoms" not in report_data:
                existing_json = json.loads(existing_ai_summary)
                ocr_metadata = existing_json.get("ocr_metadata")
            except Exception:
                pass
        if ocr_metadata:
            report_data["ocr_metadata"] = ocr_metadata
            
        # Normalize the report data schema and ensure all required fields are correctly categorized and missing fields are listed in EVENT_DT missing format
        report_data = normalize_report_data(report_data, ocr_metadata)
        
        # Compute evidence sources dynamically
        evidence_sources = []
        if normalized_drug and normalized_drug != "Unknown":
            fda_ev = evidence_service.get_fda_evidence(normalized_drug)
            if fda_ev.get("total_cases", 0) > 0:
                evidence_sources.append({
                    "source_type": "FDA_API",
                    "evidence": f"{fda_ev.get('total_cases', 0)} FDA reported cases found"
                })
            regulatory_alerts=regulatory_alerts,
            fda_signals=fda_signals
        )
        
        # G. Generate downloadable files on disk
        report_service_instance.generate_json_report(report_data, analysis_id)
        report_service_instance.generate_excel_report(report_data, analysis_id)
        report_service_instance.generate_pdf_report(report_data, analysis_id)
        
        # Format API response data
        response_data = report_data.copy()
        response_data["report_id"] = analysis_id
        response_data["json_url"] = f"/report/download/{analysis_id}?format=json"
        response_data["excel_url"] = f"/report/download/{analysis_id}?format=xlsx"
        response_data["pdf_url"] = f"/report/download/{analysis_id}?format=pdf"
        response_data["status"] = "success"
        response_data["cached"] = False
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error during report generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{analysis_id}")
async def get_report_status(analysis_id: str):
        report_data["evidence_sources"] = evidence_sources

        # Compute reasoning explanations
        if "symptoms" not in report_data:
            report_data["symptoms"] = symptoms
        if "drug_entities" not in report_data:
            report_data["drug_entities"] = drugs
            
        report_data["reasoning_explanations"] = reasoning_service.get_reasoning_explanations(report_data)
        
        # Sync seriousness, causality and missing assessments from the normalized report data to ensure consistency
        seriousness = report_data.get("seriousness_assessment", seriousness)
        causality = report_data.get("causality_assessment", causality)
        missing_data = report_data.get("missing_information", missing_data)
        
        # F. Update Supabase
        db_service.update_case_analysis_results(
            analysis_id=analysis_id,
            ai_summary=json.dumps(report_data), # store full json here
            seriousness_assessment=seriousness,
            causality_assessment=causality,
            timeline=timeline,
            missing_data=missing_data,
            regulatory_alerts=regulatory_alerts,
            fda_signals=fda_signals
        )
        
        # G. Generate downloadable files on disk
        report_service_instance.generate_json_report(report_data, analysis_id)
        report_service_instance.generate_excel_report(report_data, analysis_id)
        report_service_instance.generate_pdf_report(report_data, analysis_id)
        
        # Format API response data
        response_data = report_data.copy()
        response_data["report_id"] = analysis_id









        )
        
        # G. Generate downloadable files on disk
        report_service_instance.generate_json_report(report_data, analysis_id)
        report_service_instance.generate_excel_report(report_data, analysis_id)
        report_service_instance.generate_pdf_report(report_data, analysis_id)
        
        # Format API response data
        response_data = report_data.copy()
        response_data["report_id"] = analysis_id
        response_data["json_url"] = f"/report/download/{analysis_id}?format=json"
        response_data["excel_url"] = f"/report/download/{analysis_id}?format=xlsx"
        response_data["pdf_url"] = f"/report/download/{analysis_id}?format=pdf"
        response_data["status"] = "success"
        response_data["cached"] = False
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error during report generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{analysis_id}")
async def get_report_status(analysis_id: str):
    """
    Checks the status of report generation for a given analysis_id.
    """
    case_data = db_service.get_case_analysis(analysis_id)
    if not case_data:
        raise HTTPException(status_code=404, detail="Analysis ID not found.")
    
    return {
        "analysis_id": analysis_id,
        "status": case_data.get("status"),
        "created_at": case_data.get("created_at")
    }

@router.get("/download/{report_id}")
async def download_report(report_id: str, format: str = "json"):
    from app.services.report_service import REPORTS_DIR
    
    filepath = os.path.join(REPORTS_DIR, f"{report_id}.{format}")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report file not found.")
    
    return FileResponse(filepath, filename=f"report_{report_id}.{format}")
