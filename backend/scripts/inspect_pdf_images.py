import os
import sys
import pypdf

pdf_path = "/Users/affu01/GRAD_PROJ_NEW/Sample_PV_Inputs2/12_fax_multi_patient_ward_round_3cases.pdf"
reader = pypdf.PdfReader(pdf_path)
print(f"Pages: {len(reader.pages)}")
page = reader.pages[0]
print(f"Images on page 0: {len(page.images)}")
for idx, image_file_object in enumerate(page.images):
    print(f"Image {idx}: {image_file_object.name}, size: {len(image_file_object.data)} bytes")
