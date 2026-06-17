import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

def detect_blur(image_bytes: bytes, threshold: float = 100.0) -> dict:
    """
    Detects if an image is blurry using the Variance of Laplacian method.
    
    :param image_bytes: Raw bytes of the uploaded image
    :param threshold: The Laplacian variance threshold below which an image is considered blurry
    :return: dict containing:
             - blur_score: float (normalized score from 0.0 to 1.0, where 1.0 is sharp)
             - is_blurry: bool
             - raw_variance: float
             - warning: str or None
    """
    try:
        # Decode image from bytes
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            raise ValueError("Failed to decode image bytes using OpenCV.")
            
        # Calculate Laplacian variance
        variance = cv2.Laplacian(img, cv2.CV_64F).var()
        
        # Normalize score (cap at 300.0 for 1.0 index)
        blur_score = float(min(variance / 300.0, 1.0))
        is_blurry = variance < threshold
        
        warning = None
        if is_blurry:
            warning = f"Image may be too blurry for accurate OCR extraction (variance: {variance:.2f}, threshold: {threshold:.1f})."
            logger.warning(warning)
            
        return {
            "blur_score": round(blur_score, 4),
            "is_blurry": is_blurry,
            "raw_variance": round(variance, 4),
            "warning": warning
        }
    except Exception as e:
        logger.error(f"Error in blur detection: {e}")
        # Return fallback values to prevent pipeline failure
        return {
            "blur_score": 1.0,
            "is_blurry": False,
            "raw_variance": 0.0,
            "warning": f"Blur detection failed: {e}"
        }
