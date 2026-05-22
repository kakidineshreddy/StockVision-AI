from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from pydantic import BaseModel, ConfigDict
from app.db.database import Base

# =====================================================================
# SQLAlchemy Database Models
# =====================================================================

class StockData(Base):
    __tablename__ = "stock_data"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True, nullable=False)
    date = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('ticker', 'date', name='_ticker_date_uc'),
    )

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True, nullable=False)
    current_price = Column(Float, nullable=False)
    predicted_price = Column(Float, nullable=False)
    change_pct = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    sentiment_score = Column(Float, nullable=False)
    signal = Column(String, nullable=False)  # BUY, SELL, HOLD
    created_at = Column(DateTime, default=datetime.utcnow)

class SentimentData(Base):
    __tablename__ = "sentiment_data"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True, nullable=False)
    headline = Column(String, nullable=False)
    source = Column(String, nullable=True)
    score = Column(Float, nullable=False)      # Polarity score (-1 to 1)
    label = Column(String, nullable=False)      # positive, negative, neutral
    created_at = Column(DateTime, default=datetime.utcnow)

class ModelMetrics(Base):
    __tablename__ = "model_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True, nullable=False)
    model_type = Column(String, nullable=False) # LSTM, Transformer, Ensemble
    rmse = Column(Float, nullable=False)
    mae = Column(Float, nullable=False)
    sharpe = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# =====================================================================
# Pydantic Schemas for Validation and API
# =====================================================================

class StockBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ticker: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class StockResponse(StockBase):
    id: int

class PredictionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ticker: str
    current_price: float
    predicted_price: float
    change_pct: float
    confidence: float
    sentiment_score: float
    signal: str

class PredictionResponse(PredictionBase):
    id: int
    created_at: datetime

class SentimentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ticker: str
    headline: str
    source: Optional[str] = None
    score: float
    label: str

class SentimentResponse(SentimentBase):
    id: int
    created_at: datetime

class ModelMetricsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ticker: str
    model_type: str
    rmse: float
    mae: float
    sharpe: float

class ModelMetricsResponse(ModelMetricsBase):
    id: int
    created_at: datetime

# Multi-headlines sentiment analysis payload/response
class SentimentAnalysisRequest(BaseModel):
    ticker: str
    headlines: List[str]

class SentimentAnalysisResult(BaseModel):
    label: str
    confidence: float
    composite_score: float

class SentimentAnalysisResponse(BaseModel):
    ticker: str
    sentiment: SentimentAnalysisResult
    articles_analyzed: int

# Backtest result schema
class EquityPoint(BaseModel):
    date: str
    portfolio_value: float
    benchmark_value: float

class BacktestResult(BaseModel):
    ticker: str
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    buy_and_hold_return: float
    equity_curve: List[EquityPoint]
