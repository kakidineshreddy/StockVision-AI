import logging
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Dict, Any
from app.data.ingestion import DataIngestion

logger = logging.getLogger("stockvision.api.stocks")

router = APIRouter(prefix="/api/stocks", tags=["stocks"])

# A rich dictionary of popular global assets for standard search indices
POPULAR_STOCKS = [
    {"ticker": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "sector": "Technology", "country": "USA"},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ", "sector": "Technology", "country": "USA"},
    {"ticker": "GOOGL", "name": "Alphabet Inc. (Class A)", "exchange": "NASDAQ", "sector": "Technology", "country": "USA"},
    {"ticker": "GOOG", "name": "Alphabet Inc. (Class C)", "exchange": "NASDAQ", "sector": "Technology", "country": "USA"},
    {"ticker": "TSLA", "name": "Tesla, Inc.", "exchange": "NASDAQ", "sector": "Consumer Cyclical", "country": "USA"},
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ", "sector": "Technology", "country": "USA"},
    {"ticker": "AMZN", "name": "Amazon.com, Inc.", "exchange": "NASDAQ", "sector": "Consumer Cyclical", "country": "USA"},
    {"ticker": "META", "name": "Meta Platforms, Inc.", "exchange": "NASDAQ", "sector": "Technology", "country": "USA"},
    {"ticker": "NFLX", "name": "Netflix, Inc.", "exchange": "NASDAQ", "sector": "Communication Services", "country": "USA"},
    {"ticker": "AMD", "name": "Advanced Micro Devices, Inc.", "exchange": "NASDAQ", "sector": "Technology", "country": "USA"},
    {"ticker": "BABA", "name": "Alibaba Group Holding Limited", "exchange": "NYSE", "sector": "Consumer Cyclical", "country": "China"},
    {"ticker": "BTC-USD", "name": "Bitcoin USD", "exchange": "Cryptocurrency", "sector": "Crypto", "country": "Global"},
    {"ticker": "ETH-USD", "name": "Ethereum USD", "exchange": "Cryptocurrency", "sector": "Crypto", "country": "Global"}
]

@router.get("/search", response_model=List[Dict[str, Any]])
async def search_stocks(q: str = Query(..., description="Query string to search by name or ticker")):
    """
    Search assets in our directory by ticker symbol or company name.
    """
    query = q.strip().upper()
    if not query:
        return []
        
    matches = []
    for asset in POPULAR_STOCKS:
        if query in asset["ticker"] or query in asset["name"].upper():
            matches.append(asset)
            
    # If no standard matches found, yield a custom entry dynamically to keep it extremely flexible
    if not matches and len(query) >= 2:
        matches.append({
            "ticker": query,
            "name": f"{query} Stock Asset",
            "exchange": "Global Markets",
            "sector": "General Finance",
            "country": "Unknown"
        })
        
    return matches

@router.get("/{ticker}/history", response_model=List[Dict[str, Any]])
async def get_stock_history(ticker: str, period: str = Query("1y", description="Time span e.g. 1mo, 3mo, 6mo, 1y")):
    """
    Retrieves OHLCV price history for a given ticker.
    """
    ticker = ticker.upper()
    ingestion = DataIngestion()
    try:
        # Resolve history lookback dates
        import pandas as pd
        from datetime import datetime, timedelta
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        if period == "1mo":
            days = 30
        elif period == "3mo":
            days = 90
        elif period == "6mo":
            days = 180
        elif period == "2y":
            days = 730
        else: # default 1y
            days = 365
            
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        df = await ingestion.fetch_historical_prices(ticker, start_date=start_date, end_date=end_date)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No pricing historical logs found for symbol: {ticker}")
            
        # Format the historical rows for lightweight-charts compatibility
        history_list = []
        for _, row in df.iterrows():
            history_list.append({
                "time": int(row["date"].timestamp()), # Unix timestamp
                "date": row["date"].strftime("%Y-%m-%d"),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"])
            })
            
        return history_list
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch stock history for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await ingestion.close()
