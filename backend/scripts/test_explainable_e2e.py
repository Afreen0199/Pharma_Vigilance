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

def run_explainable_e2e_tests():
    print("=" * 80)
    print("RUNNING EXPLAINABLE AI & EVIDENCE ENGINE E2E TESTS")
    print("=" * 80)

    # 1. Ingest a patient case narrative
    narrative_text = (
        "Patient is a 71-year-old female (weighing 62 kg) who was prescribed Amiodarone "
        "for ventricular arrhythmia. Five weeks after starting therapy, she developed severe "
        "thyroid toxicosis, presenting with palpitations, tremor, and weight loss. She was hospitalized "
        "for medical stabilization, and Amiodarone was discontinued (positive dechallenge)."
    )

    print("\nStep 1: Ingesting case narrative via /analyze...")
    res_analyze = client.post("/analyze/", data={"text": narrative_text})
    print(f"Ingestion status: {res_analyze.status_code}")
    if res_analyze.status_code != 200:
        print(f"❌ Ingestion failed: {res_analyze.text}")
        sys.exit(1)

    analyze_data = res_analyze.json()
    analysis_id = analyze_data.get("analysis_id")
    print(f"✅ Ingestion successful. Analysis ID: {analysis_id}")
    print(f"Extracted drugs: {analyze_data.get('drug_entities')}")
    print(f"Extracted symptoms: {analyze_data.get('symptoms')}")

    # 2. Trigger report generation
    print(f"\nStep 2: Triggering report generation for analysis ID {analysis_id}...")
    res_report = client.post("/report/generate", json={"analysis_id": analysis_id})
    print(f"Report status: {res_report.status_code}")
    if res_report.status_code != 200:
        print(f"❌ Report generation failed: {res_report.text}")
        sys.exit(1)

    report_data = res_report.json()
    print("✅ Safety report compiled.")

    # 3. Assert Patient Demographic consolidation structure
    print("\nStep 3: Checking Patient Demographic schema...")
    assert "patient_demographic" in report_data, "❌ 'patient_demographic' key is missing from report JSON!"
    demo = report_data["patient_demographic"]
    print(f"  Unified demographic block: {demo}")
    for key in ["age", "gender", "weight", "medical_history", "age_group", "patient_weight"]:
        assert key in demo, f"❌ Key '{key}' is missing from patient_demographic!"
    print("  ✓ patient_demographic block verified successfully.")

    # Assert dual compatibility legacy fields
    print("  Checking dual compatibility legacy mappings...")
    assert "patient_information" in report_data, "❌ Legacy 'patient_information' is missing!"
    assert "patient_details" in report_data, "❌ Legacy 'patient_details' is missing!"
    assert report_data["patient_details"].get("patient_weight") == demo["patient_weight"], "❌ Weight mismatch in legacy mapping!"
    print("  ✓ Backward compatibility keys are present and mapped correctly.")

    # 4. Assert reasoning explanations and evidence sources appended at the root
    print("\nStep 4: Checking appended reasoning and evidence sources...")
    assert "evidence_sources" in report_data, "❌ 'evidence_sources' is missing from report JSON!"
    assert "reasoning_explanations" in report_data, "❌ 'reasoning_explanations' is missing from report JSON!"
    
    print(f"  Evidence Sources: {report_data['evidence_sources']}")
    print(f"  Reasoning Explanations: {json.dumps(report_data['reasoning_explanations'], indent=2)}")
    
    assert len(report_data["evidence_sources"]) > 0, "❌ Evidence sources list should not be empty!"
    assert "causality" in report_data["reasoning_explanations"], "❌ Causality reasoning is missing!"
    assert "seriousness" in report_data["reasoning_explanations"], "❌ Seriousness reasoning is missing!"
    print("  ✓ Reasoning and evidence sources verified successfully.")

    # 5. Query GET /verify-drug/{drug_name}
    drug_to_verify = "Amiodarone"
    print(f"\nStep 5: Querying GET /verify-drug/{drug_to_verify}...")
    res_verify_drug = client.get(f"/verify-drug/{drug_to_verify}")
    print(f"Verify Drug status: {res_verify_drug.status_code}")
    if res_verify_drug.status_code != 200:
        print(f"❌ Verify Drug failed: {res_verify_drug.text}")
        sys.exit(1)

    verify_drug_data = res_verify_drug.json()
    print(f"  Verification Status: {verify_drug_data.get('verification_status')}")
    assert verify_drug_data.get("drug_name").lower() == drug_to_verify.lower(), "❌ Drug name mismatch!"
    assert "fda_evidence" in verify_drug_data, "❌ fda_evidence is missing!"
    assert "local_faers_evidence" in verify_drug_data, "❌ local_faers_evidence is missing!"
    assert "knowledge_base_evidence" in verify_drug_data, "❌ knowledge_base_evidence is missing!"
    assert "supporting_cases" in verify_drug_data, "❌ supporting_cases is missing!"
    print("  ✓ Verify Drug response format verified successfully.")

    # 6. Query GET /verify-analysis/{analysis_id}
    print(f"\nStep 6: Querying GET /verify-analysis/{analysis_id}...")
    res_verify_analysis = client.get(f"/verify-analysis/{analysis_id}")
    print(f"Verify Analysis status: {res_verify_analysis.status_code}")
    if res_verify_analysis.status_code != 200:
        print(f"❌ Verify Analysis failed: {res_verify_analysis.text}")
        sys.exit(1)

    verify_analysis_data = res_verify_analysis.json()
    print(f"  Confidence Score: {verify_analysis_data.get('confidence_score')}")
    print(f"  Verified Claims: {verify_analysis_data.get('verified_claims')}")
    assert "verified_claims" in verify_analysis_data, "❌ verified_claims is missing!"
    assert "causality_reasoning" in verify_analysis_data, "❌ causality_reasoning is missing!"
    assert "seriousness_reasoning" in verify_analysis_data, "❌ seriousness_reasoning is missing!"
    assert "confidence_score" in verify_analysis_data, "❌ confidence_score is missing!"
    print("  ✓ Verify Analysis response format verified successfully.")

    # 7. Query GET /evidence/{analysis_id}
    print(f"\nStep 7: Querying GET /evidence/{analysis_id}...")
    res_evidence = client.get(f"/evidence/{analysis_id}")
    print(f"Evidence status: {res_evidence.status_code}")
    if res_evidence.status_code != 200:
        print(f"❌ Evidence retrieval failed: {res_evidence.text}")
        sys.exit(1)

    evidence_data = res_evidence.json()
    print(f"  Retrieved Chunks: {len(evidence_data.get('retrieved_chunks', []))} chunks")
    assert "retrieved_chunks" in evidence_data, "❌ retrieved_chunks is missing!"
    assert "fda_evidence" in evidence_data, "❌ fda_evidence is missing!"
    assert "faers_evidence" in evidence_data, "❌ faers_evidence is missing!"
    assert "kb_references" in evidence_data, "❌ kb_references is missing!"
    
    for chunk in evidence_data.get("retrieved_chunks", []):
        assert "source_document" in chunk, "❌ chunk is missing 'source_document'!"
        assert "source_type" in chunk, "❌ chunk is missing 'source_type'!"
        assert "retrieval_score" in chunk, "❌ chunk is missing 'retrieval_score'!"
        assert "analysis_id" in chunk, "❌ chunk is missing 'analysis_id'!"
    print("  ✓ Evidence chunks schema verified successfully.")

    print("\n🎉 ALL EXPLAINABLE AI & EVIDENCE ENGINE TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_explainable_e2e_tests()
