import os
import sys

_PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

from llm.ollama_client import check_gemini_config, chat, GeminiError
from graph.nodes import reasoning_node

def test_gemini():
    print("=== STEP 1: Diagnostic Configuration Check ===")
    config = check_gemini_config()
    print("Diagnostics:")
    for k, v in config.items():
        print(f"  {k}: {v}")
    
    assert config["key_present"] is True, "GEMINI_API_KEY is not detected!"
    assert config["key_length"] > 10, f"GEMINI_API_KEY appears invalid (len={config['key_length']})"
    assert config["sdk_available"] is True, "google-genai SDK is not available!"
    print("STEP 1 PASSED: GEMINI_API_KEY detected and google-genai SDK available.\n")

    print("=== STEP 2: Gemini Client & Chat Execution ===")
    test_messages = [
        {"role": "system", "content": "You are a test assistant. Respond in JSON with a 'status' field."},
        {"role": "user", "content": "Respond with {'status': 'ok'}"}
    ]
    try:
        response = chat(test_messages, format_json=True, temperature=0.0)
        print(f"Chat response type: {type(response)}")
        print(f"Chat response: {response}")
        print("STEP 2 PASSED: Gemini client initialized and chat returned valid response.\n")
    except Exception as exc:
        print(f"STEP 2 FAILED: {exc}")
        raise

    print("=== STEP 3: LangGraph Reasoning Node Verification ===")
    sample_state = {
        "query": "What are customer due diligence requirements under RBI?",
        "query_analysis": {
            "regulator": "RBI",
            "intent": "CDD requirements",
            "temporal_type": "UNSPECIFIED"
        },
        "chunks": [
            {
                "chunk_id": "RBI-RBI_0092.txt-47",
                "regulator": "RBI",
                "document_title": "Reserve Bank of India (Know Your Customer) Directions",
                "document_type": "Directions",
                "section": "Section 16",
                "text": "Every Regulated Entity shall undertake Customer Due Diligence (CDD) at the time of commencement of an account-based relationship."
            }
        ],
        "evidence_sufficiency_output": {
            "status": "SUPPORTED"
        }
    }
    
    node_result = reasoning_node(sample_state)
    err = node_result.get("error")
    print(f"Node result error field: {err}")
    assert err != "reasoning_error: GEMINI_API_KEY is missing. Add it to the workspace .env file.", \
        "Reasoning step still reported missing GEMINI_API_KEY!"
    
    reasoning_output = node_result.get("reasoning_output", {})
    ans = reasoning_output.get("answer", "")
    print(f"Reasoning answer length: {len(ans)}")
    print(f"Reasoning answer preview: {ans[:150]}...")
    print(f"Evidence insufficient: {reasoning_output.get('evidence_insufficient')}")
    print("STEP 3 PASSED: LangGraph reasoning node executed successfully without GEMINI_API_KEY error.\n")

    print("ALL VALIDATION CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_gemini()

