import re
from typing import Dict, Any, List

# Standard occupational mapping
OCCUPATION_MAP = {
    "MD": "Physician",
    "PH": "Pharmacist",
    "OT": "Other health-professional",
    "LW": "Lawyer",
    "CN": "Consumer"
}

# Standard drug role mapping
ROLE_MAP = {
    "PS": "Primary Suspect Drug",
    "SS": "Secondary Suspect Drug",
    "C": "Concomitant",
    "I": "Interacting",
    "DN": "Drug Not Administered"
}

# Standard age group mapping
AGE_GRP_MAP = {
    "N": "Neonate",
    "I": "Infant",
    "C": "Child",
    "T": "Adolescent",
    "A": "Adult",
    "E": "Elderly"
}

def clean_date_to_yyyymmdd(date_str: str) -> str:
    """Normalizes various date formats into YYYYMMDD."""
    if not date_str:
        return ""
    # Remove separators
    digits = re.sub(r'\D', '', date_str)
    if len(digits) == 8:
        # Check if it looks like YYYYMMDD
        if digits.startswith(("19", "20")):
            return digits
        # Check if it looks like DDMMYYYY or MMDDYYYY
        # We assume MMDDYYYY / DDMMYYYY, let's pull the year from the end
        return digits[4:] + digits[:4]
    return date_str

def parse_local_pv_fields(text: str) -> Dict[str, Any]:
    """
    Scans narrative text using regex and keyword search to extract
    critical pharmacovigilance and FAERS compliant fields.
    """
    text_lower = text.lower()
    extracted = {}

    # 1. Lot / Batch Number Extraction
    lot_pattern = r'\b(?:lot|batch)(?:\s*(?:num|number|#|id|no))?\s*[:#-]?\s*([a-zA-Z0-9-]+)\b'
    lot_match = re.search(lot_pattern, text, re.IGNORECASE)
    if lot_match:
        extracted["lot_number"] = lot_match.group(1).strip()
        extracted["batch_number"] = lot_match.group(1).strip()
    else:
        extracted["lot_number"] = ""
        extracted["batch_number"] = ""

    # 2. Patient Weight (WT)
    wt_pattern = r'\b(?:wt|weight)\s*[:#-]?\s*(\d+(?:\.\d+)?)\s*(?:kg|lbs|g)?\b'
    wt_match = re.search(wt_pattern, text, re.IGNORECASE)
    if wt_match:
        extracted["patient_weight"] = wt_match.group(1).strip()
    else:
        # Fallback to plain numbers followed by kg
        kg_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(?:kg|kilograms)\b', text, re.IGNORECASE)
        extracted["patient_weight"] = kg_match.group(1).strip() if kg_match else ""

    # 3. Event Date (EVENT_DT)
    event_dt_pattern = r'\b(?:event\s*date|event_dt|event\s*dt)\s*[:#-]?\s*(\d{4}[-/]?\d{2}[-/]?\d{2}|\d{2}[-/]?\d{2}[-/]?\d{4}|\d{8})\b'
    dt_match = re.search(event_dt_pattern, text, re.IGNORECASE)
    if dt_match:
        extracted["event_date"] = clean_date_to_yyyymmdd(dt_match.group(1).strip())
    else:
        extracted["event_date"] = ""

    # 4. Age Group (AGE_GRP)
    age_group_code = ""
    if "neonate" in text_lower or "newborn" in text_lower:
        age_group_code = "N"
    elif "infant" in text_lower or "baby" in text_lower:
        age_group_code = "I"
    elif "child" in text_lower or "pediatric" in text_lower:
        age_group_code = "C"
    elif "adolescent" in text_lower or "teenager" in text_lower or "teen" in text_lower:
        age_group_code = "T"
    elif "elderly" in text_lower or "geriatric" in text_lower or "aged" in text_lower or "senior" in text_lower:
        age_group_code = "E"
    elif "adult" in text_lower or "man" in text_lower or "woman" in text_lower:
        age_group_code = "A"
        
    if age_group_code:
        extracted["age_group"] = {
            "code": age_group_code,
            "meaning": AGE_GRP_MAP[age_group_code]
        }
    else:
        extracted["age_group"] = {"code": "", "meaning": ""}

    # 5. Reporter Occupation (OCCP_COD)
    occp_code = ""
    if "physician" in text_lower or "doctor" in text_lower or "md" in text_lower or "clinician" in text_lower:
        occp_code = "MD"
    elif "pharmacist" in text_lower or "pharmd" in text_lower:
        occp_code = "PH"
    elif "lawyer" in text_lower or "attorney" in text_lower or "legal" in text_lower:
        occp_code = "LW"
    elif "consumer" in text_lower or "patient" in text_lower or "citizen" in text_lower or "parent" in text_lower:
        occp_code = "CN"
    elif "nurse" in text_lower or "health-professional" in text_lower or "therapist" in text_lower:
        occp_code = "OT"
        
    if occp_code:
        extracted["reporter_occupation"] = {
            "code": occp_code,
            "meaning": OCCUPATION_MAP[occp_code]
        }
    else:
        extracted["reporter_occupation"] = {"code": "", "meaning": ""}

    # 6. Drug Role (ROLE_COD)
    role_code = ""
    if "primary suspect" in text_lower or "suspect drug" in text_lower or "suspected drug" in text_lower:
        role_code = "PS"
    elif "secondary suspect" in text_lower:
        role_code = "SS"
    elif "concomitant" in text_lower or "co-administered" in text_lower or "taking also" in text_lower:
        role_code = "C"
    elif "interacting" in text_lower or "interaction" in text_lower:
        role_code = "I"
        
    if role_code:
        extracted["drug_role"] = {
            "code": role_code,
            "meaning": ROLE_MAP[role_code]
        }
    else:
        extracted["drug_role"] = {"code": "", "meaning": ""}

    # 7. Dose Form (DOSE_FORM)
    dose_forms = ["tablet", "capsule", "injection", "syrup", "suspension", "cream", "ointment", "patch", "solution"]
    detected_form = ""
    for df in dose_forms:
        if df in text_lower:
            detected_form = df.title()
            break
    extracted["dose_form"] = detected_form

    # 8. Active Ingredient (PROD_AI)
    # Simple dictionary check for common ingredients
    ingredients = ["methotrexate", "paracetamol", "aspirin", "warfarin", "ibuprofen", "acetaminophen", "penicillin", "lisinopril"]
    detected_ai = ""
    for ing in ingredients:
        if ing in text_lower:
            detected_ai = ing.title()
            break
    extracted["product_active_ingredient"] = detected_ai

    # 9. Drug Recur Action (DRUG_REC_ACT)
    recur_pattern = r'\b(re-administration|readministration|rechallenge|re-challenge|recurred|reappeared|re-appeared)\b'
    recur_match = re.search(recur_pattern, text_lower)
    if recur_match:
        extracted["drug_recur_action"] = "Reaction recurred/reappeared upon re-administration or rechallenge"
    else:
        extracted["drug_recur_action"] = ""

    return extracted
