"""Turn timestamped Whisper segments into overlapping chunks that keep audio file and time range."""
import json, pathlib
from haystack import Document
from config import SEGMENTS_PER_CHUNK, SEGMENT_OVERLAP

ROOT = pathlib.Path(__file__).resolve().parent


def build_chunks(transcripts_dir=ROOT / "transcripts"):
    docs = []
    for path in sorted(pathlib.Path(transcripts_dir).glob("*.json")):
        t = json.loads(path.read_text(encoding="utf-8"))
        seg = t["segments"]
        for i in range(0, len(seg), SEGMENTS_PER_CHUNK):
            g = seg[max(0, i - SEGMENT_OVERLAP): i + SEGMENTS_PER_CHUNK]
            docs.append(Document(
                id=f"{path.stem}-{g[0]['start']}",
                content=" ".join(s["text"] for s in g),
                meta={"language": t["language"], "source": t["source"], "start": g[0]["start"], "end": g[-1]["end"]}))
    return docs
