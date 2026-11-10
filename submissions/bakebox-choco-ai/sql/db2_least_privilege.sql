-- ==============================================================================
-- BAKEBOX CHOCO AI — IBM Db2 Least-Privilege Role & Permission Script
-- Target: IBM Db2 LUW (Community Edition / Db2 11.5 / 12.1+)
-- Purpose: Enforces principle of least privilege by separating read-only RAG/lookup
--          access from runtime transactional mutations and DDL schema ownership.
-- ==============================================================================
-- Execution: Run once as Db2 schema owner / SECADM (e.g. db2 -tvf sql/db2_least_privilege.sql)
-- Note: Create OS/Db2 users `bb_reader` and `bb_app` before assigning roles.

-- 1. Read-Only Role (RAG vector search, catalog & recipe BOM read, order lookup)
CREATE ROLE BAKEBOX_READER_ROLE;

GRANT SELECT ON TABLE BB_CHUNKS_VECTOR       TO ROLE BAKEBOX_READER_ROLE;
GRANT SELECT ON TABLE BB_CAKES               TO ROLE BAKEBOX_READER_ROLE;
GRANT SELECT ON TABLE BB_INVENTORY           TO ROLE BAKEBOX_READER_ROLE;
GRANT SELECT ON TABLE BB_RECIPES             TO ROLE BAKEBOX_READER_ROLE;
GRANT SELECT ON TABLE BB_ORDERS              TO ROLE BAKEBOX_READER_ROLE;
GRANT SELECT ON TABLE BB_ORDER_ITEMS         TO ROLE BAKEBOX_READER_ROLE;
GRANT SELECT ON TABLE V_ACTIVE_BAKERY_ORDERS TO ROLE BAKEBOX_READER_ROLE;

-- Explicitly no INSERT / UPDATE / DELETE / ALTER / DROP privileges on BAKEBOX_READER_ROLE.

-- 2. Runtime Application Role (Least-privilege DML + append-only audit log)
CREATE ROLE BAKEBOX_APP_ROLE;

GRANT ROLE BAKEBOX_READER_ROLE               TO ROLE BAKEBOX_APP_ROLE;
GRANT UPDATE (STOCK_QTY) ON TABLE BB_CAKES   TO ROLE BAKEBOX_APP_ROLE;
GRANT UPDATE (ORDER_STATUS) ON TABLE BB_ORDERS TO ROLE BAKEBOX_APP_ROLE;
GRANT INSERT, SELECT ON TABLE BB_AUDIT_LOG   TO ROLE BAKEBOX_APP_ROLE;
GRANT EXECUTE ON PROCEDURE SP_RESERVE_CAKE_STOCK TO ROLE BAKEBOX_APP_ROLE;

-- Note: BB_AUDIT_LOG intentionally withholds UPDATE and DELETE grants from
--       runtime application users to enforce append-only cryptographic immutability.

-- 3. Bind Roles to Dedicated Service Accounts
-- Configure DB2_READONLY_USER=bb_reader and DB2_USER=bb_app in .env
GRANT ROLE BAKEBOX_READER_ROLE TO USER bb_reader;
GRANT ROLE BAKEBOX_APP_ROLE    TO USER bb_app;
