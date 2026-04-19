"""Tests for intent classifier agent."""

import pytest
from app.agents.state import AgentState


@pytest.fixture
def sample_state() -> AgentState:
    """Create a sample agent state for testing."""
    return {
        "question": "Why did revenue drop in February?",
        "dataset_id": "test-dataset-id",
        "user_id": "test-user-id",
        "schema_info": {
            "columns": ["date", "region", "product", "revenue", "transactions"],
            "column_types": {
                "date": "DATE",
                "region": "VARCHAR",
                "product": "VARCHAR",
                "revenue": "INTEGER",
                "transactions": "INTEGER",
            },
            "row_count": 200,
            "sample_rows": [
                {"date": "2024-01-01", "region": "North", "product": "Current Account", "revenue": 125000, "transactions": 4200},
            ],
        },
        "file_type": "csv",
        "duckdb_table_name": "sales_data",
        "intent": "",
        "intent_confidence": 0.0,
        "entities": [],
        "time_range": {},
        "metrics": [],
        "sql_query": None,
        "sql_result": None,
        "sql_error": None,
        "rag_chunks": None,
        "metric_definitions": None,
        "verification_passed": False,
        "verification_notes": "",
        "corrected_sql": None,
        "answer_narrative": "",
        "key_metric": None,
        "chart_spec": None,
        "sources": [],
        "tokens_used": 0,
        "latency_ms": 0,
        "error": None,
    }


def test_agent_state_schema():
    """Test that AgentState TypedDict has all required fields."""
    required_fields = [
        "question", "dataset_id", "user_id",
        "schema_info", "file_type", "duckdb_table_name",
        "intent", "intent_confidence",
        "sql_query", "sql_result", "sql_error",
        "answer_narrative", "chart_spec", "sources",
        "tokens_used", "latency_ms", "error",
    ]
    annotations = AgentState.__annotations__
    for field in required_fields:
        assert field in annotations, f"AgentState missing field: {field}"


def test_sample_state_valid(sample_state):
    """Test that sample state has valid values."""
    assert sample_state["question"] == "Why did revenue drop in February?"
    assert sample_state["file_type"] == "csv"
    assert len(sample_state["schema_info"]["columns"]) == 5
    assert sample_state["schema_info"]["row_count"] == 200
