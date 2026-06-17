import logging
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from app.milvus.milvus_client import milvus_client
from app.milvus.collections import knowledge_base, input_documents

logger = logging.getLogger(__name__)

# Initialize SentenceTransformer local model (shares cache if already loaded)
try:
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    logger.error(f"Failed to load SentenceTransformer model in retrieval: {e}")
    raise e

def convert_dict_to_milvus_filter(filter_dict: Dict[str, Any]) -> str:
    """Helper to convert standard dict query filters into Milvus boolean expression strings."""
    parts = []
    for k, v in filter_dict.items():
        field = k
        if k == "drug":
            field = "drug_name"
        elif k == "source":
            field = "analysis_id"
            
        if isinstance(v, str):
            parts.append(f'{field} == "{v}"')
        else:
            parts.append(f'{field} == {v}')
    return " and ".join(parts)

def retrieve_similar_context(
    collection_name: str,
    query_text: str,
    n_results: int = 3,
    where_filter: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Queries Milvus collection using local embedding similarity and pulls top-k similar matches.
    
    :param collection_name: 'knowledge_base' or 'input_documents'
    :param query_text: Raw query text to search for
    :param n_results: Number of top matches to retrieve (top-k)
    :param where_filter: Optional dict of metadata constraints (e.g. {"drug": "Warfarin"})
    :return: A list of formatted dictionaries containing the text, metadata, and distance.
    """
    if collection_name not in ["knowledge_base", "input_documents"]:
        logger.error(f"Attempted search on non-existent collection '{collection_name}'!")
        raise ValueError(f"Invalid collection name: {collection_name}. Must be 'knowledge_base' or 'input_documents'")

    try:
        # 1. Embed query text locally
        query_vector = embedding_model.encode([query_text], convert_to_numpy=True).tolist()[0]
        
        # 2. Build Milvus filter expression if filter provided
        filter_expr = None
        if where_filter:
            filter_expr = convert_dict_to_milvus_filter(where_filter)
            
        # 3. Perform semantic search
        results = milvus_client.search(
            collection_name=collection_name,
            data=[query_vector],
            anns_field="embedding",
            limit=n_results,
            output_fields=["text", "analysis_id", "drug_name", "document_type", "collection_type"],
            filter=filter_expr
        )
        
        retrieved_items = []
        if results and len(results) > 0:
            hits = results[0]
            for hit in hits:
                entity = hit.get("entity", {})
                
                # Reconstruct metadata dict structure to maintain strict backward compatibility with Chroma schema
                metadata = {
                    "analysis_id": entity.get("analysis_id"),
                    "primary_drugs": entity.get("drug_name"),
                    "document_type": entity.get("document_type"),
                    "collection_type": entity.get("collection_type"),
                    "source": entity.get("analysis_id")
                }
                
                retrieved_items.append({
                    "id": hit.get("id"),
                    "document": entity.get("text", ""),
                    "metadata": metadata,
                    "distance": hit.get("distance")
                })
                
        logger.info(f"Retrieved {len(retrieved_items)} similar nodes from Milvus collection '{collection_name}'.")
        return retrieved_items
    except Exception as e:
        logger.error(f"Error executing semantic query on Milvus collection '{collection_name}': {e}")
        return []

# Helper orchestration methods matching requirements
def retrieve_from_knowledge_base(query: str, n_results: int = 3) -> str:
    """Retrieve medical and regulatory safety guidance from the knowledge_base collection."""
    results = retrieve_similar_context("knowledge_base", query, n_results)
    documents = [item["document"] for item in results]
    return "\n\n".join(documents)

def retrieve_from_input_documents(query: str, n_results: int = 3) -> str:
    """Retrieve similar historical patient cases and summaries from the input_documents collection."""
    results = retrieve_similar_context("input_documents", query, n_results)
    documents = [item["document"] for item in results]
    return "\n\n".join(documents)

def combine_contexts(kb_context: str, doc_context: str) -> str:
    """Combines medical guidelines and patient case contexts with clean visual partitions."""
    sections = []
    if doc_context.strip():
        sections.append(f"=== RELATED HISTORICAL PATIENT CASES (Milvus: input_documents) ===\n{doc_context}")
    if kb_context.strip():
        sections.append(f"=== MEDICAL & REGULATORY GUIDELINES (Milvus: knowledge_base) ===\n{kb_context}")
    return "\n\n".join(sections)
