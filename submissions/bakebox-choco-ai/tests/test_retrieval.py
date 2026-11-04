"""
Unit and Integration Tests for BAKEBOX Choco AI Retrieval & Tool Logic.
Runs offline with zero live Db2 or external API dependencies:
  pytest tests -v
Or via standard library:
  python tests/test_retrieval.py
"""
import sys
import unittest
import re

from src.ingest import get_sample_bakery_documents
from src.retriever import SimpleBM25

def compute_3way_rrf_score(rank_dense: int, rank_bm25: int, rank_tfidf: int, k: int = 60) -> float:
    """Computes 3-way Reciprocal Rank Fusion score across Dense Db2, BM25, and TF-IDF."""
    score = 0.0
    if rank_dense is not None:
        score += 1.0 / (k + rank_dense + 1)
    if rank_bm25 is not None:
        score += 1.0 / (k + rank_bm25 + 1)
    if rank_tfidf is not None:
        score += 1.0 / (k + rank_tfidf + 1)
    return score

def classify_query_intent(query: str) -> str:
    """Robust intent classification separating ordering/buying from order tracking."""
    q_lower = query.lower()
    
    # Explicit order tracking patterns
    tracking_keywords = ["track", "status", "kahan hai", "mera order", "delivery status", "check order"]
    has_order_id = bool(re.search(r'(?:order\s*#?|#)\s*(\d{4,})', q_lower))
    
    if any(k in q_lower for k in tracking_keywords) or (has_order_id and "order" in q_lower):
        return "ORDER_TRACKING"
    
    # Policy / Advisory questions
    advisory_keywords = ["reheat", "tawa", "skillet", "microwave", "policy", "wait time", "location", "branch", "baking time"]
    if any(k in q_lower for k in advisory_keywords):
        return "POLICY_ADVISORY"
    
    # Recommendation / Purchase inquiry
    rec_signals = ["show", "suggest", "recommend", "design", "dikhao", "batao", "cake", "flavor", "order", "buy", "chahiye"]
    if any(s in q_lower for s in rec_signals):
        return "CAKE_RECOMMENDATION"
    
    return "GENERAL_INQUIRY"

def filter_upto_three_cards(candidates: list[dict], min_similarity: float = 0.4, max_cards: int = 3) -> list[dict]:
    """Filters candidate cards by similarity threshold, returning up to max_cards (not fixed 3)."""
    filtered = [c for c in candidates if c.get("similarity", 0.0) >= min_similarity]
    return filtered[:max_cards]

# ==============================================================================
# TEST CASE SUITE
# ==============================================================================

