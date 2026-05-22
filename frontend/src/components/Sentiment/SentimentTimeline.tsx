import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { NewsArticle } from '../../types';

export function SentimentTimeline({ articles }: { articles: NewsArticle[] }) {
  const data = articles.map((item, index) => ({ name: `${index + 1}`, score: item.score })).reverse();
  return (
    <section className="panel">
      <h3 className="mb-3 text-sm font-semibold text-white">Sentiment Timeline</h3>
      <div className="h-44">
        <ResponsiveContainer>
          <AreaChart data={data}>
            <defs><linearGradient id="sentimentFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#22d3ee" stopOpacity={0.45} /><stop offset="100%" stopColor="#22d3ee" stopOpacity={0.02} /></linearGradient></defs>
            <XAxis dataKey="name" hide />
            <YAxis domain={[-1, 1]} hide />
            <Tooltip contentStyle={{ background: '#09090b', border: '1px solid rgba(255,255,255,.1)', borderRadius: 8 }} />
            <Area type="monotone" dataKey="score" stroke="#22d3ee" fill="url(#sentimentFill)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
