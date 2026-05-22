import { useState } from 'react';
import { NewsArticle } from '../../types';
import { relativeTime } from '../../utils/formatters';

export function NewsFeed({ articles }: { articles: NewsArticle[] }) {
  const [open, setOpen] = useState<string | null>(null);
  return (
    <div className="max-h-[440px] space-y-2 overflow-auto pr-1">
      {articles.map((article) => (
        <button key={`${article.source}-${article.headline}`} onClick={() => setOpen(open === article.headline ? null : article.headline)} className="block w-full rounded-md border border-white/10 bg-white/[0.04] p-3 text-left transition hover:border-cyan-300/40 hover:bg-white/[0.07]">
          <div className="flex items-start gap-2">
            <span className={`mt-1 h-2.5 w-2.5 rounded-full ${article.label === 'positive' ? 'bg-emerald-400' : article.label === 'negative' ? 'bg-rose-400' : 'bg-amber-300'}`} />
            <p className={`text-sm text-zinc-100 ${open === article.headline ? '' : 'line-clamp-2'}`}>{article.headline}</p>
          </div>
          <div className="mt-2 flex items-center justify-between text-xs text-zinc-500">
            <span>{article.source}</span>
            <span>{relativeTime(article.published_at)}</span>
          </div>
        </button>
      ))}
    </div>
  );
}
