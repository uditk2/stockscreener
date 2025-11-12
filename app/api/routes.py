"""
FastAPI routes for the Stock Screener application.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from pydantic import BaseModel
import logging
from app.services.screener_orchestrator import StockScreenerOrchestrator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize orchestrator
orchestrator = StockScreenerOrchestrator()


# Request/Response Models
class InitializeRequest(BaseModel):
    use_fallback: bool = False


class ScreenStockRequest(BaseModel):
    symbol: str


class ScreenAllRequest(BaseModel):
    max_concurrent: int = 5


# Routes
@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": "Stock Screener",
        "version": "1.0.0",
        "description": "Indian Stock Market Screener with Breakout Detection"
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns the status of all services.
    """
    try:
        health = orchestrator.health_check()
        return health
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stocks/initialize")
async def initialize_stocks(request: InitializeRequest):
    """
    Initialize the stock list by fetching from NSE.
    Stores the list in Redis.

    Args:
        use_fallback: If True, use fallback stock list instead of fetching

    Returns:
        Status and count of stocks initialized
    """
    try:
        result = await orchestrator.initialize_stock_list(
            use_fallback=request.use_fallback
        )

        if result['status'] == 'success':
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get('message', 'Failed'))

    except Exception as e:
        logger.error(f"Error initializing stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks/list")
async def get_stock_list():
    """
    Get the list of all stocks from Redis.

    Returns:
        List of stocks
    """
    try:
        stocks = orchestrator.redis.get_stock_list()
        return {
            'status': 'success',
            'count': len(stocks),
            'stocks': stocks
        }
    except Exception as e:
        logger.error(f"Error getting stock list: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/screen/stock")
async def screen_stock(request: ScreenStockRequest):
    """
    Screen a single stock for breakout signals.

    Args:
        symbol: Stock symbol to screen

    Returns:
        Screening results with indicators and breakout analysis
    """
    try:
        result = await orchestrator.screen_single_stock(request.symbol)

        if result['status'] == 'success':
            return result
        elif result['status'] == 'no_data':
            raise HTTPException(status_code=404, detail=result.get('message'))
        else:
            raise HTTPException(status_code=500, detail=result.get('message'))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error screening stock: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/screen/all")
async def screen_all_stocks(
    request: ScreenAllRequest,
    background_tasks: BackgroundTasks
):
    """
    Screen all stocks in the database for breakout signals.
    This is a long-running operation that runs in the background.

    Args:
        max_concurrent: Maximum number of concurrent screening operations

    Returns:
        Status message
    """
    try:
        # Add the screening task to background
        background_tasks.add_task(
            orchestrator.screen_all_stocks,
            max_concurrent=request.max_concurrent
        )

        return {
            'status': 'started',
            'message': 'Stock screening started in background. Check /radar for results.'
        }

    except Exception as e:
        logger.error(f"Error starting full screening: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/screen/all/sync")
async def screen_all_stocks_sync(request: ScreenAllRequest):
    """
    Screen all stocks synchronously (waits for completion).
    WARNING: This can take a long time!

    Args:
        max_concurrent: Maximum number of concurrent screening operations

    Returns:
        Complete screening results
    """
    try:
        result = await orchestrator.screen_all_stocks(
            max_concurrent=request.max_concurrent
        )

        if result['status'] == 'success':
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get('message'))

    except Exception as e:
        logger.error(f"Error in full screening: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/radar")
async def get_radar_stocks():
    """
    Get all stocks currently in the radar queue (detected breakouts).

    Returns:
        List of stocks with breakout signals
    """
    try:
        result = await orchestrator.get_radar_stocks()

        if result['status'] == 'success':
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get('message'))

    except Exception as e:
        logger.error(f"Error getting radar stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock/{symbol}")
async def get_stock_data(symbol: str):
    """
    Get cached data for a specific stock.

    Args:
        symbol: Stock symbol

    Returns:
        Cached stock data including indicators and analysis
    """
    try:
        data = orchestrator.redis.get_stock_data(symbol)

        if data:
            return {
                'status': 'success',
                'data': data
            }
        else:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stock data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/data/clear")
async def clear_all_data():
    """
    Clear all data from Redis.
    WARNING: This will delete all cached stocks, indicators, and radar queue!

    Returns:
        Status message
    """
    try:
        success = orchestrator.redis.clear_all_data()

        if success:
            return {
                'status': 'success',
                'message': 'All data cleared from Redis'
            }
        else:
            raise HTTPException(status_code=500, detail='Failed to clear data')

    except Exception as e:
        logger.error(f"Error clearing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
