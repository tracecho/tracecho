import pandas as pd
import numpy as np

class RegintelHybridRetriever:
    def __init__(self, embeddings_model, vector_store, bm25_store, metadata_store):
        self.embeddings = embeddings_model
        self.vector_store = vector_store
        self.bm25_store = bm25_store
        self.metadata_store = metadata_store # dictionary lookup

        
    def _normalize_scores(self, results):
        if not results: return {}
        scores = [score for _, score in results]
        max_s = max(scores)
        norm_map = {}
        for chunk_id, score in results:
            if max_s <= 0:
                norm_map[chunk_id] = 0.0
            else:
                norm_map[chunk_id] = score / max_s
        return norm_map

    def search(self, query, alpha=0.5, k=10, filters=None):
        query_emb = self.embeddings.embed_query(query)
        
        dense_results = self.vector_store.search(query_emb, k=max(k*3, 50))
        sparse_results = self.bm25_store.search(query, k=max(k*3, 50))
        
        dense_raw = {cid: sc for cid, sc in dense_results}
        sparse_raw = {cid: sc for cid, sc in sparse_results}
        
        dense_norm = self._normalize_scores(dense_results)
        sparse_norm = self._normalize_scores(sparse_results)
        
        query_lower = query.lower()
        entities = ['ucb', 'urban co-operative', 'payments bank', 'nbfc', 'co-operative bank', 'rrb', 'regional rural bank']
        has_specific_entity = any(e in query_lower for e in entities)
        is_historical = any(w in query_lower for w in ['historical', 'superseded', 'past', 'previously', 'old'])

        combined_scores = {}
        all_ids = set(dense_norm.keys()) | set(sparse_norm.keys())
        
        for cid in all_ids:
            row = self.metadata_store.get(cid)
            if not row: continue
                
            if filters:
                skip = False
                for f_key, f_val in filters.items():
                    if row.get(f_key, "") != f_val:
                        skip = True
                        break
                if skip: continue

            ds = dense_norm.get(cid, 0.0)
            ss = sparse_norm.get(cid, 0.0)
            base_score = (alpha * ds) + ((1 - alpha) * ss)
            
            auth_adj = 0.0
            doc_type = str(row.get('document_type', '')).lower()
            subject = str(row.get('subject', '')).lower()
            
            if any(t in doc_type for t in ['master direction', 'master circular', 'regulation', 'notification']):
                auth_adj += 0.15
            elif any(t in doc_type for t in ['circular', 'direction', 'guidelines']):
                auth_adj += 0.05
            
            if any(t in doc_type for t in ['explanatory', 'discussion', 'article', 'speech', 'press release', 'legal']):
                auth_adj -= 0.10
                
            subject_has_specific = any(e in subject for e in entities)
            if not has_specific_entity:
                if subject_has_specific:
                    auth_adj -= 0.10
            else:
                for e in entities:
                    if e in query_lower and e in subject:
                        auth_adj += 0.20
            
            val_adj = 0.0
            validity = str(row.get('validity_status', 'unknown')).lower()
            if validity == 'current' or validity == 'active':
                val_adj += 0.05
            elif (validity == 'superseded' or validity == 'withdrawn') and not is_historical:
                val_adj -= 0.10
                
            final_hybrid = base_score + auth_adj + val_adj
            combined_scores[cid] = {
                'score': final_hybrid,
                'base': base_score,
                'auth': auth_adj,
                'val': val_adj,
                'row': row,
                'ds': ds,
                'ss': ss,
                'r_ds': dense_raw.get(cid, 0.0),
                'r_ss': sparse_raw.get(cid, 0.0)
            }
            
        sorted_ids = sorted(combined_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        final_results = []
        for cid, data in sorted_ids:
            row = data['row']
            print(f"DEBUG: {cid} | F: {data['ds']:.2f}, BM: {data['ss']:.2f} | Auth: {data['auth']:.2f}, Val: {data['val']:.2f} | Final: {data['score']:.2f} | {row.get('document_type', '')} - {row.get('subject', '')}")
            
            result_obj = {
                "chunk_id": cid,
                "document_id": str(row.get('document_id', '')),
                "regulator": str(row.get('regulator', '')),
                "document_title": str(row.get('subject', '')),
                "document_type": str(row.get('document_type', '')),
                "section": str(row.get('section', '')),
                "paragraph": str(row.get('paragraph', '')),
                "issue_date": str(row.get('issue_date', '')),
                "effective_date": str(row.get('effective_date', '')),
                "validity_status": str(row.get('validity_status', 'unknown')),
                "source_url": str(row.get('source_url', '')),
                "text": str(row.get('text', '')),
                "dense_score": float(data['ds']),
                "bm25_score": float(data['ss']),
                "hybrid_score": float(data['score']),
                "raw_dense_score": float(data['r_ds']),
                "raw_bm25_score": float(data['r_ss'])
            }
            final_results.append(result_obj)
            if len(final_results) == k:
                break
                
        return final_results
