import os
import joblib
import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any
from sklearn.preprocessing import MinMaxScaler
from app.config import settings

class DataPreprocessor:
    """
    Handles feature scaling, target scaling, sequence creation, 
    and train/test splitting for StockVision models.
    """
    def __init__(self, lookback_steps: int = 60, forecast_horizon: int = 1):
        self.lookback_steps = lookback_steps
        self.forecast_horizon = forecast_horizon
        self.feature_scaler = MinMaxScaler(feature_range=(0, 1))
        self.target_scaler = MinMaxScaler(feature_range=(0, 1))
        self.feature_cols: List[str] = []
        self.is_fitted = False

    def fit_transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fits the scalers on the given DataFrame and returnsscaled arrays.
        Features include OHLCV + technical indicators + rolling sentiment.
        Target is the 'close' price.
        """
        # Determine features (exclude 'ticker', 'date')
        exclude_cols = {'ticker', 'date'}
        self.feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Ensure 'close' is in features
        if 'close' not in self.feature_cols:
            raise ValueError("DataFrame must contain 'close' column to fit target scaling.")

        # Scaler fit and transform
        feature_data = df[self.feature_cols].values
        target_data = df[['close']].values

        scaled_features = self.feature_scaler.fit_transform(feature_data)
        scaled_target = self.target_scaler.fit_transform(target_data)

        self.is_fitted = True
        return scaled_features, scaled_target

    def transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Transforms features and target using already-fitted scalers."""
        if not self.is_fitted:
            raise ValueError("Preprocessor has not been fitted yet!")
        
        feature_data = df[self.feature_cols].values
        target_data = df[['close']].values

        scaled_features = self.feature_scaler.transform(feature_data)
        scaled_target = self.target_scaler.transform(target_data)
        return scaled_features, scaled_target

    def inverse_transform_target(self, scaled_target: np.ndarray) -> np.ndarray:
        """Converts scaled target predictions back to actual stock price values."""
        if not self.is_fitted:
            raise ValueError("Preprocessor has not been fitted yet!")
        return self.target_scaler.inverse_transform(scaled_target)

    def create_sequences(self, scaled_features: np.ndarray, scaled_target: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Constructs windowed sequences for sequential model inputs.
        X shape: (samples, lookback_steps, num_features)
        y shape: (samples, forecast_horizon)
        """
        X, y = [], []
        total_len = len(scaled_features)
        
        # Ensure we have enough data
        limit = total_len - self.lookback_steps - self.forecast_horizon + 1
        if limit <= 0:
            return np.array([]), np.array([])

        for i in range(limit):
            X.append(scaled_features[i : i + self.lookback_steps])
            # Next close price
            y.append(scaled_target[i + self.lookback_steps : i + self.lookback_steps + self.forecast_horizon, 0])

        return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)

    def save(self, filepath: str):
        """Saves the preprocessor states to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        state = {
            "lookback_steps": self.lookback_steps,
            "forecast_horizon": self.forecast_horizon,
            "feature_scaler": self.feature_scaler,
            "target_scaler": self.target_scaler,
            "feature_cols": self.feature_cols,
            "is_fitted": self.is_fitted
        }
        joblib.dump(state, filepath)

    @classmethod
    def load(cls, filepath: str) -> "DataPreprocessor":
        """Loads a preprocessor state from disk."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No preprocessor file found at {filepath}")
        state = joblib.load(filepath)
        preprocessor = cls(state["lookback_steps"], state["forecast_horizon"])
        preprocessor.feature_scaler = state["feature_scaler"]
        preprocessor.target_scaler = state["target_scaler"]
        preprocessor.feature_cols = state["feature_cols"]
        preprocessor.is_fitted = state["is_fitted"]
        return preprocessor
