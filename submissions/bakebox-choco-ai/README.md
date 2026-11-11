# BAKEBOX-AI: Autonomous AI Bakery Management & Customer Support
## CHOCO AI — Enterprise Hybrid RAG, Recursive BOM & ACID Concurrency on IBM Db2 12.1

[![Tests](https://img.shields.io/badge/tests-72%20passed%20%7C%200%20failed-brightgreen)](#automated-testing--verification)
[![IBM Db2](https://img.shields.io/badge/IBM%20Db2-LUW%2012.1%20Native%20Vector%20%2B%20SQL%20PL-054ADA)](#ibm-db2-integration--depth)
[![FastAPI](https://img.shields.io/badge/FastAPI-10%20REST%20Endpoints%20%2B%20%2Fdemo%20UI-009688)](#rest-api--interactive-playground)
[![Security](https://img.shields.io/badge/Security-RBAC%20%7C%202FA%20%7C%20SHA--256%20Audit-orange)](#security--privacy-architecture)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%2B-blue)](#prerequisites)

> **One-Line Pitch:** **BAKEBOX-AI (CHOCO AI)** turns **IBM Db2 LUW 12.1** into a unified AI and transactional backbone for a real 20-year Mathura bakery (*Shri Ram Baker's*) — fusing **Db2 native `VECTOR(384, FLOAT32)` cosine search with BSON metadata pushdown (`DB2LlamaVS`)**, **3-Way Reciprocal Rank Fusion ($k=60$)**, **Hinglish CRAG & Self-RAG verification**, **in-database multi-level Recursive Bill-of-Materials (BOM) CTEs**, **row-level `FOR UPDATE WITH RS` stock locking via `SP_RESERVE_CAKE_STOCK`**, **Db2-persisted session memory (`BB_USER_CONVERSATION_BUFFER`)**, and a **SHA-256 hash-chained `BB_AUDIT_LOG`** exposed through a hardened FastAPI server and interactive `/demo` playground.

---

## ⚡ Judge Quickstart (Verify Everything in 60 Seconds — Zero Docker Required)

Reviewers can validate all 72 unit/concurrency/security/HTTP tests, inspect the 30-query retrieval ablation benchmark, and launch the live interactive FastAPI playground **without live database credentials or API keys** (backed by our thread-safe, ACID snapshot-rollback PEP 249 `MockDb2Connection` and offline cosine vector engine):

```bash
# 1. Navigate to the submission package & install dependencies
cd submissions/bakebox-choco-ai
pip install -r requirements.txt

# 2. Verify all 72 automated unit, HTTP API, concurrency, security & audit tests
python -m unittest discover -s tests -v

# 3. Execute the 30-query, 4-channel empirical retrieval ablation benchmark
python tests/evaluate_retrieval.py

# 4. Launch the FastAPI REST server + Interactive Judge Console
uvicorn src.api:app --reload
# Interactive Web Playground : http://127.0.0.1:8000/demo
# OpenAPI / Swagger Docs     : http://127.0.0.1:8000/docs
```

*(To connect to live IBM Db2 12.1 Community Edition via Docker instead of offline simulation, see [Running with Live IBM Db2 (Docker)](#-running-with-live-ibm-db2-docker-mode).)*

---

## 🏆 Official Evaluation Rubric Coverage Matrix

| Evaluation Dimension | Weight | Architectural & Code Proof | Primary Source Files |
| :--- | :---: | :--- | :--- |
| **1. IBM Db2 Integration & Depth** | **25%** | • **Native Db2 `VECTOR(384, FLOAT32)` + BSON Pushdown**: `DB2LlamaVS` pushes `type`, `eggless_flag`, and `price <= budget` predicates into Db2 SQL prior to cosine distance ranking.<br>• **Multi-Level Recursive BOM CTE**: Authentic Db2 LUW `WITH RECIPE_BOM ... UNION ALL` (`DECIMAL(10, 4)`) checks sub-assembly raw ingredients across `BB_RECIPES`, `BB_INGREDIENT_COMPONENTS`, `BB_INVENTORY`.<br>• **SQL PL Stored Procedure & Row Locks**: `SP_RESERVE_CAKE_STOCK` locks `BB_CAKES` via `FOR UPDATE OF stock_qty WITH RS` + `WHERE CURRENT OF`.<br>• **Single-UOW ACID Transactions + Audit Chain + Persistent Session Buffer**: Atomic `place_verified_order_atomic()`, sargable `phone_last10` B-Tree index, `V_MASKED_BAKERY_ORDERS` view, `BB_USER_CONVERSATION_BUFFER`, and `BB_AUDIT_LOG`. | [`src/db.py`](src/db.py)<br>[`src/ingest.py`](src/ingest.py)<br>[`src/order_engine.py`](src/order_engine.py)<br>[`src/vector_store.py`](src/vector_store.py) |
| **2. Innovation & Real-World Impact** | **20%** | • Built for a live 20-year regional bakery (**Shri Ram Baker's**, Khatoti Kua & Holigate/Gosna branches, Mathura) solving late-night order loss and customization guesswork.<br>• **Hinglish CRAG + Self-RAG**: Understands vernacular queries (*"bina ande wala aadha kilo cake"*, *"petis garam"*) and enforces verified dry-tawa & 3–4h fresh-baking policies.<br>• **Interactive `/demo` Engineering Console**: Lets judges test RAG cards, BOM shortage rejection, race locks, and audit verification visually in one click. | [`src/retriever.py`](src/retriever.py)<br>[`src/query_engine.py`](src/query_engine.py)<br>[`src/demo_ui.py`](src/demo_ui.py) |
| **3. Technical Architecture & AI** | **15%** | • **3-Way Reciprocal Rank Fusion ($k=60$)** fusing Db2 dense vectors + Okapi BM25 + TF-IDF with singleton cached embeddings.<br>• **Official `google-genai` SDK** with **request-scoped agentic tool closures** (zero cross-tenant mutable state) for 5 tools + deterministic `--no-llm` fallback.<br>• Complete end-to-end DDL, Mermaid diagrams, and sequence flows documented in [`architecture.md`](architecture.md). | [`src/query_engine.py`](src/query_engine.py)<br>[`src/api.py`](src/api.py)<br>[`architecture.md`](architecture.md) |
| **4. Security** | **15%** | • **Zero Secrets & Workspace-Isolated `.env`**: Only reads submission-local `.env`, on-demand credentials, masked logs (`PWD=********`).<br>• **Least-Privilege Db2 RBAC**: [`sql/least_privilege_setup.sql`](sql/least_privilege_setup.sql) isolates `BAKEBOX_READER_ROLE` & `BAKEBOX_APP_ROLE` and restricts `BB_AUDIT_LOG` to `SELECT, INSERT` only.<br>• **SQLi, IDOR & Brute-Force Defense**: Parameterized SQL, sargable indexed lookup, regex `validate_doc_id()` guard before `DB2LlamaVS.delete()`, 2FA phone verification + `OrderAuthRateLimiter` lockout, boundary PII masking.<br>• **Bilingual Prompt & Output Hardening**: Unicode NFKC normalization, zero-width stripping, `<customer_input>` & `<conversation_history>` XML barriers, secret/XSS scrubbing, tightened CORS. | [`src/security.py`](src/security.py)<br>[`sql/least_privilege_setup.sql`](sql/least_privilege_setup.sql)<br>[`.env.example`](.env.example) |
| **5. Reproducibility & Code Quality** | **15%** | • **72 Automated Tests Passing (`0 errors, 0 failures`)**: Unit, HTTP `TestClient`, multi-thread race concurrency, audit concurrency, ACID rollback injection, tamper forensics, and session isolation tests.<br>• **Strict Ground-Truth Ablation Benchmark**: 30-query script verifying semantic, SKU, Hinglish, and policy IDs.<br>• **One-Command Docker Db2**: Ready [`docker-compose.yml`](docker-compose.yml) + Python 3.10–3.14 compatible [`requirements.txt`](requirements.txt). | [`tests/`](tests/)<br>[`docker-compose.yml`](docker-compose.yml)<br>[`requirements.txt`](requirements.txt) |
| **6. Documentation & Presentation** | **10%** | • Complete [`submission.json`](submission.json), MIT [`LICENSE`](LICENSE), [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md), 11 verified production screenshots ([`docs/screenshots/`](docs/screenshots/README.md)), live YouTube walkthrough, and clean commit history strictly scoped to `submissions/bakebox-choco-ai/`. | [`LICENSE`](LICENSE)<br>[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)<br>[`submission.json`](submission.json) |

---

## Table of Contents
- [BAKEBOX - CHOCO AI: Dual-Perspective Solution](#bakebox---choco-ai-dual-perspective-solution)
- [IBM Db2 Integration & Depth](#ibm-db2-integration--depth)
- [Hybrid RAG, CRAG & Agentic AI Pipeline](#hybrid-rag-crag--agentic-ai-pipeline)
- [Security & Privacy Architecture](#security--privacy-architecture)
- [REST API & Interactive Playground](#rest-api--interactive-playground)
- [Empirical Retrieval Quality Benchmark (30 Queries)](#empirical-retrieval-quality-benchmark-30-queries)
- [Setup, Live Docker Db2 & Verification](#setup-live-docker-db2--verification)
- [Visual Proof & Application Screenshots](#visual-proof--application-screenshots)
- [Technical Defense & Architectural FAQ](#technical-defense--architectural-faq)
- [Demo Links, Roadmap & Team](#demo-links-roadmap--team)

---

## BAKEBOX - CHOCO AI: Dual-Perspective Solution

**Shri Ram Baker's** has served Mathura for over 20 years across **Bhagel Chaupal (Khatoti Kua / Holigate)** and **Gosna**. Scaling into digital commerce created acute friction on both sides:

### Customer Challenges Solved
1. **Menu Ambiguity & Sweetness Guesswork:** Static product tiles cannot answer nuanced questions (*"Is Red Velvet overly sweet?"*, *"Difference between Khoaa Eggless and regular eggless?"*, *"0.5kg vs 1kg servings?"*).
2. **Post-9 PM Support Blackout:** High-intent celebration orders after store hours previously went unanswered.
3. **Lack of Live Kitchen Visibility:** Customers needed instant order stage updates without calling store staff manually.

### Bakery Operational Challenges Solved
1. **Concurrency Overselling:** Simultaneous buyers grabbing the final ready-to-deliver showcase cake risked double-booking without strict DB row locks.
2. **Raw Ingredient Blind Spots:** Accepting a custom cake order when a sub-ingredient (e.g. *Maraschino Cherries* or sub-assembly *Fresh Milk Solids*) is depleted causes fulfillment failures.
3. **Support Repetitive-Query Fatigue:** Automating wait-time FAQs (fresh baking takes 3–4 hours) and snack advisories (dry tawa reheating only) frees kitchen staff to focus on baking.

---

## IBM Db2 Integration & Depth

BAKEBOX uses **IBM Db2 LUW 12.1** simultaneously as an **AI vector store, persistent LLM conversation buffer, recursive manufacturing BOM engine, and ACID ledger**:

```mermaid
flowchart LR
    API["FastAPI / Agent Tool"] --> BOM["1. Recursive BOM CTE\n(WITH RECIPE_BOM UNION ALL)"]
    BOM --> SP["2. SQL PL Stored Procedure\n(SP_RESERVE_CAKE_STOCK WITH RS)"]
    SP --> ORD["3. Relational ACID Tables\n(BB_ORDERS + BB_ORDER_ITEMS)"]
    ORD --> AUD["4. Append-Only Audit Chain\n(SHA-256 BB_AUDIT_LOG)"]
    API --> VEC["5. Native Vector + BSON Filter\n(DB2LlamaVS BB_CHUNKS_VECTOR)"]
    API --> BUF["6. Persistent Session Buffer\n(BB_USER_CONVERSATION_BUFFER)"]
```

1. **Native Vector Store with BSON Metadata Pushdown ([`src/vector_store.py`](src/vector_store.py)):**
   * Stores 384-dimensional `BAAI/bge-small-en-v1.5` vectors in `BB_CHUNKS_VECTOR` (`VECTOR(384, FLOAT32)`).
   * Pushes structured `MetadataFilters` (`type = 'cake'`, `eggless_flag = 1`, `price <= max_price`, or `type IN ['policy', 'advisory', 'store_info']`) into Db2 SQL prior to cosine similarity ranking via `DB2LlamaVS`, eliminating cross-category noise at the storage layer.
   * Offline environments transparently switch to our built-in `_OfflineMockVectorStore` enforcing identical metadata predicates and numpy cosine ranking.
2. **In-Database Multi-Level Recursive BOM CTE ([`src/order_engine.py`](src/order_engine.py)):**
   * Executes genuine Db2 LUW recursive SQL (`WITH RECIPE_BOM (...) AS (anchor UNION ALL recursive)`) across `BB_RECIPES`, `BB_INGREDIENT_COMPONENTS`, and `BB_INVENTORY` with `DECIMAL(10, 4)` arithmetic.
   * For example, `Cake #1` (*Red Velvet*) checks both direct ingredients (`Khoaa Base`, `Cream Cheese Frosting`) and derived sub-components (`Fresh Milk Solids (Mawa)` at 0.65x ratio, `Whipped Dairy Cream` at 0.50x ratio). `Cake #2` detects the `Maraschino Cherries` deficit (`0.50kg` needed vs `0.20kg` stocked) and blocks overselling before payment/order creation.
3. **Row-Level Concurrency Control (`FOR UPDATE OF stock_qty WITH RS`) & Stored Procedure:**
   * `SP_RESERVE_CAKE_STOCK` opens a Read Stability update cursor (`FOR UPDATE OF stock_qty WITH RS`), checks inventory, executes `UPDATE ... WHERE CURRENT OF lock_cur`, and returns `DYNAMIC RESULT SETS 1` while respecting the caller's outer Unit of Work.
   * Verified by multi-threaded collision tests (`test_05` & `test_06`): when two buyers target the final Cake #2 concurrently, **exactly 1 succeeds and 1 fails cleanly**.
4. **Single-UOW ACID Transactions + Sargable Indexing + Views:**
   * `place_verified_order_atomic()` executes BOM check $\rightarrow$ stock lock $\rightarrow$ `BB_ORDERS` insert $\rightarrow$ `BB_ORDER_ITEMS` insert $\rightarrow$ `BB_AUDIT_LOG` append inside **one atomic transaction** (`commit=False` on sub-calls, single `conn.commit()`, full `conn.rollback()` on failure — verified via fault-injection test `test_14`).
   * Uses a dedicated indexed `phone_last10` column (`IDX_BB_ORDER_PHONE`) for sargable 2FA lookups (avoiding `RIGHT(REPLACE(...))` index bypass and Db2 `SQL0138N` short-string errors) and exposes `V_MASKED_BAKERY_ORDERS` for privacy-safe support dashboards.
5. **Cryptographic SHA-256 Hash-Chained Audit Log (`BB_AUDIT_LOG`) & Db2 Session Buffer (`BB_USER_CONVERSATION_BUFFER`):**
   * Every order creation, refund approval, and failed auth attempt chains cryptographically via `SHA256(prev_hash | session_id | action_type | canonical_payload_json)`.
   * Multi-turn dialogue turns persist in `BB_USER_CONVERSATION_BUFFER` alongside isolated in-memory `SessionBufferMemory` (1-hour TTL eviction).

---

## Hybrid RAG, CRAG & Agentic AI Pipeline

```text
Customer Query ─▶ Security Guardrail (NFKC + Bilingual Injection Block)
                      │
                      ▼
       Corrective RAG (Hinglish Expansion: "bina ande" -> "Pure Veg Khoaa Eggless")
                      │
                      ▼
       3-Way Hybrid RRF (k=60) + Metadata Pushdown
         ├─ Channel 1: IBM Db2 Native Vector Search (Cosine Similarity)
         ├─ Channel 2: Okapi BM25 (Exact SKU & Token Frequency Matching)
         └─ Channel 3: Scikit-Learn TF-IDF Cosine Matrix
                      │
                      ▼
       Request-Scoped Agentic Dispatcher (google-genai / Offline Deterministic)
         ├─ recommend_cakes()            -> Up to 3 verified catalog JSON cards
         ├─ track_live_order()           -> 2FA indexed Db2 lookup + PII masking
         ├─ get_store_policy_or_advisory()-> Policy/Tawa/Hours retrieval
         ├─ check_cake_ingredients_bom() -> Live Recursive BOM CTE status
         └─ place_verified_order()       -> Atomic BOM + WITH RS + Audit Order
                      │
                      ▼
       Self-RAG Fact Verifier & Output Scrubber (Dry Tawa Guard + Secret Redaction)
```

* **Modern SDK + Thread-Safe Tool Binding:** Uses the official **`google-genai`** SDK (`from google import genai`) with fresh per-request tool closures (`_build_request_tools(call_state, session_id)`), guaranteeing concurrent users never share or overwrite mutable tool state.
* **Offline Resilience:** When `GEMINI_API_KEY` is omitted or `--no-llm` is passed, the deterministic dispatcher routes the exact same Db2 tools with zero hallucinations.
* **Why 3-Way RRF ($k=60$) Beats Linear Weighted Sums:** Dense cosines ($[0,1]$), unbounded BM25 scores ($[0,\infty)$), and TF-IDF scores live on incompatible scales. Rank-based fusion $\sum \frac{1}{60 + \text{rank} + 1}$ smoothly rewards consensus across exact SKU lookups (`BB-RED-01-1kg`), semantic descriptions, and Hinglish phrasing without brittle weight tuning.

---

## Security & Privacy Architecture

1. **Zero-Secrets & Config Isolation:** [`src/db.py`](src/db.py) reads only `submissions/bakebox-choco-ai/.env` locally (never silently walking parent directories), resolves Db2 credentials dynamically without module-level password globals, and masks logs via `get_masked_connection_string()`.
2. **Least-Privilege Db2 Roles ([`sql/least_privilege_setup.sql`](sql/least_privilege_setup.sql)):** Separates `BAKEBOX_READER_ROLE` (catalog + masked views only) from `BAKEBOX_APP_ROLE` (operational DML + `SELECT, INSERT` append-only on `BB_AUDIT_LOG`, withholding `UPDATE`/`DELETE`).
3. **Parameterized SQL & Driver SQLi Protection:** All SQL queries use strict `?` parameter binding; [`validate_doc_id()`](src/security.py) blocks SQL injection before calling `DB2LlamaVS.delete()`.
4. **2FA Brute-Force Lockout & PII Masking:** Order tracking and refund endpoints enforce `order_id` + 10-digit phone verification, lock out after 5 consecutive failed guesses via `OrderAuthRateLimiter` (logging `REFUND_AUTH_FAILED` to `BB_AUDIT_LOG`), and mask names (`R**** S*****`), phones (`+91 ******3210`), and addresses (`***, Mathura, UP (Confidential)`) before returning data.
5. **Prompt Injection & Output Hardening ([`src/security.py`](src/security.py)):** Applies Unicode NFKC normalization, strips invisible zero-width characters (`\u200b`–`\u202e`), blocks English/Hinglish jailbreaks & DDL patterns, wraps untrusted inputs inside `<customer_input>` / `<conversation_history>` tags, and scrubs leaked API keys, `PWD=` strings, or `<script>` tags from responses.

---

## REST API & Interactive Playground

Start the server with `uvicorn src.api:app --reload` and open **`http://127.0.0.1:8000/demo`** (or **`/docs`** for Swagger UI):

| Method & Endpoint | Capability Exercised | IBM Db2 Feature |
|---|---|---|
| `GET /` & `GET /api/health` | Health telemetry, live/mock mode, catalog count, audit check | Connection & `verify_audit_chain` |
| `GET /demo` | Zero-dependency interactive Judge Engineering Console UI | Calls all live API endpoints |
| `POST /api/chat` | Bilingual CHOCO AI chat, guardrails, Self-RAG & buffer persistence | `BB_CHUNKS_VECTOR` + `BB_USER_CONVERSATION_BUFFER` |
| `GET /api/cakes/search` | Hybrid catalog search (`eggless_only`, `max_price` budget filter) | 3-Way RRF + Metadata Pushdown |
| `GET /api/cakes/{cake_id}/availability` | Live raw ingredient & sub-assembly availability breakdown | Recursive `RECIPE_BOM` CTE |
| `POST /api/orders` | End-to-end atomic cake reservation & order creation | BOM + `SP_RESERVE_CAKE_STOCK` + `BB_ORDERS` + `BB_AUDIT_LOG` |
| `GET /api/orders/masked-summary` | Privacy-compliant support order list (zero raw customer PII) | `V_MASKED_BAKERY_ORDERS` View |
| `GET /api/orders/{order_id}` | 2FA phone-verified live order & item tracking | Sargable `IDX_BB_ORDER_PHONE` + `BB_ORDER_ITEMS` |
| `POST /api/orders/{order_id}/refund` | Phone-authenticated Happiness Guarantee refund evaluation | Single-UOW `UPDATE` + `BB_AUDIT_LOG` |
| `GET /api/audit/verify` | Mathematical verification of entire cryptographic audit chain | `BB_AUDIT_LOG` SHA-256 chain traversal |

---

## Empirical Retrieval Quality Benchmark (30 Queries)

Measured directly by executing `python tests/evaluate_retrieval.py` across **30 curated queries** (10 semantic cravings, 8 exact SKU/title lookups, 6 Hinglish & dietary queries, 6 store policy/advisory queries) with **strict chunk/SKU ID verification** and category metadata pushdown:

| Retrieval Channel Configuration | Hit @ 1 | Hit @ 3 | MRR | Avg Query Latency (CPU) | Observation |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Dense Vector Only** (`BAAI/bge-small-en-v1.5`) | 80.0% | 90.0% | 0.85 | ~21 ms | Captures semantics well; misses exact SKU codes (`BB-RED-02-1kg`). |
| **Sparse BM25 Only** (Okapi BM25) | 86.7% | 93.3% | 0.90 | < 1 ms | Fast keyword recall; misses semantic & paraphrased queries. |
| **Sparse TF-IDF Only** (Scikit-Learn) | 93.3% | 100.0% | 0.96 | ~3 ms | Strong n-gram precision on uniform English terms. |
| **🏆 3-Way Hybrid RRF ($k=60$) + Hinglish CRAG** | **90.0%** | **100.0%** | **0.94** | **~28–40 ms** | **100% Top-3 recall across semantic, exact SKU, bilingual Hinglish & policy queries; eliminates single-channel blindspots.** |

*(Note: Zero external databases required to reproduce this benchmark; run `python tests/evaluate_retrieval.py` at any time.)*

---

## Setup, Live Docker Db2 & Verification

### Prerequisites
* Python `>= 3.10` (`3.11`, `3.12`, `3.13`, or `3.14`)
* `pip`
* Optional for live DB mode: Docker (for IBM Db2 Community Edition `12.1.2.0`) and optional `GEMINI_API_KEY`

### 1. Standard Offline Setup & Automated Testing
```bash
cd submissions/bakebox-choco-ai
pip install -r requirements.txt

# Run all 72 unit, concurrency, security, audit, and HTTP TestClient tests
python -m unittest discover -s tests -v

# Run CLI agent demonstration in deterministic mode
python src/query_engine.py --no-llm
```

**Verified Test Output:**
```text
Ran 72 tests in ~16.8s
OK
```

### 2. Running with Live IBM Db2 (Docker Mode)
```bash
cd submissions/bakebox-choco-ai
cp .env.example .env
# Edit .env: set real DB2_USER (e.g., db2inst1), strong DB2_PASSWORD, DB2_FORCE_MOCK=false

# Launch IBM Db2 Community Edition 12.1.2.0
docker compose up -d

# Wait for healthy status (~60-90s initial bootstrap), then create tables, SP, views & ingest vectors
python src/ingest.py

# Apply least-privilege RBAC roles & append-only audit grants as SECADM:
# db2 -tvf sql/least_privilege_setup.sql

# Launch live API & interactive playground
uvicorn src.api:app --reload
```

### 3. Official Hackathon Repository Validator
Run from the repository root:
```bash
python scripts/validate_submission.py submissions/bakebox-choco-ai
```

---

## Visual Proof & Application Screenshots

Full-resolution UI & IBM Db2 VS Code extension screenshots from our end-to-end deployment are documented in [`docs/screenshots/`](docs/screenshots/README.md):

| Proof Area | Preview | Verification Details |
|---|---|---|
| **IBM Db2 Live Tables & Vectors** | ![IBM Db2 VS Code Extension](docs/screenshots/01_ibm_db2_extension_tables.png) | Live IBM Db2 extension connected to `localhost@IBMDB201` displaying `BB_*` tables and `VECTOR` embeddings. |
| **Storefront & Catalog** | ![Storefront Overview](docs/screenshots/07_storefront_catalog_overview.png) | Full Mathura storefront demonstrating Holigate/Gosna branch indicators, 3–4h prep badges, and pure-veg markers. |
| **Contextual "Ask CHOCO"** | ![Contextual Reasoning](docs/screenshots/10_ask_choco_contextual_query.png) | 1-click SKU consultation injecting cake metadata directly into CHOCO AI context. |
| **Master Baker Advisory** | ![Master Baker Response](docs/screenshots/11_choco_master_baker_recommendation.png) | Bilingual Hinglish response detailing Khoaa eggless customization, pricing, and fresh-baking guarantees. |
| **Live Order Tracking** | ![Live Order Status Confirmed](docs/screenshots/02_choco_order_status_confirmed.png) | Real-time Db2 status lookup (`CONFIRMED` $\rightarrow$ `BAKING` $\rightarrow$ `DELIVERED`) with kitchen dispatch details. |
| **Happiness Guarantee & Refunds** | ![Happiness Guarantee Support](docs/screenshots/04_choco_happiness_guarantee_support.png) | Autonomous policy resolution grounded in Db2 policy chunks and `BB_AUDIT_LOG`. |
| **RBAC Role Authentication** | ![Role Selection Modal](docs/screenshots/05_bakebox_auth_role_modal.png) | Multi-role access separation for Customer, Store Operator, and Super Admin workflows. |

---

## Technical Defense & Architectural FAQ

* **Q1: Why isolate `submissions/bakebox-choco-ai/` from the full React frontend repository?**  
  In strict compliance with IBM Db2 TechX submission guidelines, this PR package keeps all backend AI/Db2 microservices, SQL DDL, RBAC scripts, and 72 tests self-contained without touching root repository configuration or exceeding PR review budgets. Judges can also exercise the live backend interactively at `http://127.0.0.1:8000/demo` or view the React storefront in our [YouTube Walkthrough](https://youtu.be/NLrRq6FX358?si=oZM-EGpaBt4AOSVM).
* **Q2: How do you prove offline tests aren't masking live Db2 errors?**  
  `is_live_db2_available()` only engages `MockDb2Connection` when credentials are unconfigured or `DB2_FORCE_MOCK=true`. Once real credentials are configured in `.env`, [`src/db.py`](src/db.py) connects strictly via `ibm_db_dbi.connect(...)` and surfaces authentic database errors rather than swallowing connection failures.
* **Q3: Why normalize `phone_last10` instead of querying `RIGHT(REPLACE(customer_phone, ...), 10)`?**  
  Wrapping an indexed column inside scalar string functions prevents Db2 from using `IDX_BB_ORDER_PHONE` (forcing a table scan) and risks `SQL0138N` if a stored phone string is shorter than 10 characters. Storing canonical 10 digits in indexed `phone_last10` preserves `O(log N)` B-Tree index seeks.

---

## Demo Links, Roadmap & Team

* **Video Walkthrough (YouTube):** [https://youtu.be/NLrRq6FX358?si=oZM-EGpaBt4AOSVM](https://youtu.be/NLrRq6FX358?si=oZM-EGpaBt4AOSVM)
* **LinkedIn Showcase Post:** [https://lnkd.in/p/gtXgu6wq](https://lnkd.in/p/gtXgu6wq)
* **Hackathon Submission Repo:** [https://github.com/AYUSHDHANGAR/IBM_Db2_TechX_Project_Submission](https://github.com/AYUSHDHANGAR/IBM_Db2_TechX_Project_Submission)
* **Full-Stack Storefront Repo (React 18 + FastAPI):** [https://github.com/AYUSHDHANGAR/BAKE_BOX--AI-ASSISTENT-FOR-BAKERY](https://github.com/AYUSHDHANGAR/BAKE_BOX--AI-ASSISTENT-FOR-BAKERY)

### Roadmap
* **Native Db2 Full-Text Search (Db2 Text Search `CONTAINS`)** to move lexical BM25 scoring completely inside Db2 alongside `VECTOR_DISTANCE` at 100k+ SKU catalog scale.
* **Multi-Branch Kitchen Load Balancing** between Holigate and Gosna ovens based on live `V_ACTIVE_BAKERY_ORDERS` queue depth.
* **UPI Webhook Settlement** tied directly to `BB_ORDERS` and `BB_AUDIT_LOG`.

### Author
| Name | GitHub | Role & Background |
|---|---|---|
| **Ayush Dhangar** | [@AYUSHDHANGAR](https://github.com/AYUSHDHANGAR) | BTech CSE-AIML (4th Year) · Ex-ML Intern, Pantech Prolab Pvt Ltd · AI Systems & Db2 Solutions Architect |

---

## License
Distributed under the [MIT License](LICENSE). All open-source dependencies and pre-trained embedding model attributions are declared in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
