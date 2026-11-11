import json
import requests
from datetime import datetime
from pathlib import Path

benchmark = Path("regintel/evaluation/benchmark.json")
output = Path("result_ood.json")
api_url = "http://127.0.0.1:8000/api/ask"

with benchmark.open(encoding="utf-8") as f:
    questions = json.load(f)

ood = [q for q in questions if q.get("answerable") is False]
results = []

print(f"Testing {len(ood)} OOD questions...")

for q in ood:
    print(f"\n{q['id']}: {q['question']}")
    try:
        response = requests.post(
            api_url,
            json={"query": q["question"]},
            timeout=120
        )
        try:
            answer = response.json()
        except ValueError:
            answer = response.text

        answer_text = json.dumps(answer, ensure_ascii=False).lower()
        refusal_terms = [
            "insufficient evidence", "cannot answer",
            "can't answer", "outside my scope",
            "out of scope", "not enough information",
            "unable to answer", "no relevant information"
        ]
        refusal_detected = any(term in answer_text for term in refusal_terms)

        results.append({
            "id": q["id"],
            "question": q["question"],
            "http_status": response.status_code,
            "answer": answer,
            "refusal_detected": refusal_detected,
            "refusal_check_pass": response.ok and refusal_detected
        })
        print(f"HTTP: {response.status_code} | Refusal detected: {refusal_detected}")
    except Exception as e:
        results.append({
            "id": q["id"],
            "question": q["question"],
            "error": str(e),
            "refusal_detected": False,
            "refusal_check_pass": False
        })
        print(f"ERROR: {e}")

tested = len(results)
passed = sum(r.get("refusal_check_pass", False) for r in results)

report = {
    "run_at": datetime.now().isoformat(),
    "test_type": "OOD refusal smoke test",
    "total_questions": tested,
    "refusal_checks_passed": passed,
    "preliminary_refusal_rate_percent": round(100 * passed / tested, 2) if tested else 0,
    "note": "Keyword-based preliminary check only; inspect answers before treating this as a valid refusal score.",
    "results": results
}

output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nDONE: {passed}/{tested} preliminary refusal checks passed.")
print(f"Saved to: {output.resolve()}")

