"""Db2-free test: the clearance filter becomes a SQL WHERE fragment (so it runs inside Db2, not in Python)."""
from haystack_integrations.document_stores.ibm_db.filters import FilterTranslator

ROLES = {
    "public user": ["public"],
    "internal user": ["public", "internal"],
    "restricted user": ["public", "internal", "restricted"],
}


def test_clearance_filter_is_sql_in():
    for levels in ROLES.values():
        params = []
        sql = FilterTranslator().translate({"field": "meta.clearance", "operator": "in", "value": levels}, params)
        assert "JSON_VALUE" in sql and " IN (" in sql
        assert params == levels


def test_dataset_has_all_clearances():
    import json, pathlib
    rows = [json.loads(l) for l in open(pathlib.Path(__file__).parent.parent / "src/data/documents.jsonl")]
    assert {r["meta"]["clearance"] for r in rows} == {"public", "internal", "restricted"}
    assert len(rows) == 30
