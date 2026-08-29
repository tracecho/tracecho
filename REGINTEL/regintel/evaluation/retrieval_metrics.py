def calc_mrr(retrieved_ids, target_ids):
    for i, rid in enumerate(retrieved_ids):
        if rid in target_ids:
            return 1.0 / (i + 1)
    return 0.0

def calc_recall(retrieved_ids, target_ids, k):
    ret_k = retrieved_ids[:k]
    hits = sum(1 for rid in ret_k if rid in target_ids)
    return hits / len(target_ids) if target_ids else 0.0

def evaluate_retrieval(retriever, test_cases):
    """
    test_cases: dict mapping query -> list of relevant chunk_ids
    """
    results = {
        "FAISS_Only": {"MRR": 0, "Recall@5": 0, "Recall@10": 0},
        "BM25_Only":  {"MRR": 0, "Recall@5": 0, "Recall@10": 0},
        "Hybrid":     {"MRR": 0, "Recall@5": 0, "Recall@10": 0}
    }
    
    n = len(test_cases)
    if n == 0: return results
    
    for q, targets in test_cases.items():
        # FAISS
        faiss_res = retriever.search(q, alpha=1.0, k=10) # 1.0 = Pure Vector
        f_ids = [r['chunk_id'] for r in faiss_res]
        results['FAISS_Only']['MRR'] += calc_mrr(f_ids, targets)
        results['FAISS_Only']['Recall@5'] += calc_recall(f_ids, targets, 5)
        results['FAISS_Only']['Recall@10'] += calc_recall(f_ids, targets, 10)
        
        # BM25
        bm25_res = retriever.search(q, alpha=0.0, k=10) # 0.0 = Pure BM25
        b_ids = [r['chunk_id'] for r in bm25_res]
        results['BM25_Only']['MRR'] += calc_mrr(b_ids, targets)
        results['BM25_Only']['Recall@5'] += calc_recall(b_ids, targets, 5)
        results['BM25_Only']['Recall@10'] += calc_recall(b_ids, targets, 10)
        
        # Hybrid
        hybrid_res = retriever.search(q, alpha=0.5, k=10)
        h_ids = [r['chunk_id'] for r in hybrid_res]
        results['Hybrid']['MRR'] += calc_mrr(h_ids, targets)
        results['Hybrid']['Recall@5'] += calc_recall(h_ids, targets, 5)
        results['Hybrid']['Recall@10'] += calc_recall(h_ids, targets, 10)
        
    for k in results:
        results[k]['MRR'] /= n
        results[k]['Recall@5'] /= n
        results[k]['Recall@10'] /= n
        
    return results
