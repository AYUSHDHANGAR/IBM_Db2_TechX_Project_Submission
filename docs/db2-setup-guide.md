# IBM Db2 Quick Setup & Connector Guide

This guide provides fast setup instructions for provisioning a local **IBM Db2 Community Edition** database and connecting to it from common programming languages and AI frameworks.

---

## 1. Running IBM Db2 Community Edition with Docker

The fastest way to get a local Db2 instance running for hackathon development is using Docker:

```bash
docker run -d --name db2server \
  --restart always \
  -p 50000:50000 \
  --env-file .env.db2 \
  -v db2_data:/database \
  icr.io/db2_community/db2:latest
```

Example `.env.db2` file:
```ini
LICENSE=accept
DB2INSTANCE=db2inst1
DB2INST1_PASSWORD=YourSecurePassword123!
DBNAME=testdb
BLU=false
ENABLE_ORACLE_COMPATIBILITY=false
```

Verify that the container is healthy:
```bash
docker logs -f db2server
# Wait until you see: "(*) Setup has completed."
```

---

## 2. Connecting from Python

### Native Driver (`ibm_db`)
```bash
pip install ibm_db
```
```python
import os
import ibm_db

conn_str = (
    f"DATABASE={os.getenv('DB2_DATABASE', 'testdb')};"
    f"HOSTNAME={os.getenv('DB2_HOST', 'localhost')};"
    f"PORT={os.getenv('DB2_PORT', '50000')};"
    f"PROTOCOL=TCPIP;"
    f"UID={os.getenv('DB2_USER', 'db2inst1')};"
    f"PWD={os.getenv('DB2_PASSWORD', 'YourSecurePassword123!')};"
)

conn = ibm_db.connect(conn_str, "", "")
print("Connected successfully to IBM Db2!")
```

### SQLAlchemy / LangChain Integration
```bash
pip install ibm_db_sa sqlalchemy langchain-community
```
```python
from sqlalchemy import create_engine

db_uri = f"db2+ibm_db://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(db_uri)
```

---

## 3. Connecting from Node.js / JavaScript

```bash
npm install ibm_db
```
```javascript
import ibm_db from 'ibm_db';

const connStr = `DATABASE=${process.env.DB2_DATABASE};HOSTNAME=${process.env.DB2_HOST};PORT=${process.env.DB2_PORT};PROTOCOL=TCPIP;UID=${process.env.DB2_USER};PWD=${process.env.DB2_PASSWORD};`;

ibm_db.open(connStr, (err, conn) => {
  if (err) return console.error(err);
  console.log("Connected to IBM Db2!");
  conn.close();
});
```

---

## 4. Connecting from Java / JDBC

Maven dependency:
```xml
<dependency>
    <groupId>com.ibm.db2</groupId>
    <artifactId>jcc</artifactId>
    <version>11.5.8.0</version>
</dependency>
```

JDBC Connection string:
```text
jdbc:db2://localhost:50000/testdb:user=db2inst1;password=YourSecurePassword123!;
```
