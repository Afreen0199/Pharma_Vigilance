# AI Pharmacovigilance & Regulatory Intelligence System
## Low-Level Technical Documentation & KT Guide

**Purpose:** This document is designed to onboard new developers without the need for a live Knowledge Transfer (KT) session. It breaks down the internal architecture, step-by-step data flows, and code structures.

---

### 1. System Architecture & Technology Stack

The project operates on a decoupled client-server architecture.

#### 1.1. Frontend (`/frontend_new`)
- **Framework:** React 19 + Vite
- **Styling:** Tailwind CSS + Framer Motion (for animations)
- **State/Routing:** React Router DOM
- **Charts:** Recharts
- **Directory Structure:**
  - `src/pages/`: Contains the main route views (e.g., Dashboard, Analytics).
  - `src/components/`: Reusable UI elements.
  - `src/layouts/`: Global layout wrappers like `DashboardLayout.jsx`.

#### 1.2. Backend (`/backend`)
- **Framework:** FastAPI (Python)
- **LLM Engine:** Langchain + Groq (Llama 3.3 70B Versatile, fallback to 8B Instant)
- **NLP Engine:** SciSpacy (Medical Entity Extraction)
- **Databases:**
  - **Relational:** Supabase (PostgreSQL) for case state tracking.
  - **Vector (RAG):** Milvus Lite (`milvus/` directory) for embeddings.
- **Monitoring/Observability:** Langfuse

---

### 2. Core Directory Structure (Backend)

The backend is where the core logic resides. Understanding `app/services` is crucial.

- `main.py`: The entry point. Initializes FastAPI, CORS, and registers routers (`fda`, `analyze`, `report`, `knowledgebase`, etc.).
- `app/routes/`: Contains all endpoint definitions.
- `app/services/`: Contains the business logic.
  - `llm_service.py`: Handles all interactions with the LLM via Langchain.
  - `scispacy_service.py`: Uses local NLP models to extract drugs, symptoms, and conditions.
  - `rag_service.py`: Manages Retrieval-Augmented Generation context gathering from Milvus.
  - `fda_service.py`: Interfaces with the OpenFDA API to pull historical safety signals.
  - `segmentation/`: Contains logic to split multi-patient hospital documents into distinct cases.
  - `extraction/`: Contains regex and local keyword parsers.

---

### 3. Low-Level Step-by-Step Data Pipeline

This section traces exactly what happens to a document from the moment the user uploads it.

#### Step 3.1: Document Intake & Segmentation
- **Trigger:** Frontend POSTs to `/analyze/`.
- **Logic:** 
  1. The document is received by the backend router (`app/routes/analyze.py`).
  2. If the document has multiple patients, the `case_segmentation_engine` splits the text into an array of distinct narratives.
  3. If it is an image or PDF, OCR is performed to extract raw text, and visual highlight metadata (yellow/purple highlights) is retained.

#### Step 3.2: Medical NLP Extraction
- **Trigger:** Internal function call to `scispacy_service.py`.
- **Logic:**
  1. The raw text is passed to the SciSpacy model.
  2. SciSpacy identifies named entities and categorizes them into `Drugs`, `Symptoms`, and `Conditions`.
  3. The `drug_validator_service.py` is invoked to clean the extracted terms (removing noise, validating real pharmacological substances).

#### Step 3.3: Vectorization & RAG Indexing
- **Trigger:** Internal function calls to `embedding_service.py` and `rag_service.py`.
- **Logic:**
  1. A unique UUID (`analysis_id`) is generated.
  2. The text and the SciSpacy metadata are converted into dense vector embeddings.
  3. These vectors are indexed into **Milvus** inside the `input_documents` collection. This allows future cases to find this case as historical context.
  4. Initial state is saved to the Supabase SQL database.

#### Step 3.4: Triggering Report Generation
- **Trigger:** Frontend POSTs to `/report/generate` with the `analysis_id`.
- **Logic:**
  1. Backend retrieves the case narrative from Supabase.
  2. The system invokes `llm_service.identify_suspected_drug(text)` to find the Primary Suspect Drug. It first uses a regex parser (looking for labels like "suspect drug:"). If it fails, it uses the LLM.
  3. With the suspect drug identified, `fda_service.py` queries the OpenFDA API for real-world historical signals and risk counts.

#### Step 3.5: Advanced LLM Reasoning
- **Trigger:** Call to `llm_service.generate_analysis()`.
- **Logic:**
  1. `rag_service.retrieve_context()` searches Milvus (hybrid search) for similar past cases (`input_documents`) and medical guidelines (`knowledge_base`).
  2. A massive prompt is constructed. It includes:
     - The raw medical narrative.
     - Locally extracted PV fields (Regex outputs).
     - OCR highlight metadata.
     - FDA Context.
     - RAG Context.
  3. The prompt explicitly asks the LLM to perform Causality Assessment, Seriousness Assessment, identify missing information, and generate a standardized JSON conforming to Pharmacovigilance structures.
  4. Langfuse tracks this LLM execution for observability and cost monitoring.

#### Step 3.6: Final Report Delivery
- **Trigger:** Returning the payload to the frontend.
- **Logic:**
  1. The structured JSON from the LLM is parsed and validated.
  2. The final state is updated in Supabase.
  3. `pdf_generator.py` (and potentially Excel generators) are triggered to create downloadable files.
  4. The frontend receives the JSON, rendering the interactive dashboard and making the files available for download.

---

### 4. Running the Project Locally

If a new developer needs to spin up the project to test these flows:

**1. Milvus Vector DB (Required for RAG):**
Navigate to `backend/` and start the local server:
`./venv/bin/milvus-lite server --data-dir milvus/data`

**2. FastAPI Backend:**
Open a new terminal in `backend/`:
`source venv/bin/activate`
`python -m uvicorn main:app --reload`
*Ensure `GROQ_API_KEY` and Supabase keys are in the `.env` file.*

**3. React Frontend:**
Open a new terminal in `frontend_new/`:
`npm run dev`

---
*Note: To convert this document to .docx natively on your machine, simply open Microsoft Word or Google Docs, copy this text, and save the file. No code execution is required.*
