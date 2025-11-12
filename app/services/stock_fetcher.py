"""
Stock list fetcher service for Indian stock market.
Fetches lists of stocks from NSE/BSE by category.
"""
import logging
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import pandas as pd

logger = logging.getLogger(__name__)


class IndianStockFetcher:
    """
    Fetches list of Indian stocks from NSE/BSE.
    Responsible only for retrieving stock lists.
    """

    def __init__(self):
        """Initialize the stock fetcher."""
        self.nse_base_url = "https://www.nseindia.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }

    def get_nse_equity_list(self) -> List[Dict[str, str]]:
        """
        Fetch all equity stocks listed on NSE.

        Returns:
            List of stock dictionaries with symbol, name, and category
        """
        try:
            # First, get cookies by visiting the main page
            session = requests.Session()
            session.get(self.nse_base_url, headers=self.headers, timeout=10)

            # Fetch equity list
            url = f"{self.nse_base_url}/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
            response = session.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                stocks = []

                if 'data' in data:
                    for item in data['data']:
                        stock = {
                            'symbol': item.get('symbol', ''),
                            'name': item.get('meta', {}).get('companyName', item.get('symbol', '')),
                            'category': 'F&O',
                            'exchange': 'NSE'
                        }
                        stocks.append(stock)

                logger.info(f"Fetched {len(stocks)} F&O stocks from NSE")
                return stocks
            else:
                logger.error(f"Failed to fetch NSE stocks: HTTP {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error fetching NSE equity list: {e}")
            return []

    def get_nifty_50_stocks(self) -> List[Dict[str, str]]:
        """
        Fetch NIFTY 50 stocks.

        Returns:
            List of stock dictionaries
        """
        try:
            session = requests.Session()
            session.get(self.nse_base_url, headers=self.headers, timeout=10)

            url = f"{self.nse_base_url}/api/equity-stockIndices?index=NIFTY%2050"
            response = session.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                stocks = []

                if 'data' in data:
                    for item in data['data']:
                        stock = {
                            'symbol': item.get('symbol', ''),
                            'name': item.get('meta', {}).get('companyName', item.get('symbol', '')),
                            'category': 'NIFTY50',
                            'exchange': 'NSE'
                        }
                        stocks.append(stock)

                logger.info(f"Fetched {len(stocks)} NIFTY 50 stocks")
                return stocks
            else:
                logger.error(f"Failed to fetch NIFTY 50: HTTP {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error fetching NIFTY 50: {e}")
            return []

    def get_nifty_500_stocks(self) -> List[Dict[str, str]]:
        """
        Fetch NIFTY 500 stocks.

        Returns:
            List of stock dictionaries
        """
        try:
            session = requests.Session()
            session.get(self.nse_base_url, headers=self.headers, timeout=10)

            url = f"{self.nse_base_url}/api/equity-stockIndices?index=NIFTY%20500"
            response = session.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                stocks = []

                if 'data' in data:
                    for item in data['data']:
                        stock = {
                            'symbol': item.get('symbol', ''),
                            'name': item.get('meta', {}).get('companyName', item.get('symbol', '')),
                            'category': 'NIFTY500',
                            'exchange': 'NSE'
                        }
                        stocks.append(stock)

                logger.info(f"Fetched {len(stocks)} NIFTY 500 stocks")
                return stocks
            else:
                logger.error(f"Failed to fetch NIFTY 500: HTTP {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error fetching NIFTY 500: {e}")
            return []

    def get_stocks_by_sector(self, sector: str) -> List[Dict[str, str]]:
        """
        Fetch stocks by sector.

        Args:
            sector: Sector name (e.g., 'NIFTY BANK', 'NIFTY IT', 'NIFTY PHARMA')

        Returns:
            List of stock dictionaries
        """
        try:
            session = requests.Session()
            session.get(self.nse_base_url, headers=self.headers, timeout=10)

            sector_encoded = sector.replace(' ', '%20')
            url = f"{self.nse_base_url}/api/equity-stockIndices?index={sector_encoded}"
            response = session.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                stocks = []

                if 'data' in data:
                    for item in data['data']:
                        stock = {
                            'symbol': item.get('symbol', ''),
                            'name': item.get('meta', {}).get('companyName', item.get('symbol', '')),
                            'category': sector,
                            'exchange': 'NSE'
                        }
                        stocks.append(stock)

                logger.info(f"Fetched {len(stocks)} stocks from {sector}")
                return stocks
            else:
                logger.error(f"Failed to fetch {sector}: HTTP {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error fetching {sector}: {e}")
            return []

    def get_all_stocks_by_categories(self) -> List[Dict[str, str]]:
        """
        Fetch stocks from multiple categories and combine them.

        Returns:
            Combined list of unique stocks
        """
        all_stocks = []
        seen_symbols = set()

        # Categories to fetch
        categories = [
            ('NIFTY 50', self.get_nifty_50_stocks),
            ('NIFTY 500', self.get_nifty_500_stocks),
            ('NIFTY BANK', lambda: self.get_stocks_by_sector('NIFTY BANK')),
            ('NIFTY IT', lambda: self.get_stocks_by_sector('NIFTY IT')),
            ('NIFTY PHARMA', lambda: self.get_stocks_by_sector('NIFTY PHARMA')),
            ('NIFTY AUTO', lambda: self.get_stocks_by_sector('NIFTY AUTO')),
        ]

        for category_name, fetch_func in categories:
            logger.info(f"Fetching {category_name}...")
            stocks = fetch_func()

            for stock in stocks:
                if stock['symbol'] not in seen_symbols:
                    seen_symbols.add(stock['symbol'])
                    all_stocks.append(stock)

        logger.info(f"Total unique stocks fetched: {len(all_stocks)}")
        return all_stocks

    def get_fallback_stock_list(self) -> List[Dict[str, str]]:
        """
        Fallback method to get a predefined list of popular Indian stocks.
        Used when API fetching fails.

        Returns:
            List of popular Indian stocks
        """
        popular_stocks = [
            {'symbol': 'RELIANCE', 'name': 'Reliance Industries Ltd', 'category': 'ENERGY', 'exchange': 'NSE'},
            {'symbol': 'TCS', 'name': 'Tata Consultancy Services Ltd', 'category': 'IT', 'exchange': 'NSE'},
            {'symbol': 'HDFCBANK', 'name': 'HDFC Bank Ltd', 'category': 'BANK', 'exchange': 'NSE'},
            {'symbol': 'INFY', 'name': 'Infosys Ltd', 'category': 'IT', 'exchange': 'NSE'},
            {'symbol': 'ICICIBANK', 'name': 'ICICI Bank Ltd', 'category': 'BANK', 'exchange': 'NSE'},
            {'symbol': 'HINDUNILVR', 'name': 'Hindustan Unilever Ltd', 'category': 'FMCG', 'exchange': 'NSE'},
            {'symbol': 'SBIN', 'name': 'State Bank of India', 'category': 'BANK', 'exchange': 'NSE'},
            {'symbol': 'BHARTIARTL', 'name': 'Bharti Airtel Ltd', 'category': 'TELECOM', 'exchange': 'NSE'},
            {'symbol': 'KOTAKBANK', 'name': 'Kotak Mahindra Bank Ltd', 'category': 'BANK', 'exchange': 'NSE'},
            {'symbol': 'ITC', 'name': 'ITC Ltd', 'category': 'FMCG', 'exchange': 'NSE'},
            {'symbol': 'LT', 'name': 'Larsen & Toubro Ltd', 'category': 'INFRASTRUCTURE', 'exchange': 'NSE'},
            {'symbol': 'AXISBANK', 'name': 'Axis Bank Ltd', 'category': 'BANK', 'exchange': 'NSE'},
            {'symbol': 'WIPRO', 'name': 'Wipro Ltd', 'category': 'IT', 'exchange': 'NSE'},
            {'symbol': 'MARUTI', 'name': 'Maruti Suzuki India Ltd', 'category': 'AUTO', 'exchange': 'NSE'},
            {'symbol': 'SUNPHARMA', 'name': 'Sun Pharmaceutical Industries Ltd', 'category': 'PHARMA', 'exchange': 'NSE'},
        ]

        logger.info(f"Using fallback list of {len(popular_stocks)} stocks")
        return popular_stocks
