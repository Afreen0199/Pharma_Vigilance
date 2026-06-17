import os
import sys
from dotenv import load_dotenv

# Add backend directory to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)
load_dotenv(os.path.join(backend_dir, ".env"))

from app.services.drug_validator_service import drug_validator_service
from app.services.fda_service import fda_service_instance

def run_tests():
    print("=" * 60)
    print("RUNNING FDA PIPELINE & DRUG ENTITY VALIDATION TESTS")
    print("=" * 60)
    
    # Test 1: Drug Entity Validation (Specified list in requirements)
    test_input = ["Abdominal Palpation", "Methotrexate", "Fatigue", "Rheumatoid Arthritis"]
    print(f"Test 1 Input: {test_input}")
    
    validated = drug_validator_service.validate_drugs(test_input)
    print(f"Test 1 Output: {validated}")
    
    assert validated == ["Methotrexate"], f"Expected ['Methotrexate'], but got {validated}"
    print("✅ Test 1 Passed: Drug validator successfully isolated 'Methotrexate'.")
    print("-" * 60)
    
    # Test 2: FDA Signal Summary for Methotrexate
    print("Test 2: Retrieving FDA Signal Summary for Methotrexate...")
    signal_summary = fda_service_instance.get_fda_signal_summary("Methotrexate")
    
    print(f"Output fields: {list(signal_summary.keys())}")
    print(f"Drug Name: {signal_summary.get('drug_name')}")
    print(f"Total Cases: {signal_summary.get('total_cases')}")
    print(f"Serious Cases: {signal_summary.get('serious_cases')}")
    print(f"Hospitalizations: {signal_summary.get('hospitalizations')}")
    print(f"Top Reactions: {signal_summary.get('top_reactions')}")
    print(f"Signal Score: {signal_summary.get('fda_signal_score')}")
    print(f"Recent Cases (Sample): {signal_summary.get('recent_cases')}")
    
    # Check format correctness
    assert signal_summary.get("drug_name") == "Methotrexate", "Drug name mismatch"
    assert isinstance(signal_summary.get("top_reactions"), list), "Top reactions should be a list"
    assert signal_summary.get("fda_signal_score") in ["Low", "Moderate", "High"], "Invalid signal score"
    
    # Check that unrelated reactions are not present
    blacklist = {
        "product quality issue", "drug dependence", "product label issue", 
        "product design issue", "device malfunction", "underdose"
    }
    for rx in signal_summary.get("top_reactions", []):
        assert rx.lower() not in blacklist, f"Blacklisted reaction term found in top reactions: {rx}"
        
    print("✅ Test 2 Passed: FDA signal summary matches structural & content requirements.")
    print("-" * 60)
    
    # Test 3: Validation failure handling
    print("Test 3: Querying FDA Signal Summary with an invalid drug term 'Abdominal Palpation'...")
    invalid_summary = fda_service_instance.get_fda_signal_summary("Abdominal Palpation")
    print(f"Output for invalid drug: {invalid_summary}")
    assert invalid_summary.get("total_cases") == 0, "Expected 0 total cases for invalid drug"
    assert invalid_summary.get("top_reactions") == [], "Expected empty top reactions for invalid drug"
    print("✅ Test 3 Passed: Pipeline handles validation failures gracefully.")
    print("=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
