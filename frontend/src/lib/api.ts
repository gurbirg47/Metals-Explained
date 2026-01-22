/**
 * API client for the Metals, Explained backend
 */

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ||
    (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
        ? 'http://localhost:8000'
        : '/api');

export interface VolMetric {
    value: number;
    change: number;
    type: string;
}

export interface SnapshotResponse {
    asOf: string;
    mode: 'live' | 'demo' | 'partial';
    feeds: Record<string, 'live' | 'demo'>;
    gold: { price: number | null; pctChange: number | null };
    silver: { price: number | null; pctChange: number | null };
    us10y: { yield: number | null; bpsChange: number | null };
    dxy: { value: number | null; pctChange: number | null };
    vol: {
        gold: VolMetric;
        silver: VolMetric;
    };
}

export interface TimeseriesPoint {
    t: string;
    value?: number | null;
    open?: number | null;
    high?: number | null;
    low?: number | null;
    close?: number | null;
}

export interface TimeseriesResponse {
    asOf: string;
    asset: string;
    window: string;
    supportsCandles: boolean;
    series: TimeseriesPoint[];
}

export interface ExplainSections {
    whatMoved: string;
    mostLikelyDriver: string;
    chartEvidence: string[];
    plainTakeaway: string;
}

export interface ExplainResponse {
    asOf: string;
    selectedAsset: string;
    sections: ExplainSections;
    disclaimer: string;
}

export async function getHealth(): Promise<{ status: string }> {
    const res = await fetch(`${API_BASE}/health`);
    return res.json();
}

export async function getSnapshot(): Promise<SnapshotResponse> {
    const res = await fetch(`${API_BASE}/market/snapshot`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch snapshot');
    return res.json();
}

export async function getTimeseries(
    asset: 'gold' | 'silver' | 'us10y' | 'dxy' | 'vol' | 'gold_vol' | 'silver_vol',
    window: '1D' | '5D' | '1M' | '3M' | '1Y' = '1M'
): Promise<TimeseriesResponse> {
    const res = await fetch(
        `${API_BASE}/market/timeseries?asset=${asset}&window=${window}`,
        { cache: 'no-store' }
    );
    if (!res.ok) throw new Error('Failed to fetch timeseries');
    return res.json();
}

export async function getExplanation(window: string = '1D'): Promise<ExplainResponse> {
    const res = await fetch(`${API_BASE}/market/explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ window }),
        cache: 'no-store',
    });
    if (!res.ok) throw new Error('Failed to fetch explanation');
    return res.json();
}

export async function refreshData(): Promise<{ status: string; asOf: string }> {
    const res = await fetch(`${API_BASE}/market/refresh`, { method: 'POST' });
    return res.json();
}
