import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from app.data.ingestion import DataIngestion
from app.models.finbert_sentiment import FinBertSentiment

logger = logging.getLogger("stockvision.api.sentiment")

router = APIRouter(prefix="/api/sentiment", tags=["sentiment"])

@router.get("/{ticker}", response_model=Dict[str, Any])
async def get_sentiment_analysis(ticker: str):
    """
    Downloads active news for the ticker and processes their titles through NLP sentiment classification.
    """
    ticker = ticker.upper()
    ingestion = DataIngestion()
    sentiment_engine = FinBertSentiment()
    
    try:
        # 1. Download ticker articles
        news_items = await ingestion.fetch_ticker_news(ticker)
        
        if not news_items:
            return {
                "ticker": ticker,
                "sentiment": {"label": "neutral", "confidence": 1.0, "composite_score": 0.0},
                "news_feed": [],
                "articles_count": 0
            }

        # 2. Extract headline texts and analyze them in batch
        headlines = [item["headline"] for item in news_items if item.get("headline")]
        
        if not headlines:
            raise HTTPException(status_code=404, detail=f"No article headlines available for analysis on {ticker}")
            
        # Run batch NLP prediction
        sentiment_scores = sentiment_engine.analyze_batch(headlines)
        
        # 3. Assemble response payload with individual headline details
        analyzed_feed = []
        for i, item in enumerate(news_items):
            if i >= len(sentiment_scores):
                break
            score_data = sentiment_scores[i]
            
            analyzed_feed.append({
                "headline": item["headline"],
                "source": item.get("source", "Financial News"),
                "url": item.get("url", "#"),
                "published_at": item.get("published_at", ""),
                "score": score_data["composite_score"],
                "label": score_data["label"],
                "confidence": score_data["confidence"]
            })
            
        # Calculate overall aggregate metric
        agg_result = sentiment_engine.aggregate_sentiment(headlines)
        
        return {
            "ticker": ticker,
            "sentiment": agg_result,
            "news_feed": analyzed_feed,
            "articles_count": len(analyzed_feed)
        }
        
    except Exception as e:
        logger.error(f"Error executing news sentiment analysis for {ticker}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")
    finally:
        await ingestion.close()
