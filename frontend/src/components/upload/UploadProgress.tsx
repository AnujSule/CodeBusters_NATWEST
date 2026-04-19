import React from 'react';
import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

interface UploadProgressProps {
    status: 'uploading' | 'processing' | 'ready' | 'failed';
    progress?: number;
    error?: string;
}

export const UploadProgress: React.FC<UploadProgressProps> = ({ status, progress = 0, error }) => {
    const statusConfig = {
        uploading: { icon: Loader2, color: 'text-accent-amber', bg: 'bg-accent-amber', label: 'Uploading...' },
        processing: { icon: Loader2, color: 'text-accent-blue', bg: 'bg-accent-blue', label: 'Processing dataset...' },
        ready: { icon: CheckCircle, color: 'text-accent-green', bg: 'bg-accent-green', label: 'Ready to query!' },
        failed: { icon: AlertCircle, color: 'text-accent-red', bg: 'bg-accent-red', label: 'Processing failed' },
    };

    const config = statusConfig[status];
    const Icon = config.icon;
    const isAnimating = status === 'uploading' || status === 'processing';

    return (
        <div className="mt-4 p-4 rounded-lg bg-elevated border border-border animate-fade-in">
            <div className="flex items-center gap-3 mb-3">
                <Icon className={`h-5 w-5 ${config.color} ${isAnimating ? 'animate-spin' : ''}`} />
                <span className={`text-sm font-medium ${config.color}`}>{config.label}</span>
            </div>

            {(status === 'uploading' || status === 'processing') && (
                <div className="w-full h-1.5 bg-surface rounded-full overflow-hidden">
                    <div
                        className={`h-full ${config.bg} rounded-full transition-all duration-300 ${status === 'processing' ? 'animate-pulse-slow w-full' : ''
                            }`}
                        style={status === 'uploading' ? { width: `${progress}%` } : undefined}
                    />
                </div>
            )}

            {error && (
                <p className="text-sm text-accent-red mt-2">{error}</p>
            )}
        </div>
    );
};
