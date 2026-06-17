import os
import logging
from typing import Tuple, Dict, Any, List
import cv2
import numpy as np
from app.services.extraction.blur_detection import detect_blur
from app.services.extraction.opencv_preprocessing import preprocess_image
from app.services.extraction.ocr_service import ocr_service_instance
from app.services.extraction.ocr_cleaner import clean_ocr_text

logger = logging.getLogger(__name__)

def detect_and_extract_highlights(img_color: np.ndarray) -> List[Tuple[bytes, str]]:
    """
    Detects yellow and purple highlights in an image using HSV masking.
    Returns a list of tuples containing (ROI image bytes, highlight color name).
    """
    # Convert image to HSV color space
    hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)
    
    # Yellow highlights mask
    lower_yellow = np.array([15, 60, 80])
    upper_yellow = np.array([38, 255, 255])
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # Purple/Magenta highlights mask
    lower_purple = np.array([120, 30, 40])
    upper_purple = np.array([170, 255, 255])
    mask_purple = cv2.inRange(hsv, lower_purple, upper_purple)
    
    # Combine masks to find all highlighted regions
    mask_combined = cv2.bitwise_or(mask_yellow, mask_purple)
    
    # Apply morphological operations to close gaps in highlights over text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 5))
    dilated_mask = cv2.dilate(mask_combined, kernel, iterations=1)
    
    # Find contours representing the highlighted zones
    contours, _ = cv2.findContours(dilated_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort contours by area descending
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    highlighted_rois = []
    h_img, w_img = img_color.shape[:2]
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # Filter out small noise artifacts
        if area < 150:
            continue
            
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Add padding around the ROI bounding box to improve text OCR readability
        pad = 8
        x_start = max(0, x - pad)
        y_start = max(0, y - pad)
        x_end = min(w_img, x + w + pad)
        y_end = min(h_img, y + h + pad)
        
        roi = img_color[y_start:y_end, x_start:x_end]
        
        # Determine highlight color type
        yellow_sum = np.sum(mask_yellow[y:y+h, x:x+w])
        purple_sum = np.sum(mask_purple[y:y+h, x:x+w])
        color_type = "yellow" if yellow_sum >= purple_sum else "purple"
        
        # Encode ROI to PNG bytes
        success, encoded_roi = cv2.imencode('.png', roi)
        if success:
            highlighted_rois.append((encoded_roi.tobytes(), color_type))
            
    return highlighted_rois

def extract_image_text(file_path: str, source_type: str = "image") -> Tuple[str, Dict[str, Any]]:
    """
    Orchestrates the multimodal image text extraction pipeline:
    1. Reads the raw image bytes from disk
    2. Runs Laplacian blur detection
    3. Runs OpenCV preprocessing (contrast enhancement, denoising, sharpening)
    4. Detects colored highlights (yellow, purple) and performs priority OCR on ROIs
    5. Submits enhanced full image bytes to AWS Textract for OCR
    6. Cleans and normalizes the OCR output text
    
    :param file_path: Path to the image file on disk
    :param source_type: The source category ("image", "scanned", or "handwritten")
    :return: Tuple containing:
             - Cleaned, normalized medical text string
             - OCR metadata dictionary
    """
    logger.info(f"Starting image text extraction pipeline for {file_path} (source_type: {source_type})...")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found at: {file_path}")
        
    try:
        # Read raw image bytes
        with open(file_path, "rb") as f:
            raw_bytes = f.read()
            
        # 1. Blur Detection
        blur_res = detect_blur(raw_bytes)
        logger.info(f"Blur detection results: {blur_res}")
        
        # 2. Extract Highlights (Priority OCR)
        highlighted_texts = []
        try:
            nparr = np.frombuffer(raw_bytes, np.uint8)
            img_color = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img_color is not None:
                rois = detect_and_extract_highlights(img_color)
                logger.info(f"Detected {len(rois)} highlighted region(s) in image.")
                
                # Perform OCR on each ROI separately
                for idx, (roi_bytes, color) in enumerate(rois[:6]):  # Limit to top 6 to prevent timeouts
                    try:
                        roi_text, _ = ocr_service_instance.extract_text(roi_bytes)
                        roi_text_cleaned = clean_ocr_text(roi_text)
                        if roi_text_cleaned:
                            highlighted_texts.append(f"[{color.upper()} HIGHLIGHT]: {roi_text_cleaned}")
                    except Exception as roi_err:
                        logger.warning(f"Failed to extract text from highlight zone {idx}: {roi_err}")
        except Exception as highlight_err:
            logger.error(f"Error executing color highlight detection: {highlight_err}")
            
        # 3. Image Enhancement
        logger.info("Applying OpenCV preprocessing/enhancements...")
        enhanced_bytes = preprocess_image(raw_bytes)
        
        # 4. AWS Textract OCR on full enhanced image
        logger.info("Sending preprocessed image to AWS Textract...")
        raw_text, confidence = ocr_service_instance.extract_text(enhanced_bytes)
        
        # 5. OCR Cleaning
        logger.info("Cleaning and normalizing OCR text...")
        cleaned_text = clean_ocr_text(raw_text)
        
        # Prepend highlighted text blocks to the output text so the LLM parses them with higher priority
        if highlighted_texts:
            logger.info("Prepending highlighted text blocks to output text.")
            header = "\n".join(highlighted_texts)
            cleaned_text = f"=== HIGHLIGHTED CLINICAL OBSERVATIONS ===\n{header}\n==========================================\n\n{cleaned_text}"
        
        # 6. Build metadata
        ocr_metadata = {
            "source_type": source_type,
            "ocr_used": True,
            "blur_score": blur_res["blur_score"],
            "ocr_confidence": confidence,
            "highlighted_critical_fields": highlighted_texts
        }
        
        # Add warning details to metadata if the image was blurry
        if blur_res["is_blurry"]:
            ocr_metadata["blur_warning"] = blur_res["warning"]
            
        logger.info("Image text extraction completed successfully.")
        return cleaned_text, ocr_metadata
        
    except Exception as e:
        logger.error(f"Image text extraction pipeline failed: {e}")
        raise e
