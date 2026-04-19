"""Tests for verifier agent."""

import pytest
from app.agents.graph import route_after_intent, route_after_verification


def test_route_csv_to_sql():
    """Test that CSV files route to SQL path."""
    state = {"file_type": "csv", "intent": "compare"}
    assert route_after_intent(state) == "generate_sql"


def test_route_pdf_to_rag():
    """Test that PDF files route to RAG path."""
    state = {"file_type": "pdf", "intent": "explain"}
    assert route_after_intent(state) == "retrieve_rag"


def test_route_default_to_sql():
    """Test that unknown file types default to SQL path."""
    state = {"file_type": "unknown", "intent": "summarise"}
    assert route_after_intent(state) == "generate_sql"


def test_route_verification_passed():
    """Test routing after verification passes."""
    state = {"verification_passed": True, "corrected_sql": None}
    assert route_after_verification(state) == "synthesise_response"


def test_route_verification_failed_with_correction():
    """Test routing after verification fails with corrected SQL."""
    state = {"verification_passed": False, "corrected_sql": "SELECT * FROM data LIMIT 10"}
    assert route_after_verification(state) == "execute_corrected_sql"


def test_route_verification_failed_no_correction():
    """Test routing after verification fails without corrected SQL."""
    state = {"verification_passed": False, "corrected_sql": None}
    assert route_after_verification(state) == "synthesise_response"
