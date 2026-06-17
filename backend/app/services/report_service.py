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
        
        age_group_dict = p_demo.get("age_group") if isinstance(p_demo.get("age_group"), dict) else pat_details.get("age_group") or {}
        reporter_occ_dict = reporter_details.get("occupation") if isinstance(reporter_details.get("occupation"), dict) else {}
        drug_role_dict = drug_details.get("drug_role") if isinstance(drug_details.get("drug_role"), dict) else {}

        return {
            "Case ID": case_info.get("case_id", "Unknown"),
            "Report Type": case_info.get("report_type", "Spontaneous Report"),
            "Report Date": case_info.get("report_date", "Unknown"),
            "Seriousness": case_info.get("seriousness", "Unknown"),
            "Case Status": case_info.get("case_status", "Initial"),
            "Patient Age": p_demo.get("age") or pat_info.get("age", "Unknown"),
            "Patient Gender": p_demo.get("gender") or pat_info.get("gender", "Unknown"),
            "Patient Weight (Standard)": p_demo.get("weight") or pat_info.get("weight", "Unknown"),
            "Patient Weight (PV value)": p_demo.get("patient_weight") or pat_details.get("patient_weight", "Unknown"),
            "Patient Age Group Code": age_group_dict.get("code", ""),
            "Patient Age Group Meaning": age_group_dict.get("meaning", ""),
            "Suspected Drug": drug_info.get("drug_name", "Unknown"),
            "Active Ingredient": drug_details.get("product_active_ingredient", "Unknown"),
            "Drug Role Code": drug_role_dict.get("code", ""),
            "Drug Role Meaning": drug_role_dict.get("meaning", ""),
            "Dosage": drug_info.get("dosage", "Unknown"),
            "Route": drug_info.get("route", "Unknown"),
            "Therapy Start Date": drug_info.get("therapy_start_date", "Unknown"),
            "Therapy End Date": drug_info.get("therapy_end_date", "Unknown"),
            "Indication": drug_info.get("indication", "Unknown"),
            "Adverse Event": event_info.get("adverse_event", "Unknown"),
            "Event Onset Date": event_info.get("event_start_date", "Unknown"),
            "Adverse Event Date (PV)": events_details.get("event_date", ""),
            "Drug Recur Action (PV)": events_details.get("drug_recur_action", ""),
            "Lot Number": batch_details.get("lot_number", ""),
            "Batch Number": batch_details.get("batch_number", ""),
            "Expiry Date": batch_details.get("expiry_date", ""),
            "Manufacturer": batch_details.get("manufacturer", ""),
            "Dose Form": therapy_details.get("dose_form", ""),
            "Dose Amount": therapy_details.get("dose_amount", ""),
            "Dose Unit": therapy_details.get("dose_unit", ""),
            "Dose Frequency": therapy_details.get("dose_frequency", ""),
            "Therapy Duration": therapy_details.get("therapy_duration", ""),
            "Reporter Occupation Code": reporter_occ_dict.get("code", ""),
            "Reporter Occupation Meaning": reporter_occ_dict.get("meaning", ""),
            "Outcome": event_info.get("outcome", "Unknown"),
            "Severity": event_info.get("severity", "Unknown"),
            "Action Taken": event_info.get("action_taken", "Unknown"),
            "AI Narrative Summary": data.get("ai_generated_narrative_summary") or data.get("summary") or "",
            "Suspected Relationship": causality.get("suspected_relationship", "Unknown"),
            "Causality Confidence Score": causality.get("confidence_score", 0.0),
            "Key Drug Extracted": entities.get("drug", "Unknown"),
            "Key Reaction Extracted": entities.get("reaction", "Unknown"),
            "Key Symptom Extracted": entities.get("symptom", "Unknown"),
            "Key Outcome Extracted": entities.get("outcome", "Unknown"),
            "AI Safety Insights": "; ".join(data.get("ai_safety_insights", [])),
            "Highlighted Fields": "; ".join(data.get("highlighted_critical_fields", [])),
            "Final Classification": data.get("final_case_classification", "Unknown")
        }

    def generate_excel_report(self, data: dict, report_id: str) -> str:
        filepath = os.path.join(REPORTS_DIR, f"{report_id}.xlsx")
        
        # Check if it is a parent multi-case record
        if "cases" in data and isinstance(data["cases"], list):
            rows = []
            for child_case in data["cases"]:
                child_id = child_case.get("analysis_id")
                if not child_id:
                    report_file_url = child_case.get("report_file", "")
                    if "/" in report_file_url:
                        child_id = report_file_url.split("/")[-1].split("?")[0]
                    else:
                        child_id = ""
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
        
        case_info = data.get("case_information") or {}
        pat_info = data.get("patient_information") or {}
        drug_info = data.get("suspected_drug_information") or {}
        event_info = data.get("adverse_event_details") or {}
        seriousness_ass = data.get("seriousness_assessment") or {}
        causality = data.get("causality_assessment") or {}
        entities = data.get("key_entities_extracted") or {}
        insights = data.get("ai_safety_insights") or []
        timeline = data.get("timeline") or []
        missing = data.get("missing_information") or []
        fda_sig = data.get("fda_signal") or {}
        reg_alerts = data.get("regulatory_alerts") or []
        
        # New structured PV details
        pat_details = data.get("patient_details") or {}
        p_demo = data.get("patient_demographic") or {}
        drug_details = data.get("drug_information") or {}
        events_details = data.get("adverse_events") or {}
        batch_details = data.get("drug_batch_details") or {}
        therapy_details = data.get("therapy_information") or {}
        reporter_details = data.get("reporter_information") or {}
        highlights = data.get("highlighted_critical_fields") or []
        med_insights = data.get("medical_insights") or []
        safety_obs = data.get("safety_observations") or []
        
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
        age_group_dict = p_demo.get("age_group") if isinstance(p_demo.get("age_group"), dict) else pat_details.get("age_group") or {}
        content.append(f"Age Group:      {age_group_dict.get('code', 'N/A')} - {age_group_dict.get('meaning', 'Unknown')}")
        content.append(f"Patient Weight: {p_demo.get('patient_weight') or pat_details.get('patient_weight', 'Unknown')} kg")
        content.append(f"Active Ingredient: {drug_details.get('product_active_ingredient', 'Unknown')}")
        content.append(f"Drug Role:      {drug_details.get('drug_role', {}).get('code', 'N/A')} - {drug_details.get('drug_role', {}).get('meaning', 'Unknown')}")
        content.append(f"Event Date:     {events_details.get('event_date', 'Unknown')}")
        content.append(f"Drug Recur Action: {events_details.get('drug_recur_action', 'None')}")
        content.append(f"Lot Number:     {batch_details.get('lot_number', 'Unknown')}")
        content.append(f"Batch Number:   {batch_details.get('batch_number', 'Unknown')}")
        content.append(f"Dose Form:      {therapy_details.get('dose_form', 'Unknown')}")
        content.append(f"Reporter Occp:  {reporter_details.get('occupation', {}).get('code', 'N/A')} - {reporter_details.get('occupation', {}).get('meaning', 'Unknown')}")
        content.append("")
        
        content.append("--- SUSPECTED DRUG INFORMATION ---")
        content.append(f"Drug Name:      {drug_info.get('drug_name', 'Unknown')}")
        content.append(f"Dosage:         {drug_info.get('dosage', 'Unknown')}")
        content.append(f"Route:          {drug_info.get('route', 'Unknown')}")
        content.append(f"Therapy Start:  {drug_info.get('therapy_start_date', 'Unknown')}")
        content.append(f"Therapy End:    {drug_info.get('therapy_end_date', 'Unknown')}")
        content.append(f"Indication:     {drug_info.get('indication', 'Unknown')}")
        content.append("")
        
        content.append("--- ADVERSE EVENT DETAILS ---")
        content.append(f"Adverse Event:  {event_info.get('adverse_event', 'Unknown')}")
        content.append(f"Event Start:    {event_info.get('event_start_date', 'Unknown')}")
        content.append(f"Outcome:        {event_info.get('outcome', 'Unknown')}")
        content.append(f"Severity:       {event_info.get('severity', 'Unknown')}")
        content.append(f"Action Taken:   {event_info.get('action_taken', 'Unknown')}")
        content.append("")
        
        if highlights:
            content.append("--- DETECTED HIGHLIGHTED SAFETY FIELDS ---")
            for h in highlights:
                content.append(f"- {h}")
            content.append("")
            
        content.append("--- AI-GENERATED NARRATIVE SUMMARY ---")
        content.append(data.get("ai_generated_narrative_summary") or data.get("ai_generated_summary", "Unknown"))
        content.append("")
        
        content.append("--- SERIOUSNESS ASSESSMENT ---")
        for k, v in seriousness_ass.items():
            content.append(f"{k.replace('_', ' ').title()}: {v}")
        content.append("")
        
        content.append("--- CAUSALITY ASSESSMENT (AI-ASSISTED) ---")
        content.append(f"Suspected Relationship:  {causality.get('suspected_relationship', 'Unknown')}")
        content.append(f"Confidence Score:        {causality.get('confidence_score', 0.0)}")
        content.append("")
        
        content.append("--- KEY ENTITIES EXTRACTED ---")
        for k, v in entities.items():
            content.append(f"{k.title()}: {v}")
        content.append("")
        
        if reg_alerts:
            content.append("--- REGULATORY ALERTS (BANNED/RESTRICTED DRUGS) ---")
            for alert in reg_alerts:
                if isinstance(alert, dict):
                    drug = alert.get('drug_name') or alert.get('drug') or "Unknown"
                    reason = alert.get('ban_reason') or alert.get('reason') or "Banned/Restricted"
                    country = alert.get('ban_country') or alert.get('source') or alert.get('country') or "Global"
                    content.append(f"- Drug: {drug} | Reason: {reason} | Country: {country}")
                else:
                    content.append(f"- {alert}")
            content.append("")
            
        if fda_sig:
            content.append("--- FDA SIGNAL SUMMARY ---")
            content.append(f"Total FAERS Cases:     {fda_sig.get('total_cases', 0)}")
            content.append(f"Serious Case Count:     {fda_sig.get('serious_cases', 0)}")
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
