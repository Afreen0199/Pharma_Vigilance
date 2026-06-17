from app.services.hybrid_search_service import hybrid_search_service
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class RAGService:
    def retrieve_from_knowledge_base(self, query: str, n_results: int = 3, filters: Optional[Dict[str, Any]] = None) -> str:
        """Retrieve medical and regulatory safety guidance from the knowledge_base collection using hybrid search."""
        try:
            results = hybrid_search_service.search_collection(
                collection_name="knowledge_base",
                query_text=query,
                metadata_filters=filters,
                limit=n_results
            )
            documents = [item["text"] for item in results]
            return "\n\n".join(documents)
        except Exception as e:
            logger.error(f"Error retrieving from knowledge base collection: {e}")
            return ""

    def retrieve_from_input_documents(self, query: str, n_results: int = 3, filters: Optional[Dict[str, Any]] = None) -> str:
        """Retrieve similar historical patient cases and summaries from the input_documents collection using hybrid search."""
        try:
            results = hybrid_search_service.search_collection(
                collection_name="input_documents",
                query_text=query,
                metadata_filters=filters,
                limit=n_results
            )
            documents = [item["text"] for item in results]
            return "\n\n".join(documents)
        except Exception as e:
            logger.error(f"Error retrieving from input documents collection: {e}")
            return ""

    def combine_contexts(self, kb_context: str, doc_context: str) -> str:
        """Combines medical guidelines and patient case contexts with clean visual partitions."""
        sections = []
        if doc_context.strip():
            sections.append(f"=== RELATED HISTORICAL PATIENT CASES (Milvus: input_documents) ===\n{doc_context}")
        if kb_context.strip():
            sections.append(f"=== MEDICAL & REGULATORY GUIDELINES (Milvus: knowledge_base) ===\n{kb_context}")
            
        return "\n\n".join(sections)

    def retrieve_context(self, query: str, filters: Optional[Dict[str, Any]] = None) -> str:
        """Coordinate dual-collection retrieval and return aggregated comparative context using hybrid search."""
        kb_ctx = self.retrieve_from_knowledge_base(query, filters=filters)
        doc_ctx = self.retrieve_from_input_documents(query, filters=filters)
        return self.combine_contexts(kb_ctx, doc_ctx)

rag_service_instance = RAGService()
