
# TRACECHO — Regulatory Intelligence & Compliance Platform

TRACECHO is an AI-powered regulatory intelligence platform designed to help users search, understand, and analyse Indian financial regulations issued by the **Reserve Bank of India (RBI)** and the **Securities and Exchange Board of India (SEBI)**.

The platform combines **Retrieval-Augmented Generation (RAG)**, hybrid information retrieval, LangGraph-based workflow orchestration, LLM reasoning, guardrails, and regulatory metadata to provide evidence-grounded answers rather than relying solely on an LLM's pretrained knowledge.

---

## 1. Project Overview

Financial regulations are distributed across a large number of circulars, master directions, regulations, notifications, and other regulatory publications.

Manually finding the relevant provision can be time-consuming and conventional LLM-based systems may generate unsupported or outdated information.

TRACECHO addresses this problem through two major modules:

### Module 1 — Regulatory Compliance Assistant

An agentic RAG system that:

- Accepts natural-language regulatory questions
- Identifies the relevant regulator and intent
- Searches RBI and SEBI regulatory documents
- Uses hybrid retrieval combining semantic and keyword search
- Generates evidence-grounded answers using an LLM
- Displays supporting evidence and citations
- Performs verification and guardrail checks
- Returns insufficient-evidence responses when reliable evidence is unavailable

### Module 2 — Regulatory Intelligence Dashboard

A financial intelligence dashboard designed to integrate external financial-market data with regulatory information.

The dashboard provides:

- Market and financial indicators
- Regulatory corpus statistics
- Data visualisation
- Analytical insights
- Scope for integration with additional financial APIs

---

# 2. Objectives

The main objectives of TRACECHO are:

- Build an evidence-grounded regulatory question-answering system
- Improve retrieval quality using hybrid search
- Reduce hallucination in regulatory responses
- Preserve regulatory metadata throughout the RAG pipeline
- Provide traceable regulatory evidence
- Handle current and historical regulatory information
- Detect insufficient evidence instead of fabricating answers
- Integrate regulatory knowledge with financial intelligence
- Provide an interactive web-based interface

---

# 3. System Architecture

                         TRACECHO
                            |
              ┌─────────────┴─────────────┐
              |                           |
              ▼                           ▼
      COMPLIANCE ASSISTANT       INTELLIGENCE DASHBOARD
              |                           |
              ▼                           ▼
        RBI / SEBI Data           External Financial APIs
              |                           |
              ▼                           ▼
       Data Processing             Data Processing
              |                           |
              ▼                           ▼
      Regulatory Chunking             Analytics
              |                           |
              ▼                           ▼
      Hybrid Retrieval             Visualisation
              |
              ▼
          LangGraph
              |
       ┌──────┼──────┐
       ▼      ▼      ▼
    Query   Retrieval Reasoning
    Analysis   |
               ▼
          Verification
               |
               ▼
          Guardrails
               |
               ▼
     Evidence-Grounded Answer


---

# 4. Technology Stack

## Programming

* Python

## Data Processing

* Pandas
* NumPy

## Natural Language Processing

* Sentence Transformers
* `all-MiniLM-L6-v2`

## Retrieval

* FAISS
* BM25
* Hybrid Retrieval
* Reranking

## Agent Orchestration

* LangGraph

## LLM

* Gemini

## Backend

* FastAPI
* Uvicorn

## Frontend

* Streamlit
* HTML
* CSS
* JavaScript

## Data Storage

* Parquet
* FAISS indexes
* Metadata files

## Visualisation

* Plotly
* Matplotlib

## Configuration

* Python environment variables
* `.env`

---

# 5. Regulatory Corpus

The platform uses regulatory documents from two major Indian financial regulators.

## RBI

The RBI corpus contains regulatory publications including:

* Master Directions
* Master Circulars
* Circulars
* Notifications
* NBFC-related regulations
* KYC / AML / CFT regulations
* Banking and financial-sector regulations
* Digital and cybersecurity-related regulations
* Other relevant RBI regulatory documents

Approximately **1,548 RBI PDFs were initially collected**, followed by filtering and preprocessing for the final corpus.

## SEBI

The SEBI corpus contains:

* Regulations
* Circulars
* Master Circulars
* Guidelines
* Notifications
* Investment Adviser regulations
* Alternative Investment Fund regulations
* Listed entity requirements
* Disclosure requirements
* Market intermediary regulations
* Investor protection requirements
* Other SEBI regulatory publications

The SEBI corpus contains approximately **728 document records**.

---

