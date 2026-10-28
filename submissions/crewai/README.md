# Candidate Profile to Job Matching with CrewAI & IBM Db2 Vector Search

> **One-Line Pitch:** An enterprise multi-agent candidate-to-position matching system featuring local offline IBM Granite embeddings, decoupled Haystack 2.x ingestion, and CrewAI DB2VectorSearchTool similarity search with IBM Db2.

---

## Table of Contents
- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [IBM Db2 Integration](#ibm-db2-integration)
- [AI / LLM Architecture](#ai--llm-architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [Testing & Verification](#testing--verification)
- [Known Limitations & Future Roadmap](#known-limitations--future-roadmap)
- [Team Members & Credits](#team-members--credits)

---

## Problem Statement
- **The Challenge**: Traditional talent acquisition and recruiting systems rely on rigid keyword matching, leading to high false-rejection rates, poor talent discovery, and massive recruiter fatigue when evaluating technical candidate profiles against complex job catalogs.
- **Target Audience**: Enterprise recruitment teams, talent acquisition leaders, engineering hiring managers, and career advisory platforms.
- **Why Existing Tooling Is Insufficient**: Traditional keyword-based search fails to capture semantic equivalence (e.g., matching a candidate skilled in "PyTorch & RAG" with a role requiring "Deep Learning & Generative AI"). Furthermore, cloud-dependent embedding architectures pose data privacy concerns and introduce recurring API latency and cost.

---

## Solution Overview
This solution delivers an end-to-end, privacy-first, decoupled AI matching architecture:
1. **Decoupled Ingestion Pipeline**: Uses the official **Haystack 2.x IBM Db2 Integration** (`IBMDb2DocumentStore` + `SentenceTransformersDocumentEmbedder` + `DocumentWriter`) to ingest and index job openings into IBM Db2 with vector representations.
2. **Local Offline Dense Embeddings**: Powered by IBM's open-source **`ibm-granite/granite-embedding-311m-multilingual-r2`** (via PyTorch / Sentence-Transformers), generating 768-dimensional dense vectors 100% locally with zero external API dependencies.
3. **Multi-Agent Retrieval & Reasoning**: Orchestrated with **CrewAI** using the official **`DB2VectorSearchTool`** with custom local Granite embedding functions for native `VECTOR_DISTANCE` similarity search, combined with an agentic evaluator powered by local `granite3.3:8b` via Ollama or watsonx/OpenAI.

---

## IBM Db2 Integration
- **Db2 Edition & Environment**: Compatible with IBM Db2 (v11.5+ with Vector capability) or containerized Db2.
- **Connector / Drivers Used**: `ibm_db` (native C-driver bindings), `ibm-db-haystack` (official Haystack 2.x Document Store), and `crewai-tools` (`DB2VectorSearchTool`).
- **Database Schema & Vector Models**:
  ```sql
  CREATE TABLE JOB_POSTINGS (
      ID VARCHAR(128) NOT NULL PRIMARY KEY,
      CONTENT CLOB,
      DATAFRAME CLOB,
      BLOB_DATA BLOB,
      BLOB_MIME_TYPE VARCHAR(128),
      META CLOB,
      EMBEDDING VECTOR(768, FLOAT32)
  );
  ```
- **Key Operations**:
  - Dense document indexing via Haystack `DocumentWriter` with `DuplicatePolicy.OVERWRITE`.
  - Native `VECTOR_DISTANCE(EMBEDDING, ?, 'COSINE')` similarity search via CrewAI `DB2VectorSearchTool`.
  - Safe memoryview/CLOB decoding handling via custom `DB2JSONEncoder` deserializer.

---

## AI / LLM Architecture
- **Multi-Agent Framework**: CrewAI (sequential agent workflow).
- **Ingestion Framework**: Haystack 2.x (Haystack pipeline with `SentenceTransformersDocumentEmbedder`).
- **Local Embedding Model**: `ibm-granite/granite-embedding-311m-multilingual-r2` (768-dim native, Matryoshka support).
- **Agent Reasoning LLM**: Local Ollama (`granite3.3:8b`) or watsonx / OpenAI.
- **Workflow**:
  1. **CV Reader Agent (`cv_reader`)**: Parses candidate CV (`data/cv.md`) using `FileReadTool`, extracting structured skills, domain experience, and key accomplishments.
  2. **Matcher & Evaluator Agent (`matcher`)**: Converts profile semantics into vector queries, performs cosine similarity search in IBM Db2 via `DB2VectorSearchTool`, evaluates candidate fit, and generates a ranked match report with fit scores and gap analyses.

---

## Tech Stack
- **Languages**: Python 3.11
- **Database**: IBM Db2 (Native Vector Search)
- **Agent & Ingestion Frameworks**: CrewAI, Haystack 2.x (`ibm-db-haystack`)
- **Deep Learning / NLP**: PyTorch, Sentence-Transformers, Hugging Face Transformers
- **Models**: IBM Granite Embedding (311M Multilingual R2), IBM Granite 3.3 8B

---

## Prerequisites
- Python >= 3.10, <= 3.13
- IBM Db2 instance accessible via network (or local container) with Vector support
- (Optional for offline reasoning) [Ollama](https://ollama.com/) with `ollama run granite3.3:8b`

---

## Setup & Installation

```bash
# 1. Navigate to submission directory
cd submissions/crewai

# 2. Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Copy `.env.example` to `.env` and configure your Db2 connection credentials:

```bash
cp .env.example .env
```

Example `.env` parameters:
```env
# IBM Db2 Connection Parameters
DB2_DATABASE=BLUDB
DB2_HOSTNAME=localhost
DB2_PORT=50000
DB2_USERNAME=db2admin
DB2_PASSWORD=your_password
DB2_TABLE_NAME=JOB_POSTINGS

# Local Offline Embedding Model Configuration (IBM Granite Multilingual)
EMBEDDING_MODEL=ibm-granite/granite-embedding-311m-multilingual-r2
EMBEDDING_DIMENSION=768

# Reasoning LLM Configuration
# Optional: Set OPENAI_API_KEY for OpenAI, or leave default for local Ollama
OPENAI_API_KEY=your_llm_api_key_here
OLLAMA_MODEL=ollama/granite3.3:8b
OLLAMA_BASE_URL=http://localhost:11434
```

> **Security Note:** `.env` is ignored by Git and must never contain committed credentials.

---

## Running the Project

### Step 1: Ingest Job Descriptions into IBM Db2
Run the decoupled Haystack ingestion pipeline to vectorize `data/jobs.csv` using local Granite embeddings and index them into IBM Db2:

```bash
python -m src.ingestion.ingest_jobs_haystack
```

### Step 2: Run CrewAI Profile Matching
Run the multi-agent CrewAI pipeline to analyze `data/cv.md` and perform semantic vector matching against Db2:

```bash
python -m src.match_to_proposal.main
```

---

## Testing & Verification
Execute the automated test suite to validate local Granite embedding generation, Haystack document parsing, and CrewAI agent/tool assembly:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## Known Limitations & Future Roadmap
- **Current Scope**: Optimized for text-based CV and job catalog matching using cosine distance on 768-dim embeddings.
- **Future Roadmap**:
  - Add support for multi-modal candidate portfolios (PDF/Word parsing with OCR).
  - Add real-time interview question generation based on detected skill gaps.
  - Integration with watsonx.governance for automated fairness and bias auditing.

---

## Team Members & Credits
| Name | GitHub Handle | Role / Contribution |
|---|---|---|
| Pawan Thakur | [@PawanThakurIBM](https://github.com/PawanThakurIBM) | Architecture, Db2 Vector Integration, Haystack Pipeline, CrewAI Multi-Agent System |
