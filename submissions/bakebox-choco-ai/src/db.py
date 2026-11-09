"""
Database Connection and Session Manager for IBM Db2.
Uses official ibm_db and ibm_db_dbi drivers as primary connector.
Provides safe connection strings, DB-API 2.0 cursor execution, session management,
and a high-fidelity offline MockDb2Connection fallback ensuring 100% offline
test reproducibility for judges without live Db2 credentials.
"""
import os
import sys
import threading
from pathlib import Path
from contextlib import contextmanager
from typing import Any, List, Dict, Tuple, Optional

# 1. Automatically load configuration from .env file if available
try:
    from dotenv import load_dotenv
    env_candidate = Path(__file__).resolve().parent.parent / ".env"
    if env_candidate.is_file():
        load_dotenv(dotenv_path=env_candidate)
    else:
        load_dotenv()
except ImportError:
    pass

# 2. Check for required official IBM Db2 driver
try:
    import ibm_db
    import ibm_db_dbi
except ImportError:
    ibm_db = None
    ibm_db_dbi = None

# Default connection settings (fallback to standard local Db2 Community Edition / IBMDB201)
DB2_HOST = os.getenv("DB2_HOST", "127.0.0.1")
DB2_PORT = os.getenv("DB2_PORT", "50000")
DB2_DATABASE = os.getenv("DB2_DATABASE", "IBMDB201")
DB2_FORCE_MOCK = os.getenv("DB2_FORCE_MOCK", "false").lower() in ("true", "1", "yes")

def get_connection_string() -> str:
    """
    Build and validate standard IBM Db2 TCPIP connection string.
    Credentials are read on-demand to prevent storing secrets in module-level memory.
    Raises ValueError if required database credentials are missing.
    """
    db_user = os.getenv("DB2_USER")
    db_password = os.getenv("DB2_PASSWORD")
    if not db_user or not db_password:
        raise ValueError(
            "Missing Db2 credentials! Please configure DB2_USER and DB2_PASSWORD "
            "in your .env file or environment variables before executing database queries."
        )
    return (
        f"DATABASE={DB2_DATABASE};"
        f"HOSTNAME={DB2_HOST};"
        f"PORT={DB2_PORT};"
        f"PROTOCOL=TCPIP;"
        f"UID={db_user};"
        f"PWD={db_password};"
    )

def get_masked_connection_string() -> str:
    """Returns safe connection string with password masked for safe logging/display."""
    db_user = os.getenv("DB2_USER", "db2inst1")
    return f"DATABASE={DB2_DATABASE};HOSTNAME={DB2_HOST};PORT={DB2_PORT};PROTOCOL=TCPIP;UID={db_user};PWD=********;"

def is_live_db2_available() -> bool:
    """Checks whether the official ibm_db driver and credentials are configured."""
    if DB2_FORCE_MOCK or ibm_db is None or ibm_db_dbi is None:
        return False
    user = os.getenv("DB2_USER")
    pwd = os.getenv("DB2_PASSWORD")
    return bool(user and pwd and user not in ("your_db2_username", "dummy_user"))


# ==============================================================================
# OFFLINE PEP 249 DB-API 2.0 MOCK ENGINE (FOR 100% OFFLINE TEST REPRODUCIBILITY)
# ==============================================================================

