# BAKEBOX-AI: AUTONOMOUS AI Bakery Management AND CUSTOMER SUPPORT

> **One-Line Pitch:** An enterprise-grade autonomous AI customer care, real-time kitchen order tracking, and master baker management platform for Shri Ram Baker (Mathura), powered by IBM Db2 native vector search (`DB2LlamaVS`), LlamaIndex Hybrid RRF ($k=60$), and live transactional order intelligence with zero external vector databases.

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

Traditional artisanal bakery and fresh-food retail operations in tier-2 cities like Mathura face critical operational bottlenecks:

1. **Lack of Instant Customer Care & Dietary Resolution:** Bakery customers struggle to obtain instant assistance for custom cake inquiries, dietary doubts (e.g., 100% eggless / Jain preparation), store policies, or submitting order feedback without calling the shop or waiting at crowded counters.
2. **Opaque Kitchen Order Progress:** Once an order is placed, customers have no self-service mechanism to check their live preparation and kitchen baking status. Because handcrafted fresh cakes require 3 to 4 hours of soaking and cold-setting, customers make repeated follow-up calls, creating anxiety and frustration.
3. **Overwhelmed Store Staff During Peak Hours:** Store operators and kitchen bakers get overwhelmed managing manual customer care, status inquiries, and vast catalog lookups simultaneously during peak festival and celebration hours.
4. **AI Hallucinations in Food Commerce:** Standard generic AI chatbots hallucinate non-existent cake flavors, quote arbitrary prices, or give dangerous food heating advice (such as microwaving puff pastries instead of warming them on a dry tawa).
5. **Target Beneficiaries:** 
   - **Bakery Customers:** Get 24/7 instant customer care, visual cake recommendations, easy order placement, and live order status tracking without phone calls.
   - **Bakery Owners & Support Staff:** Automate daily customer query resolution, live status updates, and order workflows, saving hours of manual counter and phone work.
   - **Local Retail Businesses:** Gain a proven, practical digital system that unifies customer support, feedback handling, and live kitchen operations.

---

## Solution Overview

**BAKEBOX** solves these challenges through a unified digital platform and an autonomous master baker AI assistant (**CHOCO AI**), deeply coupled with **IBM Db2**:

1. **24/7 AI Customer Care & Query Resolution (CHOCO AI):** An intelligent assistant that instantly resolves customer queries regarding 610+ cakes, custom designs, pricing, and store policies, while handling customer support and feedback seamlessly.
2. **Real-Time Order Status Tracking & Updates:** Customers can directly ask CHOCO AI for their live order status (e.g., *Confirmed*, *Baking in Khatoti Kua kitchen*, or *Ready for pickup*). Store staff update statuses in real time through the connected system, and the AI retrieves live ground truth directly from IBM Db2.
3. **Interactive Visual Cake Selection (Strict 3-Cake Selection Rule):** Instead of plain text replies, the AI engine renders 3 verified, interactive cake cards (with photos, verified pricing, base selection, and SKUs) right inside the chat window so customers can compare and order effortlessly.
4. **Isolated Customer Conversation Memory:** Maintains private, user-isolated chat histories (`BB_USER_CONVERSATION_BUFFER`) inside IBM Db2 so every customer receives personalized support and follow-up assistance without session cross-contamination.
5. **Culturally Grounded Persona:** Speaks with a warm, authentic Mathura Hinglish persona (*"Radhe Radhe ji! Shri Ram Baker's BAKEBOX mein aapka swagat hai!"*) backed by authentic baking advisory rules.

---

## IBM Db2 Integration

IBM Db2 (`IBMDB201`) serves as the single source of truth for all operational, analytical, conversational, and vector data, eliminating the need for external vector databases.

- **Db2 Edition & Environment:** 
  - IBM Db2 Community Edition (v12.1+) running on Docker / VS Code Extension Instance (`IBMDB201`) on port `50000`.
  - Configured, inspected, and validated using the official **IBM Db2 for Visual Studio Code Extension**, enabling direct SQL query execution, vector column validation, and table monitoring.
- **Connector / Driver Used:** 
  - Official Python drivers `ibm_db` and `ibm_db_dbi`.
  - Official LlamaIndex vector store connector `llama-index-vector-stores-db2` (`DB2LlamaVS`).
