import os
import sys
import logging
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from app.milvus.milvus_client import milvus_client
from app.services.scispacy_service import scispacy_service_instance

logger = logging.getLogger(__name__)

# Lazy load helper for SentenceTransformer to prevent multiprocessing client conflicts on uvicorn reloads
_embedding_model = None

def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        try:
            logger.info("Loading SentenceTransformer model 'all-MiniLM-L6-v2' for Hybrid Search Service...")
            _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Successfully loaded SentenceTransformer model for Hybrid Search.")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer in hybrid search: {e}")
            raise e
    return _embedding_model

class HybridSearchService:
    def extract_metadata_from_query(self, query: str) -> Dict[str, Any]:
        """
        Extracts key medical entities from the query string using SciSpacy
        to construct search filters (e.g. drug_name).
        """
        if not query:
            return {}
        try:
            entities = scispacy_service_instance.extract_entities(query)
            drugs = entities.get("drugs", [])
            symptoms = entities.get("symptoms", [])
            conditions = entities.get("conditions", [])
            
            metadata = {}
            if drugs:
                metadata["drugs"] = drugs
            if symptoms:
                metadata["symptoms"] = symptoms
            if conditions:
                metadata["conditions"] = conditions
            return metadata
        except Exception as e:
            logger.error(f"Failed to extract metadata from query: {e}")
            return {}

    def build_filter_expression(self, filters: Dict[str, Any]) -> Optional[str]:
        """
        Translates a dictionary of filter values into a Milvus boolean expression.
        Supports:
          - drug_name (or drugs list): matches exact drug name or substring in comma-separated list
          - collection_type: exact match
          - document_type: exact match
          - analysis_id: exact match
        """
        if not filters:
            return None
            
        parts = []
        
        # 1. Handle drug name filtering
        drug_val = filters.get("drug_name") or filters.get("drugs")
        if drug_val:
            if isinstance(drug_val, list):
                drug_parts = []
                for d in drug_val:
                    if d and d != "None":
                        escaped = d.replace('"', '\\"')
                        # Cover: exact, middle of list, end of list, start of list
                        drug_parts.append(
                            f'(drug_name == "{escaped}" or '
                            f'drug_name like "%, {escaped}%" or '
                            f'drug_name like "{escaped},%")'
                        )
                if drug_parts:
                    parts.append(f"({' or '.join(drug_parts)})")
            elif isinstance(drug_val, str) and drug_val != "None":
                escaped = drug_val.replace('"', '\\"')
                parts.append(
                    f'(drug_name == "{escaped}" or '
                    f'drug_name like "%, {escaped}%" or '
                    f'drug_name like "{escaped},%")'
                )

        # 2. Handle other exact match fields
        for field in ["collection_type", "document_type", "analysis_id"]:
            if field in filters and filters[field]:
                val = filters[field]
                if isinstance(val, list):
                    val_parts = [f'{field} == "{v.replace('"', '\\"')}"' for v in val if v]
                    if val_parts:
                        parts.append(f"({' or '.join(val_parts)})")
                elif isinstance(val, str) and val != "None":
                    escaped = val.replace('"', '\\"')
                    parts.append(f'{field} == "{escaped}"')

        expr = " and ".join(parts) if parts else None
        logger.info(f"Generated Milvus filter expression: {expr}")
        return expr

    def search_collection(
        self,
        collection_name: str,
        query_text: Optional[str] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
        limit: int = 5,
        boost_entities: Optional[Dict[str, List[str]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes a search on a single collection.
        Supports pure semantic, metadata-only, or hybrid search.
        """
        if collection_name not in ["knowledge_base", "input_documents"]:
            raise ValueError(f"Invalid collection name: {collection_name}")
            
        # 1. Build filter expression
        filter_expr = self.build_filter_expression(metadata_filters)
        
        # 2. Conduct query/search
        try:
            try:
                milvus_client.load_collection(collection_name)
            except Exception as load_err:
                logger.warning(f"Could not load collection '{collection_name}': {load_err}")

            results = []
            
            # Case A: Metadata-only query (no query text)
            if not query_text:
                if not filter_expr:
                    # If both are empty, default to fetching all
                    filter_expr = 'id != ""'
                    
                logger.info(f"Running metadata-only query on '{collection_name}' with filter: {filter_expr}")
                raw_results = milvus_client.query(
                    collection_name=collection_name,
                    filter=filter_expr,
                    limit=limit,
                    output_fields=["id", "text", "analysis_id", "drug_name", "document_type", "collection_type", "document_name"]
                )
                
                # Format results (since it's metadata-only, distance/score is not calculated by vector search)
                for item in raw_results:
                    results.append({
                        "id": item.get("id"),
                        "text": item.get("text"),
                        "score": 0.5,  # neutral default score
                        "drug_name": item.get("drug_name"),
                        "document_type": item.get("document_type"),
                        "collection_type": item.get("collection_type"),
                        "analysis_id": item.get("analysis_id"),
                        "document_name": item.get("document_name")
                    })
                    
            # Case B: Hybrid or pure semantic search
            else:
                query_vector = get_embedding_model().encode([query_text], convert_to_numpy=True).tolist()[0]
                
                logger.info(f"Running similarity search on '{collection_name}' (filter: {filter_expr})")
                raw_search = milvus_client.search(
                    collection_name=collection_name,
                    data=[query_vector],
                    anns_field="embedding",
                    limit=limit,
                    output_fields=["text", "analysis_id", "drug_name", "document_type", "collection_type", "document_name"],
                    filter=filter_expr
                )
                
                if raw_search and len(raw_search) > 0:
                    hits = raw_search[0]
                    for hit in hits:
                        # Extract fields correctly from Milvus response
                        entity = hit.get("entity", {})
                        distance = hit.get("distance", 0.0)
                        
                        # Convert L2 distance to standard similarity score (0.0 to 1.0)
                        # L2 distance is positive, smaller is more similar.
                        score = 1.0 / (1.0 + distance)
                        
                        results.append({
                            "id": hit.get("id"),
                            "text": entity.get("text", ""),
                            "score": score,
                            "drug_name": entity.get("drug_name"),
                            "document_type": entity.get("document_type"),
                            "collection_type": entity.get("collection_type"),
                            "analysis_id": entity.get("analysis_id"),
                            "document_name": entity.get("document_name")
                        })
                        
            # 3. Apply Contextual Reranking and Scoring
            # If boost_entities are provided (e.g. from the user query), adjust scores based on keyword matching
            if boost_entities:
                results = self._rerank_results(results, boost_entities)
                
            # Sort by score descending
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error searching collection '{collection_name}': {e}")
            return []

    def _rerank_results(self, results: List[Dict[str, Any]], boost_entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Performs a contextual reranking of search results.
        Boosts scores of results containing matching symptoms or drugs.
        """
        boosted_results = []
        drugs = [d.lower() for d in boost_entities.get("drugs", [])]
        symptoms = [s.lower() for s in boost_entities.get("symptoms", [])]
        conditions = [c.lower() for c in boost_entities.get("conditions", [])]
        
        for item in results:
            text_lower = item["text"].lower()
            score_boost = 0.0
            
            # Boost for symptoms match (extremely important for clinical accuracy)
            for symptom in symptoms:
                if symptom in text_lower:
                    score_boost += 0.05
                    
            # Boost for drug name match
            for drug in drugs:
                if drug in text_lower:
                    score_boost += 0.03
                    
            # Boost for background conditions match
            for condition in conditions:
                if condition in text_lower:
                    score_boost += 0.02
                    
            # Update score
            item["score"] = min(1.0, item["score"] + score_boost)
            boosted_results.append(item)
            
        return boosted_results

    def hybrid_search_all(
        self,
        query_text: str,
        metadata_filters: Optional[Dict[str, Any]] = None,
        limit: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Dual Collection Hybrid Search.
        Searches both collections separately and returns results.
        """
        # Extract entities from the user query to use for reranking/filtering
        extracted = self.extract_metadata_from_query(query_text)
        
        # Merge extracted drugs into metadata filters if not already provided
        filters = metadata_filters or {}
        if "drug_name" not in filters and "drugs" in extracted and extracted["drugs"]:
            # Default to filtering by the first extracted drug to lock in context
            filters["drug_name"] = extracted["drugs"][0]
            
        logger.info(f"Executing hybrid search all. Query: '{query_text}'. Filters: {filters}")
        
        kb_results = self.search_collection(
            collection_name="knowledge_base",
            query_text=query_text,
            metadata_filters=filters,
            limit=limit,
            boost_entities=extracted
        )
        
        doc_results = self.search_collection(
            collection_name="input_documents",
            query_text=query_text,
            metadata_filters=filters,
            limit=limit,
            boost_entities=extracted
        )
        
        return {
            "knowledge_base": kb_results,
            "input_documents": doc_results
        }

hybrid_search_service = HybridSearchService()
