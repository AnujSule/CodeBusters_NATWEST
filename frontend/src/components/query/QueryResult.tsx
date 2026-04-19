import React from 'react';
import { Badge } from '../ui/Badge';
import { AnswerCard } from './AnswerCard';
import { ChartRenderer } from './ChartRenderer';
import { SourceCitation } from './SourceCitation';
import { Clock, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';
import { toast } from 'sonner';
import type { QueryResponse } from '../../types/api';

interface QueryResultProps {
    result: QueryResponse;
}

const intentVariant = (intent: string) => {
    switch (intent) {
        case 'compare': return 'amber';
        case 'decompose': return 'blue';
        case 'summarise': return 'green';
        case 'explain': return 'purple';
        default: return 'default' as const;
    }
};

export const QueryResult: React.FC<QueryResultProps> = ({ result }) => {
    const handleCopy = () => {
        navigator.clipboard.writeText(result.answer);
        toast.success('Answer copied to clipboard');
    };

    return (
        <div className="card space-y-4 animate-slide-up">
            {/* Header: Intent badge + metadata */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Badge variant={intentVariant(result.intent)}>
                        {result.intent}
                    </Badge>
                    <span className="flex items-center gap-1 text-xs text-text-muted">
                        <Clock className="h-3 w-3" />
                        {result.latency_ms}ms
                    </span>
                </div>
                <div className="flex items-center gap-1">
                    <button
                        onClick={handleCopy}
                        className="p-1.5 rounded text-text-muted hover:text-text-primary hover:bg-elevated transition-colors"
                        title="Copy answer"
                    >
                        <Copy className="h-3.5 w-3.5" />
                    </button>
                    <button
                        className="p-1.5 rounded text-text-muted hover:text-accent-green hover:bg-elevated transition-colors"
                        title="Helpful"
                    >
                        <ThumbsUp className="h-3.5 w-3.5" />
                    </button>
                    <button
                        className="p-1.5 rounded text-text-muted hover:text-accent-red hover:bg-elevated transition-colors"
                        title="Not helpful"
                    >
                        <ThumbsDown className="h-3.5 w-3.5" />
                    </button>
                </div>
            </div>

            {/* Answer narrative */}
            <AnswerCard narrative={result.answer} keyMetric={result.key_metric} />

            {/* Chart */}
            {result.chart_spec && (
                <div className="pt-2 border-t border-border">
                    <ChartRenderer spec={result.chart_spec} />
                </div>
            )}

            {/* Source citation */}
            <SourceCitation sources={result.sources} sqlExecuted={result.sql_executed} />
        </div>
    );
};
