import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Complete fixed schema for Langfuse enterprise metadata
METADATA_SCHEMA = {
    # General
    "analysis_id": None,
    "case_id": None,
    "session_id": None,
    "trace_group": None,
    "run_type": None,
    "analysis_mode": None,
    "run_name": None,
    "pipeline_stage": None,
    "evaluation_target": None,
    "processing_status": None,
    "model_name": None,
    "llm_provider": None,
    "embedding_model": None,
    "report_type": None,
    
    # Retrieval
    "retrieval_strategy": None,
    "vector_database": None,
    "retrieved_chunk_count": None,
    "retrieved_document_count": None,
    "average_similarity_score": None,
    "highest_similarity_score": None,
    
    # Verification
    "verification_status": None,
    "fda_signal_score": None,
    "matched_fda_cases": None,
    "evidence_source_count": None,
    
    # Report
    "primary_suspect_drug": None,
    "primary_reaction": None,
    "seriousness": None,
    "causality": None,
    "timeline_event_count": None,
    "missing_information_count": None,
    "regulatory_alert_count": None,
    
    # Chat
    "question_type": None,
    "response_type": None,
    
    # System
    "metadata_schema_version": "1.0"
}

def build_langfuse_metadata(**kwargs) -> Dict[str, Any]:
    """
    Builds a structured, lightweight, privacy-compliant JSON-serializable dictionary
    based on the fixed enterprise metadata schema for Langfuse observability.
    Never fails or interrupts inference on errors.
    """
    metadata = METADATA_SCHEMA.copy()
    try:
        # Default session_id to analysis_id if provided
        if "analysis_id" in kwargs and kwargs["analysis_id"] is not None:
            if "session_id" not in kwargs or kwargs["session_id"] is None:
                metadata["session_id"] = kwargs["analysis_id"]

        for key, value in kwargs.items():
            if key in metadata:
                # Ensure value is JSON serializable
                if value is not None and not isinstance(value, (str, int, float, bool, list, dict)):
                    metadata[key] = str(value)
                else:
                    metadata[key] = value

        # Force schema version consistency
        metadata["metadata_schema_version"] = "1.0"

    except Exception as e:
        logger.warning(f"Failed to build Langfuse metadata: {e}. Falling back to default schema.")
        
    return metadata
