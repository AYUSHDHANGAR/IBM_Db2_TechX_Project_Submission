import os
EMB_MODEL = os.environ.get("VOICE_EMB_MODEL", "intfloat/multilingual-e5-base")
EMB_DIM = int(os.environ.get("VOICE_EMB_DIM", "768"))  # multilingual-e5-base output size
TABLE = "voice_kb"
PASSAGE_PREFIX = "passage: "  # e5 models expect these prefixes
QUERY_PREFIX = "query: "
SEGMENTS_PER_CHUNK = 3
SEGMENT_OVERLAP = 1
