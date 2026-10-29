"""Ask a question in Hindi or English. Retrieval runs in Db2; every hit is shown with its audio file and timestamps."""
import sys, os
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.components.embedders.sentence_transformers import SentenceTransformersTextEmbedder
from haystack_integrations.components.retrievers.ibm_db import IBMDb2EmbeddingRetriever
from common.db2_store import get_store
from config import EMB_MODEL, EMB_DIM, TABLE, QUERY_PREFIX

NO_LLM = "--no-llm" in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith("--")]
question = args[0] if args else "Db2 में कौन से डिस्टेंस मीट्रिक उपलब्ध हैं?"

store = get_store(TABLE, EMB_DIM, "COSINE")
tmpl = [ChatMessage.from_user(
    "Answer in the same language as the question, using ONLY the context. "
    "If the context does not contain the answer, say so.\n"
    "Context:\n{% for d in documents %}[{{ d.meta.source }} {{ d.meta.start }}s-{{ d.meta.end }}s] {{ d.content }}\n{% endfor %}\n"
    "Question: {{ question }}")]

pipe = Pipeline()
pipe.add_component("embedder", SentenceTransformersTextEmbedder(model=EMB_MODEL, prefix=QUERY_PREFIX))
pipe.add_component("retriever", IBMDb2EmbeddingRetriever(document_store=store, top_k=3))
pipe.connect("embedder.embedding", "retriever.query_embedding")
if not NO_LLM:
    pipe.add_component("prompt", ChatPromptBuilder(template=tmpl, required_variables=["question", "documents"]))
    pipe.add_component("llm", OpenAIChatGenerator(
        api_key=Secret.from_token("ollama"), model=os.environ.get("OLLAMA_MODEL", "qwen2.5:7b"),
        api_base_url=os.environ.get("OLLAMA_URL", "http://localhost:11434") + "/v1"))
    pipe.connect("retriever.documents", "prompt.documents")
    pipe.connect("prompt.prompt", "llm.messages")

data = {"embedder": {"text": question}}
if not NO_LLM:
    data["prompt"] = {"question": question}
out = pipe.run(data, include_outputs_from={"retriever"})
print("QUESTION:", question)
for d in out["retriever"]["documents"]:
    print(f"  {d.score:.3f}  {d.meta['source']}  {d.meta['start']}s-{d.meta['end']}s  [{d.meta['language']}]  {d.content[:90]}")
if not NO_LLM:
    print("ANSWER:", out["llm"]["replies"][0].text.strip())
store.close()
