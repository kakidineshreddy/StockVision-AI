import sys
import asyncio
import argparse
import logging

# Ensure parent directory is in sys.path
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.predictor import PredictorOrchestrator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("train_transformer_cli")

async def main():
    parser = argparse.ArgumentParser(description="Train Transformer model for StockVision AI")
    parser.add_argument("--ticker", type=str, default="AAPL", help="Stock ticker symbol (default: AAPL)")
    args = parser.parse_args()
    
    ticker = args.ticker.upper()
    logger.info(f"Starting standalone Transformer training for {ticker}...")
    
    orchestrator = PredictorOrchestrator()
    result = await orchestrator.train_models_for_ticker(ticker)
    
    if result["status"] == "success":
        logger.info(f"Successfully trained models! Metrics: {result}")
    else:
        logger.error(f"Failed to train models: {result.get('message')}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
