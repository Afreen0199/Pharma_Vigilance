import pypdf
import logging

logger = logging.getLogger(__name__)

def extract_pdf_text(file_path: str) -> str:
    """
    Extracts text from a digital PDF file using pypdf.
    """
    text = ""
    try:
        with open(file_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        logger.error(f"Error extracting PDF at {file_path}: {e}")
        raise e
    return text
