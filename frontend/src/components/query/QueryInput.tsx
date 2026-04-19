import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles } from 'lucide-react';

interface QueryInputProps {
    onSubmit: (question: string) => void;
    isLoading: boolean;
    columns?: string[];
}

const SUGGESTED_QUERIES = [
    'Show total revenue by region',
    'Why did South underperform in February?',
    'Compare Q1 vs Q2 revenue',
    'Break down costs by product',
    'Give me a monthly summary',
];

export const QueryInput: React.FC<QueryInputProps> = ({ onSubmit, isLoading, columns }) => {
    const [question, setQuestion] = useState('');
    const inputRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        if (!isLoading && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isLoading]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (question.trim() && !isLoading) {
            onSubmit(question.trim());
            setQuestion('');
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    const handleSuggestionClick = (suggestion: string) => {
        if (!isLoading) {
            onSubmit(suggestion);
        }
    };

    return (
        <div className="space-y-3">
            <form onSubmit={handleSubmit} className="relative">
                <div className="relative flex items-end bg-elevated border border-border rounded-xl focus-within:border-accent-amber focus-within:ring-1 focus-within:ring-accent-amber/30 transition-all duration-200">
                    <textarea
                        ref={inputRef}
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask a question about your data..."
                        disabled={isLoading}
                        rows={1}
                        className="flex-1 bg-transparent text-text-primary placeholder-text-muted px-4 py-3.5 resize-none focus:outline-none text-sm"
                        style={{ minHeight: '48px', maxHeight: '120px' }}
                    />
                    <button
                        type="submit"
                        disabled={!question.trim() || isLoading}
                        className="m-2 p-2.5 rounded-lg bg-accent-amber text-base hover:bg-amber-500 disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-200"
                    >
                        <Send className="h-4 w-4" />
                    </button>
                </div>
            </form>

            {!isLoading && (
                <div className="flex flex-wrap gap-2">
                    <Sparkles className="h-3.5 w-3.5 text-accent-purple mt-1" />
                    {SUGGESTED_QUERIES.slice(0, 3).map((suggestion) => (
                        <button
                            key={suggestion}
                            onClick={() => handleSuggestionClick(suggestion)}
                            className="px-3 py-1.5 text-xs bg-elevated border border-border rounded-full text-text-secondary hover:text-text-primary hover:border-border-active transition-colors"
                        >
                            {suggestion}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
};
