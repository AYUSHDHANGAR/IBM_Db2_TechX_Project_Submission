"""Index data/documents.jsonl into Db2: split -> embed -> write. Metadata rides along on every chunk."""
import json
from haystack import Document, Pipeline
from haystack.components.preprocessors import DocumentSplitter
from haystack_integrations.components.embedders.sentence_transformers import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from common.db2_store import get_store
from config import EMB_MODEL, EMB_DIM, TABLE

store = get_store(TABLE, EMB_DIM, "COSINE", recreate_table=True)

docs = []
for line in open("data/documents.jsonl"):
    r = json.loads(line)
    docs.append(Document(id=r["id"], content=r["text"], meta={**r["meta"], "title": r["title"], "doc_id": r["id"]}))

p = Pipeline()
p.add_component("split", DocumentSplitter(split_by="period", split_length=3, split_overlap=1))
p.add_component("embed", SentenceTransformersDocumentEmbedder(model=EMB_MODEL))
p.add_component("write", DocumentWriter(document_store=store))
p.connect("split", "embed"); p.connect("embed", "write")
print(p.run({"split": {"documents": docs}}))
print("rows in Db2:", store.count_documents())
store.close()
