import logging
from app.services.llm_service import llm_service_instance

logger = logging.getLogger(__name__)

class QuestionDomainClassifier:
    def classify_domain(self, question: str) -> str:
        """
        Classifies the incoming question into one of:
        - 'greeting'
        - 'capability_question'
        - 'pharmacovigilance_question'
        - 'irrelevant_question'
        """
        q_clean = question.strip().lower()
        if q_clean.endswith('?'):
            q_clean = q_clean[:-1].strip()

        # 1. Quick regex heuristics for greetings
        greetings = [
            "hi", "hello", "hey", "howdy", "greetings", "good morning", 
            "good afternoon", "good evening", "how are you", "how's it going",
            "yo", "hi there", "hello there"
        ]
        if q_clean in greetings:
            return "greeting"

        # 2. Quick regex heuristics for capability questions
        capabilities = [
            "who are you", "what are you", "what can you do", "what do you do", 
            "explain your capabilities", "how does this platform work", 
            "how do you work", "what is your purpose", "how to use this",
            "capabilities"
        ]
        if q_clean in capabilities or any(c in q_clean for c in ["what can you do", "who are you", "explain your capabilities", "how does this platform work"]):
            return "capability_question"

        # 3. LLM-based classification fallback for robust handling
        prompt = f"""You are a query classifier for a Pharmacovigilance safety copilot.
Classify the user's question into exactly one of these categories:
- 'greeting': Simple conversational salutations (e.g. "Hi", "Hello", "Hey", "How are you").
- 'capability_question': Questions about the safety chatbot's capabilities, identity, or how this medical platform works (e.g. "Who are you?", "What can you do?", "Explain your features").
- 'pharmacovigilance_question': Queries about patient cases, medical reports, adverse drug reactions, safety timelines, drug causality, seriousness assessment, FDA event database signals, local FAERS datasets, or regulatory warning guidelines.
- 'irrelevant_question': Questions completely unrelated to medicine, pharmacovigilance, cases, or the chatbot's system capabilities (e.g. technical coding questions, writing code, sports scores, finance/crypto, jokes, math problems, general knowledge).

User Question: "{question}"

Output only the category name in lowercase: 'greeting', 'capability_question', 'pharmacovigilance_question', or 'irrelevant_question'. Do not include explanation or markdown formatting.
"""
        try:
            config = {"run_name": "question_domain_classifier"}
            if hasattr(llm_service_instance, 'langfuse_handler') and llm_service_instance.langfuse_handler:
                config["callbacks"] = [llm_service_instance.langfuse_handler]
                
            response = llm_service_instance.llm.invoke(prompt, config=config)
            decision = response.content.strip().lower().replace("'", "").replace('"', "")
            if decision in ["greeting", "capability_question", "pharmacovigilance_question", "irrelevant_question"]:
                return decision
            
            # Simple heuristic backup in case LLM outputs excess text
            if any(cat in decision for cat in ["greeting", "capability", "pharmacovigilance", "irrelevant"]):
                for cat in ["greeting", "capability_question", "pharmacovigilance_question", "irrelevant_question"]:
                    if cat.split('_')[0] in decision:
                        return cat
            
            # Catchall based on keyword filtering
            if any(w in q_clean for w in ["code", "python", "javascript", "football", "bitcoin", "crypto", "price", "weather", "news", "movie", "song", "joke"]):
                return "irrelevant_question"
            return "pharmacovigilance_question"
        except Exception as e:
            logger.error(f"Error in LLM domain classification: {e}")
            return "pharmacovigilance_question"

question_domain_classifier = QuestionDomainClassifier()
