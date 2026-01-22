import { NextRequest, NextResponse } from 'next/server';
import {
    ASSETS,
    fetchYahooData,
    generateDemoSeries,
    type TimeseriesResponse
} from '@/lib/market-data';

export const dynamic = 'force-dynamic';

const WINDOW_MAP: Record<string, number> = {
    '1D': 5,
    '5D': 10,
    '1M': 22,
    '3M': 66,
    '6M': 130,
    '1Y': 252,
};

const RANGE_MAP: Record<string, string> = {
    '1D': '5d',
    '5D': '1mo',
    '1M': '3mo',
    '3M': '6mo',
    '6M': '1y',
    '1Y': '2y',
};

export async function GET(request: NextRequest) {
    const { searchParams } = new URL(request.url);
    const asset = searchParams.get('asset') || 'gold';
    const window = searchParams.get('window') || '1M';

    const asOf = new Date().toISOString();

    // Handle volatility series
    if (asset.startsWith('vol_')) {
        const baseAsset = asset.replace('vol_', '') as 'gold' | 'silver';
        const validAsset = baseAsset === 'gold' || baseAsset === 'silver' ? baseAsset : 'gold';

        const liveData = await fetchYahooData(ASSETS[validAsset].symbol, RANGE_MAP[window] || '3mo').catch(() => null);
        const data = liveData || generateDemoSeries(validAsset);

        const response: TimeseriesResponse = {
            asOf,
            asset,
            window,
            supportsCandles: false,
            series: data.vol.series.slice(-(WINDOW_MAP[window] || 22)),
        };

        return NextResponse.json(response);
    }

    // Validate asset
    const validAssets = ['gold', 'silver', 'us10y', 'dxy'];
    const validAsset = validAssets.includes(asset) ? asset : 'gold';

    // Fetch live data or fall back to demo
    const liveData = await fetchYahooData(ASSETS[validAsset].symbol, RANGE_MAP[window] || '3mo').catch(() => null);
    const data = liveData || generateDemoSeries(validAsset);

    // Slice to window size
    const limit = WINDOW_MAP[window] || 22;
    const series = data.series.slice(-limit);

    // Determine if candles are supported
    const supportsCandles = series.length > 0 && 'open' in series[0] && series[0].open != null;

    const response: TimeseriesResponse = {
        asOf,
        asset: validAsset,
        window,
        supportsCandles,
        series,
    };

    return NextResponse.json(response);
}
