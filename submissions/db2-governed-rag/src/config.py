import os
EMB_MODEL = os.environ.get("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")  # 384-dim, cached locally
EMB_DIM = int(os.environ.get("EMB_DIM", "384"))  # must equal the model's output size
TABLE = "gov_kb"
# user role -> clearance levels that role may read (enforced inside Db2 via the retrieval filter)
ROLES = {
    "public user":     ["public"],
    "internal user":   ["public", "internal"],
    "restricted user": ["public", "internal", "restricted"],
}
