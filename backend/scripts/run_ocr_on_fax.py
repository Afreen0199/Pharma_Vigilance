import os
import sys
from dotenv import load_dotenv

sys.path.append("/Users/affu01/GRAD_PROJ_NEW/backend")
load_dotenv("/Users/affu01/GRAD_PROJ_NEW/backend/.env")

from app.services.extraction.image_extractor import extract_image_text

image_path = "/Users/affu01/GRAD_PROJ_NEW/backend/app/uploads/12_fax_multi_patient_ward_round_3cases.png"
print(f"Running OCR on: {image_path}")
text, metadata = extract_image_text(image_path)

print("\n=== EXTRACTED TEXT ===")
print(text)
print("======================\n")

print("=== METADATA ===")
import json
print(json.dumps(metadata, indent=2))
print("================\n")
