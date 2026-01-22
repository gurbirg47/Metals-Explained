/**
 * API client for the Metals, Explained backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export interface FeedStatus {
    isLive: boolean;
}

export interface SnapshotResponse {
    asOf: string;
    mode: 'live' | 'demo' | 'partial';
    feeds: {
        gold: FeedStatus;
        silver: FeedStatus;
        us10y: FeedStatus;
        dxy: FeedStatus;
    };
    gold: { price: number | null; pctChange: number | null };
    silver: { price: number | null; pctChange: number | null };
    us10y: { yield: number | null; bpsChange: number | null };
    dxy: { value: number | null; pctChange: number | null };
    vol: { value: number | null; label: string };
    drivers: {
        primary: string;
        secondary: string;
        volLevel: string;
    };
}

export interface TimeseriesPoint {
    t: string;
    c: number | null;
    o?: number | null;
    h?: number | null;
    l?: number | null;
}

export interface TimeseriesResponse {
    asOf: string;
    asset: string;
    window: string;
    hasOHLC: boolean;
    isMock: boolean;
    series: TimeseriesPoint[];
}

export interface ExplainSections {
    whatMoved: string;
    drivers: string;
    conflictCheck: string;
    chartBullets: string[];
    plainTakeaway: string;
}

export interface ExplainResponse {
    asOf: string;
    sections: ExplainSections;
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
