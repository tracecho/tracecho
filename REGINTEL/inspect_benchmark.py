import json

with open("regintel/evaluation/benchmark.json", encoding="utf-8") as f:
    benchmark = json.load(f)

for q in benchmark:
    print("=" * 100)
    print("ID:", q["id"])
    print("Regulator:", q["regulator"], "| Temporal:", q["temporal_type"])
    print("Date range:", q["temporal_start"], "-", q["temporal_end"])
    print("Answerable:", q["answerable"])
    print("Question:", q["question"])
    print("Documents:", q["expected_document_ids"])
    print("Chunks:", q["expected_chunk_ids"])
