import json
import pandas as pd
import os

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

class ReportService:
def generate_json_report(self, data: dict, report_id: str) -> str:
filepath = os.path.join(REPORTS_DIR, f"{report_id}.json")
with open(filepath, 'w') as f:
json.dump(data, f, indent=4)
return filepath

def _flatten_single_case(self, data: dict) -> dict:
case_info = data.get("case_information", {}) or {}
pat_info = data.get("patient_information", {}) or {}
drug_info = data.get("suspected_drug_information", {}) or {}
event_info = data.get("adverse_event_details", {}) or {}
Created At: 2026-06-05T10:16:31Z
Completed At: 2026-06-05T10:16:31Z
File Path: `file:///Users/affu01/GRAD_PROJ_NEW/backend/app/services/report_service.py`
Total Lines: 39
Total Bytes: 1414
Showing lines 1 to 39
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import json
2: import pandas as pd
3: # from fpdf import FPDF  # Uncomment if fpdf is added to requirements
4: import os
5: 
6: REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
7: os.makedirs(REPORTS_DIR, exist_ok=True)
8: 
9: class ReportService:
10:     def generate_json_report(self, data: dict, report_id: str) -> str:
11:         filepath = os.path.join(REPORTS_DIR, f"{report_id}.json")
12:         with open(filepath, 'w') as f:
13:             json.dump(data, f, indent=4)
14:         return filepath
15: 
16:     def generate_excel_report(self, data: dict, report_id: str) -> str:
17:         filepath = os.path.join(REPORTS_DIR, f"{report_id}.xlsx")
18:         
19:         flattened = {
20:             "Summary": [data.get("summary", "")],
21:             "Drugs": [", ".join(data.get("drug_entities", []))],
22:             "Symptoms": [", ".join(data.get("symptoms", []))]
23:         }
24:         
25:         df = pd.DataFrame(
# MISSING LINE 52
# MISSING LINE 53
# MISSING LINE 54
# MISSING LINE 55
# MISSING LINE 56
# MISSING LINE 57
# MISSING LINE 58
# MISSING LINE 59
# MISSING LINE 60
# MISSING LINE 61
# MISSING LINE 62
# MISSING LINE 63
# MISSING LINE 64
# MISSING LINE 65
# MISSING LINE 66
# MISSING LINE 67
# MISSING LINE 68
# MISSING LINE 69
# MISSING LINE 70
# MISSING LINE 71
# MISSING LINE 72
# MISSING LINE 73
# MISSING LINE 74
# MISSING LINE 75
# MISSING LINE 76
# MISSING LINE 77
# MISSING LINE 78
# MISSING LINE 79
"Final Classification": data.get("final_case_classification", "Unknown")
}

}
}
]

================================================================================
LINE 1158 | STEP 1133 | TYPE VIEW_FILE | TIME 2026-06-07T17:43:20Z
================================================================================
CONTENT:
Created At: 2026-06-07T17:43:20Z
Completed At: 2026-06-07T17:43:20Z
File Path: `file:///Users/affu01/GRAD_PROJ_NEW/backend/app/services/report_service.py`
Total Lines: 39
Total Bytes: 1414
Showing lines 1 to 39
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import json
2: import pandas as pd
3: # from fpdf import FPDF  # Uncomment if fpdf is added to requirements
4: import os
5: 
6: REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
7: os.makedirs(REPORTS_DIR, exist_ok=True)
8: 
9: class ReportService:
10:     def generate_json_report(self, data: dict, report_id: str) -> str:
11:         filepath = os.path.join(REPORTS_DIR, f"{report_id}.json")
12:         with open(filepath, 'w') as f:
13:             json.dump(data, f, indent=4)
14:         return filepath
15: 
16:     def generate_excel_report(self, data: dict, report_id: str) -> str:
17:         filepath = os.path.join(REPORTS_DIR, f"{report_id}.xlsx")
18:         
19:         flattened = {
20:             "Summary": [data.get("summary", "")],
21:             "Drugs": [", ".join(data.get("drug_entities", []))],
22:             "Symptoms": [", ".join(data.get("symptoms", []))]
23:         }
missing = data.get("missing_information", [])
fda_sig = data.get("fda_signal", {})
reg_alerts = data.get("regulatory_alerts", [])

# New structured PV details
pat_details = data.get("patient_details", {}) or {}
p_demo = data.get("patient_demographic", {}) or {}
drug_details = data.get("drug_information", {}) or {}
events_details = data.get("adverse_events", {}) or {}
batch_details = data.get("drug_batch_details", {}) or {}
therapy_details = data.get("therapy_information", {}) or {}
reporter_details = data.get("reporter_information", {}) or {}
highlights = data.get("highlighted_critical_fields", [])
med_insights = data.get("medical_insights", [])
safety_obs = data.get("safety_observations", [])

