# Architecture: Multilingual Voice RAG on Db2

## Idea
Spoken content in Hindi and English is searchable in either language. Each answer points back to the audio file and the time range it came from.

## Components
| Component | Role |
|---|---|
| `src/scripts/make_audio.py` | Turns `scripts/talk_en.txt` and `scripts/talk_hi.txt` into `audio/talk_en.mp3` and `audio/talk_hi.mp3` (text-to-speech, one-time developer tool) |
| `src/transcribe.py` | Whisper `medium` transcribes each mp3 into timestamped segments saved as `transcripts/*.json` |
| `src/chunks.py` | Groups 3 segments per chunk with 1 segment of overlap; each chunk keeps `language`, `source`, `start`, `end` |
| `src/index.py` | `SentenceTransformersDocumentEmbedder` (multilingual-e5-base, prefix `passage: `) -> `DocumentWriter(IBMDb2DocumentStore)` |
| `src/query.py` | `SentenceTransformersTextEmbedder` (prefix `query: `) -> `IBMDb2EmbeddingRetriever` -> `ChatPromptBuilder` -> `OpenAIChatGenerator` (local Ollama) |
| `src/common/db2_store.py` | Builds `IBMDb2DocumentStore` from environment variables |

## Data flow
```text
audio mp3 -> Whisper -> segments (text, start, end) -> chunks -> embed (768-d) -> Db2 table voice_kb
question (Hindi or English) -> embed -> Db2 VECTOR_DISTANCE top 3 -> LLM answer + [audio file, start-end]
```

## Db2 design
```sql
CREATE TABLE voice_kb (
  id VARCHAR(512) NOT NULL PRIMARY KEY,
  content CLOB(2M),
  meta BLOB,                        -- JSON: language, source, start, end
  embedding VECTOR(768, FLOAT32)
)
```
Retrieval statement (from the integration source):
```sql
SELECT id, content, SYSTOOLS.BSON2JSON(meta), embedding,
       VECTOR_DISTANCE(embedding, VECTOR(?, 768, FLOAT32), COSINE) AS score
FROM voice_kb
WHERE embedding IS NOT NULL
ORDER BY score ASC FETCH FIRST 3 ROWS ONLY
```
Hindi and English chunks share one table and one vector space, so a question in either language can retrieve chunks from either file.

## Models
- Speech to text: Whisper `medium`, language forced per file (`en`, `hi`).
- Embeddings: `intfloat/multilingual-e5-base`, 768 dimensions, with `query: ` and `passage: ` prefixes. The table dimension equals the model output size.
- Answers: Ollama `qwen2.5:7b` through its OpenAI-compatible endpoint, instructed to answer in the question's language.
