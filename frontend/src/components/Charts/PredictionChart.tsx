import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { PredictionData, StockHistoryItem } from '../../types';

export function PredictionChart({ history, prediction }: { history: StockHistoryItem[]; predictions: unknown[]; prediction: PredictionData | null }) {
  const data = history.slice(-45).map((point, index, arr) => ({ date: point.date.slice(5), close: point.close, predicted: index === arr.length - 1 ? prediction?.predicted_price : undefined }));
  if (data.length && prediction) data.push({ date: 'Next', close: data[data.length - 1].close, predicted: prediction.predicted_price });
  return (
    <section className="panel">
      <h3 className="mb-3 text-sm font-semibold text-white">Prediction Path</h3>
      <div className="h-64">
        <ResponsiveContainer>
          <LineChart data={data}>
            <XAxis dataKey="date" tick={{ fill: '#71717a', fontSize: 11 }} interval="preserveStartEnd" />
            <YAxis tick={{ fill: '#71717a', fontSize: 11 }} domain={['dataMin - 5', 'dataMax + 5']} />
            <Tooltip contentStyle={{ background: '#09090b', border: '1px solid rgba(255,255,255,.1)', borderRadius: 8 }} />
            <Line type="monotone" dataKey="close" stroke="#22d3ee" dot={false} strokeWidth={2} />
            <Line type="monotone" dataKey="predicted" stroke="#c084fc" dot={{ r: 4 }} strokeDasharray="5 5" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
