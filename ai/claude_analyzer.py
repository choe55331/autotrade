"""
Claude Stock Analyzer
Uses Anthropic's Claude for sophisticated trading analysis
"""

import os
from typing import Dict, Any, Optional
import json
from datetime import datetime

from .base_analyzer import BaseAnalyzer
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class ClaudeAnalyzer(BaseAnalyzer):
    """
    Claude-based stock analyzer
    Features:
    - Long context analysis
    - Nuanced risk assessment
    - Detailed reasoning
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Claude analyzer

        Args:
            api_key: Anthropic API key (defaults to env variable)
            model: Claude model to use
        """
        super().__init__()

        try:
            import anthropic
            self.anthropic = anthropic
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. "
                "Install with: pip install anthropic"
            )

        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. "
                "Set ANTHROPIC_API_KEY environment variable"
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model

        logger.info(f"Claude Analyzer initialized with model: {model}")

    def analyze_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze stock using Claude

        Args:
            stock_data: Stock information and technical data

        Returns:
            Analysis results with signal, score, and reasoning
        """
        try:
            # Prepare analysis prompt
            prompt = self._build_analysis_prompt(stock_data)

            # Call Claude
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                system=self._get_system_prompt(),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse response
            content = message.content[0].text

            # Extract JSON from response
            analysis = self._extract_json(content)

            # Validate and normalize
            return self._normalize_response(analysis, stock_data)

        except Exception as e:
            logger.error(f"Claude analysis error: {e}")
            return self._get_default_response(stock_data)

    def _get_system_prompt(self) -> str:
        """
        System prompt for Claude trading analysis
        """
        return """You are a highly experienced quantitative trader and risk analyst with deep expertise in technical analysis, market microstructure, and behavioral finance.

Your role is to provide sophisticated trading analysis that considers:
1. Technical patterns and indicators
2. Market context and regime
3. Risk-adjusted returns
4. Behavioral factors
5. Probabilistic thinking

Analysis Framework:
- Evaluate multiple timeframes
- Consider both bullish and bearish scenarios
- Assess probability of outcomes
- Provide nuanced risk assessment
- Give actionable recommendations

Output your analysis as JSON with the following structure:
{
    "signal": "BUY" | "SELL" | "HOLD",
    "score": <0-10 float>,
    "confidence": "High" | "Medium" | "Low",
    "reasoning": "<detailed multi-paragraph explanation>",
    "bullish_factors": ["factor1", "factor2", ...],
    "bearish_factors": ["factor1", "factor2", ...],
    "risk_assessment": "<risk analysis>",
    "target_price": <number or null>,
    "stop_loss": <number or null>,
    "probability_success": <0-100>,
    "key_levels": {
        "support": [<levels>],
        "resistance": [<levels>]
    },
    "market_regime": "trending" | "ranging" | "volatile"
}

Be thorough, precise, and honest about uncertainties."""

    def _build_analysis_prompt(self, stock_data: Dict[str, Any]) -> str:
        """
        Build comprehensive analysis prompt
        """
        stock_code = stock_data.get('stock_code', 'N/A')
        stock_name = stock_data.get('stock_name', 'Unknown')
        current_price = stock_data.get('current_price', 0)
        change_rate = stock_data.get('change_rate', 0)
        volume = stock_data.get('volume', 0)

        # Technical data
        ma5 = stock_data.get('ma5', 0)
        ma20 = stock_data.get('ma20', 0)
        ma60 = stock_data.get('ma60', 0)
        rsi = stock_data.get('rsi', 50)

        # Price history
        price_history = stock_data.get('price_history', [])
        recent_prices = price_history[-20:] if len(price_history) >= 20 else price_history

        # Calculate price statistics
        if recent_prices:
            high_20d = max(recent_prices)
            low_20d = min(recent_prices)
            price_range_pct = ((high_20d - low_20d) / low_20d * 100) if low_20d > 0 else 0
        else:
            high_20d = current_price
            low_20d = current_price
            price_range_pct = 0

        prompt = f"""Conduct a comprehensive trading analysis for the following Korean stock:

