"""Ask one question as each role. Clearance filtering happens inside the Db2 SQL (WHERE ... ORDER BY VECTOR_DISTANCE)."""
import sys, json
from haystack import Pipeline
from haystack_integrations.components.embedders.sentence_transformers import SentenceTransformersTextEmbedder
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.components.retrievers.ibm_db import IBMDb2EmbeddingRetriever
from common.db2_store import get_store
import os
from config import EMB_MODEL, EMB_DIM, TABLE, ROLES

NO_LLM = "--no-llm" in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith("--")]
question = args[0] if args else "What happened in the recent security incident and how was it handled?"

store = get_store(TABLE, EMB_DIM, "COSINE")
tmpl = [ChatMessage.from_user(
    "Answer using ONLY the context. If the context does not contain the answer, say you have no access to that information.\n"
    "Context:\n{% for d in documents %}[{{ d.meta.doc_id }}] {{ d.content }}\n{% endfor %}\n"
    "Question: {{ question }}")]

pipe = Pipeline()
pipe.add_component("embedder", SentenceTransformersTextEmbedder(model=EMB_MODEL))
pipe.add_component("retriever", IBMDb2EmbeddingRetriever(document_store=store, top_k=4))
pipe.connect("embedder.embedding", "retriever.query_embedding")
if not NO_LLM:
    pipe.add_component("prompt", ChatPromptBuilder(template=tmpl, required_variables=["question", "documents"]))
    pipe.add_component("llm", OpenAIChatGenerator(
        api_key=Secret.from_token("ollama"), model=os.environ.get("OLLAMA_MODEL", "qwen2.5:7b"),
        api_base_url=os.environ.get("OLLAMA_URL", "http://localhost:11434") + "/v1"))
    pipe.connect("retriever.documents", "prompt.documents")
    pipe.connect("prompt.prompt", "llm.messages")

print(f"\nQUESTION: {question}")
for role, levels in ROLES.items():
    f = {"field": "meta.clearance", "operator": "in", "value": levels}
    data = {"embedder": {"text": question}, "retriever": {"filters": f}}
    if not NO_LLM:
        data["prompt"] = {"question": question}
    out = pipe.run(data, include_outputs_from={"retriever"})
    docs = out["retriever"]["documents"]
    print(f"\n=== {role}  filter={json.dumps(f)}")
    for d in docs:
        print(f"  {d.score:.3f}  [{d.meta['clearance']:10}] {d.meta['doc_id']:7} {d.meta['title']}")
    if not NO_LLM:
        print("  ANSWER:", out["llm"]["replies"][0].text.strip())
store.close()
