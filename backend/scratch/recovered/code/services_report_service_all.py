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
causality = data.get("causality_assessment", {}) or {}
entities = data.get("key_entities_extracted", {}) or {}

# New structured PV details
pat_details = data.get("patient_details", {}) or {}
p_demo = data.get("patient_demographic", {}) or {}
drug_details = data.get("drug_information", {}) or {}
events_details = data.get("adverse_events", {}) or {}
batch_details = data.get("drug_batch_details", {}) or {}
therapy_details = data.get("therapy_information", {}) or {}
reporter_details = data.get("reporter_information", {}) or {}

return {
"Case ID": case_info.get("case_id", "Unknown"),
"Report Ty
# MISSING LINE 35
# MISSING LINE 36
# MISSING LINE 37
# MISSING LINE 38
# MISSING LINE 39
# MISSING LINE 40
# MISSING LINE 41
# MISSING LINE 42
# MISSING LINE 43
# MISSING LINE 44
# MISSING LINE 45
# MISSING LINE 46
# MISSING LINE 47
# MISSING LINE 48
# MISSING LINE 49
# MISSING LINE 50
# MISSING LINE 51
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

def generate_excel_report(self, data: dict, report_id: str) -> str:
filepath = os.path.join(REPORTS_DIR, f"{report_id}.xlsx")

# Check if it is a parent multi-case record
if "cases" in data and isinstance(data["cases"], list):
rows = []
for child_case in data["cases"]:
report_file_url = child_case.get("report_file", "")
child_id = report_file_url.split("/")[-1].split("?")[0] if "/" in report_file_url else ""
if child_id:
child_json_path = os.path.join(REPORTS_DIR, f"{child_id}.json")
if os.path.exists(child_json_path):
with open(child_json_path, 'r') as f:
child_data = json.load(f)
rows.append(self._flatten_single_case(child_data))
if rows:
df = pd.DataFrame(rows)
df.to_excel(filepath, index=False)
return filepath

# Single case
row = self._flatten_single_case(data)
df = pd.DataFrame([row])
df.to_excel(filepath, index=False)
return filepath

def generate_pdf_report(self, data: dict, report_id: str) -> str:
filepath = os.path.join(REPORTS_DIR, f"{report_id}.pdf")

case_info = data.get("case_information", {})
pat_info = data.get("patient_information", {})
drug_info = data.get("suspected_drug_information", {})
event_info = data.get("adverse_event_details", {})
seriousness_ass = data.get("seriousness_assessment", {})
causality = data.get("causality_assessment", {})
entities = data.get("key_entities_extracted", {})
insights = data.get("ai_safety_insights", [])
timeline = data.get("timeline", [])
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
content.append("            PHARMACOVIGILANCE AI COPILOT - CASE SAFETY REPORT")
content.append("=" * 80)
content.append("")

content.append("--- CASE INFORMATION ---")
content.append(f"Case ID:        {case_info.get('case_id', 'Unknown')}")
content.append(f"Report Type:    {case_info.get('report_type', 'Spontaneous Report')}")
content.append(f"Report Date:    {case_info.get('report_date', 'Unknown')}")
content.append(f"Seriousness:    {case_info.get('seriousness', 'Unknown')}")
content.append(f"Case Status:    {case_info.get('case_status', 'Initial')}")
content.append("")

content.append("--- PATIENT INFORMATION ---")
content.append(f"Age:            {p_demo.get('age') or pat_info.get('age', 'Unknown')}")
content.append(f"Gender:         {p_demo.get('gender') or pat_info.get('gender', 'Unknown')}")
content.append(f"Weight:         {p_demo.get('weight') or pat_info.get('weight', 'Unknown')}")
content.append(f"Medical History:{p_demo.get('medical_history') or pat_info.get('medical_history', 'Unknown')}")
content.append("")

content.append("--- ENHANCED PV & FAERS DETAILS ---")
age_group_dict = p_demo.get("age_group") if isinstance(p_demo.get("age_group"), dict) else pat_details.get("age_group", {})
content.append(f"Age Group:      {age_group_dict.get('code', 'N/A')} - {age_group_dict.get('meaning', 'Unknown')}")
content.append(f"Patient Weight: {p_demo.get('patient_weight') or pat_details.get('patient_weight', 'Unknown')} kg")
content.append(f"Active Ingredient: {drug_details.get('product_active_ingredient', 'Unknown')}")
content.append(f"Drug Role:      {drug_details.get('drug_role', {}).get('code', 'N/A')} - {drug_details.get('drug_role', {}).get('meaning', 'Unknown')}")
content.append(f"Event Date:     {events_details.get('event_date', 'Unknown')}")
content.append(f"Drug Recur Action: {events_details.get('drug_recur_action', 'None')}")
content.append(f"Lot Number:     {batch_details.get('lot_number', 'Unknown')}")
# MISSING LINE 168
# MISSING LINE 169
# MISSING LINE 170
# MISSING LINE 171
# MISSING LINE 172
# MISSING LINE 173
# MISSING LINE 174
# MISSING LINE 175
# MISSING LINE 176
# MISSING LINE 177
# MISSING LINE 178
# MISSING LINE 179
# MISSING LINE 180
# MISSING LINE 181
# MISSING LINE 182
# MISSING LINE 183
# MISSING LINE 184
# MISSING LINE 185
# MISSING LINE 186
# MISSING LINE 187
# MISSING LINE 188
# MISSING LINE 189
# MISSING LINE 190
# MISSING LINE 191
# MISSING LINE 192
# MISSING LINE 193
# MISSING LINE 194
# MISSING LINE 195
# MISSING LINE 196
# MISSING LINE 197
# MISSING LINE 198
# MISSING LINE 199
# MISSING LINE 200
# MISSING LINE 201
# MISSING LINE 202
# MISSING LINE 203
# MISSING LINE 204
# MISSING LINE 205
# MISSING LINE 206
# MISSING LINE 207
# MISSING LINE 208
# MISSING LINE 209
# MISSING LINE 210
# MISSING LINE 211
# MISSING LINE 212
# MISSING LINE 213
# MISSING LINE 214
# MISSING LINE 215
# MISSING LINE 216
# MISSING LINE 217
# MISSING LINE 218
# MISSING LINE 219
# MISSING LINE 220
# MISSING LINE 221
# MISSING LINE 222
# MISSING LINE 223
# MISSING LINE 224
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