## Stock Identification
- Code: {stock_code}
- Name: {stock_name}

## Current Market Data
- Price: {current_price:,} KRW
- Daily Change: {change_rate:+.2f}%
- Volume: {volume:,} shares
- Trading Value: {stock_data.get('trading_value', 0):,} KRW

## Technical Indicators
- RSI: {rsi:.1f} (Overbought>70, Oversold<30)
- MA5: {ma5:,} KRW
- MA20: {ma20:,} KRW
- MA60: {ma60:,} KRW

## Price Action Analysis
- 20-Day High: {high_20d:,} KRW
- 20-Day Low: {low_20d:,} KRW
- Range: {price_range_pct:.1f}%
- Current vs MA5: {((current_price - ma5) / ma5 * 100):+.1f}%
- Current vs MA20: {((current_price - ma20) / ma20 * 100):+.1f}%

## Recent Price History (20 days):
{self._format_detailed_prices(recent_prices)}

## Investor Flow
- Foreign Net: {stock_data.get('foreign_net_buy', 0):,} shares
- Institution Net: {stock_data.get('institution_net_buy', 0):,} shares
- Individual Net: {stock_data.get('individual_net_buy', 0):,} shares

## Market Context
- Market Cap: {stock_data.get('market_cap', 'N/A')}
- Sector: {stock_data.get('sector', 'N/A')}
- Industry: {stock_data.get('industry', 'N/A')}

## Analysis Requirements
1. **Technical Setup**: Evaluate current technical position
2. **Momentum**: Assess trend strength and momentum
3. **Risk/Reward**: Calculate potential risk-adjusted returns
4. **Probability Assessment**: Estimate success probability
5. **Key Levels**: Identify critical support/resistance
6. **Market Regime**: Determine current market state
7. **Trading Signal**: Provide clear BUY/SELL/HOLD recommendation

## Specific Questions to Address
- What is the dominant trend (short, medium, long-term)?
- Are we at a decision point (breakout/breakdown)?
- What are the key risk factors?
- Where should stop-loss be placed?
- What is a realistic target price?
- How strong is the current momentum?
- Is volume confirming the price action?

