# BAKEBOX Choco AI (Autonomous AI Bakery Management Platform & 3D Storefront)

> **One-Line Pitch:** An enterprise autonomous AI bakery management system and master baker digital assistant for Shri Ram Baker (Mathura), powered by IBM Db2 native vector search (`DB2LlamaVS`), LlamaIndex Hybrid RRF, and real-time transactional order intelligence.

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
- [Screenshots & Demo](#screenshots--demo)
- [Known Limitations & Future Roadmap](#known-limitations--future-roadmap)
- [Team Members & Credits](#team-members--credits)

---

## Problem Statement
- **Perishable Fresh-Baked Preparation Times:** At Shri Ram Baker (Mathura), handcrafted live fresh cakes require 3 to 4 hours of soaking and cold-setting. Customers repeatedly call kitchens inquiring about live preparation progress, tying up staff.
- **Vast Catalog Discovery:** Shri Ram Baker offers over 600+ cake varieties (Khoaa eggless, multi-tiered anniversary specials, doll cakes) that cannot be discovered effectively via static menus.
- **AI Hallucinations in Food Orders:** Standard chatbots invent non-existent products, hallucinate arbitrary prices, or give dangerous reheating advice (such as microwaving puff pastries).
- **Target Audience:** Local Mathura bakery customers, celebration planners, kitchen staff, and store managers.

---

## Solution Overview
BAKEBOX bridges enterprise relational data with advanced AI retrieval through **CHOCO AI** — an autonomous Master Baker assistant:
1. **IBM Db2 Native Vector Store (`DB2LlamaVS`):** Stores 384-dimensional dense vectors in table `BB_CHUNKS_VECTOR` using Db2 v12.1.2+ native `vector(384, FLOAT32)` column.
2. **Hybrid Reciprocal Rank Fusion (RRF: $k=60$):** Combines dense vector similarity with sparse lexical TF-IDF for exact cake flavor, weight (1kg vs 0.5kg), and base matching.
3. **Live Order Knowledge Engine:** Queries relational tables `BB_ORDERS` and `BB_ORDER_ITEMS` in IBM Db2 in real time to report live kitchen baking statuses.
4. **Strict 3-Cake Precision Recommendation (AI Tool Calling):** Returns verified JSON cards with exact SKUs, local image paths, and pricing ONLY when requested.

---

## IBM Db2 Integration
- **Db2 Edition & Environment:** IBM Db2 Community Edition (Docker / VS Code Extension Instance `IBMDB201` on Port 50000).
- **Connector / Driver Used:** Official Python drivers `ibm_db` and `ibm_db_dbi`, and official LlamaIndex vector store connector `llama-index-vector-stores-db2` (`DB2LlamaVS`).
- **Database Schema / Data Models:**
  - `BB_CHUNKS_VECTOR`: Native vector table created via `DB2LlamaVS` with schema `(id VARCHAR(64) PRIMARY KEY, doc_id VARCHAR(64), embedding vector(384, FLOAT32), node_info BLOB, metadata BLOB, text CLOB)`.
  - `BB_ORDERS`: Relational order table `(order_id INT PRIMARY KEY, user_id INT, customer_name, customer_phone, order_type, order_status, total_amount, delivery_address, special_notes)`.
  - `BB_ORDER_ITEMS`: Relational line items `(item_id INT IDENTITY, order_id INT, sku_id, item_name, quantity, unit_price, cake_base, cake_weight, custom_message)`.
- **Key Queries & Operations:**
  - In-engine Cosine distance similarity search via `DB2LlamaVS.query()`.
  - Transactional relational order retrieval joining `BB_ORDERS` and `BB_ORDER_ITEMS`.

---

## AI / LLM Architecture
- **Framework:** LlamaIndex 0.14 (`llama-index-core` and `llama-index-vector-stores-db2`).
- **Embedding Model:** HuggingFace `BAAI/bge-small-en-v1.5` (384 dimensions) via FastEmbed.
- **LLM / Synthesis Provider:** Google Gemini API (`gemini-3.5-flash-lite`, 1.2s fast synthesis) with culturally-rooted Mathura Hinglish persona (*"Radhe Radhe ji! Shri Ram Baker's BAKEBOX mein aapka swagat hai!"*).
- **RAG & Tool Calling Workflow:**
  - User query is evaluated for intent.
  - If recommendation is requested: Hybrid RRF retrieval extracts top nodes and generates exactly 3 structured cake cards.
  - If order status is requested: Relational query fetches ground truth from `BB_ORDERS` and suppresses product cards.

---

## Tech Stack
- **Backend / Core:** Python 3.14, FastAPI, LlamaIndex, `llama-index-vector-stores-db2`, `ibm_db`
- **Database:** IBM Db2 (v12.1.5.0 Community Edition)
- **Frontend / UI:** React 18, Vite, Tailwind CSS, Lucide Icons
- **AI & Embedding Models:** HuggingFace `BAAI/bge-small-en-v1.5`, Google Gemini 3.5 Flash Lite

---

## Prerequisites
- Python >= 3.10 (or Python 3.14)
- Running local IBM Db2 instance (e.g. `localhost:50000`, database `testdb` or `IBMDB201`)
- Node.js >= 18 (for running the full frontend storefront)

---

## Setup & Installation

```bash
# 1. Navigate to submission directory
cd submissions/bakebox-choco-ai

# 2. Install required dependencies
pip install llama-index-core llama-index-vector-stores-db2 ibm-db fastembed scikit-learn
```

---

## Configuration

Copy `.env.example` to `.env` and fill in your Db2 credentials:

```bash
cp .env.example .env
```

```env
DB2_HOST=127.0.0.1
DB2_PORT=50000
DB2_DATABASE=IBMDB201
DB2_USER=dbayush
DB2_PASSWORD=8844
```

> **Security Warning:** Never commit `.env` or any real API keys or database passwords to Git!

---

## Running the Project

### 1. Ingest Data & Initialize Db2 Native Vector Store
```bash
python submissions/bakebox-choco-ai/src/ingest.py
```
*Creates relational tables `BB_ORDERS`, `BB_ORDER_ITEMS` and ingests 384-dimensional native vectors into `BB_CHUNKS_VECTOR` via `DB2LlamaVS`.*

### 2. Execute Interactive Query Engine
```bash
python submissions/bakebox-choco-ai/src/query_engine.py
```

---

## Testing & Verification

Reviewers can verify the submission folder structure and metadata:

```bash
# Run official hackathon validator
python scripts/validate_submission.py submissions/bakebox-choco-ai
```

**Expected Output:**
```text
Validating 1 submission folder(s)...
Checking: submissions/bakebox-choco-ai
  ✅ PASSED all validation checks.
==================================================
ALL VALIDATION CHECKS PASSED.
```

---

## Screenshots & Demo
- **Live Local Demo:** `http://127.0.0.1:3000`
- **FastAPI Interactive Docs:** `http://127.0.0.1:8000/docs`
- Visual assets and screenshots are available in `docs/screenshots/`:
  - Architecture dataflow diagram
  - CHOCO AI interactive chat modal with 3-cake recommendations
  - Cart drawer with real cake thumbnails & "Ask CHOCO" action
  - Cake Details & Master Baker Advisory Panel

---

## Known Limitations & Future Roadmap
- **Current Limitations:** Vector embeddings currently run on CPU; GPU acceleration can further reduce batch embedding latency.
- **Future Roadmap:**
  - Multi-branch kitchen load balancing across Mathura, Vrindavan, and Govardhan branches.
  - Native integration with IBM watsonx.ai Granite 3.0 models.

---

## Team Members & Credits

| Name | GitHub Handle | Role / Contribution |
|---|---|---|
| Ayush Dhangar | [@AYUSHDHANGAR](https://github.com/AYUSHDHANGAR) | Full-Stack Architect, IBM Db2 Integration, Hybrid RAG Pipeline |
| Shri Ram Baker | Partner Domain | Mathura Bakery Operations, Recipes, Policies & Catalogs |
