import spacy
import logging
from typing import Dict, List
from app.services.medical_entity_cleaner import medical_entity_cleaner_instance

logger = logging.getLogger(__name__)

class SciSpacyService:
    def __init__(self):
        self.nlp = None
        self.load_model()

    def load_model(self):
        try:
            # Load the en_core_sci_md model
            self.nlp = spacy.load("en_core_sci_md")
            logger.info("Successfully loaded SciSpacy model 'en_core_sci_md'")
        except Exception as e:
            logger.error(f"Failed to load SciSpacy model: {e}. Please ensure it is installed: pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_md-0.5.4.tar.gz")

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        if not self.nlp:
            logger.warning("SciSpacy model is not loaded. Returning empty entities.")
            return {
                "drugs": [],
                "symptoms": [],
                "diseases": [],
                "conditions": [],
                "medical_terms": []
            }
        
        doc = self.nlp(text)
        
        medical_terms = []

        # en_core_sci_md extracts entities generically. 
        # A more robust implementation would use scispacy.linker for UMLS linking to segregate into drugs, symptoms, diseases.
        for ent in doc.ents:
            medical_terms.append(ent.text)

        # Remove duplicates
        medical_terms = list(set(medical_terms))

        # Use medical_entity_cleaner to clean and classify raw extracted entities
        cleaned = medical_entity_cleaner_instance.clean_and_classify(medical_terms)

        return {
            "drugs": cleaned.get("drugs", []),
            "symptoms": cleaned.get("symptoms", []),
            "diseases": cleaned.get("conditions", []),  # Map conditions to diseases to support legacy calls if any
            "conditions": cleaned.get("conditions", []),
            "medical_terms": cleaned.get("drugs", [])  # Map drugs to medical_terms since analyze.py maps medical_terms to drugs
        }

scispacy_service_instance = SciSpacyService()