# 6. Data Processing Pipeline

The regulatory documents are processed before they become searchable.


RBI / SEBI Documents
        ↓
Data Validation
        ↓
Text Extraction
        ↓
Text Cleaning
        ↓
Regulatory-Aware Chunking
        ↓
Metadata Preservation
        ↓
Embedding Generation
        ↓
FAISS Index
        +
BM25 Index


The current processed corpus contains approximately:

10,819 searchable chunks


A chunk is a smaller section of a regulatory document that can be independently retrieved.

---

# 7. Metadata

Metadata is preserved throughout the retrieval pipeline.

Typical metadata includes:


chunk_id
document_id
regulator
document_title
document_type
circular_number
issue_date
effective_date
section
paragraph
subject
validity_status
source_url
text


This allows the system to provide traceable regulatory evidence.

---

# 8. Hybrid Retrieval

TRACECHO does not depend on a single retrieval method.

It combines:

### Dense Retrieval

FAISS searches using vector embeddings.

This helps identify documents that are semantically similar even when the exact wording differs.

### Sparse Retrieval

BM25 performs keyword-based retrieval.

This is particularly useful for regulatory terminology, circular numbers, section names, and specific legal terms.

### Hybrid Retrieval


             User Query
                  |
        ┌─────────┴─────────┐
        ▼                   ▼
     FAISS                 BM25
 Semantic Search       Keyword Search
        |                   |
        └─────────┬─────────┘
                  ▼
           Hybrid Ranking
                  ↓
             Top Results


---

# 9. Embedding Model

The system uses:


all-MiniLM-L6-v2


The embedding model converts text into numerical vectors.

For example:

"KYC requirements for NBFCs"
              ↓
      Sentence Transformer
              ↓
       Numerical Vector
              ↓
             FAISS


This enables semantic similarity search.

---

# 10. LangGraph Workflow

LangGraph is used to orchestrate the regulatory question-answering workflow.


START
  ↓
Query Analysis
  ↓
Retrieval
  ↓
Relevance Validation
  ↓
Reasoning
  ↓
Guardrails / Verification
  ↓
Final Answer


The workflow maintains state containing information such as:

query
query_intent
regulator
retrieval_queries
retrieved_documents
reasoning_output
draft_answer
verification_output
final_answer


---

# 11. Agentic Components

TRACECHO uses multiple functional agent-like stages.

### 1. Query Analysis

Identifies:

* User intent
* Relevant regulator
* Regulatory domain
* Temporal context
* Search query

### 2. Retrieval

Finds relevant regulatory evidence using:

* FAISS
* BM25
* Hybrid ranking
* Metadata
* Relevance validation

### 3. Reasoning

Uses Gemini to transform retrieved regulatory evidence into a structured answer.

### 4. Verification / Guardrails

Checks the generated response for:

* Unsupported claims
* Missing evidence
* Invalid citations
* Irrelevant evidence
* Potential hallucinations

---

# 12. Example Query Flow

User asks:

> What are the KYC requirements for NBFCs?

The system processes the question as follows:

User Query
    ↓
Query Analysis
    ↓
Regulator → RBI
    ↓
Generate Search Query
    ↓
FAISS + BM25
    ↓
Retrieve Relevant RBI Chunks
    ↓
Relevance Validation
    ↓
Gemini Reasoning
    ↓
Verification / Guardrails
    ↓
Answer + Evidence + Citation


---

# 13. Evidence-Grounded Answers

The system is designed so that regulatory answers are based on retrieved evidence.

The UI displays:

* Answer
* Regulatory requirement
* Applicability
* Conditions
* Supporting evidence
* Regulatory document
* Chunk ID
* Date
* Regulator
* Verification status

This allows the user to trace the answer back to the regulatory corpus.

---

# 14. Handling Unsupported Questions

A major reliability feature is the handling of questions for which adequate evidence is unavailable.

For example:

> What regulations has SEBI issued for cryptocurrency mining companies operating on Mars?

Instead of inventing a regulation, the system should return:


INSUFFICIENT EVIDENCE


This is important because retrieval systems can sometimes return the "closest" documents even when those documents are not actually relevant.

TRACECHO therefore includes relevance validation and safe responses.

---

# 15. Regulatory Validity

Regulations can change over time.

The system therefore preserves regulatory metadata such as:


effective_date
validity_status
supersession_status
version_lineage
superseded_by_id
supersession_edges


This helps distinguish:

CURRENT


from:


SUPERSEDED


Historical questions can also be handled using the relevant regulatory version where available.

---

