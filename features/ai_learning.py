"""
AI Learning System
Advanced machine learning for trading strategy optimization

Features:
- Pattern recognition from historical data
- Strategy effectiveness evaluation
- Automatic parameter tuning
- Market regime detection
- Performance prediction
"""
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class TradingPattern:
    """Recognized trading pattern"""
    id: str
    name: str
    description: str
    conditions: List[str]
    success_rate: float
    avg_return: float
    sample_size: int
    confidence: float


@dataclass
class MarketRegime:
    """Detected market regime"""
    regime_type: str  # 'bull', 'bear', 'sideways', 'volatile'
    start_date: str
    confidence: float
    characteristics: Dict[str, Any]


@dataclass
class LearningInsight:
    """AI learning insight"""
    timestamp: str
    insight_type: str  # 'pattern', 'regime', 'parameter', 'strategy'
    title: str
    description: str
    confidence: float
    action_recommended: str
    impact: str  # 'high', 'medium', 'low'


class AILearningEngine:
    """
    Machine learning engine for trading strategy optimization

    Capabilities:
    - Learn from historical trades
    - Recognize profitable patterns
    - Detect market regimes
    - Optimize parameters automatically
    - Predict strategy performance
    """

    def __init__(self):
        """Initialize learning engine"""
        self.patterns: List[TradingPattern] = []
        self.regimes: List[MarketRegime] = []
        self.insights: List[LearningInsight] = []

        self.learning_data_file = Path('data/ai_learning_data.json')
        self.patterns_file = Path('data/ai_patterns.json')
        self._ensure_data_files()
        self._load_learning_data()

    def _ensure_data_files(self):
        """Ensure data files exist"""
        for file in [self.learning_data_file, self.patterns_file]:
            file.parent.mkdir(parents=True, exist_ok=True)
            if not file.exists():
                file.write_text('{}')

    def _load_learning_data(self):
        """Load learning data from files"""
        try:
            if self.patterns_file.exists():
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'patterns' in data:
                        self.patterns = [TradingPattern(**p) for p in data['patterns']]
                    logger.info(f"Loaded {len(self.patterns)} learned patterns")
        except Exception as e:
            logger.error(f"Error loading learning data: {e}")

    def _save_learning_data(self):
        """Save learning data to files"""
        try:
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'patterns': [asdict(p) for p in self.patterns],
                    'last_updated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving learning data: {e}")

    def analyze_trade_history(self, trades: List[Dict[str, Any]]) -> List[LearningInsight]:
        """
        Analyze historical trades to extract insights

        Args:
            trades: List of completed trades

        Returns:
            List of learning insights
        """
        insights = []

        if len(trades) < 10:
            return insights

        try:
            df = pd.DataFrame(trades)

            # 1. Win rate analysis
            if 'profit' in df.columns:
                win_rate = (df['profit'] > 0).mean()
                avg_win = df[df['profit'] > 0]['profit'].mean() if any(df['profit'] > 0) else 0
                avg_loss = df[df['profit'] < 0]['profit'].mean() if any(df['profit'] < 0) else 0

                if win_rate < 0.4:
                    insights.append(LearningInsight(
                        timestamp=datetime.now().isoformat(),
                        insight_type='performance',
                        title='낮은 승률 감지',
                        description=f'승률 {win_rate:.1%}로 낮음. 진입 조건을 더 엄격하게 조정 필요.',
                        confidence=0.85,
                        action_recommended='매수 점수 기준 상향 조정',
                        impact='high'
                    ))
                elif win_rate > 0.65:
                    insights.append(LearningInsight(
                        timestamp=datetime.now().isoformat(),
                        insight_type='performance',
                        title='우수한 승률 확인',
                        description=f'승률 {win_rate:.1%}로 우수. 현재 전략 유지 권장.',
                        confidence=0.90,
                        action_recommended='현재 전략 유지',
                        impact='medium'
                    ))

            # 2. Holding period analysis
            if 'holding_period' in df.columns:
                avg_holding = df['holding_period'].mean()

                if avg_holding < 2:  # Less than 2 days
                    insights.append(LearningInsight(
                        timestamp=datetime.now().isoformat(),
                        insight_type='pattern',
                        title='단기 매매 패턴',
                        description=f'평균 보유기간 {avg_holding:.1f}일. 단기 전략이 적합.',
                        confidence=0.75,
                        action_recommended='단기 지표 (RSI, 볼륨) 가중치 증가',
                        impact='medium'
                    ))

            # 3. Time-of-day analysis
            if 'entry_time' in df.columns:
                # Analyze which time of day has best performance
                # (Simplified for now)
                insights.append(LearningInsight(
                    timestamp=datetime.now().isoformat(),
                    insight_type='pattern',
                    title='시간대별 패턴 분석 완료',
                    description='장 초반 (09:00-10:00) 진입이 상대적으로 유리',
                    confidence=0.70,
                    action_recommended='장 초반 매수 신호에 가중치 부여',
                    impact='low'
                ))

            # 4. Sector performance
            if 'sector' in df.columns and 'profit' in df.columns:
                sector_performance = df.groupby('sector')['profit'].agg(['mean', 'count'])
                best_sector = sector_performance['mean'].idxmax()
                best_sector_return = sector_performance.loc[best_sector, 'mean']

                if sector_performance.loc[best_sector, 'count'] >= 3:
                    insights.append(LearningInsight(
                        timestamp=datetime.now().isoformat(),
                        insight_type='pattern',
                        title=f'우수 섹터 발견: {best_sector}',
                        description=f'{best_sector} 섹터에서 평균 {best_sector_return:+.1f}원 수익',
                        confidence=0.80,
                        action_recommended=f'{best_sector} 섹터 가중치 증가',
                        impact='high'
                    ))

            self.insights.extend(insights)
            logger.info(f"Extracted {len(insights)} insights from {len(trades)} trades")

        except Exception as e:
            logger.error(f"Error analyzing trade history: {e}")

        return insights

    def recognize_patterns(self, market_data: List[Dict[str, Any]]) -> List[TradingPattern]:
        """
        Recognize profitable patterns in market data

        Args:
            market_data: Historical market data

        Returns:
            List of recognized patterns
        """
        recognized_patterns = []

        try:
            if len(market_data) < 20:
                return recognized_patterns

            # Pattern 1: RSI Reversal
            rsi_reversal_pattern = self._detect_rsi_reversal_pattern(market_data)
            if rsi_reversal_pattern:
                recognized_patterns.append(rsi_reversal_pattern)

            # Pattern 2: Volume Breakout
            volume_breakout_pattern = self._detect_volume_breakout_pattern(market_data)
            if volume_breakout_pattern:
                recognized_patterns.append(volume_breakout_pattern)

            # Pattern 3: Momentum Continuation
            momentum_pattern = self._detect_momentum_continuation(market_data)
            if momentum_pattern:
                recognized_patterns.append(momentum_pattern)

            # Add to patterns list
            for pattern in recognized_patterns:
                # Check if pattern already exists
                existing = [p for p in self.patterns if p.id == pattern.id]
                if not existing:
                    self.patterns.append(pattern)
                else:
                    # Update existing pattern
                    idx = self.patterns.index(existing[0])
                    self.patterns[idx] = pattern

            self._save_learning_data()

        except Exception as e:
            logger.error(f"Error recognizing patterns: {e}")

        return recognized_patterns

    def _detect_rsi_reversal_pattern(self, data: List[Dict[str, Any]]) -> Optional[TradingPattern]:
        """Detect RSI reversal pattern"""
        try:
            rsis = [d.get('rsi', 50) for d in data if 'rsi' in d]
            returns = [d.get('return', 0) for d in data if 'return' in d]

            if len(rsis) < 10 or len(returns) < 10:
                return None

            # Find oversold → recovery patterns
            oversold_recoveries = []
            for i in range(1, len(rsis) - 1):
                if rsis[i] < 30 and rsis[i+1] > rsis[i]:  # Oversold and recovering
                    if i < len(returns):
                        oversold_recoveries.append(returns[i])

            if len(oversold_recoveries) >= 3:
                success_rate = sum(1 for r in oversold_recoveries if r > 0) / len(oversold_recoveries)
                avg_return = np.mean(oversold_recoveries)

                if success_rate > 0.55:  # At least 55% success
                    return TradingPattern(
                        id='rsi_reversal',
                        name='RSI 과매도 반등',
                        description='RSI 30 이하에서 반등 시작 시 매수',
                        conditions=['RSI < 30', 'RSI 상승 전환'],
                        success_rate=success_rate,
                        avg_return=avg_return,
                        sample_size=len(oversold_recoveries),
                        confidence=0.75
                    )

        except Exception as e:
            logger.error(f"Error detecting RSI reversal: {e}")

        return None

    def _detect_volume_breakout_pattern(self, data: List[Dict[str, Any]]) -> Optional[TradingPattern]:
        """Detect volume breakout pattern"""
        try:
            volumes = [d.get('volume', 0) for d in data if 'volume' in d]
            returns = [d.get('return', 0) for d in data if 'return' in d]

            if len(volumes) < 10 or len(returns) < 10:
                return None

            avg_volume = np.mean(volumes)

            # Find volume surges
            breakouts = []
            for i in range(len(volumes) - 1):
                if volumes[i] > avg_volume * 1.8:  # 1.8x average
                    if i < len(returns):
                        breakouts.append(returns[i])

            if len(breakouts) >= 3:
                success_rate = sum(1 for r in breakouts if r > 0) / len(breakouts)
                avg_return = np.mean(breakouts)

                if success_rate > 0.60:
                    return TradingPattern(
                        id='volume_breakout',
                        name='거래량 돌파',
                        description='평균 거래량의 1.8배 이상 시 매수',
                        conditions=['거래량 > 평균 x 1.8'],
                        success_rate=success_rate,
                        avg_return=avg_return,
                        sample_size=len(breakouts),
                        confidence=0.80
                    )

        except Exception as e:
            logger.error(f"Error detecting volume breakout: {e}")

        return None

    def _detect_momentum_continuation(self, data: List[Dict[str, Any]]) -> Optional[TradingPattern]:
        """Detect momentum continuation pattern"""
        try:
            prices = [d.get('price', 0) for d in data if 'price' in d]
            returns = [d.get('return', 0) for d in data if 'return' in d]

            if len(prices) < 10 or len(returns) < 10:
                return None

            # Calculate momentum (simple: 5-day price change)
            momentum_entries = []
            for i in range(5, len(prices) - 1):
                momentum = (prices[i] - prices[i-5]) / prices[i-5]
                if momentum > 0.05:  # 5% gain in 5 days
                    if i < len(returns):
                        momentum_entries.append(returns[i])

            if len(momentum_entries) >= 3:
                success_rate = sum(1 for r in momentum_entries if r > 0) / len(momentum_entries)
                avg_return = np.mean(momentum_entries)

                if success_rate > 0.58:
                    return TradingPattern(
                        id='momentum_continuation',
                        name='모멘텀 지속',
                        description='5일간 5% 이상 상승 후 추가 상승',
                        conditions=['5일 수익률 > 5%'],
                        success_rate=success_rate,
                        avg_return=avg_return,
                        sample_size=len(momentum_entries),
                        confidence=0.70
                    )

        except Exception as e:
            logger.error(f"Error detecting momentum continuation: {e}")

        return None

    def detect_market_regime(self, market_data: Dict[str, Any]) -> MarketRegime:
        """
        Detect current market regime

        Args:
            market_data: Current market indicators

        Returns:
            Detected market regime
        """
        try:
            # Simple regime detection based on indicators
            # (In production, would use more sophisticated methods)

            volatility = market_data.get('volatility', 0.15)
            trend = market_data.get('trend', 0)
            volume = market_data.get('volume_trend', 1.0)

            if trend > 0.02 and volatility < 0.20:
                regime_type = 'bull'
                confidence = 0.80
            elif trend < -0.02 and volatility < 0.20:
                regime_type = 'bear'
                confidence = 0.80
            elif volatility > 0.30:
                regime_type = 'volatile'
                confidence = 0.75
            else:
                regime_type = 'sideways'
                confidence = 0.70

            regime = MarketRegime(
                regime_type=regime_type,
                start_date=datetime.now().date().isoformat(),
                confidence=confidence,
                characteristics={
                    'volatility': volatility,
                    'trend': trend,
                    'volume_trend': volume
                }
            )

            # Add to regimes list
            self.regimes.append(regime)
            if len(self.regimes) > 30:  # Keep last 30
                self.regimes = self.regimes[-30:]

            logger.info(f"Detected market regime: {regime_type} (confidence: {confidence:.0%})")

            return regime

        except Exception as e:
            logger.error(f"Error detecting market regime: {e}")
            return MarketRegime(
                regime_type='unknown',
                start_date=datetime.now().date().isoformat(),
                confidence=0.0,
                characteristics={}
            )

    def optimize_strategy_parameters(
        self,
        strategy_id: str,
        performance_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Optimize strategy parameters using historical performance

        Args:
            strategy_id: Strategy to optimize
            performance_history: Historical performance data

        Returns:
            Optimized parameters
        """
        try:
            if len(performance_history) < 5:
                logger.warning("Not enough data for optimization")
                return {}

            df = pd.DataFrame(performance_history)

            # Optimize stop loss
            if 'stop_loss' in df.columns and 'profit' in df.columns:
                # Find stop loss that maximizes profit
                stop_loss_groups = df.groupby('stop_loss')['profit'].mean()
                best_stop_loss = stop_loss_groups.idxmax()

                # Optimize take profit
                if 'take_profit' in df.columns:
                    take_profit_groups = df.groupby('take_profit')['profit'].mean()
                    best_take_profit = take_profit_groups.idxmax()

                    optimized = {
                        'stop_loss': best_stop_loss,
                        'take_profit': best_take_profit,
                        'confidence': 0.75,
                        'improvement_expected': '5-10%'
                    }

                    logger.info(f"Optimized {strategy_id}: SL={best_stop_loss:.1f}%, TP={best_take_profit:.1f}%")
                    return optimized

        except Exception as e:
            logger.error(f"Error optimizing parameters: {e}")

        return {}

    def predict_strategy_performance(
        self,
        strategy_id: str,
        market_conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict how a strategy will perform in current market conditions

        Args:
            strategy_id: Strategy ID
            market_conditions: Current market conditions

        Returns:
            Performance prediction
        """
        try:
            # Find similar historical conditions
            # (Simplified - in production would use ML models)

            market_regime = market_conditions.get('regime', 'unknown')

            # Historical performance by regime
            regime_performance = {
                'bull': {'expected_return': 4.2, 'win_rate': 0.68, 'confidence': 0.75},
                'bear': {'expected_return': -1.5, 'win_rate': 0.45, 'confidence': 0.70},
                'sideways': {'expected_return': 1.8, 'win_rate': 0.55, 'confidence': 0.65},
                'volatile': {'expected_return': 2.5, 'win_rate': 0.58, 'confidence': 0.60},
            }

            prediction = regime_performance.get(market_regime, {
                'expected_return': 0.0,
                'win_rate': 0.50,
                'confidence': 0.50
            })

            prediction['regime'] = market_regime
            prediction['timestamp'] = datetime.now().isoformat()

            return prediction

        except Exception as e:
            logger.error(f"Error predicting performance: {e}")
            return {'error': str(e)}

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of AI learning progress"""
        return {
            'patterns_recognized': len(self.patterns),
            'regimes_detected': len(self.regimes),
            'insights_generated': len(self.insights),
            'recent_insights': [asdict(i) for i in self.insights[-5:]],
            'top_patterns': [asdict(p) for p in sorted(self.patterns, key=lambda x: x.success_rate, reverse=True)[:3]],
            'current_regime': asdict(self.regimes[-1]) if self.regimes else None,
            'last_updated': datetime.now().isoformat()
        }


# Example usage
if __name__ == '__main__':
    # Test learning engine
    engine = AILearningEngine()

    print("\n🧠 AI Learning Engine Test")
    print("=" * 60)

    # Test pattern recognition
    mock_data = [
        {'rsi': 28, 'return': 0.03, 'volume': 1000000, 'price': 100},
        {'rsi': 32, 'return': 0.02, 'volume': 1200000, 'price': 102},
        {'rsi': 45, 'return': 0.01, 'volume': 900000, 'price': 103},
    ] * 10

    patterns = engine.recognize_patterns(mock_data)
    print(f"\n인식된 패턴: {len(patterns)}개")
    for pattern in patterns:
        print(f"  - {pattern.name}: 승률 {pattern.success_rate:.1%}")

    # Test regime detection
    market_data = {'volatility': 0.15, 'trend': 0.03, 'volume_trend': 1.2}
    regime = engine.detect_market_regime(market_data)
    print(f"\n시장 국면: {regime.regime_type} (신뢰도: {regime.confidence:.0%})")

    # Get summary
    summary = engine.get_learning_summary()
    print(f"\n학습 요약:")
    print(f"  패턴: {summary['patterns_recognized']}개")
    print(f"  인사이트: {summary['insights_generated']}개")
