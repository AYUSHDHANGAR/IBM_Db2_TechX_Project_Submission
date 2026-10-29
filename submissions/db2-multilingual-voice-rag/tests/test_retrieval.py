"""Db2-free tests: chunking keeps audio file + timestamps, and the multilingual embedder maps
Hindi and English questions to the matching transcript chunk (same ranking Db2 computes with COSINE)."""
import pathlib, sys
import numpy as np

SRC = pathlib.Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

from chunks import build_chunks  # noqa: E402
from config import EMB_MODEL, QUERY_PREFIX, PASSAGE_PREFIX  # noqa: E402


def test_chunks_have_source_and_time_range():
    docs = build_chunks()
    assert {d.meta["language"] for d in docs} == {"en", "hi"}
    for d in docs:
        assert d.meta["source"].startswith("audio/") and d.meta["start"] < d.meta["end"]
    assert len({d.id for d in docs}) == len(docs)


def test_hindi_and_english_questions_find_the_right_chunk():
    from sentence_transformers import SentenceTransformer
    docs = build_chunks()
    m = SentenceTransformer(EMB_MODEL)
    P = m.encode([PASSAGE_PREFIX + d.content for d in docs], normalize_embeddings=True)
    cases = [  # (question, expected source file, expected start-time window)
        ("Which distance metrics does Db2 support?", "audio/talk_en.mp3", (30, 45)),
        ("Db2 में कौन से डिस्टेंस मीट्रिक उपलब्ध हैं?", "audio/talk_hi.mp3", (25, 40)),
        ("What must match the embedding model's output size?", "audio/talk_en.mp3", (85, 95)),
        ("एम्बेडिंग का आकार किससे मेल खाना चाहिए?", "audio/talk_hi.mp3", (70, 90)),
    ]
    for q, src, (a, b) in cases:
        scores = (m.encode([QUERY_PREFIX + q], normalize_embeddings=True) @ P.T)[0]
        top = [docs[j] for j in scores.argsort()[::-1][:3]]
        assert any(d.meta["source"] == src and d.meta["start"] <= b and d.meta["end"] >= a for d in top), q
