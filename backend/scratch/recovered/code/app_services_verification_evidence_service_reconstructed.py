import os
import ast
import logging
from typing import Dict, Any, List, Optional
from app.services.fda_service import fda_service_instance, normalize_drug_name
from app.services.hybrid_search_service import hybrid_search_service

logger = logging.getLogger(__name__)

class EvidenceService:
    def get_fda_evidence(self, drug_name: str) -> Dict[str, Any]:
        """
        Fetches signal data from the FDA API using the FDAService.
        """
        try:
            summary = fda_service_instance.get_fda_signal_summary(drug_name)
            return {
                "total_cases": summary.get("api_total_cases", 0) or summary.get("total_cases", 0),
                "serious_cases": summary.get("serious_cases", 0),
                "hospitalizations": summary.get("hospitalizations", 0),
                "top_reactions": summary.get("top_reactions", [])
            }
        except Exception as e:
            logger.error(f"Error getting FDA evidence for '{drug_name}': {e}")
            return {
                "total_cases": 0,
                "serious_cases": 0,
                "hospitalizations": 0,
                "top_reactions": []
            }

    def get_local_faers_evidence(self, drug_name: str) -> List[Dict[str, Any]]:
        """
        Fetches adverse reaction counts matching the drug name from local FAERS dataset.
        """
        evidence_list = []
        if fda_service_instance.faers_df is None:
            logger.warning("Local FAERS dataset not loaded.")
            return []
            
        try:
            normalized_name = normalize_drug_name(drug_name)
            from app.services.drug_validator_service import drug_validator_service
            validated = drug_validator_service.validate_drugs([normalized_name])
            search_name = validated[0] if validated else normalized_name
            
            df = fda_service_instance.faers_df
            matching_rows = df[df['drugname'].str.contains(search_name, case=False, na=False)]
            
            reaction_counts = {}
            for idx, r_str in matching_rows['reactions'].dropna().items():
                try:
                    r_list = ast.literal_eval(r_str)
                    if isinstance(r_list, list):
                        for rx in r_list:
                            rx_title = str(rx).title().strip()
                            reaction_counts[rx_title] = reaction_counts.get(rx_title, 0) + 1
                except Exception:
                    pass
            
            # Sort reactions by count descending
            sorted_reactions = sorted(reaction_counts.items(), key=lambda x: x[1], reverse=True)
            for rx, count in sorted_reactions[:10]:
                evidence_list.append({
                    "reaction": rx,
                    "count": count,
                    "source": "FAERS_2026_Q1"
                })
        except Exception as e:
            logger.error(f"Error calculating local FAERS evidence for '{drug_name}': {e}")
            
        return evidence_list

    def get_knowledge_base_evidence(self, drug_name: str) -> List[Dict[str, Any]]:
        """
        Searches Milvus knowledge_base collection for warning texts regarding the drug.
        """
        evidence_list = []
        try:
            normalized_name = normalize_drug_name(drug_name)
            from app.services.drug_validator_service import drug_validator_service
            validated = drug_validator_service.validate_drugs([normalized_name])
            search_name = validated[0] if validated else normalized_name
            
            # Query Milvus KB using drug_name filter
            results = hybrid_search_service.search_collection(
                collection_name="knowledge_base",
                query_text=search_name,
                metadata_filters={"drug_name": search_name},
                limit=3
            )
            
            for item in results:
                doc_src = item.get("document_name") or item.get("document_type") or "Knowledge Base Document"
                if doc_src == "None":
                    doc_src = "Knowledge Base Document"
                evidence_list.append({
                    "document_source": doc_src,
                    "retrieved_chunk": item.get("text", "")
                })
        except Exception as e:
            logger.error(f"Error searching knowledge base for '{drug_name}': {e}")
            
        return evidence_list

    def get_supporting_cases(self, drug_name: str, reaction: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves matching individual case records from the local FAERS dataset.
        """
        cases = []
        if fda_service_instance.faers_df is None:
            return []
            
        try:
            normalized_name = normalize_drug_name(drug_name)
            from app.services.drug_validator_service import drug_validator_service
            validated = drug_validator_service.validate_drugs([normalized_name])
            search_name = validated[0] if validated else normalized_name
            
            df = fda_service_instance.faers_df
            matching_rows = df[df['drugname'].str.contains(search_name, case=False, na=False)]
            
            count = 0
            for idx, row in matching_rows.iterrows():
                cid = str(row.get('caseid') or row.get('primaryid') or '')
                r_str = row.get('reactions')
                if not cid or not r_str:
                    continue
                    
                try:
                    r_list = ast.literal_eval(r_str)
                    if not isinstance(r_list, list):
                        continue
                        
                    # Title-case list elements
                    r_list_title = [str(r).title().strip() for r in r_list]
                    
                    # If a specific reaction is specified, filter by it
                    if reaction:
                        if reaction.title().strip() in r_list_title:
                            cases.append({
                                "case_id": cid,
                                "reaction": reaction.title().strip()
                            })
                            count += 1
                    else:
                        # Otherwise list first reaction in case
                        rx_val = r_list_title[0] if r_list_title else "Unknown"
                        cases.append({
                            "case_id": cid,
                            "reaction": rx_val
                        })
                        count += 1
                        
                    if count >= 5:
                        break
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Error getting supporting cases: {e}")
            
        return cases

evidence_service = EvidenceService()
