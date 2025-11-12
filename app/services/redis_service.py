"""
Redis service for data storage and queue management.
Follows Single Responsibility Principle - handles only Redis operations.
"""
import redis
import json
from typing import List, Optional, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisService:
    """Manages all Redis operations for the application."""

    def __init__(self):
        """Initialize Redis connection."""
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )

    def ping(self) -> bool:
        """Check if Redis is available."""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False

    # Stock List Operations
    def store_stock_list(self, stocks: List[Dict[str, str]]) -> bool:
        """
        Store list of stocks in Redis.

        Args:
            stocks: List of stock dictionaries with symbol, name, category

        Returns:
            bool: Success status
        """
        try:
            pipeline = self.client.pipeline()
            # Clear existing list
            pipeline.delete(settings.REDIS_STOCK_LIST_KEY)
            # Store each stock as JSON
            for stock in stocks:
                pipeline.rpush(settings.REDIS_STOCK_LIST_KEY, json.dumps(stock))
            pipeline.execute()
            logger.info(f"Stored {len(stocks)} stocks in Redis")
            return True
        except Exception as e:
            logger.error(f"Failed to store stock list: {e}")
            return False

    def get_stock_list(self) -> List[Dict[str, str]]:
        """
        Retrieve list of all stocks from Redis.

        Returns:
            List of stock dictionaries
        """
        try:
            stocks_json = self.client.lrange(settings.REDIS_STOCK_LIST_KEY, 0, -1)
            return [json.loads(stock) for stock in stocks_json]
        except Exception as e:
            logger.error(f"Failed to retrieve stock list: {e}")
            return []

    # Historical Data Operations
    def store_stock_data(self, symbol: str, data: Dict[str, Any]) -> bool:
        """
        Store historical data for a stock.

        Args:
            symbol: Stock symbol
            data: Historical data dictionary

        Returns:
            bool: Success status
        """
        try:
            key = f"{settings.REDIS_STOCK_DATA_PREFIX}{symbol}"
            self.client.set(key, json.dumps(data))
            logger.debug(f"Stored data for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Failed to store data for {symbol}: {e}")
            return False

    def get_stock_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve historical data for a stock.

        Args:
            symbol: Stock symbol

        Returns:
            Historical data dictionary or None
        """
        try:
            key = f"{settings.REDIS_STOCK_DATA_PREFIX}{symbol}"
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to retrieve data for {symbol}: {e}")
            return None

    # Radar Queue Operations
    def add_to_radar(self, symbol: str, analysis: Dict[str, Any]) -> bool:
        """
        Add a stock to the radar queue.

        Args:
            symbol: Stock symbol
            analysis: Breakout analysis data

        Returns:
            bool: Success status
        """
        try:
            data = {
                "symbol": symbol,
                "analysis": analysis
            }
            self.client.rpush(settings.REDIS_RADAR_QUEUE_KEY, json.dumps(data))
            # Also store in a set for quick lookup
            self.client.sadd("stocks:radar:set", symbol)
            logger.info(f"Added {symbol} to radar queue")
            return True
        except Exception as e:
            logger.error(f"Failed to add {symbol} to radar: {e}")
            return False

    def get_radar_stocks(self) -> List[Dict[str, Any]]:
        """
        Get all stocks in the radar queue.

        Returns:
            List of radar stock data
        """
        try:
            stocks_json = self.client.lrange(settings.REDIS_RADAR_QUEUE_KEY, 0, -1)
            return [json.loads(stock) for stock in stocks_json]
        except Exception as e:
            logger.error(f"Failed to retrieve radar stocks: {e}")
            return []

    def is_in_radar(self, symbol: str) -> bool:
        """
        Check if a stock is already in radar.

        Args:
            symbol: Stock symbol

        Returns:
            bool: True if in radar
        """
        try:
            return self.client.sismember("stocks:radar:set", symbol)
        except Exception as e:
            logger.error(f"Failed to check radar status for {symbol}: {e}")
            return False

    def remove_from_radar(self, symbol: str) -> bool:
        """
        Remove a stock from radar queue.

        Args:
            symbol: Stock symbol

        Returns:
            bool: Success status
        """
        try:
            # Remove from set
            self.client.srem("stocks:radar:set", symbol)
            # Note: Removing from list requires scanning, consider using a different structure
            # For now, we'll just remove from the set
            logger.info(f"Removed {symbol} from radar tracking")
            return True
        except Exception as e:
            logger.error(f"Failed to remove {symbol} from radar: {e}")
            return False

    def clear_all_data(self) -> bool:
        """Clear all stock screener data from Redis."""
        try:
            self.client.delete(
                settings.REDIS_STOCK_LIST_KEY,
                settings.REDIS_RADAR_QUEUE_KEY,
                "stocks:radar:set"
            )
            # Clear all stock data keys
            keys = self.client.keys(f"{settings.REDIS_STOCK_DATA_PREFIX}*")
            if keys:
                self.client.delete(*keys)
            logger.info("Cleared all data from Redis")
            return True
        except Exception as e:
            logger.error(f"Failed to clear Redis data: {e}")
            return False
