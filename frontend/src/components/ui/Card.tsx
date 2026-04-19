import React from 'react';

interface CardProps {
    children: React.ReactNode;
    className?: string;
    hover?: boolean;
}

export const Card: React.FC<CardProps> = ({ children, className = '', hover = true }) => (
    <div className={`bg-surface border border-border rounded-xl p-6 ${hover ? 'hover:border-border-active transition-colors duration-200' : ''} ${className}`}>
        {children}
    </div>
);

interface CardHeaderProps {
    children: React.ReactNode;
    className?: string;
}

export const CardHeader: React.FC<CardHeaderProps> = ({ children, className = '' }) => (
    <div className={`mb-4 ${className}`}>{children}</div>
);

interface CardTitleProps {
    children: React.ReactNode;
    className?: string;
}

export const CardTitle: React.FC<CardTitleProps> = ({ children, className = '' }) => (
    <h3 className={`text-lg font-semibold text-text-primary ${className}`}>{children}</h3>
);

interface CardContentProps {
    children: React.ReactNode;
    className?: string;
}

export const CardContent: React.FC<CardContentProps> = ({ children, className = '' }) => (
    <div className={className}>{children}</div>
);
