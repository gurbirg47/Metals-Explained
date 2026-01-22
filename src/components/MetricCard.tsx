'use client';

interface MetricCardProps {
    label: string;
    value: string;
    delta?: string;
    deltaType?: 'up' | 'down' | 'neutral';
}

export default function MetricCard({ label, value, delta, deltaType = 'neutral' }: MetricCardProps) {
    return (
        <div className="metric-card">
            <div className="metric-label">{label}</div>
            <div className="metric-value">{value}</div>
            {delta && (
                <div className={`metric-delta ${deltaType}`}>
                    {delta}
                </div>
            )}
        </div>
    );
}
