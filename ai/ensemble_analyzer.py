"""
Gemini Ensemble Analyzer
Gemini 전용 고급 분석 시스템 (다중 전략 투표)
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import statistics
from enum import Enum

from .base_analyzer import BaseAnalyzer
from .gemini_analyzer import GeminiAnalyzer
from utils.logger_new import get_logger

logger = get_logger()


class AIModel(Enum):
    """AI Model types (Gemini only)"""
    GEMINI = "gemini"


class VotingStrategy(Enum):
    """Ensemble voting strategies"""
    MAJORITY = "majority"
    WEIGHTED = "weighted"
    UNANIMOUS = "unanimous"
    BEST_PERFORMER = "best_performer"


class EnsembleAnalyzer(BaseAnalyzer):
    """
    Gemini 전용 앙상블 분석기
    Features:
    - 단일 Gemini 모델 사용
    - 신뢰도 기반 가중치
    - 성능 추적
    - 적응형 분석
    """

    def __init__(
        self,
        voting_strategy: VotingStrategy = VotingStrategy.WEIGHTED
    ):
        """
        Initialize ensemble analyzer (Gemini only)

        Args:
            voting_strategy: Strategy for combining model outputs (kept for compatibility)
        super().__init__(name="GeminiEnsembleAnalyzer", config={})
        self.voting_strategy = voting_strategy

        self.analyzers: Dict[AIModel, BaseAnalyzer] = {}

        try:
            self.analyzers[AIModel.GEMINI] = GeminiAnalyzer()
            logger.info("✓ Gemini analyzer initialized (Primary AI)")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")

        self.model_performance: Dict[AIModel, Dict[str, float]] = {
            model: {
                'accuracy': 0.5,
                'total_predictions': 0,
                'correct_predictions': 0,
                'avg_confidence': 0.0
            }
            for model in self.analyzers.keys()
        }

        logger.info(f"Ensemble Analyzer initialized with {len(self.analyzers)} models")
        strategy_name = voting_strategy.value if isinstance(voting_strategy, VotingStrategy) else str(voting_strategy)
        logger.info(f"Voting strategy: {strategy_name}")

    def initialize(self) -> bool:
        """
        Initialize ensemble analyzer

        Returns:
            True if initialization successful
        """
        try:
            for model_type, analyzer in self.analyzers.items():
                """
                if hasattr(analyzer, 'initialize'):
                    analyzer.initialize()

            self.is_initialized = True
            logger.info("Ensemble analyzer initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize ensemble analyzer: {e}")
            self.is_initialized = False
            return False

    async def analyze_stock_async(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze stock using all available models asynchronously

        Args:
            stock_data: Stock information

        Returns:
            Ensemble analysis results
        """
        if not self.analyzers:
            logger.error("No AI models available")
            return self._get_default_analysis()

        tasks = []
        for model_type, analyzer in self.analyzers.items():
            """
            task = self._analyze_with_model(model_type, analyzer, stock_data)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_results = []
        for i, result in enumerate(results):
            """
            if isinstance(result, Exception):
                model_type = list(self.analyzers.keys())[i]
                logger.error(f"{model_type.value} analysis failed: {result}")
            else:
                valid_results.append(result)

        if not valid_results:
            logger.error("All models failed")
            return self._get_default_analysis()

        ensemble_result = self._combine_results(valid_results, stock_data)

        return ensemble_result

    def analyze_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronous wrapper for analyze_stock_async
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.analyze_stock_async(stock_data))

    async def _analyze_with_model(
        self,
        model_type: AIModel,
        analyzer: BaseAnalyzer,
        stock_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze stock with a specific model
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                analyzer.analyze_stock,
                stock_data
            )

            result['model'] = model_type.value
            result['model_performance'] = self.model_performance[model_type]['accuracy']

            return result

        except Exception as e:
            logger.error(f"Error in {model_type.value} analysis: {e}")
            raise

    def _combine_results(
        self,
        results: List[Dict[str, Any]],
        stock_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Combine multiple model results using voting strategy
        if self.voting_strategy == VotingStrategy.MAJORITY:
            return self._majority_vote(results, stock_data)
        elif self.voting_strategy == VotingStrategy.WEIGHTED:
            return self._weighted_average(results, stock_data)
        elif self.voting_strategy == VotingStrategy.UNANIMOUS:
            return self._unanimous_vote(results, stock_data)
        elif self.voting_strategy == VotingStrategy.BEST_PERFORMER:
            return self._best_performer(results, stock_data)
        else:
            return self._weighted_average(results, stock_data)

    def _majority_vote(
        self,
        results: List[Dict[str, Any]],
        stock_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simple majority voting
        signals = [r.get('signal', 'HOLD') for r in results]

        buy_votes = signals.count('BUY')
        sell_votes = signals.count('SELL')
        hold_votes = signals.count('HOLD')

        if buy_votes > sell_votes and buy_votes > hold_votes:
            final_signal = 'BUY'
        elif sell_votes > buy_votes and sell_votes > hold_votes:
            final_signal = 'SELL'
        else:
            final_signal = 'HOLD'

        scores = [r.get('score', 5) for r in results]
        avg_score = statistics.mean(scores)

        return {
            'signal': final_signal,
            'score': round(avg_score, 2),
            'confidence': self._calculate_confidence(results),
            'reasoning': self._combine_reasoning(results),
            'model_votes': {
                'BUY': buy_votes,
                'SELL': sell_votes,
                'HOLD': hold_votes
            },
            'individual_results': results,
            'voting_strategy': 'majority',
            'timestamp': datetime.now().isoformat()
        }

    def _weighted_average(
        self,
        results: List[Dict[str, Any]],
        stock_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Confidence and performance weighted averaging
        total_weight = 0
        weighted_score = 0
        signal_weights = {'BUY': 0, 'SELL': 0, 'HOLD': 0}

        for result in results:
            model_name = result.get('model', 'unknown')
            model_enum = None
            for m in AIModel:
                if m.value == model_name:
                    model_enum = m
                    break

            if model_enum and model_enum in self.model_performance:
                performance = self.model_performance[model_enum]['accuracy']
            else:
                performance = 0.5

            confidence_map = {'High': 1.0, 'Medium': 0.7, 'Low': 0.4}
            confidence = confidence_map.get(result.get('confidence', 'Medium'), 0.7)

            weight = performance * confidence
            total_weight += weight

            score = result.get('score', 5)
            weighted_score += score * weight

            signal = result.get('signal', 'HOLD')
            signal_weights[signal] += weight

        if total_weight > 0:
            final_score = weighted_score / total_weight
        else:
            final_score = 5.0

        final_signal = max(signal_weights, key=signal_weights.get)

        max_weight = signal_weights[final_signal]
        confidence_pct = (max_weight / total_weight * 100) if total_weight > 0 else 50

        if confidence_pct >= 80:
            final_confidence = 'High'
        elif confidence_pct >= 60:
            final_confidence = 'Medium'
        else:
            final_confidence = 'Low'

        return {
            'signal': final_signal,
            'score': round(final_score, 2),
            'confidence': final_confidence,
            'confidence_pct': round(confidence_pct, 1),
            'reasoning': self._combine_reasoning(results),
            'signal_weights': {k: round(v, 2) for k, v in signal_weights.items()},
            'individual_results': results,
            'voting_strategy': 'weighted',
            'timestamp': datetime.now().isoformat()
        }

    def _unanimous_vote(
        self,
        results: List[Dict[str, Any]],
        stock_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Only buy/sell if all models agree
        signals = [r.get('signal', 'HOLD') for r in results]

        if len(set(signals)) == 1:
            final_signal = signals[0]
            final_confidence = 'High'
        else:
            final_signal = 'HOLD'
            final_confidence = 'Low'

        scores = [r.get('score', 5) for r in results]
        avg_score = statistics.mean(scores)

        return {
            'signal': final_signal,
            'score': round(avg_score, 2),
            'confidence': final_confidence,
            'reasoning': self._combine_reasoning(results),
            'agreement': len(set(signals)) == 1,
            'individual_results': results,
            'voting_strategy': 'unanimous',
            'timestamp': datetime.now().isoformat()
        }

    def _best_performer(
        self,
        results: List[Dict[str, Any]],
        stock_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use the historically best performing model
        best_result = None
        best_accuracy = 0

        for result in results:
            model_name = result.get('model', 'unknown')
            model_enum = None
            for m in AIModel:
                if m.value == model_name:
                    model_enum = m
                    break

            if model_enum and model_enum in self.model_performance:
                accuracy = self.model_performance[model_enum]['accuracy']
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_result = result

        if best_result is None:
            best_result = results[0]

        best_result['voting_strategy'] = 'best_performer'
        best_result['selected_model_accuracy'] = round(best_accuracy, 3)
        best_result['all_results'] = results

        return best_result

    def _calculate_confidence(self, results: List[Dict[str, Any]]) -> str:
        """
        Calculate overall confidence from multiple results
        """
        confidence_map = {'High': 3, 'Medium': 2, 'Low': 1}
        confidences = [
            confidence_map.get(r.get('confidence', 'Medium'), 2)
            for r in results
        ]

        avg_confidence = statistics.mean(confidences)

        if avg_confidence >= 2.5:
            return 'High'
        elif avg_confidence >= 1.5:
            return 'Medium'
        else:
            return 'Low'

    def _combine_reasoning(self, results: List[Dict[str, Any]]) -> str:
        """
        Combine reasoning from multiple models
        """
        reasoning_parts = []

        for i, result in enumerate(results, 1):
            """
            model = result.get('model', f'Model{i}')
            signal = result.get('signal', 'HOLD')
            score = result.get('score', 5)
            reasoning = result.get('reasoning', 'No reasoning provided')

            if len(reasoning) > 150:
                reasoning = reasoning[:150] + "..."

            reasoning_parts.append(
                f"[{model.upper()}] {signal} (Score: {score}) - {reasoning}"
            )

        return " | ".join(reasoning_parts)

    def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze overall market using ensemble
        """
        if not self.analyzers:
            return self._get_default_market_analysis()

        results = []
        for model_type, analyzer in self.analyzers.items():
            """
            try:
                result = analyzer.analyze_market(market_data)
                result['model'] = model_type.value
                results.append(result)
            except Exception as e:
                logger.error(f"{model_type.value} market analysis failed: {e}")

        if not results:
            return self._get_default_market_analysis()

        sentiments = [r.get('sentiment', 'Neutral') for r in results]
        sentiment_votes = {
            'Bullish': sentiments.count('Bullish'),
            'Bearish': sentiments.count('Bearish'),
            'Neutral': sentiments.count('Neutral')
        }
        final_sentiment = max(sentiment_votes, key=sentiment_votes.get)

        scores = [r.get('score', 5) for r in results]
        avg_score = statistics.mean(scores)

        return {
            'sentiment': final_sentiment,
            'score': round(avg_score, 2),
            'sentiment_votes': sentiment_votes,
            'conditions': self._combine_conditions(results),
            'individual_results': results,
            'timestamp': datetime.now().isoformat()
        }

    def analyze_portfolio(
        self,
        portfolio_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze portfolio using ensemble

        Args:
            portfolio_data: Portfolio information

        Returns:
            Portfolio analysis results
        """
        if not self.analyzers:
            return {
                'score': 5,
                'health': 'Unknown',
                'recommendations': ['No AI models available'],
                'risks': [],
                'timestamp': datetime.now().isoformat()
            }

        results = []
        for model_type, analyzer in self.analyzers.items():
            """
            try:
                if hasattr(analyzer, 'analyze_portfolio'):
                    """
                    result = analyzer.analyze_portfolio(portfolio_data)
                    result['model'] = model_type.value
                    results.append(result)
            except Exception as e:
                logger.error(f"{model_type.value} portfolio analysis failed: {e}")

        if not results:
            return {
                'score': 5,
                'health': 'Unknown',
                'recommendations': ['Portfolio analysis unavailable'],
                'risks': [],
                'timestamp': datetime.now().isoformat()
            }

        scores = [r.get('score', 5) for r in results]
        avg_score = statistics.mean(scores)

        if avg_score >= 7.5:
            health = 'Excellent'
        elif avg_score >= 6.0:
            health = 'Good'
        elif avg_score >= 4.5:
            health = 'Fair'
        else:
            health = 'Poor'

        all_recommendations = []
        all_risks = []
        for result in results:
            all_recommendations.extend(result.get('recommendations', []))
            all_risks.extend(result.get('risks', []))

        unique_recommendations = list(set(all_recommendations))[:10]
        unique_risks = list(set(all_risks))[:10]

        return {
            'score': round(avg_score, 2),
            'health': health,
            'recommendations': unique_recommendations,
            'risks': unique_risks,
            'individual_results': results,
            'timestamp': datetime.now().isoformat()
        }

    def _combine_conditions(self, results: List[Dict[str, Any]]) -> List[str]:
        """
        Combine market conditions from multiple models
        """
        all_conditions = []
        for result in results:
            conditions = result.get('conditions', [])
            all_conditions.extend(conditions)

        unique_conditions = []
        seen = set()
        for condition in all_conditions:
            if condition not in seen:
                seen.add(condition)
                unique_conditions.append(condition)

        return unique_conditions[:10]

    def update_model_performance(
        self,
        model: AIModel,
        was_correct: bool,
        confidence: str
    ):
        """
        Update performance tracking for a model

        Args:
            model: The AI model
            was_correct: Whether the prediction was correct
            confidence: The confidence level of the prediction
        if model not in self.model_performance:
            return

        perf = self.model_performance[model]
        perf['total_predictions'] += 1
        if was_correct:
            perf['correct_predictions'] += 1

        perf['accuracy'] = perf['correct_predictions'] / perf['total_predictions']

        confidence_map = {'High': 1.0, 'Medium': 0.7, 'Low': 0.4}
        conf_value = confidence_map.get(confidence, 0.7)

        current_avg = perf['avg_confidence']
        total = perf['total_predictions']
        perf['avg_confidence'] = (current_avg * (total - 1) + conf_value) / total

        logger.info(
            f"Updated {model.value} performance: "
            f"Accuracy={perf['accuracy']:.2%}, "
            f"Total={total}"
        )

    def get_model_rankings(self) -> List[Dict[str, Any]]:
        """
        Get current model performance rankings
        """
        rankings = []
        for model, perf in self.model_performance.items():
            """
            rankings.append({
                'model': model.value,
                'accuracy': round(perf['accuracy'], 3),
                'total_predictions': perf['total_predictions'],
                'correct_predictions': perf['correct_predictions'],
                'avg_confidence': round(perf['avg_confidence'], 3)
            })

        rankings.sort(key=lambda x: x['accuracy'], reverse=True)
        return rankings

    def _get_default_analysis(self) -> Dict[str, Any]:
        """Default analysis when all models fail"""
        return {
            'signal': 'HOLD',
            'score': 5,
            'confidence': 'Low',
            'reasoning': 'All AI models unavailable - defaulting to HOLD',
            'timestamp': datetime.now().isoformat()
        }

    def _get_default_market_analysis(self) -> Dict[str, Any]:
        """Default market analysis when all models fail"""
        return {
            'sentiment': 'Neutral',
            'score': 5,
            'conditions': ['Market analysis unavailable'],
            'timestamp': datetime.now().isoformat()
        }


_analyzer_instance: Optional[EnsembleAnalyzer] = None


def get_analyzer(
    voting_strategy: VotingStrategy = VotingStrategy.WEIGHTED
) -> EnsembleAnalyzer:
    """
    Get singleton instance of EnsembleAnalyzer (Gemini only)

    Args:
        voting_strategy: Strategy for combining model outputs

    Returns:
        EnsembleAnalyzer instance
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = EnsembleAnalyzer(
            voting_strategy=voting_strategy
        )
    return _analyzer_instance
