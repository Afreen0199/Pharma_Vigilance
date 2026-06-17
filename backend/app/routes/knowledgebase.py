from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
from app.services.extraction_service import extraction_service_instance
from app.milvus.vector_insert_service import insert_document

router = APIRouter(prefix="/knowledgebase", tags=["Knowledge Base Ingestion"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_regulatory_guideline(file: UploadFile = File(...)):
    """
    Admin endpoint to upload and index regulatory guidelines, drug bans, and safety reference 
    literature directly into the static 'knowledge_base' ChromaDB Cloud collection.
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    try:
        from app.milvus.milvus_client import milvus_client
        milvus_client.load_collection("knowledge_base")
        
        # Check if document already exists in Milvus
        existing = milvus_client.query(
            collection_name="knowledge_base",
            filter=f'document_name == "{file.filename.replace("\"", "\\\"")}"',
            limit=1
        )
        if existing:
            raise HTTPException(
                status_code=409, 
                detail=f"Document with name '{file.filename}' already exists in collection 'knowledge_base'."
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database check failed: {e}")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        # Write files temporarily on disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Extract text using backend service
        extracted_text = extraction_service_instance.extract_text(file_path, file.filename)
        
        # Setup static reference document metadata tags
        metadata = {
            "source": file.filename,
            "document_type": "regulatory_reference_document",
            "ingested_via": "/knowledgebase/upload"
        }
        
        # Chunk text, generate embeddings locally, and store in 'knowledge_base' cloud collection
        chunks_count = insert_document(
            collection_name="knowledge_base",
            text=extracted_text,
            document_id=file.filename,
            metadata=metadata
        )
        
        return {
            "filename": file.filename,
            "status": "success",
            "destination_collection": "knowledge_base",
            "extracted_text_length": len(extracted_text),
            "text_preview": extracted_text[:200],
            "chunks_indexed": chunks_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_regulatory_documents(collection_name: str = "knowledge_base"):
    """
    List all unique documents currently indexed in the specified Milvus collection.
    """
    if collection_name not in ["knowledge_base", "input_documents"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid collection name. Must be 'knowledge_base' or 'input_documents'."
        )
        
    try:
        from app.milvus.milvus_client import milvus_client
        
        # Ensure collection is loaded
        milvus_client.load_collection(collection_name)
        
        # Query up to 1000 records to extract unique document names
        # Since Milvus doesn't have native SELECT DISTINCT, we filter id != '' and pull document_name/type
        results = milvus_client.query(
            collection_name=collection_name,
            filter='id != ""',
            output_fields=["document_name", "document_type"],
            limit=1000
        )
        
        unique_docs = {}
        for item in results:
            doc_name = item.get("document_name")
            if doc_name and doc_name != "None":
                doc_type = item.get("document_type", "None")
                unique_docs[doc_name] = {
                    "document_name": doc_name,
                    "document_type": doc_type
                }
                
        return {
            "collection": collection_name,
            "documents": list(unique_docs.values())
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to query indexed documents from Milvus: {e}"
        )

@router.delete("/document")
async def delete_document_by_name(document_name: str, collection_name: str = "knowledge_base"):
    """
    Delete all chunks/vectors associated with a document_name from the specified Milvus collection.
    If input_documents is selected, also deletes the metadata from Supabase.
    """
    if not document_name:
        raise HTTPException(status_code=400, detail="document_name is required.")
        
    if collection_name not in ["knowledge_base", "input_documents"]:
        raise HTTPException(status_code=400, detail="Invalid collection name.")
        
    try:
        from app.milvus.milvus_client import milvus_client
        milvus_client.load_collection(collection_name)
        
        # 1. Query Milvus first to see if any chunks match
        # This acts as validation and allows us to get the analysis_id if we need to clean up Supabase
        records = milvus_client.query(
            collection_name=collection_name,
            filter=f'document_name == "{document_name.replace('"', '\\"')}"',
            output_fields=["id", "analysis_id"],
            limit=1
        )
        
        if not records:
            raise HTTPException(
                status_code=404, 
                detail=f"No document found with name '{document_name}' in collection '{collection_name}'."
            )
            
        # 2. Perform deletion in Milvus
        res = milvus_client.delete(
            collection_name=collection_name,
            filter=f'document_name == "{document_name.replace('"', '\\"')}"'
        )
        milvus_client.flush(collection_name)
        
        # 3. Clean up Supabase if it was a case document
        supabase_details = None
        if collection_name == "input_documents":
            from app.services.database_service import db_service
            analysis_id = records[0].get("analysis_id")
            if analysis_id and analysis_id != "None":
                try:
                    db_service.client.table("case_analyses").delete().eq("analysis_id", analysis_id).execute()
                    supabase_details = f"Deleted case analysis '{analysis_id}' from Supabase."
                except Exception as db_err:
                    supabase_details = f"Failed to delete metadata from Supabase: {db_err}"
                    
        return {
            "status": "success",
            "document_name": document_name,
            "collection": collection_name,
            "milvus_details": res,
            "supabase_details": supabase_details
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
