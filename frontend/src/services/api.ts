import axios from 'axios';
import { 
  StockHistoryItem, 
  PredictionData, 
  SentimentAnalysisResponse, 
  BacktestResponse,
  StockAssetInfo
} from '../types';

// Fallback to localhost if window is undefined, otherwise dynamically point to backend container or host
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  /** Search assets by query */
  async searchStocks(query: string): Promise<StockAssetInfo[]> {
    const res = await client.get<StockAssetInfo[]>('/api/stocks/search', { params: { q: query } });
    return res.data;
  },

  /** Retrieve candle price history */
  async getStockHistory(ticker: string, period: string = '1y'): Promise<StockHistoryItem[]> {
    const res = await client.get<StockHistoryItem[]>(`/api/stocks/${ticker}/history`, { params: { period } });
    return res.data;
  },

  /** Run news headlines sentiment analysis */
  async getSentiment(ticker: string): Promise<SentimentAnalysisResponse> {
    const res = await client.get<SentimentAnalysisResponse>(`/api/sentiment/${ticker}`);
    return res.data;
  },

  /** Fetch current live prediction */
  async getPrediction(ticker: string): Promise<PredictionData> {
    const res = await client.get<PredictionData>(`/api/predictions/predict/${ticker}`);
    return res.data;
  },

  /** Fetch prediction database history log */
  async getPredictionHistory(ticker: string): Promise<any[]> {
    const res = await client.get<any[]>(`/api/predictions/history/${ticker}`);
    return res.data;
  },

  /** Run model backtesting over a day interval */
  async getBacktest(ticker: string, days: number = 252): Promise<BacktestResponse> {
    const res = await client.get<BacktestResponse>(`/api/predictions/backtest/${ticker}`, { params: { days } });
    return res.data;
  },

  /** Launch background model training */
  async trainModel(ticker: string): Promise<{ ticker: string; status: string; message: string }> {
    const postRes = await client.post<{ ticker: string; status: string; message: string }>(`/api/predictions/train/${ticker}`);
    return postRes.data;
  }
};
