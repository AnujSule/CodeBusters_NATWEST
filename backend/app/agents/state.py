"""LangGraph AgentState TypedDict defining the shared state for the multi-agent pipeline.

This state is passed through all nodes in the agent graph. Each node reads what it needs
and writes its outputs back to the state.
"""

from typing import TypedDict, Optional, List, Any


class AgentState(TypedDict):
    """Shared state for the multi-agent data analysis pipeline.

    This TypedDict defines all fields that flow through the LangGraph StateGraph.
    Fields are populated progressively as each agent node executes.
    """

    # ── Input (set before graph invocation) ────────────────────
    question: str              # Original user question
    dataset_id: str            # UUID of the dataset being queried
    user_id: str               # UUID of the authenticated user

    # ── Dataset Context (set before graph invocation) ──────────
    schema_info: dict          # Column names, types, sample rows
    file_type: str             # "csv" or "pdf"
    duckdb_table_name: str     # Virtual table name in DuckDB

    # ── Intent Classifier Output ──────────────────────────────
    intent: str                # compare | decompose | summarise | explain
    intent_confidence: float   # 0.0 - 1.0
    entities: list             # Extracted entities (regions, products, etc.)
    time_range: dict           # Resolved time range {"start": ..., "end": ...}
    metrics: list              # Canonical metric names referenced

    # ── SQL Agent Output ──────────────────────────────────────
    sql_query: Optional[str]   # Generated SQL query
    sql_result: Optional[list] # Rows returned from DuckDB execution
    sql_error: Optional[str]   # Error message if SQL execution failed

    # ── RAG Agent Output ──────────────────────────────────────
    rag_chunks: Optional[list] # Retrieved document chunks from pgvector
    metric_definitions: Optional[dict]  # Resolved metric term definitions

    # ── Verifier Agent Output ─────────────────────────────────
    verification_passed: bool  # Whether the verification check passed
    verification_notes: str    # Notes from the verifier
    corrected_sql: Optional[str]  # Corrected SQL if verifier found issues

    # ── Synthesiser Agent Output ──────────────────────────────
    answer_narrative: str      # Plain-English answer for the user
    key_metric: Optional[str]  # One-line key metric summary
    chart_spec: Optional[dict] # Recharts-compatible chart configuration
    sources: list              # Citations [{file, columns, rows, confidence}]

    # ── Metadata ──────────────────────────────────────────────
    tokens_used: int           # Total tokens consumed across all agents
    latency_ms: int            # Total processing time in milliseconds
    error: Optional[str]       # Global error message if pipeline fails
