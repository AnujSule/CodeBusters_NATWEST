/** Chart specification types for Recharts rendering. */

export type ChartType = 'bar' | 'line' | 'pie' | 'area';

export interface ChartConfig {
    type: ChartType;
    title: string;
    xKey: string;
    yKey: string;
    colorKey: string | null;
    data: Record<string, unknown>[];
}

export const CHART_COLORS = {
    primary: '#f59e0b',
    secondary: '#3b82f6',
    success: '#10b981',
    danger: '#ef4444',
    purple: '#8b5cf6',
    grid: '#1e2d45',
    text: '#7c8fa8',
    background: '#111827',
} as const;

export const CHART_COLOR_PALETTE = [
    '#f59e0b',
    '#3b82f6',
    '#10b981',
    '#ef4444',
    '#8b5cf6',
    '#06b6d4',
    '#f97316',
    '#ec4899',
];
