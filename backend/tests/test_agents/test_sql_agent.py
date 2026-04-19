"""Tests for SQL agent."""

import pytest
from app.services.csv_processor import sanitize_table_name


def test_sanitize_table_name_basic():
    """Test basic table name sanitization."""
    assert sanitize_table_name("sales_data.csv") == "sales_data"


def test_sanitize_table_name_spaces():
    """Test table name with spaces."""
    assert sanitize_table_name("my sales data.csv") == "my_sales_data"


def test_sanitize_table_name_special_chars():
    """Test table name with special characters."""
    assert sanitize_table_name("data-2024 (v2).csv") == "data_2024__v2_"


def test_sanitize_table_name_starts_with_number():
    """Test table name starting with a number."""
    assert sanitize_table_name("2024_sales.csv") == "t_2024_sales"


def test_sanitize_table_name_empty():
    """Test empty filename."""
    assert sanitize_table_name(".csv") == "dataset"
