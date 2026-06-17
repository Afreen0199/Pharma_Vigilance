import os
import logging
import pypdf
from typing import List, Dict, Any

from app.services.extraction.pdf_extractor import extract_pdf_text
from app.services.extraction.docx_extractor import extract_docx_text
from app.services.extraction.text_extractor import extract_text_file
from app.services.extraction.ocr_service import ocr_service_instance
from app.services.extraction.ocr_cleaner import clean_ocr_text

from app.services.segmentation.visual_section_detector import detect_visual_sections
from app.services.segmentation.patient_boundary_detector import find_patient_boundaries
from app.services.segmentation.multi_case_parser import parse_segmented_case
from app.services.segmentation.case_normalizer import normalize_case_data

logger = logging.getLogger(__name__)

def segment_document(file_path: str, filename: str) -> List[Dict[str, Any]]:
    """
    Main orchestration function for Multi-Patient document segmentation.
    1. Detects file type.
    2. Runs visual slicing (OpenCV) for scanned/image documents.
    3. Runs text splitting (regex/heuristics) for digital documents.
    4. Parses and normalizes each case independently.
    5. Returns a list of structured case dictionaries.
    """
    logger.info(f"Starting Multi-Patient segmentation on: {filename} ({file_path})")
    
    ext = os.path.splitext(filename)[1].lower()
    
    # 1. Scanned Image / Image-based upload
    if ext in ['.png', '.jpg', '.jpeg']:
        with open(file_path, "rb") as f:
            image_bytes = f.read()
            
        # Try visual segmentation
        slices = detect_visual_sections(image_bytes)
        if len(slices) > 1:
            logger.info(f"Visual Section Detector: Segmented scanned image into {len(slices)} slices.")
            cases = []
            for idx, slice_bytes in enumerate(slices):
                try:
                    # Run OCR on this crop slice
                    raw_text, confidence = ocr_service_instance.extract_text(slice_bytes)
                    cleaned_text = clean_ocr_text(raw_text)
                    
                    # Parse and normalize
                    parsed = parse_segmented_case(cleaned_text)
                    normalized = normalize_case_data(parsed)
                    
                    cases.append({
                        "patient_index": idx + 1,
                        "text": cleaned_text,
                        "normalized": normalized,
                        "ocr_metadata": {
                            "source_type": "image_slice",
                            "ocr_used": True,
                            "ocr_confidence": confidence
                        }
                    })
                except Exception as slice_err:
                    logger.error(f"Failed to process crop slice {idx+1}: {slice_err}")
            if cases:
                return cases
                
        # If visual segmentation yielded nothing, fall back to full OCR and text boundaries
        logger.info("Visual Section Detector: No visual slices. Falling back to full OCR and text boundaries.")
        from app.services.extraction.image_extractor import extract_image_text
        text, img_meta = extract_image_text(file_path)
        return segment_text_cases(text, img_meta)

    # 2. PDF upload (could be digital or scanned)
    elif ext == '.pdf':
        # Check if it has embedded images representing scanned pages
        try:
            reader = pypdf.PdfReader(file_path)
            if len(reader.pages) == 1:
                page = reader.pages[0]
                if len(page.images) == 1:
                    logger.info("PDF: Scanned single-image PDF detected. Attempting visual image segmentation.")
                    image_bytes = page.images[0].data
                    slices = detect_visual_sections(image_bytes)
                    if len(slices) > 1:
                        logger.info(f"PDF Visual segmentation: Split PDF page into {len(slices)} crops.")
                        cases = []
                        for idx, slice_bytes in enumerate(slices):
                            raw_text, confidence = ocr_service_instance.extract_text(slice_bytes)
                            cleaned_text = clean_ocr_text(raw_text)
                            parsed = parse_segmented_case(cleaned_text)
                            normalized = normalize_case_data(parsed)
                            cases.append({
                                "patient_index": idx + 1,
                                "text": cleaned_text,
                                "normalized": normalized,
                                "ocr_metadata": {
                                    "source_type": "scanned_pdf_slice",
                                    "ocr_used": True,
                                    "ocr_confidence": confidence
                                }
                            })
                        if cases:
                            return cases
        except Exception as pdf_img_err:
            logger.warning(f"Failed to extract and segment PDF images: {pdf_img_err}. Falling back to text extractor.")
            
        # Use digital PDF text extractor
        text = extract_pdf_text(file_path)
        ocr_meta = {
            "source_type": "pdf",
            "ocr_used": False,
            "blur_score": 0.0,
            "ocr_confidence": 1.0
        }
        return segment_text_cases(text, ocr_meta)
        
    # 3. Word Document (.docx)
    elif ext == '.docx':
        text = extract_docx_text(file_path)
        ocr_meta = {
            "source_type": "pdf",
            "ocr_used": False,
            "blur_score": 0.0,
            "ocr_confidence": 1.0
        }
        return segment_text_cases(text, ocr_meta)
        
    # 4. Plain Text (.txt)
    elif ext == '.txt':
        text = extract_text_file(file_path)
        ocr_meta = {
            "source_type": "pdf",
            "ocr_used": False,
            "blur_score": 0.0,
            "ocr_confidence": 1.0
        }
        return segment_text_cases(text, ocr_meta)
        
    else:
        raise ValueError(f"Unsupported document file extension: {ext}")

def segment_text_cases(full_text: str, ocr_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Splits document text narrative into distinct cases based on patient boundary detection.
    """
    boundaries = find_patient_boundaries(full_text)
    
    # If no boundaries or only 1 boundary, treat as a single patient case
    if len(boundaries) <= 1:
        logger.info("Case Segmentation: Single case narrative detected.")
        parsed = parse_segmented_case(full_text)
        normalized = normalize_case_data(parsed)
        return [{
            "patient_index": 1,
            "text": full_text,
            "normalized": normalized,
            "ocr_metadata": ocr_meta
        }]
        
    # Split text into segments
    logger.info(f"Case Segmentation: Segmented document into {len(boundaries)} text regions.")
    cases = []
    for idx, b in enumerate(boundaries):
        case_text = full_text[b["start"]:b["end"]].strip()
        parsed = parse_segmented_case(case_text)
        normalized = normalize_case_data(parsed)
        
        # Override patient index from boundary if specified
        p_idx = b.get("patient_index") or (idx + 1)
        
        cases.append({
            "patient_index": p_idx,
            "text": case_text,
            "normalized": normalized,
            "ocr_metadata": ocr_meta
        })
        
    return cases
