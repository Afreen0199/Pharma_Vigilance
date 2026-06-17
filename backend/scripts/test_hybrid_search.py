import os
import sys
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Ensure backend directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)
env_path = os.path.join(backend_dir, ".env")
load_dotenv(env_path)

from app.services.hybrid_search_service import hybrid_search_service

def test_hybrid_retrieval():
    logger.info("Starting Hybrid Search Retrieval Architecture Tests...\n")

    # Scenario 1: Pure Semantic Search
    logger.info("=== SCENARIO 1: Pure Semantic Search (Query: 'warfarin bleeding', No Filters) ===")
    results = hybrid_search_service.search_collection(
        collection_name="input_documents",
        query_text="warfarin bleeding",
        metadata_filters=None,
        limit=2
    )
    for i, res in enumerate(results, 1):
        logger.info(f"Result {i} (Score: {res['score']:.4f}):")
        logger.info(f"  Text: {res['text'][:150]}...")
        logger.info(f"  Drug Name: {res['drug_name']}")
        logger.info(f"  Doc Type: {res['document_type']}")
    logger.info("\n" + "="*80 + "\n")

    # Scenario 2: Metadata-only Filtering
    logger.info("=== SCENARIO 2: Metadata-Only Filtering (Filter: drug_name == 'Warfarin', No Query Text) ===")
    results = hybrid_search_service.search_collection(
        collection_name="input_documents",
        query_text=None,
        metadata_filters={"drug_name": "Warfarin"},
        limit=2
    )
    for i, res in enumerate(results, 1):
        logger.info(f"Result {i} (Score: {res['score']:.4f}):")
        logger.info(f"  Text: {res['text'][:150]}...")
        logger.info(f"  Drug Name: {res['drug_name']}")
        logger.info(f"  Doc Type: {res['document_type']}")
    logger.info("\n" + "="*80 + "\n")

    # Scenario 3: Hybrid Search (Query: 'warfarin bleeding' + Filter: drug_name == 'Warfarin')
    logger.info("=== SCENARIO 3: Hybrid Search (Query: 'warfarin bleeding', Filter: drug_name == 'Warfarin') ===")
    results = hybrid_search_service.search_collection(
        collection_name="input_documents",
        query_text="warfarin bleeding",
        metadata_filters={"drug_name": "Warfarin"},
        limit=2
    )
    for i, res in enumerate(results, 1):
        logger.info(f"Result {i} (Score: {res['score']:.4f}):")
        logger.info(f"  Text: {res['text'][:150]}...")
        logger.info(f"  Drug Name: {res['drug_name']}")
        logger.info(f"  Doc Type: {res['document_type']}")
    logger.info("\n" + "="*80 + "\n")

    # Scenario 4: Dual Collection Search
    logger.info("=== SCENARIO 4: Dual Collection Search (Query: 'warfarin bleeding') ===")
    dual_results = hybrid_search_service.hybrid_search_all(
        query_text="warfarin bleeding",
        metadata_filters={"drug_name": "Warfarin"},
        limit=2
    )
    for col, res_list in dual_results.items():
        logger.info(f"--- COLLECTION: {col} ---")
        for i, res in enumerate(res_list, 1):
            logger.info(f"  Result {i} (Score: {res['score']:.4f}):")
            logger.info(f"    Text: {res['text'][:150]}...")
            logger.info(f"    Drug Name: {res['drug_name']}")
            logger.info(f"    Doc Type: {res['document_type']}")
    logger.info("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_hybrid_retrieval()
