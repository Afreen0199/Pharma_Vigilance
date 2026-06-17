import os
import logging
import json
from typing import Dict, Any, Optional, List
from supabase import create_client, Client
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.client: Optional[Client] = None
        
        if not self.supabase_url or not self.supabase_key:
            logger.error("Supabase credentials (SUPABASE_URL, SUPABASE_KEY) are missing in environment variables!")
        else:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
                logger.info("Successfully initialized Supabase Client.")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase Client: {e}")

    def save_case_analysis(
        self,
        analysis_id: str,
        filename: str,
        extracted_text: str,
        drugs: List[str],
        symptoms: List[str],
        conditions: List[str],
        ocr_metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Inserts a new case analysis record in Supabase with a 'pending' status.
        """
        if not self.client:
            logger.error("Supabase client is not initialized.")
            return False
            "analysis_id": analysis_id,
            "filename": filename,
            "extracted_text": extracted_text,
            "drugs": drugs,
            "symptoms": symptoms,
            "conditions": conditions,
            "symptoms": symptoms,
            "conditions": conditions,
            "status": "pending"
        }
        
        if ocr_metadata:
            payload["ai_summary"] = json.dumps({"ocr_metadata": ocr_metadata})

        try:
            # Insert record using Supabase client
            response = self.client.table("case_analyses").insert(payload).execute()
            logger.info(f"Successfully saved case analysis '{analysis_id}' to Supabase. Response: {response}")
            return True
        except Exception as e:
            logger.error(f"Error saving case analysis '{analysis_id}' to Supabase: {e}")
            raise e

    def get_case_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a case analysis record from Supabase by analysis_id.
        """
        if not self.client:
            logger.error("Supabase client is not initialized.")
            return None

        try:
            response = self.client.table("case_analyses").select("*").eq("analysis_id", analysis_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error retrieving case analysis '{analysis_id}' from Supabase: {e}")
            raise e

    def update_case_analysis_results(
        self,
        analysis_id: str,
        ai_summary: str,
        seriousness_assessment: Dict[str, Any],
        causality_assessment: Dict[str, Any],
        timeline: List[Dict[str, Any]],
        missing_data: List[str],
        regulatory_alerts: List[Dict[str, Any]],
        fda_signals: Dict[str, Any]
    ) -> bool:
        """
        Updates the case analysis record in Supabase with full clinical report results.
        Marks the status as 'completed'.
        """
        if not self.client:
            logger.error("Supabase client is not initialized.")
            return False

        payload = {
            "ai_summary": ai_summary,
            "seriousness_assessment": seriousness_assessment,
            "causality_assessment": causality_assessment,
            "timeline": timeline,
            "missing_data": missing_data,
            "regulatory_alerts": regulatory_alerts,
            "fda_signals": fda_signals,
            "status": "completed"
        }

        try:
            response = self.client.table("case_analyses").update(payload).eq("analysis_id", analysis_id).execute()
            logger.info(f"Successfully updated analysis '{analysis_id}' to status 'completed'. Response: {response}")
            return True
        except Exception as e:
            logger.error(f"Error updating case analysis '{analysis_id}' in Supabase: {e}")
            raise e

    def get_all_case_analyses(self) -> List[Dict[str, Any]]:
        """
        Retrieves all case analyses from Supabase.
        """
        if not self.client:
            logger.error("Supabase client is not initialized.")
            return []
        try:
            response = self.client.table("case_analyses").select("*").execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error retrieving all case analyses: {e}")
            return []

# Singleton Database Service Instance
db_service = DatabaseService()



