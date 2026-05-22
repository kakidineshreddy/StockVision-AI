import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { EquityCurvePoint } from '../../types';

export function EquityCurve({ data }: { data: EquityCurvePoint[] }) {
  return (
    <section className="panel">
      <h3 className="mb-3 text-sm font-semibold text-white">Backtest Equity Curve</h3>
      <div className="h-72">
        <ResponsiveContainer>
          <AreaChart data={data}>
            <XAxis dataKey="date" tick={{ fill: '#71717a', fontSize: 11 }} interval="preserveStartEnd" />
            <YAxis tick={{ fill: '#71717a', fontSize: 11 }} domain={['dataMin - 200', 'dataMax + 200']} />
            <Tooltip contentStyle={{ background: '#09090b', border: '1px solid rgba(255,255,255,.1)', borderRadius: 8 }} />
            <Area type="monotone" dataKey="portfolio_value" stroke="#22d3ee" fill="#22d3ee33" />
            <Area type="monotone" dataKey="benchmark_value" stroke="#f59e0b" fill="#f59e0b22" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
