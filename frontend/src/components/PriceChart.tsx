'use client';

import { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, ColorType, LineSeries, CandlestickSeries } from 'lightweight-charts';
import { TimeseriesPoint } from '@/lib/api';

interface PriceChartProps {
    title: string;
    series: TimeseriesPoint[];
    hasOHLC: boolean;
    chartType: 'line' | 'candlestick';
    color?: string;
    caption?: string;
}

export default function PriceChart({
    title,
    series,
    hasOHLC,
    chartType,
    color = '#FFD700',
    caption,
}: PriceChartProps) {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);
    const [chartKey, setChartKey] = useState(0);

    useEffect(() => {
        if (!chartContainerRef.current || series.length === 0) return;

        // Clear any existing chart
        if (chartRef.current) {
            chartRef.current.remove();
            chartRef.current = null;
        }

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: 'transparent' },
                textColor: '#B0B8C0',
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 13,
            },
            grid: {
                vertLines: { color: 'rgba(160, 168, 176, 0.1)' },
                horzLines: { color: 'rgba(160, 168, 176, 0.15)' },
            },
            维持Width: true,
            width: chartContainerRef.current.clientWidth,
            height: 280,
            timeScale: {
                borderColor: 'rgba(160, 168, 176, 0.2)',
                timeVisible: true,
                secondsVisible: false,
            },
            rightPriceScale: {
                borderColor: 'rgba(160, 168, 176, 0.2)',
            },
        });

        chartRef.current = chart;

        const useCandlestick = chartType === 'candlestick' && hasOHLC;

        if (useCandlestick) {
            const candlestickSeries = chart.addSeries(CandlestickSeries, {
                upColor: '#00E676',
                downColor: '#FF453A',
                borderUpColor: '#00E676',
                borderDownColor: '#FF453A',
                wickUpColor: '#00E676',
                wickDownColor: '#FF453A',
            });

            const candleData = series
                .filter((p) => p.open != null && p.high != null && p.low != null && p.close != null)
                .map((p) => ({
                    time: p.t.split('T')[0] as `${number}-${number}-${number}`,
                    open: p.open!,
                    high: p.high!,
                    low: p.low!,
                    close: p.close!,
                }));

            candlestickSeries.setData(candleData);
        } else {
            const lineSeries = chart.addSeries(LineSeries, {
                color: color,
                lineWidth: 2,
            });

            const lineData = series
                .filter((p) => p.value != null || p.close != null)
                .map((p) => ({
                    time: p.t.split('T')[0] as `${number}-${number}-${number}`,
                    value: (p.value ?? p.close)!,
                }));

            lineSeries.setData(lineData);
        }

        chart.timeScale().fitContent();

        // Handle resize
        const handleResize = () => {
            if (chartContainerRef.current && chartRef.current) {
                chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
            }
        };
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            if (chartRef.current) {
                chartRef.current.remove();
                chartRef.current = null;
            }
        };
    }, [series, chartType, hasOHLC, color, chartKey]);

    // Force re-render when chart type changes
    useEffect(() => {
        setChartKey((k) => k + 1);
    }, [chartType]);

    if (series.length === 0) {
        return (
            <div className="chart-container flex items-center justify-center h-[320px]">
                <p className="text-[var(--text-muted)]">No data available</p>
            </div>
        );
    }

    return (
        <div className="chart-container">
            <h4 className="chart-title">{title}</h4>
            <div ref={chartContainerRef} key={chartKey} />
            {caption && <p className="chart-caption">{caption}</p>}
            {chartType === 'candlestick' && !hasOHLC && (
                <p className="chart-caption text-[var(--signal-volatility)]">
                    Candlestick view unavailable for this series.
                </p>
            )}
        </div>
    );
}
