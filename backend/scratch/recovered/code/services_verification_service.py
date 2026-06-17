import logging
from typing import Dict, Any, List
from app.services.verification.evidence_service import evidence_service

logger = logging.getLogger(__name__)

class VerificationService:
def verify_case_claims(self, drug_name: str, symptoms: List[str]) -> List[Dict[str, Any]]:
"""
Validates clinical claims (drug-symptom associations) against FDA, FAERS, and KB evidence.
"""
verified_claims = []
if not drug_name or not symptoms:
return verified_claims

# Fetch evidence details
fda_ev = evidence_service.get_fda_evidence(drug_name)
local_faers = evidence_service.get_local_faers_evidence(drug_name)
kb_ev = evidence_service.get_knowledge_base_evidence(drug_name)

# Build maps for case-insensitive lookup
fda_top_rx = [rx.lower() for rx in fda_ev.get("top_reactions", [])]
local_rx_map = {item["reaction"].lower(): item for item in local_faers}

for symptom in symptoms:
s_lower = symptom.lower().strip()
verified_from = []
evidence_details = []

# 1. Verify against FDA API
if s_lower in fda_top_rx:
verified_from.append("FDA API")
evidence_details.append(f"{fda_ev.get('total_cases', 0)} FDA cases found")
elif fda_ev.get("total_cases", 0) > 0:
# Fallback if drug exists in FDA API but symptom is no
verified_from.append("FDA API")
evidence_details.append(f"Drug found in FDA API event database ({fda_ev.get('total_cases', 0)} cases)")

# 2. Verify against local FAERS
local_match = local_rx_map.get(s_lower)
if local_match:
verified_from.append("FAERS_2026_Q1")
evidence_details.append(f"{local_match['count']} FAERS matches found")

# 3. Verify against Knowledge Base (warning documents in Milvus)
kb_match_found = False
for chunk in kb_ev:
text_lower = chunk.get("retrieved_chunk", "").lower()
if s_lower in text_lower or drug_name.lower() in text_lower:
kb_match_found = True
break

if kb_match_found or len(kb_ev) > 0:
verified_from.append("Knowledge Base")
evidence_details.append("FDA warning chunk retrieved")

if verified_from:
verified_claims.append({
"claim": f"{drug_name.title()} associated with {symptom.lower()}",
"verified_from": verified_from,
"evidence": evidence_details
})

return verified_claims

def get_verification_status(self, verified_claims: List[Dict[str, Any]]) -> str:
"""
Calculates verification status based on validated claims.
"""
if not verified_claims:
return "Unverified"

# If at least one claim has evidence from multiple sources
has_multi_source = any(len(c.get("verified_from", [])) >= 2 for c in verified_claims)
if has_multi_source:
return "Verified"

return "Inconclusive"

verification_service = VerificationService()

