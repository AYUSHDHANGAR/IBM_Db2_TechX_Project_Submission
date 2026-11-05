# Verification, Screenshots & Visual Proof: BAKEBOX Choco AI

This directory documents execution traces, architectural flow, and visual verification screenshots demonstrating the real-world deployment, IBM Db2 database integration, and autonomous customer support capabilities of **BAKEBOX - CHOCO AI**.

A full interactive video walkthrough demonstrating the live queries, order tracking, and cake recommendation cards is available on YouTube:  
**[Watch Video Walkthrough (YouTube)](https://youtu.be/MvH82OEsDUA?si=nVuy2awvxKJAaZkV)**

---

## 1. Visual Verification & Production Screenshots

### 1.1 IBM Db2 Live Database & Vector Store Verification
#### `01_ibm_db2_extension_tables.png`
![IBM Db2 Developer Extension](01_ibm_db2_extension_tables.png)
- **Component:** IBM Db2 Developer Extension in Visual Studio Code.
- **Connection:** Live instance connected at `localhost@IBMDB201` under schema `DBAYUSH`.
- **Database Tables Verified:**
  - `BB_CAKES`: Full product catalog table containing 558+ live bakery items.
  - `BB_CHUNKS_VECTOR`: Dense vector table created via `DB2LlamaVS` for native vector search.
  - `BB_CUSTOM_CAKES`: User-customized cake design records.
  - `BB_DEMO_LLAMA_COSINE`: LlamaIndex cosine similarity index table.
  - `BB_ORDERS`: Relational order table storing order statuses, customer details, and kitchen dispatch data.
  - `BB_ORDER_ITEMS`: Relational line items associated with each order.
  - `BB_PARTY_ACCESSORIES`: Bakery party supplies and add-ons.
  - `BB_RAG_CHUNKS`: Hybrid RAG knowledge base table storing dense vector embeddings, metadata JSON, and chunk text.
  - `BB_USERS`: Registered bakery customer profiles and authentication credentials.
  - `BB_USER_CONVERSATION_BUFFER`: Strict session-isolated conversation history buffer.
- **Data Viewer:** Highlights active records in `DBAYUSH.BB_RAG_CHUNKS` with `METADATA_JSON`, vector embeddings, and real-time timestamps.

---

### 1.2 Customer Storefront & Catalog Experience
#### `07_storefront_catalog_overview.png`
![Storefront Catalog Overview](07_storefront_catalog_overview.png)
- **Component:** BAKEBOX AI 2.0 Customer Storefront & Header.
- **Operational Metrics:** Real-time branch indicators (*Branch 1: Bhagel Chaupal, Khatoti Kua (Mathura) | Branch 2: Gausna (Mathura)*), 3-4 hours baking wait time badge, and 100% Pure Veg (Khoaa Eggless Available) badge.
- **Catalog Navigation:** Instant category filters (*Standard Cakes (558), Custom Designer Cakes (52), Fresh Oven Patties (29), Party Accessories (45)*).
- **Cake Cards:** Shows standard cake tier cards (Premium Chocolate Truffle, Kitkat Border, Belgian Truffle) with dynamic weights and instant actions.

#### `09_product_catalog_grid_actions.png`
![Product Catalog Grid Actions](09_product_catalog_grid_actions.png)
- **Component:** Strawberry Collection Catalog Grid with Direct Actions.
- **Features:** Shows specific cake metadata (*Khoaa, Veg Eggless & Egg Available, Pricing at ₹299*), pagination across 558 cakes, and 1-click **Ask CHOCO** & **Add** buttons on every card.

---

### 1.3 Autonomous Master Baker & AI Advisory (CHOCO AI)
#### `10_ask_choco_contextual_query.png`
![Ask CHOCO Contextual Query](10_ask_choco_contextual_query.png)
- **Component:** 1-Click Contextual Cake Advisory Trigger.
- **Action:** Clicking "Ask CHOCO" on a cake card auto-injects the exact cake name, SKU ID (`BB-STR-04-05kg`), flavor, and weight into the chat session, displaying the real-time reasoning state: *"CHOCO master baker is retrieving catalog & reasoning..."*.

#### `11_choco_master_baker_recommendation.png`
![CHOCO Master Baker Recommendation](11_choco_master_baker_recommendation.png)
- **Component:** CHOCO AI Precision Recommendation Response.
- **Output:** Generates a warm, bilingual (Hinglish/English) recommendation detailing SKU verification, recommended party size (4-6 people), transparent pricing (₹299.00), base customizations (100% Pure Khoaa/Mawa eggless base), and visual design features directly retrieved from Db2 hybrid RAG.

---

### 1.4 Live Order Tracking & Transactional Db2 Queries
#### `02_choco_order_status_confirmed.png`
![CHOCO Order Status Confirmed](02_choco_order_status_confirmed.png)
- **Component:** Live Order Tracking via Agentic Tool Calling.
- **User Query:** *"Order #1104 what was the order status of this order id ."*
- **Database Query Execution:** CHOCO AI queries `BB_ORDERS` and `BB_ORDER_ITEMS` in real time and reports:
  - **Order ID:** #1104
  - **Customer Name:** Ayush ji (Phone: 8279783653)
  - **Status:** `CONFIRMED`
  - **Items Ordered:** 1x Strawberry Sweet Berry Glaze (0.5kg, Khoaa Eggless base)
  - **Kitchen Dispatch:** Bhagel Chaupal, Khatoti Kua Branch (Mathura).

#### `03_choco_order_status_delivered.png`
![CHOCO Order Status Delivered](03_choco_order_status_delivered.png)
- **Component:** Real-Time Order Lifecycle Updates.
- **User Query:** *"Order #1104 new status"*
- **Resolution:** Live synchronization with IBM Db2 reflects status change from `CONFIRMED` to `DELIVERED`, confirming safe hand-off to the customer's delivery address in Mathura.

---

### 1.5 Intelligent Customer Care & Policy Resolution
#### `04_choco_happiness_guarantee_support.png`
![Happiness Guarantee Support](04_choco_happiness_guarantee_support.png)
- **Component:** Damaged Order Resolution & Emotional Alignment.
- **User Query:** *"the order i got is damaged help me ."*
- **Policy Retrieval:** CHOCO AI instantly references the bakery's *Celebration Happiness Guarantee & Replacement Policy* from unstructured document embeddings in Db2 to offer 100% Free Re-bake or Instant Full Refund without human escalation.

#### `08_refund_replacement_resolution.png`
![Refund & Replacement Resolution](08_refund_replacement_resolution.png)
- **Component:** Refund Procedure Guidance.
- **User Query:** *"i got previous was damaged how i raise refund ."*
- **Resolution:** Step-by-step instructions (photo verification within 2 hours via WhatsApp helpline `+91 8923701210`) with priority re-baking dispatch within 60-90 minutes.

---

### 1.6 Role-Based Access Control & Operations Management
#### `05_bakebox_auth_role_modal.png`
![BAKEBOX Authentication Role Modal](05_bakebox_auth_role_modal.png)
- **Component:** Multi-Role Authentication Modal.
- **Roles:** Demonstrates role-based access control with one-click demo credentials for **Customer Demo**, **Super Admin**, and **Store Operator**.

#### `06_operator_login.png`
![Store Operator Login](06_operator_login.png)
- **Component:** Store Operator Authentication.
- **Role:** Authenticates operator account (`operator@bakebox.in`) to manage kitchen workflows, live baking queues, and branch dispatch synchronization.

---

## 2. Terminal Verification: Db2 Vector & Relational Ingestion
```text
==================================================================
BAKEBOX CHOCO AI — IBM Db2 DATA INGESTION PIPELINE
==================================================================
Step 1: Setting up IBM Db2 Relational Tables (BB_ORDERS & BB_ORDER_ITEMS)...
  -> Table BB_ORDERS created successfully.
  -> Table BB_ORDER_ITEMS created successfully.
  -> Seeded demo active order #1002 for 'Rahul Sharma' (Status: BAKING at Khatoti Kua kitchen).

Step 2: Loading HuggingFace Embedding Model 'BAAI/bge-small-en-v1.5'...

Step 3: Generating 384-dimensional dense vectors for bakery knowledge chunks...
  -> Generated embeddings for 10 knowledge nodes.

Step 4: Ingesting into IBM Db2 native vector table 'BB_CHUNKS_VECTOR' via DB2LlamaVS...
  -> Ingestion complete! Chunks & vectors safely stored in IBM Db2.

==================================================================
DATA INGESTION SUCCESSFULLY COMPLETED!
==================================================================
```

---

## 3. Terminal Verification: Agentic Query Engine & Hybrid RRF
```text
Initializing BAKEBOX Choco Query Engine with IBM Db2 & LlamaIndex...
[INFO] Operating in deterministic ground-truth synthesis mode (Offline / Zero-Hallucination).
[OK] Choco Query Engine is fully operational!

==================================================================
QUERY: 'I want to order a red velvet cake for anniversary celebration'
INTENT: CAKE_RECOMMENDATION
CARDS RETURNED: 3 (Up to 3)
CHOCO REPLY:
Radhe Radhe ji! Shri Ram Baker's BAKEBOX mein aapka swagat hai!

Aapki celebration ke liye hamare paas 3 fresh live options available hain:
• Red Velvet Crimson Crumb Crown (₹649.0, 1.0kg)
• Red Velvet Heart Love Affair (₹649.0, 1.0kg)
• Red Velvet Berry Fantasy (₹649.0, 1.0kg)

Hamare sabhi cakes 100% pure vegetarian (Khoaa Eggless available) hain 
aur order par live fresh bake kiye jaate hain (standard 3-4 ghante wait time)!

==================================================================
QUERY: 'Where is my order? Status of order #1002 please'
INTENT: ORDER_TRACKING
CARDS RETURNED: 0
CHOCO REPLY:
Radhe Radhe ji! Shri Ram Baker's BAKEBOX mein aapka swagat hai!

Humne aapke order ki live details IBM Db2 se verify kar li hain:
• Order ID: #1002 (Rahul Sharma)
• Status: BAKING (at Bhagel Chaupal, Khatoti Kua kitchen)
• Items: 1x Red Velvet Heart Special (1.0kg, Khoaa (Eggless))
• Delivery Address: Krishna Nagar, Mathura

Shri Ram Baker par har cake order par fresh bake hota hai (3-4 ghante wait time)!
```

---

## 4. Automated Test Suite Execution
```text
pytest submissions/bakebox-choco-ai/tests -v

tests/test_retrieval.py::test_rrf_scoring_formula PASSED
tests/test_retrieval.py::test_intent_classification_no_order_hijack PASSED
tests/test_retrieval.py::test_intent_classification_order_tracking PASSED
tests/test_retrieval.py::test_intent_classification_policy PASSED
tests/test_retrieval.py::test_filter_upto_three_cards_dynamic PASSED
tests/test_retrieval.py::test_sample_bakery_documents_schema PASSED

============================== 6 passed in 0.12s ==============================
```
