/**
 * API client for the Metals, Explained backend
 * Uses Next.js API routes (relative paths) for seamless deployment.
 */

export interface VolMetric {
    value: number;
    change: number;
    type: string;
}

export interface SnapshotResponse {
    asOf: string;
    mode: 'live' | 'demo' | 'partial';
    feeds: Record<string, 'live' | 'demo'>;
    gold: { price: number; pctChange: number };
    silver: { price: number; pctChange: number };
    us10y: { yield: number; bpsChange: number };
    dxy: { value: number; pctChange: number };
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
    const res = await fetch('/api/health');
    return res.json();
}

export async function getSnapshot(): Promise<SnapshotResponse> {
    const res = await fetch('/api/market/snapshot', { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch snapshot');
    return res.json();
}

export async function getTimeseries(
    asset: 'gold' | 'silver' | 'us10y' | 'dxy' | 'vol_gold' | 'vol_silver',
    window: '1D' | '5D' | '1M' | '3M' | '6M' | '1Y' = '1M'
): Promise<TimeseriesResponse> {
    const res = await fetch(
        `/api/market/timeseries?asset=${asset}&window=${window}`,
        { cache: 'no-store' }
    );
    if (!res.ok) throw new Error('Failed to fetch timeseries');
    return res.json();
}

export async function getExplanation(
    asset: string = 'gold',
    snapshot: SnapshotResponse
): Promise<ExplainResponse> {
    const res = await fetch('/api/market/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selectedAsset: asset, snapshot }),
        cache: 'no-store',
    });
    if (!res.ok) throw new Error('Failed to fetch explanation');
    return res.json();
}

export async function refreshData(): Promise<{ status: string }> {
    // For Next.js API routes, refresh just means refetching
    return { status: 'ready' };
}
