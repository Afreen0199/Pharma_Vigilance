

Modify the `/analyze` and `/analyze/text` endpoints in the backend to synchronously generate and complete reports. This eliminates the `"pending"` status step and returns the final completed report immediately, while maintaining full backward compatibility.

---

## User Review Required

> [!IMPORTANT]
> **Synchronous Processing Latency**: Since report generation queries openFDA, retrieves vector database chunks via Milvus, and executes Groq LLM clinical reasoning, the `/analyze/` request will block for 5-10 seconds per case. 
> 
> **Backward Compatibility**: The frontend still triggers a secondary `/report/generate` call in `UploadCasePage.jsx` during the simulated progress step. Because `/report/generate` returns the cached completed report instantly, this frontend flow will remain fully functional and compatible without needing immediate updates.

---

## Proposed Changes

### [MODIFY] [analyze.py](file:///Users/affu01/GRAD_PROJ_NEW/backend/app/routes/analyze.py)

We will modify the return statements in all ingestion handlers to import `generate_report` and `ReportGenerateRequest` locally, await report generation, and return the final output directly.

#### 1. Universal single-patient file upload endpoint return (around line 129)
Instead of returning a dictionary with `"status": "pending"`, we will execute:
```python
from app.routes.report import gene
return await generate_report(ReportGenerateRequest(analysis_id=analysis_id, force=True))
```

#### 2. Universal multi-patient document upload parent record return (around line 222)
Instead of returning a dictionary with `"status": "pending"`, we will execute:
```python
from app.routes.report import generate_report, ReportGenerateRequest
return await generate_report(ReportGenerateRequest(analysis_id=parent_analysis_id, force=True))
```

#### 3. Narrative text single-patient input endpoint return (around line 302)
Instead of returning a dictionary with `"status": "pending"`, we will execute:
```python
from app.routes.report import generate_report, ReportGenerateRequest
return await generate_report(ReportGenerateRequest(analysis_id=analysis_id, force=True))
```

#### 4. Narrative text multi-patient input parent record return (around line 389)
Instead of returning a dictionary with `"status": "pending"`, we will execute:
```python
from app.routes.report import generate_report, ReportGenerateRequest
return await generate_report(ReportGenerateRequest(analysis_id=parent_analysis_id, force=True))
```

---

## Verification Plan

### Automated Tests
* We can run the ingestion pipeline via the backend terminal test commands to ensure the `/analyze/` endpoint responds with the completed report dictionary.
* Check that `status` in the response is `"success"` and all clinical assessments (seriousness, causality) are fully populated.

### Manual Verification
* Upload a patient file or narrative text via the React frontend.
* Observe the dashboard ingestion progress bar. It should transition successfully through the simulated steps and navigate to the clinical workspace showing the fully generated report.

cases_segmented = segment_document(file_path, file.filename)
if cases_segmented:
# Use the OCR metadata from the first slice/case
ocr_metadata.update(cases_segmented[0].get("ocr_metadata", {}))
except Exception as e:
logger.error(f"Failed to segment file: {e}")
raise HTTPException(status_code=500, detail=f"Failed to process case file: {e}")

# 2. Process form-text narrative if present and not processed via file
elif text:
from app.services.segmentation.case_segmentation_engine import segment_text_cases
cases_segmented = segment_text_cases(text, ocr_metadata)

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

return {
"filename": source_filename,
"analysis_id": analysis_id,
"status": "pending",
"drug_entities": validated_drugs,
"symptoms": symptoms,
"conditions": conditions,
"text_preview": extracted_text[:500],
"ocr_metadata": ocr_metadata
}
except Exception as e:
raise HTTPException(status_code=500, detail=str(e))
else:
# Multi-patient document flow
parent_analysis_id = str(uuid.uuid4())
child_details = []
child_ids = []
)

