import { useEffect, useState, useRef, useCallback } from 'react';
import { WebSocketPayload } from '../types';

export const useWebSocket = (ticker: string) => {
  const [data, setData] = useState<WebSocketPayload | null>(null);
  const [connected, setConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const connect = useCallback(() => {
    if (!ticker) return;

    // Close any prior connections
    if (socketRef.current) {
      socketRef.current.close();
    }

    const wsUrl = `ws://localhost:8000/ws/${ticker.toUpperCase()}`;
    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      reconnectAttemptsRef.current = 0;
      console.log(`WebSocket connected to stream: ${ticker}`);
    };

    ws.onmessage = (event) => {
      try {
        const payload: WebSocketPayload = JSON.parse(event.data);
        if (payload.type === 'stock_update') {
          setData(payload);
        }
      } catch (err) {
        console.error('Error parsing WS message:', err);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      // Exponential backoff reconnect
      const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
      reconnectAttemptsRef.current += 1;
      
      console.log(`WebSocket disconnected. Retrying in ${delay / 1000}s...`);
      reconnectTimeoutRef.current = window.setTimeout(() => {
        connect();
      }, delay);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      ws.close();
    };
  }, [ticker]);

  useEffect(() => {
    connect();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [ticker, connect]);

  return { data, connected };
};
