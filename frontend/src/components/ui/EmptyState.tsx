import React from 'react';
import { Database, Upload } from 'lucide-react';

interface EmptyStateProps {
    icon?: React.ReactNode;
    title: string;
    description: string;
    action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ icon, title, description, action }) => (
    <div className="flex flex-col items-center justify-center py-16 px-8 text-center animate-fade-in">
        <div className="mb-6 p-4 rounded-2xl bg-elevated border border-border">
            {icon || <Database className="h-10 w-10 text-text-muted" />}
        </div>
        <h3 className="text-xl font-semibold text-text-primary mb-2">{title}</h3>
        <p className="text-text-secondary max-w-md mb-6">{description}</p>
        {action}
    </div>
);