child_details.append({
"case_id": case_id,
"analysis_id": case_id, # for backwards compatibility with tests
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

# Validate drugs list
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
"analysis_id": child_id,
"patient_index": case_data["patient_index"],
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

# Parent record status remains 'pending' until report generation compiles details.

return {
"filename": source_filename,
"analysis_id": parent_analysis_id,
"status": "pending",
"total_cases_detected": len(cases_segmented),
"cases": child_details
}
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
drugs = entities.get("drugs", [])
symptoms = entities.get("symptoms", [])
conditions = entities.get("conditions", [])

# 1. Validate drugs list
from app.services.drug_validator_service import drug_validator_service
validated_drugs = drug_validator_service.validate_drugs(drugs)

# 2. Generate unique analysis ID
analysis_id = str(uuid.uuid4())

# 3. Chunk, embed, and store analyzed patient report into input_documents collection
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

# 4. Save case state in Supabase
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
else:
# Multi-patient document flow
parent_analysis_id = str(uuid.uuid4())
child_details = []
child_ids = []

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
conditions = entities.get("conditions", [])

from app.services.drug_validator_service import drug_validator_service
validated_drugs = drug_validator_service.validate_drugs(drugs)

# Index in Milvus
metadata = {
"source": source_filename,
"document_type": "multi_case_patient_segment",
"primary_drugs": ", ".join(validated_drugs) if validated_drugs else "None"
"analysis_id": child_id,
"patient_index": case_data["patient_index"],
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

conditions=[],
ocr_metadata=parent_ocr_meta
)
# Parent record status remains 'pending' initially.

return {
"filename": source_filename,
"analysis_id": parent_analysis_id,
"status": "pending",
"total_cases_detected": len(cases_segmented),
"cases": child_details
}
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

regulatory_alerts=[],
fda_signals={}
)

return {
"filename": source_filename,
"analysis_id": parent_analysis_id,
"status": "pending",
"total_cases_detected": len(cases_segmented),
"cases": child_details
}
except Exception as e:
logger.error(f"Failed to process multi-case text: {e}")
raise HTTPException(status_code=500, detail=str(e))

# MISSING LINE 428
# MISSING LINE 429
# MISSING LINE 430
# MISSING LINE 431
# MISSING LINE 432
# MISSING LINE 433
# MISSING LINE 434
# MISSING LINE 435
# MISSING LINE 436
# MISSING LINE 437
# MISSING LINE 438
# MISSING LINE 439
# MISSING LINE 440
# MISSING LINE 441
# MISSING LINE 442
# MISSING LINE 443
# MISSING LINE 444
# MISSING LINE 445
# MISSING LINE 446
# MISSING LINE 447
# MISSING LINE 448
# MISSING LINE 449
# MISSING LINE 450
# MISSING LINE 451
# MISSING LINE 452
# MISSING LINE 453
# MISSING LINE 454
# MISSING LINE 455
# MISSING LINE 456
# MISSING LINE 457
# MISSING LINE 458
# MISSING LINE 459
# MISSING LINE 460
# MISSING LINE 461
# MISSING LINE 462
# MISSING LINE 463
# MISSING LINE 464
# MISSING LINE 465
# MISSING LINE 466
# MISSING LINE 467
# MISSING LINE 468
# MISSING LINE 469
# MISSING LINE 470
# MISSING LINE 471
# MISSING LINE 472
# MISSING LINE 473
# MISSING LINE 474
# MISSING LINE 475
# MISSING LINE 476
# MISSING LINE 477
# MISSING LINE 478
# MISSING LINE 479
# MISSING LINE 480
# MISSING LINE 481
# MISSING LINE 482
# MISSING LINE 483
# MISSING LINE 484
# MISSING LINE 485
# MISSING LINE 486
# MISSING LINE 487
# MISSING LINE 488
# MISSING LINE 489
# MISSING LINE 490
# MISSING LINE 491
# MISSING LINE 492
# MISSING LINE 493
# MISSING LINE 494
# MISSING LINE 495
# MISSING LINE 496
# MISSING LINE 497
# MISSING LINE 498
# MISSING LINE 499
# MISSING LINE 500
# MISSING LINE 501
# MISSING LINE 502
# MISSING LINE 503
# MISSING LINE 504
# MISSING LINE 505
# MISSING LINE 506
# MISSING LINE 507
# MISSING LINE 508
# MISSING LINE 509
# MISSING LINE 510
# MISSING LINE 511
# MISSING LINE 512
# MISSING LINE 513
# MISSING LINE 514
# MISSING LINE 515
# MISSING LINE 516
# MISSING LINE 517
# MISSING LINE 518
# MISSING LINE 519
# MISSING LINE 520
# MISSING LINE 521
# MISSING LINE 522
# MISSING LINE 523
# MISSING LINE 524
# MISSING LINE 525
# MISSING LINE 526
# MISSING LINE 527
# MISSING LINE 528
# MISSING LINE 529
# MISSING LINE 530
# MISSING LINE 531
# MISSING LINE 532
# MISSING LINE 533
# MISSING LINE 534
# MISSING LINE 535
# MISSING LINE 536
# MISSING LINE 537
# MISSING LINE 538
# MISSING LINE 539
# MISSING LINE 540
# MISSING LINE 541
# MISSING LINE 542
# MISSING LINE 543
# MISSING LINE 544
# MISSING LINE 545
# MISSING LINE 546
# MISSING LINE 547
# MISSING LINE 548
# MISSING LINE 549
# MISSING LINE 550
# MISSING LINE 551
# MISSING LINE 552
# MISSING LINE 553
# MISSING LINE 554
# MISSING LINE 555
# MISSING LINE 556
# MISSING LINE 557
# MISSING LINE 558
# MISSING LINE 559
# MISSING LINE 560
# MISSING LINE 561
# MISSING LINE 562
# MISSING LINE 563
# MISSING LINE 564
# MISSING LINE 565
# MISSING LINE 566
# MISSING LINE 567
# MISSING LINE 568
# MISSING LINE 569
# MISSING LINE 570
# MISSING LINE 571
# MISSING LINE 572
# MISSING LINE 573
# MISSING LINE 574
# MISSING LINE 575
# MISSING LINE 576
# MISSING LINE 577
# MISSING LINE 578
# MISSING LINE 579
# MISSING LINE 580
# MISSING LINE 581
# MISSING LINE 582
# MISSING LINE 583
# MISSING LINE 584
# MISSING LINE 585
# MISSING LINE 586
# MISSING LINE 587
# MISSING LINE 588
# MISSING LINE 589
# MISSING LINE 590
# MISSING LINE 591
# MISSING LINE 592
# MISSING LINE 593
# MISSING LINE 594
# MISSING LINE 595
# MISSING LINE 596
# MISSING LINE 597
# MISSING LINE 598
# MISSING LINE 599
# MISSING LINE 600
# MISSING LINE 601
# MISSING LINE 602
# MISSING LINE 603
# MISSING LINE 604
# MISSING LINE 605
# MISSING LINE 606
# MISSING LINE 607
# MISSING LINE 608
# MISSING LINE 609
# MISSING LINE 610
# MISSING LINE 611
# MISSING LINE 612
# MISSING LINE 613
# MISSING LINE 614
# MISSING LINE 615
# MISSING LINE 616
# MISSING LINE 617
# MISSING LINE 618
# MISSING LINE 619

### 4. Verification & E2E Validation
* Updated E2E tests (`scripts/test_chat_e2e.py`) to verify greetings and irrelevant questions:
- **Greetings Onboarding**: Querying `"Who are you?"` returned `general_conversational` classification, onboarding description, and minimal keys (`['summary']`).
- **Irrelevant Query Refusal**: Querying `"Who won the football match?"` returned `irrelevant_question` classification and the standard PV refusal response.
- All tests passed successfully with exit code 0!

---

## React Frontend Application Implementation

We have successfully designed, built, and verified the complete React (Vite) + JavaScript enterprise-grade frontend for the AI Pharmacovigilance & Regulatory Intelligence platform.

### 1. Ingestion & Preprocessing Workspace
* **[UploadCasePage.jsx](file:///Users/affu01/GRAD_PROJ_NEW/frontend/src/pages/UploadCasePage.jsx)**:
* Implemented a unified workspace page allowing clinical safety reviewers to upload scanned report files or paste clinical text narratives.
* Incorporates a simulated step-by-step progress tracking pipeline detailing PDF parsing, OCR detection, RAG retrieval, and FDA query phases.
* Formats and renders segmented sub-cards for multi-patient documents, providing instant access to child case workspaces.

### 2. Clinical Evaluation Workspace & Collapsible Safety Chatbot
* **[AnalysisWorkspace.jsx](file:///Users/affu01/GRAD_PROJ_NEW/frontend/src/pages/AnalysisWo
# MISSING LINE 641
# MISSING LINE 642
# MISSING LINE 643
# MISSING LINE 644
# MISSING LINE 645
# MISSING LINE 646
# MISSING LINE 647
# MISSING LINE 648
# MISSING LINE 649
# MISSING LINE 650
# MISSING LINE 651
# MISSING LINE 652
# MISSING LINE 653
# MISSING LINE 654
# MISSING LINE 655
# MISSING LINE 656
# MISSING LINE 657
# MISSING LINE 658
# MISSING LINE 659
# MISSING LINE 660
# MISSING LINE 661
# MISSING LINE 662
# MISSING LINE 663
# MISSING LINE 664
# MISSING LINE 665
```
`✓ built in 685ms` compiling `dist/assets/index.css` and `dist/assets/index.js` bundle files.

---

## Synchronous Backend Report Generation Ingestion Update

We updated the backend case ingestion API flow (`/analyze/` and `/analyze/text`) to generate full clinical safety reports synchronously upon ingestion. This completely eliminates the unnecessary `"pending"` status step and outputs the fully compiled report details with status `"success"` immediately.

### 1. Synchronous Router Execution
* **[analyze.py](file:///Users/affu01/GRAD_PROJ_NEW/backend/app/routes/analyze.py)**:
* Modified all 4 ingestion returns (single/multi-case PDF file and text narrative routes) to import `generate_report` and `ReportGenerateRequest` locally from `app.routes.report`.
* Awaits `generate_report(..., force=True)` synchronously and returns the completed report dict directly in the response payload.
* In parent multi-case flows, it synchronously triggers report generation for all segmented child cases, builds the zip bundle on disk, saves the parent state, and returns the aggregated parent safety payload.

### 2. Verification
* Tested both single-case and multi-case ingestion flows using programmatic test clients:
* **Single Case**: Verified that `POST /analyze/text` synchronously invokes openFDA, Milvus, and Groq reasoning, returning status `"success"` and a fully compiled 7.7KB report containing causality and seriousness assessments.
* **Multi Case**: Verified that `POST /analyze/text` splits the multi-patient narrative text, invokes child report generations, compiles the consolidated parent report sheet, saves the parent ZIP archive on disk, and returns status `"success"` with all segment child results in the response payload.

### 3. Frontend Integration Fix
* **[UploadCasePage.jsx](file:///Users/affu01/GRAD_PROJ_NEW/frontend/src/pages/UploadCasePage.jsx)**:
* Modified the `executePipeline` function to extract the analysis ID from either `ingestData.analysis_id` or `ingestData.report_id` (since the synchronous response returns the completed report object directly).
* This resolves the `422 Unprocessable Entity` API error caused by calling the report generation endpoint with an undefined `analysis_id`.
* Updated the navigation action on each child segmented case card to read `analysis_id` directly, allowing reviewers to jump to case workspaces without manual URL extraction.

### 4. Non-overlapping Clinical Insights Refinement
* **[llm_service.py](file:///Users/affu01/GRAD_PROJ_NEW/backend/app/services/llm_service.py)**:
* Refined prompt schema descriptions for `ai_safety_insights`, `medical_insights`, and `safety_observations` to enforce distinct categories of clinical review content.
* This prevents the model from generating overlapping/repetitive text across report tabs and guarantees that each section provides unique clinical value (safety warnings, patient risk factors, and actionable physician recommendations).

