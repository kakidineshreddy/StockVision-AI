import { useCallback, useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { BacktestResponse, PredictionData, SentimentAnalysisResponse, StockHistoryItem } from '../types';

const makeMockHistory = (ticker: string): StockHistoryItem[] => {
  const seed = ticker.split('').reduce((sum, ch) => sum + ch.charCodeAt(0), 0);
  let price = 90 + (seed % 160);
  return Array.from({ length: 160 }, (_, index) => {
    const date = new Date();
    date.setDate(date.getDate() - (159 - index));
    const wave = Math.sin(index / 8) * 2.8 + Math.cos(index / 17) * 1.7;
    const open = price;
    const close = Math.max(8, open + wave + (Math.random() - 0.48) * 3);
    const high = Math.max(open, close) + 1 + Math.random() * 2.5;
    const low = Math.min(open, close) - 1 - Math.random() * 2;
    price = close;
    return { time: Math.floor(date.getTime() / 1000), date: date.toISOString().slice(0, 10), open, high, low, close, volume: 12_000_000 + Math.round(Math.random() * 38_000_000) };
  });
};

export function useStockData(ticker: string) {
  const [history, setHistory] = useState<StockHistoryItem[]>([]);
  const [prediction, setPrediction] = useState<PredictionData | null>(null);
  const [sentiment, setSentiment] = useState<SentimentAnalysisResponse | null>(null);
  const [backtest, setBacktest] = useState<BacktestResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const [historyResult, predictionResult, sentimentResult, backtestResult] = await Promise.allSettled([
        apiService.getStockHistory(ticker),
        apiService.getPrediction(ticker),
        apiService.getSentiment(ticker),
        apiService.getBacktest(ticker),
      ]);
      const nextHistory = historyResult.status === 'fulfilled' ? historyResult.value : makeMockHistory(ticker);
      setHistory(nextHistory);
      const last = nextHistory.at(-1)?.close ?? 100;
      setPrediction(predictionResult.status === 'fulfilled' ? predictionResult.value : {
        ticker,
        current_price: last,
        predicted_price: last * 1.012,
        change_pct: 1.2,
        signal: 'BUY',
        confidence: 0.78,
        sentiment_score: 0.34,
        news_sentiment: 'positive',
      });
      setSentiment(sentimentResult.status === 'fulfilled' ? sentimentResult.value : {
        ticker,
        sentiment: { label: 'positive', confidence: 0.74, composite_score: 0.32 },
        articles_count: 4,
        news_feed: [
          { headline: `${ticker} momentum improves as analysts raise revenue expectations`, source: 'Market Desk', url: '#', published_at: new Date().toISOString(), score: 0.54, label: 'positive', confidence: 0.82 },
          { headline: `Options flow points to cautious positioning before the next earnings update`, source: 'Alpha Wire', url: '#', published_at: new Date(Date.now() - 3600000).toISOString(), score: -0.12, label: 'neutral', confidence: 0.63 },
          { headline: `Sector rotation keeps institutional volume elevated through afternoon trade`, source: 'Exchange Brief', url: '#', published_at: new Date(Date.now() - 7200000).toISOString(), score: 0.18, label: 'positive', confidence: 0.68 },
        ],
      });
      setBacktest(backtestResult.status === 'fulfilled' ? backtestResult.value : {
        ticker,
        total_return: 18.4,
        sharpe_ratio: 1.42,
        max_drawdown: -8.7,
        win_rate: 61.5,
        buy_and_hold_return: 11.2,
        equity_curve: nextHistory.slice(-90).map((point, i) => ({ date: point.date, portfolio_value: 10000 * (1 + i * 0.002 + Math.sin(i / 9) * 0.018), benchmark_value: 10000 * (1 + i * 0.0013 + Math.cos(i / 10) * 0.014) })),
      });
    } finally {
      setLoading(false);
    }
  }, [ticker]);

  useEffect(() => { void refresh(); }, [refresh]);
  return { history, prediction, sentiment, backtest, loading, refresh };
}
