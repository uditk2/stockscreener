# Stock Screener - Indian Stock Market Breakout Detection

A comprehensive stock screening application for the Indian stock market that uses Yahoo Finance data, technical indicators, and AI-powered analysis to detect potential breakouts.

## Features

- **Stock List Fetching**: Automatically fetches Indian stock lists from NSE by category (NIFTY 50, NIFTY 500, sectoral indices)
- **Historical Data**: Downloads 2 years of historical data using yfinance with intelligent rate limiting
- **Technical Indicators**: Calculates comprehensive technical indicators using pandas and TA-Lib:
  - Moving Averages (SMA, EMA)
  - Momentum Indicators (RSI, MACD, Stochastic)
  - Volatility Indicators (Bollinger Bands, ATR)
  - Volume Indicators (OBV)
  - Trend Indicators (ADX)
- **AI-Powered Analysis**: Uses LLM (OpenAI GPT-4) to analyze technical indicators and detect breakout signals
- **Radar Queue**: Automatically tracks stocks with high-confidence breakout signals
- **Redis Caching**: Fast data storage and retrieval
- **RESTful API**: Built with FastAPI for easy integration
- **Dockerized**: Complete Docker setup for easy deployment
- **Modular Design**: Follows Single Responsibility Principle for maintainability

## Architecture

```
stockscreener/
├── app/
│   ├── models/              # Data models (Pydantic)
│   │   └── stock.py
│   ├── services/            # Business logic (SRP)
│   │   ├── redis_service.py           # Redis operations
│   │   ├── stock_fetcher.py           # Fetch Indian stock lists
│   │   ├── yfinance_service.py        # Historical data with rate limiting
│   │   ├── technical_indicators.py    # Technical analysis
│   │   ├── llm_service.py             # AI breakout detection
│   │   ├── radar_queue.py             # Radar queue management
│   │   └── screener_orchestrator.py   # Main workflow orchestration
│   ├── api/                 # API routes
│   │   └── routes.py
│   ├── utils/               # Utilities
│   │   └── rate_limiter.py
│   ├── config.py            # Configuration management
│   └── main.py              # FastAPI application
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Prerequisites

- Docker and Docker Compose
- OpenAI API key (optional, for AI-powered analysis)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd stockscreener
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key (optional)
```

### 3. Start the Application

```bash
docker-compose up -d
```

This will start:
- Redis server on port 6379
- FastAPI application on port 8000

### 4. Access the Application

- API Documentation: http://localhost:8000/docs
- ReDoc Documentation: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## API Usage

### Initialize Stock List

Fetch and store Indian stocks from NSE:

```bash
curl -X POST "http://localhost:8000/api/v1/stocks/initialize" \
  -H "Content-Type: application/json" \
  -d '{"use_fallback": false}'
```

### Get Stock List

```bash
curl "http://localhost:8000/api/v1/stocks/list"
```

### Screen a Single Stock

```bash
curl -X POST "http://localhost:8000/api/v1/screen/stock" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "RELIANCE"}'
```

### Screen All Stocks (Background)

```bash
curl -X POST "http://localhost:8000/api/v1/screen/all" \
  -H "Content-Type: application/json" \
  -d '{"max_concurrent": 5}'
```

### Get Radar Stocks (Detected Breakouts)

```bash
curl "http://localhost:8000/api/v1/radar"
```

### Get Stock Data

```bash
curl "http://localhost:8000/api/v1/stock/RELIANCE"
```

## Workflow

1. **Initialize**: Fetch list of Indian stocks from NSE and store in Redis
2. **Screen**: For each stock:
   - Fetch 2 years of historical data from Yahoo Finance (with rate limiting)
   - Calculate technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, etc.)
   - Send indicators to LLM for breakout analysis
   - If breakout detected with high confidence, add to radar queue
3. **Monitor**: Check radar queue for stocks to track

## Configuration

Edit `.env` or set environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_HOST` | Redis hostname | redis |
| `REDIS_PORT` | Redis port | 6379 |
| `YFINANCE_REQUESTS_PER_MINUTE` | Rate limit for yfinance | 2000 |
| `YFINANCE_DELAY_BETWEEN_REQUESTS` | Delay between requests (seconds) | 0.5 |
| `LLM_API_KEY` | OpenAI API key | - |
| `LLM_MODEL` | LLM model to use | gpt-4 |
| `HISTORICAL_DATA_YEARS` | Years of historical data | 2 |
| `DEBUG` | Debug mode | false |

## Rate Limiting

The application implements intelligent rate limiting for yfinance to avoid API throttling:
- Configurable requests per minute
- Configurable delay between requests
- Token bucket algorithm for smooth rate limiting

## Technical Indicators

The application calculates the following indicators:

### Moving Averages
- SMA (20, 50, 200 periods)
- EMA (12, 26 periods)

### Momentum
- RSI (14 period)
- MACD (12, 26, 9)
- Stochastic Oscillator

### Volatility
- Bollinger Bands (20 period, 2 std dev)
- ATR (14 period)

### Volume
- Volume SMA (20 period)
- On-Balance Volume (OBV)

### Trend
- ADX (14 period)

## AI Breakout Detection

The LLM analyzes all technical indicators and provides:
- Breakout signal (yes/no)
- Confidence level (0-100%)
- Key signals supporting the decision
- Detailed reasoning

If LLM is not configured, the application falls back to rule-based analysis.

## Development

### Running Locally (without Docker)

1. Install dependencies:

```bash
# Install TA-Lib system library
# On Ubuntu/Debian:
sudo apt-get install ta-lib

# On macOS:
brew install ta-lib

# Install Python packages
pip install -r requirements.txt
```

2. Start Redis:

```bash
redis-server
```

3. Run the application:

```bash
uvicorn app.main:app --reload
```

### Running Tests

```bash
# TODO: Add tests
pytest
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Returns status of all services including Redis connection.

### Logs

View application logs:

```bash
docker-compose logs -f api
```

View Redis logs:

```bash
docker-compose logs -f redis
```

## Troubleshooting

### Redis Connection Failed

Ensure Redis is running:

```bash
docker-compose ps
```

### No Stocks Fetched

The NSE API can be flaky. Use fallback mode:

```bash
curl -X POST "http://localhost:8000/api/v1/stocks/initialize" \
  -H "Content-Type: application/json" \
  -d '{"use_fallback": true}'
```

### Rate Limiting Issues

Adjust rate limiting in `.env`:

```
YFINANCE_REQUESTS_PER_MINUTE=1000
YFINANCE_DELAY_BETWEEN_REQUESTS=1.0
```

## Future Enhancements

- [ ] Add authentication and user management
- [ ] Implement WebSocket for real-time updates
- [ ] Add email/SMS notifications for breakouts
- [ ] Create frontend dashboard
- [ ] Add more technical indicators
- [ ] Implement backtesting functionality
- [ ] Add portfolio tracking
- [ ] Support for more exchanges (BSE, etc.)

## License

MIT

## Contributing

Contributions are welcome! Please follow the Single Responsibility Principle when adding new features.

## Disclaimer

This application is for educational purposes only. Stock market trading involves substantial risk. Always do your own research and consult with a financial advisor before making investment decisions.
