/**
 * Market Data Utilities for Next.js API Routes
 * Provides data fetching, demo generation, and analysis functions.
 */

// ============ TYPES ============
export interface AssetConfig {
    symbol: string;
    basePrice: number;
    volBase?: number;
    type: 'price' | 'index' | 'yield';
}

export interface Metrics {
    latest: number;
    changePct: number;
    ma20?: number;
    ma50?: number;
    above50?: boolean;
}

export interface VolData {
    current: number;
    series: Array<{ t: string; value: number }>;
}

export interface AssetData {
    isLive: boolean;
    metrics: Metrics;
    vol: VolData;
    series: TimeseriesPoint[];
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
        gold: { value: number; change: number; type: string };
        silver: { value: number; change: number; type: string };
    };
}

export interface TimeseriesPoint {
    t: string;
    value?: number;
    open?: number;
    high?: number;
    low?: number;
    close?: number;
}

export interface TimeseriesResponse {
    asOf: string;
    asset: string;
    window: string;
    supportsCandles: boolean;
    series: TimeseriesPoint[];
}

// ============ CONFIGURATION ============
export const ASSETS: Record<string, AssetConfig> = {
    gold: { symbol: 'GC=F', basePrice: 2680.0, volBase: 14.5, type: 'price' },
    silver: { symbol: 'SI=F', basePrice: 30.50, volBase: 22.0, type: 'price' },
    dxy: { symbol: 'DX-Y.NYB', basePrice: 108.5, type: 'index' },
    us10y: { symbol: '^TNX', basePrice: 4.60, type: 'yield' },
};

// ============ SEEDED RANDOM ============
function seededRandom(seed: number): () => number {
    return function () {
        seed = (seed * 1103515245 + 12345) & 0x7fffffff;
        return seed / 0x7fffffff;
    };
}

function seededNormal(random: () => number): number {
    const u1 = random();
    const u2 = random();
    return Math.sqrt(-2 * Math.log(u1 || 0.0001)) * Math.cos(2 * Math.PI * u2);
}

// ============ DEMO DATA GENERATION ============
export function generateDemoSeries(
    assetKey: string,
    days: number = 60
): { series: TimeseriesPoint[]; metrics: Metrics; vol: VolData } {
    const config = ASSETS[assetKey] || ASSETS.gold;
    const basePrice = config.basePrice;
    const dailyVol = assetKey === 'silver' ? 0.015 : 0.01;

    // Use date-based seed for daily consistency
    const today = new Date();
    const seed = today.getFullYear() * 10000 + (today.getMonth() + 1) * 100 + today.getDate();
    const random = seededRandom(seed + assetKey.charCodeAt(0));

    const series: TimeseriesPoint[] = [];
    let price = basePrice;
    const prices: number[] = [];

    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);

        const ret = seededNormal(random) * dailyVol;
        price = price * Math.exp(ret);
        prices.push(price);

        const point: TimeseriesPoint = { t: date.toISOString() };

        if (config.type === 'price') {
            const open = price * (1 + seededNormal(random) * 0.002);
            const high = Math.max(open, price) * (1 + Math.abs(seededNormal(random) * 0.005));
            const low = Math.min(open, price) * (1 - Math.abs(seededNormal(random) * 0.005));
            point.open = parseFloat(open.toFixed(4));
            point.high = parseFloat(high.toFixed(4));
            point.low = parseFloat(low.toFixed(4));
            point.close = parseFloat(price.toFixed(4));
        } else {
            point.value = parseFloat(price.toFixed(4));
        }

        series.push(point);
    }

    // Calculate metrics
    const latest = prices[prices.length - 1];
    const prev = prices[prices.length - 2] || latest;
    const changePct = ((latest - prev) / prev) * 100;

    // Calculate MAs
    const ma20 = prices.length >= 20
        ? prices.slice(-20).reduce((a, b) => a + b, 0) / 20
        : undefined;
    const ma50 = prices.length >= 50
        ? prices.slice(-50).reduce((a, b) => a + b, 0) / 50
        : undefined;

    // Calculate volatility
    let volCurrent = config.volBase || 15;
    const volSeries: Array<{ t: string; value: number }> = [];

    if (assetKey === 'gold' || assetKey === 'silver') {
        const returns = prices.slice(1).map((p, i) => (p - prices[i]) / prices[i]);
        if (returns.length >= 20) {
            const recent = returns.slice(-20);
            const std = Math.sqrt(recent.reduce((sum, r) => sum + r * r, 0) / recent.length);
            volCurrent = std * Math.sqrt(252) * 100;
        }

        // Generate vol series
        for (let i = 0; i < Math.min(40, series.length); i++) {
            const volRandom = seededRandom(seed + 1000 + i);
            const vol = (config.volBase || 15) + seededNormal(volRandom) * 2;
            const date = new Date(today);
            date.setDate(date.getDate() - (40 - i - 1));
            volSeries.push({ t: date.toISOString(), value: parseFloat(Math.max(5, Math.min(45, vol)).toFixed(2)) });
        }
    }

    return {
        series,
        metrics: {
            latest: parseFloat(latest.toFixed(4)),
            changePct: parseFloat(changePct.toFixed(4)),
            ma20: ma20 ? parseFloat(ma20.toFixed(4)) : undefined,
            ma50: ma50 ? parseFloat(ma50.toFixed(4)) : undefined,
            above50: ma50 ? latest > ma50 : undefined,
        },
        vol: {
            current: parseFloat(volCurrent.toFixed(2)),
            series: volSeries,
        },
    };
}