# 16. Backend Architecture

FastAPI acts as the backend API layer.


Streamlit Frontend
        ↓
HTTP Request
        ↓
FastAPI
        ↓
LangGraph Workflow
        ↓
RAG Pipeline
        ↓
Structured Response
        ↓
FastAPI
        ↓
Streamlit


The main question-answering endpoint is:

POST /api/ask


---

# 17. Frontend

The user interface is built using:

* Streamlit
* HTML
* CSS
* JavaScript

The application contains:


TRACECHO

├── Regulatory Assistant
├── Intelligence Dashboard
├── Document Explorer
└── System / Evaluation


The Regulatory Assistant displays:

* Query analysis
* Answer
* Regulatory details
* Applicability
* Conditions
* Supporting evidence
* Citations
* Retrieved chunks
* Verification status

---

# 18. Regulatory Intelligence Dashboard

The dashboard is designed as a separate intelligence module.

Its architecture is:


External Financial API
        ↓
API Client
        ↓
Data Validation
        ↓
Data Processing
        ↓
Analytics
        ↓
Dashboard


Potential dashboard features include:

### Market Overview

* Market indices
* Daily changes
* Market trends
* Volume

### Sector Analysis

* Sector performance
* Comparative trends
* Sector indicators

### Time-Series Analysis

* Historical movements
* Rolling averages
* Volatility indicators

### Regulatory Context

Financial/market observations can be connected to relevant regulatory domains.

---

# 19. API Configuration

External APIs are configured using environment variables.

Example:

```env
ALPHA_VANTAGE_API_KEY=YOUR_KEY_HERE
```

API keys are not hard-coded into the source code.

Additional financial APIs can be integrated in future versions.

---

# 20. Evaluation Framework

The system should be evaluated at both the retrieval and answer-generation levels.

## Retrieval Metrics

### Precision@K

Measures how many of the top K retrieved chunks are relevant.

### Recall@K

Measures how many relevant chunks were successfully retrieved.

### MRR

Mean Reciprocal Rank measures how early the first relevant result appears.

### nDCG

Measures the quality of the ranking, giving more importance to highly relevant results appearing near the top.

---

# 21. Retrieval Comparison

The proposed retrieval architecture can be compared against:


Vector Retrieval
       vs
BM25
       vs
Hybrid Retrieval
       vs
Hybrid + Reranking


This allows the project to measure whether combining semantic and keyword retrieval improves performance.

---

# 22. Answer Evaluation

Generated answers can be evaluated using:

* Answer correctness
* Faithfulness
* Context relevance
* Citation accuracy
* Unsupported claim rate
* Hallucination rate

The evaluation should determine whether the generated answer is actually supported by the retrieved regulatory evidence.

---

# 23. Baseline Comparison

The proposed system can be compared against simpler architectures.

### Baseline 1 — LLM Only

```text
Question
   ↓
LLM
   ↓
Answer
```

### Baseline 2 — Vector RAG

```text
Question
   ↓
Vector Search
   ↓
LLM
   ↓
Answer
```

### Baseline 3 — Hybrid RAG

```text
Question
   ↓
BM25 + Vector Search
   ↓
LLM
   ↓
Answer
```

### Proposed System

```text
Question
   ↓
Query Analysis
   ↓
Hybrid Retrieval
   ↓
Relevance Validation
   ↓
Reasoning
   ↓
Verification
   ↓
Guardrails
   ↓
Verified Answer
```

---

# 24. Hallucination Risk and Mitigation

LLMs can generate information that is not supported by the source documents.

TRACECHO reduces this risk by grounding responses in retrieved RBI and SEBI evidence, validating retrieval relevance, displaying supporting evidence, and applying verification and guardrails before returning the final answer. When adequate evidence is unavailable, the system is designed to return an insufficient-evidence response instead of fabricating regulatory information.

---

# 25. Advantages

* Evidence-grounded regulatory answers
* Hybrid semantic and keyword retrieval
* RBI and SEBI regulatory coverage
* Regulatory metadata preservation
* Support for temporal regulatory context
* Citation and evidence visibility
* Reduced hallucination risk
* Insufficient-evidence handling
* Modular LangGraph architecture
* Interactive Streamlit interface
* FastAPI backend
* Extensible financial intelligence dashboard
* Suitable for future RegTech applications

---

# 26. Limitations