Provide your analysis in JSON format with detailed reasoning. Be specific about why you reach your conclusions."""

        return prompt

    def _format_detailed_prices(self, prices: list) -> str:
        """
        Format price history with more detail
        """
        if not prices:
            return "No price history available"

        formatted = []
        for i, price in enumerate(reversed(prices), 1):
            formatted.append(f"{i:2d} days ago: {price:>10,} KRW")

        return "\n".join(formatted[:20])  # Limit to 20 days

    def _extract_json(self, content: str) -> Dict[str, Any]:
        """
        Extract JSON from Claude's response
        Claude may wrap JSON in markdown code blocks
        """
        # Try to find JSON in markdown code blocks
        import re

        # Look for ```json ... ``` blocks
        json_pattern = r'```json\s*(.*?)\s*```'
        matches = re.findall(json_pattern, content, re.DOTALL)

        if matches:
            json_str = matches[0]
        else:
            # Look for plain JSON object
            json_pattern = r'\{.*\}'
            matches = re.findall(json_pattern, content, re.DOTALL)
            if matches:
                json_str = matches[0]
            else:
                # Return entire content and try to parse
                json_str = content

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from Claude response")
            # Return a basic structure
            return {
                'signal': 'HOLD',
                'score': 5,
                'confidence': 'Low',
                'reasoning': content[:500]  # Use first 500 chars as reasoning
            }

    def _normalize_response(
        self,
        analysis: Dict[str, Any],
        stock_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Normalize and validate Claude response
        """
        # Extract and validate fields
        signal = analysis.get('signal', 'HOLD').upper()
        if signal not in ['BUY', 'SELL', 'HOLD']:
            signal = 'HOLD'

        score = float(analysis.get('score', 5))
        score = max(0, min(10, score))

        confidence = analysis.get('confidence', 'Medium')
        if confidence not in ['High', 'Medium', 'Low']:
            confidence = 'Medium'

        # Build normalized response
        return {
            'signal': signal,
            'score': round(score, 1),
            'confidence': confidence,
            'reasoning': analysis.get('reasoning', 'No reasoning provided'),
            'bullish_factors': analysis.get('bullish_factors', []),
            'bearish_factors': analysis.get('bearish_factors', []),
            'risk_assessment': analysis.get('risk_assessment', ''),
            'target_price': analysis.get('target_price'),
            'stop_loss': analysis.get('stop_loss'),
            'probability_success': analysis.get('probability_success', 50),
            'key_levels': analysis.get('key_levels', {}),
            'market_regime': analysis.get('market_regime', 'ranging'),
            'model': 'claude',
            'timestamp': datetime.now().isoformat()
        }

    def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze overall market using Claude
        """
        try:
            prompt = self._build_market_prompt(market_data)

            message = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.3,
                system="You are an expert market analyst. "
                       "Analyze market conditions and provide sentiment assessment. "
                       "Output as JSON with: sentiment, score, conditions, and reasoning.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            content = message.content[0].text
            analysis = self._extract_json(content)

            sentiment = analysis.get('sentiment', 'Neutral')
            if sentiment not in ['Bullish', 'Bearish', 'Neutral']:
                sentiment = 'Neutral'

            return {
                'sentiment': sentiment,
                'score': round(float(analysis.get('score', 5)), 1),
                'conditions': analysis.get('conditions', []),
                'reasoning': analysis.get('reasoning', ''),
                'market_dynamics': analysis.get('market_dynamics', ''),
                'model': 'claude',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Claude market analysis error: {e}")
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

        prompt = f"""Analyze the current state of the Korean stock market:

## Index Performance
**KOSPI:**
- Level: {kospi.get('current', 0):.2f}
- Change: {kospi.get('change_rate', 0):+.2f}%
- Volume: {kospi.get('volume', 0):,}

**KOSDAQ:**
- Level: {kosdaq.get('current', 0):.2f}
- Change: {kosdaq.get('change_rate', 0):+.2f}%
- Volume: {kosdaq.get('volume', 0):,}

## Market Breadth
- Advancing: {market_data.get('advancing', 0)} stocks
- Declining: {market_data.get('declining', 0)} stocks
- Unchanged: {market_data.get('unchanged', 0)} stocks
- Advance/Decline Ratio: {self._calculate_ad_ratio(market_data)}

## Analysis Request
Provide a comprehensive market sentiment analysis considering:
1. Index direction and momentum
2. Market breadth (advance/decline)
3. Volume characteristics
4. Risk-on vs risk-off sentiment
5. Sector rotation signals

Output as JSON with:
- sentiment: Bullish/Bearish/Neutral
- score: 0-10 (bearish to bullish)
- conditions: list of key market factors
- reasoning: detailed explanation
- market_dynamics: description of current market behavior"""

        return prompt

    def _calculate_ad_ratio(self, market_data: Dict[str, Any]) -> str:
        """
        Calculate advance/decline ratio
        """
        advancing = market_data.get('advancing', 0)
        declining = market_data.get('declining', 0)

        if declining > 0:
            ratio = advancing / declining
            return f"{ratio:.2f}"
        elif advancing > 0:
            return "∞ (no decliners)"
        else:
            return "N/A"

    def _get_default_response(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Default response when analysis fails
        """
        return {
            'signal': 'HOLD',
            'score': 5,
            'confidence': 'Low',
            'reasoning': 'Analysis failed - defaulting to HOLD',
            'bullish_factors': [],
            'bearish_factors': ['Analysis unavailable'],
            'risk_assessment': 'Unable to assess risk',
            'target_price': None,
            'stop_loss': None,
            'probability_success': 50,
            'key_levels': {},
            'market_regime': 'unknown',
            'model': 'claude',
            'timestamp': datetime.now().isoformat()
        }
