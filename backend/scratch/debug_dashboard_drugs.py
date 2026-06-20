import sys
import os
import json

# Add backend directory to path
sys.path.append("/Users/affu01/GRAD_PROJ_NEW/backend")
from app.services.database_service import db_service

def debug():
    analyses = db_service.get_all_case_analyses()
    for a in analyses:
        print(f"--- Analysis ID: {a.get('analysis_id')} ---")
        print(f"Status: {a.get('status')}")
        print(f"Filename: {a.get('filename')}")
        
        try:
            ai_summary = json.loads(a.get("ai_summary", "{}"))
        except:
            ai_summary = {}
            
        is_multi = False
        ocr_meta = ai_summary.get("ocr_metadata", {})
        if ocr_meta.get("is_parent") is True or ai_summary.get("is_multi_case") is True:
            is_multi = True
            
        print(f"Is Multi: {is_multi}")
        
        primary_drug = "Not Available"
        if "suspected_drug_information" in ai_summary and ai_summary["suspected_drug_information"].get("drug_name"):
            primary_drug = ai_summary["suspected_drug_information"]["drug_name"]
        elif "drug_information" in ai_summary and ai_summary["drug_information"].get("product_active_ingredient"):
            primary_drug = ai_summary["drug_information"]["product_active_ingredient"]
        elif a.get("drugs"):
            primary_drug = a["drugs"][0] if a["drugs"] else "No drugs"
            
        print(f"Primary Drug logic gives: {primary_drug}")
        
        if is_multi and "cases" in ai_summary:
            print(f"Child cases found: {len(ai_summary['cases'])}")
            for c in ai_summary["cases"]:
                print(f"  Child drug_entities: {c.get('drug_entities')}")
                print(f"  Child drug_info: {c.get('drug_information', {}).get('product_active_ingredient')}")
        print("\n")

if __name__ == "__main__":
    debug()
