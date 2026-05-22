import uvicorn
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import init_db
from app.services.scheduler import BackgroundScheduler

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("stockvision.main")

# Setup scheduler instance
scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown application cycles.
    """
    logger.info("Starting StockVision AI Predictor API...")
    
    # 1. Initialize databases and tables
    await init_db()
    
    # 2. Launch background ML training scheduler
    await scheduler.start()
    
    yield
    
    # 3. Shutdown background scheduler tasks on close
    logger.info("Stopping StockVision AI Predictor API...")
    await scheduler.stop()

# Initialize FastAPI App
app = FastAPI(
    title="StockVision AI API",
    description="Real-Time Stock Market Predictor Backend with LSTM, Transformers, and Sentiment analysis.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS Middleware
cors_origins = settings.parsed_cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Expose internal package modules (including sub-packages)
from app.api import stocks, sentiment, predictions, websocket

# Register Routers
app.include_router(stocks.router)
app.include_router(sentiment.router)
app.include_router(predictions.router)
app.include_router(websocket.router)

@app.get("/")
async def health_check():
    """Service health-check query"""
    return {
        "status": "online",
        "service": "StockVision AI Predictor",
        "version": "1.0.0",
        "env": settings.ENV,
        "debug": settings.DEBUG
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
