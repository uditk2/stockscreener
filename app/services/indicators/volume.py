"""
Volume technical indicators.
Calculates volume-based indicators like Volume SMA and OBV.
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


class VolumeIndicator(BaseIndicator):
    """Calculate volume indicators."""

    def calculate(self, close: np.ndarray, volume: np.ndarray) -> Dict[str, float]:
        """
        Calculate volume indicators.

        Args:
            close: Array of closing prices
            volume: Array of volume data

        Returns:
            Dictionary with volume indicators
        """
        indicators = {}

        try:
            # Volume SMA
            volume_series = pd.Series(volume)
            volume_sma = volume_series.rolling(20).mean()
            indicators['volume_sma'] = float(volume_sma.iloc[-1]) if not pd.isna(volume_sma.iloc[-1]) else None

            # OBV (On-Balance Volume)
            if self.talib_available:
                obv = talib.OBV(close, volume)
                indicators['obv'] = float(obv[-1]) if not np.isnan(obv[-1]) else None
            else:
                # OBV - Pandas implementation
                close_series = pd.Series(close)
                volume_series = pd.Series(volume)
                obv = (np.sign(close_series.diff()) * volume_series).fillna(0).cumsum()
                indicators['obv'] = float(obv.iloc[-1]) if not pd.isna(obv.iloc[-1]) else None

        except Exception as e:
            logger.error(f"Error calculating volume indicators: {e}")

        return indicators
