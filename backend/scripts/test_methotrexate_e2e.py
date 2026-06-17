import os
import sys
import requests
import json

def run_e2e_test():
    print("=" * 60)
    print("E2E VERIFICATION FOR METHOTREXATE CASE NARRATIVE")
    print("=" * 60)
    
    # 1. Read case text
    case_text = """
================================================================================
PHARMACOVIGILANCE CASE NARRATIVE — PLAIN TEXT FORMAT
Case Reference: PV-NARR-2026-0047
Report Type: Healthcare Professional Spontaneous Report
Source: Rheumatology OPD, Madras Medical College, Chennai
Report Date: 25-May-2026
================================================================================

CASE SUMMARY
------------
A 42-year-old female with a 5-year history of rheumatoid arthritis (RA) experienced
clinically significant drug-induced hepatotoxicity (DILI) following dose escalation of
Methotrexate from 10 mg/week to 20 mg/week.

--------------------------------------------------------------------------------
PATIENT DETAILS
---------------
Patient Code  : MMC-RA-2026-0047
Age           : 42 years
Sex           : Female
Weight        : 58 kg
BMI           : 22.6 kg/m²
Occupation    : School teacher

MEDICAL HISTORY
- Rheumatoid Arthritis (seropositive, RF+, Anti-CCP+) — diagnosed 2021
- No history of alcohol consumption
- No history of hepatitis B or C infection (screened negative at baseline in 2021)
- No pre-existing liver disease

--------------------------------------------------------------------------------
SUSPECT DRUG DETAILS
--------------------
Drug Name      : Methotrexate (MTX)
Previous dose  : 10 mg once weekly (oral) — started January 2024, well tolerated
Dose change    : Escalated to 20 mg once weekly (oral) — from 01-Feb-2026
Indication     : Rheumatoid Arthritis (disease-modifying therapy — inadequate response at 10 mg)
Folic acid     : 5 mg weekly (given 2 days after MTX as per standard protocol)

CONCOMITANT MEDICATIONS
1. Hydroxychloroquine 200 mg twice daily (RA — combination DMARD)
2. Prednisolone 5 mg once daily (RA — bridging therapy)
3. Calcium + Vitamin D supplement once daily (bone protection)
4. No NSAIDs, no other hepatotoxic drugs

--------------------------------------------------------------------------------
ADVERSE EVENT DETAILS
---------------------
Event         : Drug-Induced Liver Injury (DILI) — hepatocellular pattern
Onset Date    : Approximately 10-Mar-2026 (6 weeks post dose escalation)
Presenting complaints at 12-Mar-2026 clinic visit:
  - Fatigue and malaise (onset ~1 week prior)
  - Right upper quadrant discomfort
  - Mild nausea (no vomiting)
  - No jaundice, no dark urine, no fever

Clinical findings:
  - Mild hepatomegaly on abdominal palpation
  - No splenomegaly, no ascites
  - No signs of acute liver failure
"""
    
    # 2. Submit to /analyze/text
    print("Step 1: Submitting new narrative to /analyze/text...")
    url_analyze = "http://127.0.0.1:8000/analyze/text"
    headers = {"Content-Type": "application/json"}
    payload_analyze = {"text": case_text}
    
    res_analyze = requests.post(url_analyze, json=payload_analyze, headers=headers)
    if res_analyze.status_code != 200:
        print(f"❌ Analysis failed: {res_analyze.text}")
        return
        
    data_analyze = res_analyze.json()
    analysis_id = data_analyze.get("analysis_id")
    drugs = data_analyze.get("drug_entities")
    print(f"✅ Success! Analysis ID: {analysis_id}")
    print(f"Drugs Extracted (after validator): {drugs}")
    
    # 3. Generate Report
    print(f"\nStep 2: Triggering report generation for Analysis ID {analysis_id}...")
    url_report = "http://127.0.0.1:8000/report/generate"
    payload_report = {"analysis_id": analysis_id}
    
    res_report = requests.post(url_report, json=payload_report, headers=headers)
    if res_report.status_code != 200:
        print(f"❌ Report generation failed: {res_report.text}")
        return
        
    data_report = res_report.json()
    print("✅ Success! Report generated.")
    
    # 4. Print FDA signal from generated report
    fda_signal = data_report.get("fda_signal", {})
    print("\n--- FDA SIGNAL IN NEW REPORT ---")
    print(json.dumps(fda_signal, indent=2))
    
    print("\n--- CLINICAL NARRATIVE SUMMARY ---")
    print(data_report.get("ai_generated_narrative_summary"))
    
    # Verify correctness
    assert fda_signal.get("drug_name") == "Methotrexate", f"Expected drug_name 'Methotrexate', got '{fda_signal.get('drug_name')}'"
    print("\n✅ Verification Passed: The new report successfully used 'Methotrexate' for the FDA signal, filtering out 'Abdominal Palpation'.")
    print("=" * 60)

if __name__ == "__main__":
    run_e2e_test()
