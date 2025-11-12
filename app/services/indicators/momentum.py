"""
Momentum technical indicators.
Calculates RSI, MACD, and Stochastic indicators.
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


class MomentumIndicator(BaseIndicator):
    """Calculate momentum indicators."""

    def calculate(self, close: np.ndarray) -> Dict[str, float]:
        """
        Calculate momentum indicators.

        Args:
            close: Array of closing prices

        Returns:
            Dictionary with momentum indicators
        """
        indicators = {}

        try:
            if self.talib_available:
                # RSI
                rsi = talib.RSI(close, timeperiod=14)
                indicators['rsi'] = float(rsi[-1]) if not np.isnan(rsi[-1]) else None

                # MACD
                macd, signal, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
                indicators['macd'] = float(macd[-1]) if not np.isnan(macd[-1]) else None
                indicators['macd_signal'] = float(signal[-1]) if not np.isnan(signal[-1]) else None
                indicators['macd_histogram'] = float(hist[-1]) if not np.isnan(hist[-1]) else None

                # Stochastic
                slowk, slowd = talib.STOCH(close, close, close, fastk_period=14, slowk_period=3, slowd_period=3)
                indicators['stochastic_k'] = float(slowk[-1]) if not np.isnan(slowk[-1]) else None
                indicators['stochastic_d'] = float(slowd[-1]) if not np.isnan(slowd[-1]) else None

            else:
                # RSI - Pandas implementation
                delta = pd.Series(close).diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                indicators['rsi'] = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None

                # MACD - Pandas implementation
                close_series = pd.Series(close)
                ema_12 = close_series.ewm(span=12).mean()
                ema_26 = close_series.ewm(span=26).mean()
                macd = ema_12 - ema_26
                signal = macd.ewm(span=9).mean()
                hist = macd - signal

                indicators['macd'] = float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else None
                indicators['macd_signal'] = float(signal.iloc[-1]) if not pd.isna(signal.iloc[-1]) else None
                indicators['macd_histogram'] = float(hist.iloc[-1]) if not pd.isna(hist.iloc[-1]) else None

        except Exception as e:
            logger.error(f"Error calculating momentum indicators: {e}")

        return indicators
