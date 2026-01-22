'use client';

import { SnapshotResponse } from '@/lib/api';

interface DataBannerProps {
    snapshot: SnapshotResponse;
    onRefresh: () => void;
    isLoading?: boolean;
}

export default function DataBanner({ snapshot, onRefresh, isLoading }: DataBannerProps) {
    const mode = snapshot.mode;
    const asOf = new Date(snapshot.asOf).toLocaleTimeString();

    return (
        <div className={`data-banner ${mode}`}>
            <div className="flex items-center gap-3">
                <span className="font-medium">
                    {mode === 'live' && '● Live data'}
                    {mode === 'demo' && '◆ Demo mode'}
                    {mode === 'partial' && '◐ Partial feeds'}
                </span>
                <span className="opacity-70">
                    Updated: {asOf}
                </span>
            </div>
            <button
                onClick={onRefresh}
                disabled={isLoading}
                className="btn btn-primary"
            >
                {isLoading ? '↻...' : '↻ Refresh'}
            </button>
        </div>
    );
}
