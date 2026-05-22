import logging
from typing import Dict, Any

logger = logging.getLogger("stockvision.ensemble")

class EnsembleCombiner:
    """
    Combines LSTM, Transformer, and NLP sentiment predictions into a single, unified trade advisory.
    Weights: 40% LSTM, 40% Transformer, 20% News Sentiment.
    """
    def __init__(self, lstm_weight: float = 0.4, transformer_weight: float = 0.4, sentiment_weight: float = 0.2):
        self.lstm_weight = lstm_weight
        self.transformer_weight = transformer_weight
        self.sentiment_weight = sentiment_weight

    def combine(
        self, 
        current_price: float, 
        lstm_price: float, 
        transformer_price: float, 
        sentiment_score: float
    ) -> Dict[str, Any]:
        """
        Runs the weighted ensemble combination.
        
        Parameters:
            current_price: float - Yesterday's close or latest traded price
            lstm_price: float - LSTM model predicted next-close price
            transformer_price: float - Transformer model predicted next-close price
            sentiment_score: float - NLP aggregate sentiment score (-1.0 to 1.0)
            
        Returns:
            Dict containing predicted_price, change_pct, signal, confidence.
        """
        # Sentiment impact represents the sentiment adjustment to current price.
        # Max sentiment (+1.0) could represent up to 2% upward momentum lift.
        sentiment_impact_pct = sentiment_score * 0.02
        sentiment_equivalent_price = current_price * (1.0 + sentiment_impact_pct)

        # 1. Weighted Price forecast
        predicted_price = (
            self.lstm_weight * lstm_price +
            self.transformer_weight * transformer_price +
            self.sentiment_weight * sentiment_equivalent_price
        )
        
        # Avoid mathematical dividing division anomalies
        if current_price <= 0:
            current_price = 1e-9

        # 2. Predicted Percentage Change
        change_pct = ((predicted_price - current_price) / current_price) * 100.0

        # 3. Model Consensus & Directional Agreement
        lstm_dir = 1 if lstm_price > current_price else -1
        trans_dir = 1 if transformer_price > current_price else -1
        sentiment_dir = 1 if sentiment_score > 0.05 else (-1 if sentiment_score < -0.05 else 0)
        
        # Directional Consensus Index (0.5 to 1.0)
        # Full agreement: both models agree + sentiment aligns.
        agreement_factor = 0.0
        if lstm_dir == trans_dir:
            agreement_factor += 0.6  # High model agreement
            if sentiment_dir == lstm_dir:
                agreement_factor += 0.4 # Sentiment supports model direction
            else:
                agreement_factor += 0.2
        else:
            agreement_factor += 0.4  # Split model agreement
            if sentiment_dir != 0:
                agreement_factor += 0.2
                
        confidence = min(agreement_factor, 1.0)

        # 4. Signal Generation (BUY / SELL / HOLD)
        # Thresholds: BUY if change_pct >= 1.0% and consensus is bullish.
        # SELL if change_pct <= -1.0% and consensus is bearish.
        # Otherwise HOLD.
        if change_pct >= 1.0 and lstm_dir == 1 and trans_dir == 1:
            signal = "BUY"
        elif change_pct <= -1.0 and lstm_dir == -1 and trans_dir == -1:
            signal = "SELL"
        else:
            # Check for strong sentiment overrides
            if change_pct >= 0.5 and sentiment_score > 0.4:
                signal = "BUY"
            elif change_pct <= -0.5 and sentiment_score < -0.4:
                signal = "SELL"
            else:
                signal = "HOLD"

        return {
            "current_price": float(current_price),
            "predicted_price": float(predicted_price),
            "change_pct": float(change_pct),
            "signal": signal,
            "confidence": float(confidence),
            "sentiment_score": float(sentiment_score)
        }
