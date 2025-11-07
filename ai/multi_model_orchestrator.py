"""
Multi-Model AI Orchestrator v1.0
여러 AI 모델을 조합하여 분석 정확도 향상
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from statistics import mean, stdev

from utils.logger_new import get_logger
from utils.advanced_performance_monitor import track_execution_time

logger = get_logger()


@dataclass
class ModelPrediction:
    """개별 모델 예측 결과"""
    model_name: str
    signal: str
    confidence_score: float
    overall_score: float
    reasons: List[str]
    risks: List[str]
    target_price: Optional[float]
    stop_loss: Optional[float]
    detailed_reasoning: str
    execution_time: float
    timestamp: datetime


@dataclass
class ConsensusAnalysis:
    """통합 분석 결과"""
    final_signal: str
    consensus_confidence: float
    consensus_score: float
    agreement_level: float
    model_predictions: List[ModelPrediction]
    combined_reasons: List[str]
    combined_risks: List[str]
    target_price_range: tuple
    stop_loss_consensus: float
    disagreement_factors: List[str]
    recommendation: str


class MultiModelOrchestrator:
    """
    멀티모델 AI 오케스트레이터

    Features:
    - Multiple AI models for cross-verification
    - Consensus-based decision making
    - Confidence scoring and weighting
    - Disagreement detection and analysis
    - Performance tracking per model
    """

    def __init__(self):
        """
        """
        self.models: Dict[str, Any] = {}
        self.model_performance: Dict[str, Dict[str, float]] = {}

        logger.info("MultiModelOrchestrator initialized")

    def register_model(self, name: str, analyzer_instance, weight: float = 1.0):
        """모델 등록"""
        self.models[name] = {
            'analyzer': analyzer_instance,
            'weight': weight,
            'enabled': True
        }

        self.model_performance[name] = {
            'total_calls': 0,
            'successful_calls': 0,
            'avg_execution_time': 0.0,
            'avg_confidence': 0.0
        }

        logger.info(f"Registered model: {name} (weight={weight})")

    @track_execution_time("MultiModelOrchestrator.analyze_stock_consensus")
    async def analyze_stock_consensus(
        self,
        stock_data: Dict[str, Any],
        technical_indicators: Dict[str, Any],
        market_data: Dict[str, Any],
        portfolio_info: Optional[str] = None
    ) -> ConsensusAnalysis:
        """
        여러 모델을 사용한 합의 기반 분석

        Args:
            stock_data: 종목 데이터
            technical_indicators: 기술적 지표
            market_data: 시장 데이터
            portfolio_info: 포트폴리오 정보

        Returns:
            ConsensusAnalysis: 통합 분석 결과
        """
        enabled_models = {
            name: model for name, model in self.models.items()
            if model['enabled']
        }

        if not enabled_models:
            raise ValueError("No enabled models available")

        tasks = []
        model_names = []

        for name, model_info in enabled_models.items():
            task = self._analyze_with_model(
                name,
                model_info['analyzer'],
                stock_data,
                technical_indicators,
                market_data,
                portfolio_info
            )
            tasks.append(task)
            model_names.append(name)

"""
        predictions = await asyncio.gather(*tasks, return_exceptions=True)

        valid_predictions = []
        for pred in predictions:
            if isinstance(pred, ModelPrediction):
                valid_predictions.append(pred)
            elif isinstance(pred, Exception):
                logger.error(f"Model prediction failed: {pred}")

        if not valid_predictions:
            raise ValueError("All model predictions failed")

        consensus = self._calculate_consensus(valid_predictions, enabled_models)

        return consensus

    async def _analyze_with_model(
        self,
        model_name: str,
        analyzer,
        stock_data: Dict[str, Any],
        technical_indicators: Dict[str, Any],
        market_data: Dict[str, Any],
        portfolio_info: Optional[str]
    ) -> ModelPrediction:
        """개별 모델로 분석"""
        import time

        start_time = time.time()

        try:
            self.model_performance[model_name]['total_calls'] += 1

            if hasattr(analyzer, 'analyze_stock_async'):
                result = await analyzer.analyze_stock_async(
                """
                    stock_data=stock_data,
                    technical_indicators=technical_indicators,
                    market_data=market_data,
                    portfolio_info=portfolio_info
                )
            elif hasattr(analyzer, 'analyze_stock'):
                result = analyzer.analyze_stock(
                """
                    stock_data=stock_data,
                    technical_indicators=technical_indicators,
                    market_data=market_data,
                    portfolio_info=portfolio_info
                )
            else:
                raise AttributeError(f"Model {model_name} has no analyze method")

            execution_time = time.time() - start_time

            prediction = ModelPrediction(
                model_name=model_name,
                signal=result.get('signal', 'hold'),
                confidence_score=result.get('confidence_score', 50.0),
                overall_score=result.get('overall_score', 5.0),
                reasons=result.get('reasons', []),
                risks=result.get('risks', []),
                target_price=result.get('target_price'),
                stop_loss=result.get('stop_loss'),
                detailed_reasoning=result.get('detailed_reasoning', ''),
                execution_time=execution_time,
                timestamp=datetime.now()
            )

            self.model_performance[model_name]['successful_calls'] += 1
            self.model_performance[model_name]['avg_execution_time'] = (
                (self.model_performance[model_name]['avg_execution_time'] *
                 (self.model_performance[model_name]['successful_calls'] - 1) +
                 execution_time) /
                self.model_performance[model_name]['successful_calls']
            )
            self.model_performance[model_name]['avg_confidence'] = (
                (self.model_performance[model_name]['avg_confidence'] *
                 (self.model_performance[model_name]['successful_calls'] - 1) +
                 prediction.confidence_score) /
                self.model_performance[model_name]['successful_calls']
            )

            return prediction

        except Exception as e:
            logger.error(f"Model {model_name} analysis failed: {e}")
            raise

    def _calculate_consensus(
        self,
        predictions: List[ModelPrediction],
        models: Dict[str, Dict]
    ) -> ConsensusAnalysis:
        """합의 계산"""
        signal_votes = {}
        weighted_scores = []
        all_reasons = []
        all_risks = []
        target_prices = []
        stop_losses = []

        for pred in predictions:
            model_weight = models[pred.model_name]['weight']

            signal_votes[pred.signal] = signal_votes.get(pred.signal, 0) + model_weight
            weighted_scores.append(pred.overall_score * model_weight)
            all_reasons.extend(pred.reasons)
            all_risks.extend(pred.risks)

            if pred.target_price:
                target_prices.append(pred.target_price)
            if pred.stop_loss:
                stop_losses.append(pred.stop_loss)

        final_signal = max(signal_votes, key=signal_votes.get)

        total_weight = sum(models[pred.model_name]['weight'] for pred in predictions)
        consensus_score = sum(weighted_scores) / total_weight if total_weight > 0 else 5.0

        agreement_level = signal_votes[final_signal] / total_weight if total_weight > 0 else 0.0

        consensus_confidence = mean([p.confidence_score for p in predictions])

        combined_reasons = list(set(all_reasons))[:5]
        combined_risks = list(set(all_risks))[:3]

        if target_prices:
            target_price_range = (min(target_prices), max(target_prices))
        else:
            target_price_range = (0, 0)

        stop_loss_consensus = mean(stop_losses) if stop_losses else 0

        disagreement_factors = []
        if len(signal_votes) > 1:
            for signal, votes in signal_votes.items():
                if signal != final_signal:
                """
                    models_disagreeing = [
                        p.model_name for p in predictions if p.signal == signal
                    ]
                    disagreement_factors.append(
                        f"{', '.join(models_disagreeing)} 모델(들)은 {signal} 신호를 제시"
                    )

        if target_prices and len(target_prices) > 1:
            price_stdev = stdev(target_prices)
            if price_stdev / mean(target_prices) > 0.1:
                disagreement_factors.append(
                    f"목표가 편차 큼: {min(target_prices):,.0f}원 ~ {max(target_prices):,.0f}원"
                )

        recommendation = self._generate_recommendation(
            final_signal,
            consensus_confidence,
            agreement_level,
            disagreement_factors
        )

        return ConsensusAnalysis(
            final_signal=final_signal,
            consensus_confidence=consensus_confidence,
            consensus_score=consensus_score,
            agreement_level=agreement_level,
            model_predictions=predictions,
            combined_reasons=combined_reasons,
            combined_risks=combined_risks,
            target_price_range=target_price_range,
            stop_loss_consensus=stop_loss_consensus,
            disagreement_factors=disagreement_factors,
            recommendation=recommendation
        )

    def _generate_recommendation(
        self,
        signal: str,
        confidence: float,
        agreement: float,
        disagreements: List[str]
    ) -> str:
        """추천 생성"""
        if signal == 'buy':
            if agreement >= 0.8 and confidence >= 70:
                return "강력 매수 추천 - 모든 모델이 일치된 견해"
            elif agreement >= 0.6:
                return "매수 추천 - 다수 모델 합의"
            else:
                return "주의 매수 - 모델 간 의견 차이 존재, 신중한 접근 필요"

        elif signal == 'sell':
            if agreement >= 0.8 and confidence >= 70:
                return "강력 매도 추천 - 모든 모델이 일치된 견해"
            elif agreement >= 0.6:
                return "매도 추천 - 다수 모델 합의"
            else:
                return "주의 매도 - 모델 간 의견 차이 존재"

        else:
            if confidence >= 60:
                return "보유 추천 - 관망이 유리"
            else:
                return "보유 (불확실성 높음) - 추가 분석 필요"

    def get_model_performance(self) -> Dict[str, Any]:
        """모델 성능 조회"""
        performance_summary = {}

        for model_name, perf in self.model_performance.items():
            success_rate = (
                perf['successful_calls'] / max(perf['total_calls'], 1) * 100
            )

"""
            performance_summary[model_name] = {
                'total_calls': perf['total_calls'],
                'successful_calls': perf['successful_calls'],
                'success_rate': f"{success_rate:.1f}%",
                'avg_execution_time': f"{perf['avg_execution_time']:.2f}s",
                'avg_confidence': f"{perf['avg_confidence']:.1f}%",
                'enabled': self.models[model_name]['enabled'],
                'weight': self.models[model_name]['weight']
            }

        return performance_summary

    def set_model_enabled(self, model_name: str, enabled: bool):
        """모델 활성화/비활성화"""
        if model_name in self.models:
            self.models[model_name]['enabled'] = enabled
            logger.info(f"Model {model_name} {'enabled' if enabled else 'disabled'}")
        else:
            raise ValueError(f"Model {model_name} not found")

    def update_model_weight(self, model_name: str, weight: float):
        """모델 가중치 업데이트"""
        if model_name in self.models:
            self.models[model_name]['weight'] = weight
            logger.info(f"Model {model_name} weight updated to {weight}")
        else:
            raise ValueError(f"Model {model_name} not found")


_global_orchestrator: Optional[MultiModelOrchestrator] = None


def get_multi_model_orchestrator() -> MultiModelOrchestrator:
    """전역 오케스트레이터 인스턴스 반환"""
    global _global_orchestrator
    if _global_orchestrator is None:
        _global_orchestrator = MultiModelOrchestrator()
    return _global_orchestrator
