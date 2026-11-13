TRACECHO

AI-Powered Regulatory Intelligence

Making regulatory information easier to discover, understand, and navigate — with answers grounded in documentary evidence.

TRACECHO is an AI-powered regulatory intelligence platform designed to simplify research across complex financial regulations. It uses Retrieval-Augmented Generation (RAG) to retrieve relevant regulatory documents and generate clear, source-backed answers.

The platform currently focuses on regulatory information from the Reserve Bank of India (RBI) and the Securities and Exchange Board of India (SEBI).

Overview

Regulatory information is often distributed across extensive circulars, notifications, guidelines, and amendments. Finding the right information and understanding its context can be time-consuming.

TRACECHO addresses this challenge through:

Intelligent Regulatory Search: Discover relevant information across regulatory documents.

AI-Powered Question Answering: Ask questions in natural language and receive contextual responses.

Hybrid Retrieval: Combine semantic vector search with keyword-based retrieval.

Source Citations: Trace generated answers back to supporting regulatory documents.

Evidence Verification: Apply verification and guardrails to reduce unsupported responses.

Responsible AI: Identify insufficient evidence rather than confidently generating unsupported answers.

Key Features

Feature

Description

AI Regulatory Assistant

Ask questions about RBI and SEBI regulations.

Hybrid Search

Combine FAISS vector retrieval and BM25 keyword search.

Contextual Answers

Generate responses using retrieved regulatory evidence.

Source Attribution

Display supporting documents and citations.

Guardrails

Detect insufficient evidence and unsupported responses.

Document Explorer

Explore the regulatory document collection.

Evaluation

Assess retrieval and answer quality.

User Authentication

JWT-based signup and sign-in with PostgreSQL.

Architecture

TRACECHO follows a multi-stage RAG architecture.

              User Question
                    |
                    v
             Query Analysis
                    |
                    v
             Hybrid Retrieval
              /          \
             v            v
        FAISS Search   BM25 Search
             \            /
              v          v
          Retrieved Documents
                    |
                    v
             AI Reasoning
                    |
                    v
          Evidence Verification
                    |
              +-----+-----+
              |           |
              v           v
        Supported      Insufficient
          Answer         Evidence
              |           |
              v           v
          Citations    Responsible
                        Response

Technology Stack

Frontend

React

TypeScript

Vite

Tailwind CSS

Backend

Python

FastAPI

LangGraph

Retrieval and AI

FAISS

BM25

Sentence Transformers (all-MiniLM-L6-v2)

Gemini API

Retrieval-Augmented Generation (RAG)

Database and Authentication

PostgreSQL

SQLAlchemy

Alembic

JWT Authentication

Development Tools

Git and GitHub

Jupyter Notebook / Google Colab

VS Code

Project Structure

TRACECHO/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── context/
│   │   └── ...
│   └── package.json
│
├── regintel/
│   ├── api/
│   ├── db/
│   ├── retrieval/
│   ├── ...
│   ├── alembic/
│   └── ui/
│
├── .env.example
├── .gitignore
└── README.md

The structure above is a simplified overview; individual directories may evolve as development progresses.

Getting Started

Prerequisites

Python 3.10+

Node.js and npm

PostgreSQL

Git

Gemini API key

1. Clone the repository

git clone https://github.com/karlinnn/tracecho.git
cd tracecho

2. Configure environment variables

Create a .env file in the project root using the variables required by the application.

Example configuration:

DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/tracecho
GEMINI_API_KEY=your_gemini_api_key

Add any additional variables required by your local configuration, including optional SMTP settings for contact email notifications.

Never commit .env or expose API keys and credentials.

3. Set up the Python environment

python -m venv .venv

Activate it:

.\.venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

4. Run database migrations

From the project root:

cd regintel
..\.venv\Scripts\python.exe -m alembic -c alembic.ini upgrade head

5. Start the backend

From the project root:

.\.venv\Scripts\python.exe -m uvicorn regintel.api.main:app --reload --port 8000

Backend API:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

6. Start the frontend

Open another terminal:

cd frontend
npm install
npm run dev

Open the local development URL displayed by Vite, usually:

http://localhost:5173

Responsible AI and Reliability

TRACECHO is designed around evidence-grounded generation.

Rather than treating every generated response as automatically correct, the system incorporates:

Retrieval from regulatory source documents.

Context-aware answer generation.

Source attribution.

Evidence verification.

Guardrails for insufficient or unsupported information.

The objective is to make regulatory research more transparent and traceable, not to replace professional legal, compliance, or financial advice.

Roadmap

Potential areas of continued development:

Advanced hybrid retrieval and reranking.

Improved document versioning and regulatory amendment tracking.

Expanded evaluation datasets and retrieval metrics.

Persistent query history and user feedback.

PostgreSQL-backed evaluation history.

Administrative enquiry management.

Configurable email notifications.

Expanded regulatory document coverage.

Disclaimer

TRACECHO is an AI-powered research and information discovery project. Its generated responses may contain inaccuracies or omissions.

Always consult the original RBI and SEBI publications and qualified professionals before making regulatory, legal, financial, or compliance decisions.

Author

Karlin Francis

MSc Data Science | AI/ML Engineering

GitHub: https://github.com/karlinnn

LinkedIn: https://www.linkedin.com/in/karlin-francis-ab69b2213/

TRACECHO — Regulatory intelligence, grounded in evidence.
