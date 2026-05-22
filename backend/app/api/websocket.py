import asyncio
import logging
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
from app.data.ingestion import DataIngestion
from app.services.predictor import PredictorOrchestrator

logger = logging.getLogger("stockvision.api.websocket")

router = APIRouter(tags=["websocket"])

class ConnectionManager:
    """
    Manages active WebSocket connections grouped by stock ticker.
    """
    def __init__(self):
        # Key: ticker symbol (upper), Value: list of active WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, ticker: str):
        await websocket.accept()
        ticker = ticker.upper()
        if ticker not in self.active_connections:
            self.active_connections[ticker] = []
        self.active_connections[ticker].append(websocket)
        logger.info(f"New client subscribed to stream: {ticker}. Total active: {len(self.active_connections[ticker])}")

    def disconnect(self, websocket: WebSocket, ticker: str):
        ticker = ticker.upper()
        if ticker in self.active_connections:
            if websocket in self.active_connections[ticker]:
                self.active_connections[ticker].remove(websocket)
                logger.info(f"Client unsubscribed from stream: {ticker}. Total active: {len(self.active_connections[ticker])}")
            if not self.active_connections[ticker]:
                del self.active_connections[ticker]

    async def broadcast_to_ticker(self, ticker: str, message: dict):
        ticker = ticker.upper()
        if ticker not in self.active_connections:
            return
            
        data = json.dumps(message)
        # Broadcast to all subscribed sockets
        for connection in list(self.active_connections[ticker]):
            try:
                await connection.send_text(data)
            except Exception as e:
                logger.warning(f"Error sending WebSocket broadcast. Client likely dead: {e}")
                self.disconnect(connection, ticker)

manager = ConnectionManager()

@router.websocket("/ws/{ticker}")
async def websocket_endpoint(websocket: WebSocket, ticker: str):
    ticker = ticker.upper()
    await manager.connect(websocket, ticker)
    
    ingestion = DataIngestion()
    orchestrator = PredictorOrchestrator()
    
    # Spawn background task to feed live updates every 5 seconds
    async def send_updates_loop():
        try:
            while True:
                # 1. Fetch live stock data and ensemble prediction
                live_price_data = await ingestion.fetch_live_price(ticker)
                
                # Fetch prediction details
                pred_data = await orchestrator.get_ensemble_prediction(ticker)
                
                # Assemble streaming payload
                payload = {
                    "type": "stock_update",
                    "ticker": ticker,
                    "price": live_price_data["price"],
                    "change": live_price_data["change"],
                    "change_pct": live_price_data["change_pct"],
                    "predicted_price": pred_data["predicted_price"],
                    "predicted_change_pct": pred_data["change_pct"],
                    "signal": pred_data["signal"],
                    "confidence": pred_data["confidence"],
                    "sentiment_score": pred_data["sentiment_score"],
                    "timestamp": live_price_data["timestamp"]
                }
                
                await websocket.send_text(json.dumps(payload))
                
                # Stream interval: 5 seconds
                await asyncio.sleep(5)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"WebSocket sender exception for {ticker}: {e}")
            
    # Run loop asynchronously
    sender_task = asyncio.create_task(send_updates_loop())
    
    try:
        # Keep connection open and listen for close/incoming messages
        while True:
            data = await websocket.receive_text()
            # Handle incoming ping-pong or ticker switch commands if sent by client
            try:
                msg = json.loads(data)
                if msg.get("action") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except Exception:
                pass
                
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from WebSocket stream: {ticker}")
    except Exception as e:
        logger.error(f"WebSocket client loop exception for {ticker}: {e}")
    finally:
        # Clean up tasks and unsubscribe
        sender_task.cancel()
        manager.disconnect(websocket, ticker)
        await ingestion.close()
