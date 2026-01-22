import { NextResponse } from 'next/server';
import {
    ASSETS,
    fetchYahooData,
    generateDemoSeries,
    type SnapshotResponse
} from '@/lib/market-data';

export const dynamic = 'force-dynamic';

export async function GET() {
    const asOf = new Date().toISOString();

    // Fetch all assets in parallel with timeout
    const [goldData, silverData, dxyData, us10yData] = await Promise.all([
        fetchYahooData(ASSETS.gold.symbol).catch(() => null),
        fetchYahooData(ASSETS.silver.symbol).catch(() => null),
        fetchYahooData(ASSETS.dxy.symbol).catch(() => null),
        fetchYahooData(ASSETS.us10y.symbol).catch(() => null),
    ]);

    // Fall back to demo data if live fetch fails
    const gold = goldData || generateDemoSeries('gold');
    const silver = silverData || generateDemoSeries('silver');
    const dxy = dxyData || generateDemoSeries('dxy');
    const us10y = us10yData || generateDemoSeries('us10y');

    // Track which feeds are live
    const feeds: Record<string, 'live' | 'demo'> = {
        gold: goldData ? 'live' : 'demo',
        silver: silverData ? 'live' : 'demo',
        us10y: us10yData ? 'live' : 'demo',
        dxy: dxyData ? 'live' : 'demo',
        vol_gold: goldData ? 'live' : 'demo',
        vol_silver: silverData ? 'live' : 'demo',
    };

    const liveCount = Object.values(feeds).filter(v => v === 'live').length;
    const mode = liveCount === 6 ? 'live' : liveCount === 0 ? 'demo' : 'partial';

    const response: SnapshotResponse = {
        asOf,
        mode,
        feeds,
        gold: {
            price: gold.metrics.latest,
            pctChange: gold.metrics.changePct,
        },
        silver: {
            price: silver.metrics.latest,
            pctChange: silver.metrics.changePct,
        },
        us10y: {
            yield: us10y.metrics.latest,
            bpsChange: us10y.metrics.changePct * 10,
        },
        dxy: {
            value: dxy.metrics.latest,
            pctChange: dxy.metrics.changePct,
        },
        vol: {
            gold: {
                value: gold.vol.current,
                change: 0,
                type: 'realized',
            },
            silver: {
                value: silver.vol.current,
                change: 0,
                type: 'realized',
            },
        },
    };

    return NextResponse.json(response);
}
