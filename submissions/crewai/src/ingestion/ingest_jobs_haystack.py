#!/usr/bin/env python
"""
Official Haystack 2.x Ingestion Pipeline for IBM Db2.
Uses local offline IBM Granite Embedding Model (ibm-granite/granite-embedding-311m-multilingual-r2)
via SentenceTransformersDocumentEmbedder to embed and index job postings into IBMDb2DocumentStore.
"""

import os
import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from haystack import Pipeline, Document
from haystack.utils import Secret
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy

try:
    from haystack_integrations.components.embedders.sentence_transformers import (
        SentenceTransformersDocumentEmbedder,
    )
except ImportError:
    SentenceTransformersDocumentEmbedder = None

try:
    from haystack_integrations.document_stores.ibm_db.document_store import IBMDb2DocumentStore
except ImportError:
    IBMDb2DocumentStore = None

from src.utils.db2_config import get_db2_config
from src.utils.embeddings import get_embedding_model_name, get_embedding_dimension


def get_db2_document_store() -> "IBMDb2DocumentStore":
    """Initialize the official IBM Db2 Document Store for Haystack using unified config."""
    if IBMDb2DocumentStore is None:
        print("Error: 'ibm-db-haystack' is not installed.")
        print("Please run: pip install ibm-db-haystack")
        sys.exit(1)

    cfg = get_db2_config()
    embedding_dim = get_embedding_dimension()

    print(
        f"🔧 Connecting to IBM Db2 Document Store ({cfg['hostname']}:{cfg['port']}/{cfg['database']}), "
        f"Table: '{cfg['table_name']}' (Vector Dim: {embedding_dim})..."
    )

    return IBMDb2DocumentStore(
        database=cfg["database"],
        hostname=cfg["hostname"],
        port=cfg["port"],
        username=Secret.from_token(cfg["username"]),
        password=Secret.from_token(cfg["password"]),
        protocol=cfg["protocol"],
        table_name=cfg["table_name"],
        embedding_dim=embedding_dim,
        distance_metric="COSINE",
        recreate_table=False,
    )


def load_job_documents_from_csv(csv_path: str) -> list[Document]:
    """Load job listings from a CSV file and convert them into Haystack Document objects."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Job dataset not found at: {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"📄 Loaded {len(df)} job records from {csv_path}")

    documents = []
    for _, row in df.iterrows():
        job_id = str(row["job_id"])
        job_title = str(row["job_title"])
        company = str(row["company_name"])
        location = str(row["location"])
        exp_level = str(row.get("experience_level", "Mid-Senior"))
        skills = str(row["required_skills"])
        responsibilities = str(row["responsibilities"])

        # Formulate full descriptive text for dense embedding representation
        content = (
            f"Job Title: {job_title}\n"
            f"Company: {company}\n"
            f"Location: {location}\n"
            f"Experience Level: {exp_level}\n"
            f"Required Skills: {skills}\n"
            f"Responsibilities: {responsibilities}"
        )

        metadata = {
            "job_id": job_id,
            "job_title": job_title,
            "company_name": company,
            "location": location,
            "experience_level": exp_level,
            "required_skills": skills,
            "responsibilities": responsibilities,
        }

        documents.append(Document(id=job_id, content=content, meta=metadata))

    return documents


def build_haystack_ingestion_pipeline(document_store: "IBMDb2DocumentStore") -> Pipeline:
    """
    Build the Haystack ingestion pipeline using local SentenceTransformersDocumentEmbedder
    with the offline IBM Granite Embedding Model.
    """
    model_name = get_embedding_model_name()
    print(f"📦 Configuring Haystack Local Embedder with model: '{model_name}'...")

    pipeline = Pipeline()

    # 1. Local Offline SentenceTransformers Document Embedder (IBM Granite)
    pipeline.add_component(
        "embedder",
        SentenceTransformersDocumentEmbedder(
            model=model_name,
            progress_bar=True,
        ),
    )

    # 2. Document Writer component for IBM Db2
    pipeline.add_component(
        "writer",
        DocumentWriter(
            document_store=document_store,
            policy=DuplicatePolicy.OVERWRITE,
        ),
    )

    # Connect components: embedder -> writer
    pipeline.connect("embedder.documents", "writer.documents")

    return pipeline


def main():
    print("==================================================")
    print("🚀 Starting Local Haystack Ingestion -> IBM Db2")
    print(f"🧠 Model: {get_embedding_model_name()}")
    print("==================================================")

    workspace_root = Path(__file__).resolve().parent.parent.parent
    csv_path = os.getenv("JOBS_CSV_PATH", str(workspace_root / "data" / "jobs.csv"))

    # 1. Initialize official IBMDb2DocumentStore with unified config
    doc_store = get_db2_document_store()

    # 2. Load dataset into Haystack Documents
    documents = load_job_documents_from_csv(csv_path)

    # 3. Assemble and execute Haystack ingestion pipeline with local Granite embedder
    pipeline = build_haystack_ingestion_pipeline(document_store=doc_store)

    print("\n⚡ Running local embedding & ingestion pipeline...")
    result = pipeline.run({"embedder": {"documents": documents}})

    written_count = result.get("writer", {}).get("documents_written", len(documents))
    print(f"\n Successfully ingested {written_count} documents into IBM Db2 Document Store.")
    print("==================================================")


if __name__ == "__main__":
    main()
