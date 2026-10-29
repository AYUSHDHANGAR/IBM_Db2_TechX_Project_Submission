# Architecture: Governed RAG on Db2

## Idea
Access control is enforced **before** the LLM sees anything. The clearance rule is a `WHERE` clause in the same Db2 statement that ranks by vector similarity, so restricted text is never fetched for an unauthorised user.

## Components
| Component | Role |
|---|---|
| `src/build_dataset.py` | Writes 30 synthetic, non-sensitive documents with `category`, `priority`, `department`, `clearance` metadata to `src/data/documents.jsonl` |
| `src/index.py` | Haystack pipeline: `DocumentSplitter(period)` -> `SentenceTransformersDocumentEmbedder` -> `DocumentWriter(IBMDb2DocumentStore)` |
| `src/query.py` | Haystack pipeline: `SentenceTransformersTextEmbedder` -> `IBMDb2EmbeddingRetriever(filters=role filter)` -> `ChatPromptBuilder` -> `OpenAIChatGenerator` (pointed at local Ollama) |
| `src/common/db2_store.py` | One factory that builds `IBMDb2DocumentStore` from environment variables |

## Data flow
```text
documents.jsonl -> split -> embed (384-d) -> Db2 table gov_kb
question + role -> embed -> Db2: WHERE clearance IN (role levels) ORDER BY VECTOR_DISTANCE -> top 4 chunks -> LLM -> answer
```

## Db2 design
Table created by `ibm-db-haystack`:
```sql
CREATE TABLE gov_kb (
  id VARCHAR(512) NOT NULL PRIMARY KEY,
  content CLOB(2M),
  meta BLOB,                       -- JSON metadata (clearance, category, ...)
  embedding VECTOR(384, FLOAT32)
)
```
Retrieval statement (from the integration source):
```sql
SELECT id, content, SYSTOOLS.BSON2JSON(meta), embedding,
       VECTOR_DISTANCE(embedding, VECTOR(?, 384, FLOAT32), COSINE) AS score
FROM gov_kb
WHERE JSON_VALUE(SYSTOOLS.BSON2JSON(meta), '$.clearance' RETURNING VARCHAR(1000)) IN (?, ?)
  AND embedding IS NOT NULL
ORDER BY score ASC FETCH FIRST ? ROWS ONLY
```

## Role mapping
| Role | Clearance levels allowed |
|---|---|
| public user | public |
| internal user | public, internal |
| restricted user | public, internal, restricted |

## Models
Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions), run locally. Answers: Ollama `qwen2.5:7b`, called through its OpenAI-compatible endpoint.
