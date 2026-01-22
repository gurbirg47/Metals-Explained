'use client';

import { useState, useEffect, useCallback, memo } from 'react';
import DataBanner from '@/components/DataBanner';
import MetricCard from '@/components/MetricCard';
import PriceChart from '@/components/PriceChart';
import {
  getSnapshot,
  getTimeseries,
  getExplanation,
  refreshData,
  API_BASE,
  SnapshotResponse,
  TimeseriesResponse,
  ExplainResponse,
} from '@/lib/api';

// Session cache - includes both gold and silver volatility
const dataCache: {
  snapshot: SnapshotResponse | null;
  gold: TimeseriesResponse | null;
  silver: TimeseriesResponse | null;
  yield: TimeseriesResponse | null;
  dxy: TimeseriesResponse | null;
  goldVol: TimeseriesResponse | null;
  silverVol: TimeseriesResponse | null;
  explanation: ExplainResponse | null;
  timestamp: number;
} = {
  snapshot: null,
  gold: null,
  silver: null,
  yield: null,
  dxy: null,
  goldVol: null,
  silverVol: null,
  explanation: null,
  timestamp: 0,
};

const CACHE_TTL = 5 * 60 * 1000;

function isCacheValid(): boolean {
  return Date.now() - dataCache.timestamp < CACHE_TTL && dataCache.snapshot !== null;
}

// Chart skeleton
function ChartSkeleton({ title }: { title: string }) {
  return (
    <div className="chart-container flex items-center justify-center h-[280px] bg-[rgba(255,255,255,0.02)]">
      <div className="text-center">
        <div className="w-5 h-5 border-2 border-[var(--signal-accent)] border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
        <p className="text-[var(--text-muted)] text-xs">Loading {title}...</p>
      </div>
    </div>
  );
}

// Memoized chart
const MemoizedChart = memo(function MemoizedChart({
  title,
  series,
  chartType,
  color,
}: {
  title: string;
  series: TimeseriesResponse | null;
  chartType: 'line' | 'candlestick';
  color: string;
}) {
  if (!series || series.series.length === 0) {
    return <ChartSkeleton title={title} />;
  }

  return (
    <PriceChart
      title={title}
      series={series.series}
      hasOHLC={series.hasOHLC}
      chartType={chartType}
      color={color}
    />
  );
});

