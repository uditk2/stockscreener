"""
Data models for stock information.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class StockInfo(BaseModel):
    """Basic stock information."""
    symbol: str
    name: str
    category: Optional[str] = None
    exchange: str = "NSE"


class StockHistoricalData(BaseModel):
    """Historical stock data."""
    symbol: str
    data: Dict[str, float]  # Date -> Price mapping
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class TechnicalIndicators(BaseModel):
    """Technical indicators for a stock."""
    symbol: str
    # Moving Averages
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None

    # Momentum Indicators
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None

    # Volatility Indicators
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    atr: Optional[float] = None

    # Volume Indicators
    volume_sma: Optional[float] = None
    obv: Optional[float] = None

    # Other Indicators
    stochastic_k: Optional[float] = None
    stochastic_d: Optional[float] = None
    adx: Optional[float] = None

    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class BreakoutAnalysis(BaseModel):
    """LLM analysis result for breakout detection."""
    symbol: str
    is_breakout: bool
    confidence: float  # 0-1
    reasoning: str
    signals: List[str]
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class RadarStock(BaseModel):
    """Stock in radar for tracking."""
    symbol: str
    added_at: datetime = Field(default_factory=datetime.utcnow)
    breakout_analysis: BreakoutAnalysis
    last_price: Optional[float] = None
