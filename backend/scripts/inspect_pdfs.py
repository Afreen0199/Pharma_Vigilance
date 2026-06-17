import os
import sys
import pypdf

# Add backend directory to path
sys.path.append("/Users/affu01/GRAD_PROJ_NEW/backend")

pdfs = [
    "/Users/affu01/GRAD_PROJ_NEW/Sample_PV_Inputs2/12_fax_multi_patient_ward_round_3cases.pdf",
    "/Users/affu01/GRAD_PROJ_NEW/Sample_PV_Inputs2/17_adr_register_4patients_multi_case.pdf",
    "/Users/affu01/GRAD_PROJ_NEW/Sample_PV_Inputs2/18_clinical_trial_safety_log_2subjects_apratixaban.pdf"
]

for pdf in pdfs:
    print("=" * 80)
    print(f"FILE: {os.path.basename(pdf)}")
    print("=" * 80)
    try:
        reader = pypdf.PdfReader(pdf)
        print(f"Number of pages: {len(reader.pages)}")
        for idx, page in enumerate(reader.pages):
            print(f"--- PAGE {idx+1} ---")
            print(page.extract_text())
    except Exception as e:
        print(f"Error reading {pdf}: {e}")
    print("\n")
