"""
Unit and Integration Tests for BAKEBOX Choco AI Retrieval & Tool Logic.
Validates real production components (ChocoQueryEngine, Db2HybridRRFRetriever,
BakeboxDb2VectorStore, SimpleBM25, and PII Security Masking).
Runs offline with zero external network or database dependencies:
  pytest tests -v
Or via standard library:
  python tests/test_retrieval.py
"""
import os
import sys
import unittest
import json

# Ensure parent directory is in sys.path so 'src' can be imported seamlessly
_pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from src.ingest import get_sample_bakery_documents
from src.retriever import SimpleBM25, compute_rrf_score, Db2HybridRRFRetriever
from src.query_engine import (
    ChocoQueryEngine,
    SessionBufferMemory,
    mask_customer_name,
    mask_phone_number,
    mask_delivery_address
)
from src.db import get_masked_connection_string

try:
    from llama_index.core.schema import TextNode
except ImportError:
    TextNode = None


class TestBakeboxProduction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize real production engine in deterministic offline mode
        cls.engine = ChocoQueryEngine(use_llm=False)

    def test_3way_rrf_scoring_formula(self):
        """Verify 3-way reciprocal rank fusion formula calculation (Dense + BM25 + TF-IDF)."""
        score_top = compute_rrf_score([0, 0, 0], k=60)
        expected_top = (1.0 / 61) + (1.0 / 61) + (1.0 / 61)
        self.assertAlmostEqual(score_top, expected_top, places=4)

        score_dense_only = compute_rrf_score([0, None, None], k=60)
        self.assertAlmostEqual(score_dense_only, (1.0 / 61), places=4)

        # Fused multi-channel score is strictly higher than single channel
        score_fused = compute_rrf_score([1, 2, 0], k=60)
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

    def test_real_engine_intent_routing_cake_purchase(self):
        """Verify real ChocoQueryEngine routes purchase queries to CAKE_RECOMMENDATION (not order tracking)."""
        res1 = self.engine.query("I want to order a red velvet cake for anniversary celebration", session_id="test_rec_1")
        self.assertEqual(res1["intent"], "CAKE_RECOMMENDATION")
        self.assertTrue(len(res1["ui_cards"]) > 0)

        res2 = self.engine.query("Show me pineapple cakes", session_id="test_rec_2")
        self.assertEqual(res2["intent"], "CAKE_RECOMMENDATION")

    def test_real_engine_intent_routing_order_tracking(self):
        """Verify real ChocoQueryEngine routes tracking queries to ORDER_TRACKING intents."""
        res1 = self.engine.query("Where is my order? Status please", session_id="test_track_1")
        self.assertEqual(res1["intent"], "ORDER_TRACKING_PROMPT")

        res2 = self.engine.query("Track order #1002", session_id="test_track_2")
        self.assertEqual(res2["intent"], "ORDER_AUTH_REQUIRED")

    def test_real_engine_intent_routing_policy(self):
        """Verify real ChocoQueryEngine routes operational queries to store policy or general inquiry."""
        res = self.engine.query("Patties ko reheat kaise karna chahiye?", session_id="test_pol_1")
        self.assertIn(res["intent"], ["GENERAL_INQUIRY", "POLICY_ADVISORY"])
        self.assertIn("tawa", res["reply"].lower())

    def test_real_tool_recommend_cakes_dynamic_upto_three(self):
        """Verify real engine.tool_recommend_cakes returns UP TO 3 dynamic cards (not fixed 3)."""
        cards = self.engine.tool_recommend_cakes("red velvet", limit=3)
        self.assertLessEqual(len(cards), 3)
        self.assertGreaterEqual(len(cards), 1)
        for c in cards:
            self.assertIn("sku_id", c)
            self.assertIn("name", c)
            self.assertIn("price", c)
            self.assertTrue(c["price"] > 0)

    def test_real_tool_track_live_order_security_and_masking(self):
        """Verify real engine.tool_track_live_order enforces two-factor auth and PII masking."""
        # 1. Order ID without phone must be blocked
        res_no_phone = self.engine.tool_track_live_order(order_id=1002, phone_number=None)
        self.assertEqual(res_no_phone.get("auth_error"), "VERIFICATION_REQUIRED")

        # 2. Order ID with wrong phone must be rejected
        res_wrong_phone = self.engine.tool_track_live_order(order_id=1002, phone_number="9999999999")
        self.assertEqual(res_wrong_phone.get("auth_error"), "PHONE_MISMATCH")

        # 3. Order ID with registered phone must succeed with masked PII
        res_verified = self.engine.tool_track_live_order(order_id=1002, phone_number="+91 9876543210")
        self.assertIsNotNone(res_verified)
        self.assertEqual(res_verified["ORDER_ID"], 1002)
        # Ensure customer name and phone are masked at the database layer
        self.assertIn("*", res_verified["CUSTOMER_NAME"])
        self.assertIn("*", res_verified["CUSTOMER_PHONE"])
        self.assertTrue(res_verified["CUSTOMER_PHONE"].endswith("3210"))
        self.assertIn("Confidential", res_verified["DELIVERY_ADDRESS"])

        # Also verify space-separated phone formatting works seamlessly
        res_spaced = self.engine.tool_track_live_order(order_id=1002, phone_number="98765 43210")
        self.assertIsNotNone(res_spaced)
        self.assertEqual(res_spaced["ORDER_ID"], 1002)

    def test_real_tool_track_live_order_like_wildcard_defense(self):
        """Verify that wildcard injection characters (% or _) in phone are neutralized."""
        # Attempting wildcard injection '%' or short input returns VERIFICATION_REQUIRED
        res_pct = self.engine.tool_track_live_order(order_id=1002, phone_number="%")
        self.assertEqual(res_pct.get("auth_error"), "VERIFICATION_REQUIRED")

        # 10 characters with wildcards like '98%65432_0' stripped to 8 digits returns VERIFICATION_REQUIRED
        res_wild = self.engine.tool_track_live_order(order_id=1002, phone_number="98%65432_0")
        self.assertEqual(res_wild.get("auth_error"), "VERIFICATION_REQUIRED")

        # 10 numeric digits that don't match the order phone returns PHONE_MISMATCH
        res_wrong = self.engine.tool_track_live_order(order_id=1002, phone_number="9111111111")
        self.assertEqual(res_wrong.get("auth_error"), "PHONE_MISMATCH")

    def test_multi_order_offline_support(self):
        """Verify real order tracking supports both Order #1002 and Order #1104 from sample_orders.json."""
        res_1104 = self.engine.tool_track_live_order(order_id=1104, phone_number="+91 9811223344")
        self.assertIsNotNone(res_1104)
        self.assertEqual(res_1104["ORDER_ID"], 1104)
        self.assertIn("*", res_1104["CUSTOMER_NAME"])
        self.assertTrue(res_1104["CUSTOMER_PHONE"].endswith("3344"))

    def test_session_isolation_and_buffer_memory(self):
        """Verify real SessionBufferMemory maintains strict session isolation."""
        session_a = SessionBufferMemory(session_id="user_alice")
        session_b = SessionBufferMemory(session_id="user_bob")

        session_a.add_turn("I want a red velvet cake", "Here are recommendations", "CAKE_REC")
        session_b.add_turn("Where is my order #1002?", "Order #1002 is baking", "ORDER_TRACKING")

        self.assertIn("red velvet", session_a.get_context_summary())
        self.assertNotIn("1002", session_a.get_context_summary())

        self.assertIn("1002", session_b.get_context_summary())
        self.assertNotIn("red velvet", session_b.get_context_summary())

    def test_session_memory_ttl_expiration(self):
        """Verify that inactive sessions expire and are cleanly evicted after TTL."""
        session = SessionBufferMemory(session_id="test_expiring_session", ttl_seconds=10)
        session.add_turn("Hello", "Hi there", "GREETING")

        self.assertFalse(session.is_expired(current_time=session.last_active + 5))
        self.assertTrue(session.is_expired(current_time=session.last_active + 11))

    def test_real_retriever_dynamic_index_synchronization(self):
        """Verify real Db2HybridRRFRetriever.refresh_index synchronizes lexical channels."""
        if not TextNode:
            self.skipTest("llama_index TextNode not available")

        retriever = self.engine.retriever
        initial_count = len(retriever.corpus_nodes)
        new_node = TextNode(
            text="Special Mathura Peda Delight Cake with saffron pistachios",
            id_="CAKE_PEDA_01",
            metadata={"sku_id": "BB-PEDA-01", "name": "Mathura Peda Delight"}
        )
        updated_nodes = list(retriever.corpus_nodes) + [new_node]
        retriever.refresh_index(updated_nodes)

        self.assertEqual(len(retriever.corpus_nodes), initial_count + 1)
        scores = retriever.bm25.score("mathura peda delight")
        self.assertTrue(any(s > 0.0 for s in scores))

    def test_policy_metadata_filtering_strictness(self):
        """Verify real engine.tool_get_store_policy_or_advisory never returns cake SKU cards."""
        policy_texts = self.engine.tool_get_store_policy_or_advisory("reheat patties")
        self.assertTrue(len(policy_texts) > 0)
        for p in policy_texts:
            self.assertNotIn("SKU: BB-", p)

    def test_data_directory_and_masked_connection(self):
        """Verify sample data files are present and connection strings mask passwords."""
        # 1. Verify sample_catalog.json and sample_orders.json are present and populated
        cat_path = os.path.join(_pkg_root, "data", "sample_catalog.json")
        ord_path = os.path.join(_pkg_root, "data", "sample_orders.json")
        self.assertTrue(os.path.isfile(cat_path), "data/sample_catalog.json must exist")
        self.assertTrue(os.path.isfile(ord_path), "data/sample_orders.json must exist")

        with open(cat_path, "r", encoding="utf-8") as f:
            cat_data = json.load(f)
        with open(ord_path, "r", encoding="utf-8") as f:
            ord_data = json.load(f)
        self.assertGreaterEqual(len(cat_data), 5)
        self.assertGreaterEqual(len(ord_data), 2)

        # 2. Verify masked connection string does not expose plaintext secrets
        masked = get_masked_connection_string()
        self.assertIn("PWD=********", masked)


if __name__ == "__main__":
    unittest.main()
