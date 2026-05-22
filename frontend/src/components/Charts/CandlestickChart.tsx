import { useEffect, useRef } from 'react';
import { ColorType, createChart } from 'lightweight-charts';
import { PredictionData, StockHistoryItem } from '../../types';

export function CandlestickChart({ data, prediction }: { data: StockHistoryItem[]; prediction: PredictionData | null }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    const chart = createChart(ref.current, {
      height: 430,
      layout: { background: { type: ColorType.Solid, color: 'transparent' }, textColor: '#a1a1aa' },
      grid: { vertLines: { color: 'rgba(255,255,255,.05)' }, horzLines: { color: 'rgba(255,255,255,.05)' } },
      rightPriceScale: { borderColor: 'rgba(255,255,255,.08)' },
      timeScale: { borderColor: 'rgba(255,255,255,.08)' },
      crosshair: { mode: 1 },
    });
    const candleSeries = chart.addCandlestickSeries({ upColor: '#22c55e', downColor: '#ef4444', wickUpColor: '#22c55e', wickDownColor: '#ef4444', borderVisible: false });
    candleSeries.setData(data.map((d) => ({ time: d.date, open: d.open, high: d.high, low: d.low, close: d.close })));
    const ma20 = chart.addLineSeries({ color: '#22d3ee', lineWidth: 1 });
    const ma50 = chart.addLineSeries({ color: '#f472b6', lineWidth: 1 });
    ma20.setData(data.map((d, i) => ({ time: d.date, value: data.slice(Math.max(0, i - 19), i + 1).reduce((s, p) => s + p.close, 0) / Math.min(i + 1, 20) })));
    ma50.setData(data.map((d, i) => ({ time: d.date, value: data.slice(Math.max(0, i - 49), i + 1).reduce((s, p) => s + p.close, 0) / Math.min(i + 1, 50) })));
    if (prediction && data.length) {
      const last = data[data.length - 1];
      const pred = chart.addLineSeries({ color: '#c084fc', lineStyle: 2, lineWidth: 2 });
      pred.setData([{ time: last.date, value: last.close }, { time: new Date((last.time + 86400) * 1000).toISOString().slice(0, 10), value: prediction.predicted_price }]);
    }
    chart.timeScale().fitContent();
    const resize = () => chart.applyOptions({ width: ref.current?.clientWidth ?? 600 });
    resize();
    window.addEventListener('resize', resize);
    return () => { window.removeEventListener('resize', resize); chart.remove(); };
  }, [data, prediction]);

  return <section className="panel"><h3 className="mb-3 text-sm font-semibold text-white">Candlestick Chart</h3><div ref={ref} className="h-[430px] w-full" /></section>;
}
