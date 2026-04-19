/** API response types matching the backend Pydantic schemas. */

export interface UserResponse {
    id: string;
    email: string;
    full_name: string;
}

export interface TokenResponse {
    access_token: string;
    refresh_token?: string;
    token_type: string;
    user_id?: string;
}

export interface DatasetResponse {
    id: string;
    dataset_id?: string;
    user_id?: string;
    name: string;
    description?: string | null;
    file_type: string;
    file_size_bytes: number;
    status: 'pending' | 'processing' | 'ready' | 'failed';
    row_count: number | null;
    column_names: string[] | null;
    schema_info?: Record<string, unknown> | null;
    created_at?: string;
    updated_at?: string;
    error?: string | null;
}

export interface DatasetListResponse {
    datasets: DatasetResponse[];
    total: number;
}

export interface SourceCitation {
    file: string;
    columns_used?: string[] | null;
    rows_returned?: number | null;
    sql?: string | null;
}

export interface ChartSpec {
    type: 'bar' | 'line' | 'pie' | 'area';
    title: string;
    x_key: string;
    y_key: string;
    color_key?: string | null;
    data: Record<string, unknown>[];
}

export interface QueryResponse {
    query_id: string;
    intent: string;
    answer: string;
    key_metric?: string | null;
    chart_spec?: ChartSpec | null;
    sources?: SourceCitation[];
    sql_executed?: string | null;
    latency_ms?: number;
    model_used?: string;
    created_at?: string;
    error?: string | null;
}

export interface QueryHistoryResponse {
    queries: QueryResponse[];
    total: number;
}

export interface AuditLogEntry {
    query_id: string;
    dataset_id: string;
    question: string;
    intent?: string;
    sql_executed?: string | null;
    model_used?: string;
    tokens_used?: number;
    latency_ms?: number;
    error?: string | null;
    created_at?: string;
}

export interface AuditLogResponse {
    entries: AuditLogEntry[];
    total: number;
    page: number;
    page_size: number;
}

export interface ApiError {
    detail: string;
    status_code?: number;
}
