# AI Pharmacovigilance & Regulatory Intelligence System

## 1. Project Overview & Conceptual Summary

**Pharmacovigilance (PV)** is the science of collecting, monitoring, assessing, and evaluating information from healthcare providers and patients on the adverse effects of medications, biological products, blood products, and herbalism, with a view to identifying new information about hazards associated with medicines and preventing harm to patients. 

This project is a complete **End-to-End AI-Powered Pharmacovigilance Platform**. It automates the incredibly tedious and historically manual process of reading patient case narratives, identifying suspected drugs, verifying symptoms, checking against global regulatory databases (like the FDA), and generating standardized medical safety reports. 

By leveraging **Natural Language Processing (SciSpacy)**, **Large Language Models (LLMs)**, **Retrieval-Augmented Generation (RAG) via Milvus**, and the **OpenFDA API**, this system transforms unstructured medical text into actionable, structured regulatory intelligence.

---

## 2. Technology Stack

### Frontend
* **Framework:** React 19 + Vite
* **Styling:** Tailwind CSS + Framer Motion (for dynamic UI animations)
* **Data Visualization:** Recharts
* **Routing & HTTP:** React Router DOM, Axios
* **Icons:** Lucide React

### Backend
* **Framework:** FastAPI (Python)
* **Medical NLP:** SciSpacy (for extracting Medical Entities: Drugs, Symptoms, Conditions)
* **Database:** Supabase (for persistent relational data storage of case analyses)
* **Vector Database (RAG):** Milvus (for embedding and retrieving historical cases)
* **External APIs:** OpenFDA API (for real-time regulatory signals and safety data)
* **AI/LLM:** Integrated LLM Service for advanced reasoning, causality, and seriousness assessments

---

## 3. End-to-End Workflow: Technical & Conceptual Breakdown

This section explains exactly what happens step-by-step from the moment a user interacts with the system until the final report is generated.

### Step 1: Case Intake & Segmentation
* **User Action:** A Pharmacovigilance officer or medical professional goes to the frontend dashboard and uploads a patient case document (PDF, DOCX, TXT, Image) or directly pastes a raw text narrative.
* **What is Happening:** 
    * The frontend sends a `POST /analyze/` request to the FastAPI backend.
    * The backend passes the document to a **Segmentation Engine** (`case_segmentation_engine`).
    * If the document contains multiple patients, it dynamically slices the document into distinct, individual patient cases.
    * It extracts raw text and calculates OCR metadata (like blur score and confidence) if it was an image/PDF.
* **Outcome:** The system now has a clean, segmented text narrative for one or multiple individual patient cases.

### Step 2: Medical Entity Extraction (NLP)
* **What is Happening:** 
    * The raw text narrative is passed to **SciSpacy** (a specialized medical NLP model).
    * SciSpacy scans the text and extracts named entities, categorizing them into: `Drugs`, `Symptoms`, and `Conditions`.
    * The extracted drugs are then passed through a `drug_validator_service` to filter out noise and ensure only valid pharmacological substances are tracked.
* **Response/Outcome:** The system possesses structured arrays of validated `drugs` (e.g., ["Aspirin", "Lisinopril"]), `symptoms` (e.g., ["Nausea", "Headache"]), and `conditions` (e.g., ["Hypertension"]).

### Step 3: Vectorization & Knowledge Base Indexing (RAG)
* **What is Happening:** 
    * A unique UUID (`analysis_id`) is generated for the case.
    * The raw text, along with the extracted medical entities as metadata, is embedded into dense vectors.
    * These vectors are indexed into the local **Milvus Vector Database** inside the `input_documents` collection.
    * *Conceptual Reason:* By vectorizing the case immediately, it becomes part of the system's "memory". Future cases can query Milvus to find historically similar adverse events.
* **Outcome:** The case is successfully indexed for semantic search, and the initial case state is saved to the **Supabase** SQL database. The API returns the `analysis_id` to the frontend.

