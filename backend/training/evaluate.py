import sys
import asyncio
import argparse
import logging
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Ensure parent directory is in sys.path
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.predictor import PredictorOrchestrator
from app.services.backtester import WalkForwardBacktester

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("evaluate_cli")

async def main():
    parser = argparse.ArgumentParser(description="Evaluate StockVision models")
    parser.add_argument("--ticker", type=str, default="AAPL", help="Stock ticker symbol")
    parser.add_argument("--days", type=int, default=252, help="Testing window days")
    args = parser.parse_args()
    
    ticker = args.ticker.upper()
    logger.info(f"Running comprehensive model evaluation and metrics aggregation for {ticker}...")
    
    # 1. Run backtester walk-forward
    backtester = WalkForwardBacktester()
    res = await backtester.run_backtest(ticker, days=args.days)
    
    logger.info("=====================================================================")
    logger.info(f"EVALUATION RESULTS FOR {ticker} OVER THE LAST {args.days} TRADING DAYS")
    logger.info("=====================================================================")
    logger.info(f"Ensemble Total Return:      {res['total_return']:.2f}%")
    logger.info(f"Buy-and-Hold Benchmark:     {res['buy_and_hold_return']:.2f}%")
    logger.info(f"Annualized Sharpe Ratio:    {res['sharpe_ratio']:.3f}")
    logger.info(f"Max Portfolio Drawdown:     {res['max_drawdown']:.2f}%")
    logger.info(f"Ensemble Signal Win Rate:   {res['win_rate']:.2f}%")
    
    # Estimate standard RMSE and MAE relative to prices
    curve = res["equity_curve"]
    if len(curve) > 1:
        p_vals = np.array([pt["portfolio_value"] for pt in curve])
        b_vals = np.array([pt["benchmark_value"] for pt in curve])
        
        # Absolute scale error proxy
        rmse = np.sqrt(mean_squared_error(p_vals, b_vals))
        mae = mean_absolute_error(p_vals, b_vals)
        logger.info(f"Estimated RMSE vs Benchmark: {rmse:.4f}")
        logger.info(f"Estimated MAE vs Benchmark:  {mae:.4f}")
    logger.info("=====================================================================")

if __name__ == "__main__":
    asyncio.run(main())