// ============ EXTERNAL DATA FETCHING ============
export async function fetchYahooData(symbol: string, range: string = '3mo'): Promise<AssetData | null> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    try {
        const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}?range=${range}&interval=1d`;
        const res = await fetch(url, {
            signal: controller.signal,
            headers: { 'User-Agent': 'Mozilla/5.0' }
        });

        clearTimeout(timeout);

        if (!res.ok) return null;

        const data = await res.json();
        const result = data?.chart?.result?.[0];
        if (!result) return null;

        const timestamps = result.timestamp || [];
        const quote = result.indicators?.quote?.[0] || {};
        const adjClose = result.indicators?.adjclose?.[0]?.adjclose || quote.close || [];

        if (timestamps.length < 2) return null;

        const series: TimeseriesPoint[] = [];
        const closes: number[] = [];

        for (let i = 0; i < timestamps.length; i++) {
            const date = new Date(timestamps[i] * 1000);
            const close = adjClose[i] ?? quote.close?.[i];
            if (close == null || isNaN(close)) continue;

            closes.push(close);
            const point: TimeseriesPoint = { t: date.toISOString() };

            if (quote.open && quote.high && quote.low) {
                point.open = quote.open[i];
                point.high = quote.high[i];
                point.low = quote.low[i];
                point.close = close;
            } else {
                point.value = close;
            }

            series.push(point);
        }

        if (closes.length < 2) return null;

        const latest = closes[closes.length - 1];
        const prev = closes[closes.length - 2];
        const changePct = ((latest - prev) / prev) * 100;

        // Calculate volatility for metals
        let volCurrent = 15;
        const volSeries: Array<{ t: string; value: number }> = [];

        const returns = closes.slice(1).map((p, i) => (p - closes[i]) / closes[i]);
        if (returns.length >= 20) {
            const recent = returns.slice(-20);
            const std = Math.sqrt(recent.reduce((sum, r) => sum + r * r, 0) / recent.length);
            volCurrent = std * Math.sqrt(252) * 100;

            // Build vol series
            for (let i = 19; i < Math.min(returns.length, 60); i++) {
                const windowReturns = returns.slice(i - 19, i + 1);
                const windowStd = Math.sqrt(windowReturns.reduce((sum, r) => sum + r * r, 0) / windowReturns.length);
                const vol = windowStd * Math.sqrt(252) * 100;
                volSeries.push({ t: series[i + 1]?.t || new Date().toISOString(), value: parseFloat(vol.toFixed(2)) });
            }
        }

        return {
            isLive: true,
            metrics: {
                latest,
                changePct,
                ma20: closes.length >= 20 ? closes.slice(-20).reduce((a, b) => a + b, 0) / 20 : undefined,
                ma50: closes.length >= 50 ? closes.slice(-50).reduce((a, b) => a + b, 0) / 50 : undefined,
                above50: closes.length >= 50 ? latest > closes.slice(-50).reduce((a, b) => a + b, 0) / 50 : undefined,
            },
            vol: { current: volCurrent, series: volSeries },
            series,
        };
    } catch {
        clearTimeout(timeout);
        return null;
    }
}

// ============ ANALYSIS ENGINE ============
export function generateExplanation(
    selectedAsset: 'gold' | 'silver',
    snapshot: SnapshotResponse
): {
    whatMoved: string;
    mostLikelyDriver: string;
    chartEvidence: string[];
    plainTakeaway: string;
} {
    const label = selectedAsset.charAt(0).toUpperCase() + selectedAsset.slice(1);
    const assetData = selectedAsset === 'gold' ? snapshot.gold : snapshot.silver;
    const change = assetData.pctChange;
    const yieldChange = snapshot.us10y.bpsChange;
    const dxyChange = snapshot.dxy.pctChange;

    // Determine primary driver
    const yieldScore = Math.abs(yieldChange) * 1.5;
    const dxyScore = Math.abs(dxyChange) * 10;
    const primaryDriver = yieldScore > dxyScore ? 'Interest Rates' : 'U.S. Dollar';

    // Generate whatMoved
    let whatMoved: string;
    if (Math.abs(change) < 0.15) {
        whatMoved = `${label} is trading largely unchanged at $${assetData.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} (${change >= 0 ? '+' : ''}${change.toFixed(2)}%).`;
    } else if (change > 0) {
        whatMoved = `${label} has advanced ${change.toFixed(2)}% to $${assetData.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}.`;
    } else {
        whatMoved = `${label} has declined ${Math.abs(change).toFixed(2)}% to $${assetData.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}.`;
    }

    // Generate chartEvidence
    const chartEvidence: string[] = [];

    if (snapshot.vol[selectedAsset]) {
        chartEvidence.push(
            `The price chart displays ${label}'s recent trajectory, providing context for current levels.`
        );
    }

    chartEvidence.push(
        `The 10-year Treasury yield is at ${snapshot.us10y.yield.toFixed(2)}%, ${Math.abs(yieldChange) > 5
            ? (yieldChange > 0 ? 'up' : 'down') + ` ${Math.abs(yieldChange).toFixed(0)} bps`
            : 'relatively stable'
        }.`
    );

    chartEvidence.push(
        `The Dollar Index (DXY) is at ${snapshot.dxy.value.toFixed(2)}, ${Math.abs(dxyChange) > 0.2
            ? (dxyChange > 0 ? 'strengthening' : 'weakening')
            : 'showing limited movement'
        }.`
    );

    // Generate takeaway
    let plainTakeaway: string;
    if (Math.abs(change) < 0.15) {
        plainTakeaway = `${label} exhibited limited price movement during this session, with no dominant macro driver identified.`;
    } else if (primaryDriver === 'Interest Rates') {
        plainTakeaway = change > 0
            ? `${label} advanced, appearing consistent with declining Treasury yields which reduce the opportunity cost of holding non-yielding assets.`
            : `${label} declined, appearing consistent with rising Treasury yields which increase the relative attractiveness of interest-bearing instruments.`;
    } else {
        plainTakeaway = change > 0
            ? `${label} advanced, appearing consistent with U.S. dollar weakness which historically supports dollar-denominated commodities.`
            : `${label} declined, appearing consistent with U.S. dollar strength which historically creates headwinds for precious metals.`;
    }

    return {
        whatMoved,
        mostLikelyDriver: primaryDriver,
        chartEvidence,
        plainTakeaway,
    };
}