* Answer quality depends on the completeness and quality of the regulatory corpus.
* The system may retrieve partially relevant documents for highly ambiguous questions.
* Regulatory interpretation ultimately requires human/legal expertise.
* External LLM APIs introduce availability and rate-limit dependencies.
* External financial APIs may have rate limits and data-access restrictions.
* Current dashboard functionality depends on the availability and reliability of external market data.
* Citation metadata and document-level aggregation can require additional validation.
* The system should not be treated as a substitute for professional legal or compliance advice.

---

# 27. Future Enhancements

Planned improvements include:

* Add more financial-market APIs to the dashboard.
* Integrate additional real-time market and economic indicators.
* Add predictive analytics for market and sector trends.
* Develop forecasting models for selected financial indicators.
* Add anomaly and risk detection to the intelligence dashboard.
* Expand the regulatory corpus with newly issued RBI and SEBI documents automatically.
* Improve regulatory version and supersession tracking.
* Add more sophisticated reranking models.
* Expand the evaluation benchmark to 100–200+ regulatory questions.
* Add multilingual regulatory question support.
* Introduce document-level comparison between current and historical regulations.
* Improve dashboard-to-compliance-assistant integration.
* Add automated alerts for important regulatory changes.

---

# 28. Project Structure

```text
regintel/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── evaluation/
│
├── ingestion/
│   ├── loaders.py
│   ├── cleaner.py
│   ├── chunker.py
│   └── metadata.py
│
├── retrieval/
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── bm25.py
│   ├── hybrid_search.py
│   └── reranker.py
│
├── agents/
│   ├── retrieval_agent.py
│   ├── reasoning_agent.py
│   └── verification_agent.py
│
├── graph/
│   ├── state.py
│   ├── nodes.py
│   └── workflow.py
│
├── guardrails/
│   ├── schemas.py
│   └── validators.py
│
├── prompts/
│   ├── retrieval.py
│   ├── reasoning.py
│   └── verification.py
│
├── rag/
│   ├── context_builder.py
│   ├── citation.py
│   └── pipeline.py
│
├── dashboard/
│   ├── api_client.py
│   ├── data_processor.py
│   ├── analytics.py
│   └── charts.py
│
├── evaluation/
│   ├── benchmark.py
│   ├── retrieval_metrics.py
│   ├── answer_metrics.py
│   └── evaluation_runner.py
│
├── api/
│   └── main.py
│
├── ui/
│   └── app.py
│
├── config/
│   └── settings.py
│
├── tests/
│
├── .env.example
├── requirements.txt
└── README.md
```

---

# 29. Running the Project

## 1. Activate the Python environment

Use the project's configured Python environment.

## 2. Configure environment variables

Create a `.env` file and configure the required API keys.

Example:

```env
ALPHA_VANTAGE_API_KEY=YOUR_KEY_HERE
```

Configure the required LLM/API credentials according to the project environment.

## 3. Start FastAPI

From the `regintel` directory:

```bash
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

## 4. Start Streamlit

Open another terminal:

```bash
streamlit run ui/app.py
```

The application will be available through the Streamlit local URL.

---

# 30. Example Output

For a query such as:

```text
What are the KYC requirements for NBFCs?
```

TRACECHO can display:

```text
Query Analysis
    ↓
Regulator: RBI

Retrieved Evidence
    ↓
Relevant RBI regulatory chunks

Answer
    ↓
Evidence-grounded regulatory response

Regulatory Basis
    ↓
Document + Chunk ID + Date + Regulator

Verification
    ↓
Evidence Grounded
Citation Checked
```

---

# 31. Research Questions

The project investigates:

### RQ1

Does hybrid retrieval improve retrieval quality compared with vector-only retrieval?

### RQ2

Does regulatory metadata and supersession awareness reduce outdated regulatory answers?

### RQ3

Does verification reduce unsupported claims and hallucination?

### RQ4

Does agentic RAG improve citation accuracy compared with conventional RAG?

### RQ5

Does integrating financial-market data with regulatory intelligence improve the usefulness of the platform for compliance-oriented analysis?

---

# 32. Conclusion

TRACECHO combines regulatory document retrieval, LLM-based reasoning, verification, and financial intelligence into a unified RegTech platform.

The system moves beyond a conventional chatbot by combining:

```text
Regulatory Documents
        +
Hybrid Retrieval
        +
LangGraph Workflow
        +
LLM Reasoning
        +
Verification
        +
Guardrails
        +
Financial Intelligence
        ↓
TRACECHO
```

The primary focus is on **accuracy, evidence grounding, traceability, regulatory validity, and reduced hallucination**, making the platform suitable as a foundation for further research and development in AI-assisted regulatory intelligence.

```
```
