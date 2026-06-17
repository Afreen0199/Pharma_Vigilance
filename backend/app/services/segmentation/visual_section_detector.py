import cv2
import numpy as np
import logging
from typing import List

logger = logging.getLogger(__name__)

def detect_visual_sections(image_bytes: bytes) -> List[bytes]:
    """
    Analyzes scanned document page images using OpenCV to identify color-coded horizontal section divider bars.
    Crops the page image vertically at these bar boundaries and returns a list of crop-image bytes.
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            logger.error("Failed to decode image bytes using OpenCV.")
            return []
            
        h_img, w_img = img.shape[:2]
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Color ranges in HSV for blue, green, and purple header divider bars
        color_ranges = [
            # Blue
            (np.array([90, 50, 50]), np.array([130, 255, 255])),
            # Green
            (np.array([35, 40, 40]), np.array([85, 255, 255])),
            # Purple
            (np.array([125, 30, 40]), np.array([170, 255, 255]))
        ]
        
        y_coords = []
        
        for lower, upper in color_ranges:
            mask = cv2.inRange(hsv, lower, upper)
            
            # Clean noise with morphological open/close
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
            mask_cleaned = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask_cleaned = cv2.morphologyEx(mask_cleaned, cv2.MORPH_OPEN, kernel)
            
            contours, _ = cv2.findContours(mask_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                # Filter out small noise
                if area > 1000:
                    x, y, w, h = cv2.boundingRect(cnt)
                    # Check if it spans at least 40% of the image width to count as a horizontal separator bar
                    if w > w_img * 0.4:
                        y_coords.append(y)
                        logger.info(f"Visual Section Detector: Detected separator bar at y={y}, w={w}, h={h}")
                        
        # Sort and deduplicate y coordinates that are very close (within 30 pixels)
        y_coords = sorted(list(set(y_coords)))
        filtered_y = []
        for y in y_coords:
            if not filtered_y or y - filtered_y[-1] > 30:
                filtered_y.append(y)
                
        logger.info(f"Visual Section Detector: Found boundary y-coordinates: {filtered_y}")
        
        # If we didn't find multiple divider bars, we cannot segment visually
        if len(filtered_y) <= 1:
            logger.info("Visual Section Detector: Less than 2 boundary divider bars found. Visual segmentation not applicable.")
            return []
            
        # Slice:
        # - Slice 1: from y_1 to y_2
        # - Slice 2: from y_2 to y_3
        # ...
        # - Slice m: from y_m to h_img
        
        slices = []
        for i in range(len(filtered_y)):
            y_start = filtered_y[i]
            y_end = filtered_y[i+1] if i + 1 < len(filtered_y) else h_img
            
            # Crop the image slice
            crop = img[y_start:y_end, :]
            
            # Encode back to PNG bytes
            success, encoded_crop = cv2.imencode('.png', crop)
            if success:
                slices.append(encoded_crop.tobytes())
                logger.info(f"Visual Section Detector: Created vertical slice {i+1} from y={y_start} to y={y_end}")
                
        return slices
    except Exception as e:
        logger.error(f"Error in visual section detector: {e}")
        return []
