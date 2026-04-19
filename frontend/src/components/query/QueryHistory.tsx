import React from 'react';
import { MessageSquare, Clock } from 'lucide-react';
import { Badge } from '../ui/Badge';
import type { QueryResponse } from '../../types/api';

interface QueryHistoryProps {
    queries: QueryResponse[];
    onSelect: (query: QueryResponse) => void;
}

export const QueryHistory: React.FC<QueryHistoryProps> = ({ queries, onSelect }) => {
    if (queries.length === 0) {
        return (
            <div className="text-center py-8">
                <MessageSquare className="h-8 w-8 text-text-muted mx-auto mb-2" />
                <p className="text-sm text-text-muted">No queries yet</p>
            </div>
        );
    }

    const intentColor = (intent: string) => {
        switch (intent) {
            case 'compare': return 'amber';
            case 'decompose': return 'blue';
            case 'summarise': return 'green';
            case 'explain': return 'purple';
            default: return 'default' as const;
        }
    };

    return (
        <div className="space-y-1">
            <div className="px-2 py-2 text-xs font-medium text-text-muted uppercase tracking-wider">
                Recent Queries
            </div>
            {queries.map((query) => (
                <button
                    key={query.query_id}
                    onClick={() => onSelect(query)}
                    className="w-full text-left px-3 py-2.5 rounded-lg hover:bg-elevated transition-colors group"
                >
                    <div className="flex items-start gap-2">
                        <Badge variant={intentColor(query.intent)} className="mt-0.5 shrink-0">
                            {query.intent.slice(0, 3).toUpperCase()}
                        </Badge>
                        <div className="flex-1 min-w-0">
                            <p className="text-xs text-text-primary truncate group-hover:text-accent-amber transition-colors">
                                {query.key_metric || query.answer.slice(0, 60)}
                            </p>
                            <div className="flex items-center gap-2 mt-1">
                                <Clock className="h-3 w-3 text-text-muted" />
                                <span className="text-xs text-text-muted">{query.latency_ms}ms</span>
                            </div>
                        </div>
                    </div>
                </button>
            ))}
        </div>
    );
};
