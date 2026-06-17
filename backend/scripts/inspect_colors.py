import cv2
import numpy as np
import os

image_path = "/Users/affu01/GRAD_PROJ_NEW/backend/app/uploads/12_fax_multi_patient_ward_round_3cases.png"
if not os.path.exists(image_path):
    print("Image not found!")
    exit(1)

img = cv2.imread(image_path)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
h_img, w_img = img.shape[:2]
print(f"Loaded image size: {w_img}x{h_img}")

# Color ranges in HSV:
# Note: blue, green, purple sections
colors = {
    "blue": {
        "lower": np.array([90, 50, 50]),
        "upper": np.array([130, 255, 255])
    },
    "green": {
        "lower": np.array([35, 40, 40]),
        "upper": np.array([85, 255, 255])
    },
    "purple": {
        "lower": np.array([125, 30, 40]),
        "upper": np.array([170, 255, 255])
    }
}

for color_name, range_vals in colors.items():
    mask = cv2.inRange(hsv, range_vals["lower"], range_vals["upper"])
    # Clean noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    mask_cleaned = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask_cleaned = cv2.morphologyEx(mask_cleaned, cv2.MORPH_OPEN, kernel)
    
    contours, _ = cv2.findContours(mask_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"\nColor: {color_name} | Mask pixel count: {np.sum(mask > 0)}")
    for idx, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area > 1000:
            x, y, w, h = cv2.boundingRect(cnt)
            print(f"  Contour {idx}: Area={area:.1f}, Bounding Box: x={x}, y={y}, w={w}, h={h}")
