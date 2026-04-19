import React from 'react';
import {
    BarChart, Bar, LineChart, Line, PieChart, Pie, AreaChart, Area,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Legend,
} from 'recharts';
import type { ChartSpec } from '../../types/api';
import { CHART_COLORS, CHART_COLOR_PALETTE } from '../../types/chart';

interface ChartRendererProps {
    spec: ChartSpec;
}

const CustomTooltip: React.FC<{ active?: boolean; payload?: any[]; label?: string }> = ({
    active, payload, label,
}) => {
    if (!active || !payload?.length) return null;
    return (
        <div className="bg-elevated border border-border rounded-lg px-3 py-2 shadow-xl">
            <p className="text-xs text-text-secondary mb-1">{label}</p>
            {payload.map((entry: any, i: number) => (
                <p key={i} className="text-sm font-mono font-medium" style={{ color: entry.color }}>
                    {entry.name}: {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}
                </p>
            ))}
        </div>
    );
};

export const ChartRenderer: React.FC<ChartRendererProps> = ({ spec }) => {
    const { type, title, x_key, y_key, data } = spec;

    if (!data || data.length === 0) return null;

    const commonProps = {
        data,
        margin: { top: 10, right: 30, left: 10, bottom: 5 },
    };

    const axisProps = {
        stroke: CHART_COLORS.text,
        fontSize: 11,
        fontFamily: "'JetBrains Mono', monospace",
        tickLine: false,
        axisLine: false,
    };

    return (
        <div className="animate-fade-in">
            <h4 className="text-sm font-medium text-text-secondary mb-3">{title}</h4>
            <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    {type === 'bar' ? (
                        <BarChart {...commonProps}>
                            <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />
                            <XAxis dataKey={x_key} {...axisProps} />
                            <YAxis {...axisProps} />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend wrapperStyle={{ fontSize: 12, color: CHART_COLORS.text }} />
                            <Bar dataKey={y_key} fill={CHART_COLORS.primary} radius={[4, 4, 0, 0]} />
                        </BarChart>
                    ) : type === 'line' ? (
                        <LineChart {...commonProps}>
                            <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />
                            <XAxis dataKey={x_key} {...axisProps} />
                            <YAxis {...axisProps} />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend wrapperStyle={{ fontSize: 12, color: CHART_COLORS.text }} />
                            <Line
                                type="monotone"
                                dataKey={y_key}
                                stroke={CHART_COLORS.primary}
                                strokeWidth={2}
                                dot={{ r: 4, fill: CHART_COLORS.primary }}
                                activeDot={{ r: 6, fill: CHART_COLORS.primary }}
                            />
                        </LineChart>
                    ) : type === 'area' ? (
                        <AreaChart {...commonProps}>
                            <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />
                            <XAxis dataKey={x_key} {...axisProps} />
                            <YAxis {...axisProps} />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend wrapperStyle={{ fontSize: 12, color: CHART_COLORS.text }} />
                            <Area
                                type="monotone"
                                dataKey={y_key}
                                stroke={CHART_COLORS.primary}
                                fill={CHART_COLORS.primary}
                                fillOpacity={0.15}
                                strokeWidth={2}
                            />
                        </AreaChart>
                    ) : (
                        <PieChart>
                            <Pie
                                data={data}
                                dataKey={y_key}
                                nameKey={x_key}
                                cx="50%"
                                cy="50%"
                                outerRadius={100}
                                innerRadius={40}
                                paddingAngle={2}
                                label={({ name, percent }: any) => `${name} ${(percent * 100).toFixed(0)}%`}
                                labelLine={false}
                            >
                                {data.map((_, index: number) => (
                                    <Cell key={index} fill={CHART_COLOR_PALETTE[index % CHART_COLOR_PALETTE.length]} />
                                ))}
                            </Pie>
                            <Tooltip content={<CustomTooltip />} />
                            <Legend wrapperStyle={{ fontSize: 12, color: CHART_COLORS.text }} />
                        </PieChart>
                    )}
                </ResponsiveContainer>
            </div>
        </div>
    );
};
