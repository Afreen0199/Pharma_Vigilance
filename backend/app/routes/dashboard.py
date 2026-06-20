import logging
import json
import os
from collections import defaultdict
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.services.database_service import db_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def parse_json_safely(data):
    if isinstance(data, dict):
        return data
    if isinstance(data, str):
        try:
            return json.loads(data)
        except Exception:
            return {}
    return {}

@router.get("/")
async def get_dashboard_summary() -> Dict[str, Any]:
    """
    Returns a unified dashboard overview populated from existing analyses.
    No new AI inference or reports are generated here.
    """
    analyses = db_service.get_all_case_analyses()
    if not analyses:
        return {
            "statistics": {
                "total_cases": 0, "completed": 0, "processing": 0,
                "failed": 0, "high_risk": 0, "single_case_documents": 0, "multi_case_documents": 0
            },
            "submission_trend": [],
            "seriousness_distribution": {},
            "recent_uploads": [],
            "all_analyses": []
        }

    # Order analyses by created_at DESC
    try:
        analyses.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    except Exception:
        pass

    stats = {
        "total_cases": len(analyses),
        "completed": 0,
        "processing": 0,
        "failed": 0,
        "high_risk": 0,
        "single_case_documents": 0,
        "multi_case_documents": 0
    }

    trend_counts = defaultdict(int)
    seriousness_counts = defaultdict(int)

    all_analyses = []

    for a in analyses:
        # Parse stored JSON columns
        ai_summary = parse_json_safely(a.get("ai_summary", {}))
        
        status = a.get("status", "pending").lower()
        # Load file fallback if ai_summary is empty
        if not ai_summary and status == "completed" and a.get("analysis_id"):
            report_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", f"{a['analysis_id']}.json")
            if os.path.exists(report_path):
                try:
                    with open(report_path, "r") as f:
                        ai_summary = json.load(f)
                except:
                    pass

        ocr_meta = ai_summary.get("ocr_metadata", {})
        
        # Skip child records in the dashboard to prevent duplicates
        if ocr_meta.get("parent_document_id"):
            continue

        if status == "completed":
            stats["completed"] += 1
        elif status in ["failed", "error"]:
            stats["failed"] += 1
        else:
            stats["processing"] += 1

        # Trend chart date
        created_at = a.get("created_at", "")
        date_str = created_at.split("T")[0] if "T" in created_at else "Unknown"
        if date_str != "Unknown":
            trend_counts[date_str] += 1

        seriousness_assessment = parse_json_safely(a.get("seriousness_assessment", {}))
        if not seriousness_assessment and "seriousness_assessment" in ai_summary:
            seriousness_assessment = parse_json_safely(ai_summary["seriousness_assessment"])

        # Determine if multi-case
        is_multi = False
        if ocr_meta.get("is_parent") is True or ai_summary.get("is_multi_case") is True or "total_cases_detected" in ai_summary:
            is_multi = True
        
        if is_multi:
            stats["multi_case_documents"] += 1
        else:
            stats["single_case_documents"] += 1

        # Extract Primary Drug & Reaction
        primary_drug = "Not Available"
        reaction = "Not Available"
        classification = "Not Available"
        seriousness_level = "Non-Serious"
        
        classification = ai_summary.get("final_case_classification", "Not Available")
        
        # Try finding drug
        if is_multi and "cases" in ai_summary and isinstance(ai_summary["cases"], list):
            child_drugs = []
            for c in ai_summary["cases"]:
                d = c.get("drug_information", {}).get("product_active_ingredient")
                if not d and c.get("drug_entities") and len(c["drug_entities"]) > 0:
                    d = c["drug_entities"][0]
                if d and d not in child_drugs and d != "Unknown" and d != "Creatinine":
                    child_drugs.append(d)
            if child_drugs:
                primary_drug = ", ".join(child_drugs)
            else:
                primary_drug = "Multi-case Document"
        elif "suspected_drug_information" in ai_summary and ai_summary["suspected_drug_information"].get("drug_name") and ai_summary["suspected_drug_information"].get("drug_name") != "Unknown":
            primary_drug = ai_summary["suspected_drug_information"]["drug_name"]
        elif "drug_information" in ai_summary and ai_summary["drug_information"].get("product_active_ingredient") and ai_summary["drug_information"].get("product_active_ingredient") != "Unknown":
            primary_drug = ai_summary["drug_information"]["product_active_ingredient"]
        elif a.get("drugs") and isinstance(a["drugs"], list) and len(a["drugs"]) > 0:
            # Fallback but filter out common noise
            filtered = [d for d in a["drugs"] if d.lower() != "creatinine"]
            if filtered:
                primary_drug = filtered[0]
            else:
                primary_drug = a["drugs"][0]
        
        # Try finding reaction
        if "adverse_event_details" in ai_summary and ai_summary["adverse_event_details"].get("adverse_event"):
            reaction = ai_summary["adverse_event_details"]["adverse_event"]
        elif a.get("symptoms") and isinstance(a["symptoms"], list) and len(a["symptoms"]) > 0:
            reaction = a["symptoms"][0]

        # High Risk Logic
        is_high_risk = False
        if "high risk" in classification.lower() or "serious adr" in classification.lower():
            is_high_risk = True
        if ai_summary.get("regulatory_alerts") and len(ai_summary["regulatory_alerts"]) > 0:
            is_high_risk = True

        if seriousness_assessment:
            lvl = seriousness_assessment.get("level", seriousness_assessment.get("suspected_relationship", ""))
            if lvl:
                seriousness_level = str(lvl)
            else:
                seriousness_level = "Serious"
            
            if seriousness_assessment.get("caused_hospitalization") or seriousness_assessment.get("life_threatening"):
                is_high_risk = True
                seriousness_level = "Serious"

        if is_high_risk:
            stats["high_risk"] += 1
            
        if status == "completed":
            s_key = "Serious" if "serious" in seriousness_level.lower() and "non" not in seriousness_level.lower() else "Non-Serious"
            seriousness_counts[s_key] += 1

        all_analyses.append({
            "analysis_id": a.get("analysis_id", ""),
            "filename": a.get("filename", "Unknown"),
            "primary_drug": primary_drug,
            "reaction": reaction,
            "status": status.capitalize(),
            "classification": classification,
            "seriousness": seriousness_level,
            "created_at": created_at,
            "is_multi_case": is_multi
        })

    # Recalculate total_cases dynamically
    total_cases = 0
    for a in all_analyses:
        if a["is_multi_case"]:
            # Count the number of drugs as a proxy for cases if total_cases_detected not parsed easily, 
            # or we can pull it directly. 
            count = len(a["primary_drug"].split(",")) if "Multi-case" not in a["primary_drug"] else 2
            total_cases += max(2, count) # Safe default for multi
        else:
            total_cases += 1
            
    stats["total_cases"] = total_cases

    submission_trend = [{"date": k, "count": v} for k, v in sorted(trend_counts.items())]

    # ensure basic serious vs non_serious keys exist
    if "Serious" not in seriousness_counts: seriousness_counts["Serious"] = 0
    if "Non-Serious" not in seriousness_counts: seriousness_counts["Non-Serious"] = 0

    return {
        "statistics": stats,
        "submission_trend": submission_trend,
        "seriousness_distribution": {
            "serious": seriousness_counts["Serious"],
            "non_serious": seriousness_counts["Non-Serious"]
        },
        "recent_uploads": all_analyses[:5],
        "all_analyses": all_analyses
    }
