export interface StockHistoryItem {
  time: number; // Unix timestamp
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface PredictionData {
  ticker: string;
  current_price: number;
  predicted_price: number;
  change_pct: number;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  sentiment_score: number;
  news_sentiment: 'positive' | 'negative' | 'neutral';
}

export interface NewsArticle {
  headline: string;
  source: string;
  url: string;
  published_at: string;
  score: number;
  label: 'positive' | 'negative' | 'neutral';
  confidence: number;
}

export interface SentimentAnalysisResponse {
  ticker: string;
  sentiment: {
    label: 'positive' | 'negative' | 'neutral';
    confidence: number;
    composite_score: number;
  };
  news_feed: NewsArticle[];
  articles_count: number;
}

export interface EquityCurvePoint {
  date: string;
  portfolio_value: number;
  benchmark_value: number;
}

export interface BacktestResponse {
  ticker: string;
  total_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  buy_and_hold_return: number;
  equity_curve: EquityCurvePoint[];
}

export interface WebSocketPayload {
  type: 'stock_update' | 'pong';
  ticker: string;
  price: number;
  change: number;
  change_pct: number;
  predicted_price: number;
  predicted_change_pct: number;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  sentiment_score: number;
  timestamp: string;
}

export interface StockAssetInfo {
  ticker: string;
  name: string;
  exchange: string;
  sector: string;
  country: string;
}
