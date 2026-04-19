import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface AnswerCardProps {
    narrative: string;
    keyMetric: string | null;
}

export const AnswerCard: React.FC<AnswerCardProps> = ({ narrative, keyMetric }) => (
    <div className="space-y-3 animate-slide-up">
        {keyMetric && (
            <div className="text-xl font-bold gradient-text leading-tight">
                {keyMetric}
            </div>
        )}
        <div className="prose prose-invert prose-sm max-w-none text-text-secondary leading-relaxed">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{narrative}</ReactMarkdown>
        </div>
    </div>
);
