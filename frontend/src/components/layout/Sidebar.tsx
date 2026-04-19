import React from 'react';
import { FileText, FileSpreadsheet, Plus, RefreshCw } from 'lucide-react';
import { useDatasetStore } from '../../store/datasetStore';
import { Badge, statusVariant } from '../ui/Badge';
import type { DatasetResponse } from '../../types/api';

interface SidebarProps {
    onUploadClick: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onUploadClick }) => {
    const { datasets, selectedDataset, selectDataset } = useDatasetStore();

    const formatSize = (bytes: number): string => {
        if (bytes < 1024) return `${bytes}B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
    };

    const FileIcon: React.FC<{ type: string }> = ({ type }) =>
        type === 'csv' ? (
            <FileSpreadsheet className="h-4 w-4 text-accent-green" />
        ) : (
            <FileText className="h-4 w-4 text-accent-blue" />
        );

    return (
        <aside className="w-72 bg-surface border-r border-border flex flex-col h-full">
            <div className="p-4 border-b border-border">
                <button
                    onClick={onUploadClick}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-accent-amber/10 text-accent-amber border border-accent-amber/25 rounded-lg hover:bg-accent-amber/20 transition-colors text-sm font-medium"
                >
                    <Plus className="h-4 w-4" />
                    Upload Dataset
                </button>
            </div>

            <div className="flex-1 overflow-y-auto p-2">
                <div className="px-2 py-2 text-xs font-medium text-text-muted uppercase tracking-wider">
                    Datasets ({datasets.length})
                </div>

                {datasets.map((dataset: DatasetResponse) => (
                    <button
                        key={dataset.id}
                        onClick={() => selectDataset(dataset)}
                        className={`w-full text-left px-3 py-3 rounded-lg mb-1 transition-all duration-150 group ${selectedDataset?.id === dataset.id
                                ? 'bg-elevated border border-border-active'
                                : 'hover:bg-elevated border border-transparent'
                            }`}
                    >
                        <div className="flex items-center gap-2.5">
                            <FileIcon type={dataset.file_type} />
                            <div className="flex-1 min-w-0">
                                <div className="text-sm font-medium text-text-primary truncate">
                                    {dataset.name}
                                </div>
                                <div className="flex items-center gap-2 mt-1">
                                    <Badge variant={statusVariant(dataset.status)}>
                                        {dataset.status}
                                    </Badge>
                                    <span className="text-xs text-text-muted">
                                        {formatSize(dataset.file_size_bytes)}
                                    </span>
                                </div>
                            </div>
                            {dataset.status === 'processing' && (
                                <RefreshCw className="h-3.5 w-3.5 text-accent-blue animate-spin" />
                            )}
                        </div>
                    </button>
                ))}
            </div>
        </aside>
    );
};
