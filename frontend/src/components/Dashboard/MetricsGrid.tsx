import { motion } from 'framer-motion';
import { Activity, Gauge, LineChart, Percent, ShieldCheck, TrendingDown, TrendingUp, Zap } from 'lucide-react';
import { BacktestResponse, PredictionData } from '../../types';
import { formatCurrency, formatPercent } from '../../utils/formatters';

export function MetricsGrid({ prediction, backtest }: { prediction: PredictionData | null; backtest: BacktestResponse | null }) {
  const metrics = [
    { icon: Activity, label: 'Current Price', value: formatCurrency(prediction?.current_price ?? 0), change: 'live' },
    { icon: TrendingUp, label: 'Predicted', value: formatCurrency(prediction?.predicted_price ?? 0), change: formatPercent(prediction?.change_pct ?? 0) },
    { icon: Percent, label: 'Change', value: formatPercent(prediction?.change_pct ?? 0), change: prediction?.signal ?? 'HOLD' },
    { icon: ShieldCheck, label: 'Confidence', value: `${Math.round((prediction?.confidence ?? 0) * 100)}%`, change: 'agreement' },
    { icon: Zap, label: 'Sentiment', value: (prediction?.sentiment_score ?? 0).toFixed(2), change: 'FinBERT' },
    { icon: Gauge, label: 'Sharpe Ratio', value: (backtest?.sharpe_ratio ?? 0).toFixed(2), change: 'walk-forward' },
    { icon: LineChart, label: 'Win Rate', value: `${(backtest?.win_rate ?? 0).toFixed(1)}%`, change: 'trades' },
    { icon: TrendingDown, label: 'Max Drawdown', value: formatPercent(backtest?.max_drawdown ?? 0), change: 'risk' },
  ];
  return (
    <motion.div initial="hidden" animate="show" variants={{ show: { transition: { staggerChildren: 0.05 } } }} className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {metrics.map(({ icon: Icon, label, value, change }) => (
        <motion.div key={label} variants={{ hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } }} className="mini-panel transition hover:-translate-y-0.5 hover:border-cyan-300/40 hover:shadow-glow-blue">
          <div className="mb-3 flex items-center justify-between">
            <Icon size={17} className="text-cyan-200" />
            <span className="text-[11px] uppercase text-zinc-500">{change}</span>
          </div>
          <p className="text-xs text-zinc-500">{label}</p>
          <p className="mt-1 truncate text-xl font-bold text-white">{value}</p>
        </motion.div>
      ))}
    </motion.div>
  );
}
