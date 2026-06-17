from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import os
import shutil
import uuid
import json
import logging
from pydantic import BaseModel
from app.services.scispacy_service import scispacy_service_instance
from app.services.database_service import db_service
from app.milvus.vector_insert_service import insert_document
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["Analysis"])

class AnalyzeRequest(BaseModel):
    text: str
    document_id: Optional[str] = None

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def analyze_document(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
):
    """
    Universal Medical Ingestion and Case Analysis endpoint.
    Accepts EITHER an uploaded patient file (PDF/DOCX/TXT/Image), a raw text case narrative 
    form parameter, or both. It dynamically extracts text using dedicated file-type extractors,
    runs medical entity mapping, embeds and indexes the case in the 'input_documents' collection,
    stores the initial extracted case state and OCR metadata in Supabase, and returns a unique analysis_id.
    """
    if not file and not text:
        raise HTTPException(
            status_code=400, 
            detail="You must provide either an uploaded case file or a raw text case narrative."
        )

    source_filename = "raw_pasted_narrative"
    ocr_metadata = {
        "source_type": "pdf",
        "ocr_used": False,
        "blur_score": 0.0,
        "ocr_confidence": 1.0
    }

    cases_segmented = []

    # 1. Process uploaded case file if present
    if file and file.filename:
        source_filename = file.filename
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        try:
            # Cache the file to disk
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            from app.services.segmentation.case_segmentation_engine import segment_document
            cases_segmented = segment_document(file_path, file.filename)
            if cases_segmented:
                # Use the OCR metadata from the first slice/case
                ocr_metadata.update(cases_segmented[0].get("ocr_metadata", {}))
        except Exception as e:
            logger.error(f"Failed to segment file: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process case file: {e}")

    # 2. Process form-text narrative if present and not processed via file
    elif text:
        try:
            from app.services.segmentation.case_segmentation_engine import segment_text_cases
            cases_segmented = segment_text_cases(text, ocr_metadata)
        except Exception as e:
            logger.error(f"Failed to segment text narrative: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to segment text narrative: {e}")

    if not cases_segmented:
        raise HTTPException(
            status_code=400, 
            detail="No readable text narrative found in your upload or form inputs."
        )

    # Check if we have multiple cases or a single case
    if len(cases_segmented) == 1:
        # Single patient case - execute legacy flow
        single_case = cases_segmented[0]
        extracted_text = single_case["text"]
        ocr_metadata.update(single_case.get("ocr_metadata", {}))

        try:
            # 3. SciSpacy Medical Entity Extraction
            entities = scispacy_service_instance.extract_entities(extracted_text)
            drugs = entities.get("drugs", [])
            symptoms = entities.get("symptoms", [])
            conditions = entities.get("conditions", [])

            # 4. Validate drugs list to filter out noisy entities
            from app.services.drug_validator_service import drug_validator_service
            validated_drugs = drug_validator_service.validate_drugs(drugs)

            # 5. Generate unique analysis ID
            analysis_id = str(uuid.uuid4())

            # 6. Chunk, embed locally, and index the case report in 'input_documents' collection
            metadata = {
                "source": source_filename,
                "document_type": "patient_narrative_ingested",
                "primary_drugs": ", ".join(validated_drugs) if validated_drugs else "None"
            }
            # Add ocr metadata fields to Milvus dynamic payload
            metadata.update(ocr_metadata)

            insert_document(
                collection_name="input_documents",
                text=extracted_text,
                document_id=analysis_id,
                metadata=metadata
            )

            # 7. Save case state in Supabase
            db_service.save_case_analysis(
                analysis_id=analysis_id,
                filename=source_filename,
                extracted_text=extracted_text,
                drugs=validated_drugs,
                symptoms=symptoms,
                conditions=conditions,
                ocr_metadata=ocr_metadata
            )

            from app.routes.report import generate_report, ReportGenerateRequest
            return await generate_report(ReportGenerateRequest(analysis_id=analysis_id, force=True))
        except Exception as e:
            logger.error(f"Error during universal analyze: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Multi-patient document flow
        parent_analysis_id = str(uuid.uuid4())
        child_details = []
        child_ids = []

        try:
            for idx, case_data in enumerate(cases_segmented):
                child_id = str(uuid.uuid4())
                child_text = case_data["text"]
                child_ocr_meta = case_data.get("ocr_metadata", ocr_metadata).copy()

                child_ocr_meta["parent_document_id"] = parent_analysis_id
                child_ocr_meta["patient_index"] = case_data["patient_index"]
                child_ocr_meta["case_id"] = f"PV-2026-000{case_data['patient_index']}"

                # SciSpacy on child segment
                entities = scispacy_service_instance.extract_entities(child_text)
                drugs = entities.get("drugs", [])
                symptoms = entities.get("symptoms", [])
                conditions = entities.get("conditions", [])

                from app.services.drug_validator_service import drug_validator_service
                validated_drugs = drug_validator_service.validate_drugs(drugs)

                # Index child case in Milvus
                metadata = {
                    "source": source_filename,
                    "document_type": "multi_case_patient_segment",
                    "primary_drugs": ", ".join(validated_drugs) if validated_drugs else "None"
                }
                metadata.update(child_ocr_meta)

                insert_document(
                    collection_name="input_documents",
                    text=child_text,
                    document_id=child_id,
                    metadata=metadata
                )

                # Save child case state in Supabase
                db_service.save_case_analysis(
                    analysis_id=child_id,
                    filename=f"Patient_{case_data['patient_index']}_{source_filename}",
                    extracted_text=child_text,
                    drugs=validated_drugs,
                    symptoms=symptoms,
                    conditions=conditions,
                    ocr_metadata=child_ocr_meta
                )

                child_ids.append(child_id)
                child_details.append({
                    "case_id": child_ocr_meta["case_id"],
                    "analysis_id": child_id,
                    "patient_index": case_data["patient_index"],
                    "status": "analyzed",
                    "drug_entities": validated_drugs,
                    "symptoms": symptoms,
                    "conditions": conditions,
                    "text_preview": child_text[:300]
                })

            # Save parent record in Supabase
            parent_ocr_meta = ocr_metadata.copy()
            parent_ocr_meta["is_parent"] = True
            parent_ocr_meta["child_ids"] = child_ids
            parent_ocr_meta["total_cases"] = len(cases_segmented)

            db_service.save_case_analysis(
                analysis_id=parent_analysis_id,
                filename=source_filename,
                extracted_text=f"Multi-Patient Document containing {len(cases_segmented)} cases.",
                drugs=[],
                symptoms=[],
                conditions=[],
                ocr_metadata=parent_ocr_meta
            )

            from app.routes.report import generate_report, ReportGenerateRequest
            return await generate_report(ReportGenerateRequest(analysis_id=parent_analysis_id, force=True))
        except Exception as e:
            logger.error(f"Failed to process multi-case document: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/text")
async def analyze_document_text(request: AnalyzeRequest):
    """
    Text-based Case Analysis Ingestion endpoint.
    Accepts raw narrative text input, extracts SciSpacy entities, chunks/embeds 
    into 'input_documents', registers a pending analysis in Supabase, and returns analysis_id.
    """
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required for analysis.")

    text = request.text
    source_filename = request.document_id or "raw_text_input"
    ocr_metadata = {
        "source_type": "pdf",
        "ocr_used": False,
        "blur_score": 0.0,
        "ocr_confidence": 1.0
    }

    try:
        from app.services.segmentation.case_segmentation_engine import segment_text_cases
        cases_segmented = segment_text_cases(text, ocr_metadata)
    except Exception as e:
        logger.error(f"Failed to segment text: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to segment text: {e}")

    if not cases_segmented:
        raise HTTPException(status_code=400, detail="No readable text found.")

    if len(cases_segmented) == 1:
        single_case = cases_segmented[0]
        extracted_text = single_case["text"]
        ocr_metadata.update(single_case.get("ocr_metadata", {}))

        try:
            # 1. SciSpacy Medical Entity Extraction
            entities = scispacy_service_instance.extract_entities(extracted_text)
            drugs = entities.get("drugs", [])
            symptoms = entities.get("symptoms", [])
            conditions = entities.get("conditions", [])

            # 2. Validate drugs list
            from app.services.drug_validator_service import drug_validator_service
            validated_drugs = drug_validator_service.validate_drugs(drugs)

            # 3. Generate unique analysis ID
            analysis_id = str(uuid.uuid4())

            # 4. Chunk, embed, and store analyzed patient report into input_documents collection
            metadata = {
                "source": source_filename,
                "document_type": "analyzed_case_report",
                "primary_drugs": ", ".join(validated_drugs) if validated_drugs else "None"
            }
            metadata.update(ocr_metadata)

            insert_document(
                collection_name="input_documents",
                text=extracted_text,
                document_id=analysis_id,
                metadata=metadata
            )

            # 5. Save case state in Supabase
            db_service.save_case_analysis(
                analysis_id=analysis_id,
                filename=source_filename,
                extracted_text=extracted_text,
                drugs=validated_drugs,
                symptoms=symptoms,
                conditions=conditions,
                ocr_metadata=ocr_metadata
            )

            from app.routes.report import generate_report, ReportGenerateRequest
            return await generate_report(ReportGenerateRequest(analysis_id=analysis_id, force=True))
        except Exception as e:
            logger.error(f"Error during analyze text: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Multi-patient document flow
        parent_analysis_id = str(uuid.uuid4())
        child_details = []
        child_ids = []

        try:
            for idx, case_data in enumerate(cases_segmented):
                child_id = str(uuid.uuid4())
                child_text = case_data["text"]
                child_ocr_meta = case_data.get("ocr_metadata", ocr_metadata).copy()

                child_ocr_meta["parent_document_id"] = parent_analysis_id
                child_ocr_meta["patient_index"] = case_data["patient_index"]
                child_ocr_meta["case_id"] = f"PV-2026-000{case_data['patient_index']}"

                # SciSpacy on child segment
                entities = scispacy_service_instance.extract_entities(child_text)
                drugs = entities.get("drugs", [])
                symptoms = entities.get("symptoms", [])
                conditions = entities.get("conditions", [])

                from app.services.drug_validator_service import drug_validator_service
                validated_drugs = drug_validator_service.validate_drugs(drugs)

                # Index in Milvus
                metadata = {
                    "source": source_filename,
                    "document_type": "multi_case_patient_segment",
                    "primary_drugs": ", ".join(validated_drugs) if validated_drugs else "None"
                }
                metadata.update(child_ocr_meta)

                insert_document(
                    collection_name="input_documents",
                    text=child_text,
                    document_id=child_id,
                    metadata=metadata
                )

                # Save child state in Supabase
                db_service.save_case_analysis(
                    analysis_id=child_id,
                    filename=f"Patient_{case_data['patient_index']}_{source_filename}",
                    extracted_text=child_text,
                    drugs=validated_drugs,
                    symptoms=symptoms,
                    conditions=conditions,
                    ocr_metadata=child_ocr_meta
                )

                child_ids.append(child_id)
                child_details.append({
                    "case_id": child_ocr_meta["case_id"],
                    "analysis_id": child_id,
                    "patient_index": case_data["patient_index"],
                    "status": "analyzed",
                    "drug_entities": validated_drugs,
                    "symptoms": symptoms,
                    "conditions": conditions,
                    "text_preview": child_text[:300]
                })

            # Save parent record in Supabase
            parent_ocr_meta = ocr_metadata.copy()
            parent_ocr_meta["is_parent"] = True
            parent_ocr_meta["child_ids"] = child_ids
            parent_ocr_meta["total_cases"] = len(cases_segmented)

            db_service.save_case_analysis(
                analysis_id=parent_analysis_id,
                filename=source_filename,
                extracted_text=f"Multi-Patient Document containing {len(cases_segmented)} cases.",
                drugs=[],
                symptoms=[],
                conditions=[],
                ocr_metadata=parent_ocr_meta
            )

            from app.routes.report import generate_report, ReportGenerateRequest
            return await generate_report(ReportGenerateRequest(analysis_id=parent_analysis_id, force=True))
        except Exception as e:
            logger.error(f"Failed to process multi-case text: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_analyses():
    """
    GET /analyze/
    Returns all case analysis records from database.
    """
    try:
        data = db_service.get_all_case_analyses()
        return data
    except Exception as e:
        logger.error(f"Failed to list analyses: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve case history: {e}")
