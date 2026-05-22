import pandas as pd
import numpy as np

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate 25 financial technical indicators and engineered features.
    Required indicators: SMA(20,50), EMA(12,26), MACD, RSI(14), Bollinger Bands, 
    ADX, Stochastic, ATR, OBV, Williams %R, returns, log returns, volatility.
    
    Parameters:
        df: pd.DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
        
    Returns:
        pd.DataFrame containing original columns plus 25 engineered features.
    """
    df = df.copy()
    
    # 1. Price Features
    df['returns'] = df['close'].pct_change().fillna(0)
    df['log_returns'] = np.log(df['close'] / df['close'].shift(1)).fillna(0)
    df['volatility'] = df['returns'].rolling(window=10).std().fillna(0)
    df['price_range'] = (df['high'] - df['low']) / df['close']

    # 2. SMAs & EMAs
    df['sma_20'] = df['close'].rolling(window=20).mean().fillna(df['close'])
    df['sma_50'] = df['close'].rolling(window=50).mean().fillna(df['close'])
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean().fillna(df['close'])
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean().fillna(df['close'])

    # 3. MACD (Moving Average Convergence Divergence)
    df['macd_line'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd_line'].ewm(span=9, adjust=False).mean().fillna(0)
    df['macd_hist'] = df['macd_line'] - df['macd_signal']

    # 4. RSI (Relative Strength Index)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().fillna(0)
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().fillna(0)
    rs = gain / np.where(loss == 0, 1e-9, loss)
    df['rsi_14'] = (100 - (100 / (1 + rs))).fillna(50)

    # 5. Bollinger Bands
    bb_std = df['close'].rolling(window=20).std().fillna(0)
    df['bb_mid'] = df['sma_20']
    df['bb_high'] = df['bb_mid'] + (2 * bb_std)
    df['bb_low'] = df['bb_mid'] - (2 * bb_std)

    # 6. Average True Range (ATR)
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift(1))
    low_close = np.abs(df['low'] - df['close'].shift(1))
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr_14'] = tr.rolling(window=14).mean().fillna(tr.mean() if not tr.empty else 0)

    # 7. Williams %R
    highest_high = df['high'].rolling(window=14).max().fillna(df['high'])
    lowest_low = df['low'].rolling(window=14).min().fillna(df['low'])
    denom = highest_high - lowest_low
    df['williams_r'] = ((-100) * (highest_high - df['close']) / np.where(denom == 0, 1e-9, denom)).fillna(-50)

    # 8. Stochastic Oscillator
    df['stoch_k'] = ((df['close'] - lowest_low) / np.where(denom == 0, 1e-9, denom) * 100).fillna(50)
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean().fillna(50)

    # 9. On Balance Volume (OBV)
    obv = [0]
    closes = df['close'].values
    volumes = df['volume'].values
    for i in range(1, len(df)):
        if closes[i] > closes[i-1]:
            obv.append(obv[-1] + volumes[i])
        elif closes[i] < closes[i-1]:
            obv.append(obv[-1] - volumes[i])
        else:
            obv.append(obv[-1])
    df['obv'] = obv

    # 10. Volume Features
    df['volume_sma_20'] = df['volume'].rolling(window=20).mean().fillna(df['volume'])
    df['volume_ratio'] = df['volume'] / np.where(df['volume_sma_20'] == 0, 1e-9, df['volume_sma_20'])

    # 11. Average Directional Index (ADX)
    # Simple ADX implementation
    plus_dm = df['high'].diff()
    minus_dm = df['low'].diff()
    plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0)
    minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0)
    
    tr_sum = tr.rolling(window=14).sum().fillna(1.0)
    plus_di = 100 * (pd.Series(plus_dm).rolling(window=14).sum().fillna(0) / tr_sum)
    minus_di = 100 * (pd.Series(minus_dm).rolling(window=14).sum().fillna(0) / tr_sum)
    
    dx = 100 * np.abs(plus_di - minus_di) / np.where((plus_di + minus_di) == 0, 1e-9, (plus_di + minus_di))
    df['adx_14'] = pd.Series(dx).rolling(window=14).mean().fillna(25).values

    # 12. Sentiment Placeholder (will be populated dynamically by ingestion)
    # Ensure column exists
    if 'sentiment' not in df.columns:
        df['sentiment'] = 0.0
    
    df['sentiment_rolling_5'] = df['sentiment'].rolling(window=5, min_periods=1).mean().fillna(0.0)

    # Clean any remaining NaNs to prevent PyTorch loading issues
    df = df.fillna(0)

    return df
