import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ReasoningService:
    def explain_seriousness(self, case_data: Dict[str, Any]) -> List[str]:
        """
        Derives human-readable explanation bullets for the seriousness assessment of a case.
        """
        reasons = []
        seriousness = case_data.get("seriousness_assessment", {}) or {}
        case_info = case_data.get("case_information", {}) or {}

        # Look at seriousness keys
        is_serious = False
        
        # Check hospitalization
        hosp = seriousness.get("hospitalization") or seriousness.get("hospitalized")
        if hosp and str(hosp).lower() in ["yes", "true", "1", "serious"]:
            reasons.append("Hospitalization occurred")
            is_serious = True
            
        # Check life threatening
        lt = seriousness.get("life_threatening") or seriousness.get("is_life_threatening")
        if lt and str(lt).lower() in ["yes", "true", "1", "serious"]:
            reasons.append("Life-threatening event flagged")
            is_serious = True

        # Check death
        death = seriousness.get("death") or seriousness.get("died")
        if death and str(death).lower() in ["yes", "true", "1", "serious"]:
            reasons.append("Fatal outcome reported")
            is_serious = True

        # Check disabling
        disabling = seriousness.get("disabling") or seriousness.get("disability")
        if disabling and str(disabling).lower() in ["yes", "true", "1", "serious"]:
            reasons.append("Disabling/incapacitating condition reported")
            is_serious = True

        # Check congenital anomaly
        congenital = seriousness.get("congenital_anomaly")
        if congenital and str(congenital).lower() in ["yes", "true", "1", "serious"]:
            reasons.append("Congenital anomaly detected")
            is_serious = True

        # Fallback medically significant / other check
        overall_serious = case_info.get("seriousness") or seriousness.get("is_serious")
        if str(overall_serious).lower() in ["serious", "yes", "true"]:
            if not reasons:
                reasons.append("Medically significant event")
            else:
                reasons.append("Assessed as clinically serious")
        else:
            if not reasons:
                reasons.append("Mild adverse drug reaction")
                reasons.append("No seriousness criteria met")

        return reasons

    def explain_causality(self, case_data: Dict[str, Any]) -> List[str]:
        """
        Derives human-readable explanation bullets for the causality assessment of a case.
        """
        reasons = []
        causality = case_data.get("causality_assessment", {}) or {}
        fda_sig = case_data.get("fda_signal", {}) or case_data.get("fda_signals", {}) or {}
        events = case_data.get("adverse_events", {}) or {}
        
        # Check FDA signal count
        top_reactions = fda_sig.get("top_reactions", [])
        has_fda_matches = False
        
        # Extract symptoms list to cross-reference
        symptoms = case_data.get("symptoms", []) or case_data.get("drug_entities", []) or []
        for sym in symptoms:
            if sym.title() in [rx.title() for rx in top_reactions]:
                has_fda_matches = True
                break
                
        if has_fda_matches or fda_sig.get("fda_signal_score", "Low") in ["Moderate", "High"]:
            reasons.append("Known FDA adverse reaction")
        else:
            reasons.append("Temporal association present")

        # Check dechallenge / rechallenge info
        drug_recur = events.get("drug_recur_action", "")
        if drug_recur and any(w in drug_recur.lower() for w in ["reappeared", "recurred", "rechallenge", "positive"]):
            reasons.append("Positive rechallenge observed")
        elif "dechallenge" in str(causality).lower() and "positive" in str(causality).lower():
            reasons.append("Positive dechallenge observed")
        else:
            reasons.append("Temporal relationship exists")

        # Check suspect relationship strength
        relationship = causality.get("suspected_relationship") or causality.get("causality_score")
        if relationship and str(relationship).lower() in ["certain", "probable", "highly likely", "high"]:
            reasons.append("Strong suspect relationship strength")
        elif relationship and str(relationship).lower() in ["possible", "moderate"]:
            reasons.append("Possible suspect drug association")
        else:
            reasons.append("Requires clinical validation and tracking")

        return reasons

    def get_reasoning_explanations(self, case_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Returns reasoning explanations dictionary containing both causality and seriousness lists.
        """
        return {
            "causality": self.explain_causality(case_data),
            "seriousness": self.explain_seriousness(case_data)
        }

reasoning_service = ReasoningService()
