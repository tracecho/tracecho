import os
import pandas as pd
import json

from retrieval.embeddings import RegintelEmbeddings
from retrieval.vector_store import RegintelVectorStore
from retrieval.bm25 import RegintelBM25Store
from retrieval.hybrid_search import RegintelHybridRetriever
from retrieval.metadata_store import MetadataStore
from evaluation.retrieval_metrics import evaluate_retrieval

def build_indexes():
    sebi_df = pd.read_parquet(r"d:\REGINTEL\regintel\data\processed\sebi_chunks.parquet")
    rbi_df = pd.read_parquet(r"d:\REGINTEL\regintel\data\processed\rbi_chunks.parquet")
    
    # Combined for indexing
    df = pd.concat([sebi_df, rbi_df], ignore_index=True)
    df.set_index('chunk_id', inplace=True, drop=False)
    
    print(f"Total chunks to index: {len(df)}")
    texts = df['text'].tolist()
    chunk_ids = df['chunk_id'].tolist()
    
    emb_model = RegintelEmbeddings()
    embeddings = emb_model.embed_documents(texts)
    
    vs = RegintelVectorStore()
    vs.build_index(embeddings, chunk_ids)
    print("FAISS Index Built")
    
    bs = RegintelBM25Store()
    bs.build_index(texts, chunk_ids)
    print("BM25 Index Built")

def load_system():
    emb_model = RegintelEmbeddings()
    vs = RegintelVectorStore()
    vs.load()
    bs = RegintelBM25Store()
    bs.load()
    ms = MetadataStore()
    if not ms.load():
        ms.build_store()
    
    retriever = RegintelHybridRetriever(emb_model, vs, bs, ms)
    return retriever

def test_queries(retriever):
    test_queries = [
        "What are the KYC requirements applicable to NBFCs?",
        "Regulations around digital banking interfaces.",
        "SEBI guidelines for mutual funds investments.",
        "Investor protection rules by SEBI.",
        "Fraud detection and cybersecurity framework for banks.",
        "What is the applicability of the Master Direction on NBFCs?",
        "Historical regulations for Mutual Funds before 2022.",
        "What are the rules for Investment Advisers?",
        "KYC norms for digital payment systems.",
        "When does a SEBI superseding circular take effect?",
        "Regulations regarding fraud reporting by commercial banks."
    ]
    
    print("\n--- SAMPLE QUERIES ---")
    for q in test_queries:
        print(f"\nQUERY: {q}")
        res = retriever.search(q, alpha=0.5, k=3)
        for r in res:
            print(f"  [{r['chunk_id']}] Type: {r['document_type']}, valid: {r['validity_status']}, Score: {r['hybrid_score']:.3f}")
            print(f"  Text: {r['text'][:100]}...")

def evaluate(retriever):
    print("\n--- EVALUATION ---")
    queries_path = r"d:\REGINTEL\regintel\evaluation\golden_queries.json"
    if not os.path.exists(queries_path):
        print(f"Evaluation file not found: {queries_path}")
        return
        
    with open(queries_path, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
        
    if test_cases:
        results = evaluate_retrieval(retriever, test_cases)
        for method, metrics in results.items():
            print(f"{method}: {metrics}")

if __name__ == '__main__':
    # Checking if index exists
    if not os.path.exists("d:/REGINTEL/regintel/data/processed/faiss_index.bin"):
        build_indexes()
        
    retriever = load_system()
    test_queries(retriever)
    evaluate(retriever)