- **Database Schema / Data Models:**
  - `BB_CHUNKS_VECTOR` / `BB_RAG_CHUNKS`: Native vector table created and managed via `DB2LlamaVS` storing 746 embedded chunks with schema `(id VARCHAR(64) PRIMARY KEY, doc_id VARCHAR(64), embedding vector(384, FLOAT32), node_info BLOB, metadata BLOB, text CLOB)`.
  - `BB_ORDERS`: Relational transactional table tracking live customer orders `(order_id INT PRIMARY KEY, user_id INT, customer_name VARCHAR(100), customer_phone VARCHAR(20), order_type VARCHAR(50), order_status VARCHAR(50), total_amount DECIMAL(10,2), delivery_address VARCHAR(255), special_notes VARCHAR(255))`.
  - `BB_ORDER_ITEMS`: Relational line items tracking customized orders `(item_id INT IDENTITY, order_id INT, sku_id VARCHAR(64), item_name VARCHAR(120), quantity INT, unit_price DECIMAL(10,2), cake_base VARCHAR(50), cake_weight VARCHAR(20), custom_message VARCHAR(255))`.
  - `BB_CAKES`, `BB_CUSTOM_CAKES`, `BB_PARTY_ACCESSORIES`: Structured inventory tables housing the complete 610+ item bakery catalog.
  - `BB_USER_CONVERSATION_BUFFER` & `BB_USERS`: Stores authenticated customer identities and user-isolated multi-turn conversational history.
- **Key Queries & Operations:**
  - **In-Engine Native Cosine Vector Search:** Hardware-accelerated Cosine similarity computed directly inside the Db2 engine (`DB2LlamaVS.query()`), eliminating external vector DB latency and maintenance overhead.
  - **Relational Ground-Truth Joins:** Live parameterized SQL joins across `BB_ORDERS` and `BB_ORDER_ITEMS` triggered upon order inquiry intent, guaranteeing zero hallucination in order status.

---

## AI / LLM Architecture

- **Framework:** LlamaIndex 0.14 (`llama-index-core` and `llama-index-vector-stores-db2`).
- **Embedding Model:** HuggingFace `BAAI/bge-small-en-v1.5` (384 dimensions) via FastEmbed.
- **LLM / Synthesis Provider:** Google Gemini API (`gemini-3.5-flash-lite`, 1.2s response latency) with Mathura bakery domain guardrails.
- **Hybrid Retrieval Pipeline (Dense + Sparse RRF):**
  1. **Intent Classification:** Classifies customer queries into:
     - *Recommendation Intent:* (e.g., *"Show me anniversary chocolate cake"*)
     - *Live Order Tracking Intent:* (e.g., *"Status of order #1002"*)
     - *Store Policy / Advisory Intent:* (e.g., *"Patties reheating rules"*)
  2. **Reciprocal Rank Fusion (RRF: $k=60$):** Fuses dense vector similarity from IBM Db2 `DB2LlamaVS` with sparse lexical TF-IDF matching:
     $$\text{RRF Score}(d) = \frac{1}{60 + R_{\text{dense}}(d)} + \frac{1}{60 + R_{\text{sparse}}(d)}$$
     Ensures exact match on weights (e.g., 0.5kg vs 1kg) and bases (eggless vs regular) alongside deep semantic understanding.
  3. **Strict 3-Cake Selection Tool:** Generates exactly 3 verified product cards with validated SKUs, pricing, and local assets, avoiding chat screen clutter.
  4. **Ground-Truth Order Verification:** Intercepts order inquiries to pull directly from Db2 relational tables, returning accurate kitchen statuses (*BAKING at Khatoti Kua kitchen with 3-4 hours preparation notice*) and cleanly suppressing product recommendation cards.

---

## Tech Stack

- **Database Engine:** IBM Db2 (v12.1+ Community Edition / `IBMDB201` via IBM Db2 VS Code Extension)
- **Database Connectors:** `ibm_db`, `ibm_db_dbi`, `llama-index-vector-stores-db2` (`DB2LlamaVS`)
- **Backend Framework:** Python 3.11+, FastAPI, Uvicorn, Pydantic
- **AI & RAG Pipeline:** LlamaIndex, FastEmbed (`BAAI/bge-small-en-v1.5`), Google Gemini 3.5 Flash Lite, FlashRank Reranker
- **Frontend / Storefront:** React 18, Vite, Tailwind CSS, Lucide Icons, Three.js 3D Storefront

---

## Prerequisites

- Python >= 3.10
- Running IBM Db2 instance (Local Docker container or VS Code Db2 extension instance on port `50000`, e.g., `IBMDB201`)
- Node.js >= 18 (for the React storefront UI)

