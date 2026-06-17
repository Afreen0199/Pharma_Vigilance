import re
import logging
from typing import Dict, List, Set, Any
from app.services.fda_service import fda_service_instance

logger = logging.getLogger(__name__)

class MedicalEntityCleaner:
    """
    Hybrid Medical Entity Cleaning Pipeline.
    Cleans up OCR noise, deletes non-medical tokens, standardizes text casing,
    and classifies extracted entities into 'drugs', 'symptoms', and 'conditions'
    using static indexes and the loaded local FAERS database.
    """
    def __init__(self):
        # 1. Comprehensive blacklist of stopwords, OCR artifacts, and generic hospital terms
        self.stopwords: Set[str] = {
            "criteria", "admission", "nadir", "episodes", "gi", "indication", "yes", "no", "month",
            "dose", "elevated", "inr", "rechallenge", "outpatient review", "discharge", "primary diagnosis",
            "treating", "chronic", "normalised", "treating physician", "patient", "hb", "discharge summary",
            "department of internal medicine", "action", "female", "tamil nadu", "gender", "af", "resume",
            "md", "administered", "haemoglobin", "years", "emergency department", "yes | death",
            "cardiologist", "prn", "antiplatelet", "probable/definite", "discharge", "ip-2026", "plasma",
            "chennai", "classification", "follow-up", "date", "apollo", "discontinuation", "score",
            "hospitalization", "no.\napl-2026", "signature", "ffp", "iv vitamin k", "prevention", "ip",
            "expectedness", "symptomatic", "therapeutic", "ceased", "ward", "cover", "male", "reduced",
            "india", "medical icu", "day", "over-anticoagulation", "seriousness", "vitamin k 10 mg iv",
            "oral", "internal medicine", "frequency", "drug", "weeks", "age", "secondary to", "self-adjust",
            "fresh", "transfusion", "daily", "days", "monitoring", "long-term", "stable condition",
            "monitoring scheduled", "platelet count", "discharged", "revealed", "serum creatinine", "pt",
            "mrd", "ppi", "causality\nseriousness", "narajo", "naranjo", "physician", "ppi therapy",
            "transfused", "upper", "drug-induced", "protection", "secondary diagnosis", "complication",
            "gi endoscopy", "dechallenge", "adr", "10-apr-2026", "complication", "packed", "red cells",
            "blood", "department", "medicine", "yes/no", "tablet", "capsule", "history", "admitted",
            "clinical", "findings", "investigations", "diagnosed", "prescribed", "stopped", "started",
            "increased", "decreased", "positive", "negative", "normal", "abnormal", "treatment"
        }

        # 2. Known pharmaceutical indices for standard validation
        self.known_drugs: Set[str] = {
            "warfarin", "aspirin", "pantoprazole", "amlodipine", "ibuprofen", "paracetamol", "acetaminophen",
            "metformin", "lisinopril", "atorvastatin", "simvastatin", "rosuvastatin", "clopidogrel", "heparin",
            "enoxaparin", "apixaban", "rivaroxaban", "dabigatran", "warfarin sodium", "insulin", "vitamin k",
            "vitamin d", "prednisone", "prednisolone", "methotrexate", "sirolimus", "tacrolimus", "cyclosporine",
            "basiliximab", "mycophenolate mofetil", "clofazimine", "sandostatin", "afinitor", "dexilant",
            "crestor", "voltaren", "dilaudid", "zocor", "diltiazem", "effexor", "nimesulide"
        }

        # 3. Known clinical symptoms / ADR indices
        self.known_symptoms: Set[str] = {
            "gi bleeding", "bleeding", "haematemesis", "melaena", "dizziness", "anaemia", "haemorrhage",
            "hemorrhage", "bruising", "bruises", "unusual bruising", "blood in vomit", "vomit", "vomiting",
            "peptic ulcer", "peptic ulcer disease", "oesophageal erosions", "erythema", "scab", "rosacea",
            "bone pain", "pneumonia", "eye pruritus", "pain", "peripheral swelling", "periorbital oedema",
            "illness", "cellulitis", "nasopharyngitis", "urinary tract infection", "fatigue", "swelling",
            "skin irritation", "pruritus", "dyspepsia", "rash", "oedema", "tremor", "nausea", "dyspnoea",
            "dysphonia", "drug eruption", "drug hypersensitivity", "toxicity", "iritis", "transplant rejection",
            "wound infection", "skin infection", "anxiety", "insomnia", "hallucination", "paraesthesia",
            "hypokinesia", "asthenia", "nasal polyps", "nasal congestion", "dizziness postural", "joint swelling",
            "joint warmth"
        }

        # 4. Known disease / background condition indices
        self.known_conditions: Set[str] = {
            "atrial fibrillation", "hypertension", "coronary artery disease", "stroke", "diabetes", "arthritis",
            "neuroendocrine tumour", "renal transplant", "leprosy", "parkinson's disease", "osteoarthritis",
            "asthma", "clavicle fracture", "general physical health deterioration", "obesity", "geriatric",
            "copd", "cancer"
        }

        # 5. Fast compile formatting regex filters
        self.non_alpha_num = re.compile(r'[^a-zA-Z0-9\s\-/]')
        self.digits_only = re.compile(r'^\d+$')
        
        # 6. FAERS CSV unique drug dictionary cache
        self.faers_drugs: Set[str] = set()
        self._load_faers_dictionary()

    def _load_faers_dictionary(self):
        """Asynchronously builds an optimized lowercased dictionary index from the FAERS dataset."""
        try:
            if fda_service_instance.faers_df is not None:
                if 'drugname' in fda_service_instance.faers_df.columns:
                    unique_names = fda_service_instance.faers_df['drugname'].dropna().unique()
                    self.faers_drugs = {str(name).lower().strip() for name in unique_names}
                    logger.info(f"Hybrid Drug Validation: Successfully indexed {len(self.faers_drugs)} unique drug names from local FAERS database.")
        except Exception as e:
            logger.warning(f"Could not build FAERS dictionary index for dynamic cleaning: {e}")

    def clean_entity_text(self, text: str) -> str:
        """Filters non-alphanumeric noise and newlines from raw extracted entity text."""
        if not text:
            return ""
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = self.non_alpha_num.sub('', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def clean_and_classify(self, raw_entities: List[str]) -> Dict[str, List[str]]:
        """
        Accepts raw extracted entities list, cleans them, applies stopwords and regex,
        validates drug candidates using hybrid matching, and maps terms to structured keys.
        """
        cleaned_drugs: Set[str] = set()
        cleaned_symptoms: Set[str] = set()
        cleaned_conditions: Set[str] = set()

        # Resilient load in case FAERS data loaded after cleaner initialization
        if not self.faers_drugs and fda_service_instance.faers_df is not None:
            self._load_faers_dictionary()

        for raw_ent in raw_entities:
            cleaned_text = self.clean_entity_text(raw_ent)
            lower_text = cleaned_text.lower()

            # Discard number-only tokens, short symbols, and stopwords
            if len(lower_text) < 3 and lower_text not in {"gi", "af", "inr", "ppi", "adr", "iv", "prn"}:
                continue
            if lower_text in self.stopwords:
                continue
            if self.digits_only.match(lower_text):
                continue

            # Standardized title normalization
            normalized_name = cleaned_text.title() if not lower_text in {"gi", "af", "inr", "ppi", "adr", "iv", "prn"} else cleaned_text.upper()

            # A. Dynamic Drug Validation (FAERS + known drugs list)
            if lower_text in self.known_drugs or lower_text in self.faers_drugs:
                cleaned_drugs.add(normalized_name)
                continue
                
            # Perform loose subset matching against FAERS drug names
            is_faers_match = False
            for faers_d in self.faers_drugs:
                if len(faers_d) > 4 and (faers_d in lower_text or lower_text in faers_d):
                    if lower_text not in self.stopwords and faers_d not in self.stopwords:
                        cleaned_drugs.add(normalized_name)
                        is_faers_match = True
                        break
            if is_faers_match:
                continue

            # B. Symptom & Adverse Event validation
            if lower_text in self.known_symptoms:
                cleaned_symptoms.add(normalized_name)
                continue

            # C. Background disease & chronic conditions validation
            if lower_text in self.known_conditions:
                cleaned_conditions.add(normalized_name)
                continue

            # D. Heuristic fallback classification (Suffix / Prefix patterns)
            if any(lower_text.endswith(suffix) for suffix in ["in", "ole", "ine", "pam", "lol", "sone", "umab", "imab", "mofetil"]):
                cleaned_drugs.add(normalized_name)
            elif any(sympt_kw in lower_text for sympt_kw in ["bleed", "pain", "nausea", "vomit", "dizz", "swelling", "pruritus", "rash"]):
                cleaned_symptoms.add(normalized_name)
            elif any(cond_kw in lower_text for cond_kw in ["fibrillation", "tension", "sclerosis", "disease", "transplant", "stroke", "fracture", "polyps"]):
                cleaned_conditions.add(normalized_name)

        return {
            "drugs": sorted(list(cleaned_drugs)),
            "symptoms": sorted(list(cleaned_symptoms)),
            "conditions": sorted(list(cleaned_conditions))
        }

# Singleton cleaner instance
medical_entity_cleaner_instance = MedicalEntityCleaner()
