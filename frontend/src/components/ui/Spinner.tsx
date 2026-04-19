import React from 'react';

interface SpinnerProps {
    size?: 'sm' | 'md' | 'lg';
    className?: string;
}

const sizeMap = { sm: 'h-4 w-4', md: 'h-8 w-8', lg: 'h-12 w-12' };

export const Spinner: React.FC<SpinnerProps> = ({ size = 'md', className = '' }) => (
    <div className={`flex items-center justify-center ${className}`}>
        <svg className={`animate-spin ${sizeMap[size]} text-accent-amber`} fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
    </div>
);

export const TypingIndicator: React.FC = () => (
    <div className="flex items-center gap-1.5 py-2">
        <div className="typing-dot h-2 w-2 rounded-full bg-accent-amber" />
        <div className="typing-dot h-2 w-2 rounded-full bg-accent-amber" />
        <div className="typing-dot h-2 w-2 rounded-full bg-accent-amber" />
        <span className="ml-2 text-sm text-text-secondary">Analysing your data...</span>
    </div>
);
