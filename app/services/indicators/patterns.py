"""
Pattern detection for technical analysis.
Detects common chart patterns like Golden Cross and Death Cross.
"""
import pandas as pd
from typing import Dict
import logging

from .base import BaseIndicator

logger = logging.getLogger(__name__)


class PatternDetector(BaseIndicator):
    """Detect common chart patterns."""

    def detect(self, df: pd.DataFrame) -> Dict[str, bool]:
        """
        Detect common chart patterns.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with detected patterns
        """
        patterns = {}

        try:
            close = df['Close'].values

            # Golden Cross (50 SMA crosses above 200 SMA)
            if len(close) >= 200:
                sma_50 = pd.Series(close).rolling(50).mean()
                sma_200 = pd.Series(close).rolling(200).mean()

                if len(sma_50) > 1 and len(sma_200) > 1:
                    patterns['golden_cross'] = (
                        sma_50.iloc[-2] <= sma_200.iloc[-2] and
                        sma_50.iloc[-1] > sma_200.iloc[-1]
                    )

            # Death Cross (50 SMA crosses below 200 SMA)
            if len(close) >= 200:
                sma_50 = pd.Series(close).rolling(50).mean()
                sma_200 = pd.Series(close).rolling(200).mean()

                if len(sma_50) > 1 and len(sma_200) > 1:
                    patterns['death_cross'] = (
                        sma_50.iloc[-2] >= sma_200.iloc[-2] and
                        sma_50.iloc[-1] < sma_200.iloc[-1]
                    )

        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")

        return patterns
