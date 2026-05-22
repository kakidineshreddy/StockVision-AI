import { ArrowDownRight, ArrowUpRight, Minus } from 'lucide-react';
import { PredictionData } from '../../types';
import { AnimatedNumber } from '../UI/AnimatedNumber';
import { ConfidenceMeter } from './ConfidenceMeter';
import { SignalBadge } from './SignalBadge';
import { formatCurrency, formatPercent } from '../../utils/formatters';

export function PredictionCard({ prediction }: { prediction: PredictionData | null }) {
  const change = prediction?.change_pct ?? 0;
  const TrendIcon = change > 0.2 ? ArrowUpRight : change < -0.2 ? ArrowDownRight : Minus;
  return (
    <section className="panel overflow-hidden">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-zinc-500">Ensemble Signal</p>
          <h2 className="mt-1 text-2xl font-extrabold text-white">{prediction?.ticker ?? 'Loading'}</h2>
        </div>
        <SignalBadge signal={prediction?.signal} />
      </div>
      <div className="space-y-4">
        <div>
          <p className="text-sm text-zinc-400">Current Price</p>
          <AnimatedNumber value={prediction?.current_price ?? 0} formatter={formatCurrency} className="text-4xl font-extrabold text-white" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="mini-panel">
            <p className="text-xs text-zinc-500">Predicted</p>
            <AnimatedNumber value={prediction?.predicted_price ?? 0} formatter={formatCurrency} className="text-lg font-bold text-cyan-100" />
          </div>
          <div className="mini-panel">
            <p className="text-xs text-zinc-500">Move</p>
            <div className={`flex items-center gap-1 text-lg font-bold ${change >= 0 ? 'text-emerald-300' : 'text-rose-300'}`}>
              <TrendIcon size={18} />
              <AnimatedNumber value={change} formatter={formatPercent} />
            </div>
          </div>
        </div>
        <ConfidenceMeter value={prediction?.confidence ?? 0} />
        <div className="flex items-center justify-between rounded-md bg-white/[0.04] px-3 py-2 text-sm">
          <span className="text-zinc-400">Sentiment</span>
          <span className="font-semibold text-white">{(prediction?.sentiment_score ?? 0).toFixed(2)}</span>
        </div>
      </div>
    </section>
  );
}
