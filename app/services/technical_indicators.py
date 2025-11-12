"""
Technical indicators calculation service.
Uses pandas and TA-Lib for calculating various technical indicators.
"""
import pandas as pd
import numpy as np
from typing import Optional, Dict
import logging

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    logging.warning("TA-Lib not available, using pandas implementations")

logger = logging.getLogger(__name__)


class TechnicalIndicatorService:
    """
    Service for calculating technical indicators.
    Responsible only for technical analysis calculations.
    """

    def __init__(self):
        """Initialize the technical indicator service."""
        self.talib_available = TALIB_AVAILABLE

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
            indicators.update(self._calculate_moving_averages(close))

            # Momentum Indicators
            indicators.update(self._calculate_momentum_indicators(close))

            # Volatility Indicators
            indicators.update(self._calculate_volatility_indicators(df))

            # Volume Indicators
            indicators.update(self._calculate_volume_indicators(close, volume))

            # Trend Indicators
            indicators.update(self._calculate_trend_indicators(high, low, close))

            logger.debug(f"Calculated {len(indicators)} indicators")
            return indicators

        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return None

    def _calculate_moving_averages(self, close: np.ndarray) -> Dict[str, float]:
        """Calculate various moving averages."""
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

    def _calculate_momentum_indicators(self, close: np.ndarray) -> Dict[str, float]:
        """Calculate momentum indicators."""
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

    def _calculate_volatility_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate volatility indicators."""
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

    def _calculate_volume_indicators(self, close: np.ndarray, volume: np.ndarray) -> Dict[str, float]:
        """Calculate volume indicators."""
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

    def _calculate_trend_indicators(self, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> Dict[str, float]:
        """Calculate trend indicators."""
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

    def detect_patterns(self, df: pd.DataFrame) -> Dict[str, bool]:
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
