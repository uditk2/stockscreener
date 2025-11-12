"""
LLM service for analyzing technical indicators and detecting breakouts.
Uses AI to interpret technical signals and identify potential breakouts.
"""
import logging
from typing import Dict, Optional
import json
import requests
from app.config import settings

logger = logging.getLogger(__name__)


class LLMBreakoutService:
    """
    Service for using LLM to analyze technical indicators and detect breakouts.
    Responsible only for AI-based analysis.
    """

    def __init__(self):
        """Initialize the LLM service."""
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        self.api_url = settings.LLM_API_URL

    def analyze_breakout(
        self,
        symbol: str,
        indicators: Dict[str, float],
        price_data: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Analyze technical indicators to detect potential breakouts.

        Args:
            symbol: Stock symbol
            indicators: Dictionary of technical indicators
            price_data: Optional current price information

        Returns:
            Dictionary with breakout analysis results
        """
        try:
            # Create the analysis prompt
            prompt = self._create_analysis_prompt(symbol, indicators, price_data)

            # Call LLM API
            response = self._call_llm_api(prompt)

            if response:
                # Parse LLM response
                analysis = self._parse_llm_response(symbol, response)
                return analysis
            else:
                logger.warning(f"No LLM response for {symbol}, using fallback analysis")
                return self._fallback_analysis(symbol, indicators)

        except Exception as e:
            logger.error(f"Error in LLM analysis for {symbol}: {e}")
            return self._fallback_analysis(symbol, indicators)

    def _create_analysis_prompt(
        self,
        symbol: str,
        indicators: Dict[str, float],
        price_data: Optional[Dict] = None
    ) -> str:
        """Create a detailed prompt for the LLM."""

        prompt = f"""Analyze the following technical indicators for stock {symbol} and determine if there is a potential breakout signal.

Technical Indicators:
"""

        # Add all indicators to the prompt
        for key, value in indicators.items():
            if value is not None:
                prompt += f"- {key}: {value:.2f}\n"

        if price_data:
            prompt += f"\nCurrent Price Data:\n"
            for key, value in price_data.items():
                prompt += f"- {key}: {value}\n"

        prompt += """
Analyze these indicators and provide:
1. Is there a breakout signal? (yes/no)
2. Confidence level (0-100%)
3. Key signals supporting your decision (list)
4. Brief reasoning (2-3 sentences)

Consider the following for breakout detection:
- RSI: Values above 70 indicate overbought (potential reversal), below 30 oversold (potential bounce)
- MACD: Positive crossover (MACD > Signal) is bullish, negative is bearish
- Moving Averages: Price above SMA/EMA is bullish, golden cross (50 SMA > 200 SMA) is very bullish
- Bollinger Bands: Price near upper band with high volume suggests breakout, near lower band suggests oversold
- Volume: Increasing volume confirms breakout strength
- ADX: Above 25 indicates strong trend
- Stochastic: Above 80 overbought, below 20 oversold

Respond in the following JSON format:
{
    "is_breakout": true/false,
    "confidence": 0-100,
    "signals": ["signal1", "signal2", ...],
    "reasoning": "Your analysis here"
}
"""

        return prompt

    def _call_llm_api(self, prompt: str) -> Optional[str]:
        """
        Call the LLM API with the given prompt.

        Args:
            prompt: Analysis prompt

        Returns:
            LLM response text or None
        """
        if not self.api_key:
            logger.warning("LLM API key not configured")
            return None

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a technical analysis expert specializing in stock market breakout detection."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 500
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                logger.debug(f"LLM response received: {len(content)} chars")
                return content
            else:
                logger.error(f"LLM API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error calling LLM API: {e}")
            return None

    def _parse_llm_response(self, symbol: str, response: str) -> Dict[str, any]:
        """
        Parse the LLM response and extract analysis results.

        Args:
            symbol: Stock symbol
            response: LLM response text

        Returns:
            Parsed analysis dictionary
        """
        try:
            # Try to extract JSON from response
            # Sometimes LLM might wrap JSON in markdown code blocks
            response = response.strip()
            if '```json' in response:
                start = response.find('```json') + 7
                end = response.find('```', start)
                response = response[start:end].strip()
            elif '```' in response:
                start = response.find('```') + 3
                end = response.find('```', start)
                response = response[start:end].strip()

            # Parse JSON
            data = json.loads(response)

            return {
                'symbol': symbol,
                'is_breakout': data.get('is_breakout', False),
                'confidence': data.get('confidence', 0) / 100.0,  # Convert to 0-1 range
                'signals': data.get('signals', []),
                'reasoning': data.get('reasoning', '')
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Response was: {response}")
            # Try to extract basic info from text
            is_breakout = 'yes' in response.lower() or 'breakout' in response.lower()
            return {
                'symbol': symbol,
                'is_breakout': is_breakout,
                'confidence': 0.5,
                'signals': [],
                'reasoning': response[:200]  # First 200 chars
            }

    def _fallback_analysis(self, symbol: str, indicators: Dict[str, float]) -> Dict[str, any]:
        """
        Fallback rule-based analysis when LLM is not available.

        Args:
            symbol: Stock symbol
            indicators: Technical indicators

        Returns:
            Analysis dictionary
        """
        signals = []
        score = 0
        max_score = 0

        # RSI Analysis
        if indicators.get('rsi') is not None:
            max_score += 1
            rsi = indicators['rsi']
            if 30 < rsi < 70:
                score += 0.5
                signals.append(f"RSI at {rsi:.1f} (neutral range)")
            elif rsi < 30:
                score += 1
                signals.append(f"RSI at {rsi:.1f} (oversold, potential bounce)")
            elif rsi > 70:
                signals.append(f"RSI at {rsi:.1f} (overbought, caution)")

        # MACD Analysis
        if indicators.get('macd') is not None and indicators.get('macd_signal') is not None:
            max_score += 1
            macd = indicators['macd']
            signal = indicators['macd_signal']

            if macd > signal and macd > 0:
                score += 1
                signals.append("MACD bullish crossover")
            elif macd > signal:
                score += 0.5
                signals.append("MACD above signal line")

        # Moving Average Analysis
        if all(k in indicators and indicators[k] is not None for k in ['sma_20', 'sma_50']):
            max_score += 1
            if indicators['sma_20'] > indicators['sma_50']:
                score += 1
                signals.append("20 SMA above 50 SMA (bullish)")

        # Bollinger Bands
        if all(k in indicators and indicators[k] is not None for k in ['bollinger_upper', 'bollinger_lower', 'bollinger_middle']):
            max_score += 1
            # Would need current price to properly analyze
            signals.append("Bollinger Bands calculated")

        # Volume
        if indicators.get('obv') is not None:
            signals.append("Volume analysis available")

        # Calculate confidence
        confidence = (score / max_score) if max_score > 0 else 0
        is_breakout = confidence > 0.6 and score >= 2

        reasoning = f"Rule-based analysis: {len(signals)} signals detected. "
        if is_breakout:
            reasoning += "Multiple bullish indicators suggest potential breakout."
        else:
            reasoning += "Insufficient bullish signals for breakout confirmation."

        return {
            'symbol': symbol,
            'is_breakout': is_breakout,
            'confidence': confidence,
            'signals': signals,
            'reasoning': reasoning
        }
