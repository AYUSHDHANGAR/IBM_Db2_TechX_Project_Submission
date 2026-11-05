"""
Advanced Hybrid RRF (Reciprocal Rank Fusion) Retriever for LlamaIndex & IBM Db2.
Fuses three independent retrieval channels:
1. Native IBM Db2 Vector Store Search (via DB2LlamaVS with in-engine Cosine distance)
2. BM25 Lexical Ranking (Okapi BM25 Term Matching & Document Frequency)
3. TF-IDF Lexical Feature Ranking (Scikit-Learn Sub-linear Term Matching)
Fused using Reciprocal Rank Fusion (RRF: k=60) for enterprise retrieval precision.
"""
import math
import re
from collections import Counter
from typing import List, Dict, Any, Optional
import numpy as np
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
except ImportError:
    TfidfVectorizer = None

try:
    from fastembed import TextEmbedding
    HAS_FASTEMBED = True
except ImportError:
    HAS_FASTEMBED = False
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        pass

try:
    from llama_index.core.retrievers import BaseRetriever
    from llama_index.core.schema import NodeWithScore, TextNode
    from llama_index.core.vector_stores.types import VectorStoreQuery
except ImportError:
    class BaseRetriever:
        pass
    NodeWithScore = None
    TextNode = None
    VectorStoreQuery = None

from src.vector_store import BakeboxDb2VectorStore