export default function HomePage() {
  const [snapshot, setSnapshot] = useState<SnapshotResponse | null>(dataCache.snapshot);
  const [goldSeries, setGoldSeries] = useState<TimeseriesResponse | null>(dataCache.gold);
  const [silverSeries, setSilverSeries] = useState<TimeseriesResponse | null>(dataCache.silver);
  const [yieldSeries, setYieldSeries] = useState<TimeseriesResponse | null>(dataCache.yield);
  const [dxySeries, setDxySeries] = useState<TimeseriesResponse | null>(dataCache.dxy);
  const [goldVolSeries, setGoldVolSeries] = useState<TimeseriesResponse | null>(dataCache.goldVol);
  const [silverVolSeries, setSilverVolSeries] = useState<TimeseriesResponse | null>(dataCache.silverVol);
  const [explanation, setExplanation] = useState<ExplainResponse | null>(dataCache.explanation);

  const [selectedAsset, setSelectedAsset] = useState<'gold' | 'silver'>('gold');
  const [chartType, setChartType] = useState<'line' | 'candlestick'>('line');
  const [isLoading, setIsLoading] = useState(!isCacheValid());
  const [error, setError] = useState<string | null>(null);

  // Diagnostic connectivity check
  useEffect(() => {
    console.log(`[Diagnostic] Attempting to reach backend at: ${API_BASE}`);
    fetch(`${API_BASE}/health`)
      .then(r => console.log(`[Diagnostic] Health check: ${r.status} ${r.ok ? 'OK' : 'Error'}`))
      .catch(e => console.error(`[Diagnostic] Backend unreachable:`, e.message));
  }, []);

  const loadData = useCallback(async (forceRefresh = false) => {
    if (!forceRefresh && isCacheValid()) {
      setSnapshot(dataCache.snapshot);
      setGoldSeries(dataCache.gold);
      setSilverSeries(dataCache.silver);
      setYieldSeries(dataCache.yield);
      setDxySeries(dataCache.dxy);
      setGoldVolSeries(dataCache.goldVol);
      setSilverVolSeries(dataCache.silverVol);
      setExplanation(dataCache.explanation);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Fetch all data in parallel
      const results = await Promise.allSettled([
        getSnapshot(),
        getTimeseries('gold', '1M'),
        getTimeseries('silver', '1M'),
        getTimeseries('us10y', '1M'),
        getTimeseries('dxy', '1M'),
        getTimeseries('gold_vol', '1M'),
        getTimeseries('silver_vol', '1M'),
      ]);

      const snap = results[0].status === 'fulfilled' ? results[0].value : null;
      const gold = results[1].status === 'fulfilled' ? results[1].value : null;
      const silver = results[2].status === 'fulfilled' ? results[2].value : null;
      const yld = results[3].status === 'fulfilled' ? results[3].value : null;
      const dxy = results[4].status === 'fulfilled' ? results[4].value : null;
      const goldVol = results[5].status === 'fulfilled' ? results[5].value : null;
      const silverVol = results[6].status === 'fulfilled' ? results[6].value : null;

      if (!snap) {
        const errorDetail = results[0].status === 'rejected' ? (results[0].reason as Error).message : 'Snapshot returned empty data (null)';
        const baseUrl = API_BASE || 'NONE';
        setError(`Unable to load market data: ${errorDetail}. URL: ${baseUrl}.`);
        setIsLoading(false);
        return;
      }

      setSnapshot(snap);
      setGoldSeries(gold);
      setSilverSeries(silver);
      setYieldSeries(yld);
      setDxySeries(dxy);
      setGoldVolSeries(goldVol);
      setSilverVolSeries(silverVol);
      setIsLoading(false);

      // Update cache
      dataCache.snapshot = snap;
      dataCache.gold = gold;
      dataCache.silver = silver;
      dataCache.yield = yld;
      dataCache.dxy = dxy;
      dataCache.goldVol = goldVol;
      dataCache.silverVol = silverVol;
      dataCache.timestamp = Date.now();

    } catch (err) {
      console.error('Load error:', err);
      setError('Failed to load market data.');
      setIsLoading(false);
    }
  }, []);

  // Fetch explanation when asset changes
  useEffect(() => {
    if (!snapshot) return;

    setExplanation(null); // Clear old analysis
    getExplanation(selectedAsset, '1D')
      .then((explain) => {
        setExplanation(explain);
        dataCache.explanation = explain;
      })
      .catch(() => { });
  }, [selectedAsset, snapshot]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleRefresh = async () => {
    setIsLoading(true);
    try {
      await refreshData();
    } catch (e) {
      console.error('Refresh failed:', e);
    }
    dataCache.timestamp = 0;
    loadData(true);
  };

  const formatPrice = (value: number | null, decimals = 2): string => {
    if (value === null) return 'N/A';
    return value.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  };

  const formatChange = (value: number | null): { text: string; type: 'up' | 'down' | 'neutral' } => {
    if (value === null) return { text: 'N/A', type: 'neutral' };
    const sign = value >= 0 ? '+' : '';
    return {
      text: `${sign}${value.toFixed(2)}%`,
      type: value > 0 ? 'up' : value < 0 ? 'down' : 'neutral',
    };
  };

  if (isLoading && !snapshot) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] text-center">
        <h1 className="text-2xl font-bold mb-3">Metals, Explained</h1>
        <p className="text-[var(--text-muted)] text-xs mb-6">A learning-focused guide to gold and silver markets.</p>
        <div className="w-5 h-5 border-2 border-[var(--signal-accent)] border-t-transparent rounded-full animate-spin mb-3"></div>
        <p className="mono text-[var(--signal-accent)] text-xs">Loading market data...</p>
      </div>
    );
  }

  if (error || !snapshot) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] text-center">
        <h1 className="text-2xl font-bold mb-3">Metals, Explained</h1>
        <p className="text-[var(--signal-down)] text-xs mb-4">{error || 'Unable to load market data.'}</p>
        <button onClick={() => loadData(true)} className="btn btn-primary text-xs">
          ↻ Retry
        </button>
      </div>
    );
  }

  const goldChange = formatChange(snapshot.gold.pctChange);
  const silverChange = formatChange(snapshot.silver.pctChange);
  const dxyChange = formatChange(snapshot.dxy.pctChange);

  const selectedSeries = selectedAsset === 'gold' ? goldSeries : silverSeries;
  const selectedVolSeries = selectedAsset === 'gold' ? goldVolSeries : silverVolSeries;
  const selectedColor = selectedAsset === 'gold' ? '#FFD700' : '#C0C0C0';
  const selectedLabel = selectedAsset === 'gold' ? 'Gold' : 'Silver';
  const selectedVolLabel = selectedAsset === 'gold' ? 'Gold Volatility (20D)' : 'Silver Volatility (20D)';

  return (
    <div>
      {/* Dev-only Diagnostic Banner */}
      {(process.env.NODE_ENV === 'development' || (typeof window !== 'undefined' && window.location.hostname.includes('vercel.app'))) && (
        <div className="bg-[rgba(51,197,244,0.1)] border-b border-[rgba(51,197,244,0.2)] px-4 py-1 text-[10px] mono text-[var(--signal-accent)] flex justify-between items-center">
          <span>[DIAGNOSTIC] API_BASE: {API_BASE}</span>
          <span className={snapshot ? 'text-green-400' : 'text-red-400'}>
            BACKEND: {snapshot ? 'CONNECTED' : 'DISCONNECTED'}
          </span>
        </div>
      )}

      <DataBanner snapshot={snapshot} onRefresh={handleRefresh} isLoading={isLoading} />

      {/* Header */}
      <h1 className="mb-1 text-xl">Metals, Explained</h1>
      <p className="text-[var(--text-muted)] text-xs mb-4">
        A learning-focused guide to understanding gold and silver markets.
      </p>

      {/* Market Snapshot */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-2 mb-4">
        <MetricCard
          label="GOLD"
          value={`$${formatPrice(snapshot.gold.price)}`}
          delta={goldChange.text}
          deltaType={goldChange.type}
        />
        <MetricCard
          label="SILVER"
          value={`$${formatPrice(snapshot.silver.price)}`}
          delta={silverChange.text}
          deltaType={silverChange.type}
        />
        <MetricCard
          label="10Y YIELD"
          value={snapshot.us10y.yield ? `${snapshot.us10y.yield.toFixed(2)}%` : 'N/A'}
          delta={snapshot.us10y.bpsChange ? `${snapshot.us10y.bpsChange >= 0 ? '+' : ''}${snapshot.us10y.bpsChange.toFixed(0)} bps` : 'flat'}
          deltaType={snapshot.us10y.bpsChange && snapshot.us10y.bpsChange > 0 ? 'up' : snapshot.us10y.bpsChange && snapshot.us10y.bpsChange < 0 ? 'down' : 'neutral'}
        />
        <MetricCard
          label="DXY"
          value={formatPrice(snapshot.dxy.value)}
          delta={dxyChange.text}
          deltaType={dxyChange.type}
        />
        <MetricCard
          label={`${selectedAsset.toUpperCase()} VOL`}
          value={snapshot.vol[selectedAsset]?.value ? `${snapshot.vol[selectedAsset].value.toFixed(1)}%` : 'N/A'}
          delta={snapshot.vol[selectedAsset]?.type || "realized"}
          deltaType="neutral"
        />
      </div>

      {/* Price Chart Section */}
      <h3 className="mt-5 mb-3 text-base">Price Charts</h3>

      {/* Controls Row */}
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <div className="flex items-center gap-2">
          <label className="text-xs text-[var(--text-muted)] mono">Asset:</label>
          <select
            value={selectedAsset}
            onChange={(e) => setSelectedAsset(e.target.value as 'gold' | 'silver')}
            className="bg-[var(--bg-surface)] border border-[rgba(255,255,255,0.2)] rounded px-2 py-1 text-xs text-[var(--text-primary)] mono cursor-pointer focus:border-[var(--signal-accent)] focus:outline-none"
          >
            <option value="gold">Gold</option>
            <option value="silver">Silver</option>
          </select>
        </div>

        <div className="flex gap-1">
          <button
            onClick={() => setChartType('line')}
            className={`btn btn-secondary text-xs py-1 px-2 ${chartType === 'line' ? 'active' : ''}`}
          >
            📈 Line
          </button>
          <button
            onClick={() => setChartType('candlestick')}
            className={`btn btn-secondary text-xs py-1 px-2 ${chartType === 'candlestick' ? 'active' : ''}`}
          >
            🕯️ Candle
          </button>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
        <MemoizedChart
          title={selectedLabel}
          series={selectedSeries}
          chartType={chartType}
          color={selectedColor}
        />
        <MemoizedChart
          title="U.S. 10-Year Yield"
          series={yieldSeries}
          chartType="line"
          color="#FF6B00"
        />
        <MemoizedChart
          title="U.S. Dollar Index (DXY)"
          series={dxySeries}
          chartType="line"
          color="#33C5F4"
        />
        <MemoizedChart
          title={selectedVolLabel}
          series={selectedVolSeries}
          chartType="line"
          color="#FF453A"
        />
      </div>

      {/* Market Analysis */}
      <div className="mt-5">
        <h2 className="text-lg border-b border-[var(--text-muted)] pb-2 mb-3">Market Analysis</h2>

        <p className="text-[var(--text-muted)] text-xs italic mb-3 px-2 py-1 bg-[rgba(255,255,255,0.02)] rounded">
          {explanation?.disclaimer || "Market analysis is provided for educational purposes only and does not constitute financial or investment advice."}
        </p>

        {explanation ? (
          <div className="space-y-2">
            <div className="section-card py-2">
              <h4 className="section-title text-xs">Observation: What Moved</h4>
              <p className="text-[var(--text-muted)] text-xs">{explanation.sections.whatMoved}</p>
            </div>

            <div className="section-card py-2">
              <h4 className="section-title text-xs">Mechanism: Most Likely Driver</h4>
              <p className="text-[var(--text-muted)] text-xs">{explanation.sections.mostLikelyDriver}</p>
            </div>

            <div className="section-card py-2">
              <h4 className="section-title text-xs">Chart Evidence</h4>
              <div className="space-y-1">
                {explanation.sections.chartEvidence.map((bullet, i) => (
                  <p key={i} className="text-[var(--text-muted)] text-xs">• {bullet}</p>
                ))}
              </div>
            </div>

            <div className="section-card py-2 bg-[rgba(255,255,255,0.02)] border-l-2 border-[var(--signal-accent)]">
              <h4 className="section-title text-xs">Plain Takeaway</h4>
              <p className="text-[var(--text-primary)] text-xs">{explanation.sections.plainTakeaway}</p>
            </div>
          </div>
        ) : (
          <div className="section-card py-2">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 border-2 border-[var(--signal-accent)] border-t-transparent rounded-full animate-spin"></div>
              <p className="text-[var(--text-muted)] text-xs">Generating market analysis...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
