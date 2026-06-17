import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.pdf_generator import PDFReportGenerator

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")
json_files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".json")]

if not json_files:
    print("No JSON reports found.")
    sys.exit(0)

test_file = json_files[-1]
report_id = test_file.replace(".json", "")
json_path = os.path.join(REPORTS_DIR, test_file)

with open(json_path, 'r') as f:
    data = json.load(f)

pdf_path = os.path.join(REPORTS_DIR, f"{report_id}_test.pdf")
print(f"Generating PDF for {report_id} at {pdf_path}")

generator = PDFReportGenerator(pdf_path, data, report_id)
generator.build()

print("PDF generated successfully!")
