import json
from pathlib import Path

p = Path("data/evaluation/results/evaluation_detailed_20260831_203101.json")
data = json.loads(p.read_text(encoding="utf-8"))

for method, records in data.items():
    rows = [r for r in records if r.get("answerable")]
    n = len(rows)
    hits = 0
    rr_total = 0.0
    mismatches = 0

    for r in rows:
        expected = set(r.get("expected_chunk_ids") or [])
        retrieved = r.get("retrieved_chunk_ids") or []
        ranks = [i for i, c in enumerate(retrieved, 1) if c in expected]
        rank = min(ranks) if ranks else None
        hit = rank is not None and rank <= 5
        hits += int(hit)
        rr_total += 1 / rank if rank is not None else 0
        mismatches += int(r.get("hit_at_5") != hit)

    print(f"{method}: HitRate@5={hits}/{n}, MRR={rr_total/n if n else 0:.3f}, mismatches={mismatches}")
