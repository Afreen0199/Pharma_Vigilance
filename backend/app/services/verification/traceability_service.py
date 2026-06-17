import logging
from typing import Dict, Any, List, Optional
from app.services.hybrid_search_service import hybrid_search_service

logger = logging.getLogger(__name__)

class TraceabilityService:
    def get_traceable_chunks(self, drug_name: str, analysis_id: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves semantic vector chunks from both input_documents and knowledge_base collections,
        formatting them with clean source metadata and retrieval scores.
        """
        chunks = []
        try:
            filters = {}
            if drug_name:
                filters["drug_name"] = drug_name
            if analysis_id:
                filters["analysis_id"] = analysis_id

            # Query knowledge_base
            kb_results = hybrid_search_service.search_collection(
                collection_name="knowledge_base",
                query_text=drug_name,
                metadata_filters=filters,
                limit=limit
            )

            # Query input_documents
            doc_filters = {}
            if analysis_id:
                doc_filters["analysis_id"] = analysis_id
            elif drug_name:
                doc_filters["drug_name"] = drug_name
                
            doc_results = hybrid_search_service.search_collection(
                collection_name="input_documents",
                query_text=drug_name or "patient",
                metadata_filters=doc_filters,
                limit=limit
            )

            # Format and aggregate retrieved chunks
            for item in kb_results:
                doc_name = item.get("document_name") or item.get("document_type") or "Knowledge Base Document"
                if doc_name == "None":
                    doc_name = "Knowledge Base Document"
                chunks.append({
                    "source_document": doc_name,
                    "source_type": item.get("document_type") or "Regulatory Guidance",
                    "retrieval_score": round(float(item.get("score", 0.5)), 4),
                    "analysis_id": item.get("analysis_id") or "None"
                })

            for item in doc_results:
                doc_name = item.get("document_name") or item.get("document_type") or "Ingested Patient Case File"
                if doc_name == "None":
                    doc_name = "Ingested Patient Case File"
                chunks.append({
                    "source_document": doc_name,
                    "source_type": item.get("document_type") or "Patient Narrative",
                    "retrieval_score": round(float(item.get("score", 0.5)), 4),
                    "analysis_id": item.get("analysis_id") or "None"
                })
        except Exception as e:
            logger.error(f"Error gathering traceable chunks: {e}")

        # Sort combined chunks by score descending
        chunks.sort(key=lambda x: x["retrieval_score"], reverse=True)
        return chunks[:limit]

traceability_service = TraceabilityService()
