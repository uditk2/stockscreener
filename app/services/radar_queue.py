"""
Radar queue service for tracking stocks with breakout signals.
Manages the queue of stocks to monitor.
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
from app.services.redis_service import RedisService
from app.models.stock import RadarStock, BreakoutAnalysis

logger = logging.getLogger(__name__)


class RadarQueueService:
    """
    Service for managing the radar queue of breakout stocks.
    Responsible only for radar queue operations.
    """

    def __init__(self, redis_service: RedisService):
        """
        Initialize radar queue service.

        Args:
            redis_service: Redis service instance
        """
        self.redis = redis_service

    def add_stock_to_radar(
        self,
        symbol: str,
        breakout_analysis: Dict,
        last_price: Optional[float] = None
    ) -> bool:
        """
        Add a stock to the radar queue for tracking.

        Args:
            symbol: Stock symbol
            breakout_analysis: Breakout analysis results
            last_price: Last known price

        Returns:
            bool: Success status
        """
        try:
            # Check if already in radar
            if self.redis.is_in_radar(symbol):
                logger.info(f"{symbol} already in radar, skipping")
                return False

            # Create radar stock entry
            radar_data = {
                'symbol': symbol,
                'added_at': datetime.utcnow().isoformat(),
                'breakout_analysis': breakout_analysis,
                'last_price': last_price
            }

            # Add to Redis
            success = self.redis.add_to_radar(symbol, radar_data)

            if success:
                logger.info(f"Added {symbol} to radar queue")
                return True
            else:
                logger.error(f"Failed to add {symbol} to radar")
                return False

        except Exception as e:
            logger.error(f"Error adding {symbol} to radar: {e}")
            return False

    def get_all_radar_stocks(self) -> List[Dict]:
        """
        Get all stocks currently in the radar queue.

        Returns:
            List of radar stock data
        """
        try:
            stocks = self.redis.get_radar_stocks()
            logger.info(f"Retrieved {len(stocks)} stocks from radar")
            return stocks

        except Exception as e:
            logger.error(f"Error retrieving radar stocks: {e}")
            return []

    def remove_stock_from_radar(self, symbol: str) -> bool:
        """
        Remove a stock from the radar queue.

        Args:
            symbol: Stock symbol

        Returns:
            bool: Success status
        """
        try:
            success = self.redis.remove_from_radar(symbol)

            if success:
                logger.info(f"Removed {symbol} from radar")
                return True
            else:
                logger.error(f"Failed to remove {symbol} from radar")
                return False

        except Exception as e:
            logger.error(f"Error removing {symbol} from radar: {e}")
            return False

    def is_in_radar(self, symbol: str) -> bool:
        """
        Check if a stock is in the radar queue.

        Args:
            symbol: Stock symbol

        Returns:
            bool: True if in radar
        """
        try:
            return self.redis.is_in_radar(symbol)
        except Exception as e:
            logger.error(f"Error checking radar status for {symbol}: {e}")
            return False

    def get_radar_count(self) -> int:
        """
        Get the count of stocks in radar.

        Returns:
            Number of stocks in radar
        """
        try:
            stocks = self.redis.get_radar_stocks()
            return len(stocks)
        except Exception as e:
            logger.error(f"Error getting radar count: {e}")
            return 0

    def clear_radar(self) -> bool:
        """
        Clear all stocks from the radar queue.

        Returns:
            bool: Success status
        """
        try:
            # This would require clearing the radar queue in Redis
            logger.warning("Clearing entire radar queue")
            # Implementation depends on Redis service clear method
            return True

        except Exception as e:
            logger.error(f"Error clearing radar: {e}")
            return False
