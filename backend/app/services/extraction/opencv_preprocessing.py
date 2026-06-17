import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

def remove_shadows(gray_img: np.ndarray) -> np.ndarray:
    """
    Removes uneven illumination and shadows from mobile camera images.
    Divides the image by a heavily blurred version of itself (background model).
    """
    try:
        # Create a background model using a large Gaussian blur kernel
        # Kernel size must be odd and large enough to smooth out text
        bg = cv2.GaussianBlur(gray_img, (101, 101), 0)
        # Divide the original image by the background to normalize illumination
        normalized = cv2.divide(gray_img, bg, scale=255)
        return normalized
    except Exception as e:
        logger.warning(f"Failed to remove shadows: {e}")
        return gray_img

def deskew_image(gray_img: np.ndarray) -> np.ndarray:
    """
    Detects skew angle in text alignment and rotates the image to align it horizontally.
    """
    try:
        # Threshold the image to get text pixels as foreground (binary invert)
        _, thresh = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Grab all (x, y) coordinates of text pixels
        pts = np.column_stack(np.where(thresh > 0))
        
        # Find minimum area bounding box around all text pixels
        rect = cv2.minAreaRect(pts)
        angle = rect[-1]
        
        # Normalize the angle to get correct rotation
        # minAreaRect returns angle in range [-90, 0]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        # Rotate if the angle is significant but reasonable (skewed document, not rotated sideways)
        if 0.5 < abs(angle) < 45:
            logger.info(f"Deskewing image: detected skew angle of {angle:.2f} degrees.")
            h, w = gray_img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(gray_img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated
            
        return gray_img
    except Exception as e:
        logger.warning(f"Failed to deskew image: {e}")
        return gray_img

def preprocess_image(image_bytes: bytes) -> bytes:
    """
    Performs advanced image enhancement to prepare document images for OCR:
    1. Grayscale conversion
    2. illumination normalization (shadow removal)
    3. Rotation alignment (deskewing)
    4. Contrast Limited Adaptive Histogram Equalization (CLAHE)
    5. Laplacian edge-sharpening
    6. Adaptive Gaussian thresholding (binarization)
    
    :param image_bytes: Raw input image bytes
    :return: Enhanced binarized image bytes in PNG format
    """
    try:
        # 1. Decode bytes to color image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Failed to decode image bytes using OpenCV.")
            
        # 2. Convert to Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 3. Denoising to remove initial camera/scanner noise
        denoised = cv2.fastNlMeansDenoising(gray, None, h=5, templateWindowSize=7, searchWindowSize=21)
        
        # 4. Shadow removal / mobile photo cleanup
        clean_bg = remove_shadows(denoised)
        
        # 5. Perspective correction / deskewing
        aligned = deskew_image(clean_bg)
        
        # 6. Enhance Contrast locally using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(aligned)
        
        # 7. Apply edge-sharpening to clarify letters
        kernel = np.array([
            [ 0, -1,  0],
            [-1,  5, -1],
            [ 0, -1,  0]
        ], dtype=np.float32)
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        # 8. Adaptive Thresholding for crisp binarization (clean black on white)
        binarized = cv2.adaptiveThreshold(
            sharpened, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            15, 
            10
        )
        
        # 9. Encode back to PNG bytes
        success, encoded_img = cv2.imencode('.png', binarized)
        if not success:
            raise RuntimeError("Failed to encode preprocessed image back to PNG format.")
            
        return encoded_img.tobytes()
        
    except Exception as e:
        logger.error(f"Error during advanced OpenCV preprocessing: {e}. Returning raw bytes as fallback.")
        return image_bytes
