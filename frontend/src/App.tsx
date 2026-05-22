import { useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { BarChart3, Newspaper, RefreshCcw, Wifi, WifiOff } from 'lucide-react';
import { Layout } from './components/Layout/Layout';
import { Scene3D } from './components/Three/Scene3D';
import { CandlestickChart } from './components/Charts/CandlestickChart';
import { PredictionChart } from './components/Charts/PredictionChart';
import { VolumeChart } from './components/Charts/VolumeChart';
import { EquityCurve } from './components/Charts/EquityCurve';
import { PredictionCard } from './components/Dashboard/PredictionCard';
import { MetricsGrid } from './components/Dashboard/MetricsGrid';
import { NewsFeed } from './components/Sentiment/NewsFeed';
import { SentimentGauge } from './components/Sentiment/SentimentGauge';
import { SentimentTimeline } from './components/Sentiment/SentimentTimeline';
import { StockSelector } from './components/UI/StockSelector';
import { TrainButton } from './components/UI/TrainButton';
import { LoadingSpinner } from './components/UI/LoadingSpinner';
import { useStockData } from './hooks/useStockData';
import { useWebSocket } from './hooks/useWebSocket';
import { formatCurrency } from './utils/formatters';

export default function App() {
  const [ticker, setTicker] = useState('AAPL');
  const { history, prediction, sentiment, backtest, loading, refresh } = useStockData(ticker);
  const { data: live, connected } = useWebSocket(ticker);

  const livePrediction = useMemo(() => {
    if (!prediction) return null;
    if (!live) return prediction;
    return {
      ...prediction,
      current_price: live.price,
      predicted_price: live.predicted_price,
      change_pct: live.predicted_change_pct,
      confidence: live.confidence,
      sentiment_score: live.sentiment_score,
      signal: live.signal,
    };
  }, [prediction, live]);

  return (
    <Layout ticker={ticker}>
      <Scene3D selectedTicker={ticker} onSelectTicker={setTicker} prediction={livePrediction} history={history} />
      <div className="relative z-10 min-h-screen px-4 pb-8 pt-4 sm:px-6 lg:px-8">
        <div className="mx-auto flex max-w-[1700px] flex-col gap-4">
          <div className="flex flex-col gap-3 rounded-lg border border-white/10 bg-zinc-950/70 p-3 backdrop-blur-xl lg:flex-row lg:items-center lg:justify-between">
            <div className="flex flex-wrap items-center gap-3">
              <StockSelector value={ticker} onChange={setTicker} />
              <TrainButton ticker={ticker} />
              <button className="icon-button" onClick={refresh} title="Refresh market data">
                <RefreshCcw size={18} />
              </button>
              <span className={`inline-flex items-center gap-2 rounded-md px-2.5 py-1 text-xs font-medium ${connected ? 'bg-emerald-500/15 text-emerald-300' : 'bg-rose-500/15 text-rose-300'}`}>
                {connected ? <Wifi size={14} /> : <WifiOff size={14} />}
                {connected ? 'Live' : 'Reconnecting'}
              </span>
            </div>
            <div className="flex items-center gap-2 text-sm text-zinc-300">
              <BarChart3 size={16} />
              <span>{ticker}</span>
              <span className="text-zinc-500">latest</span>
              <strong className="text-white">{formatCurrency(live?.price ?? prediction?.current_price ?? 0)}</strong>
            </div>
          </div>

          {loading && !prediction ? (
            <div className="grid min-h-[60vh] place-items-center"><LoadingSpinner /></div>
          ) : (
            <AnimatePresence mode="wait">
              <motion.div
                key={ticker}
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.35 }}
                className="grid grid-cols-1 gap-4 xl:grid-cols-[380px_minmax(0,1fr)_340px]"
              >
                <aside className="space-y-4">
                  <PredictionCard prediction={livePrediction} />
                  <SentimentGauge score={sentiment?.sentiment.composite_score ?? livePrediction?.sentiment_score ?? 0} confidence={sentiment?.sentiment.confidence ?? livePrediction?.confidence ?? 0} />
                </aside>
                <main className="space-y-4">
                  <MetricsGrid prediction={livePrediction} backtest={backtest} />
                  <CandlestickChart data={history} prediction={livePrediction} />
                  <div className="grid gap-4 lg:grid-cols-2">
                    <PredictionChart history={history} predictions={[]} prediction={livePrediction} />
                    <VolumeChart data={history} />
                  </div>
                  <EquityCurve data={backtest?.equity_curve ?? []} />
                </main>
                <aside className="space-y-4">
                  <div className="panel">
                    <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-white">
                      <Newspaper size={16} />
                      Market News
                    </div>
                    <NewsFeed articles={sentiment?.news_feed ?? []} />
                  </div>
                  <SentimentTimeline articles={sentiment?.news_feed ?? []} />
                </aside>
              </motion.div>
            </AnimatePresence>
          )}
        </div>
      </div>
    </Layout>
  );
}
