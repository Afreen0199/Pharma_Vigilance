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

def run_in_process_test():
    print("=" * 60)
    print("IN-PROCESS TEST CLIENT VERIFICATION")
    print("=" * 60)
    
    case_text = """
A 42-year-old female with a 5-year history of rheumatoid arthritis experienced
clinically significant drug-induced hepatotoxicity following dose escalation of
Methotrexate. Clinical findings included mild hepatomegaly on abdominal palpation.
"""
    
    # Post to /analyze/text
    print("Posting to /analyze/text in-process...")
    res = client.post("/analyze/text", json={"text": case_text})
    print(f"Status Code: {res.status_code}")
    
    if res.status_code == 200:
        data = res.json()
        print(f"Analysis ID: {data.get('analysis_id')}")
        print(f"Drugs Extracted: {data.get('drug_entities')}")
        print(f"Symptoms: {data.get('symptoms')}")
        
        # Check that Abdominal Palpation is NOT in drug_entities
        drugs = data.get("drug_entities", [])
        assert "Abdominal Palpation" not in drugs, "Abdominal Palpation should be filtered out!"
        assert "Methotrexate" in drugs, "Methotrexate should be in drug_entities!"
        print("✅ In-process validation passed successfully! No noisy entities in drug_entities.")
    else:
        print(f"❌ Failed: {res.text}")
    print("=" * 60)

if __name__ == "__main__":
    run_in_process_test()
