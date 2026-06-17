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

def run_multicase_tests():
    print("=" * 70)
    print("RUNNING MULTI-CASE DOCUMENT SEGMENTATION E2E TESTS")
    print("=" * 70)
    
    # ----------------------------------------------------
    # TEST 1: Hospital Monthly ADR Register (4 digital cases)
    # ----------------------------------------------------
    print("\n--- TEST 1: Hospital Monthly ADR Register (4 Cases) ---")
    register_pdf = "/Users/affu01/GRAD_PROJ_NEW/Sample_PV_Inputs2/17_adr_register_4patients_multi_case.pdf"
    if not os.path.exists(register_pdf):
        print(f"❌ Reference PDF not found at: {register_pdf}")
        sys.exit(1)
        
    print(f"Uploading Monthly Register PDF: {os.path.basename(register_pdf)}")
    with open(register_pdf, "rb") as f:
        files = {"file": (os.path.basename(register_pdf), f, "application/pdf")}
        res_analyze = client.post("/analyze/", files=files)
        
    print(f"Analyze Status Code: {res_analyze.status_code}")
    if res_analyze.status_code != 200:
        print(f"❌ Ingestion failed: {res_analyze.text}")
        sys.exit(1)
        
    analyze_data = res_analyze.json()
    parent_id = analyze_data.get("analysis_id")
    total_cases = analyze_data.get("total_cases_detected")
    print(f"✅ Success! Ingested Monthly Register. Parent Analysis ID: {parent_id}")
    print(f"Total Cases Detected: {total_cases}")
    assert total_cases == 4, f"Expected 4 cases, got {total_cases}!"
    
    cases = analyze_data.get("cases", [])
    assert len(cases) == 4, "Expected 4 case segments!"
    
    for idx, c in enumerate(cases):
        print(f"  Case Segment {idx+1}: Child ID={c.get('analysis_id')}, Patient Index={c.get('patient_index')}")
        print(f"    Drugs: {c.get('drug_entities')}")
        print(f"    Symptoms: {c.get('symptoms')}")
        assert c.get("patient_index") == idx + 1, "Patient index mismatch!"
        assert c.get("analysis_id") is not None, "Child analysis ID is missing!"
        
    # Trigger report generation for parent case
    print(f"\nTriggering multi-case report generation for parent ID {parent_id}...")
    res_report = client.post("/report/generate", json={"analysis_id": parent_id})
    print(f"Report Generation Status Code: {res_report.status_code}")
    if res_report.status_code != 200:
        print(f"❌ Report generation failed: {res_report.text}")
        sys.exit(1)
        
    report_data = res_report.json()
    print("✅ Success! Parent and child reports generated.")
    assert report_data.get("total_cases_detected") == 4, "Expected 4 cases in completed report!"
    
    completed_cases = report_data.get("cases", [])
    assert len(completed_cases) == 4, "Expected 4 completed case reports in list!"
    
    # Verify separate patient/drug details for each case
    # Patient 1: Rifampicin / Joint pain
    # Patient 2: Vancomycin / Red Man Syndrome
    # Patient 3: Lithium / Tremor
    # Patient 4: Haloperidol / rigidity
    expected_drugs = ["Rifampicin", "Vancomycin", "Lithium", "Haloperidol"]
    for idx, c in enumerate(completed_cases):
        case_id = c.get("case_id")
        active_ing = c.get("drug_information", {}).get("product_active_ingredient", "")
        weight = c.get("patient_details", {}).get("patient_weight", "")
        summary = c.get("summary", "")
        report_url = c.get("report_file", "")
        
        print(f"  Completed Child Case {idx+1}: {case_id}")
        print(f"    Active Ingredient: {active_ing}")
        print(f"    Weight: {weight} kg")
        print(f"    Report Download URL: {report_url}")
        
        assert expected_drugs[idx].lower() in active_ing.lower(), f"Expected active ingredient '{expected_drugs[idx]}', got '{active_ing}'!"
        assert weight != "Not Specified", "Patient weight should be extracted!"
        assert report_url.startswith("/report/download/"), "Missing report file download URL!"
        
    # Verify zip bundle exists
    from app.services.report_service import REPORTS_DIR
    zip_path = os.path.join(REPORTS_DIR, f"{parent_id}.zip")
    assert os.path.exists(zip_path), f"ZIP bundle not found at {zip_path}!"
    print(f"✓ ZIP bundle successfully compiled at: {zip_path}")
    
    # Verify excel report exists and has multiple rows
    xlsx_path = os.path.join(REPORTS_DIR, f"{parent_id}.xlsx")
    assert os.path.exists(xlsx_path), f"Excel report not found at {xlsx_path}!"
    import pandas as pd
    df = pd.read_excel(xlsx_path)
    print(f"✓ Excel report created with {len(df)} rows (columns: {list(df.columns)[:5]}...)")
    assert len(df) == 4, f"Expected 4 rows in Excel report, got {len(df)}!"
    
    # ----------------------------------------------------
    # TEST 2: Scanned Multi-Patient Fax (3 color-coded cases)
    # ----------------------------------------------------
    print("\n--- TEST 2: Fax Scanned Multi-Patient AE Summary (3 Cases) ---")
    fax_pdf = "/Users/affu01/GRAD_PROJ_NEW/Sample_PV_Inputs2/12_fax_multi_patient_ward_round_3cases.pdf"
    if not os.path.exists(fax_pdf):
        print(f"❌ Scanned Fax PDF not found at: {fax_pdf}")
        sys.exit(1)
        
    print(f"Uploading Fax Scanned PDF: {os.path.basename(fax_pdf)}")
    with open(fax_pdf, "rb") as f:
        files = {"file": (os.path.basename(fax_pdf), f, "application/pdf")}
        res_analyze2 = client.post("/analyze/", files=files)
        
    print(f"Analyze Status Code: {res_analyze2.status_code}")
    if res_analyze2.status_code != 200:
        print(f"❌ Ingestion failed: {res_analyze2.text}")
        sys.exit(1)
        
    analyze_data2 = res_analyze2.json()
    parent_id2 = analyze_data2.get("analysis_id")
    total_cases2 = analyze_data2.get("total_cases_detected")
    print(f"✅ Success! Ingested Fax PDF. Parent Analysis ID: {parent_id2}")
    print(f"Total Cases Detected: {total_cases2}")
    assert total_cases2 == 3, f"Expected 3 cases, got {total_cases2}!"
    
    cases2 = analyze_data2.get("cases", [])
    assert len(cases2) == 3, "Expected 3 case segments!"
    
    # Trigger report generation for scanned parent
    print(f"\nTriggering multi-case report generation for scanned parent ID {parent_id2}...")
    res_report2 = client.post("/report/generate", json={"analysis_id": parent_id2})
    print(f"Report Generation Status Code: {res_report2.status_code}")
    if res_report2.status_code != 200:
        print(f"❌ Report generation failed: {res_report2.text}")
        sys.exit(1)
        
    report_data2 = res_report2.json()
    print("✅ Success! Scanned parent and child reports generated.")
    assert report_data2.get("total_cases_detected") == 3, "Expected 3 cases in completed report!"
    
    completed_cases2 = report_data2.get("cases", [])
    # Case 1: Amiodarone / Thyrotoxicosis
    # Case 2: Lisinopril / Angioedema
    # Case 3: Ciprofloxacin / Tendon rupture
    expected_drugs2 = ["Amiodarone", "Lisinopril", "Ciprofloxacin"]
    for idx, c in enumerate(completed_cases2):
        active_ing = c.get("drug_information", {}).get("product_active_ingredient", "")
        print(f"  Completed Child Case {idx+1}: Active Ingredient={active_ing}")
        assert expected_drugs2[idx].lower() in active_ing.lower(), f"Expected active ingredient '{expected_drugs2[idx]}', got '{active_ing}'!"
        
    zip_path2 = os.path.join(REPORTS_DIR, f"{parent_id2}.zip")
    assert os.path.exists(zip_path2), f"ZIP bundle not found at {zip_path2}!"
    print(f"✓ ZIP bundle successfully compiled at: {zip_path2}")
    
    print("\n🎉 ALL E2E MULTI-CASE SEGMENTATION TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_multicase_tests()
