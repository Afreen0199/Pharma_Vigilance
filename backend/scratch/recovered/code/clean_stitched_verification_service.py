# pydisasm version 6.1.8
# Python bytecode 3.12.0 (3531)
# Disassembled from Python 3.12.4 | packaged by Anaconda, Inc. | (main, Jun 18 2024, 10:07:17) [Clang 14.0.6 ]
# Timestamp in code: 1781533053 (2026-06-15 19:47:33)
# Source code size mod 2**32: 3304 bytes
# Method Name:       <module>
# Filename:          /Users/affu01/GRAD_PROJ_NEW/backend/app/services/verification/verification_service.py
# Argument count:    0
# Position-only argument count: 0
# Keyword-only arguments: 0
# Number of locals:  0
# Stack size:        4
# Flags:             0x00000000 (0x0)
# First Line:        1
# Constants:
#    0: 0
#    1: None
#    2: ('Dict', 'Any', 'List')
#    3: ('evidence_service',)
#    4: <code object VerificationService at 0x101d556b0, file "/Users/affu01/GRAD_PROJ_NEW/backend/app/services/verification/verification_service.py", line 7>
#    5: 'VerificationService'
# Names:
#    0: logging
#    1: typing
#    2: Dict
#    3: Any
#    4: List
#    5: app.services.verification.evidence_service
#    6: evidence_service
#    7: getLogger
#    8: __name__
#    9: logger
#   10: VerificationService
#   11: verification_service
0:           0 RESUME               0

1:           2 LOAD_CONST           (0)
4 LOAD_CONST           (None)
6 IMPORT_NAME          (logging)
8 STORE_NAME           (logging)

2:          10 LOAD_CONST           (0)
12

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

