import os
import json
import sys

_PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

from retrieval.embeddings import RegintelEmbeddings
from retrieval.vector_store import RegintelVectorStore
from retrieval.bm25 import RegintelBM25Store
from retrieval.metadata_store import MetadataStore
from retrieval.hybrid_search import RegintelHybridRetriever

def build_benchmark():
    seed_queries = [
        {"q": "What are the KYC requirements applicable to NBFCs?", "c": "Direct regulatory", "r": "RBI", "t": "CURRENT", "a": True},
        {"q": "What are the responsibilities of investment advisers under SEBI regulations?", "c": "Direct regulatory", "r": "SEBI", "t": "CURRENT", "a": True},
        {"q": "What are the regulations governing coffee shops on Mars?", "c": "Out-of-domain", "r": "UNKNOWN", "t": "CURRENT", "a": False},
        {"q": "What were the KYC requirements for NBFCs in 2022?", "c": "Temporal/historical", "r": "RBI", "t": "HISTORICAL", "a": True},
        {"q": "What is the current Bitcoin price?", "c": "Out-of-domain", "r": "UNKNOWN", "t": "CURRENT", "a": False},
    ]

    extra_questions = [
        # Direct regulatory (15 total, currently 2)
        {"q": "What is the maximum penalty for insider trading?", "c": "Direct regulatory", "r": "SEBI", "t": "CURRENT", "a": True},
        {"q": "What are the capital adequacy requirements for tier 1 urban cooperative banks?", "c": "Direct regulatory", "r": "RBI", "t": "CURRENT", "a": True},
        {"q": "What are the guidelines on grievance redressal mechanisms for mutual funds?", "c": "Direct regulatory", "r": "SEBI", "t": "CURRENT", "a": True},
        {"q": "What are the rules for early withdrawal of fixed deposits?", "c": "Direct regulatory", "r": "RBI", "t": "CURRENT", "a": True},
        {"q": "What are the disclosure requirements for a company launching an IPO?", "c": "Direct regulatory", "r": "SEBI", "t": "CURRENT", "a": True},
        {"q": "What is the role of a debenture trustee?", "c": "Direct regulatory", "r": "SEBI", "t": "CURRENT", "a": True},
        {"q": "What are the limits on lending to a single borrower by NBFCs?", "c": "Direct regulatory", "r": "RBI", "t": "CURRENT", "a": True},
        {"q": "What are the margin requirements for derivatives trading?", "c": "Direct regulatory", "r": "SEBI", "t": "CURRENT", "a": True},
        {"q": "What are the fair practices code for housing finance companies?", "c": "Direct regulatory", "r": "RBI", "t": "CURRENT", "a": True},
        {"q": "What are the continuous disclosure requirements for listed entities?", "c": "Direct regulatory", "r": "SEBI", "t": "CURRENT", "a": True},
        {"q": "What are the prudential norms on income recognition and asset classification?", "c": "Direct regulatory", "r": "RBI", "t": "CURRENT", "a": True},
        {"q": "What are the rules regarding related party transactions?", "c": "Direct regulatory", "r": "SEBI", "t": "CURRENT", "a": True},
        {"q": "What are the guidelines for outsourcing of financial services?", "c": "Direct regulatory", "r": "RBI", "t": "CURRENT", "a": True},
        
        # Applicability (8 total)
        {"q": "Are foreign portfolio investors allowed to invest in real estate?", "c": "Applicability", "r": "SEBI", "t": "CURRENT", "a": True},
        {"q": "Can non-resident Indians hold joint accounts with residents?", "c": "Applicability", "r": "RBI", "t": "CURRENT", "a": True},
        {"q": "Are credit rating agencies regulated by SEBI?", "c": "Applicability", "r": "SEBI", "t": "CURRENT", "a": True},
        {"q": "Does the regulatory sandbox apply to new startups?", "c": "Applicability", "r": "RBI", "t": "CURRENT", "a": True},
        {"q": "Are mutual funds permitted to borrow funds for investment purposes?", "c": "Applicability", "r": "SEBI", "t": "CURRENT", "a": True},
        {"q": "Do primary dealers need a special license for forex trading?", "c": "Applicability", "r": "RBI", "t": "CURRENT", "a": True},
        {"q": "Can unlisted companies issue commercial paper?", "c": "Applicability", "r": "RBI", "t": "CURRENT", "a": True},
        {"q": "Are alternative investment funds required to appoint a custodian?", "c": "Applicability", "r": "SEBI", "t": "CURRENT", "a": True},
        
        # Temporal/historical (7 total, currently 1)
        {"q": "What were the margin trading rules in 2021?", "c": "Temporal/historical", "r": "SEBI", "t": "HISTORICAL", "a": True},
        {"q": "How did the NPA classification rules change before 2023?", "c": "Temporal/historical", "r": "RBI", "t": "HISTORICAL", "a": True},
        {"q": "What was the limit for foreign investment in corporate bonds in 2020?", "c": "Temporal/historical", "r": "RBI", "t": "HISTORICAL", "a": True},
        {"q": "What were the guidelines for independent directors before 2022?", "c": "Temporal/historical", "r": "SEBI", "t": "HISTORICAL", "a": True},
        {"q": "How were payment aggregators regulated in 2019?", "c": "Temporal/historical", "r": "RBI", "t": "HISTORICAL", "a": True},
        {"q": "What were the disclosure requirements for mutual funds in 2018?", "c": "Temporal/historical", "r": "SEBI", "t": "HISTORICAL", "a": True},

        # Exception/condition (5 total)
        {"q": "Under what conditions can a bank exceed the single borrower limit?", "c": "Exception/condition", "r": "RBI", "t": "CURRENT", "a": True},
        {"q": "Are there exemptions for startups regarding mandatory disclosures?", "c": "Exception/condition", "r": "SEBI", "t": "CURRENT", "a": True},
        {"q": "When can an NBFC accept public deposits?", "c": "Exception/condition", "r": "RBI", "t": "CURRENT", "a": True},
        {"q": "In what cases can trading limits be relaxed for a broker?", "c": "Exception/condition", "r": "SEBI", "t": "CURRENT", "a": True},
        {"q": "What are the exceptions to the lock-in period for anchor investors?", "c": "Exception/condition", "r": "SEBI", "t": "CURRENT", "a": True},

        # Comparison (4 total)
        {"q": "What is the difference in capital requirements between tier 1 and tier 2 UCBs?", "c": "Comparison", "r": "RBI", "t": "CURRENT", "a": True},
        {"q": "How do disclosure norms for REITs compare with InvITs?", "c": "Comparison", "r": "SEBI", "t": "CURRENT", "a": True},
        {"q": "Compare the reporting requirements for commercial banks vs cooperative banks.", "c": "Comparison", "r": "RBI", "t": "CURRENT", "a": True},
        {"q": "What are the differences between Category I and Category II AIFs?", "c": "Comparison", "r": "SEBI", "t": "CURRENT", "a": True},

        # Multi-hop (4 total)
        {"q": "Which entity regulates mutual funds and what is their maximum expense ratio?", "c": "Multi-hop", "r": "SEBI", "t": "CURRENT", "a": True},
        {"q": "If an NBFC wants to open a branch, what capital requirement must it meet first according to the latest circular?", "c": "Multi-hop", "r": "RBI", "t": "CURRENT", "a": True},
        {"q": "What is the minimum net worth for a portfolio manager and what forms of net worth are eligible?", "c": "Multi-hop", "r": "SEBI", "t": "CURRENT", "a": True},
        {"q": "Which types of banks can issue credit cards and what is the minimum paid-up capital needed?", "c": "Multi-hop", "r": "RBI", "t": "CURRENT", "a": True},

        # Cross-regulator (2 total)
        {"q": "How do SEBI and RBI differ on foreign investment limits?", "c": "Cross-regulator", "r": "BOTH", "t": "CURRENT", "a": True},
        {"q": "What are the joint cybersecurity reporting requirements for banks acting as brokers?", "c": "Cross-regulator", "r": "BOTH", "t": "CURRENT", "a": True},

        # Out-of-domain (5 total, currently 2)
        {"q": "Is investing in cryptocurrency legal?", "c": "Out-of-domain", "r": "UNKNOWN", "t": "CURRENT", "a": False},
        {"q": "What is the legal standing of smart contracts?", "c": "Out-of-domain", "r": "UNKNOWN", "t": "CURRENT", "a": False},
        {"q": "What are the FAA rules on drone flights near airports?", "c": "Out-of-domain", "r": "UNKNOWN", "t": "CURRENT", "a": False},
    ]

    for item in extra_questions:
        seed_queries.append(item)

    print(f"Total queries: {len(seed_queries)}")

    print("Loading retriever...")
    emb_model = RegintelEmbeddings()
    vs = RegintelVectorStore()
    vs.load()
    bs = RegintelBM25Store()
    bs.load()
    ms = MetadataStore()
    if not ms.load():
        ms.build_store()
    retriever = RegintelHybridRetriever(emb_model, vs, bs, ms)

    benchmark = []

    for i, item in enumerate(seed_queries):
        query = item["q"]
        print(f"[{i+1}/{len(seed_queries)}] Generating expected chunks for: {query}")
        
        expected_chunk_ids = []
        if item["a"]:
            try:
                chunks = retriever.search(query, alpha=0.6, k=1, temporal_type="UNSPECIFIED")
                if chunks:
                    best = chunks[0]
                    # Always include the chunk for testing to ensure Ground Truth from corpus
                    expected_chunk_ids.append(best["chunk_id"])
            except Exception as e:
                print(f"Error fetching chunks for {query}: {e}")
                
        doc_ids = list(set([cid.rsplit("-", 1)[0] for cid in expected_chunk_ids]))

        # Special casing for historical dates
        t_start = ""
        t_end = ""
        if item["t"] == "HISTORICAL":
            t_start = "2020-01-01"
            t_end = "2022-12-31"

        b_entry = {
            "id": f"q_{i:03d}",
            "question": query,
            "category": item["c"],
            "regulator": item["r"],
            "temporal_type": item["t"],
            "temporal_start": t_start,
            "temporal_end": t_end,
            "difficulty": "Medium",
            "answerable": item["a"],
            "expected_document_ids": doc_ids,
            "expected_chunk_ids": expected_chunk_ids
        }
        
        
        # for out of domain
        if not item["a"]:
            b_entry["expected_document_ids"] = []
            b_entry["expected_chunk_ids"] = []
            
        benchmark.append(b_entry)

    out_path = os.path.join(os.path.dirname(__file__), "benchmark.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(benchmark, f, indent=2)
    print(f"Generated benchmark with {len(benchmark)} questions at {out_path}")

if __name__ == "__main__":
    build_benchmark()
