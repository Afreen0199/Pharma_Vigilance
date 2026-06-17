import os
import pandas as pd
import logging
from typing import List, Set

logger = logging.getLogger(__name__)

FAERS_CSV_PATH = "/Users/affu01/GRAD_PROJ_NEW/faers_master.csv"

GENERIC_SALTS_AND_FORMS = {
    "sodium", "potassium", "calcium", "chloride", "acid", "tablet", "tablets",
    "capsule", "capsules", "injection", "injections", "mg", "ml", "oral", "water",
    "solution", "suspension", "cream", "ointment", "gel", "spray", "patch",
    "supplement", "supplementation", "dose", "dosage", "escalation", "history"
}

class DrugValidatorService:
    def __init__(self):
        # 1. Curated list of known medications (clean and safe for token matching)
        self.known_drugs: Set[str] = {
            "warfarin", "aspirin", "pantoprazole", "amlodipine", "ibuprofen", "paracetamol", "acetaminophen",
            "metformin", "lisinopril", "atorvastatin", "simvastatin", "rosuvastatin", "clopidogrel", "heparin",
            "enoxaparin", "apixaban", "rivaroxaban", "dabigatran", "warfarin sodium", "insulin", "vitamin k",
            "vitamin d", "prednisone", "prednisolone", "methotrexate", "sirolimus", "tacrolimus", "cyclosporine",
            "basiliximab", "mycophenolate mofetil", "clofazimine", "sandostatin", "afinitor", "dexilant",
            "crestor", "voltaren", "dilaudid", "zocor", "diltiazem", "effexor", "nimesulide",
            "folic", "folic acid", "hydroxychloroquine", "telmisartan", "glipizide", "amoxicillin", 
            "penicillin", "albuterol", "omeprazole", "statin", "corticosteroid"
        }
        
        self.known_symptoms: Set[str] = set()
        self.known_conditions: Set[str] = set()
        self.stopwords: Set[str] = set()
        self.banned_drugs: Set[str] = set()
        self.faers_drugs: Set[str] = set()
        
        # 2. Blacklists for procedures, body parts, and generic medical nouns
        self.procedures_blacklist: Set[str] = {
            "palpation", "abdominal palpation", "ultrasound", "mri", "x-ray", "ct scan", 
            "biopsy", "surgery", "endoscopy", "colonoscopy", "blood test", "test", 
            "procedure", "examination", "physical", "ecg", "endoscopic", "operation"
        }
        
        self.body_parts_blacklist: Set[str] = {
            "stomach", "liver", "kidney", "heart", "lung", "brain", "skin", "blood", 
            "urine", "eye", "ear", "throat", "head", "chest", "abdomen", "abdominal",
            "muscle", "joint", "joints", "muscles", "bone", "bones", "blood vessel", "vein",
            "calf", "calves"
        }
        
        self.generic_medical_blacklist: Set[str] = {
            "alert", "report", "patient", "case", "hospital", "doctor", "physician", 
            "nurse", "treatment", "therapy", "dose", "dosage", "administer", 
            "administration", "intravenous", "oral", "tablet", "capsule", "mg", "ml",
            "clinical", "findings", "investigation", "investigations", "diagnosed",
            "prescribed", "stopped", "started", "increased", "decreased", "positive",
            "negative", "normal", "abnormal", "dechallenge", "rechallenge", "adr",
            "baseline", "trend", "supplement", "supplementation", "escalation", "history"
        }

        self._load_dictionaries()

    def _load_dictionaries(self):
        """Pre-loads datasets from cleaner and regulatory services."""
        from app.services.medical_entity_cleaner import medical_entity_cleaner_instance
        from app.services.regulatory_service import regulatory_service_instance
        
        # Load from MedicalEntityCleaner to extend our known_drugs set
        cleaner = medical_entity_cleaner_instance
        self.known_drugs.update({d.lower().strip() for d in cleaner.known_drugs})
        self.known_symptoms = {s.lower().strip() for s in cleaner.known_symptoms}
        self.known_conditions = {c.lower().strip() for c in cleaner.known_conditions}
        self.stopwords = {sw.lower().strip() for sw in cleaner.stopwords}
        
        # Load from regulatory service
        reg = regulatory_service_instance
        if not reg.cdsco_df.empty and 'drug_name' in reg.cdsco_df.columns:
            self.banned_drugs.update(
                reg.cdsco_df['drug_name'].dropna().str.lower().str.strip().tolist()
            )
        if not reg.un_df.empty and 'drug_name' in reg.un_df.columns:
            self.banned_drugs.update(
                reg.un_df['drug_name'].dropna().str.lower().str.strip().tolist()
            )

    def get_faers_drugs(self) -> Set[str]:
        """Lazy loads or reuses FAERS drug names list from MedicalEntityCleaner or reads directly."""
        from app.services.medical_entity_cleaner import medical_entity_cleaner_instance
        cleaner = medical_entity_cleaner_instance
        if cleaner.faers_drugs:
            self.faers_drugs = cleaner.faers_drugs
            return self.faers_drugs
        
        if self.faers_drugs:
            return self.faers_drugs
            
        # Fallback: Read drug names directly from FAERS CSV using optimized pandas loader
        if os.path.exists(FAERS_CSV_PATH):
            try:
                logger.info(f"Validator: Loading drug list from FAERS dataset: {FAERS_CSV_PATH}")
                df = pd.read_csv(FAERS_CSV_PATH, usecols=["drugname"])
                faers_set = {str(name).lower().strip() for name in df["drugname"].dropna().unique()}
                cleaner.faers_drugs = faers_set # Cache it in cleaner too
                self.faers_drugs = faers_set
                logger.info(f"Validator: Loaded {len(faers_set)} unique drug names from FAERS.")
                return faers_set
            except Exception as e:
                logger.error(f"Validator fallback failed to load FAERS dataset: {e}")
        return set()

    def validate_drugs(self, entities: List[str]) -> List[str]:
        """
        Validates a list of medical entities and returns only those that are confirmed
        to be actual drug names.
        
        Filters out:
          - Symptoms and adverse events
          - Chronic/background conditions and diseases
          - Procedures, diagnostic tests
          - Generic medical terms and body parts
          - Noisy OCR artifacts or stopwords
        """
        if not entities:
            return []
            
        validated_drugs = []
        faers_drugs = self.get_faers_drugs()
        
        for ent in entities:
            if not ent:
                continue
                
            clean_ent = ent.strip()
            lower_ent = clean_ent.lower()
            
            # 1. STOPWORDS & BASIC FILTERS
            if len(lower_ent) < 3 and lower_ent not in {"iv", "k"}:
                continue
            if lower_ent in self.stopwords:
                continue
                
            # 2. BLACKLIST FILTERS (Symptom, Condition, Procedure, Body Part, Generic)
            if lower_ent in self.known_symptoms or any(s in lower_ent for s in self.known_symptoms if len(s) > 4):
                continue
            if lower_ent in self.known_conditions or any(c in lower_ent for c in self.known_conditions if len(c) > 4):
                continue
            if lower_ent in self.procedures_blacklist or any(p in lower_ent for p in self.procedures_blacklist):
                continue
            if lower_ent in self.body_parts_blacklist or any(b in lower_ent for b in self.body_parts_blacklist):
                continue
            if lower_ent in self.generic_medical_blacklist or any(g in lower_ent for g in self.generic_medical_blacklist):
                continue
                
            # 3. DRUG CROSS-CHECK VALIDATION
            is_valid = False
            
            # A. Exact Match (The safest match against any dictionary including noisy FAERS)
            if lower_ent in self.known_drugs or lower_ent in self.banned_drugs or lower_ent in faers_drugs:
                is_valid = True
                
            # B. Token/Word Match (Only matching tokens against curated, clean lists to prevent false positives)
            if not is_valid:
                # Split by space or hyphen
                words = [w.strip() for w in lower_ent.replace("-", " ").split()]
                for w in words:
                    if w in self.known_drugs or w in self.banned_drugs:
                        # Ensure we don't match generic salts/forms
                        if w not in GENERIC_SALTS_AND_FORMS and len(w) > 3:
                            is_valid = True
                            break
                            
            if is_valid:
                # Format to Title Case nicely, keeping uppercase standard for abbreviations like IV or APL
                formatted = clean_ent.title() if lower_ent not in {"iv", "apl", "un", "inr"} else clean_ent.upper()
                if formatted not in validated_drugs:
                    validated_drugs.append(formatted)
                    
        return validated_drugs

# Singleton instance
drug_validator_service = DrugValidatorService()