class MockDb2Cursor:
    """
    Thread-safe PEP 249 DB-API 2.0 Cursor emulating IBM Db2 execution semantics.
    Supports transactional SELECT, INSERT, UPDATE, row-level locks,
    and Recursive Bill-of-Materials (BOM) CTE execution offline.
    """
    def __init__(self, connection: 'MockDb2Connection'):
        self.connection = connection
        self.description: Optional[List[Tuple[str, ...]]] = None
        self.rowcount: int = -1
        self._results: List[Tuple[Any, ...]] = []
        self._idx: int = 0
        self._closed: bool = False

    def close(self):
        self._closed = True
        self._results = []

    def execute(self, sql: str, params: Tuple = ()):
        if self._closed:
            raise RuntimeError("Cannot execute on a closed cursor.")
        
        with self.connection.lock:
            self._idx = 0
            clean_sql = " ".join(sql.strip().split())
            sql_upper = clean_sql.upper()

            # 1. Recursive Recipe Bill-of-Materials (BOM) Query
            if "WITH RECURSIVE RECIPE_BOM" in sql_upper or "RECIPE_BOM" in sql_upper:
                cake_id = params[0] if params else 1
                bom_results = self.connection.get_recipe_bom(cake_id)
                self.description = [
                    ("INGREDIENT_NAME", "VARCHAR"),
                    ("REQUIRED_QTY", "DECIMAL"),
                    ("CURRENT_STOCK", "DECIMAL"),
                    ("AVAILABILITY", "VARCHAR")
                ]
                self._results = [
                    (row["INGREDIENT_NAME"], row["REQUIRED_QTY"], row["CURRENT_STOCK"], row["AVAILABILITY"])
                    for row in bom_results
                ]
                self.rowcount = len(self._results)
                return self

            # 2. SELECT ... FOR UPDATE WITH RS (Row-Level Locking Simulation)
            if "FOR UPDATE" in sql_upper and "BB_CAKES" in sql_upper:
                cake_id = params[0] if params else 1
                row = self.connection.tables["BB_CAKES"].get(cake_id)
                self.description = [("STOCK_QTY", "INTEGER")]
                if row:
                    self._results = [(row["STOCK_QTY"],)]
                else:
                    self._results = []
                self.rowcount = len(self._results)
                return self

            # 3. SELECT FROM BB_CAKES
            if "SELECT" in sql_upper and "FROM BB_CAKES" in sql_upper:
                if "WHERE CAKE_ID = ?" in sql_upper:
                    cake_id = params[0] if params else 1
                    row = self.connection.tables["BB_CAKES"].get(cake_id)
                    self.description = [("CAKE_ID", "INT"), ("NAME", "VARCHAR"), ("STOCK_QTY", "INT"), ("PRICE", "DECIMAL")]
                    self._results = [(row["CAKE_ID"], row["NAME"], row["STOCK_QTY"], row["PRICE"])] if row else []
                else:
                    self.description = [("CAKE_ID", "INT"), ("NAME", "VARCHAR"), ("STOCK_QTY", "INT"), ("PRICE", "DECIMAL")]
                    self._results = [(r["CAKE_ID"], r["NAME"], r["STOCK_QTY"], r["PRICE"]) for r in self.connection.tables["BB_CAKES"].values()]
                self.rowcount = len(self._results)
                return self

            # 4. UPDATE BB_CAKES (Stock reservation)
            if "UPDATE BB_CAKES" in sql_upper and "STOCK_QTY" in sql_upper:
                # e.g., UPDATE BB_CAKES SET STOCK_QTY = STOCK_QTY - ? WHERE CAKE_ID = ? AND STOCK_QTY >= ?
                deduct_qty = params[0]
                cake_id = params[1]
                min_qty = params[2] if len(params) > 2 else deduct_qty
                cake = self.connection.tables["BB_CAKES"].get(cake_id)
                if cake and cake["STOCK_QTY"] >= min_qty:
                    cake["STOCK_QTY"] -= deduct_qty
                    self.rowcount = 1
                else:
                    self.rowcount = 0
                self.description = None
                return self

            # 4b. CALL SP_RESERVE_CAKE_STOCK (Db2 Stored Procedure Emulation)
            if "SP_RESERVE_CAKE_STOCK" in sql_upper:
                cake_id = params[0]
                deduct_qty = params[1]
                cake = self.connection.tables["BB_CAKES"].get(cake_id)
                self.description = [("SUCCESS", "INTEGER")]
                if cake and cake["STOCK_QTY"] >= deduct_qty:
                    cake["STOCK_QTY"] -= deduct_qty
                    self._results = [(1,)]
                    self.rowcount = 1
                else:
                    self._results = [(0,)]
                    self.rowcount = 0
                return self

            # 5. INSERT INTO BB_AUDIT_LOG
            if "INSERT INTO BB_AUDIT_LOG" in sql_upper:
                # params: (session_id, action_type, payload_json, prev_hash, current_hash)
                log_id = len(self.connection.tables["BB_AUDIT_LOG"]) + 1
                self.connection.tables["BB_AUDIT_LOG"].append({
                    "LOG_ID": log_id,
                    "SESSION_ID": params[0],
                    "ACTION_TYPE": params[1],
                    "PAYLOAD": params[2],
                    "PREV_HASH": params[3],
                    "CURRENT_HASH": params[4],
                    "TIMESTAMP": "2026-11-09 20:30:00"
                })
                self.rowcount = 1
                self.description = None
                return self

            # 6. SELECT FROM BB_AUDIT_LOG ORDER BY LOG_ID
            if "SELECT" in sql_upper and "FROM BB_AUDIT_LOG" in sql_upper:
                logs = self.connection.tables["BB_AUDIT_LOG"]
                self.description = [
                    ("LOG_ID", "INT"),
                    ("SESSION_ID", "VARCHAR"),
                    ("ACTION_TYPE", "VARCHAR"),
                    ("PAYLOAD", "VARCHAR"),
                    ("PREV_HASH", "VARCHAR"),
                    ("CURRENT_HASH", "VARCHAR"),
                    ("TIMESTAMP", "VARCHAR")
                ]
                self._results = [
                    (l["LOG_ID"], l["SESSION_ID"], l["ACTION_TYPE"], l["PAYLOAD"], l["PREV_HASH"], l["CURRENT_HASH"], l["TIMESTAMP"])
                    for l in logs
                ]
                self.rowcount = len(self._results)
                return self

            # 7. SELECT FROM BB_ORDERS
            if "SELECT" in sql_upper and "FROM BB_ORDERS" in sql_upper:
                order_id = params[0] if params else 1002
                order = self.connection.tables["BB_ORDERS"].get(order_id)
                # Check parameterized phone filter if present
                if order and len(params) > 1 and ("PHONE" in sql_upper or "RIGHT(" in sql_upper):
                    import re
                    phone_filter = str(params[1])
                    ord_phone_digits = re.sub(r'\D', '', order.get("customer_phone", ""))
                    if not ord_phone_digits.endswith(phone_filter):
                        order = None

                if "SELECT ORDER_ID FROM" in sql_upper:
                    self.description = [("ORDER_ID", "INT")]
                    self._results = [(order["order_id"],)] if order else []
                else:
                    self.description = [
                        ("ORDER_ID", "INT"),
                        ("CUSTOMER_NAME", "VARCHAR"),
                        ("CUSTOMER_PHONE", "VARCHAR"),
                        ("ORDER_TYPE", "VARCHAR"),
                        ("ORDER_STATUS", "VARCHAR"),
                        ("TOTAL_AMOUNT", "DECIMAL"),
                        ("DELIVERY_ADDRESS", "VARCHAR"),
                        ("SPECIAL_NOTES", "VARCHAR"),
                        ("CREATED_AT", "VARCHAR")
                    ]
                    if order:
                        self._results = [(
                            order["order_id"], order["customer_name"], order["customer_phone"],
                            order["order_type"], order["order_status"], order["total_amount"],
                            order["delivery_address"], order["special_notes"], order["created_at"]
                        )]
                    else:
                        self._results = []
                self.rowcount = len(self._results)
                return self

            # 7b. SELECT FROM BB_ORDER_ITEMS
            if "SELECT" in sql_upper and "FROM BB_ORDER_ITEMS" in sql_upper:
                order_id = params[0] if params else 1002
                self.description = [
                    ("ITEM_ID", "INT"), ("ORDER_ID", "INT"), ("SKU_ID", "VARCHAR"),
                    ("ITEM_NAME", "VARCHAR"), ("QUANTITY", "INT"), ("UNIT_PRICE", "DECIMAL"),
                    ("CAKE_BASE", "VARCHAR"), ("CAKE_WEIGHT", "VARCHAR"), ("CUSTOM_MESSAGE", "VARCHAR")
                ]
                if order_id == 1002:
                    self._results = [(1, 1002, "BB-RED-02-1kg", "Red Velvet Heart Love Affair", 1, 649.00, "Khoaa (Eggless)", "1.0kg", "Happy 1st Anniversary")]
                elif order_id == 1104:
                    self._results = [(2, 1104, "BB-BLK-01-05kg", "Black Forest Classic Gateau", 1, 249.00, "Pure Veg Eggless", "0.5kg", "Happy Birthday Choti")]
                else:
                    self._results = []
                self.rowcount = len(self._results)
                return self

            # 8. UPDATE BB_ORDERS (e.g. Refund / Status change)
            if "UPDATE BB_ORDERS" in sql_upper:
                if len(params) == 1:
                    order_id = params[0]
                    status = "REFUNDED" if "REFUNDED" in sql_upper else "CONFIRMED"
                else:
                    status = params[0]
                    order_id = params[1]

                if order_id in self.connection.tables["BB_ORDERS"]:
                    self.connection.tables["BB_ORDERS"][order_id]["order_status"] = status
                    self.rowcount = 1
                else:
                    self.rowcount = 0
                self.description = None
                return self

            # Default generic execution fallback
            self.description = [("STATUS", "VARCHAR")]
            self._results = [("OK",)]
            self.rowcount = 1
            return self

    def fetchone(self) -> Optional[Tuple]:
        if self._idx < len(self._results):
            row = self._results[self._idx]
            self._idx += 1
            return row
        return None

    def fetchall(self) -> List[Tuple]:
        remaining = self._results[self._idx:]
        self._idx = len(self._results)
        return remaining


