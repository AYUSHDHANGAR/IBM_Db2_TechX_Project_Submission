"""Single factory for IBMDb2DocumentStore; connection settings come from the environment."""
import os

from haystack.utils import Secret
from haystack_integrations.document_stores.ibm_db import IBMDb2DocumentStore


def _load_dotenv(paths=(".env", "../.env")):
    for path in paths:
        if not os.path.exists(path):
            continue
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


_load_dotenv()


def get_store(table_name, embedding_dim, distance_metric="COSINE", recreate_table=False):
    schema = os.environ.get("DB2_SCHEMA") or None
    return IBMDb2DocumentStore(
        database=os.environ["DB2_DB"],
        hostname=os.environ["DB2_HOST"],
        port=int(os.environ.get("DB2_PORT", "50000")),
        username=Secret.from_env_var("DB2_USERNAME"),
        password=Secret.from_env_var("DB2_PASSWORD"),
        schema=schema,
        table_name=table_name,
        embedding_dim=embedding_dim,
        distance_metric=distance_metric,
        recreate_table=recreate_table,
    )
