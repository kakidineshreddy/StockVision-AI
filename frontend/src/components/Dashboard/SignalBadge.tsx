import { motion } from 'framer-motion';

export function SignalBadge({ signal = 'HOLD' }: { signal?: 'BUY' | 'SELL' | 'HOLD' }) {
  const cls = signal === 'BUY' ? 'bg-emerald-400/15 text-emerald-200 shadow-glow-green' : signal === 'SELL' ? 'bg-rose-400/15 text-rose-200 shadow-glow-red' : 'bg-amber-400/15 text-amber-200';
  return <motion.span animate={{ scale: [1, 1.04, 1] }} transition={{ repeat: Infinity, duration: 1.8 }} className={`inline-flex rounded-md px-3 py-1 text-xs font-extrabold ${cls}`}>{signal}</motion.span>;
}
