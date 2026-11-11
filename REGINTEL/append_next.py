import json
import requests
from pathlib import Path
from datetime import datetime

path = Path("result_ood.json")
data = json.loads(path.read_text(encoding="utf-8-sig"))
benchmark = json.loads(Path("regintel/evaluation/benchmark.json").read_text(encoding="utf-8-sig"))
existing = {r["id"] for r in data.get("results", [])}

for q in benchmark:
    if q["id"] not in ["q_011", "q_012", "q_013"] or q["id"] in existing:
        continue
    print(f'Testing {q["id"]}: {q["question"]}')
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/ask",
            json={"query": q["question"]},
            timeout=120
        )
        try:
            answer = response.json()
        except ValueError:
            answer = {"answer": response.text}
        result = {
            "id": q["id"],
            "question": q["question"],
            "http_status": response.status_code,
            "answer": answer
        }
        data["results"].append(result)
        print("HTTP:", response.status_code)
    except Exception as e:
        print("ERROR:", e)

data["total_questions"] = len(data["results"])
data["run_at"] = datetime.now().isoformat()
data["test_type"] = "Cumulative question test"
path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f'\nSaved {len(data["results"])} total results to {path.resolve()}')
