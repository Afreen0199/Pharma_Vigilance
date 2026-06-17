import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def extract_kv_pairs(text: str) -> Dict[str, str]:
    """
    Scans lines for specific PV field labels and extracts the subsequent lines
    as values. This is designed for table/register grids serialized as lines.
    """
    # Split by lines and clean
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    kv = {}
    
    # Standard labels in medical registers / logs
    labels = [
        ("patient_code", ["patient code", "subject id", "patient code value", "subject id value"]),
        ("age_sex", ["age / sex", "age/sex"]),
        ("weight", ["weight"]),
        ("history", ["medical history"]),
        ("suspect_drug", ["suspect drug", "suspect drugs", "investigational drug"]),
        ("adr", ["adr", "sae", "adverse event"]),
        ("onset", ["onset"]),
        ("labs", ["key labs", "labs, imaging:", "labs", "ct findings", "labs, imaging"]),
        ("action", ["action", "action taken"]),
        ("outcome", ["outcome"]),
        ("seriousness", ["seriousness"]),
        ("naranjo", ["naranjo"]),
        ("meddra_pt", ["meddra pt", "meddra"])
    ]
    
    for label_key, label_aliases in labels:
        for idx, line in enumerate(lines):
            line_lower = line.lower()
            # Match label alias exactly, or as a word boundary prefix
            if any(alias == line_lower or line_lower.startswith(alias + " ") or line_lower.startswith(alias + ":") for alias in label_aliases):
                # The value is usually on the next line
                if idx + 1 < len(lines):
                    next_line = lines[idx + 1]
                    # If the next line is itself a label alias, then the value for the current label is empty
                    is_other_label = False
                    for _, other_aliases in labels:
                        if any(next_line.lower() == other_alias or next_line.lower().startswith(other_alias + " ") or next_line.lower().startswith(other_alias + ":") for other_alias in other_aliases):
                            is_other_label = True
                            break
                    if not is_other_label:
                        kv[label_key] = next_line
                        break
    return kv

def parse_segmented_case(text: str) -> Dict[str, Any]:
    """
    Transforms a raw segmented patient text section into a parsed case dictionary.
    First tries grid/table key extraction, then falls back to regex lookups.
    """
    # 1. Table/Grid KV pair extraction
    kv = extract_kv_pairs(text)
    
    # 2. Local regex extraction
    from app.services.extraction.local_parser import parse_local_pv_fields
    regex_fields = parse_local_pv_fields(text)
    
    merged = {}
    
    # Patient Code / Subject ID
    merged["patient_code"] = kv.get("patient_code") or ""
    if not merged["patient_code"]:
        # Search for Subject ID or Patient Code via regex
        id_match = re.search(r'\b(?:MMC-ADR|BPI-CARD|APL-W3)-[a-zA-Z0-9-]+\b', text)
        if id_match:
            merged["patient_code"] = id_match.group(0).strip()
            
    # Age & Sex splitting
    age_sex = kv.get("age_sex", "")
    age = ""
    gender = ""
    if age_sex and "/" in age_sex:
        parts = age_sex.split("/")
        age = parts[0].strip()
        gender = parts[1].strip()
    elif age_sex and "Yrs" in age_sex:
        parts = age_sex.split()
        age = parts[0].strip() + " Years"
        
    # If not found in table KV, search via regex in the narrative text
    if not age:
        age_match = re.search(r'\b(\d+)\s*(?:years|yrs|yr-old|year-old|yrs-old)\b', text, re.IGNORECASE)
        if age_match:
            age = age_match.group(0).strip()
    if not gender:
        gender_match = re.search(r'\b(female|male|woman|man|boy|girl)\b', text, re.IGNORECASE)
        if gender_match:
            gender = gender_match.group(1).strip()
            
    merged["age"] = age
    merged["gender"] = gender
    
    # Patient Weight
    merged["weight"] = kv.get("weight") or regex_fields.get("patient_weight", "")
    if not merged["weight"]:
        wt_match = re.search(r'\b(\d+)\s*(?:kg|kilograms|lbs)\b', text, re.IGNORECASE)
        if wt_match:
            merged["weight"] = wt_match.group(1).strip()
            
    # Medical History
    merged["medical_history"] = kv.get("history") or "Not Specified"
    
    # Suspect Drug
    merged["suspect_drug"] = kv.get("suspect_drug") or regex_fields.get("product_active_ingredient", "")
    if not merged["suspect_drug"]:
        # Guess from the text or scispacy validator later
        pass
        
    # Reaction
    merged["reaction"] = kv.get("adr") or ""
    
    # Onset Date
    merged["onset_date"] = kv.get("onset") or regex_fields.get("event_date", "")
    
    # Spacing and details
    merged["labs"] = kv.get("labs") or ""
    merged["action_taken"] = kv.get("action") or ""
    merged["outcome"] = kv.get("outcome") or ""
    merged["naranjo"] = kv.get("naranjo") or ""
    merged["meddra_pt"] = kv.get("meddra_pt") or ""
    merged["seriousness"] = kv.get("seriousness") or ""
    
    # Ensure default values for missing details
    for k, v in merged.items():
        if not v:
            merged[k] = "Not Specified"
            
    return merged
