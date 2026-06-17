import logging
from pymilvus import DataType
from app.milvus.milvus_client import milvus_client

logger = logging.getLogger(__name__)

# List of collections required for the dual-collection RAG architecture
COLLECTIONS = ["knowledge_base", "input_documents"]

def initialize_collections():
    """
    Initializes Milvus collections starting from a completely clean state.
    Drops existing collections, creates schemas manually, builds IVF_FLAT indices with L2 metric,
    inserts a dummy test vector, flushes, loads, and executes test queries to confirm correctness.
    """
    for col_name in COLLECTIONS:
        try:
            # Drop existing collection to clear schemas, indices, and any corruption/duplicates
            if milvus_client.has_collection(col_name):
                logger.info(f"Dropping existing collection '{col_name}' to start from a clean state...")
                milvus_client.drop_collection(col_name)
                logger.info(f"Successfully dropped collection '{col_name}'.")
            
            logger.info(f"1. Creating Milvus collection '{col_name}' schema...")
            
            # Explicitly define the full schema manually
            schema = milvus_client.create_schema(
                auto_id=False,
                enable_dynamic_field=True
            )
            
            # Use 'embedding' field for floating vectors as required
            schema.add_field(field_name="id", datatype=DataType.VARCHAR, max_length=255, is_primary=True)
            schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
            schema.add_field(field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=384)
            schema.add_field(field_name="analysis_id", datatype=DataType.VARCHAR, max_length=255)
            schema.add_field(field_name="drug_name", datatype=DataType.VARCHAR, max_length=4096)
            schema.add_field(field_name="document_type", datatype=DataType.VARCHAR, max_length=255)
            schema.add_field(field_name="collection_type", datatype=DataType.VARCHAR, max_length=255)
            schema.add_field(field_name="document_name", datatype=DataType.VARCHAR, max_length=512)
            
            # Create the collection
            milvus_client.create_collection(
                collection_name=col_name,
                schema=schema
            )
            logger.info(f"Collection '{col_name}' schema registered.")

            logger.info(f"2. Creating vector index on 'embedding' field using FLAT & L2 metric...")
            # Prepare index params (Metric: L2, Index Type: FLAT)
            index_params = milvus_client.prepare_index_params()
            index_params.add_index(
                field_name="embedding",
                metric_type="L2",
                index_type="FLAT",
                index_name="embedding_index"
            )
            milvus_client.create_index(
                collection_name=col_name,
                index_params=index_params
            )
            logger.info(f"Index created on 'embedding' field for '{col_name}'.")

            logger.info(f"3. Inserting one test vector into '{col_name}'...")
            dummy_vector = [0.1] * 384
            dummy_data = {
                "id": f"dummy_init_{col_name}",
                "text": "dummy initialization text segment",
                "embedding": dummy_vector,
                "analysis_id": "None",
                "drug_name": "None",
                "document_type": "None",
                "collection_type": col_name,
                "document_name": "None"
            }
            milvus_client.insert(collection_name=col_name, data=[dummy_data])
            logger.info("Test vector inserted.")

            logger.info(f"4. Flushing collection '{col_name}'...")
            milvus_client.flush(col_name)
            logger.info("Collection flushed.")

            logger.info(f"5. Loading collection '{col_name}'...")
            milvus_client.load_collection(col_name)
            logger.info("Collection loaded into memory.")

            logger.info(f"6. Running test search on '{col_name}'...")
            test_results = milvus_client.search(
                collection_name=col_name,
                data=[dummy_vector],
                anns_field="embedding",
                limit=1,
                output_fields=["text"]
            )
            logger.info(f"Test search results for '{col_name}': {test_results}")
            logger.info(f"7. Milvus Collection '{col_name}' successfully initialized and ready for bulk ingestion.")

        except Exception as e:
            logger.error(f"Failed to initialize Milvus collection '{col_name}': {e}")
            raise e

# Auto-initialize collections on import - REMOVED to prevent initialization issues on import
# initialize_collections()

# Exports for routing components
knowledge_base = "knowledge_base"
input_documents = "input_documents"
