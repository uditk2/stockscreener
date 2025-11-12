"""
Rate limiter utility to prevent API throttling.
"""
import time
import logging
from threading import Lock
from collections import deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter for API calls.
    Ensures we don't exceed rate limits.
    """

    def __init__(self, requests_per_minute: int, delay_between_requests: float = 0):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests allowed per minute
            delay_between_requests: Minimum delay between requests in seconds
        """
        self.requests_per_minute = requests_per_minute
        self.delay_between_requests = delay_between_requests
        self.request_times = deque()
        self.lock = Lock()
        self.last_request_time = None

    def wait_if_needed(self):
        """
        Wait if necessary to comply with rate limits.
        Blocks until it's safe to make the next request.
        """
        with self.lock:
            now = datetime.now()

            # Remove requests older than 1 minute
            cutoff = now - timedelta(minutes=1)
            while self.request_times and self.request_times[0] < cutoff:
                self.request_times.popleft()

            # Check if we've hit the per-minute limit
            if len(self.request_times) >= self.requests_per_minute:
                oldest = self.request_times[0]
                wait_time = (oldest + timedelta(minutes=1) - now).total_seconds()
                if wait_time > 0:
                    logger.debug(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                    time.sleep(wait_time)
                    # Recursively check again
                    return self.wait_if_needed()

            # Check minimum delay between requests
            if self.last_request_time and self.delay_between_requests > 0:
                elapsed = (now - self.last_request_time).total_seconds()
                if elapsed < self.delay_between_requests:
                    wait_time = self.delay_between_requests - elapsed
                    logger.debug(f"Delaying {wait_time:.2f} seconds between requests")
                    time.sleep(wait_time)
                    now = datetime.now()

            # Record this request
            self.request_times.append(now)
            self.last_request_time = now

    def __enter__(self):
        """Context manager entry."""
        self.wait_if_needed()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass
