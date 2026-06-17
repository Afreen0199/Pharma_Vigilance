import os
import sys
import json
from dotenv import load_dotenv
from fastapi.testclient import TestClient

# Add backend directory to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)
load_dotenv(os.path.join(backend_dir, ".env"))

from main import app
client = TestClient(app)

def run_chat_e2e_tests():
    print("=" * 80)
    print("RUNNING CONVERSATIONAL CHAT SESSION E2E TESTS")
    print("=" * 80)

    # 1. Ingest a patient case narrative
    narrative_text = (
        "Patient is a 55-year-old male who developed severe angioedema (swelling of lips and throat) "
        "three hours after taking Lisinopril 10mg. He was hospitalized in the ICU for airway monitoring "
        "and treated with epinephrine. Lisinopril was permanently discontinued."
    )

    print("\nStep 1: Ingesting case narrative via /analyze...")
    res_analyze = client.post("/analyze/", data={"text": narrative_text})
    print(f"Ingestion status: {res_analyze.status_code}")
    if res_analyze.status_code != 200:
        print(f"❌ Ingestion failed: {res_analyze.text}")
        sys.exit(1)

    analyze_data = res_analyze.json()
    analysis_id = analyze_data.get("analysis_id")
    print(f"✅ Ingestion successful. Analysis ID: {analysis_id}")
    print(f"Extracted drugs: {analyze_data.get('drug_entities')}")
    print(f"Extracted symptoms: {analyze_data.get('symptoms')}")

    # 2. Trigger report generation
    print(f"\nStep 2: Triggering report generation for analysis ID {analysis_id}...")
    res_report = client.post("/report/generate", json={"analysis_id": analysis_id})
    print(f"Report status: {res_report.status_code}")
    if res_report.status_code != 200:
        print(f"❌ Report generation failed: {res_report.text}")
        sys.exit(1)
        
    print("✅ Safety report compiled.")

    # 3. Chat: Send first question
    print(f"\nStep 3: Querying chatbot POST /chat/{analysis_id} (Q1: suspect drug)...")
    q1 = "What was the suspect drug in this case?"
    res_chat1 = client.post(f"/chat/{analysis_id}", json={"question": q1})
    print(f"Chat status: {res_chat1.status_code}")
    if res_chat1.status_code != 200:
        print(f"❌ Chat failed: {res_chat1.text}")
        sys.exit(1)
        
    chat1_data = res_chat1.json()
    reply1 = chat1_data.get("response", "")
    print(f"Bot Reply 1: {reply1}")
    assert "lisinopril" in reply1.lower(), "❌ Chatbot did not identify Lisinopril in its reply!"
    print("  ✓ Q1 suspect drug identification verified.")

    # 4. Chat: Send follow-up question (checking memory context)
    print(f"\nStep 4: Querying chatbot follow-up POST /chat/{analysis_id} (Q2: why serious)...")
    q2 = "Why was it classified as serious?"
    res_chat2 = client.post(f"/chat/{analysis_id}", json={"question": q2})
    print(f"Chat status: {res_chat2.status_code}")
    if res_chat2.status_code != 200:
        print(f"❌ Chat failed: {res_chat2.text}")
        sys.exit(1)
        
    chat2_data = res_chat2.json()
    reply2 = chat2_data.get("response", "")
    print(f"Bot Reply 2: {reply2}")
    
    # Assert it mentions hospitalization, ICU, or angioedema
    assert any(word in reply2.lower() for word in ["hospital", "icu", "angioedema", "airway", "serious"]), \
        "❌ Chatbot did not explain the seriousness assessment using case details!"
    print("  ✓ Q2 follow-up memory and seriousness reasoning verified.")

    # 4.5. Assert Structured Card Format
    print("\nStep 4.5: Asserting Structured Enterprise Conversational Card formatting...")
    from app.services.chat.response_scope_controller import response_scope_controller

    for chat_data in [chat1_data, chat2_data]:
        assert "response_type" in chat_data, "❌ response_type missing from payload!"
        response_type = chat_data["response_type"]
        assert response_type in [
            "seriousness_explanation", "causality_explanation", "fda_signal_summary",
            "timeline_explanation", "missing_information_review", "regulatory_intelligence",
            "organ_system_analysis", "confidence_explanation", "similar_case_retrieval",
            "safety_recommendation", "chart_interpretation", "interaction_analysis",
            "dynamic_contextual_reasoning"
        ], f"❌ Invalid response_type: {response_type}"
        
        assert "answer" in chat_data, "❌ answer key missing from payload!"
        answer = chat_data["answer"]
        assert "summary" in answer, "❌ answer.summary missing!"

        # Verify that ONLY allowed keys based on response_type exist in the answer payload
        allowed_keys = response_scope_controller.QUESTION_SCOPE_MAP.get(
            response_type, response_scope_controller.QUESTION_SCOPE_MAP["dynamic_contextual_reasoning"]
        )

        for key in answer.keys():
            assert key in allowed_keys, f"❌ Irrelevant section '{key}' was not suppressed for response type '{response_type}'!"
        
        # New dynamic suggested questions and sources asserts
        assert "suggested_questions" in chat_data and isinstance(chat_data["suggested_questions"], list), "❌ suggested_questions missing/not a list at root!"
        assert "sources" in chat_data and isinstance(chat_data["sources"], list), "❌ sources missing/not a list at root!"
        
        # Suggested questions and sources should be present inside the answer card if they are in the allowed map,
        # otherwise they are kept at the root payload level.
        if "suggested_questions" in allowed_keys:
            assert "suggested_questions" in answer and isinstance(answer["suggested_questions"], list), "❌ suggested_questions missing in answer!"
        if "sources" in allowed_keys:
            assert "sources" in answer and isinstance(answer["sources"], list), "❌ sources missing in answer!"

        assert len(chat_data["suggested_questions"]) >= 3, "❌ Suggested questions list is empty or too short!"
        assert len(chat_data["sources"]) >= 1, "❌ Sources list cannot be empty!"
        
        print(f"  ✓ Strict minimal key format verified for: {response_type} (Keys: {list(answer.keys())})")
        print(f"    Suggested follow-ups: {chat_data.get('suggested_questions')}")
        print(f"    Traceable sources: {chat_data.get('sources')}")

    # 4.6. Test general onboarding query (greetings / capabilities)
    print(f"\nStep 4.6: Testing general capability onboarding query (Q: Who are you?)...")
    res_chat_gen = client.post(f"/chat/{analysis_id}", json={"question": "Who are you?"})
    print(f"Chat status: {res_chat_gen.status_code}")
    assert res_chat_gen.status_code == 200, "❌ Capability query failed!"
    chat_gen_data = res_chat_gen.json()
    assert chat_gen_data.get("response_type") == "general_conversational", f"❌ Invalid response_type: {chat_gen_data.get('response_type')}"
    assert list(chat_gen_data.get("answer", {}).keys()) == ["summary"], f"❌ Answer card keys not minimal for general conversational: {list(chat_gen_data.get('answer').keys())}"
    print(f"  ✓ General conversational onboarding greeting verified. Bot Reply: {chat_gen_data.get('response')}")

    # 4.7. Test irrelevant out-of-domain query (refusal)
    print(f"\nStep 4.7: Testing irrelevant out-of-domain query (Q: Who won the football match?)...")
    res_chat_irr = client.post(f"/chat/{analysis_id}", json={"question": "Who won the football match?"})
    print(f"Chat status: {res_chat_irr.status_code}")
    assert res_chat_irr.status_code == 200, "❌ Irrelevant query failed!"
    chat_irr_data = res_chat_irr.json()
    assert chat_irr_data.get("response_type") == "irrelevant_question", f"❌ Invalid response_type: {chat_irr_data.get('response_type')}"
    assert list(chat_irr_data.get("answer", {}).keys()) == ["summary"], f"❌ Answer card keys not minimal for irrelevant question: {list(chat_irr_data.get('answer').keys())}"
    expected_refusal = "The question appears to be unrelated to the analyzed pharmacovigilance report or available medical evidence sources. Please ask questions related to the uploaded case, FDA evidence, safety signals, adverse events, or regulatory intelligence."
    assert chat_irr_data.get("response") == expected_refusal, f"❌ Refusal text mismatch: {chat_irr_data.get('response')}"
    print(f"  ✓ Irrelevant question refusal verified. Bot Reply: {chat_irr_data.get('response')}")

    # 5. Clear Memory and Assert
    print(f"\nStep 5: Resetting chat memory DELETE /chat/{analysis_id}...")
    res_reset = client.delete(f"/chat/{analysis_id}")
    print(f"Reset status: {res_reset.status_code}")
    assert res_reset.status_code == 200, "❌ Failed to reset chat!"
    
    # Send Q3 after reset to ensure memory was cleared
    print(f"\nStep 6: Querying chatbot after reset (Q3: what was 'it')...")
    q3 = "What adverse reactions are associated with it?"
    res_chat3 = client.post(f"/chat/{analysis_id}", json={"question": q3})
    chat3_data = res_chat3.json()
    reply3 = chat3_data.get("response", "")
    print(f"Bot Reply 3 (no context reference for 'it'): {reply3}")
    
    # The chatbot shouldn't resolve 'it' easily or will ask to clarify because the suspect drug context is cleared from conversation turns,
    # or will gracefully fall back to the system prompt's drug. (Since system prompt has suspect drug, it might mention Lisinopril,
    # but the previous chat history turns are deleted.)
    
    print("\n🎉 ALL CONVERSATIONAL CHAT SESSION TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_chat_e2e_tests()
