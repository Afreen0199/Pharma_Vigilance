import json
import pandas as pd
# from fpdf import FPDF  # Uncomment if fpdf is added to requirements
import os

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

class ReportService:
    def generate_json_report(self, data: dict, report_id: str) -> str:
        filepath = os.path.join(REPORTS_DIR, f"{report_id}.json")
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        return filepath

    def generate_excel_report(self, data: dict, report_id: str) -> str:
        filepath = os.path.join(REPORTS_DIR, f"{report_id}.xlsx")
        
        flattened = {
            "Summary": [data.get("summary", "")],
            "Drugs": [", ".join(data.get("drug_entities", []))],
            "Symptoms": [", ".join(data.get("symptoms", []))]
        }
        
        df = pd.DataFrame(flattened)
        df.to_excel(filepath, index=False)
        return filepath

    def generate_pdf_report(self, data: dict, report_id: str) -> str:
        filepath = os.path.join(REPORTS_DIR, f"{report_id}.pdf")
        
        # Simplified Mock PDF generation until fpdf is installed
        with open(filepath, 'w') as f:
            f.write(f"AI Pharmacovigilance Report\n\nReport ID: {report_id}\n\nSummary:\n{data.get('summary', '')}")
            
        return filepath

report_service_instance = ReportService()
