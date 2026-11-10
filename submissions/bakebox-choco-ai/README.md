# BAKEBOX-AI: Autonomous AI Bakery Management & Customer Support
## CHOCO AI: Advanced Hybrid RAG & ACID Transactional Platform on IBM Db2

[![Tests](https://img.shields.io/badge/tests-64%20offline%20%26%20concurrency%20tests-brightgreen)](#automated-testing--verification)
[![Db2](https://img.shields.io/badge/IBM%20Db2-Community%20Edition%2012.1-blue)](#4-ibm-db2-integration-summary)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20Endpoints-009688)](#running-the-project)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-yellow)](#prerequisites)

> **One-Line Pitch:** An enterprise autonomous AI bakery management and customer engagement platform powered by **CHOCO AI** — combining IBM Db2 hybrid storage (relational ACID tables + native vector search via `DB2LlamaVS`), 3-way Reciprocal Rank Fusion (RRF: $k=60$ across Db2 Cosine + BM25 + TF-IDF), session isolation with TTL buffer memory, an in-engine Bill-of-Materials (BOM) CTE (`WITH RECIPE_BOM`), row-level concurrency locking (`SELECT FOR UPDATE WITH RS`), stored procedure `SP_RESERVE_CAKE_STOCK`, SHA-256 hash-chained audit trails (`BB_AUDIT_LOG`), least-privilege Db2 roles, and production FastAPI REST endpoints.

---


## Table of Contents
- [1. Project Overview](#1-project-overview)
- [2. Problem We Are Solving (Customer & Business POV)](#2-problem-we-are-solving-customer--business-pov)
- [3. The BAKEBOX Solution: CHOCO AI as a Digital Master Baker](#3-the-bakebox-solution-choco-ai-as-a-digital-master-baker)
- [4. IBM Db2 Integration Summary](#4-ibm-db2-integration-summary)
- [AI & Advanced Hybrid RAG Architecture (BM25 + TF-IDF + Db2 Vectors)](#ai--advanced-hybrid-rag-architecture-bm25--tf-idf--db2-vectors)
- [Agentic Tools (Hybrid RRF Ranked Cards & Protected Order Tracking)](#agentic-tools-hybrid-rrf-ranked-cards--protected-order-tracking)
- [Session Isolation & Buffer Memory](#session-isolation--buffer-memory)
- [Visual Proof & Application Screenshots](#visual-proof--application-screenshots)
- [Prerequisites](#prerequisites)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [Automated Testing & Verification](#automated-testing--verification)
- [Retrieval Quality Benchmark & Evaluation](#retrieval-quality-benchmark--evaluation)
- [Technical Defense & Architectural FAQ](#technical-defense--architectural-faq)
- [Demo & Submission Links](#demo--submission-links)
- [Known Limitations & Future Roadmap](#known-limitations--future-roadmap)
- [Team Members & Credits](#team-members--credits)
- [License](#license)

---

### 1. Project Overview
- **Project Type:** Business Solution / Enterprise AI Commerce
- **Project Title:** BAKEBOX-AI: Autonomous AI Bakery Assistant & Customer Support
- **Project Slug:** bakebox-choco-ai

#### Description (What We Are)
BAKEBOX is an autonomous AI-powered bakery management platform featuring **CHOCO AI** — an intelligent conversational assistant. It serves as the digital and technological extension of our family-owned business, **Shri Ram Baker's**, operating in Mathura for over 20 years across two established local branches in **Holigate** and **Gosna**.

#### Vision
While Shri Ram Baker's has traditionally served local customers through offline channels, BAKEBOX bridges the gap into digital commerce — scaling operations for online discovery, real-time order tracking, Happiness Guarantee support, and ACID-safe inventory management on IBM Db2.

---

### 2. Problem We Are Solving (Customer & Business POV)

#### Customer Perspective: Information Hesitation & Static Descriptions
- **Query Resolution & Product Clarity:** Customers often want exact details about ingredients, weight options, freshness, sweetness, and replacement terms that are difficult to hardcode across every static product card.
- **Sweetness & Flavor Guesswork:** Customers wonder about subjective taste profiles (*"Is this overly sweet, balanced, or dark bitter-sweet?"*) but hesitate to call store staff for minor questions.
- **The "Baking Knowledge" Gap:** Shoppers may not know the difference between standard eggless vs. authentic **Khoaa Eggless** bases, portion sizing (0.5kg vs. 1kg), or fresh-baking wait times.
- **Support Drop-off Post-9 PM:** Traditional bakery phone lines close early, leaving late-night celebration planners and order-tracking inquiries unassisted.

#### Business Perspective: Communication & Operational Bottlenecks
- **Lost Late-Night Conversions:** When human staff go offline after 9 PM, high-intent customers abandon carts due to unanswered questions.
- **Support Fatigue:** Kitchen and sales staff spend hours answering repetitive questions (*"Is this eggless?", "Kitna meetha hai?", "Reheat kaise karein?"*) instead of focusing on fresh baking and fulfillment.
- **Custom Cake & Base Complexity:** Explaining design options, flavor profiles, and eggless/Khoaa base availability manually across hundreds of SKUs does not scale.

---

### 3. The BAKEBOX Solution: CHOCO AI as a Digital Master Baker
CHOCO AI bridges both perspectives using **IBM Db2 Hybrid RAG & agentic tools**:

- **Instant Food & Ingredient Intelligence:** Answers deep questions about ingredients, sweetness levels, allergens, and sponge textures with zero wait time.
- **Contextual Cake Advisory:** Recommends up to 3 relevant cakes based on flavor, occasion, weight, and dietary choice (100% Pure Veg Khoaa Eggless or Egg).
- **Zero-Hallucination Order Tracking:** Queries live Db2 relational tables (`BB_ORDERS`, `BB_ORDER_ITEMS`) behind two-factor phone verification and PII masking.
- **24/7 Bilingual Query Resolution:** Maintains isolated multi-turn sessions via `gemini-1.5-flash` (with deterministic offline fallback) in bilingual Hinglish/English.
- **Culinary Care & Happiness Guarantee:** Delivers verified post-purchase advisories (e.g., dry tawa patty reheating) and automated Happiness Guarantee refund/replacement eligibility checks.
- **Target Audience:** Local bakery customers, celebration planners, dietary-conscious buyers, kitchen staff, and store managers.

---

### 4. IBM Db2 Integration Summary
- **IBM Db2 Edition / Environment:** IBM Db2 Community Edition (VS Code Extension Instance `IBMDB201` on Port 50000).
- **How IBM Db2 is Used:** IBM Db2 serves as the single unified data layer — simultaneously acting as a native high-dimensional vector store (via `DB2LlamaVS`) for embedding-based semantic retrieval AND as an ACID relational database housing live customer orders, cake stock, ingredient inventory, recipes, and cryptographic audit logs.
- **Db2 Connectors & Frameworks:** `ibm_db`, `ibm_db_dbi`, `llama-index-vector-stores-db2` (`DB2LlamaVS`).
- **Schema & Data Stored:**
  - `BB_CHUNKS_VECTOR`: Native vector table with `vector(384, FLOAT32)` column for dense semantic embeddings.
  - `BB_ORDERS` & `BB_ORDER_ITEMS`: Relational transactional order tables with `GENERATED ALWAYS AS IDENTITY` and `ON DELETE CASCADE` foreign key constraint.
  - `BB_CAKES`, `BB_INVENTORY`, `BB_RECIPES`: Relational cake stock, raw ingredient stock, and recipe BOM tables seeded idempotently by `src/ingest.py` and queried via the Db2 LUW `WITH RECIPE_BOM` Common Table Expression.
  - `BB_AUDIT_LOG`: Cryptographic SHA-256 hash-chained audit trail table serialized via `_AUDIT_CHAIN_LOCK` + `LOCK TABLE BB_AUDIT_LOG IN EXCLUSIVE MODE` and queried with `ORDER BY LOG_ID DESC FETCH FIRST 1 ROW ONLY`.
  - `V_ACTIVE_BAKERY_ORDERS` & B-Tree Indexes: Operational aggregation SQL view plus `IDX_BB_ORDER_PHONE`, `IDX_BB_ITEM_ORDER`, `IDX_BB_AUDIT_PREV`, `IDX_BB_AUDIT_CURR`, and `IDX_BB_RECIPE_CAKE`.
  - `SP_RESERVE_CAKE_STOCK`: Native IBM Db2 SQL PL stored procedure (`FOR UPDATE WITH RS` row-level locking) invoked via `ibm_db_dbi` `cursor.callproc()`.
  - **Least-Privilege Roles (`sql/db2_least_privilege.sql`):** Separates `BAKEBOX_READER_ROLE` (`DB2_READONLY_USER` for RAG & order lookup) from `BAKEBOX_APP_ROLE` (`DB2_USER` for column-scoped stock/status updates, `SP_RESERVE_CAKE_STOCK` execution, and append-only `BB_AUDIT_LOG` inserts).
- **Verification Steps:**
  1. `python submissions/bakebox-choco-ai/src/ingest.py` — Creates relational tables, view, indexes, stored procedure `SP_RESERVE_CAKE_STOCK`, seeds `BB_ORDERS`/`BB_ORDER_ITEMS`/`BB_CAKES`/`BB_INVENTORY`/`BB_RECIPES`, and ingests 384-d vectors into `BB_CHUNKS_VECTOR`.
  2. `python submissions/bakebox-choco-ai/src/query_engine.py` — Executes hybrid RRF retrieval and live order lookups.
  3. `python -m unittest discover -s submissions/bakebox-choco-ai/tests -v` — Runs complete offline unit, concurrency, audit-chain, and API guardrail test suite.
  4. `python scripts/validate_submission.py submissions/bakebox-choco-ai` — Passes official CI validation checks.

---

## AI & Advanced Hybrid RAG Architecture (BM25 + TF-IDF + Db2 Vectors)

1. **Local Dense Embedding:** Uses `BAAI/bge-small-en-v1.5` via FastEmbed / SentenceTransformers to generate 384-dimensional dense vectors locally.
2. **Dense Vector Search:** In-engine cosine distance search inside IBM Db2 (`BB_CHUNKS_VECTOR`).
3. **Sparse Lexical Search A (BM25):** Okapi BM25 term frequency matching across product names and descriptions.
4. **Sparse Lexical Search B (TF-IDF):** Sub-linear token matching across cake weights, bases, and flavors.
5. **3-Way Reciprocal Rank Fusion (RRF: $k=60$):** Combines dense and sparse channels to guarantee both conceptual relevance and exact keyword precision:
   $$\text{RRF Score}(d) = \frac{1}{60 + R_{\text{dense}}(d)} + \frac{1}{60 + R_{\text{bm25}}(d)} + \frac{1}{60 + R_{\text{tfidf}}(d)}$$
6. **Synthesis Engine:** Powered by Google Gemini 1.5 Flash (`gemini-1.5-flash`) for bilingual responses, with an automatic deterministic ground-truth fallback for offline environments (`--no-llm`).

---

## Agentic Tools (Hybrid RRF Ranked Cards & Protected Order Tracking)

All 3 core agentic tools are defined in `src/query_engine.py` and bound directly to **Google Gemini 1.5 Flash** via `_bind_gemini_tools()`:

### 1. `recommend_cakes(user_query: str, limit: int = 3)`
* **Purpose:** Precision cake product recommendation.
* **How it works:**
  * Queries IBM Db2 native vector store (`BB_CHUNKS_VECTOR`) using Cosine Similarity via `DB2LlamaVS`.
  * Concurrently queries BM25 (exact flavor keywords) and TF-IDF (weights, bases).
  * Fuses rankings with **3-Way Reciprocal Rank Fusion ($k=60$)**.
  * Enforces a quality threshold (`min_rrf_score >= 0.015`).
  * Returns **up to 3** clean JSON cards containing SKU, name, flavor, weight, price, and image URL.

### 2. `track_live_order(order_id: int, phone_number: str)`
* **Purpose:** Real-time backend transactional order lookup without human customer support latency.
* **How it works:**
  * Connects to IBM Db2 relational tables using `ibm_db_dbi`.
  * Executes a live SQL query joining `BB_ORDERS` and `BB_ORDER_ITEMS`.
  * **Two-Factor Authentication Barrier:** Requires both `order_id` and the customer's registered 10-digit mobile number to prevent unauthorized order snooping.
  * **Automated PII Masking:** Masks names (`R**** S*****`), phone numbers (`+91 ******3210`), and delivery addresses directly at the database retrieval boundary.
  * Provides ground-truth baking & delivery stages (`CONFIRMED` → `BAKING` → `OUT_FOR_DELIVERY` → `DELIVERED`).

### 3. `get_store_policy_or_advisory(user_query: str)`
* **Purpose:** Store agreements, baking timelines, and kitchen advice.
* **How it works:**
  * Performs hybrid retrieval strictly filtered for policy and advisory chunks.
  * Answers specific bakery rules:
    * Standard fresh-baking wait time: **3–4 hours** (ensuring all cakes are baked live on order).
    * Authentic **Khoaa Eggless (100% Pure Veg)** vs. Egg base options.
    * Snack reheating guidelines (**dry tawa / skillet only**, never microwave).

### How Gemini Directly Interacts with the Tools (Code Implementation)
In `src/query_engine.py`, Gemini is configured with native Python function calling:
```python
# 1. Bind Python functions as callable tools for Gemini
tools = self._bind_gemini_tools()
# 2. Supply tools and Master Baker system instruction
self.model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    tools=tools,
    system_instruction=system_instruction,
)
# 3. Delimit untrusted history/query and execute automatic function calling
delimited_prompt = _build_delimited_user_prompt(history_ctx, user_message)
chat = self.model.start_chat(enable_automatic_function_calling=True)
response = chat.send_message(delimited_prompt)
```
- **Automatic Function Execution:** With `enable_automatic_function_calling=True`, the Gemini SDK itself detects when a customer query requires database information, calls the Python tool, receives the database result, and synthesizes a polite, bilingual Hinglish response.
- **Deterministic Offline Fallback:** If the API key is not present or network is unavailable (`--no-llm`), the system includes a zero-hallucination deterministic dispatcher that executes the exact same tools directly, guaranteeing the application always functions reliably.

---

## Session Isolation & Buffer Memory

- **Session Isolation:** Each customer runs in an isolated session context (`session_id`), preventing cross-user data leakage.
- **Conversation Buffer Memory:** Uses a sliding-window `SessionBufferMemory` to retain recent conversation context across multi-turn interactions.
- **TTL Eviction:** Sessions inactive for more than 1 hour (3600s) are automatically evicted to ensure bounded memory usage.

---

## Visual Proof & Application Screenshots

All high-resolution production screenshots are cataloged in [`docs/screenshots/`](docs/screenshots/README.md):

| Feature / Proof | Screenshot Preview | Description |
|---|---|---|
| **IBM Db2 Database & Vectors** | ![IBM Db2 VS Code Extension](docs/screenshots/01_ibm_db2_extension_tables.png) | Active VS Code Db2 extension connected to `localhost@IBMDB201` showing all `BB_*` relational tables and `BB_CHUNKS_VECTOR` vector embeddings. |
| **Catalog & Multi-Branch Storefront** | ![Storefront Overview](docs/screenshots/07_storefront_catalog_overview.png) | Production storefront catalog showing multi-branch operational indicators, pure-veg badges, and the full multi-branch cake menu demonstrated in live video. |
| **Direct Product Querying** | ![Catalog Grid & Ask CHOCO](docs/screenshots/09_product_catalog_grid_actions.png) | 1-Click "Ask CHOCO" buttons directly embedded into product catalog cards for instant AI consultations. |
| **Real-Time Reasoning & RAG Retrieval** | ![Contextual Reasoning](docs/screenshots/10_ask_choco_contextual_query.png) | CHOCO AI dynamically ingesting cake SKU (`BB-STR-04-05kg`) into context with live reasoning indicator. |
| **Master Baker Advisory** | ![Master Baker Response](docs/screenshots/11_choco_master_baker_recommendation.png) | Rich Hinglish response with exact ingredients, base options (Khoaa eggless), and personalized recommendations. |
| **Live Order Tracking (Db2 Query)** | ![Live Order Status Confirmed](docs/screenshots/02_choco_order_status_confirmed.png) | Real-time SQL transactional lookup against `BB_ORDERS` and `BB_ORDER_ITEMS` for Order #1104 (`CONFIRMED`). |
| **Real-Time Delivery Lifecycle** | ![Order Status Delivered](docs/screenshots/03_choco_order_status_delivered.png) | Synchronized delivery update reflecting `DELIVERED` status and kitchen dispatch tracking. |
| **Customer Support & Policy Engine** | ![Happiness Guarantee Support](docs/screenshots/04_choco_happiness_guarantee_support.png) | Autonomous damaged order resolution referencing *Celebration Happiness Guarantee* from Db2 hybrid RAG. |
| **Refund & Re-Bake Workflow** | ![Refund Resolution](docs/screenshots/08_refund_replacement_resolution.png) | Instant step-by-step resolution offering 100% Free Re-Bake or Full Refund without human latency. |
| **Role-Based Authentication (RBAC)** | ![Role Selection Modal](docs/screenshots/05_bakebox_auth_role_modal.png) | Multi-role access control for Customer Demo, Super Admin, and Store Operator. |
| **Store Operator Console** | ![Operator Login](docs/screenshots/06_operator_login.png) | Store operator login for kitchen management and branch order routing. |

---

## Prerequisites
- Python >= 3.10
- Running IBM Db2 instance (e.g. `localhost:50000`, database `IBMDB201`)
- `pip` package manager
---

## Setup & Installation
```bash
# 1. Navigate to submission directory
cd submissions/bakebox-choco-ai
# 2. Install all required dependencies
pip install -r requirements.txt
```
---
## Configuration
Copy `.env.example` to `.env` and fill in your Db2 credentials:
```bash
cp .env.example .env
```
Edit `.env`:
```env
DB2_HOST=127.0.0.1
DB2_PORT=50000
DB2_DATABASE=IBMDB201
DB2_USER=your_db2_app_username_here
DB2_PASSWORD=your_db2_app_password_here
DB2_READONLY_USER=your_db2_reader_username_here  # Optional least-privilege RO role
DB2_READONLY_PASSWORD=your_db2_reader_password_here
GEMINI_MODEL=gemini-1.5-flash
GEMINI_API_KEY=your_gemini_api_key_here  # Optional: leave blank for deterministic mode
```
Optional (live Db2 least-privilege setup): run [`sql/db2_least_privilege.sql`](sql/db2_least_privilege.sql) once as schema owner after `src/ingest.py` creates the schema.

> **Security Hygiene:** Never commit `.env` or any production credentials to Git!

---

## Running the Project

### 1. Ingest Data & Initialize Db2 Tables
```bash
python src/ingest.py
```
*Creates relational tables (`BB_ORDERS`, `BB_ORDER_ITEMS`, `BB_CAKES`, `BB_INVENTORY`, `BB_RECIPES`, `BB_AUDIT_LOG`), view `V_ACTIVE_BAKERY_ORDERS`, indexes, stored procedure `SP_RESERVE_CAKE_STOCK`, seeds sample records, and ingests 384-dim dense vectors into `BB_CHUNKS_VECTOR` via `DB2LlamaVS`.*

### 2. Execute Interactive Query Engine
```bash
# Run with Gemini 1.5 Flash natural language synthesis
python src/query_engine.py
# Or force deterministic offline mode explicitly
python src/query_engine.py --no-llm
```

### 3. Start the Production FastAPI Server
```bash
uvicorn src.api:app --reload --host 127.0.0.1 --port 8000
# Open Swagger UI at: http://127.0.0.1:8000/docs
```

---

## Automated Testing & Verification
Reviewers can verify the submission offline with zero external database or API keys:

### 1. Run Official Hackathon Submission Validator
```bash
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

### 2. Run Full Offline Unit, Concurrency, Audit & Security Test Suite
```bash
python -m unittest discover -s submissions/bakebox-choco-ai/tests -v
```
**Verified Offline Result (64 tests across 6 test modules):**
- `test_audit_chain.py` (9 tests: genesis block, hash chaining, tamper detection, multi-thread concurrency)
- `test_guardrails_and_api.py` (12 tests: prompt injection, SQLi defense, 2FA `/refund` endpoint, direct engine guardrail, least-privilege RO connection string)
- `test_order_concurrency.py` (12 tests: `FOR UPDATE WITH RS` race stress, `WITH RECIPE_BOM` CTE, `SP_RESERVE_CAKE_STOCK` `callproc()`, `ingest.py` seeding)
- `test_retrieval.py` (14 tests: RRF, BM25, routing, 2FA order tracking, PII masking; 1 test skips cleanly if `llama_index` is not installed)
- `test_rrf_fusion.py` (10 tests: RRF `k=60` formula, BM25 saturation, boundary cases)
- `test_session_memory.py` (7 tests: multi-tenant isolation, sliding window, TTL, PII masking)

### 3. Run Empirical 30-Query Retrieval Benchmark
```bash
python submissions/bakebox-choco-ai/tests/evaluate_retrieval.py
```
**Verified Offline Result (Strict ID Matching across All 4 Categories):**
```text
Total Benchmark Queries : 30
Hit Rate @ 1 (Top-1)    : 86.7% (26/30)
Hit Rate @ 3 (Top-3)    : 100.0% (30/30)
Mean Reciprocal Rank    : 0.93 MRR
Average CPU Latency     : < 1.0ms per query (lexical offline mode)
[PASSED] Empirical evaluation benchmark successfully verified!
```

---

## Retrieval Quality Benchmark & Evaluation

Empirical evaluation across **30 curated bakery queries** (semantic cravings, exact SKU lookups, dietary/base constraints, and strictly verified policy/advisory ID matching):

| Metric | Measured Result | Notes |
|---|---:|---|
| **Hit Rate @ 1 (Top-1)** | **86.7% (26/30)** | Exact SKU, product title, and primary flavor queries rank #1. |
| **Hit Rate @ 3 (Top-3)** | **100.0% (30/30)** | All 30 queries retrieve the ground-truth SKU or policy document within Top-3. |
| **Mean Reciprocal Rank (MRR)** | **0.93** | Computed over all 30 queries including strict policy ID verification. |
| **3-Way RRF Constant** | **$k = 60$** | Fuses `DB2LlamaVS` dense cosine search + Okapi BM25 + TF-IDF. |

---

## Technical Defense & Architectural FAQ

### Q1: Why choose Reciprocal Rank Fusion (RRF: $k=60$) over linear score normalization?
- **Score Scale Incompatibility:** Dense cosine similarity lies in $[0, 1]$, Okapi BM25 outputs unbounded positive scores, and TF-IDF outputs $[0, 1]$. RRF combines ordinal ranks via $\sum_m \frac{1}{60 + \text{rank}_m(d) + 1}$, preventing lexical outliers from drowning out semantic matches.

### Q2: How are concurrent stock reservations and audit-chain writes protected?
- **Stock Reservations:** Uses `SELECT STOCK_QTY FROM BB_CAKES WHERE CAKE_ID = ? FOR UPDATE WITH RS` (and `SP_RESERVE_CAKE_STOCK` via `cursor.callproc()`).
- **Audit Log Chain:** `append_audit_log()` serializes writers with `_AUDIT_CHAIN_LOCK` plus `LOCK TABLE BB_AUDIT_LOG IN EXCLUSIVE MODE` and reads the tail hash via `ORDER BY LOG_ID DESC FETCH FIRST 1 ROW ONLY` inside a single atomic transaction.

### Q3: How are customer PII and LLM prompts protected?
- **Order & Refund 2FA:** Both order lookup (`GET /api/orders/{id}`) and refunds (`POST /api/orders/{id}/refund`) require matching `order_id` + 10-digit customer phone via parameterized `RIGHT(REPLACE(...), 10) = ?`, with PII masked at the database boundary.
- **Prompt Defense:** `check_prompt_security()` runs directly inside `ChocoQueryEngine.query()` as well as the FastAPI layer, and untrusted history/queries are wrapped inside explicit `<conversation_history_readonly>` and `<customer_query_untrusted>` delimiters.

---

## Demo & Submission Links

- **Demo Video (YouTube Walkthrough):** [https://youtu.be/NLrRq6FX358?si=hjcFKSU-FCOhvToW](https://youtu.be/NLrRq6FX358?si=hjcFKSU-FCOhvToW)
- **LinkedIn Post:** [https://lnkd.in/p/gZXgB8B4](https://lnkd.in/p/gZXgB8B4)
- **Hackathon PR Submission Repository:** [https://github.com/AYUSHDHANGAR/IBM_Db2_TechX_Project_Submission](https://github.com/AYUSHDHANGAR/IBM_Db2_TechX_Project_Submission)
- **Full-Stack Application Repository (React 18 Storefront + FastAPI Backend):** [https://github.com/AYUSHDHANGAR/BAKE_BOX--AI-ASSISTENT-FOR-BAKERY](https://github.com/AYUSHDHANGAR/BAKE_BOX--AI-ASSISTENT-FOR-BAKERY)
- **Standalone Seed Datasets:** High-quality JSON records provided in [`data/sample_catalog.json`](data/sample_catalog.json) and [`data/sample_orders.json`](data/sample_orders.json).

---

## Known Limitations & Future Roadmap

- **Current Scope:**
  - Vector embeddings execute via local CPU; GPU acceleration can further minimize batch vectorization latency.
  - Session conversation memory is intentionally implemented in-memory (`SessionBufferMemory`) with automatic 1-hour TTL expiration for lightweight, zero-dependency hackathon demonstration.
- **Future Roadmap:**
  - **Persistent Session Storage:** Transition from in-memory session buffer to Redis / Db2-backed TTL session cache for multi-worker horizontal scaling.
  - **Payment & Invoicing Gateway:** Direct UPI integration with automated receipt generation and live order state transitions in IBM Db2.
  - **Multi-Branch Kitchen Load Balancing:** Intelligent dispatch routing between Holigate and Gosna kitchens based on oven capacity, with planned future expansion to Vrindavan and Govardhan.
  - **Predictive Inventory Forecasting:** Time-series demand forecasting on historical Db2 order records to optimize fresh daily baking schedules.

---

## Team Members & Credits

| Name | GitHub Handle | Role / Contribution |
|---|---|---|
| **Ayush Dhangar** | [@AYUSHDHANGAR](https://github.com/AYUSHDHANGAR) | BTech CSE-AIML, 4th Year · Ex-Intern Pantech Prolab Pvt Ltd (Machine Learning) · AI Systems & Db2 Solutions Architect |

---
## License

Distributed under the MIT License. Built for the IBM Db2 TechX Summit 2026.
