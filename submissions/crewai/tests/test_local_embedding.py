"""
Automated validation and test suite for IBM Granite Local Embeddings,
Haystack Document Pipeline, and CrewAI DB2 Vector Search Tool configuration.
"""

import sys
import unittest
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.utils.embeddings import (
    local_embedding_function,
    get_sentence_transformer_model,
    get_embedding_dimension,
)
from src.ingestion.ingest_jobs_haystack import load_job_documents_from_csv
from src.utils.db2_config import get_db2_config


class TestProfileMatcherArchitecture(unittest.TestCase):
    """Test suite for validating local models and pipeline components."""

    def test_01_granite_local_embedding(self):
        """Verify local IBM Granite embedding generation and dimension size."""
        test_text = "Senior Python AI Engineer with CrewAI and RAG experience."
        print(f"\n[Test] Generating local embedding for: '{test_text}'")
        
        embedding = local_embedding_function(test_text)
        self.assertIsInstance(embedding, list)
        self.assertEqual(len(embedding), 768, f"Expected 768 dimensions, got {len(embedding)}")
        self.assertTrue(all(isinstance(x, float) for x in embedding))
        print(f" Embedding generated successfully: length={len(embedding)}, sample={embedding[:3]}...")

    def test_02_job_data_parsing(self):
        """Verify Haystack Document loading from CSV."""
        csv_path = str(ROOT_DIR / "data" / "jobs.csv")
        documents = load_job_documents_from_csv(csv_path)
        
        self.assertGreater(len(documents), 0, "Expected non-empty documents list")
        doc = documents[0]
        self.assertIn("job_title", doc.meta)
        self.assertIn("required_skills", doc.meta)
        self.assertIn("Job Title:", doc.content)
        print(f" Haystack documents parsed successfully: count={len(documents)}, sample_id='{doc.id}'")

    def test_03_db2_config_resolution(self):
        """Verify unified Db2 configuration generation."""
        cfg = get_db2_config()
        self.assertIn("connection_string", cfg)
        self.assertIn("table_name", cfg)
        self.assertTrue(cfg["connection_string"].startswith("DATABASE="))
        print(f" Db2 unified config generated: {cfg['connection_string']}")


if __name__ == "__main__":
    unittest.main()
