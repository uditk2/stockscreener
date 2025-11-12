"""
Technical indicators calculation service.
Uses pandas and TA-Lib for calculating various technical indicators.
"""
import pandas as pd
from typing import Optional, Dict
import logging

from .moving_averages import MovingAveragesIndicator
from .momentum import MomentumIndicator
from .volatility import VolatilityIndicator
from .volume import VolumeIndicator
from .trend import TrendIndicator
from .patterns import PatternDetector

logger = logging.getLogger(__name__)


class TechnicalIndicatorService:
    """
    Service for calculating technical indicators.
    Responsible only for technical analysis calculations.
    """

    def __init__(self):
        """Initialize the technical indicator service."""
        self.moving_averages = MovingAveragesIndicator()
        self.momentum = MomentumIndicator()
        self.volatility = VolatilityIndicator()
        self.volume = VolumeIndicator()
        self.trend = TrendIndicator()
        self.pattern_detector = PatternDetector()

    def calculate_all_indicators(self, df: pd.DataFrame) -> Optional[Dict[str, float]]:
        """
        Calculate all technical indicators for the given price data.

        Args:
            df: DataFrame with OHLCV data (Open, High, Low, Close, Volume)

        Returns:
            Dictionary with all calculated indicators or None if failed
        """
        try:
            if df is None or df.empty:
                logger.warning("Empty dataframe provided")
                return None

            indicators = {}

            # Get the most recent values
            close = df['Close'].values
            high = df['High'].values
            low = df['Low'].values
            volume = df['Volume'].values

            # Moving Averages
            indicators.update(self.moving_averages.calculate(close))

            # Momentum Indicators
            indicators.update(self.momentum.calculate(close))

            # Volatility Indicators
            indicators.update(self.volatility.calculate(df))

            # Volume Indicators
            indicators.update(self.volume.calculate(close, volume))

            # Trend Indicators
            indicators.update(self.trend.calculate(high, low, close))

            logger.debug(f"Calculated {len(indicators)} indicators")
            return indicators

        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return None

    def detect_patterns(self, df: pd.DataFrame) -> Dict[str, bool]:
        """
        Detect common chart patterns.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with detected patterns
        """
        return self.pattern_detector.detect(df)