class TestBakeboxRetrieval(unittest.TestCase):

    def test_3way_rrf_scoring_formula(self):
        """Verify 3-way reciprocal rank fusion formula calculation (Dense + BM25 + TF-IDF)."""
        score_top = compute_3way_rrf_score(0, 0, 0, k=60)
        expected_top = (1.0 / 61) + (1.0 / 61) + (1.0 / 61)
        self.assertAlmostEqual(score_top, expected_top, places=4)

        score_dense_only = compute_3way_rrf_score(0, None, None, k=60)
        self.assertAlmostEqual(score_dense_only, (1.0 / 61), places=4)

        # Fused multi-channel score is strictly higher than single channel
        score_fused = compute_3way_rrf_score(1, 2, 0, k=60)
        self.assertGreater(score_fused, score_dense_only)

    def test_bm25_lexical_scoring(self):
        """Verify Okapi BM25 correctly matches relevant domain tokens."""
        corpus = [
            "Red Velvet Crimson Crumb Crown with vanilla cream cheese",
            "Black Forest Classic Cherry Gateau with chocolate curls",
            "Pineapple Classic Spiral Mirror with fresh fruit chunks"
        ]
        bm25 = SimpleBM25(corpus)
        scores = bm25.score("red velvet")
        self.assertGreater(scores[0], scores[1])
        self.assertGreater(scores[0], scores[2])

    def test_intent_classification_no_order_hijack(self):
        """Verify that queries wanting to 'order' or 'buy' a cake are NOT hijacked into order status tracking."""
        self.assertEqual(classify_query_intent("I want to order a red velvet cake for anniversary"), "CAKE_RECOMMENDATION")
        self.assertEqual(classify_query_intent("Can I order a chocolate cake online?"), "CAKE_RECOMMENDATION")
        self.assertEqual(classify_query_intent("Show me pineapple cakes"), "CAKE_RECOMMENDATION")
        self.assertEqual(classify_query_intent("Black forest cake chahiye"), "CAKE_RECOMMENDATION")

    def test_intent_classification_order_tracking(self):
        """Verify that order tracking queries correctly route to ORDER_TRACKING."""
        self.assertEqual(classify_query_intent("Where is my order? Status please"), "ORDER_TRACKING")
        self.assertEqual(classify_query_intent("Track order #1002"), "ORDER_TRACKING")
        self.assertEqual(classify_query_intent("Track order for 9876543210"), "ORDER_TRACKING")
        self.assertEqual(classify_query_intent("Mera order kahan hai?"), "ORDER_TRACKING")
        self.assertEqual(classify_query_intent("Can you check the delivery status of order 1002"), "ORDER_TRACKING")

    def test_intent_classification_policy(self):
        """Verify that store policy and heating guidelines route to POLICY_ADVISORY."""
        self.assertEqual(classify_query_intent("Patties ko reheat kaise karna chahiye?"), "POLICY_ADVISORY")
        self.assertEqual(classify_query_intent("Can I microwave the fresh patties?"), "POLICY_ADVISORY")
        self.assertEqual(classify_query_intent("What is the fresh baking wait time?"), "POLICY_ADVISORY")
        self.assertEqual(classify_query_intent("Where is your main branch kitchen located?"), "POLICY_ADVISORY")

    def test_filter_upto_three_cards_dynamic(self):
        """Verify the up-to-3 cake recommendation rule (not fixed 3)."""
        candidates = [
            {"sku_id": "BB-RED-01", "name": "Red Velvet Crown", "similarity": 0.88},
            {"sku_id": "BB-RED-02", "name": "Red Velvet Heart", "similarity": 0.75},
            {"sku_id": "BB-RED-05", "name": "Red Velvet Berry", "similarity": 0.62},
            {"sku_id": "BB-RED-08", "name": "Red Velvet Cup", "similarity": 0.45},
            {"sku_id": "BB-BLK-01", "name": "Black Forest", "similarity": 0.15},
        ]

        # Should return top 3 above 0.4 threshold
        res = filter_upto_three_cards(candidates, min_similarity=0.4, max_cards=3)
        self.assertEqual(len(res), 3)
        self.assertEqual([c["sku_id"] for c in res], ["BB-RED-01", "BB-RED-02", "BB-RED-05"])

        # When only 2 match threshold, should return exactly 2 (not fixed 3)
        res_high_thresh = filter_upto_three_cards(candidates, min_similarity=0.70, max_cards=3)
        self.assertEqual(len(res_high_thresh), 2)
        self.assertEqual([c["sku_id"] for c in res_high_thresh], ["BB-RED-01", "BB-RED-02"])

        # When 1 matches
        res_very_high = filter_upto_three_cards(candidates, min_similarity=0.85, max_cards=3)
        self.assertEqual(len(res_very_high), 1)

    def test_session_isolation_and_buffer_memory(self):
        """Verify conversation buffer memory maintains strict session isolation."""
        from src.query_engine import SessionBufferMemory
        
        session_a = SessionBufferMemory(session_id="user_alice")
        session_b = SessionBufferMemory(session_id="user_bob")

        session_a.add_turn("I want a red velvet cake", "Here are 3 recommendations", "CAKE_REC")
        session_b.add_turn("Where is my order #1002?", "Order #1002 is baking", "ORDER_TRACKING")

        # Session A must not see Session B's context
        self.assertIn("red velvet", session_a.get_context_summary())
        self.assertNotIn("1002", session_a.get_context_summary())

        # Session B must not see Session A's context
        self.assertIn("1002", session_b.get_context_summary())
        self.assertNotIn("red velvet", session_b.get_context_summary())

    def test_masked_connection_string_security(self):
        """Verify that masked connection strings never expose real passwords in logs."""
        from src.db import get_masked_connection_string
        masked = get_masked_connection_string()
        self.assertIn("PWD=********", masked)
        self.assertNotIn("8844", masked)

    def test_sample_bakery_documents_schema(self):
        """Validate all seeded domain knowledge chunks adhere to required catalog attributes."""
        docs = get_sample_bakery_documents()
        self.assertGreaterEqual(len(docs), 10, "Should contain at least 10 knowledge chunks")

        cake_count = 0
        policy_count = 0
        for doc in docs:
            self.assertTrue("id" in doc and len(doc["id"]) > 0)
            self.assertTrue("text" in doc and len(doc["text"]) > 20)
            meta = doc.get("metadata", {})
            if "sku_id" in meta:
                cake_count += 1
                self.assertIn("name", meta)
                self.assertTrue(meta["price"] > 0)
                self.assertTrue(meta["weight_kg"] > 0)
            else:
                policy_count += 1
                self.assertIn("title", meta)

        self.assertGreaterEqual(cake_count, 7, "Should have at least 7 cake catalog items")
        self.assertGreaterEqual(policy_count, 3, "Should have at least 3 policy/advisory documents")

if __name__ == "__main__":
    unittest.main()
