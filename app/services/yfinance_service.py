"""
YFinance service for fetching historical stock data.
Implements rate limiting to avoid API throttling.
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging
from app.config import settings
from app.utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class YFinanceService:
    """
    Service for fetching stock data from Yahoo Finance.
    Responsible only for data retrieval with proper rate limiting.
    """

    def __init__(self):
        """Initialize the YFinance service with rate limiter."""
        self.rate_limiter = RateLimiter(
            requests_per_minute=settings.YFINANCE_REQUESTS_PER_MINUTE,
            delay_between_requests=settings.YFINANCE_DELAY_BETWEEN_REQUESTS
        )

    def get_historical_data(
        self,
        symbol: str,
        years: int = None
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical stock data for the specified period.

        Args:
            symbol: Stock symbol (add .NS for NSE stocks)
            years: Number of years of historical data (default from config)

        Returns:
            DataFrame with historical data or None if failed
        """
        if years is None:
            years = settings.HISTORICAL_DATA_YEARS

        try:
            # Add .NS suffix for NSE stocks if not present
            if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
                symbol = f"{symbol}.NS"

            # Wait for rate limiter
            with self.rate_limiter:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=years * 365)

                logger.debug(f"Fetching data for {symbol} from {start_date.date()} to {end_date.date()}")

                # Fetch data using yfinance
                ticker = yf.Ticker(symbol)
                df = ticker.history(
                    start=start_date,
                    end=end_date,
                    interval='1d'
                )

                if df.empty:
                    logger.warning(f"No data found for {symbol}")
                    return None

                logger.info(f"Fetched {len(df)} days of data for {symbol}")
                return df

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get the latest closing price for a stock.

        Args:
            symbol: Stock symbol

        Returns:
            Latest closing price or None
        """
        try:
            if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
                symbol = f"{symbol}.NS"

            with self.rate_limiter:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period='1d')

                if not data.empty:
                    latest_price = data['Close'].iloc[-1]
                    logger.debug(f"Latest price for {symbol}: {latest_price}")
                    return float(latest_price)
                else:
                    logger.warning(f"No price data for {symbol}")
                    return None

        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None

    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        Get detailed stock information.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with stock info or None
        """
        try:
            if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
                symbol = f"{symbol}.NS"

            with self.rate_limiter:
                ticker = yf.Ticker(symbol)
                info = ticker.info

                logger.debug(f"Fetched info for {symbol}")
                return info

        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {e}")
            return None

    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if a stock symbol is valid.

        Args:
            symbol: Stock symbol

        Returns:
            True if valid, False otherwise
        """
        try:
            if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
                symbol = f"{symbol}.NS"

            with self.rate_limiter:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period='5d')
                return not data.empty

        except Exception as e:
            logger.error(f"Error validating symbol {symbol}: {e}")
            return False
