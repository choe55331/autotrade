"""
GPT-4 Stock Analyzer
Uses OpenAI's GPT-4 for advanced trading analysis
"""

import os
from typing import Dict, Any, Optional
import json
from datetime import datetime

from .base_analyzer import BaseAnalyzer
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class GPT4Analyzer(BaseAnalyzer):
    """
    GPT-4 based stock analyzer
    Features:
    - Advanced reasoning capabilities
    - Multi-step analysis
    - Chain-of-thought prompting
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        """
        Initialize GPT-4 analyzer

        Args:
            api_key: OpenAI API key (defaults to env variable)
            model: GPT-4 model to use
        """
        super().__init__()

        try:
            import openai
            self.openai = openai
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. "
                "Install with: pip install openai"
            )

        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. "
                "Set OPENAI_API_KEY environment variable"
            )

        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model

        logger.info(f"GPT-4 Analyzer initialized with model: {model}")

    def analyze_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze stock using GPT-4

        Args:
            stock_data: Stock information and technical data

        Returns:
            Analysis results with signal, score, and reasoning
        """
        try:
            # Prepare analysis prompt
            prompt = self._build_analysis_prompt(stock_data)

            # Call GPT-4
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=1500,
                response_format={"type": "json_object"}
            )

            # Parse response
            content = response.choices[0].message.content
            analysis = json.loads(content)

            # Validate and normalize
            return self._normalize_response(analysis, stock_data)

        except Exception as e:
            logger.error(f"GPT-4 analysis error: {e}")
            return self._get_default_response(stock_data)

    def _get_system_prompt(self) -> str:
        """
        System prompt for GPT-4 trading analysis
        """
        return """You are an expert quantitative trader and technical analyst with 20+ years of experience.

Your task is to analyze stock data and provide actionable trading recommendations.

Analysis framework:
1. Technical Analysis: Evaluate price action, volume, and technical indicators
2. Momentum Analysis: Assess trend strength and momentum
3. Risk Assessment: Evaluate potential risks and volatility
4. Signal Generation: Provide clear BUY/SELL/HOLD signal

Output Requirements:
- Provide response as JSON only
- Be precise and data-driven
- Consider both bullish and bearish factors
- Assign confidence based on signal strength

JSON Format:
{
    "signal": "BUY" | "SELL" | "HOLD",
    "score": <0-10>,
    "confidence": "High" | "Medium" | "Low",
    "reasoning": "<detailed explanation>",
    "technical_factors": ["factor1", "factor2", ...],
    "risk_factors": ["risk1", "risk2", ...],
    "target_price": <number or null>,
    "stop_loss": <number or null>,
    "time_horizon": "short" | "medium" | "long"
}

Signal Guidelines:
- BUY: Strong bullish indicators, positive momentum, manageable risk
- SELL: Strong bearish indicators, negative momentum, high risk
- HOLD: Mixed signals, consolidation, or insufficient data

Score Guidelines (0-10):
- 9-10: Extremely strong signal, high conviction
- 7-8: Strong signal, good confidence
- 5-6: Moderate signal, neutral bias
- 3-4: Weak signal, low conviction
- 0-2: Very weak or contradictory signals

Confidence Guidelines:
- High: Multiple confirming indicators, clear trend
- Medium: Some confirming indicators, developing trend
- Low: Few indicators, unclear trend or mixed signals"""

    def _build_analysis_prompt(self, stock_data: Dict[str, Any]) -> str:
        """
        Build detailed analysis prompt
        """
        stock_code = stock_data.get('stock_code', 'N/A')
        stock_name = stock_data.get('stock_name', 'Unknown')
        current_price = stock_data.get('current_price', 0)
        change_rate = stock_data.get('change_rate', 0)
        volume = stock_data.get('volume', 0)
        trading_value = stock_data.get('trading_value', 0)

        # Technical indicators
        ma5 = stock_data.get('ma5', 0)
        ma20 = stock_data.get('ma20', 0)
        ma60 = stock_data.get('ma60', 0)
        rsi = stock_data.get('rsi', 50)

        # Price history
        price_history = stock_data.get('price_history', [])
        recent_prices = price_history[-10:] if len(price_history) >= 10 else price_history

        # Foreign/Institutional data
        foreign_net = stock_data.get('foreign_net_buy', 0)
        institution_net = stock_data.get('institution_net_buy', 0)

        prompt = f"""Analyze the following Korean stock for trading decision:

**Stock Information:**
- Code: {stock_code}
- Name: {stock_name}
- Current Price: {current_price:,} KRW
- Change Rate: {change_rate:+.2f}%
- Volume: {volume:,} shares
- Trading Value: {trading_value:,} KRW

**Technical Indicators:**
- MA5: {ma5:,} KRW
- MA20: {ma20:,} KRW
- MA60: {ma60:,} KRW
- RSI: {rsi:.1f}

**Price Trend (Recent 10 days):**
{self._format_price_history(recent_prices)}

**Investor Activity:**
- Foreign Net Buy: {foreign_net:,} shares
- Institution Net Buy: {institution_net:,} shares

**Moving Average Alignment:**
{self._analyze_ma_alignment(current_price, ma5, ma20, ma60)}

**Volume Analysis:**
{self._analyze_volume(volume, stock_data)}

Provide comprehensive trading analysis with clear signal, score (0-10), and confidence level.
Focus on:
1. Trend direction and strength
2. Momentum indicators
3. Support/Resistance levels
4. Risk/Reward ratio
5. Entry/Exit points

Output in JSON format as specified."""

        return prompt

    def _format_price_history(self, prices: list) -> str:
        """
        Format price history for display
        """
        if not prices:
            return "No price history available"

        formatted = []
        for i, price in enumerate(prices, 1):
            formatted.append(f"Day-{i}: {price:,} KRW")

        return "\n".join(formatted)

    def _analyze_ma_alignment(
        self,
        current: float,
        ma5: float,
        ma20: float,
        ma60: float
    ) -> str:
        """
        Analyze moving average alignment
        """
        if not all([current, ma5, ma20, ma60]):
            return "Insufficient MA data"

        if current > ma5 > ma20 > ma60:
            return "✓ Perfect bullish alignment (Price > MA5 > MA20 > MA60)"
        elif current < ma5 < ma20 < ma60:
            return "✗ Perfect bearish alignment (Price < MA5 < MA20 < MA60)"
        elif current > ma5 and current > ma20:
            return "✓ Bullish (Price above short-term MAs)"
        elif current < ma5 and current < ma20:
            return "✗ Bearish (Price below short-term MAs)"
        else:
            return "⚠ Mixed signals (No clear alignment)"

    def _analyze_volume(self, volume: int, stock_data: Dict[str, Any]) -> str:
        """
        Analyze volume characteristics
        """
        if not volume:
            return "Volume data not available"

        # Get average volume if available
        avg_volume = stock_data.get('avg_volume', 0)

        if avg_volume and volume > avg_volume * 2:
            return f"✓ High volume (2x+ average) - Strong interest"
        elif avg_volume and volume > avg_volume * 1.5:
            return f"✓ Above average volume (1.5x) - Increased activity"
        elif avg_volume and volume < avg_volume * 0.5:
            return f"✗ Low volume (50% below average) - Weak interest"
        else:
            return f"Normal volume: {volume:,} shares"

    def _normalize_response(
        self,
        analysis: Dict[str, Any],
        stock_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Normalize and validate GPT-4 response
        """
        # Extract and validate fields
        signal = analysis.get('signal', 'HOLD').upper()
        if signal not in ['BUY', 'SELL', 'HOLD']:
            signal = 'HOLD'

        score = float(analysis.get('score', 5))
        score = max(0, min(10, score))  # Clamp to 0-10

        confidence = analysis.get('confidence', 'Medium')
        if confidence not in ['High', 'Medium', 'Low']:
            confidence = 'Medium'

        reasoning = analysis.get('reasoning', 'No detailed reasoning provided')

        # Build normalized response
        return {
            'signal': signal,
            'score': round(score, 1),
            'confidence': confidence,
            'reasoning': reasoning,
            'technical_factors': analysis.get('technical_factors', []),
            'risk_factors': analysis.get('risk_factors', []),
            'target_price': analysis.get('target_price'),
            'stop_loss': analysis.get('stop_loss'),
            'time_horizon': analysis.get('time_horizon', 'medium'),
            'model': 'gpt4',
            'timestamp': datetime.now().isoformat()
        }

    def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze overall market sentiment using GPT-4
        """
        try:
            prompt = self._build_market_prompt(market_data)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert market analyst. "
                                   "Analyze market data and provide sentiment assessment. "
                                   "Output as JSON with: sentiment (Bullish/Bearish/Neutral), "
                                   "score (0-10), and conditions (list of key market factors)."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=800,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            analysis = json.loads(content)

            sentiment = analysis.get('sentiment', 'Neutral')
            if sentiment not in ['Bullish', 'Bearish', 'Neutral']:
                sentiment = 'Neutral'

            return {
                'sentiment': sentiment,
                'score': round(float(analysis.get('score', 5)), 1),
                'conditions': analysis.get('conditions', []),
                'reasoning': analysis.get('reasoning', ''),
                'model': 'gpt4',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"GPT-4 market analysis error: {e}")
            return {
                'sentiment': 'Neutral',
                'score': 5,
                'conditions': ['Analysis unavailable'],
                'timestamp': datetime.now().isoformat()
            }

    def _build_market_prompt(self, market_data: Dict[str, Any]) -> str:
        """
        Build market analysis prompt
        """
        kospi = market_data.get('kospi', {})
        kosdaq = market_data.get('kosdaq', {})

        prompt = f"""Analyze current Korean stock market conditions:

**KOSPI:**
- Current: {kospi.get('current', 0):.2f}
- Change: {kospi.get('change_rate', 0):+.2f}%
- Volume: {kospi.get('volume', 0):,}

**KOSDAQ:**
- Current: {kosdaq.get('current', 0):.2f}
- Change: {kosdaq.get('change_rate', 0):+.2f}%
- Volume: {kosdaq.get('volume', 0):,}

**Market Metrics:**
- Advancing stocks: {market_data.get('advancing', 0)}
- Declining stocks: {market_data.get('declining', 0)}
- Unchanged: {market_data.get('unchanged', 0)}

Provide market sentiment assessment (Bullish/Bearish/Neutral) with score (0-10) and key conditions."""

        return prompt

    def _get_default_response(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Default response when analysis fails
        """
        return {
            'signal': 'HOLD',
            'score': 5,
            'confidence': 'Low',
            'reasoning': 'Analysis failed - defaulting to HOLD',
            'technical_factors': [],
            'risk_factors': ['Analysis unavailable'],
            'target_price': None,
            'stop_loss': None,
            'time_horizon': 'medium',
            'model': 'gpt4',
            'timestamp': datetime.now().isoformat()
        }