---

## Setup & Installation

```bash
# 1. Clone your fork and switch to the submission directory
cd submissions/bakebox-choco-ai

# 2. Install Python dependencies
pip install llama-index-core llama-index-vector-stores-db2 ibm-db fastembed scikit-learn
```

---

## Configuration

Copy `.env.example` to `.env` and fill in your IBM Db2 credentials:

```bash
cp .env.example .env
```

```env
# IBM Db2 Connection Parameters (Local Community Edition / IBMDB201)
DB2_HOST=127.0.0.1
DB2_PORT=50000
DB2_DATABASE=IBMDB201
DB2_USER=your_db2_user
DB2_PASSWORD=your_db2_password

# Embedding Model Configuration
EMBEDDING_MODEL_NAME=BAAI/bge-small-en-v1.5
EMBEDDING_DIM=384

# LLM Synthesis API
GEMINI_API_KEY=your_gemini_api_key
```

> **Security Notice:** Never commit `.env` or sensitive production credentials to Git!

---

## Running the Project

### 1. Ingest Data & Initialize Db2 Native Vector Store
```bash
python submissions/bakebox-choco-ai/src/ingest.py
```
*Initializes relational tables `BB_ORDERS`, `BB_ORDER_ITEMS` and ingests 384-dimensional native vectors into `BB_CHUNKS_VECTOR` via `DB2LlamaVS`.*

### 2. Execute Interactive Query Engine
```bash
python submissions/bakebox-choco-ai/src/query_engine.py
```

---

## Testing & Verification

Reviewers can verify the submission folder structure, metadata, and functionality using the official hackathon validator:

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

### Verification Test Scenarios
1. **Cake Recommendation Intent:** Query *"Show me red velvet cake for anniversary"* → Returns **EXACTLY 3 verified cake cards** (`BB-RED-02-1kg`, `BB-RED-05-1kg`, `BB-RED-01-1kg`) with ₹649 price and verified local image paths.
2. **Live Order Status Tracking:** Query *"Status of order #1002"* → Queries `BB_ORDERS` in IBM Db2, reports **BAKING** at Khatoti Kua kitchen, and suppresses product cards (`ui_cards: []`).
3. **Store Guidelines & Advisory:** Query *"Patties ko reheat kaise karna chahiye?"* → Advises warming on a dry tawa for 2-3 minutes, never microwave.

---

## Screenshots & Demo

- **Video Walkthrough (YouTube):** [Watch BAKEBOX Demo on YouTube](https://youtu.be/MvH82OEsDUA?si=ls0FZOuDwLTDWvQO)
- **LinkedIn Project Announcement:** [View Hackathon Post on LinkedIn](https://lnkd.in/p/gtXgu6wq)
- **LinkedIn Profile:** [Ayush Dhangar on LinkedIn](http://www.linkedin.com/in/ayush-dhangar-63b190442)
- **Live Local Demo:** `http://127.0.0.1:3000`
- **FastAPI Interactive Docs:** `http://127.0.0.1:8000/docs`
- **Visual Assets in `docs/screenshots/`:**
  - Architecture data flow diagram
  - CHOCO AI interactive chat modal with 3-cake precision cards
  - Cart drawer with live thumbnails and "Ask CHOCO" action
  - Cake Details & Master Baker Advisory Panel
  - Terminal logs demonstrating successful `DB2LlamaVS` ingestion and hybrid retrieval

---

## Known Limitations & Future Roadmap

- **Current Limitations:** Vector embeddings currently run on CPU; GPU acceleration can further minimize initial ingestion latency.
- **Future Roadmap:**
  - Multi-branch kitchen load balancing across Mathura, Vrindavan, and Govardhan branches.
  - Native integration with IBM watsonx.ai Granite 3.0 foundation models.

---

## Team Members & Credits

| Name | GitHub Handle | Email | Role / Contribution |
|---|---|---|---|
| Ayush Dhangar | [@AYUSHDHANGAR](https://github.com/AYUSHDHANGAR) | ayush.dhangar2024@glbajgroup.org | Full-Stack Architect, IBM Db2 Integration, Hybrid RAG Pipeline |
| Shri Ram Baker | Partner Domain | Mathura, UP | Bakery Domain Knowledge, Recipes, Catalog & Operational Policies |

*IBM Db2 TechX Summit 2026 (Db2Hack)*
