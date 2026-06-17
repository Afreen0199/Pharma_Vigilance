import os
import pypdf
import pandas as pd
import logging

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

class PreprocessingService:
    def convert_pdf_to_csv(self, pdf_path: str, csv_path: str, source: str):
        """Simplistic implementation to parse PDF and extract data to CSV."""
        if not os.path.exists(pdf_path):
            logger.warning(f"PDF not found for preprocessing: {pdf_path}")
            return
        
        try:
            data = []
            with open(pdf_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        for line in text.split('\n'):
                            if len(line.strip()) > 3:
                                data.append({
                                    "drug_name": line[:50].strip(), # simplistic parsing
                                    "ban_reason": "Extracted from PDF",
                                    "ban_country": "Global" if source == "UN" else "India",
                                    "regulatory_source": source
                                })
            
            df = pd.DataFrame(data)
            df.to_csv(csv_path, index=False)
            logger.info(f"Successfully converted {pdf_path} to {csv_path}")
        except Exception as e:
            logger.error(f"Error converting {pdf_path} to CSV: {e}")

preprocessing_service_instance = PreprocessingService()
