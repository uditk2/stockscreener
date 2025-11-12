"""
Stock screener orchestrator service.
Coordinates all services to perform the complete screening workflow.
"""
import logging
from typing import List, Dict, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.services.redis_service import RedisService
from app.services.stock_fetcher import IndianStockFetcher
from app.services.yfinance_service import YFinanceService
from app.services.technical_indicators import TechnicalIndicatorService
from app.services.llm_service import LLMBreakoutService
from app.services.radar_queue import RadarQueueService

logger = logging.getLogger(__name__)


class StockScreenerOrchestrator:
    """
    Main orchestrator that coordinates all screening operations.
    Implements the complete workflow for stock screening.
    """

    def __init__(self):
        """Initialize all services."""
        self.redis = RedisService()
        self.stock_fetcher = IndianStockFetcher()
        self.yfinance = YFinanceService()
        self.technical_indicators = TechnicalIndicatorService()
        self.llm_service = LLMBreakoutService()
        self.radar_queue = RadarQueueService(self.redis)

    async def initialize_stock_list(self, use_fallback: bool = False) -> Dict[str, any]:
        """
        Step 1: Fetch and store list of Indian stocks.

        Args:
            use_fallback: Use fallback stock list if True

        Returns:
            Dictionary with status and count
        """
        try:
            logger.info("Starting stock list initialization...")

            if use_fallback:
                stocks = self.stock_fetcher.get_fallback_stock_list()
            else:
                stocks = self.stock_fetcher.get_all_stocks_by_categories()

                # Fallback if main fetch failed
                if not stocks:
                    logger.warning("Main fetch failed, using fallback")
                    stocks = self.stock_fetcher.get_fallback_stock_list()

            # Store in Redis
            if stocks:
                success = self.redis.store_stock_list(stocks)
                if success:
                    logger.info(f"Stored {len(stocks)} stocks in Redis")
                    return {
                        'status': 'success',
                        'count': len(stocks),
                        'stocks': stocks
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Failed to store stocks in Redis'
                    }
            else:
                return {
                    'status': 'error',
                    'message': 'No stocks fetched'
                }

        except Exception as e:
            logger.error(f"Error initializing stock list: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }

    async def screen_single_stock(self, symbol: str) -> Dict[str, any]:
        """
        Screen a single stock: fetch data, calculate indicators, analyze breakout.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with screening results
        """
        try:
            logger.info(f"Screening {symbol}...")

            # Step 1: Fetch historical data
            df = self.yfinance.get_historical_data(symbol)

            if df is None or df.empty:
                logger.warning(f"No data available for {symbol}")
                return {
                    'status': 'no_data',
                    'symbol': symbol,
                    'message': 'No historical data available'
                }

            # Step 2: Calculate technical indicators
            indicators = self.technical_indicators.calculate_all_indicators(df)

            if not indicators:
                logger.warning(f"Failed to calculate indicators for {symbol}")
                return {
                    'status': 'error',
                    'symbol': symbol,
                    'message': 'Failed to calculate indicators'
                }

            # Step 3: Get latest price
            latest_price = float(df['Close'].iloc[-1])

            # Step 4: Analyze for breakout using LLM
            breakout_analysis = self.llm_service.analyze_breakout(
                symbol=symbol,
                indicators=indicators,
                price_data={'latest_price': latest_price}
            )

            # Step 5: Store data in Redis
            stock_data = {
                'symbol': symbol,
                'indicators': indicators,
                'latest_price': latest_price,
                'breakout_analysis': breakout_analysis,
                'data_length': len(df)
            }
            self.redis.store_stock_data(symbol, stock_data)

            # Step 6: If breakout detected, add to radar
            if breakout_analysis.get('is_breakout', False):
                confidence = breakout_analysis.get('confidence', 0)
                if confidence > 0.6:  # Only add high-confidence breakouts
                    self.radar_queue.add_stock_to_radar(
                        symbol=symbol,
                        breakout_analysis=breakout_analysis,
                        last_price=latest_price
                    )

            logger.info(f"Completed screening {symbol} - Breakout: {breakout_analysis.get('is_breakout', False)}")

            return {
                'status': 'success',
                'symbol': symbol,
                'indicators': indicators,
                'breakout_analysis': breakout_analysis,
                'latest_price': latest_price,
                'added_to_radar': breakout_analysis.get('is_breakout', False) and confidence > 0.6
            }

        except Exception as e:
            logger.error(f"Error screening {symbol}: {e}")
            return {
                'status': 'error',
                'symbol': symbol,
                'message': str(e)
            }

    async def screen_all_stocks(self, max_concurrent: int = 5) -> Dict[str, any]:
        """
        Screen all stocks in the Redis list.

        Args:
            max_concurrent: Maximum concurrent screenings

        Returns:
            Dictionary with screening summary
        """
        try:
            logger.info("Starting full stock screening...")

            # Get stock list from Redis
            stocks = self.redis.get_stock_list()

            if not stocks:
                return {
                    'status': 'error',
                    'message': 'No stocks in Redis. Run initialize_stock_list first.'
                }

            logger.info(f"Screening {len(stocks)} stocks...")

            results = {
                'total': len(stocks),
                'processed': 0,
                'breakouts': 0,
                'errors': 0,
                'no_data': 0
            }

            # Process stocks with concurrency limit
            symbols = [stock['symbol'] for stock in stocks]

            # Use ThreadPoolExecutor for I/O-bound operations
            with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
                # Create tasks
                loop = asyncio.get_event_loop()
                tasks = []

                for symbol in symbols:
                    task = loop.run_in_executor(
                        executor,
                        self._screen_stock_sync,
                        symbol
                    )
                    tasks.append(task)

                # Wait for all tasks to complete
                screening_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in screening_results:
                if isinstance(result, Exception):
                    results['errors'] += 1
                    continue

                results['processed'] += 1

                if result.get('status') == 'success':
                    if result.get('added_to_radar', False):
                        results['breakouts'] += 1
                elif result.get('status') == 'no_data':
                    results['no_data'] += 1
                else:
                    results['errors'] += 1

            logger.info(f"Screening complete: {results}")

            return {
                'status': 'success',
                'results': results
            }

        except Exception as e:
            logger.error(f"Error in full screening: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _screen_stock_sync(self, symbol: str) -> Dict[str, any]:
        """
        Synchronous wrapper for screening a single stock.
        Used for ThreadPoolExecutor.

        Args:
            symbol: Stock symbol

        Returns:
            Screening result
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.screen_single_stock(symbol))
        finally:
            loop.close()

    async def get_radar_stocks(self) -> Dict[str, any]:
        """
        Get all stocks currently in the radar queue.

        Returns:
            Dictionary with radar stocks
        """
        try:
            stocks = self.radar_queue.get_all_radar_stocks()

            return {
                'status': 'success',
                'count': len(stocks),
                'stocks': stocks
            }

        except Exception as e:
            logger.error(f"Error getting radar stocks: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def health_check(self) -> Dict[str, any]:
        """
        Check health of all services.

        Returns:
            Health status dictionary
        """
        health = {
            'redis': self.redis.ping(),
            'stock_count': len(self.redis.get_stock_list()),
            'radar_count': self.radar_queue.get_radar_count()
        }

        all_healthy = health['redis']

        return {
            'status': 'healthy' if all_healthy else 'unhealthy',
            'services': health
        }
