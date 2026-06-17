import os
import sys
import logging
from dotenv import load_dotenv
from pymilvus import MilvusClient, DataType

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables from backend/.env
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)
env_path = os.path.join(backend_dir, ".env")
load_dotenv(env_path)

try:
    from app.milvus.milvus_client import milvus_client as client
    logger.info("Successfully loaded Milvus client from app.")
except Exception as e:
    logger.error(f"Failed to connect to Milvus client: {e}")
    sys.exit(1)

COLLECTIONS = ["knowledge_base", "input_documents"]

def setup():
    for col_name in COLLECTIONS:
        try:
            # Drop existing collection if it exists
            if client.has_collection(col_name):
                logger.info(f"Dropping existing collection '{col_name}'...")
                client.drop_collection(col_name)
                logger.info(f"Successfully dropped collection '{col_name}'.")

            logger.info(f"Creating collection '{col_name}' schema...")
            schema = client.create_schema(
                auto_id=False,
                enable_dynamic_field=True
            )
            schema.add_field(field_name="id", datatype=DataType.VARCHAR, max_length=255, is_primary=True)
            schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
            schema.add_field(field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=384)
            schema.add_field(field_name="analysis_id", datatype=DataType.VARCHAR, max_length=255)
            schema.add_field(field_name="drug_name", datatype=DataType.VARCHAR, max_length=4096)
            schema.add_field(field_name="document_type", datatype=DataType.VARCHAR, max_length=255)
            schema.add_field(field_name="collection_type", datatype=DataType.VARCHAR, max_length=255)
            schema.add_field(field_name="document_name", datatype=DataType.VARCHAR, max_length=512)

            client.create_collection(
                collection_name=col_name,
                schema=schema
            )
            logger.info(f"Collection '{col_name}' schema registered.")

            logger.info(f"Creating vector index on 'embedding' field for '{col_name}'...")
            index_params = client.prepare_index_params()
            index_params.add_index(
                field_name="embedding",
                metric_type="L2",
                index_type="FLAT",
                index_name="embedding_index"
            )
            client.create_index(
                collection_name=col_name,
                index_params=index_params
            )
            logger.info(f"Index created on 'embedding' field for '{col_name}'.")

            logger.info(f"Inserting dummy test vector into '{col_name}'...")
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
            client.insert(collection_name=col_name, data=[dummy_data])
            logger.info("Test vector inserted.")

            logger.info(f"Flushing collection '{col_name}'...")
            client.flush(col_name)
            logger.info("Collection flushed.")

            logger.info(f"Loading collection '{col_name}'...")
            client.load_collection(col_name)
            logger.info("Collection loaded into memory.")

            logger.info(f"Running test search on '{col_name}'...")
            test_results = client.search(
                collection_name=col_name,
                data=[dummy_vector],
                anns_field="embedding",
                limit=1,
                output_fields=["text"]
            )
            logger.info(f"Test search results for '{col_name}': {test_results}")
            logger.info(f"Milvus Collection '{col_name}' successfully setup and ready.\n")

        except Exception as e:
            logger.error(f"Failed to setup collection '{col_name}': {e}")
            sys.exit(1)

if __name__ == "__main__":
    setup()
