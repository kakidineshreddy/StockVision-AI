import { Activity, Cpu } from 'lucide-react';

export function Header({ ticker }: { ticker: string }) {
  return (
    <header className="sticky top-0 z-20 border-b border-white/10 bg-black/55 backdrop-blur-xl">
      <div className="mx-auto flex h-14 max-w-[1700px] items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="grid h-9 w-9 place-items-center rounded-md bg-cyan-400/15 text-cyan-200 shadow-glow-blue">
            <Activity size={20} />
          </div>
          <div>
            <h1 className="text-base font-extrabold tracking-normal text-white">StockVision AI</h1>
            <p className="text-xs text-zinc-400">Real-time ensemble predictor</p>
          </div>
        </div>
        <div className="hidden items-center gap-2 rounded-md border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-zinc-300 sm:flex">
          <Cpu size={14} className="text-fuchsia-300" />
          LSTM + Transformer + FinBERT
          <span className="font-semibold text-white">{ticker}</span>
        </div>
      </div>
    </header>
  );
}
