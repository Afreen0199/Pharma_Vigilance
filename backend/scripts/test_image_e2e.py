import os
import sys
import json
from dotenv import load_dotenv
from fastapi.testclient import TestClient

# Add backend directory to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)
load_dotenv(os.path.join(backend_dir, ".env"))

from main import app
client = TestClient(app)

def run_image_e2e_test():
    print("=" * 60)
    print("IN-PROCESS IMAGE E2E PIPELINE VERIFICATION")
    print("=" * 60)
    
    image_path = "/Users/affu01/.gemini/antigravity-ide/brain/268c45e6-1c20-463b-b840-2ec2ac644add/highlighted_medical_report_1781171497636.png"
    if not os.path.exists(image_path):
        print(f"❌ Image not found at {image_path}")
        return
        
    print(f"Uploading image: {os.path.basename(image_path)}")
    with open(image_path, "rb") as img_file:
        files = {"file": (os.path.basename(image_path), img_file, "image/png")}
        res_analyze = client.post("/analyze/", files=files)
        
    print(f"Analyze status code: {res_analyze.status_code}")
    if res_analyze.status_code != 200:
        print(f"❌ Analyze failed: {res_analyze.text}")
        return
        
    analyze_data = res_analyze.json()
    analysis_id = analyze_data.get("analysis_id")
    print(f"✅ Success! Ingested image case. Analysis ID: {analysis_id}")
    print(f"Extracted OCR metadata: {json.dumps(analyze_data.get('ocr_metadata'), indent=2)}")
    
    # Check highlights are present in metadata
    ocr_meta = analyze_data.get("ocr_metadata", {})
    highlights = ocr_meta.get("highlighted_critical_fields", [])
    print(f"OCR Highlights found: {highlights}")
    assert len(highlights) > 0, "No OCR highlights found in metadata!"
    
    # 2. Trigger Report Generation
    print("\nTriggering report generation...")
    res_report = client.post("/report/generate", json={"analysis_id": analysis_id})
    print(f"Report status code: {res_report.status_code}")
    if res_report.status_code != 200:
        print(f"❌ Report generation failed: {res_report.text}")
        return
        
    report_data = res_report.json()
    print("✅ Success! Report generated successfully.")
    
    # 3. Validate Structured Response Layout
    print("\n--- VALIDATING NEW STRUCTURED PV SCHEMA ---")
    required_sections = [
        "patient_details", "drug_information", "adverse_events",
        "drug_batch_details", "therapy_information", "reporter_information"
    ]
    for section in required_sections:
        assert section in report_data, f"Missing section '{section}' in report!"
        assert isinstance(report_data[section], dict), f"Section '{section}' should be a dictionary!"
        print(f"✓ Section '{section}' exists and is a dictionary.")
        
    # Check specific fields mapping
    # 1. Patient weight
    weight_val = report_data["patient_details"].get("patient_weight")
    print(f"Patient Weight: {weight_val}")
    
    # 2. Age Group
    age_group = report_data["patient_details"].get("age_group", {})
    print(f"Age Group: {age_group}")
    assert "code" in age_group and "meaning" in age_group, "Age group dictionary must contain 'code' and 'meaning'!"
    
    # 3. Lot / Batch
    lot_num = report_data["drug_batch_details"].get("lot_number")
    print(f"Lot Number: {lot_num}")
    assert lot_num == "LOT-AX9921", f"Expected lot_number 'LOT-AX9921', got '{lot_num}'!"
    
    # 4. Highlighted Critical Fields
    report_highlights = report_data.get("highlighted_critical_fields", [])
    print(f"Report Highlighted Fields: {report_highlights}")
    assert any("LOT-AX9921" in h for h in report_highlights), "Expected highlighted lot number in report highlighted fields!"
    
    # 5. Missing Information Formatting
    missing_info = report_data.get("missing_information", [])
    print(f"Missing Information: {missing_info}")
    assert isinstance(missing_info, list), "missing_information must be a list!"
    for item in missing_info:
        assert item.endswith(" missing"), f"Missing info item '{item}' must end with ' missing'!"
    print("✓ All items in missing_information correctly follow 'FIELD_NAME missing' format.")
    
    print("\n🎉 ALL E2E VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_image_e2e_test()
