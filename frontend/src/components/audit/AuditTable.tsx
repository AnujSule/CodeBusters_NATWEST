import React from 'react';
import { Clock, Code, ArrowUpDown, Search } from 'lucide-react';
import { Badge } from '../ui/Badge';
import type { AuditLogEntry } from '../../types/api';

interface AuditTableProps {
    entries: AuditLogEntry[];
    total: number;
    page: number;
    pageSize: number;
    onPageChange: (page: number) => void;
}

export const AuditTable: React.FC<AuditTableProps> = ({
    entries, total, page, pageSize, onPageChange,
}) => {
    const totalPages = Math.ceil(total / pageSize);

    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) +
            ' ' + date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
    };

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
        <div className="space-y-4">
            <div className="overflow-x-auto rounded-xl border border-border">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="bg-elevated text-text-secondary text-xs uppercase tracking-wider">
                            <th className="text-left px-4 py-3 font-medium">Timestamp</th>
                            <th className="text-left px-4 py-3 font-medium">Dataset</th>
                            <th className="text-left px-4 py-3 font-medium">Question</th>
                            <th className="text-left px-4 py-3 font-medium">Intent</th>
                            <th className="text-left px-4 py-3 font-medium">Model</th>
                            <th className="text-right px-4 py-3 font-medium">Tokens</th>
                            <th className="text-right px-4 py-3 font-medium">Latency</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                        {entries.map((entry) => (
                            <tr key={entry.id} className="hover:bg-elevated/50 transition-colors">
                                <td className="px-4 py-3 text-text-muted font-mono text-xs whitespace-nowrap">
                                    {formatDate(entry.created_at)}
                                </td>
                                <td className="px-4 py-3 text-text-primary text-xs">
                                    {entry.dataset_name || 'Unknown'}
                                </td>
                                <td className="px-4 py-3 text-text-primary max-w-xs truncate">
                                    {entry.question}
                                </td>
                                <td className="px-4 py-3">
                                    <Badge variant={intentColor(entry.intent)}>{entry.intent}</Badge>
                                </td>
                                <td className="px-4 py-3 text-text-muted font-mono text-xs">
                                    {entry.model_used.split('/').pop()}
                                </td>
                                <td className="px-4 py-3 text-text-muted text-right font-mono text-xs">
                                    {entry.tokens_used.toLocaleString()}
                                </td>
                                <td className="px-4 py-3 text-text-muted text-right font-mono text-xs">
                                    {entry.latency_ms}ms
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {totalPages > 1 && (
                <div className="flex items-center justify-between">
                    <span className="text-sm text-text-muted">
                        Showing {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, total)} of {total}
                    </span>
                    <div className="flex gap-2">
                        <button
                            onClick={() => onPageChange(page - 1)}
                            disabled={page <= 1}
                            className="px-3 py-1.5 text-sm bg-elevated border border-border rounded-lg disabled:opacity-30 hover:bg-surface transition-colors"
                        >
                            Previous
                        </button>
                        <button
                            onClick={() => onPageChange(page + 1)}
                            disabled={page >= totalPages}
                            className="px-3 py-1.5 text-sm bg-elevated border border-border rounded-lg disabled:opacity-30 hover:bg-surface transition-colors"
                        >
                            Next
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};
