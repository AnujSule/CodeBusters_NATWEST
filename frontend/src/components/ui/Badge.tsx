import React from 'react';

type BadgeVariant = 'amber' | 'green' | 'red' | 'blue' | 'purple' | 'default';

interface BadgeProps {
    variant?: BadgeVariant;
    children: React.ReactNode;
    className?: string;
}

const variantStyles: Record<BadgeVariant, string> = {
    amber: 'bg-accent-amber/15 text-accent-amber border border-accent-amber/25',
    green: 'bg-accent-green/15 text-accent-green border border-accent-green/25',
    red: 'bg-accent-red/15 text-accent-red border border-accent-red/25',
    blue: 'bg-accent-blue/15 text-accent-blue border border-accent-blue/25',
    purple: 'bg-accent-purple/15 text-accent-purple border border-accent-purple/25',
    default: 'bg-elevated text-text-secondary border border-border',
};

export const Badge: React.FC<BadgeProps> = ({ variant = 'default', children, className = '' }) => (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium uppercase tracking-wider ${variantStyles[variant]} ${className}`}>
        {children}
    </span>
);

/** Map dataset/query status to badge variant. */
export const statusVariant = (status: string): BadgeVariant => {
    switch (status) {
        case 'ready': return 'green';
        case 'processing': return 'blue';
        case 'pending': return 'amber';
        case 'failed': return 'red';
        default: return 'default';
    }
};
