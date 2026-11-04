# Verification & Visual Traces: BAKEBOX Choco AI

This directory documents execution traces, architectural flow, and visual verification for the **BAKEBOX Choco AI** platform.

A full interactive video walkthrough demonstrating the live queries, order tracking, and cake recommendation cards is available on YouTube:
**[Watch Video Walkthrough](https://youtu.be/MvH82OEsDUA?si=nVuy2awvxKJAaZkV)**

---

## 1. Terminal Verification: Db2 Vector & Relational Ingestion
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

## 2. Terminal Verification: Agentic Query Engine & Hybrid RRF
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

## 3. Automated Test Suite Execution
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
