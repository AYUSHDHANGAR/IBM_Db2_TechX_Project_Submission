"""Transcripts (timestamped Whisper segments) -> chunks -> multilingual embeddings -> Db2 table voice_kb."""
from haystack import Pipeline
from haystack.components.writers import DocumentWriter
from haystack_integrations.components.embedders.sentence_transformers import SentenceTransformersDocumentEmbedder
from common.db2_store import get_store
from chunks import build_chunks
from config import EMB_MODEL, EMB_DIM, TABLE, PASSAGE_PREFIX

docs = build_chunks()

store = get_store(TABLE, EMB_DIM, "COSINE", recreate_table=True)
p = Pipeline()
p.add_component("embed", SentenceTransformersDocumentEmbedder(model=EMB_MODEL, prefix=PASSAGE_PREFIX))
p.add_component("write", DocumentWriter(document_store=store))
p.connect("embed", "write")
print(p.run({"embed": {"documents": docs}}))
print("rows in Db2:", store.count_documents())
store.close()
