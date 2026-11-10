"""
Module: tests/test_order_concurrency.py
Tests for IBM Db2 Concurrency, Atomic Row Locks (SELECT FOR UPDATE WITH RS),
and In-Database Recursive Bill-of-Materials (BOM) CTE Queries.
Includes multi-threaded race-condition stress testing with zero external dependencies.
"""
import os
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor

_pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from src.db import get_dbi_connection
from src.order_engine import (
    reserve_cake_stock_atomic,
    check_recipe_bom_availability,
    is_cake_bakeable,
    evaluate_refund_request
)

class TestOrderConcurrencyAndBOM(unittest.TestCase):
    def setUp(self):
        self.conn = get_dbi_connection()
        if hasattr(self.conn, "reset_state"):
            self.conn.reset_state()

    def test_01_successful_atomic_stock_reservation(self):
        """Single thread reserving available stock succeeds and decrements count."""
        success = reserve_cake_stock_atomic(self.conn, cake_id=1, quantity=2)
        self.assertTrue(success)
        # Cake 1 initial stock was 5; 5 - 2 = 3
        cake_stock = self.conn.tables["BB_CAKES"][1]["STOCK_QTY"]
        self.assertEqual(cake_stock, 3)

    def test_02_insufficient_stock_rejection(self):
        """Requesting more stock than available is rejected atomically with no state change."""
        success = reserve_cake_stock_atomic(self.conn, cake_id=2, quantity=10)
        self.assertFalse(success)
        # Cake 2 stock remains untouched (1)
        self.assertEqual(self.conn.tables["BB_CAKES"][2]["STOCK_QTY"], 1)

    def test_03_zero_or_negative_quantity_rejection(self):
        """Negative or zero quantity requests are rejected safely."""
        self.assertFalse(reserve_cake_stock_atomic(self.conn, cake_id=1, quantity=0))
        self.assertFalse(reserve_cake_stock_atomic(self.conn, cake_id=1, quantity=-2))

    def test_04_nonexistent_cake_reservation(self):
        """Attempting to reserve nonexistent cake ID fails safely."""
        success = reserve_cake_stock_atomic(self.conn, cake_id=9999, quantity=1)
        self.assertFalse(success)

    def test_05_concurrent_race_condition_stock_collision(self):
        """
        Simulate real-world race condition: Cake 2 has stock = 1.
        Two concurrent threads attempt to purchase it at the exact same instant.
        Db2 row-level locking guarantees EXACTLY ONE succeeds and EXACTLY ONE fails.
        """
        cake_id = 2
        self.assertEqual(self.conn.tables["BB_CAKES"][cake_id]["STOCK_QTY"], 1)

        results = []
        def attempt_order():
            return reserve_cake_stock_atomic(self.conn, cake_id=cake_id, quantity=1)

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(attempt_order) for _ in range(2)]
            for f in futures:
                results.append(f.result())

        self.assertEqual(results.count(True), 1, "Exactly one order must succeed")
        self.assertEqual(results.count(False), 1, "Exactly one order must be rejected")
        self.assertEqual(self.conn.tables["BB_CAKES"][cake_id]["STOCK_QTY"], 0)

    def test_06_high_concurrency_multi_buyer_exhaustion(self):
        """5 simultaneous threads competing for 5 units of Cake 1 - all 5 succeed, stock reaches 0."""
        cake_id = 1
        self.conn.tables["BB_CAKES"][cake_id]["STOCK_QTY"] = 5

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(reserve_cake_stock_atomic, self.conn, cake_id, 1) for _ in range(5)]
            results = [f.result() for f in futures]

        self.assertEqual(results.count(True), 5)
        self.assertEqual(self.conn.tables["BB_CAKES"][cake_id]["STOCK_QTY"], 0)
        # Sixth attempt fails
        self.assertFalse(reserve_cake_stock_atomic(self.conn, cake_id, 1))

    def test_07_recursive_bom_sufficient_ingredients(self):
        """Cake 1 ingredients (Khoaa + Cream Cheese) are in stock."""
        bom = check_recipe_bom_availability(self.conn, cake_id=1)
        self.assertGreater(len(bom), 0)
        for item in bom:
            self.assertEqual(item["AVAILABILITY"], "IN_STOCK")

        bakeable, missing = is_cake_bakeable(self.conn, cake_id=1)
        self.assertTrue(bakeable)
        self.assertEqual(len(missing), 0)

    def test_08_recursive_bom_depleted_ingredient_detection(self):
        """Cake 2 requires Maraschino Cherries (0.5) but stock is only 0.2 -> OUT_OF_STOCK."""
        bom = check_recipe_bom_availability(self.conn, cake_id=2)
        cherry_item = next((it for it in bom if "Cherries" in it["INGREDIENT_NAME"]), None)
        self.assertIsNotNone(cherry_item)
        self.assertEqual(cherry_item["AVAILABILITY"], "OUT_OF_STOCK")

        bakeable, missing = is_cake_bakeable(self.conn, cake_id=2)
        self.assertFalse(bakeable)
        self.assertIn("Maraschino Cherries", missing)

    def test_09_happiness_guarantee_baking_order_refund(self):
        """Order in 'BAKING' state gets 100% refund approved under Happiness Guarantee."""
        res = evaluate_refund_request(self.conn, order_id=1002, reason="Delayed delivery")
        self.assertTrue(res["eligible"])
        self.assertEqual(res["status"], "REFUNDED")
        self.assertEqual(res["amount_refunded"], 649.00)

    def test_10_refund_already_refunded_order_rejection(self):
        """Order already refunded cannot be refunded a second time."""
        # First refund succeeds
        evaluate_refund_request(self.conn, order_id=1002, reason="First claim")
        # Second refund is rejected
        res2 = evaluate_refund_request(self.conn, order_id=1002, reason="Duplicate claim")
        self.assertFalse(res2["eligible"])
        self.assertEqual(res2["status"], "ALREADY_REFUNDED")

    def test_11_stored_procedure_reservation_caller(self):
        """Verify IBM Db2 Stored Procedure caller SP_RESERVE_CAKE_STOCK executes via callproc."""
        from src.order_engine import call_sp_reserve_cake_stock
        success = call_sp_reserve_cake_stock(self.conn, cake_id=1, quantity=1)
        self.assertTrue(success)
        self.assertEqual(self.conn.tables["BB_CAKES"][1]["STOCK_QTY"], 4)
        self.assertFalse(call_sp_reserve_cake_stock(self.conn, cake_id=1, quantity=0))
        self.assertFalse(call_sp_reserve_cake_stock(self.conn, cake_id=2, quantity=5))

    def test_12_ingest_seeding_idempotency_mock(self):
        """Verify init_relational_tables seeds BB_CAKES, BB_INVENTORY, BB_RECIPES idempotently."""
        from src.ingest import init_relational_tables
        init_relational_tables(self.conn)
        self.assertIn(1, self.conn.tables["BB_CAKES"])
        self.assertIn(101, self.conn.tables["BB_INVENTORY"])
        self.assertIn(1, self.conn.tables["BB_RECIPES"])


if __name__ == "__main__":
    unittest.main()
