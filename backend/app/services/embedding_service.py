from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100,
                separators=["\n\n", "\n", " ", ""]
            )
            logger.info("Initialized EmbeddingService with all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")

    def chunk_text(self, text: str) -> list:
        return self.text_splitter.split_text(text)
    
    def get_embeddings(self, texts: list) -> list:
        return self.embeddings.embed_documents(texts)

embedding_service_instance = EmbeddingService()
