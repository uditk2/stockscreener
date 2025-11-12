"""
Moving Averages technical indicators.
Calculates SMA and EMA indicators.
"""
import pandas as pd
import numpy as np
from typing import Dict
import logging

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False

from .base import BaseIndicator

logger = logging.getLogger(__name__)


class MovingAveragesIndicator(BaseIndicator):
    """Calculate various moving averages."""

    def calculate(self, close: np.ndarray) -> Dict[str, float]:
        """
        Calculate various moving averages.

        Args:
            close: Array of closing prices

        Returns:
            Dictionary with moving average indicators
        """
        indicators = {}

        try:
            if self.talib_available:
                # Simple Moving Averages
                sma_20 = talib.SMA(close, timeperiod=20)
                sma_50 = talib.SMA(close, timeperiod=50)
                sma_200 = talib.SMA(close, timeperiod=200)

                # Exponential Moving Averages
                ema_12 = talib.EMA(close, timeperiod=12)
                ema_26 = talib.EMA(close, timeperiod=26)

                indicators['sma_20'] = float(sma_20[-1]) if not np.isnan(sma_20[-1]) else None
                indicators['sma_50'] = float(sma_50[-1]) if not np.isnan(sma_50[-1]) else None
                indicators['sma_200'] = float(sma_200[-1]) if not np.isnan(sma_200[-1]) else None
                indicators['ema_12'] = float(ema_12[-1]) if not np.isnan(ema_12[-1]) else None
                indicators['ema_26'] = float(ema_26[-1]) if not np.isnan(ema_26[-1]) else None
            else:
                # Pandas implementation
                close_series = pd.Series(close)
                indicators['sma_20'] = float(close_series.rolling(20).mean().iloc[-1]) if len(close) >= 20 else None
                indicators['sma_50'] = float(close_series.rolling(50).mean().iloc[-1]) if len(close) >= 50 else None
                indicators['sma_200'] = float(close_series.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None
                indicators['ema_12'] = float(close_series.ewm(span=12).mean().iloc[-1]) if len(close) >= 12 else None
                indicators['ema_26'] = float(close_series.ewm(span=26).mean().iloc[-1]) if len(close) >= 26 else None

        except Exception as e:
            logger.error(f"Error calculating moving averages: {e}")

        return indicators
