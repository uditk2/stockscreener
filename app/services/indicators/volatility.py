"""
Volatility technical indicators.
Calculates Bollinger Bands and ATR indicators.
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


class VolatilityIndicator(BaseIndicator):
    """Calculate volatility indicators."""

    def calculate(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate volatility indicators.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with volatility indicators
        """
        indicators = {}

        try:
            close = df['Close'].values
            high = df['High'].values
            low = df['Low'].values

            if self.talib_available:
                # Bollinger Bands
                upper, middle, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
                indicators['bollinger_upper'] = float(upper[-1]) if not np.isnan(upper[-1]) else None
                indicators['bollinger_middle'] = float(middle[-1]) if not np.isnan(middle[-1]) else None
                indicators['bollinger_lower'] = float(lower[-1]) if not np.isnan(lower[-1]) else None

                # ATR
                atr = talib.ATR(high, low, close, timeperiod=14)
                indicators['atr'] = float(atr[-1]) if not np.isnan(atr[-1]) else None

            else:
                # Bollinger Bands - Pandas implementation
                close_series = pd.Series(close)
                sma = close_series.rolling(20).mean()
                std = close_series.rolling(20).std()

                indicators['bollinger_upper'] = float((sma + 2 * std).iloc[-1]) if not pd.isna((sma + 2 * std).iloc[-1]) else None
                indicators['bollinger_middle'] = float(sma.iloc[-1]) if not pd.isna(sma.iloc[-1]) else None
                indicators['bollinger_lower'] = float((sma - 2 * std).iloc[-1]) if not pd.isna((sma - 2 * std).iloc[-1]) else None

                # ATR - Pandas implementation
                high_low = pd.Series(high) - pd.Series(low)
                high_close = np.abs(pd.Series(high) - pd.Series(close).shift())
                low_close = np.abs(pd.Series(low) - pd.Series(close).shift())
                ranges = pd.concat([high_low, high_close, low_close], axis=1)
                true_range = ranges.max(axis=1)
                atr = true_range.rolling(14).mean()

                indicators['atr'] = float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else None

        except Exception as e:
            logger.error(f"Error calculating volatility indicators: {e}")

        return indicators
