import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

MONTH_MAP = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
    "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"
}

def parse_date_to_yyyymmdd(date_str: str) -> str:
    """
    Normalizes textual dates (e.g., '02-Mar-2026', '10-May-2026', '19-May-2020') to YYYYMMDD.
    """
    if not date_str or date_str.lower() == "not specified":
        return "Not Specified"
        
    date_str_clean = date_str.strip()
    
    # 1. Match dd-mmm-yyyy (e.g. 02-Mar-2026)
    match = re.search(r'\b(\d{1,2})[-/\s]?([a-zA-Z]{3})[-/\s]?(\d{4})\b', date_str_clean)
    if match:
        day = match.group(1).zfill(2)
        month_name = match.group(2).lower()[:3]
        year = match.group(3)
        month = MONTH_MAP.get(month_name, "01")
        return f"{year}{month}{day}"
        
    # 2. Extract digits only if len is 8
    digits = re.sub(r'\D', '', date_str_clean)
    if len(digits) == 8:
        if digits.startswith(("19", "20")):
            return digits
            
    return date_str_clean

def normalize_weight(weight_str: str) -> str:
    """Extracts numeric weight values."""
    if not weight_str or weight_str.lower() == "not specified":
        return "Not Specified"
    match = re.search(r'\b(\d+(?:\.\d+)?)\b', weight_str)
    return match.group(1) if match else weight_str

def determine_age_group(age_str: str) -> Dict[str, str]:
    """
    Groups patient ages into standard FAERS age groups:
    N: Neonate, I: Infant, C: Child, T: Adolescent, A: Adult, E: Elderly.
    """
    if not age_str or age_str.lower() == "not specified":
        return {"code": "A", "meaning": "Adult"} # default to Adult
        
    # Extract numbers from string
    match = re.search(r'\b(\d+)\b', age_str)
    if not match:
        return {"code": "A", "meaning": "Adult"}
        
    age = int(match.group(1))
    
    # Grouping
    if age < 1:
        return {"code": "I", "meaning": "Infant"}
    elif age <= 12:
        return {"code": "C", "meaning": "Child"}
    elif age <= 17:
        return {"code": "T", "meaning": "Adolescent"}
    elif age <= 65:
        return {"code": "A", "meaning": "Adult"}
    else:
        return {"code": "E", "meaning": "Elderly"}

