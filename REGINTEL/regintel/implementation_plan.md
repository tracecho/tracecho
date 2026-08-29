# RegIntel Implementation Plan

## Phase 1 — Existing Data (Completed)
- Visually inspected SEBI `.parquet` file schemas.
- Found SEBI dataset contains 368 superseded, 357 current, 2 partially_superseded, 1 unknown statuses. 
- Found RBI data has unstructured PDFs and text files but explicit RBI metadata was empty. Will assume text generation for chunking.

## Phase 2 — Processing
- [ ] Implement `ingestion/cleaner.py` (Text cleaning).
- [ ] Implement `ingestion/chunker.py` (Regulatory-aware chunking).
- [ ] Extract and preserve metadata for both SEBI and RBI.
- [ ] Save processed corpus to `data/processed`.

## Phase 3 — Retrieval
- [ ] Set up `retrieval/embeddings.py` (Sentence Transformers).
- [ ] Setup `retrieval/vector_store.py` (FAISS).
- [ ] Setup `retrieval/bm25.py` and `retrieval/hybrid_search.py`.

## Phase 4 — Basic RAG & Phase 5-8 Agent Integration
- [ ] Implement LangGraph orchestration.
- [ ] Agent 1: Retrieval Agent
- [ ] Agent 2: Compliance Reasoning Agent
- [ ] Agent 3: Verification Agent

## Phase 9-14 — Guardrails, Dashboard, Evaluation & UI
- [ ] Add Guardrails integration.
- [ ] External API dashboard (Module 2).
- [ ] Streamlit UI.
