import pandas as pd
import numpy as np

class RegintelHybridRetriever:
    def __init__(self, embeddings_model, vector_store, bm25_store, metadata_store):
        self.embeddings = embeddings_model
        self.vector_store = vector_store
        self.bm25_store = bm25_store
        self.metadata_store = metadata_store # dictionary lookup

        
    def _normalize_bm25(self, results):
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

    def _normalize_dense(self, results):
        # We already converted to cosine similarity which is roughly in [-1, 1]
        # Map to [0, 1]
        norm_map = {}
        for chunk_id, score in results:
            norm_map[chunk_id] = max(0.0, min(1.0, score))
        return norm_map

    def search(self, query, alpha=0.6, k=10, filters=None, temporal_type="UNSPECIFIED", temporal_year="", skip_rerank=False):
        query_emb = self.embeddings.embed_query(query)
        
        # INCREASE K to allow for filtering and reranking
        candidate_k = max(k*3, 50)
        dense_results = self.vector_store.search(query_emb, k=candidate_k)
        sparse_results = self.bm25_store.search(query, k=candidate_k)
        
        dense_raw = {cid: sc for cid, sc in dense_results}
        sparse_raw = {cid: sc for cid, sc in sparse_results}
        
        dense_norm = self._normalize_dense(dense_results)
        sparse_norm = self._normalize_bm25(sparse_results)
        
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
            issue_date = str(row.get('issue_date', ''))
            is_temporal_match = False
            
            if temporal_type == "HISTORICAL":
                # For historical queries, give strong preference to provisions applicable in the year requested.
                # Avoid simply jumping to current versions if they weren't applicable.
                eff_date = str(row.get('effective_date', ''))
                if temporal_year and (temporal_year in issue_date or temporal_year in eff_date):
                    val_adj += 0.35
                    is_temporal_match = True
                elif temporal_year and int(temporal_year) > 2000 and (f"20" in issue_date):
                    # Slight penalty for other years if we have a specific temporal_year
                    val_adj -= 0.10
                if validity == 'superseded' or validity == 'withdrawn':
                    val_adj += 0.10
                elif validity == 'current' or validity == 'active':
                    # Current provisions might not be historical
                    val_adj -= 0.15
            else:
                if validity == 'current' or validity == 'active':
                    val_adj += 0.15
                elif (validity == 'superseded' or validity == 'withdrawn') and not is_historical:
                    val_adj -= 0.20
                
            # Filter obvious boilerplate chunks based on text
            text = str(row.get('text', ''))
            lower_text = text.lower()
            if len(text.strip()) < 150 and any(w in lower_text for w in ['tel:', 'email:', 'website:', 'counsel', 'telephone', 'telephone no']):
                continue
                
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
                'r_ss': sparse_raw.get(cid, 0.0),
                'temporal_match': is_temporal_match
            }
            
        # Optional Lightweight CrossEncoder reranking
        if not skip_rerank:
            try:
                from sentence_transformers import CrossEncoder
                # Memoize model in class to avoid reloading
                if not hasattr(self, 'cross_encoder'):
                    self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)
                
                # Take top 20 candidates for reranking
                sorted_by_hybrid = sorted(combined_scores.items(), key=lambda x: x[1]['score'], reverse=True)[:20]
                
                pairs = []
                for cid, data in sorted_by_hybrid:
                    pairs.append((query, str(data['row'].get('text', ''))))
                    
                if pairs:
                    ce_scores = self.cross_encoder.predict(pairs)
                    
                    # Normalize CE scores relative to candidates
                    ce_min = float(min(ce_scores))
                    ce_max = float(max(ce_scores))
                    
                    for idx, (cid, data) in enumerate(sorted_by_hybrid):
                        ce_score = float(ce_scores[idx])
                        if ce_max > ce_min:
                            norm_ce = (ce_score - ce_min) / (ce_max - ce_min)
                        else:
                            norm_ce = 0.5
                        
                        # Store for logging
                        combined_scores[cid]['rerank_score'] = ce_score
                        combined_scores[cid]['norm_ce'] = norm_ce
                        
                        # Final score combines hybrid + reranker
                        combined_scores[cid]['final_score'] = data['score'] * 0.4 + norm_ce * 0.6
                        combined_scores[cid]['is_reranked'] = True
                        
                # Any chunks not in the top 20 should be pushed to the bottom so they don't outrank
                for cid, data in combined_scores.items():
                    if not data.get('is_reranked'):
                        data['final_score'] = -999.0
                        data['norm_ce'] = 0.0
                        data['rerank_score'] = 0.0
                        
            except Exception as e:
                print(f"Reranker skipped: {e}")
                for cid, data in combined_scores.items():
                     data['rerank_score'] = 0.0
                     data['norm_ce'] = 0.0
                     data['final_score'] = data['score']
        else:
            for cid, data in combined_scores.items():
                 data['rerank_score'] = 0.0
                 data['norm_ce'] = 0.0
                 data['final_score'] = data['score']
                 
        sorted_ids = sorted(combined_scores.items(), key=lambda x: x[1]['final_score'], reverse=True)
        
        final_results = []
        doc_count = {}
        
        for cid, data in sorted_ids:
            row = data['row']
            
            if row.get('document_origin') == "NON_RBI":
                continue
                
            doc_id = str(row.get('document_id', ''))
            
            # Document diversity constraint (max 3 chunks from same doc)
            if doc_id:
                if doc_count.get(doc_id, 0) >= 3:
                    continue
                doc_count[doc_id] = doc_count.get(doc_id, 0) + 1
                
            print(f"DEBUG:\nDocument: {doc_id}\nDense Raw: {data['r_ds']:.2f}\nDense Norm: {data['ds']:.2f}\nBM25 Raw: {data['r_ss']:.2f}\nBM25 Norm: {data['ss']:.2f}\nMetadata: {(data['auth'] + data['val']):+.2f}\nHybrid: {data['score']:.2f}\nCE Raw: {data.get('rerank_score', 0.0):.2f}\nCE Norm: {data.get('norm_ce', 0.0):.2f}\nFinal: {data.get('final_score', data['score']):.3f}\nTemporal Match: {bool(data.get('temporal_match', False))}\nValidity: {str(row.get('validity_status', 'unknown')).upper()}\n")
            
            result_obj = {
                "chunk_id": cid,
                "document_id": doc_id,
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
                "raw_bm25_score": float(data['r_ss']),
                "metadata_adj": float(data['auth'] + data['val']),
                "reranker_score": float(data.get('rerank_score', 0.0)),
                "norm_reranker_score": float(data.get('norm_ce', 0.0)),
                "final_score": float(data.get('final_score', data['score'])),
                "temporal_match": bool(data.get('temporal_match', False)),
            }
            final_results.append(result_obj)
            if len(final_results) == k:
                break
                
        return final_results
