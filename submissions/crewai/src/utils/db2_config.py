"""
Shared IBM Db2 Configuration Helper.
Allows unified environment variables across both Haystack ingestion and CrewAI retrieval.
Supports either a single `DB2_CONNECTION_STRING` or individual `DB2_*` parameters.
"""

import os
from typing import Dict, Any

# Ensure CrewAI DB2JSONEncoder supports memoryview/CLOB objects returned by ibm_db
try:
    from crewai_tools.tools.db2_search_tool.db2_search_tool import DB2JSONEncoder

    _orig_default = DB2JSONEncoder.default

    def _safe_db2_json_default(self, obj):
        if isinstance(obj, memoryview):
            try:
                return bytes(obj).decode("utf-8")
            except UnicodeDecodeError:
                return bytes(obj).hex()
        return _orig_default(self, obj)

    DB2JSONEncoder.default = _safe_db2_json_default
except (ImportError, AttributeError):
    pass


def parse_db2_connection_string(conn_str: str) -> Dict[str, Any]:
    """Parse a Db2 connection string into key-value pairs."""
    params: Dict[str, Any] = {}
    if not conn_str:
        return params

    for part in conn_str.strip().strip(";").split(";"):
        if "=" in part:
            key, val = part.split("=", 1)
            params[key.strip().upper()] = val.strip()
    return params


def get_db2_config() -> Dict[str, Any]:
    """
    Get consolidated Db2 configuration.
    Extracts parameters from either DB2_CONNECTION_STRING or individual environment variables.
    """
    conn_str = os.getenv("DB2_CONNECTION_STRING", "")
    parsed = parse_db2_connection_string(conn_str)

    database = parsed.get("DATABASE") or os.getenv("DB2_DATABASE", "BLUDB")
    hostname = parsed.get("HOSTNAME") or os.getenv("DB2_HOSTNAME", "localhost")
    port = int(parsed.get("PORT") or os.getenv("DB2_PORT", "50000"))
    protocol = parsed.get("PROTOCOL") or os.getenv("DB2_PROTOCOL", "TCPIP")
    username = parsed.get("UID") or os.getenv("DB2_USERNAME", "db2inst1")
    password = parsed.get("PWD") or os.getenv("DB2_PASSWORD", "password")
    table_name = os.getenv("DB2_TABLE_NAME", "JOB_POSTINGS")

    # Form standard connection string if not explicitly defined
    if not conn_str:
        conn_str = f"DATABASE={database};HOSTNAME={hostname};PORT={port};PROTOCOL={protocol};UID={username};PWD={password};"

    return {
        "database": database,
        "hostname": hostname,
        "port": port,
        "protocol": protocol,
        "username": username,
        "password": password,
        "table_name": table_name,
        "connection_string": conn_str,
    }
