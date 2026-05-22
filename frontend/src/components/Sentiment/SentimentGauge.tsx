import { sentimentColor } from '../../utils/animations';

export function SentimentGauge({ score, confidence }: { score: number; confidence: number }) {
  const normalized = (Math.max(-1, Math.min(1, score)) + 1) / 2;
  return (
    <section className="panel">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white">Sentiment Gauge</h3>
        <span className="text-xs text-zinc-400">{Math.round(confidence * 100)}% confidence</span>
      </div>
      <div className="relative h-28">
        <div className="absolute inset-x-4 bottom-0 h-20 rounded-t-full border-[14px] border-b-0 border-zinc-800" />
        <div className="absolute inset-x-4 bottom-0 h-20 rounded-t-full border-[14px] border-b-0" style={{ borderColor: `${sentimentColor(score)} transparent transparent transparent`, clipPath: `inset(0 ${100 - normalized * 100}% 0 0)` }} />
        <div className="absolute bottom-0 left-1/2 h-20 w-1 origin-bottom -translate-x-1/2 rounded-full bg-white transition-transform duration-700" style={{ transform: `translateX(-50%) rotate(${normalized * 180 - 90}deg)` }} />
      </div>
      <div className="mt-2 text-center text-2xl font-extrabold" style={{ color: sentimentColor(score) }}>{score.toFixed(2)}</div>
    </section>
  );
}
