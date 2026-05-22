import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { StockHistoryItem } from '../../types';
import { compactNumber } from '../../utils/formatters';

export function VolumeChart({ data }: { data: StockHistoryItem[] }) {
  const rows = data.slice(-45).map((d) => ({ date: d.date.slice(5), volume: d.volume, fill: d.close >= d.open ? '#22c55e' : '#ef4444' }));
  return (
    <section className="panel">
      <h3 className="mb-3 text-sm font-semibold text-white">Volume</h3>
      <div className="h-64">
        <ResponsiveContainer>
          <BarChart data={rows}>
            <XAxis dataKey="date" tick={{ fill: '#71717a', fontSize: 11 }} interval="preserveStartEnd" />
            <YAxis tickFormatter={compactNumber} tick={{ fill: '#71717a', fontSize: 11 }} />
            <Tooltip formatter={(v) => compactNumber(Number(v))} contentStyle={{ background: '#09090b', border: '1px solid rgba(255,255,255,.1)', borderRadius: 8 }} />
            <Bar dataKey="volume" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
