import os
import pandas as pd
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CDSCO_CSV_PATH = os.path.join(DATA_DIR, "cdsco_banned.csv")
UN_CSV_PATH = os.path.join(DATA_DIR, "un_banned.csv")

class RegulatoryService:
    def __init__(self):
        self.cdsco_df = self._load_csv(CDSCO_CSV_PATH)
        self.un_df = self._load_csv(UN_CSV_PATH)

    def _load_csv(self, path: str):
        if os.path.exists(path):
            try:
                return pd.read_csv(path)
            except Exception as e:
                logger.error(f"Failed to load CSV at {path}: {e}")
        return pd.DataFrame()

    def check_banned_drugs(self, drug_names: List[str]) -> List[Dict]:
        alerts = []
        for drug in drug_names:
            if not self.cdsco_df.empty and 'drug_name' in self.cdsco_df.columns:
                cdsco_match = self.cdsco_df[self.cdsco_df['drug_name'].astype(str).str.contains(drug, case=False, na=False)]
                if not cdsco_match.empty:
                    alerts.append({
                        "drug_name": drug,
                        "source": "CDSCO",
                        "reason": cdsco_match.iloc[0].get("ban_reason", "Banned in India")
                    })
            if not self.un_df.empty and 'drug_name' in self.un_df.columns:
                un_match = self.un_df[self.un_df['drug_name'].astype(str).str.contains(drug, case=False, na=False)]
                if not un_match.empty:
                    alerts.append({
                        "drug_name": drug,
                        "source": "UN",
                        "reason": un_match.iloc[0].get("ban_reason", "Globally restricted")
                    })
        return alerts

regulatory_service_instance = RegulatoryService()
