import React, { useRef, useEffect } from 'react';
import { FileSpreadsheet, FileText, Rows3, Columns3, HardDrive } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Badge, statusVariant } from '../components/ui/Badge';
import { TypingIndicator } from '../components/ui/Spinner';
import { QueryInput } from '../components/query/QueryInput';
import { QueryResult } from '../components/query/QueryResult';
import { QueryHistory } from '../components/query/QueryHistory';
import { useDatasetStore } from '../store/datasetStore';
import { useSubmitQuery } from '../hooks/useQuery';
import type { QueryResponse } from '../types/api';

const DatasetPage: React.FC = () => {
    const { selectedDataset, queryHistory } = useDatasetStore();
    const submitQuery = useSubmitQuery();
    const resultsEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (queryHistory.length > 0) {
            resultsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [queryHistory.length]);

    if (!selectedDataset) return null;

    const handleQuery = (question: string) => {
        submitQuery.mutate({ datasetId: selectedDataset.id, question });
    };

    const handleHistorySelect = (_query: QueryResponse) => {
        // Could scroll to or highlight the selected query
    };

    const formatSize = (bytes: number): string => {
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
    };

    const isCSV = selectedDataset.file_type === 'csv';
    const isReady = selectedDataset.status === 'ready';

    return (
        <div className="flex w-full h-full">
            {/* Main content */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Dataset info bar */}
                <div className="px-6 py-4 border-b border-border bg-surface/50">
                    <div className="flex items-center gap-4">
                        <div className="p-2 rounded-lg bg-elevated">
                            {isCSV ? (
                                <FileSpreadsheet className="h-5 w-5 text-accent-green" />
                            ) : (
                                <FileText className="h-5 w-5 text-accent-blue" />
                            )}
                        </div>
                        <div className="flex-1">
                            <h2 className="text-lg font-semibold text-text-primary">{selectedDataset.name}</h2>
                            <div className="flex items-center gap-4 mt-1">
                                <Badge variant={statusVariant(selectedDataset.status)}>
                                    {selectedDataset.status}
                                </Badge>
                                {selectedDataset.row_count && (
                                    <span className="flex items-center gap-1 text-xs text-text-muted">
                                        <Rows3 className="h-3 w-3" />
                                        {selectedDataset.row_count.toLocaleString()} rows
                                    </span>
                                )}
                                {selectedDataset.column_names && (
                                    <span className="flex items-center gap-1 text-xs text-text-muted">
                                        <Columns3 className="h-3 w-3" />
                                        {selectedDataset.column_names.length} columns
                                    </span>
                                )}
                                <span className="flex items-center gap-1 text-xs text-text-muted">
                                    <HardDrive className="h-3 w-3" />
                                    {formatSize(selectedDataset.file_size_bytes)}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Query results feed */}
                <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
                    {queryHistory.slice().reverse().map((result) => (
                        <QueryResult key={result.query_id} result={result} />
                    ))}

                    {submitQuery.isPending && (
                        <div className="card">
                            <TypingIndicator />
                        </div>
                    )}

                    <div ref={resultsEndRef} />
                </div>

                {/* Query input (pinned to bottom) */}
                <div className="px-6 py-4 border-t border-border bg-surface/80 backdrop-blur-sm">
                    <QueryInput
                        onSubmit={handleQuery}
                        isLoading={submitQuery.isPending}
                        columns={selectedDataset.column_names || undefined}
                    />
                </div>
            </div>

            {/* Query history sidebar */}
            <div className="w-64 border-l border-border bg-surface/50 overflow-y-auto hidden xl:block">
                <QueryHistory queries={queryHistory} onSelect={handleHistorySelect} />
            </div>
        </div>
    );
};

export default DatasetPage;
