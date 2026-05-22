import asyncio
import logging
from typing import List
from app.services.predictor import PredictorOrchestrator

logger = logging.getLogger("stockvision.scheduler")

class BackgroundScheduler:
    """
    Manages automated background tasks like model retraining and caching.
    """
    def __init__(self, tickers: List[str] = None):
        self.tickers = tickers or ["AAPL", "MSFT", "GOOG", "TSLA", "NVDA"]
        self.orchestrator = PredictorOrchestrator()
        self.is_running = False
        self.task = None

    async def start(self):
        """Starts the periodic background scheduler task"""
        if self.is_running:
            return
        self.is_running = True
        self.task = asyncio.create_task(self._scheduler_loop())
        logger.info("Background retraining scheduler active.")

    async def stop(self):
        """Gracefully stops the scheduler"""
        if not self.is_running:
            return
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Background retraining scheduler stopped.")

    async def _scheduler_loop(self):
        """
        Runs periodic retraining loops.
        Retrains models for active tickers every 24 hours (86400 seconds).
        Initial pass triggers 10 seconds after boot to fill cold caches.
        """
        await asyncio.sleep(10) # boot delay to prioritize main HTTP processes
        while self.is_running:
            logger.info("Starting automated periodic retraining run...")
            for ticker in self.tickers:
                if not self.is_running:
                    break
                try:
                    logger.info(f"Triggering background retrain for ticker: {ticker}")
                    # Fit scales and optimize weights
                    res = await self.orchestrator.train_models_for_ticker(ticker)
                    logger.info(f"Retraining status for {ticker}: {res.get('status')}")
                except Exception as e:
                    logger.error(f"Failed background retraining loop for {ticker}: {e}")
                
                # Small cooling pause between training tickers to prevent high CPU congestion
                await asyncio.sleep(5)
                
            # Sleep for 24 hours
            try:
                await asyncio.sleep(86400)
            except asyncio.CancelledError:
                break
