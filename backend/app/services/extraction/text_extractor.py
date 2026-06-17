import logging

logger = logging.getLogger(__name__)

def extract_text_file(file_path: str) -> str:
    """
    Extracts text from a plain text file (.txt).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading plain text file at {file_path}: {e}")
        raise e
