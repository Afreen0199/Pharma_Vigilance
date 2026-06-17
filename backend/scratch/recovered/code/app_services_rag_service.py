from app.services.chroma_service import chroma_service_instance
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def retrieve_context(self, query: str) -> str:
        """Retrieve relevant context from ChromaDB based on the query."""
        try:
            results = chroma_service_instance.query([query], n_results=3)
            documents = results.get("documents", [[]])[0]
            context = "\n\n".join(documents)
            return context
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return ""

rag_service_instance = RAGService()
