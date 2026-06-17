from app.services.database_service import db_service
import sys

# Get case 3 text
case_data = db_service.get_case_analysis('2849ba4f-a901-4245-9278-40d7e3a15605')
if not case_data:
    print("Case not found!")
    sys.exit(1)

text = case_data['extracted_text']
print("--- Text ---")
print(repr(text))
print("------------")

suspect_keywords = ["suspect drug", "suspected drug", "primary suspect", "primary suspected drug"]
detected_drug = None

lines = text.split("\n")
for idx, line in enumerate(lines):
    line_lower = line.lower().strip()
    for kw in suspect_keywords:
        if kw in line_lower:
            print(f"Matched keyword '{kw}' on line {idx}: {repr(line)}")
            after_kw = ""
            if ":" in line:
                after_kw = line.split(":", 1)[1].strip()
            elif kw != line_lower:
                after_kw = line_lower.split(kw, 1)[1].strip()
            
            candidates = [after_kw] if after_kw else []
            if idx + 1 < len(lines):
                candidates.append(lines[idx+1].strip())
            if idx + 2 < len(lines):
                candidates.append(lines[idx+2].strip())
            
            print(f"Candidates: {candidates}")
            for candidate in candidates:
                candidate_lower = candidate.lower()
                for target in ["rifampicin", "vancomycin", "lithium", "haloperidol", "amiodarone", "lisinopril", "ciprofloxacin"]:
                    if target in candidate_lower:
                        detected_drug = target.capitalize()
                        print(f"Success! Matched target '{target}' in candidate '{candidate}'")
                        break
                if detected_drug:
                    break
        if detected_drug:
            break
    if detected_drug:
        break

if not detected_drug:
    print("Failed to detect drug!")
