import os
import sys
import pypdf

pdf_path = "/Users/affu01/GRAD_PROJ_NEW/Sample_PV_Inputs2/12_fax_multi_patient_ward_round_3cases.pdf"
reader = pypdf.PdfReader(pdf_path)
page = reader.pages[0]
image = page.images[0]

output_dir = "/Users/affu01/GRAD_PROJ_NEW/backend/app/uploads"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "12_fax_multi_patient_ward_round_3cases.png")

with open(output_path, "wb") as f:
    f.write(image.data)

print(f"Extracted image saved to: {output_path}")
print(f"Size: {len(image.data)} bytes")
