# BAKEBOX Choco AI (Autonomous AI Bakery Management Platform & 3D Storefront)

**IBM Db2 TechX Summit Hackathon Project (Db2Hack Dev Hacks)**  
*GL Bajaj Group of Institutions, Mathura*  
**Developer:** Ayush Dhangar ([@AYUSHDHANGAR](https://github.com/AYUSHDHANGAR))  
**Client / Domain:** Shri Ram Baker (Mathura, Uttar Pradesh)  
**Database:** IBM Db2 (`IBMDB201` / Community Edition on `localhost:50000`)  
**AI Frameworks:** LlamaIndex, `llama-index-vector-stores-db2` (`DB2LlamaVS`), `ibm_db_dbi`, HuggingFace `BAAI/bge-small-en-v1.5`

---

## 📌 Problem Statement

Traditional bakery and fresh-food businesses in tier-2 cities like Mathura face severe challenges:
1. **Perishable Inventory & Fresh Preparation Times:** Live handcrafted fresh cakes take 3–4 hours of soaking and cold-setting. Customers repeatedly call kitchens inquiring about live order progress.
2. **Catalog Discovery:** Over 600+ cake varieties (Khoaa eggless, designer tiers, doll cakes) cannot be effectively browsed via static menus.
3. **AI Hallucinations in Food Orders:** Standard chatbots invent non-existent products, incorrect prices, or inaccurate baking time estimates.

---

## 💡 The Solution: BAKEBOX & CHOCO AI

**BAKEBOX** solves this through a unified digital platform and an autonomous master baker AI assistant (**CHOCO**), powered by:
- **IBM Db2 Native Vector Storage (`DB2LlamaVS`):** Stores 384-dimensional dense vectors in table `BB_CHUNKS_VECTOR` using Db2 v12.1.2+ native `vector(384, FLOAT32)` datatype and hardware-accelerated Cosine distance calculations.
- **Hybrid Reciprocal Rank Fusion (RRF: $k=60$):** Combines dense vector similarity with sparse lexical TF-IDF for exact cake flavor, weight (1kg vs 0.5kg), and base matching.
- **Relational Ground-Truth Verification:** Directly queries transactional tables `BB_ORDERS` and `BB_ORDER_ITEMS` for real-time live kitchen progress.
- **Strict 3-Cake Precision Recommendation:** Emits verified JSON cards with exact SKUs, local image paths, and pricing only when requested.

---

## 📂 Project Structure

```text
submissions/bakebox-choco-ai/
├── src/
│   ├── __init__.py
│   ├── db.py               # IBM Db2 connection manager (ibm_db_dbi)
│   ├── vector_store.py     # Official DB2LlamaVS vector store wrapper
│   ├── retriever.py        # Custom Hybrid RRF Retriever (Dense + Sparse)
│   ├── ingest.py           # Ingestion pipeline for native vectors & tables
│   └── query_engine.py     # Main query engine for cake recommendation & orders
├── README.md               # Project documentation & setup instructions
├── architecture.md         # Detailed system architecture & schema diagrams
├── submission.json         # Hackathon submission metadata
├── .env.example            # Environment variables template
└── docs/
    └── screenshots/        # UI and terminal execution screenshots
```

---

## 🛠️ Step-by-Step Setup & Reproducibility Guide

### 1. Prerequisites
- Python 3.10+ (or Python 3.14)
- Running local IBM Db2 instance (e.g. `localhost:50000`, database `testdb` or `IBMDB201`)
- Install Python dependencies:
  ```bash
  pip install llama-index-core llama-index-vector-stores-db2 ibm-db fastembed scikit-learn
  ```

### 2. Configure Environment (`.env`)
Copy `.env.example` to `.env` and fill your Db2 credentials:
```bash
cp .env.example .env
```
Example configuration:
```env
DB2_HOST=127.0.0.1
DB2_PORT=50000
DB2_DATABASE=IBMDB201
DB2_USER=dbayush
DB2_PASSWORD=8844
```

### 3. Run Data Ingestion
Set up relational tables (`BB_ORDERS`, `BB_ORDER_ITEMS`) and ingest native vector embeddings into `BB_CHUNKS_VECTOR`:
```bash
python submissions/bakebox-choco-ai/src/ingest.py
```

### 4. Test Query Engine
Execute the interactive query engine demonstrating hybrid RRF search, 3-cake recommendations, and live order tracking:
```bash
python submissions/bakebox-choco-ai/src/query_engine.py
```

---

## 🎯 Verification Test Scenarios

### Scenario 1: Cake Recommendation Intent
- **Input:** *"Show me some red velvet cake for anniversary celebration"*
- **Output:** Returns **EXACTLY 3 verified cake cards** (`BB-RED-02-1kg`, `BB-RED-05-1kg`, `BB-RED-01-1kg`) with price ₹649 and exact image paths.

### Scenario 2: Live Order Status Tracking
- **Input:** *"Actually I have placed one order can you provide me the status?"*
- **Output:** Queries `BB_ORDERS` for Order #1002. Reports **BAKING** status at Khatoti Kua kitchen with 3-4 hours preparation notice. Returns **0 cards** (no clutter).

### Scenario 3: Store Guidelines & Heating Advisory
- **Input:** *"Patties ko reheat kaise karna chahiye?"*
- **Output:** Advises reheating on a **dry tawa for 2-3 minutes**, never in a microwave.

---

## 📜 License
Distributed under the MIT License. Built for the IBM Db2 TechX Summit Hackathon.
