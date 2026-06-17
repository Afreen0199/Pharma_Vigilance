import logging
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from app.milvus.milvus_client import milvus_client
from app.milvus.collections import knowledge_base, input_documents

logger = logging.getLogger(__name__)

# Lazy load helper for SentenceTransformer to prevent client conflicts on reload
_embedding_model = None

def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        try:
            logger.info("Loading SentenceTransformer model 'all-MiniLM-L6-v2' for Milvus vector insertion...")
            _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Successfully loaded SentenceTransformer model.")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model: {e}")
            raise e
    return _embedding_model

# Self-contained text splitter config matching ChromaDB splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n\n", "\n", " ", ""]
)

def chunk_text(text: str) -> List[str]:
    """Splits raw document text into clean semantic chunks."""
    return text_splitter.split_text(text)

def insert_document(
    collection_name: str,
    text: str,
    document_id: str,
    metadata: Dict[str, Any]
) -> int:
    """
    Chunks a text document, generates embeddings locally using all-MiniLM-L6-v2,
    and inserts records directly into the specified Milvus collection.
    
    :param collection_name: 'knowledge_base' or 'input_documents'
    :param text: Raw text contents to be ingested
    :param document_id: Unique string identifier for the source document
    :param metadata: Context dict containing details like source, document_type, primary_drugs
    :return: The total number of semantic chunks successfully stored.
    """
    if collection_name not in ["knowledge_base", "input_documents"]:
        logger.error(f"Attempted insert on non-existent collection '{collection_name}'!")
        raise ValueError(f"Invalid collection name: {collection_name}. Must be 'knowledge_base' or 'input_documents'")

    chunks = chunk_text(text)
    if not chunks:
        logger.warning(f"Extracted document text was empty or too small. No chunks created for {document_id}.")
        return 0

    try:
        # Generate 384-dim embeddings locally
        embeddings = get_embedding_model().encode(chunks, convert_to_numpy=True).tolist()
        
        # Safely extract and truncate primary_drugs string to avoid exceeding VARCHAR limits (e.g. 255)
        raw_drug_name = metadata.get("primary_drugs", "None")
        if not isinstance(raw_drug_name, str):
            raw_drug_name = str(raw_drug_name)
        drug_name_val = raw_drug_name[:255] if raw_drug_name else "None"

        # Extract document_name metadata
        doc_name_val = "None"
        if collection_name == "knowledge_base":
            doc_name_val = document_id
        else:
            doc_name_val = metadata.get("source", document_id)
        if not doc_name_val:
            doc_name_val = "None"

        data = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{i}"
            
            # Map parameters matching Milvus collections schemas
            payload = {
                "id": chunk_id,
                "embedding": embeddings[i],
                "text": chunk,
                "analysis_id": document_id if collection_name == "input_documents" else metadata.get("analysis_id", "None"),
                "drug_name": drug_name_val,
                "document_type": metadata.get("document_type", "None"),
                "collection_type": collection_name,
                "document_name": doc_name_val
            }
            # Dynamically pass extra metadata fields (e.g., OCR details) to Milvus dynamic fields
            for key, val in metadata.items():
                if key not in payload and key not in ["primary_drugs", "source"]:
                    payload[key] = val
            data.append(payload)
            
        logger.info(f"Inserting {len(chunks)} chunks into Milvus collection '{collection_name}'...")
        res = milvus_client.insert(collection_name=collection_name, data=data)
        logger.info(f"Successfully inserted {len(chunks)} chunks under ID '{document_id}' into Milvus.")
        return len(chunks)
    except Exception as e:
        logger.error(f"Failed to insert chunks into Milvus collection '{collection_name}': {e}")
        raise e

def insert_document_chunks(
    collection_name: str,
    chunks: List[str],
    embeddings: List[List[float]],
    metadatas: List[Dict[str, Any]],
    ids: List[str]
) -> int:
    """
    Direct low-level vector insertion. Inserts pre-computed chunks and embeddings.
    """
    if collection_name not in ["knowledge_base", "input_documents"]:
        logger.error(f"Attempted insert_document_chunks on invalid collection '{collection_name}'!")
        raise ValueError(f"Invalid collection: {collection_name}")
        
    try:
        data = []
        for i in range(len(chunks)):
            meta = metadatas[i] if i < len(metadatas) else {}
            raw_drug_name = meta.get("primary_drugs", meta.get("drug_name", "None"))
            if not isinstance(raw_drug_name, str):
                raw_drug_name = str(raw_drug_name)
            drug_name_val = raw_drug_name[:255] if raw_drug_name else "None"
            
            doc_name_val = meta.get("document_name") or meta.get("source") or meta.get("filename") or "None"
            
            payload = {
                "id": ids[i],
                "embedding": embeddings[i],
                "text": chunks[i],
                "analysis_id": meta.get("analysis_id", "None"),
                "drug_name": drug_name_val,
                "document_type": meta.get("document_type", "None"),
                "collection_type": collection_name,
                "document_name": doc_name_val
            }
            # Dynamically pass extra metadata fields to Milvus dynamic fields
            for key, val in meta.items():
                if key not in payload and key not in ["primary_drugs", "source", "drug_name", "document_name"]:
                    payload[key] = val
            data.append(payload)
            
        res = milvus_client.insert(collection_name=collection_name, data=data)
        return len(chunks)
    except Exception as e:
        logger.error(f"Failed in insert_document_chunks: {e}")
        raise e
