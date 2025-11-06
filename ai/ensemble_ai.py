"""
Ensemble AI System
Combines multiple AI models for superior predictions
"""

Features:
- Multiple AI model integration
- Weighted voting system
- Dynamic weight adjustment based on performance
- Meta-model for final decision
- Confidence aggregation
- Model selection based on market conditions
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModelPrediction:
    """Single model's prediction"""
    model_name: str
    action: str
    confidence: float
    expected_return: float
    reasoning: List[str]
    timestamp: str


@dataclass
class EnsemblePrediction:
    """Ensemble prediction result"""
    final_action: str
    final_confidence: float
    expected_return: float
    model_predictions: List[ModelPrediction]
    model_weights: Dict[str, float]
    consensus_score: float
    reasoning: List[str]
    timestamp: str


class EnsembleAI:
    """
    Ensemble AI system that combines multiple models

    Models included:
    - ML Price Predictor
    - RL Agent
    - AI Mode Agent
    - Technical Analysis
    - Sentiment Analysis
    """

    def __init__(self):
        """Initialize ensemble system"""
        self.model_weights = {
            'ml_predictor': 0.25,
            'rl_agent': 0.25,
            'ai_mode': 0.20,
            'technical': 0.15,
            'sentiment': 0.15
        }

        self.model_performance = defaultdict(lambda: {'correct': 0, 'total': 0, 'avg_return': 0.0})

        self.predictions_history: List[EnsemblePrediction] = []

        self.weights_file = Path('data/ensemble/model_weights.json')
        self.performance_file = Path('data/ensemble/model_performance.json')
        self.weights_file.parent.mkdir(parents=True, exist_ok=True)

        self._load_state()

    def _load_state(self):
        """Load saved state"""
        try:
            if self.weights_file.exists():
                with open(self.weights_file, 'r') as f:
                    self.model_weights = json.load(f)

            if self.performance_file.exists():
                with open(self.performance_file, 'r') as f:
                    data = json.load(f)
                    self.model_performance = defaultdict(
                        lambda: {'correct': 0, 'total': 0, 'avg_return': 0.0},
                        data
                    )

            logger.info("Ensemble AI state loaded")

        except Exception as e:
            logger.error(f"Error loading ensemble state: {e}")

    def _save_state(self):
        """Save state"""
        try:
            with open(self.weights_file, 'w') as f:
                json.dump(self.model_weights, f, indent=2)

            with open(self.performance_file, 'w') as f:
                json.dump(dict(self.model_performance), f, indent=2)

        except Exception as e:
            logger.error(f"Error saving ensemble state: {e}")

    def predict(
        self,
        stock_code: str,
        stock_name: str,
        market_data: Dict[str, Any]
    ) -> EnsemblePrediction:
        Make ensemble prediction

        Args:
            stock_code: Stock code
            stock_name: Stock name
            market_data: Market data

        Returns:
            Ensemble prediction
        try:
            model_predictions = []

            ml_pred = self._get_ml_prediction(stock_code, stock_name, market_data)
            if ml_pred:
                model_predictions.append(ml_pred)

            rl_pred = self._get_rl_prediction(market_data)
            if rl_pred:
                model_predictions.append(rl_pred)

            ai_pred = self._get_ai_mode_prediction(stock_code, stock_name, market_data)
            if ai_pred:
                model_predictions.append(ai_pred)

            tech_pred = self._get_technical_prediction(market_data)
            if tech_pred:
                model_predictions.append(tech_pred)

            sent_pred = self._get_sentiment_prediction(stock_code)
            if sent_pred:
                model_predictions.append(sent_pred)

            ensemble_pred = self._combine_predictions(model_predictions)

            self.predictions_history.append(ensemble_pred)
            if len(self.predictions_history) > 100:
                self.predictions_history = self.predictions_history[-100:]

            return ensemble_pred

        except Exception as e:
            logger.error(f"Error in ensemble prediction: {e}")
            return self._fallback_prediction(stock_code, stock_name)

    def _get_ml_prediction(
        self,
        stock_code: str,
        stock_name: str,
        data: Dict[str, Any]
    ) -> Optional[ModelPrediction]:
        try:
            from ai.ml_predictor import get_ml_predictor

            predictor = get_ml_predictor()
            prediction = predictor.predict(stock_code, stock_name, data)

            if prediction.direction == 'up':
                action = 'buy'
            elif prediction.direction == 'down':
                action = 'sell'
            else:
                action = 'hold'

            return ModelPrediction(
                model_name='ml_predictor',
                action=action,
                confidence=prediction.confidence,
                expected_return=prediction.expected_return,
                reasoning=[
                    f"ML 예측: {prediction.direction}",
                    f"예상 수익률: {prediction.expected_return:+.1f}%",
                    f"예측 구간: {prediction.prediction_interval_low:.0f} ~ {prediction.prediction_interval_high:.0f}"
                ],
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            logger.error(f"Error getting ML prediction: {e}")
            return None

    def _get_rl_prediction(self, data: Dict[str, Any]) -> Optional[ModelPrediction]:
        """Get RL agent prediction"""
        try:
            from ai.rl_agent import get_rl_agent, RLState

            agent = get_rl_agent()

            state = RLState(
                portfolio_value=data.get('portfolio_value', 10000000),
                cash_balance=data.get('cash_balance', 5000000),
                position_count=data.get('position_count', 0),
                current_price=data.get('price', 0),
                price_change_5m=data.get('price_change_5m', 0),
                price_change_1h=data.get('price_change_1h', 0),
                rsi=data.get('rsi', 50),
                macd=data.get('macd', 0),
                volume_ratio=data.get('volume_ratio', 1.0),
                market_trend=data.get('market_trend', 0),
                time_of_day=datetime.now().hour / 24
            )

            state_vec = agent._state_to_vector(state)
            action_idx = agent.act(state_vec)
            action_interp = agent.get_action_interpretation(action_idx)

            return ModelPrediction(
                model_name='rl_agent',
                action=action_interp.action_type,
                confidence=action_interp.confidence,
                expected_return=0.0,
                reasoning=[
                    f"RL 행동: {action_interp.action_type}",
                    f"수량: {action_interp.quantity}%",
                    f"탐험률: {agent.epsilon:.2f}"
                ],
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            logger.error(f"Error getting RL prediction: {e}")
            return None

    def _get_ai_mode_prediction(
        self,
        stock_code: str,
        stock_name: str,
        data: Dict[str, Any]
    ) -> Optional[ModelPrediction]:
        try:
            from features.ai_mode import get_ai_agent

            agent = get_ai_agent()

            if not agent.is_enabled():
                return None

            decision = agent.make_trading_decision(stock_code, stock_name, data)

            return ModelPrediction(
                model_name='ai_mode',
                action=decision.decision_type,
                confidence=decision.confidence,
                expected_return=0.0,
                reasoning=decision.reasoning,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            logger.error(f"Error getting AI mode prediction: {e}")
            return None

    def _get_technical_prediction(self, data: Dict[str, Any]) -> ModelPrediction:
        """Get technical analysis prediction"""
        try:
            rsi = data.get('rsi', 50)
            macd = data.get('macd', 0)
            volume_ratio = data.get('volume_ratio', 1.0)

            buy_signals = 0
            sell_signals = 0

            if rsi < 30:
                buy_signals += 2
            elif rsi < 45:
                buy_signals += 1
            elif rsi > 70:
                sell_signals += 2
            elif rsi > 55:
                sell_signals += 1

            if macd > 0:
                buy_signals += 1
            else:
                sell_signals += 1

            if volume_ratio > 1.5:
                buy_signals += 1

            if buy_signals > sell_signals:
                action = 'buy'
                confidence = min(0.9, 0.5 + (buy_signals - sell_signals) * 0.1)
            elif sell_signals > buy_signals:
                action = 'sell'
                confidence = min(0.9, 0.5 + (sell_signals - buy_signals) * 0.1)
            else:
                action = 'hold'
                confidence = 0.4

            return ModelPrediction(
                model_name='technical',
                action=action,
                confidence=confidence,
                expected_return=0.0,
                reasoning=[
                    f"기술적 신호: {buy_signals}개 매수, {sell_signals}개 매도",
                    f"RSI: {rsi:.1f}",
                    f"MACD: {macd:.1f}",
                    f"거래량 비율: {volume_ratio:.1f}x"
                ],
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            logger.error(f"Error getting technical prediction: {e}")
            return ModelPrediction(
                model_name='technical',
                action='hold',
                confidence=0.3,
                expected_return=0.0,
                reasoning=["기술적 분석 오류"],
                timestamp=datetime.now().isoformat()
            )

    def _get_sentiment_prediction(self, stock_code: str) -> Optional[ModelPrediction]:
        """Get sentiment analysis prediction"""
        try:
            from features.news_feed import NewsFeedService

            service = NewsFeedService()
            summary = service.get_news_summary(stock_code, stock_code)

            if not summary:
                return None

            if summary.overall_sentiment == 'positive':
                action = 'buy'
                confidence = 0.6 + (summary.avg_sentiment_score * 0.2)
            elif summary.overall_sentiment == 'negative':
                action = 'sell'
                confidence = 0.6 + (abs(summary.avg_sentiment_score) * 0.2)
            else:
                action = 'hold'
                confidence = 0.4

            return ModelPrediction(
                model_name='sentiment',
                action=action,
                confidence=confidence,
                expected_return=0.0,
                reasoning=[
                    f"뉴스 감성: {summary.overall_sentiment}",
                    f"긍정: {summary.positive_count}건, 부정: {summary.negative_count}건",
                    f"평균 점수: {summary.avg_sentiment_score:.2f}"
                ],
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            logger.error(f"Error getting sentiment prediction: {e}")
            return None

    def _combine_predictions(
        self,
        predictions: List[ModelPrediction]
    ) -> EnsemblePrediction:
        if not predictions:
            return self._fallback_prediction('unknown', 'unknown')

        action_scores = {'buy': 0.0, 'sell': 0.0, 'hold': 0.0}
        expected_returns = []
        all_reasoning = []

        for pred in predictions:
            weight = self.model_weights.get(pred.model_name, 0.1)
            action_scores[pred.action] += pred.confidence * weight

            if pred.expected_return != 0:
                expected_returns.append(pred.expected_return * weight)

            all_reasoning.extend(pred.reasoning)

        final_action = max(action_scores.items(), key=lambda x: x[1])[0]
        final_confidence = action_scores[final_action] / sum(action_scores.values())

        max_score = max(action_scores.values())
        total_score = sum(action_scores.values())
        consensus_score = max_score / total_score if total_score > 0 else 0

        expected_return = sum(expected_returns) if expected_returns else 0.0

        model_weights = {pred.model_name: self.model_weights.get(pred.model_name, 0.1)
                        for pred in predictions}

        return EnsemblePrediction(
            final_action=final_action,
            final_confidence=final_confidence,
            expected_return=expected_return,
            model_predictions=predictions,
            model_weights=model_weights,
            consensus_score=consensus_score,
            reasoning=all_reasoning,
            timestamp=datetime.now().isoformat()
        )

    def _fallback_prediction(
        self,
        stock_code: str,
        stock_name: str
    ) -> EnsemblePrediction:
        return EnsemblePrediction(
            final_action='hold',
            final_confidence=0.3,
            expected_return=0.0,
            model_predictions=[],
            model_weights={},
            consensus_score=0.0,
            reasoning=["Fallback prediction - models unavailable"],
            timestamp=datetime.now().isoformat()
        )

    def update_weights(self, prediction: EnsemblePrediction, actual_outcome: str, actual_return: float):
        """
        Update model weights based on prediction accuracy

        Args:
            prediction: Previous prediction
            actual_outcome: Actual outcome ('profit' or 'loss')
            actual_return: Actual return percentage
        """
        try:
            for model_pred in prediction.model_predictions:
                model_name = model_pred.model_name

                was_correct = False
                if actual_outcome == 'profit' and model_pred.action == 'buy':
                    was_correct = True
                elif actual_outcome == 'loss' and model_pred.action == 'sell':
                    was_correct = True

                self.model_performance[model_name]['total'] += 1
                if was_correct:
                    self.model_performance[model_name]['correct'] += 1

                prev_avg = self.model_performance[model_name]['avg_return']
                total = self.model_performance[model_name]['total']
                new_avg = ((prev_avg * (total - 1)) + actual_return) / total
                self.model_performance[model_name]['avg_return'] = new_avg

            self._recalculate_weights()

            self._save_state()

            logger.info("Ensemble weights updated")

        except Exception as e:
            logger.error(f"Error updating weights: {e}")

    def _recalculate_weights(self):
        """Recalculate model weights based on performance"""
        accuracies = {}
        for model_name, perf in self.model_performance.items():
            if perf['total'] > 0:
                accuracies[model_name] = perf['correct'] / perf['total']
            else:
                accuracies[model_name] = 0.5

        total_accuracy = sum(accuracies.values())
        if total_accuracy > 0:
            for model_name in self.model_weights.keys():
                if model_name in accuracies:
                    self.model_weights[model_name] = accuracies[model_name] / total_accuracy

    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report"""
        return {
            'model_weights': self.model_weights,
            'model_performance': dict(self.model_performance),
            'total_predictions': len(self.predictions_history),
            'recent_consensus': [
                p.consensus_score for p in self.predictions_history[-10:]
            ],
            'last_updated': datetime.now().isoformat()
        }


_ensemble_ai: Optional[EnsembleAI] = None


def get_ensemble_ai() -> EnsembleAI:
    """Get or create ensemble AI instance"""
    global _ensemble_ai
    if _ensemble_ai is None:
        _ensemble_ai = EnsembleAI()
    return _ensemble_ai


if __name__ == '__main__':
    ensemble = EnsembleAI()

    print("\n🎯 Ensemble AI System Test")
    print("=" * 60)

    market_data = {
        'price': 73500,
        'rsi': 55,
        'macd': 100,
        'volume_ratio': 1.3,
        'portfolio_value': 10000000,
        'cash_balance': 5000000,
        'position_count': 2
    }

    prediction = ensemble.predict('005930', '삼성전자', market_data)

    print(f"\n최종 결정: {prediction.final_action.upper()}")
    print(f"신뢰도: {prediction.final_confidence:.0%}")
    print(f"합의 점수: {prediction.consensus_score:.0%}")
    print(f"\n모델별 예측:")
    for model_pred in prediction.model_predictions:
        print(f"  - {model_pred.model_name}: {model_pred.action} ({model_pred.confidence:.0%})")
