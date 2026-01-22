import { NextRequest, NextResponse } from 'next/server';
import { generateExplanation, type SnapshotResponse } from '@/lib/market-data';

export const dynamic = 'force-dynamic';

interface ExplainRequest {
    selectedAsset?: 'gold' | 'silver';
    window?: string;
    snapshot: SnapshotResponse;
}

export async function POST(request: NextRequest) {
    const asOf = new Date().toISOString();

    try {
        const body = await request.json() as ExplainRequest;
        const selectedAsset = body.selectedAsset || 'gold';
        const snapshot = body.snapshot;

        if (!snapshot) {
            return NextResponse.json(
                { error: 'snapshot is required in request body' },
                { status: 400 }
            );
        }

        const explanation = generateExplanation(
            selectedAsset as 'gold' | 'silver',
            snapshot
        );

        return NextResponse.json({
            asOf,
            selectedAsset,
            sections: {
                whatMoved: explanation.whatMoved,
                mostLikelyDriver: explanation.mostLikelyDriver,
                chartEvidence: explanation.chartEvidence,
                plainTakeaway: explanation.plainTakeaway,
            },
            disclaimer: 'Market analysis is provided for educational purposes only and does not constitute financial or investment advice.',
        });
    } catch {
        return NextResponse.json(
            { error: 'Failed to generate explanation' },
            { status: 500 }
        );
    }
}