class SimpleBM25:
    """
    Lightweight, high-performance Okapi BM25 implementation for lexical sparse retrieval.
    Precomputes term frequencies using hash maps (O(1) lookups) avoiding repeated list scanning.
    Zero external heavy dependencies; calculates exact BM25 scores across corpus tokens.
    """
    def __init__(self, corpus_texts: List[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus_texts)
        self.tokenized_corpus = [self._tokenize(doc) for doc in corpus_texts]
        self.doc_counts = [Counter(doc) for doc in self.tokenized_corpus]
        self.doc_lengths = [len(doc) for doc in self.tokenized_corpus]
        self.avg_doc_len = sum(self.doc_lengths) / (self.corpus_size or 1)
        
        # Calculate Document Frequencies (DF)
        self.df: Dict[str, int] = {}
        for counts in self.doc_counts:
            for term in counts.keys():
                self.df[term] = self.df.get(term, 0) + 1

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b[a-zA-Z0-9_\-]+\b', text.lower())

    def score(self, query: str) -> List[float]:
        q_tokens = self._tokenize(query)
        scores = [0.0] * self.corpus_size
        
        for term in q_tokens:
            if term not in self.df:
                continue
            df_term = self.df[term]
            # Standard Robertson-Spärck Jones IDF
            idf = math.log(1.0 + (self.corpus_size - df_term + 0.5) / (df_term + 0.5))
            
            for i, counts in enumerate(self.doc_counts):
                tf = counts.get(term, 0)
                if tf > 0:
                    denom = tf + self.k1 * (1.0 - self.b + self.b * (self.doc_lengths[i] / (self.avg_doc_len or 1)))
                    scores[i] += idf * (tf * (self.k1 + 1.0) / denom)
        return scores


class Db2HybridRRFRetriever(BaseRetriever):
    """
    Advanced Hybrid RAG Retriever that fuses IBM Db2 native dense vector search
    with both BM25 and TF-IDF lexical retrieval using Reciprocal Rank Fusion (RRF: k=60).
    """
    def __init__(
        self,
        vector_store: BakeboxDb2VectorStore,
        corpus_nodes: Optional[List[TextNode]] = None,
        model_name: str = "BAAI/bge-small-en-v1.5",
        rrf_k: int = 60
    ):
        super().__init__()
        self.vector_store = vector_store
        self.rrf_k = rrf_k
        self.corpus_nodes = corpus_nodes or []
        self.nodes_dict = {n.id_: n for n in self.corpus_nodes}
        self.corpus_ids = [n.id_ for n in self.corpus_nodes]
        self.corpus_texts = [n.text for n in self.corpus_nodes]

        # 1. Local Dense Embedding Engine
        print(f"Loading embedding model '{model_name}' for query vectorization...")
        if HAS_FASTEMBED:
            self.fast_model = TextEmbedding(model_name=model_name)
            self.embed_func = lambda q: list(self.fast_model.embed([q]))[0].tolist()
        else:
            from sentence_transformers import SentenceTransformer
            self.st_model = SentenceTransformer(model_name)
            self.embed_func = lambda q: self.st_model.encode(q).tolist()

        # 2. Sparse Lexical Engine A: Okapi BM25
        self.bm25 = SimpleBM25(self.corpus_texts) if self.corpus_texts else None

        # 3. Sparse Lexical Engine B: TF-IDF
        if TfidfVectorizer and self.corpus_texts:
            self.tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
            self.tfidf_matrix = self.tfidf.fit_transform(self.corpus_texts)
        else:
            self.tfidf = None
            self.tfidf_matrix = None

    def _retrieve(self, query_bundle) -> List[NodeWithScore]:
        query_str = query_bundle.query_str
        return self.hybrid_retrieve(query_str, top_k=5)

    def hybrid_retrieve(self, query: str, top_k: int = 5) -> List[NodeWithScore]:
        """
        Executes 3-way hybrid search:
        - Dense Vector Search in IBM Db2 (DB2LlamaVS)
        - Sparse Lexical BM25 Ranking
        - Sparse Lexical TF-IDF Ranking
        Fuses rankings using Reciprocal Rank Fusion: score = sum(1 / (k + rank)).
        """
        # Channel 1: Dense Semantic Search via IBM Db2 DB2LlamaVS
        q_emb = self.embed_func(query)
        dense_res = self.vector_store.query(query_embedding=q_emb, top_k=top_k * 3)
        dense_ranked_ids = dense_res.ids or []

        # Cache any live nodes returned directly by DB2LlamaVS
        live_nodes_map: Dict[str, TextNode] = {}
        if dense_res.nodes:
            for idx, n in enumerate(dense_res.nodes):
                node_id = dense_ranked_ids[idx] if idx < len(dense_ranked_ids) else n.id_
                live_nodes_map[node_id] = n

        # Channel 2: Sparse Lexical BM25 Search
        bm25_ranked_ids = []
        if self.bm25 and self.corpus_texts:
            bm25_scores = self.bm25.score(query)
            top_bm25_indices = np.argsort(bm25_scores)[::-1][:top_k * 3]
            bm25_ranked_ids = [self.corpus_ids[i] for i in top_bm25_indices if bm25_scores[i] > 0.0]

        # Channel 3: Sparse Lexical TF-IDF Search
        tfidf_ranked_ids = []
        if self.tfidf_matrix is not None and self.corpus_texts:
            try:
                q_vec = self.tfidf.transform([query])
                sims = (self.tfidf_matrix * q_vec.T).toarray().flatten()
                top_tfidf_indices = np.argsort(sims)[::-1][:top_k * 3]
                tfidf_ranked_ids = [self.corpus_ids[i] for i in top_tfidf_indices if sims[i] > 0.0]
            except Exception:
                tfidf_ranked_ids = []

        # 4. Multi-Channel Reciprocal Rank Fusion (RRF: k=60)
        rrf_scores: Dict[str, float] = {}

        # Dense ranking contribution (IBM Db2)
        for rank, doc_id in enumerate(dense_ranked_ids):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (self.rrf_k + rank + 1))

        # BM25 ranking contribution
        for rank, doc_id in enumerate(bm25_ranked_ids):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (self.rrf_k + rank + 1))

        # TF-IDF ranking contribution
        for rank, doc_id in enumerate(tfidf_ranked_ids):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (self.rrf_k + rank + 1))

        # Sort candidate documents by fused RRF score
        sorted_candidates = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        # Construct final NodeWithScore objects
        results: List[NodeWithScore] = []
        for doc_id, score in sorted_candidates:
            node = live_nodes_map.get(doc_id) or self.nodes_dict.get(doc_id)
            if node:
                results.append(NodeWithScore(node=node, score=score))

        return results

    def refresh_index(self, updated_nodes: List[TextNode]):
        """
        Dynamically synchronizes lexical BM25 and TF-IDF channels with newly ingested
        Db2 document nodes, ensuring corpus consistency across all 3 retrieval channels.
        """
        self.corpus_nodes = updated_nodes
        self.nodes_dict = {n.id_: n for n in updated_nodes}
        self.corpus_ids = [n.id_ for n in updated_nodes]
        self.corpus_texts = [n.text for n in updated_nodes]
        
        # Rebuild lexical indexes for newly synced corpus
        self.bm25 = SimpleBM25(self.corpus_texts)
        if TfidfVectorizer and self.corpus_texts:
            self.tfidf_matrix = self.tfidf.fit_transform(self.corpus_texts)
        print(f"[SYNC] Lexical BM25 and TF-IDF indexes synchronized ({len(updated_nodes)} nodes).")