def normalize_case_data(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs normalization steps on a parsed case details dictionary.
    Maps fields to standard FAERS values, formats dates, and groups age/seriousness.
    """
    normalized = {}
    
    # Case IDs and headers
    normalized["patient_code"] = case_data.get("patient_code", "Not Specified")
    
    # Patient details
    age_str = case_data.get("age", "")
    normalized["age_group"] = determine_age_group(age_str)
    normalized["patient_weight"] = normalize_weight(case_data.get("weight", ""))
    
    # Drug details
    suspect_drug = case_data.get("suspect_drug", "Not Specified")
    # Clean dose details if embedded in drug name (e.g. "Rifampicin 600mg" -> "Rifampicin")
    active_ingredient = suspect_drug
    dose_match = re.split(r'\s+\d+', suspect_drug)
    if dose_match:
        active_ingredient = dose_match[0].strip()
    # Remove dosage units if any
    active_ingredient = re.sub(r'(?i)\b(?:mg|g|ml|iv|im|po)\b', '', active_ingredient).strip()
    normalized["product_active_ingredient"] = active_ingredient.title()
    
    # Drug role (default to PS - Primary Suspect)
    normalized["drug_role"] = {
        "code": "PS",
        "meaning": "Primary Suspect Drug"
    }
    
    # Adverse events
    onset_date = case_data.get("onset_date", "")
    normalized["event_date"] = parse_date_to_yyyymmdd(onset_date)
    
    # Drug recur action
    normalized["drug_recur_action"] = "Not Specified"
    
    # Drug batch
    normalized["lot_number"] = "Not Specified"
    normalized["batch_number"] = "Not Specified"
    normalized["expiry_date"] = "Not Specified"
    normalized["manufacturer"] = "Not Specified"
    
    # Therapy details
    dose_form = "Not Specified"
    dose_amount = "Not Specified"
    dose_unit = "Not Specified"
    dose_frequency = "Not Specified"
    route = "Not Specified"
    
    # Try parsing route and dose from suspect_drug or text
    drug_lower = suspect_drug.lower()
    if "iv" in drug_lower:
        route = "Intravenous"
    elif "im" in drug_lower:
        route = "Intramuscular"
    elif "oral" in drug_lower or "tablet" in drug_lower or "capsule" in drug_lower:
        route = "Oral"
        
    if "tablet" in drug_lower:
        dose_form = "Tablet"
    elif "capsule" in drug_lower:
        dose_form = "Capsule"
    elif "iv" in drug_lower or "im" in drug_lower:
        dose_form = "Injection"
        
    # Extract dose amount (e.g. "600mg" -> 600)
    amt_match = re.search(r'\b(\d+)\s*(mg|g|ml)\b', suspect_drug, re.IGNORECASE)
    if amt_match:
        dose_amount = amt_match.group(1)
        dose_unit = amt_match.group(2)
        
    normalized["dose_form"] = dose_form
    normalized["dose_amount"] = dose_amount
    normalized["dose_unit"] = dose_unit
    normalized["dose_frequency"] = dose_frequency
    normalized["route"] = route
    normalized["therapy_duration"] = "Not Specified"
    
    # Reporter details (default MD / Physician for clinical summaries)
    normalized["reporter_occupation"] = {
        "code": "MD",
        "meaning": "Physician"
    }
    
    # Seriousness assessment
    seriousness_str = case_data.get("seriousness", "").lower()
    hosp = "No"
    life = "No"
    dis = "No"
    death = "No"
    
    if "hospitalisation" in seriousness_str or "hospitalised" in seriousness_str or "hospitalization" in seriousness_str or "hospital" in seriousness_str or "icu" in seriousness_str:
        hosp = "Yes"
    if "life-threatening" in seriousness_str or "life threatening" in seriousness_str:
        life = "Yes"
    if "disability" in seriousness_str or "disabled" in seriousness_str:
        dis = "Yes"
    if "death" in seriousness_str or "fatal" in seriousness_str:
        death = "Yes"
        
    normalized["seriousness_assessment"] = {
        "hospitalization": hosp,
        "life_threatening": life,
        "disability": dis,
        "death": death
    }
    
    # Naranjo causality
    naranjo_str = str(case_data.get("naranjo", "")).lower()
    causality_rel = "Possible"  # default
    
    # Try to extract a numeric score first
    score_match = re.search(r'\b(-?\d+)\b', naranjo_str)
    if score_match:
        score = int(score_match.group(1))
        if score >= 9:
            causality_rel = "Highly probable"
        elif 5 <= score <= 8:
            causality_rel = "Probable"
        elif 1 <= score <= 4:
            causality_rel = "Possible"
        else:
            causality_rel = "Doubtful"
    else:
        # Fallback to text matching
        if "highly probable" in naranjo_str or "definite" in naranjo_str:
            causality_rel = "Highly probable"
        elif "probable" in naranjo_str:
            causality_rel = "Probable"
        elif "doubtful" in naranjo_str or "unlikely" in naranjo_str:
            causality_rel = "Doubtful"
        elif "possible" in naranjo_str:
            causality_rel = "Possible"
            
    conf_map = {
        "Highly probable": 0.95,
        "Probable": 0.80,
        "Possible": 0.50,
        "Doubtful": 0.20
    }
        
    normalized["causality_assessment"] = {
        "suspected_relationship": causality_rel,
        "confidence_score": conf_map.get(causality_rel, 0.50)
    }
    
    # Carry over structured raw details for LLM formatting
    normalized["raw_details"] = case_data
    
    return normalized
