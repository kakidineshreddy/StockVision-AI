import { useEffect, useState } from 'react';
import { Search } from 'lucide-react';
import { apiService } from '../../services/api';
import { StockAssetInfo } from '../../types';

export function StockSelector({ value, onChange }: { value: string; onChange: (ticker: string) => void }) {
  const [query, setQuery] = useState(value);
  const [matches, setMatches] = useState<StockAssetInfo[]>([]);

  useEffect(() => {
    const id = window.setTimeout(async () => {
      if (query.length < 1) return;
      try { setMatches(await apiService.searchStocks(query)); } catch { setMatches([]); }
    }, 180);
    return () => window.clearTimeout(id);
  }, [query]);

  return (
    <div className="relative min-w-[260px]">
      <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={16} />
      <input value={query} onChange={(e) => setQuery(e.target.value.toUpperCase())} onKeyDown={(e) => e.key === 'Enter' && onChange(query.toUpperCase())} className="h-10 w-full rounded-md border border-white/10 bg-black/40 pl-9 pr-3 text-sm text-white outline-none transition focus:border-cyan-300/60" />
      {matches.length > 0 && query !== value && (
        <div className="absolute left-0 right-0 top-12 z-30 max-h-72 overflow-auto rounded-lg border border-white/10 bg-zinc-950/95 p-1 shadow-2xl backdrop-blur-xl">
          {matches.slice(0, 6).map((item) => (
            <button key={item.ticker} className="flex w-full items-center justify-between rounded-md px-3 py-2 text-left text-sm hover:bg-white/10" onClick={() => { onChange(item.ticker); setQuery(item.ticker); }}>
              <span><strong className="text-white">{item.ticker}</strong><span className="ml-2 text-zinc-400">{item.name}</span></span>
              <span className="text-xs text-zinc-500">{item.exchange}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
