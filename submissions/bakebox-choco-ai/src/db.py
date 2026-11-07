"""
Database Connection and Session Manager for IBM Db2.
Uses official ibm_db and ibm_db_dbi drivers.
Provides safe connection strings, DB-API 2.0 cursor execution, and session management.
"""
import os
import sys
from pathlib import Path
from contextlib import contextmanager
from typing import Any, List, Dict, Tuple

# 1. Automatically load configuration from .env file if available
try:
    from dotenv import load_dotenv
    # Check parent submission folder first, then current directory
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
DB2_USER = os.getenv("DB2_USER")
DB2_PASSWORD = os.getenv("DB2_PASSWORD")

def get_connection_string() -> str:
    """
    Build and validate standard IBM Db2 TCPIP connection string.
    Raises ValueError if required database credentials are missing.
    """
    if not DB2_USER or not DB2_PASSWORD:
        raise ValueError(
            "Missing Db2 credentials! Please configure DB2_USER and DB2_PASSWORD "
            "in your .env file or environment variables before executing database queries."
        )
    return (
        f"DATABASE={DB2_DATABASE};"
        f"HOSTNAME={DB2_HOST};"
        f"PORT={DB2_PORT};"
        f"PROTOCOL=TCPIP;"
        f"UID={DB2_USER};"
        f"PWD={DB2_PASSWORD};"
    )

def get_masked_connection_string() -> str:
    """Returns safe connection string with password masked for safe logging/display."""
    return f"DATABASE={DB2_DATABASE};HOSTNAME={DB2_HOST};PORT={DB2_PORT};PROTOCOL=TCPIP;UID={DB2_USER};PWD=********;"

def get_raw_connection():
    """Returns a raw ibm_db connection."""
    if ibm_db is None:
        raise ImportError("Please install the official IBM Db2 driver via 'pip install ibm-db' before connecting.")
    conn_str = get_connection_string()
    return ibm_db.connect(conn_str, "", "")

def get_dbi_connection():
    """Returns an active Python DB-API 2.0 connection using ibm_db_dbi."""
    if ibm_db_dbi is None:
        raise ImportError("Please install the official IBM Db2 driver via 'pip install ibm-db' before connecting.")
    conn_str = get_connection_string()
    return ibm_db_dbi.connect(conn_str, "", "")

@contextmanager
def db_session():
    """
    Context manager for safe database cursor execution.
    Ensures automatic commit on success and automatic rollback on exception.
    Always closes the connection upon completion to prevent socket leaks.
    """
    conn = get_dbi_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_query(conn: Any, sql: str, params: tuple = ()) -> list[dict]:
    """Execute a SELECT query and return list of dictionaries with uppercase column keys."""
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        cols = [desc[0].upper() for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return [dict(zip(cols, row)) for row in rows]
    finally:
        cursor.close()

def execute_dml(conn: Any, sql: str, params: tuple = ()) -> int:
    """Execute INSERT/UPDATE/DELETE statement with explicit commit."""
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
