
import requests
import re
import pandas as pd
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Constants
FDA_API_BASE_URL = "https://api.fda.gov/drug/event.json"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
FAERS_CSV_PATH = "/Users/affu01/GRAD_PROJ_NEW/faers_master.csv"

UNRELATED_REACTIONS_BLACKLIST = {
    "product quality issue", "drug dependence", "product label issue", 
    "product design issue", "device malfunction", "underdose", 
    "intentional product misuse", "overdose", "off label use", 
    "drug abuse", "incorrect dose administered", "product use issue", 
    "therapy interruption", "accidental overdose", "intentional overdose",
    "misplaced product", "product conversion issue", "wrong drug",
    "incorrect product storage", "exposure to product", "product container issue",
    "no adverse event", "drug interaction", "condition aggravated", "off-label use", 
    "product packaging issue", "product administration error", "wrong product administered",
    "device use issue", "therapeutic product effect decreased", "treatment noncompliance"
}

def normalize_drug_name(drug_name: str) -> str:
    """
    Cleans and normalizes raw drug name input.
    Removes:
      - Parenthesized text (e.g. (MTX) or (Simvastatin))
      - Dosage text (e.g. 20 mg/week, 500mg, 10 mg once weekly)
      - Routes, forms, and frequency keywords
      - Trailing pu
    """
    if not drug_name:
        return ""
        
    # Remove parenthesis and anything inside
    name = re.sub(r'\(.*?\)', '', drug_name)
    
    # Remove dosage patterns (number followed by mg, mcg, g, ml, etc.)
    name = re.split(r'\b\d+\s*(?:mg|mcg|g|ml)\b', name, flags=re.IGNORECASE)[0]
    
    # Remove numbers if a dosage was listed differently
    name = re.split(r'\b\d', name)[0]
    
    # Split by route, form, or frequency keywords to strip them out
    name = re.split(
        r'\b(?:oral|orally|intravenous|iv|im|prn|daily|weekly|tablet|tablets|capsule|capsules|pill|pills|injection)\b', 
        name, 
        flags=re.IGNORECASE
    )[0]
    
    return name.strip(",. \t\n\r")








        # Local data aggregation (if available)
        local_total = 0
        if self.faers_df is not None:
            # Assuming 'drug_name' column exists
            local_total = len(self.faers_df[self.faers_df['drug_name'].str.contains(drug_name, case=False, na=False)])

        return {
            "drug_name": drug_name,
            "api_records_retrieved": len(api_results),
            "local_records_found": local_total,
            "hybrid_search_active": True,






















            return None

    def search_by_drug(self, drug_name: str) -> Dict:
        """Search adverse events by drug name using hybrid approach."""
        normalized_name = normalize_drug_name(drug_name)
        from app.services.drug_validator_service import drug_validator_service
        validated = drug_validator_service.validate_drugs([normalized_name])
        if not validated:
            logger.warning(f"Drug validation failed for '{normalized_name}' (original: '{drug_name}') in search_by_drug.")
            return {
                "drug_name": normalized_name or drug_name,
                "api_records_retrieved": 0,
                "local_records_found": 0,
                "hybrid_search_active": False,
                "raw_api_results": []
            }
        validated_drug = validated[0]
        
        api_query = f'patient.drug.medicinalproduct:"{validated_drug}"'
        api_data = self._query_openfda(api_query, limit=100)
        
        # Aggregate from API
        api_results = api_data.get("results", []) if api_data else []
        total_api_cases = api_data.get("meta", {}).get("results", {}).get("total", len(api_results)) if api_data else 0
        
        # Local data aggregation (if available)
        local_total = 0
        if self.faers_df is not None:
            local_total = len(self.faers_df[self.faers_df['drugname'].str.contains(validated_drug, case=False, na=False)])

        return {
            "drug_name": validated_drug,
            "api_records_retrieved": total_api_cases,
            "local_records_found": local_total,
            "hybrid_search_active": True,
            "raw_api_results": api_results[:5]
        }

    def search_by_reaction(self, reaction: str) -> Dict:
        """Search adverse events by reaction."""
        api_query = f'patient.reaction.reactionmeddrapt:"{reaction}"'
        api_data = self._query_openfda(api_query, limit=100)
        api_results = api_data.get("results", []) if api_data else []
        total_api_cases = api_data.get("meta", {}).get("results", {}).get("total", len(api_results)) if api_data else 0

        return {
            "reaction": reaction,
            "api_records_retrieved": total_api_cases,
            "raw_api_results": api_results[:5]
        }

    def get_serious_cases(self, drug_name: str) -> List[Dict]:
        """Retrieve serious cases for a given drug."""
        normalized_name = normalize_drug_name(drug_name)
        from app.services.drug_validator_service import drug_validator_service
        validated = drug_validator_service.validate_drugs([normalized_name])
        if not validated:
            logger.warning(f"Drug validation failed for '{normalized_name}' (original: '{drug_name}') in get_serious_cases.")
            return []
        validated_drug = validated[0]
        
        api_query = f'(patient.drug.medicinalproduct:"{validated_drug}") AND (serious:1)'
        api_data = self._query_openfda(api_query, limit=50)
        return api_data.get("results", []) if api_data else []

    def get_recent_cases(self, drug_name: str) -> List[Dict]:
        """Retrieve the most recent cases for a given drug."""
        normalized_name = normalize_drug_name(drug_name)
        from app.services.drug_validator_service import drug_validator_service
        validated = drug_validator_service.validate_drugs([normalized_name])
        if not validated:
            logger.warning(f"Drug validation failed for '{normalized_name}' (original: '{drug_name}') in get_recent_cases.")
            return []
        validated_drug = validated[0]
        
        api_query = f'patient.drug.medicinalproduct:"{validated_drug}"'
        params = {"search": api_query, "limit": 10, "sort": "receivedate:desc"}
        
        try:
            response = self.session.get(FDA_API_BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            logger.error(f"Error fetching recent cases for {validated_drug}: {e}")
            return []

    def get_fda_signal_summary(self, drug_name_or_structure, case_context: Optional[Dict] = None) -> Dict:
        """
        Generate a summarized signal analysis for a drug, aggregating local and API data.
        Accepts either a raw drug name string or a structured output dictionary.
        Uses case context to query context-specific cases and rank reactions semantically.
        """
        if isinstance(drug_name_or_structure, dict):
            # Extract from structured output as required
            structured_output = drug_name_or_structure
            drug_name = structured_output.get("suspected_drug_information", {}).get("drug_name", "")
            # Automatically build case_context if not provided
            if not case_context:
                case_context = {
                    "adverse_event": structured_output.get("adverse_event_details", {}).get("adverse_event", ""),
                    "symptoms": structured_output.get("key_entities_extracted", {}).get("symptom", "") or structured_output.get("symptoms", []),
                    "conditions": structured_output.get("key_entities_extracted", {}).get("condition", "") or structured_output.get("conditions", [])
                }
        else:
            drug_name = str(drug_name_or_structure)

        # Normalize the drug name (remove dosage,
        normalized_name = normalize_drug_name(drug_name)
        
        from app.services.drug_validato
        validated = drug_validator_service.validate_drugs([normalized_name])















        # Extract case context details
        context_text = ""
        if case_context:
            adverse_event = case_context.get("adverse_event", "")
            symptoms_list = case_context.get("symptoms", [])
            conditions_list = case_context.get("conditions", [])
            symptoms_str = ", ".join(symptoms_list) if isinstance(symptoms_list, list) else str(symptoms_list)
            conditions_str = ", ".join(conditions_list) if isinstance(conditions_list, list) else str(conditions_list)
            context_text = f"{adverse_event} {symptoms_str} {conditions_str}".lower()

        # Define organ system keyword groups
        ORGAN_SYSTEMS = {
            "hepatic": {
                "keywords": {"liver", "hepat", "dili", "alt", "ast", "bilirubin", "transaminase", "ascites", "jaundice", "hepatic", "ggt", "alp", "hepatotoxicity"},
                "adr_terms": {"hepatotoxicity", "drug-induced liver injury", "alanine aminotransferase increased", "aspartate aminotransferase increased", "liver injury", "hepatic failure", "ascites", "jaundice", "hyperbilirubinaemia", "hepatic function abnormal"}
            },
            "renal": {
                "keywords": {"renal", "kidney", "nephr", "creatinine", "urea", "anuria", "oliguria", "dysuria", "nephrotoxicity"},
                "adr_terms": {"renal failure", "acute kidney injury", "nephrotoxicity", "renal impairment", "blood creatinine increased", "blood urea increased", "anuria", "oliguria"}
            },
            "dermatological": {
                "keywords": {"skin", "rash", "erythema", "pruritus", "dermat", "urticaria", "hives", "blister", "sjs", "ten", "dermal", "epidermal"},
                "adr_terms": {"rash", "erythema", "pruritus", "toxic epidermal necrolysis", "stevens-johnson syndrome", "dermatitis", "urticaria", "hives", "drug eruption", "blister"}
            },
            "gastrointestinal": {
                "keywords": {"gastro", "stomach", "bleed", "haemorrhage", "hemorrhage", "nausea", "vomit", "melaena", "haematemesis", "peptic", "ulcer", "abdominal", "constipation", "diarrhoea", "dyspepsia"},
                "adr_terms": {"nausea", "vomiting", "diarrhoea", "abdominal pain", "gastrointestinal haemorrhage", "dyspepsia", "melaena", "haematemesis", "peptic ulcer", "stomatitis"}
            },
            "cardiac": {
                "keywords": {"cardiac", "heart", "myocardial", "arrhythmia", "infarction", "stroke", "hypertension", "hypotension", "tachycardia", "bradycardia", "angina"},
                "adr_terms": {"myocardial infarction", "cardiac arrest", "arrhythmia", "hypertension", "hypotension", "tachycardia", "bradycardia", "atrial fibrillation", "cardiac failure"}
            },
            "neurological": {
                "keywords": {"dizziness", "headache", "seizure", "neurop", "paresthesia", "tremor", "somnolence", "insomnia", "convulsion"},
                "adr_terms": {"dizziness", "headache", "tremor", "convulsion", "paraesthesia", "somnolence", "neuropathy", "insomnia"}
            },
            "hematological": {
                "keywords": {"blood", "anaemia", "anemia", "thrombocytopenia", "neutropenia", "leukopenia", "pancytopenia", "agranulocytosis", "haemoglobin", "platelet"},
                "adr_terms": {"anaemia", "thrombocytopenia", "neutropenia", "pancytopenia", "leukopenia", "agranulocytosis", "platelet count decreased", "white blood cell count decreased"}
            }
        }

        # Detect target organ systems
        target_systems = []
        for system_name, system_data in ORGAN_SYSTEMS.items():
            if any(kw in
                target_systems.append(system_name)

        # 1. Gather API data
        api_query = f'patient.drug.medicinalproduct:"{validated_drug}"'
        
        # Build contextual query additions if we detected target systems
        context_query_parts = []
        for sys in target_systems:
            terms = list(ORGAN_SYSTEMS[sys]["adr_terms"])[:3]
            for t in terms:
                context_query_parts.append(f'patient.reaction.reactionmeddrapt:"{t}"')

        api_data = None
        active_query = api_query
        if context_query_parts:
            context_query = f'({api_query}) AND ({" OR ".join(context_query_parts)})'
            logger.info(f"Attempting context-aware openFDA query: {context_query}")
            api_data = self._query_openfda(context_query, limit=100)
            if api_data and api_data.get("results"):
                active_query = context_query

        # Fallback to drug-only query if no data returned for the specific contextual query
        if not api_data or not api_data.get("results"):
            logger.info(f"Fallback to drug-only query for: {api_query}")
            api_data = self._query_openfda(api_query, limit=100)
            active_query = api_query

        api_results = api_data.get("results", []) if api_data else []
        total_api_cases = api_data.get("meta", {}).get("results", {}).get("total", len(api_results)) if api_data else 0
        
        # Retrieve true global/contextual counts for serious and hospitalization cases via metadata query
        serious_total = 0
        hosp_total = 0
        if total_api_cases > 0:
            try:
                serious_query = f"({active_query}) AND serious:1"
                serious_data = self._query_openfda(serious_query, limit=1)
                if serious_data:
                    serious_total = serious_data.get("meta", {}).get("results", {}).get("total", 0)
            except Exception as e:
                logger.error(f"Error fetching global serious count: {e}")
                
            try:
                hosp_query = f"({active_query}) AND seriousnesshospitalization:1"
                hosp_data = self._query_openfda(hosp_query, limit=1)
                if hosp_data:
                    hosp_total = hosp_data.get("meta", {}).get("results", {}).get("total", 0)
            except Exception as e:
                logger.error(f"Error fetching global hospitalization count: {e}")
        
        serious_count = 0
        hosp_count = 0
        reactions_freq = {}
        
        for case in api_results:
            if case.get("serious") == "1":
                serious_count += 1
            if case.get("seriousnesshospitalization") == "1":
                hosp_count += 1
                
            patient = case.get("patient", {})
            for r in patient.get("reaction", []):
                reaction_term = r.get("reactionmeddrapt", "")
                if reaction_term:
                    term_lower = reaction_term.lower().strip()
                    # Filter out unrelated/administrative reactions
                    if term_lower in UNRELATED_REACTIONS_BLACKLIST:
                        continue
                    if len(term_lower) < 3:
                        continue
                    term_title = reaction_term.title().strip()
            

        # Fallback to sample count if API total call was missing/failed
        serious_total = max(serious_total, serious_count)
        hosp_total = max(hosp_total, hosp_count)
        
        # Apply Reaction Relevance Scoring
        scored_reactions = []
        for term_title, freq in reactions_freq.items():
            term_lower = term_title.lower()
            
            # Base score from openFDA frequency
            score = float(freq)
            
            # Apply multiplier boost for target systems
            boost_multiplier = 1.0
            for sys in target_systems:
                if any(kw in term_lower for kw in ORGAN_SYSTEMS[sys]["keywords"]) or term_lower in ORGAN_SYSTEMS[sys]["adr_terms"]:
                    boost_multiplier += 15.0  # High relevance organ system match
                    
            # Additional match boost for exact words from symptoms/reactions
            for word in context_text.split():
                if len(word) > 3 and word in term_lower:
                    boost_multiplier += 5.0
                    
            final_score = score * boost_multiplier
            scored_reactions.append((term_title, final_score))

        # Sort top reactions by final relevance score descending
        top_reactions = sorted(scored_reactions, key=lambda x: x[1], reverse=True)[:10]
        top_reactions_list = [r[0] for r in top_reactions]
        
        # Calculate matching strength
        contextual_match_strength = 0
        for rx in top_reactions_list:
            rx_lower = rx.lower()
            for sys in target_systems:
                if any(kw in rx_lower for kw in ORGAN_SYSTEMS[sys]["keywords"]):
                    contextual_match_strength += 1

        # Severe 
        severe_terms = {
            "hepatotoxicity", "liver failure", "anaphylaxis", "kidney injury", "renal failure",
            "myopathy", "rhabdomyolysis", "death", "cardiac arrest", "stevens-johnson syndrome",
            "toxic epidermal necrolysis", "stroke", "haemorrhage", "thrombocytopenia", 
            "agranulocytosis", "myocardial infarction", "hepatitis", "acute liver failure",
            "acute kidney injury", "angioedema", "pancytopenia", "gastrointestinal haemorrhage"
        }
        has_severe_adr = any(term in r.lower() for r in top_reactions_list for term in severe_terms)
        
        # Calculate percentages based on global totals for scoring
        serious_pct = (serious_total / total_api_cases) * 100 if total_api_cases > 0 else 0
        hosp_pct = (hosp_total / total_api_cases) * 100 if total_api_cases > 0 else 0
        
        # Rule-based Signal Scoring considering contextual ADR match strength
        signal_score = "Low"
        if serious_pct > 50 or hosp_pct > 20 or (has_severe_adr and contextual_match_strength >= 1):
            signal_score = "High"
        elif serious_pct > 20 or hosp_pct > 5 or contextual_match_strength >= 1:
            signal_score = "Moderate"

        # 2. Add local CSV data processing if available
        local_total_cases = 0
        if self.faers_df is not None:
             local_total_cases = len(self.faers_df[self.faers_df['drugname'].str.contains(validated_drug, case=False, na=False)])

        # 3. Retrieve recent cases
        recent_cases_list = []
        recent_cases_raw = self.get_recent_cases(validated_drug)
        if recent_cases_raw:
            recent_cases_list = [c.get("safetyreportid") or c.get("caseid") for c in recent_cases_raw[:5] if c.get("safetyreportid") or c.get("caseid")]

        fda_signal = {
            "drug_name": validated_drug,
            "total_cases": total_api_cases + local_total_cases,
            "api_total_cases": total_api_cases,
            "local_total_cases": local_total_cases,
            "serious_cases": serious_total,
            "hospitalizations": hosp_total,
            "top_reactions": top_reactions_list,
            "fda_signal_score": signal_score,
            "recent_cases": [c for c in recent_cases_list if c]
        }

        # Generate visual analytics payloads
        from app.services.chart_service import chart_service_instance
        visualizations = chart_service_instance.generate_charts(validated_drug, fda_signal, api_results)
        fda_signal["visualizations"] = visualizations

        return fda_signal

# Singleton instance
fda_service_instance = FDAService()
