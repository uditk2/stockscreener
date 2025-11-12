"""
Trend technical indicators.
Calculates ADX and other trend indicators.
"""
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


class TrendIndicator(BaseIndicator):
    """Calculate trend indicators."""

    def calculate(self, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> Dict[str, float]:
        """
        Calculate trend indicators.

        Args:
            high: Array of high prices
            low: Array of low prices
            close: Array of closing prices

        Returns:
            Dictionary with trend indicators
        """
        indicators = {}

        try:
            if self.talib_available:
                # ADX (Average Directional Index)
                adx = talib.ADX(high, low, close, timeperiod=14)
                indicators['adx'] = float(adx[-1]) if not np.isnan(adx[-1]) else None
            else:
                # ADX calculation is complex, skip for now in pandas-only mode
                indicators['adx'] = None

        except Exception as e:
            logger.error(f"Error calculating trend indicators: {e}")

        return indicators
