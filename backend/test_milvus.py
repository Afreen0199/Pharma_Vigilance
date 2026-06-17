import os
import sys
import logging
from dotenv import load_dotenv
from pymilvus import MilvusClient

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load env
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")
load_dotenv(env_path)

milvus_uri = os.getenv("MILVUS_URI", "http://127.0.0.1:19530")
logger.info(f"Connecting to Milvus at {milvus_uri}...")

try:
    client = MilvusClient(uri=milvus_uri)
    logger.info("Successfully connected to Milvus.")
except Exception as e:
    logger.error(f"Failed to connect to Milvus at {milvus_uri}: {e}")
    sys.exit(1)

# List collections
collections = client.list_collections()
logger.info(f"Collections present in database: {collections}")

# Describe collections
for col in ["knowledge_base", "input_documents"]:
    if client.has_collection(col):
        desc = client.describe_collection(col)
        logger.info(f"\nSchema for '{col}': {desc}")
        stats = client.get_collection_stats(col)
        logger.info(f"Stats for '{col}': {stats}")
    else:
        logger.warning(f"Collection '{col}' does not exist.")
