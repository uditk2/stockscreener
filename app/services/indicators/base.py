"""
Base module for technical indicators.
Contains common utilities and base classes.
"""
import logging

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    logging.warning("TA-Lib not available, using pandas implementations")

logger = logging.getLogger(__name__)


class BaseIndicator:
    """Base class for all technical indicators."""

    def __init__(self):
        """Initialize the base indicator."""
        self.talib_available = TALIB_AVAILABLE
