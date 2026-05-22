export function ConfidenceMeter({ value = 0 }: { value?: number }) {
  const pct = Math.round(Math.max(0, Math.min(1, value)) * 100);
  return (
    <div>
      <div className="mb-1 flex justify-between text-xs text-zinc-400"><span>Confidence</span><span>{pct}%</span></div>
      <div className="h-2 overflow-hidden rounded-full bg-white/10">
        <div className="h-full rounded-full bg-gradient-to-r from-cyan-300 via-fuchsia-400 to-rose-300 transition-all duration-700" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