### Step 4: Triggering the AI Report Generation
* **User Action:** The system automatically (or the user manually) triggers the report generation phase.
* **What is Happening:** 
    * The frontend sends a `POST /report/generate` request using the `analysis_id`.
    * The backend retrieves the initial case state from Supabase.

### Step 5: Suspect Drug Identification & Regulatory Lookup
* **What is Happening:**
    * The backend uses an LLM to read the narrative and identify the **Primary Suspect Drug** (the drug most likely causing the adverse event).
    * **Regulatory Alerts Lookup:** The suspect drug is checked against a database of banned or restricted drugs (`regulatory_service`).
    * **OpenFDA API Query:** The backend queries the official FDA database using the suspect drug and the patient's symptoms. It retrieves historical FAERS (FDA Adverse Event Reporting System) data, checking if this drug-symptom combination is a known "Signal" or a newly emerging risk.
* **Outcome:** The system gathers real-world, global regulatory context regarding the specific adverse event.

### Step 6: Advanced LLM Analysis & Assessment
* **What is Happening:**
    * The backend constructs a massive prompt containing: The raw text, the SciSpacy entities, the FDA signals, and context retrieved from Milvus (RAG).
    * The LLM is tasked with generating a comprehensive medical assessment, which includes:
        * **Causality Assessment:** Did the drug actually cause the symptom? (e.g., Certain, Probable, Possible, Unlikely).
        * **Seriousness Assessment:** Is this a life-threatening event? Did it require hospitalization?
        * **Patient Timeline:** A chronological reconstruction of events.
        * **Missing Data Identification:** The LLM flags critical missing fields (e.g., "Missing patient weight", "Missing drug batch number").
* **Outcome:** A deeply analytical, structured JSON object containing a complete medical safety report is generated by the AI.

### Step 7: Evidence Mapping & Reasoning Transparency
* **What is Happening:**
    * The system doesn't just output AI guesses; it backs them up. The `evidence_service` maps the AI's conclusions back to hard data sources.
    * It tallies FDA reported cases, local FAERS dataset matches, and Knowledge Base document retrievals.
    * The `reasoning_service` formulates plain-English explanations for *why* the AI made its causality and seriousness determinations.
* **Outcome:** The final report is injected with verifiable evidence, drastically reducing AI hallucination risks and building trust with human reviewers.

### Step 8: Finalization, Export & Delivery
* **What is Happening:**
    * The backend normalizes the JSON to ensure schema consistency.
    * It updates the Supabase database with the final, completed report data.
    * The `report_service` generates downloadable files on the server's disk: **JSON, Excel (.xlsx), and PDF**.
    * If the document was a multi-patient document, it bundles all individual patient reports into a single **ZIP file**.
* **Final Response to User:** The backend returns the complete structured JSON to the frontend.
* **Frontend Outcome:** The React frontend renders a beautiful, interactive dashboard displaying the AI Summary, FDA Signals (via Recharts charts), extracted entities, the causality assessment, and provides direct download links for the PDF and Excel reports.

---

## 4. Key Architectural Highlights to Mention in the Panel

1. **Dual-Processing Engine:** The system isn't just an LLM wrapper. It uses deterministic NLP (SciSpacy) for precise medical entity extraction *before* utilizing generative AI. This guarantees baseline accuracy.
2. **Retrieval-Augmented Generation (RAG):** By using Milvus, the system actively "remembers" past cases and official knowledge bases, grounding the LLM's assessments in historical facts rather than isolated reasoning.
3. **Multi-Patient Slicing:** A standout technical feature is the segmentation engine, capable of taking a single chaotic hospital document containing notes on 5 different patients, and correctly branching them into 5 parallel analysis pipelines.
4. **Transparent AI Evidence:** The integration of the `evidence_service` means every AI conclusion is cross-referenced with real OpenFDA API data and local datasets. It solves the "black box" problem of medical AI.
