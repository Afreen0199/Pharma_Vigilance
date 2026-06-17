import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def find_patient_boundaries(text: str) -> List[Dict[str, Any]]:
    """
    Parses a digital text document to detect patient section boundaries.
    Looks for repeated headers or templates (e.g. PATIENT 1 OF 4, SUBJECT 1 OF 2, Patient Code:, Subject ID:).
    Returns a list of dictionaries with section details:
      {"start": start_char_idx, "end": end_char_idx, "case_header": match_text, "patient_index": index}
    """
    if not text:
        return []

    boundaries = []
    
    # 1. Look for explicit multi-patient section headers:
    # PATIENT 1 OF 4, SUBJECT 1 OF 2, CASE 1 OF 3, etc.
    pattern_explicit = r'(?i)\b(?:patient|subject|case|subj)\s+(\d+)\s+of\s+(\d+)\b'
    matches = list(re.finditer(pattern_explicit, text))
    
    if len(matches) > 1:
        logger.info(f"Patient Boundary Detector: Detected {len(matches)} explicit section headers via PATIENT X OF Y.")
        for idx, match in enumerate(matches):
            start = match.start()
            patient_index = int(match.group(1))
            case_header = match.group(0)
            boundaries.append({
                "start": start,
                "case_header": case_header,
                "patient_index": patient_index
            })
            
        # Sort by start offset
        boundaries = sorted(boundaries, key=lambda x: x["start"])
        # Set end coordinates
        for idx in range(len(boundaries)):
            next_idx = idx + 1
            boundaries[idx]["end"] = boundaries[next_idx]["start"] if next_idx < len(boundaries) else len(text)
            
        return boundaries

    # 2. Look for explicit standalone case numbers at start of lines or within text:
    # PATIENT 1, SUBJECT 2, CASE 3, etc.
    pattern_standalone = r'(?i)\b(?:patient|subject|case|subj)\s*(\d+)\s*(?:of\s*[a-zA-Z0-9]+)?\b'
    # Filter for multiple matches that form a sequence (e.g., Patient 1, Patient 2) or simply multiple distinct numbers
    matches = list(re.finditer(pattern_standalone, text))
    if len(matches) > 1:
        logger.info(f"Patient Boundary Detector: Detected {len(matches)} potential case/patient references.")
        # Deduplicate matches that are too close (e.g. within 50 chars) or repeat the same patient index
        seen_indices = set()
        for match in matches:
            patient_index = int(match.group(1))
            if patient_index not in seen_indices:
                seen_indices.add(patient_index)
                boundaries.append({
                    "start": match.start(),
                    "case_header": match.group(0).strip(),
                    "patient_index": patient_index
                })
                
        if len(boundaries) > 1:
            boundaries = sorted(boundaries, key=lambda x: x["start"])
            for idx in range(len(boundaries)):
                next_idx = idx + 1
                boundaries[idx]["end"] = boundaries[next_idx]["start"] if next_idx < len(boundaries) else len(text)
            return boundaries

    # 3. Fallback: Look for repeated identifier tags like "Patient Code", "Subject ID", "Patient ID", or "Patie (Code:"
    boundaries = []
    pattern_identifiers = r'(?i)\b(?:patient\s*code|subject\s*id|patient\s*id|patie\s*\(?code)\b'
    matches = list(re.finditer(pattern_identifiers, text))
    if len(matches) > 1:
        logger.info(f"Patient Boundary Detector: Detected {len(matches)} repeated patient/subject identifier tags. Splitting text.")
        for idx, match in enumerate(matches):
            start = match.start()
            boundaries.append({
                "start": start,
                "case_header": f"Case {idx + 1}",
                "patient_index": idx + 1
            })
            
        boundaries = sorted(boundaries, key=lambda x: x["start"])
        for idx in range(len(boundaries)):
            next_idx = idx + 1
            boundaries[idx]["end"] = boundaries[next_idx]["start"] if next_idx < len(boundaries) else len(text)
            
        return boundaries

    # If no boundaries found, return empty list
    logger.info("Patient Boundary Detector: No multi-case text boundaries detected.")
    return []
