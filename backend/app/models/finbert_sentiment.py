import logging
from typing import List, Dict, Any, Tuple
from textblob import TextBlob

logger = logging.getLogger("stockvision.sentiment")

# Try to import transformers, set a flag if unavailable
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logger.warning("HuggingFace 'transformers' library not found. Falling back to local NLP engine.")

class FinBertSentiment:
    """
    NLP sentiment analysis using HuggingFace ProsusAI/finbert with a high-performance TextBlob fallback.
    """
    def __init__(self, use_fallback: bool = False):
        self.model_name = "ProsusAI/finbert"
        self.pipeline = None
        self.fallback = use_fallback or not HAS_TRANSFORMERS
        
        if not self.fallback:
            try:
                logger.info("Initializing HuggingFace FinBERT pipeline (ProsusAI/finbert)...")
                # Initialize tokenizer and classifier model
                tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
                
                # Check for CUDA availability
                device = 0 if hasattr(model, 'device') and model.device.type == 'cuda' else -1
                
                self.pipeline = pipeline(
                    "sentiment-analysis",
                    model=model,
                    tokenizer=tokenizer,
                    device=device
                )
                logger.info("HuggingFace FinBERT pipeline loaded successfully.")
            except Exception as e:
                logger.warning(f"Failed to load FinBERT: {e}. Switching to TextBlob NLP fallback engine.")
                self.fallback = True

    def analyze_headline(self, headline: str) -> Dict[str, Any]:
        """
        Analyzes a single news headline.
        Returns: label, confidence, and composite_score (-1 to 1).
        """
        if not headline:
            return {"label": "neutral", "confidence": 1.0, "composite_score": 0.0}

        # Use HuggingFace pipeline if active
        if not self.fallback and self.pipeline:
            try:
                results = self.pipeline(headline)
                if results:
                    res = results[0]
                    label = res['label'].lower() # positive, negative, neutral
                    confidence = float(res['score'])
                    
                    # Convert label and confidence to composite score (-1 to 1)
                    if label == "positive":
                        composite_score = confidence
                    elif label == "negative":
                        composite_score = -confidence
                    else:
                        composite_score = 0.0
                        
                    return {
                        "label": label,
                        "confidence": confidence,
                        "composite_score": composite_score
                    }
            except Exception as e:
                logger.error(f"FinBERT single inference failed: {e}. Using fallback.")
                
        # High-performance TextBlob fallback
        blob = TextBlob(headline)
        polarity = blob.sentiment.polarity  # Range -1 to 1
        subjectivity = blob.sentiment.subjectivity # Range 0 to 1
        
        # Classify polarity
        if polarity > 0.05:
            label = "positive"
            confidence = min(0.5 + abs(polarity) / 2 + subjectivity / 10, 0.99)
        elif polarity < -0.05:
            label = "negative"
            confidence = min(0.5 + abs(polarity) / 2 + subjectivity / 10, 0.99)
        else:
            label = "neutral"
            confidence = min(0.8 + subjectivity / 5, 0.99)
            
        return {
            "label": label,
            "confidence": confidence,
            "composite_score": polarity
        }

    def analyze_batch(self, headlines: List[str]) -> List[Dict[str, Any]]:
        """
        Analyzes a batch of headlines in one pass.
        """
        if not headlines:
            return []
            
        if not self.fallback and self.pipeline:
            try:
                results = self.pipeline(headlines)
                parsed = []
                for res in results:
                    label = res['label'].lower()
                    confidence = float(res['score'])
                    if label == "positive":
                        composite_score = confidence
                    elif label == "negative":
                        composite_score = -confidence
                    else:
                        composite_score = 0.0
                    parsed.append({
                        "label": label,
                        "confidence": confidence,
                        "composite_score": composite_score
                    })
                return parsed
            except Exception as e:
                logger.error(f"FinBERT batch inference failed: {e}. Using individual fallback loops.")
                
        return [self.analyze_headline(h) for h in headlines]

    def aggregate_sentiment(self, headlines: List[str]) -> Dict[str, Any]:
        """
        Aggregates sentiment details across multiple headlines for a single composite score.
        """
        if not headlines:
            return {"label": "neutral", "confidence": 1.0, "composite_score": 0.0}
            
        results = self.analyze_batch(headlines)
        
        total_score = 0.0
        pos_count = 0
        neg_count = 0
        neu_count = 0
        confidence_sum = 0.0
        
        for res in results:
            total_score += res["composite_score"]
            confidence_sum += res["confidence"]
            
            label = res["label"]
            if label == "positive":
                pos_count += 1
            elif label == "negative":
                neg_count += 1
            else:
                neu_count += 1
                
        n = len(headlines)
        avg_score = total_score / n
        avg_confidence = confidence_sum / n
        
        # Decide collective label
        if pos_count > neg_count and pos_count > neu_count:
            agg_label = "positive"
        elif neg_count > pos_count and neg_count > neu_count:
            agg_label = "negative"
        else:
            agg_label = "neutral"
            
        return {
            "label": agg_label,
            "confidence": avg_confidence,
            "composite_score": avg_score
        }
