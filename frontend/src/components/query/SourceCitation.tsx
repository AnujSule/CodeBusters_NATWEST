import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Database, Code } from 'lucide-react';
import type { SourceCitation as SourceCitationType } from '../../types/api';

interface SourceCitationProps {
    sources: SourceCitationType[];
    sqlExecuted: string | null;
}

export const SourceCitation: React.FC<SourceCitationProps> = ({ sources, sqlExecuted }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [showSql, setShowSql] = useState(false);

    if (!sources.length && !sqlExecuted) return null;

    return (
        <div className="border border-border rounded-lg overflow-hidden animate-fade-in">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex items-center justify-between px-4 py-2.5 bg-elevated/50 hover:bg-elevated transition-colors"
            >
                <div className="flex items-center gap-2 text-sm">
                    <Database className="h-3.5 w-3.5 text-accent-amber" />
                    <span className="text-text-secondary font-medium">Sources & Transparency</span>
                    {sources[0] && (
                        <span className="text-text-muted">
                            · {sources[0].file} · {sources[0].rows_used} rows used
                        </span>
                    )}
                </div>
                {isExpanded ? (
                    <ChevronUp className="h-4 w-4 text-text-muted" />
                ) : (
                    <ChevronDown className="h-4 w-4 text-text-muted" />
                )}
            </button>

            {isExpanded && (
                <div className="px-4 py-3 space-y-3 border-t border-border bg-surface/50">
                    {sources.map((source, index) => (
                        <div key={index} className="flex flex-wrap gap-x-6 gap-y-1 text-xs">
                            <span className="text-text-secondary">
                                <strong className="text-text-primary">Source:</strong> {source.file}
                            </span>
                            {source.columns && (
                                <span className="text-text-secondary">
                                    <strong className="text-text-primary">Columns:</strong>{' '}
                                    {source.columns.join(', ')}
                                </span>
                            )}
                            <span className="text-text-secondary">
                                <strong className="text-text-primary">Rows:</strong>{' '}
                                {source.rows_used} of {source.total_rows}
                            </span>
                            {source.confidence && (
                                <span className="text-text-secondary">
                                    <strong className="text-text-primary">Confidence:</strong>{' '}
                                    {(source.confidence * 100).toFixed(0)}%
                                </span>
                            )}
                        </div>
                    ))}

                    {sqlExecuted && (
                        <div>
                            <button
                                onClick={() => setShowSql(!showSql)}
                                className="flex items-center gap-1.5 text-xs text-accent-blue hover:text-blue-400 transition-colors"
                            >
                                <Code className="h-3 w-3" />
                                {showSql ? 'Hide SQL' : 'Show SQL'}
                            </button>
                            {showSql && (
                                <pre className="mt-2 p-3 bg-base rounded-lg text-xs font-mono text-text-secondary overflow-x-auto border border-border">
                                    {sqlExecuted}
                                </pre>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
