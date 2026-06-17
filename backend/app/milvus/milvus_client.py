import os
import logging
from pymilvus import MilvusClient

logger = logging.getLogger(__name__)

# First check if MILVUS_URI is provided in environment/dot-env (for external gRPC server / Attu support)
milvus_uri = os.getenv("MILVUS_URI")

if milvus_uri:
    uri = milvus_uri
    logger.info(f"Initializing Milvus Client (Connecting to gRPC server: {uri})...")
else:
    DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(DB_DIR, exist_ok=True)
    uri = os.path.join(DB_DIR, "milvus_pv_ai.db")
    logger.info(f"Initializing Milvus Client (Milvus Lite local file: {uri})...")

try:
    # Relaxed keepalive and ping options to prevent 'too_many_pings' gRPC GOAWAY signals
    grpc_options = [
        ("grpc.keepalive_time_ms", 300000),             # 5 minutes ping interval
        ("grpc.keepalive_timeout_ms", 20000),           # 20 seconds wait response
        ("grpc.keepalive_permit_without_calls", 0)       # disable keepalive when channel is idle
    ]
    milvus_client = MilvusClient(uri=uri, grpc_options=grpc_options)
    logger.info("Successfully connected to Milvus client.")
except Exception as e:
    logger.error(f"Failed to initialize Milvus Client: {e}")
    raise e
