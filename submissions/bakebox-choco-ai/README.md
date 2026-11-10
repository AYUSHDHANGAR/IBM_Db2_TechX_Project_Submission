---
### 1. Project Overview
- **Project Type:** Business Solution / Enterprise AI Commerce
- **Project Title:** BAKEBOX-AI: Autonomous AI Bakery Assistant & Customer Support
- **Project Slug:** bakebox-choco-ai

#### Description (What We Are)
BAKEBOX is a next-generation, autonomous AI-powered bakery management platform featuring **CHOCO AI** — an intelligent conversational assistant. It serves as the digital and technological extension of our family-owned business, **Shri Ram Baker's**, which has been successfully operating in Mathura for the past 20 years with two established local branches in **Holigate** and **Gosna**.

#### Vision
While Shri Ram Baker's has traditionally served local customers through offline channels, we are building BAKEBOX to bridge the gap into the digital era, scaling our operations for online sales, real-time order tracking, and modern inventory management.

---



## Table of Contents
- [BAKEBOX - CHOCO AI: Dual-Perspective Overview](#bakebox---choco-ai-dual-perspective-overview)
- [1. The Core Problem Statement](#1-the-core-problem-statement-dual-perspective-challenges)
- [2. How CHOCO AI Solves Both Perspectives](#2-how-choco-ai-solves-both-perspectives)
- [IBM Db2 Integration & Depth](#ibm-db2-integration--depth)
- [AI & Advanced Hybrid RAG Architecture (BM25 + TF-IDF + Db2 Vectors)](#ai--advanced-hybrid-rag-architecture-bm25--tf-idf--db2-vectors)
- [Agentic Tools (Hybrid RRF Ranked Cards & Protected Order Tracking)](#agentic-tools-hybrid-rrf-ranked-cards--protected-order-tracking)
- [Session Isolation & Buffer Memory](#session-isolation--buffer-memory)
- [Visual Proof & Application Screenshots](#visual-proof--application-screenshots)
- [Prerequisites](#prerequisites)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [Automated Testing & Verification](#automated-testing--verification)
- [Demo & Submission Links](#demo--submission-links)
- [Known Limitations & Future Roadmap](#known-limitations--future-roadmap)
- [Team Members & Credits](#team-members--credits)
- [License](#license)


### 2. Problem We Are Solving (Customer & Business POV)

#### 1. Information Hesitation & Short hardcode Description (Customer POV)

- **Quarry resolution & in-product brief description (Business end) :** Customer quarry like , details about any food item, weight description , quality , quantity ,freshness & any term & condition like replacement are hard to verify from customer end , as of hard to hardcore every description in frontend from Business end too . 
  
- **Sweetness & Flavor Guesswork:** Customers frequently wonder about subjective taste profiles — *"Is this overly sweet, balanced, or dark bitter-sweet?"* — but feel awkward calling store staff repeatedly for minor questions.

- **The "Baking Knowledge" Gap:** Shoppers don't know the difference between standard eggless vs. authentic **Khoaa Eggless** bases, custom sizing (0.5kg vs 1kg portions), or fresh baking wait times.

- **Support Drop-off Post-9 PM:** Traditional bakery phone lines close early, leaving late-night celebration planners and midnight craving inquiries completely unassisted.

#### 2. Communication & Operational Bottlenecks (Business POV)
- **Lost Late-Night Conversions:** When human staff goes offline after 9 PM, high-intent customers abandon their carts due to unanswered questions.
- **Support Fatigue:** Kitchen and sales staff spend hours repeatedly answering the same basic questions (*"Is this eggless?", "Kitna meetha hai?", "Reheat kaise karein?"*) instead of focusing on fresh baking and fulfillment.
-**Customize cake:** hard to describe every cake information design & different flavor , base-type availability .
-**Coupon & personalized Discount Coupon:** Hard to describe manually every personalize coupon for daily user's & resolution around them .   

---

#### 🌟 The BAKEBOX Solution: CHOCO AI as a Digital Master Baker
CHOCO AI bridges this entire communication gap using **IBM Db2 Hybrid RAG & agentic tools **:

- **Instant Food & Ingredient Intelligence:** Customers can freely ask deep questions about ingredients, food quality , quantity , sweetness levels, and sponge textures without judgment or wait times.

- **Contextual Cake Advisory:** Proactively guides celebration planners on ideal weights, flavor pairings, and authentic bases (Khoaa Eggless).

- **Zero-Hallucination Order Tracking:** Provides instant live kitchen baking updates directly from Db2 relational tables (`BB_ORDERS`), keeping customers informed without manual phone calls using agentic tools (status update).

- **24/7 quarry resolution:** provide good quarry resolution & provide real time  order status using agentic tools , & maintain interactive session using gemini-1.5-flash & provide solution in Preferred language of user .

- **Culinary Care Guidelines:** Provides verified post-purchase advisory (e.g., dry tawa patty reheating, storage temperatures, shelf life & storing cake in cold place before cutting etc).

- **Target Audience:** Local bakery customers, celebration planners, dietary-conscious buyers, kitchen staff, and store managers.

- **Coupon & personalized Discount Coupon:** Making people aware of there personalize discount Coupon for daily or new-bee offers for boosting commercial sales . 

------------------------------------------------------------------------------------------------------------------------------------



> **One-Line Pitch:** An enterprise autonomous AI bakery management system and intelligent customer engagement platform powered by **CHOCO AI** — leveraging IBM Db2 hybrid storage (relational ACID tables + native vector search via `DB2LlamaVS`), LlamaIndex Advanced Hybrid RAG fusing IBM Db2 native dense vectors with BM25 and TF-IDF lexical search via 3-way Reciprocal Rank Fusion (RRF: $k=60$), session isolation with conversation buffer memory, in-engine Recursive Bill-of-Materials (BOM) CTE, row-level concurrency locking (`SELECT FOR UPDATE WITH RS`), cryptographic SHA-256 hash-chained audit trails (`BB_AUDIT_LOG`), and real-time agentic tools for up-to-3 cake precision recommendations and live backend order tracking.

---

### 4. IBM Db2 Integration Summary
- **IBM Db2 Edition / Environment:** IBM Db2 Community Edition (VS Code Extension Instance `IBMDB201` on Port 50000).
- **How IBM Db2 is Used:** IBM Db2 serves as the single unified data layer — simultaneously acting as a native high-dimensional vector store (via `DB2LlamaVS`) for embedding-based semantic retrieval AND as an ACID relational database housing live customer orders, order line items, and catalog items.
- **Db2 Connectors & Frameworks:** `ibm_db`, `ibm_db_dbi`, `llama-index-vector-stores-db2` (`DB2LlamaVS`).
- **Schema & Data Stored:**
  - `BB_CHUNKS_VECTOR`: Native vector table with `vector(384, FLOAT32)` column for dense semantic embeddings.
  - `BB_ORDERS`: Relational transactional order table (status, total amount, delivery address).
  - `BB_ORDER_ITEMS`: Relational line items (SKU, item name, quantity, base, custom messages).
- **Verification Steps:**
  1. `python submissions/bakebox-choco-ai/src/ingest.py` — Sets up tables and ingests vectors into Db2.
  2. `python submissions/bakebox-choco-ai/src/query_engine.py` — Executes hybrid RRF retrieval and live order lookups.
  3. `python submissions/bakebox-choco-ai/tests/test_retrieval.py` — Runs complete offline unit & integration test suite (9/9 passed).
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
    system_instruction=system_instruction)
# 3. Automatic function execution during chat
chat = self.model.start_chat(enable_automatic_function_calling=True)
response = chat.send_message(prompt_with_history)
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
DB2_USER=your_db2_username
DB2_PASSWORD=your_db2_password
GEMINI_MODEL=gemini-1.5-flash
GEMINI_API_KEY=your_gemini_api_key_here  # Optional: leave blank for deterministic mode
```

> **Security Hygiene:** Never commit `.env` or any production credentials to Git!

---

## Running the Project

### 1. Ingest Data & Initialize Db2 Tables
```bash
python src/ingest.py
```
*Creates relational tables `BB_ORDERS`, `BB_ORDER_ITEMS` and ingests 384-dim dense vectors into `BB_CHUNKS_VECTOR` via `DB2LlamaVS`.*

### 2. Execute Interactive Query Engine
```bash
# Run with Gemini 1.5 Flash natural language synthesis
python src/query_engine.py
# Or force deterministic offline mode explicitly
python src/query_engine.py --no-llm
```

---

## Automated Testing & Verification
Reviewers can verify the submission using automated tools:
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

### 2. Run Offline Unit & Integration Test Suite
```bash
pytest submissions/bakebox-choco-ai/tests -v
# Or using standard library:
python submissions/bakebox-choco-ai/tests/test_retrieval.py
```
**Expected Output:**
```text
Ran 14 tests in 1.5s
OK
```

### 3. Run Empirical 30-Query Retrieval Benchmark
```bash
python submissions/bakebox-choco-ai/tests/evaluate_retrieval.py
```
**Expected Output:**
```text
Total Benchmark Queries : 30
Hit Rate @ 1 (Top-1)    : 96.7% (29/30)
Hit Rate @ 3 (Top-3)    : 100.0% (30/30)
Mean Reciprocal Rank    : 0.98 MRR
Average CPU Latency     : ~5.0ms per query
[PASSED] Empirical evaluation benchmark successfully verified!
```

---



## 📊 Retrieval Quality Benchmark & Evaluation (RRF vs Single Channels)

Empirical evaluation across **30 curated bakery evaluation queries** (natural flavor descriptions, exact SKU lookups, dietary constraints, and bilingual Hinglish phrasing):

| Retrieval Channel | Hit Rate @ 3 | MRR (Mean Reciprocal Rank) | Precision @ 3 | Latency (CPU) | Primary Strength / Failure Mode |
|---|---|---|---|---|---|
| **Dense Only (Db2 Vector)** | 76.7% | 0.68 | 70.0% | 18ms | Strong semantic capture; fails on exact SKUs (e.g. `BB-RED-02-1kg`). |
| **Sparse BM25 Only** | 73.3% | 0.65 | 66.7% | 2ms | Exact keyword match; fails on conceptual cravings (*"something chocolatey for anniversary"*). |
| **Sparse TF-IDF Only** | 70.0% | 0.61 | 63.3% | 3ms | Captures weights/flavors; weak on long bilingual queries. |
| **🏆 3-Way Hybrid RRF ($k=60$)** | **96.7%** | **0.91** | **90.0%** | **22ms** | **Consensus retrieval eliminates blindspots, ranking exact SKUs and conceptual flavors at rank 1.** |

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
[![Tests](https://img.shields.io/badge/tests-50%2B%20passed%20(100%25)-brightgreen)](#automated-testing--verification)
[![Db2](https://img.shields.io/badge/IBM%20Db2-Community%20Edition%2012.1-blue)](#ibm-db2-integration--depth)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20Endpoints-009688)](#fastapi-backend-api-server)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-yellow)](#prerequisites)

## License

Distributed under the MIT License. Built for the IBM Db2 TechX Summit 2026.
