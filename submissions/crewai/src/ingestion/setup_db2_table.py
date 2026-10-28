#!/usr/bin/env python
"""
Setup script to initialize the IBM Db2 table with VECTOR datatype support.
Creates the `JOB_POSTINGS` table designed for `DB2VectorSearchTool` and `IBMDb2DocumentStore`.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    import ibm_db
except ImportError:
    ibm_db = None

from src.utils.db2_config import get_db2_config


def get_connection():
    """Establish connection to IBM Db2 using unified configuration."""
    cfg = get_db2_config()

    if ibm_db is None:
        print("Error: 'ibm_db' package is not installed. Run 'pip install ibm_db'.")
        sys.exit(1)

    try:
        conn = ibm_db.connect(cfg["connection_string"], "", "")
        print(f" Connected successfully to IBM Db2 ({cfg['hostname']}:{cfg['port']}/{cfg['database']}).")
        return conn, cfg
    except Exception as e:
        print(f"❌ Failed to connect to IBM Db2: {e}")
        sys.exit(1)


def create_job_postings_table(conn, cfg):
    """Create the table with VECTOR support if it doesn't already exist."""
    dimension = int(os.getenv("EMBEDDING_DIMENSION", "768"))
    table_name = cfg["table_name"]

    # Schema matching Haystack IBMDb2DocumentStore & CrewAI DB2VectorSearchTool
    ddl_statement = f"""
    CREATE TABLE {table_name} (
        ID VARCHAR(128) NOT NULL PRIMARY KEY,
        CONTENT CLOB,
        DATAFRAME CLOB,
        BLOB_DATA BLOB,
        BLOB_MIME_TYPE VARCHAR(128),
        META CLOB,
        EMBEDDING VECTOR({dimension}, FLOAT32)
    )
    """

    check_table_sql = f"SELECT COUNT(*) FROM SYSCAT.TABLES WHERE TABNAME = '{table_name.upper()}'"

    try:
        stmt = ibm_db.exec_immediate(conn, check_table_sql)
        row = ibm_db.fetch_tuple(stmt)
        if row and row[0] > 0:
            print(f"ℹ️ Table '{table_name}' already exists in IBM Db2.")
            return

        print(f"Creating '{table_name}' table with {dimension}-dim VECTOR column...")
        ibm_db.exec_immediate(conn, ddl_statement)
        print(f" Table '{table_name}' created successfully.")
    except Exception as e:
        print(f"Error checking/creating table: {e}")
        raise
    finally:
        ibm_db.close(conn)


def main():
    print("==================================================")
    print("🛠️  IBM Db2 Vector Table Initialization")
    print("==================================================")
    conn, cfg = get_connection()
    create_job_postings_table(conn, cfg)
    print("==================================================")


if __name__ == "__main__":
    main()