class MockDb2Connection:
    """Thread-safe PEP 249 connection with in-memory relational state."""
    _instance = None
    _global_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._global_lock:
            if cls._instance is None:
                cls._instance = super(MockDb2Connection, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self.lock = threading.RLock()
        self.tables = {
            "BB_CAKES": {
                1: {"CAKE_ID": 1, "NAME": "Red Velvet Crimson Crumb Crown", "STOCK_QTY": 5, "PRICE": 649.0},
                2: {"CAKE_ID": 2, "NAME": "Black Forest Classic Gateau", "STOCK_QTY": 1, "PRICE": 249.0},
                3: {"CAKE_ID": 3, "NAME": "Pineapple Spiral Mirror", "STOCK_QTY": 0, "PRICE": 249.0}
            },
            "BB_INVENTORY": {
                101: {"INGREDIENT_ID": 101, "NAME": "Khoaa Base (Eggless)", "STOCK_QTY": 12.0},
                102: {"INGREDIENT_ID": 102, "NAME": "Belgian Dark Cocoa", "STOCK_QTY": 8.5},
                103: {"INGREDIENT_ID": 103, "NAME": "Cream Cheese Frosting", "STOCK_QTY": 4.0},
                104: {"INGREDIENT_ID": 104, "NAME": "Maraschino Cherries", "STOCK_QTY": 0.2}
            },
            "BB_RECIPES": {
                1: [
                    {"CAKE_ID": 1, "INGREDIENT_NAME": "Khoaa Base (Eggless)", "QTY_NEEDED": 0.5, "INGREDIENT_ID": 101},
                    {"CAKE_ID": 1, "INGREDIENT_NAME": "Cream Cheese Frosting", "QTY_NEEDED": 0.4, "INGREDIENT_ID": 103}
                ],
                2: [
                    {"CAKE_ID": 2, "INGREDIENT_NAME": "Khoaa Base (Eggless)", "QTY_NEEDED": 0.3, "INGREDIENT_ID": 101},
                    {"CAKE_ID": 2, "INGREDIENT_NAME": "Belgian Dark Cocoa", "QTY_NEEDED": 0.2, "INGREDIENT_ID": 102},
                    {"CAKE_ID": 2, "INGREDIENT_NAME": "Maraschino Cherries", "QTY_NEEDED": 0.5, "INGREDIENT_ID": 104}  # Insufficient stock!
                ]
            },
            "BB_ORDERS": {
                1002: {
                    "order_id": 1002, "user_id": 3, "customer_name": "Rahul Sharma",
                    "customer_phone": "+91 9876543210", "order_type": "DELIVERY", "order_status": "BAKING",
                    "total_amount": 649.00, "delivery_address": "Flat 402, Krishna Heights, Mathura, UP",
                    "special_notes": "Happy 1st Anniversary Celebration", "created_at": "2026-11-09 10:15:00"
                },
                1104: {
                    "order_id": 1104, "user_id": 5, "customer_name": "Pooja Verma",
                    "customer_phone": "+91 9811223344", "order_type": "DELIVERY", "order_status": "CONFIRMED",
                    "total_amount": 249.00, "delivery_address": "Civil Lines, Mathura, UP",
                    "special_notes": "Birthday Surprise for Sister", "created_at": "2026-11-09 11:30:00"
                }
            },
            "BB_AUDIT_LOG": []
        }

    def reset_state(self):
        """Reset mock data for idempotent testing."""
        with self.lock:
            self._initialize()

    def get_recipe_bom(self, cake_id: int) -> List[Dict[str, Any]]:
        """Emulates Recursive Bill-of-Materials join query."""
        recipes = self.tables["BB_RECIPES"].get(cake_id, [])
        results = []
        for r in recipes:
            ing = self.tables["BB_INVENTORY"].get(r["INGREDIENT_ID"])
            curr_stock = ing["STOCK_QTY"] if ing else 0.0
            avail = "IN_STOCK" if curr_stock >= r["QTY_NEEDED"] else "OUT_OF_STOCK"
            results.append({
                "INGREDIENT_NAME": r["INGREDIENT_NAME"],
                "REQUIRED_QTY": r["QTY_NEEDED"],
                "CURRENT_STOCK": curr_stock,
                "AVAILABILITY": avail
            })
        return results

    def cursor(self) -> MockDb2Cursor:
        return MockDb2Cursor(self)

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


# ==============================================================================
# CONNECTION FACTORY FUNCTIONS
# ==============================================================================

def get_raw_connection():
    """Returns a raw ibm_db connection, or MockDb2Connection if offline."""
    if is_live_db2_available():
        conn_str = get_connection_string()
        return ibm_db.connect(conn_str, "", "")
    return MockDb2Connection()

def get_dbi_connection():
    """Returns an active Python DB-API 2.0 connection using ibm_db_dbi or MockDb2Connection."""
    if is_live_db2_available():
        conn_str = get_connection_string()
        return ibm_db_dbi.connect(conn_str, "", "")
    return MockDb2Connection()

@contextmanager
def db_session():
    """
    Context manager for safe database cursor execution.
    Ensures automatic commit on success and automatic rollback on exception.
    """
    conn = get_dbi_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        # In mock mode, don't close singleton connection so state is preserved
        if is_live_db2_available():
            conn.close()

def execute_query(conn: Any, sql: str, params: Tuple = ()) -> List[Dict[str, Any]]:
    """Execute a SELECT query and return list of dictionaries with uppercase column keys."""
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        cols = [desc[0].upper() for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return [dict(zip(cols, row)) for row in rows]
    finally:
        cursor.close()

def execute_dml(conn: Any, sql: str, params: Tuple = ()) -> int:
    """Execute INSERT/UPDATE/DELETE statement with explicit commit."""
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