# Format the PDF as a detailed text-based report that reads professionally
content = []
content.append("=" * 80)
"drug_entities": ["Methotrexate"],
"symptoms": ["Pruritus"],
"conditions": [],
"text_preview": "PROGRESS NOTES\nPatient Name: Jane Doe...",
"ocr_metadata": {
"source_type": "image",
"ocr_used": true,
"blur_score": 1.0,
"ocr_confidence": 0.9989
}
}
```

#### Ingested Milvus Record Details:
```python
{
'id': 'de582c3e-96d2-4bc6-a171-0d7881a3bc20_chunk_0', 
'blur_score': 1.0, 
'ocr_confidence': 0.9989, 
'ocr_used': True, 
'source_type': 'image'
}
```
All clinical signals, seriousness assessments, outcomes charts, and LLM analysis compiled and persisted successfully!

---

## Enhanced Pharmacovigilance Ingestion & Highlight-Aware OCR

We have successfully enhanced the text extraction layer and final clinical reporting pipeline to perform robust local parsing of key FAERS categories, identify yellow/purple visual marker highlights, and output a highly structured, compliant pharmacovigilance JSON schema.

### 1. Highlight-Aware OCR Preprocessing
* **[image_extractor.py](file:///Users/affu01/GRAD_PROJ_NEW/backend/app/services/extraction/image_extractor.py)**:
* Implemented an HSV color masking algorithm to detect yellow highlights (`HSV[15, 60, 80]` to `HSV[38, 255, 255]`) and purple/magenta highlights (`HSV[120, 30, 40]` to `HSV[170, 255, 255]`).
* Extracts these zones of interest (ROIs) as standalone sub-images, adds margin pad
* Records the text inside a dedicated `'highlighted_critical_fields'` list in `ocr_metadata`.
* Prepends these observations to the main text narrative so that the downstream LLM parses highlighted information with high priority.
* **[opencv_preprocessing.py](file:///Users/affu01/GRAD_PROJ_NEW/backend/app/services/extraction/opencv_preprocessing.py)**:
* Added mobile photo cleanup with shadow removal (background normalization division).
* Integrated perspective rotation alignment (deskewing) based on minimum area bounding boxes of text pixels to straighten tilted phone camera photos.
* Applied adaptive Gaussian binarization for clean black-on-white text output.

### 2. Local Regex & Keyword Ingestion
* **[local_pv_parser.py](file:///Users/affu01/GRAD_PROJ_NEW/backend/app/services/extraction/local_parser.py)**:
* Developed a regex-driven parser that scans documents for FAERS specific fields like lot numbers, patient weight values, event dates (normalizing formats to `YYYYMMDD`), and code categorizations (reporter occupation codes, age groups, drug roles, recur actions).

### 3. LLM Structured Report Schema
* **[llm_service.py](file:///Users/affu01/GRAD_PROJ_NEW/backend/app/services/llm_service.py)**:
* Upgraded prompt templates to enforce compliance with the new target JSON output format containing dedicated nodes: `patient_details`, `drug_information`, `drug_batch_details`, `adverse_events`, `therapy_information`, `reporter_information`, `medical_insights`, `safety_observations`.
* Integrates the local parser outputs and visual highlight regions directly into the prompt.
* Validates completeness: automatically scans for missing required clinical fields and appends them to the `"missing_information"` array (e.g. `"WT missing"`).

### 4. Downloader Updates
* **[report_service.py](file:///Users/affu01/GRAD_PROJ_NEW/backend/app/services/report_service.py)**:
* Modified the `.xlsx` compiler to map and export the new PV values, occupations, and visual highlights.
* Formatted the text-based PDF report to cleanly output dedicated sections: `--- ENHANCED PV & FAERS DETAILS ---`, `--- DETECTED HIGHLIGHTED SAFETY FIELDS ---`, and `--- SAFETY OBSERVATIONS ---`.

---

### 5. Verification Test
We tested the entire pipeline using a tilted, shadowed mobile photo mockup containing yellow-highlighted text and printed notes:
![Highlighted Medical Report Mockup Image](/Users/affu01/.gemini/antigravity-ide/brain/268c45e6-1c20-463b-b840-2ec2ac644add/highlighted_medical_report_1781171497636.png)
content.append(f"Hospitalization Count:  {fda_sig.get('hospitalizations', 0)}")
content.append(f"FDA Signal Score:       {fda_sig.get('fda_signal_score', 'Low')}")
if fda_sig.get("top_reactions"):
content.append(f"Top 10 Reactions:       {', '.join(fda_sig.get('top_reactions'))}")
content.append("")

if insights or med_insights:
content.append("--- AI SAFETY & CLINICAL INSIGHTS ---")
for insight in (insights if insights else med_insights):
content.append(f"- {insight}")
content.append("")

if safety_obs:
content.append("--- SAFETY OBSERVATIONS ---")
for obs in safety_obs:
content.append(f"- {obs}")
content.append("")

if timeline:
content.append("--- CASE TIMELINE ---")
content.append(f"Hospitalization Count:  {fda_sig.get('hospitalizations', 0)}")
content.append(f"FDA Signal Score:       {fda_sig.get('fda_signal_score', 'Low')}")
if fda_sig.get("top_reactions"):
content.append(f"Hospitalization Count:  {fda_sig.get('hospitalizations', 0)}")
content.append(f"FDA Signal Score:       {fda_sig.get('fda_signal_score', 'Low')}")
if fda_sig.get("top_reactions"):
content.append(f"Top 10 Reactions:       {', '.join(fda_sig.get('top_reactions'))}")
content.append("")

if insights or med_insights:
content.append("--- AI SAFETY & CLINICAL INSIGHTS ---")
for insight in (insights if insights else med_insights):
content.append(f"- {insight}")
content.append("")

if safety_obs:
content.append("--- SAFETY OBSERVATIONS ---")
for obs in safety_obs:
content.append(f"- {obs}")
content.append("")

if timeline:
content.append("--- CASE TIMELINE ---")
for t in timeline:
content.append(f"- [{t.get('timestamp', 'Unknown')}]: {t.get('event')}")
content.append("")

if missing:
content.append("--- MISSING CLINICAL INFORMATION ---")
for item in missing:
content.append(f"- {item}")
content.append("")

content.append("=" * 80)
content.append(f"FINAL CASE CLASSIFICATION: {data.get('final_case_classification', 'Serious ADR - Requires Medical Review')}")
content.append("=" * 80)
content.append("Generated by Pharmacovigilance AI Copilot")

with open(filepath, 'w') as f:
f.write("\n".join(content))

return filepath

report_service_instance = ReportService()

