import docx
import logging

logger = logging.getLogger(__name__)

def extract_docx_text(file_path: str) -> str:
    """
    Extracts text from a DOCX file using python-docx.
    """
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        logger.error(f"Error extracting DOCX at {file_path}: {e}")
        raise e
    return text
