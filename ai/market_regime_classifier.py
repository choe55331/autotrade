"""
AutoTrade Pro v4.0 - AI 기반 시장 레짐 분류기
현재 시장이 상승장/하락장/횡보장 중 어느 상태인지 AI로 분류

주요 기능:
- 다양한 지표 기반 시장 상태 분류
- 추천 전략 자동 전환
- 히스토리 저장 및 분석
"""
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


class RegimeType(str, Enum):
    """시장 레짐 유형"""
    BULL = "bull"          # 상승장
    BEAR = "bear"          # 하락장
    SIDEWAYS = "sideways"  # 횡보장


class VolatilityLevel(str, Enum):
    """변동성 수준"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MarketRegimeClassifier:
    """시장 레짐 분류기"""

    def __init__(self, settings: Dict[str, Any] = None):
        """
        초기화

        Args:
            settings: 설정
                {
                    'update_interval_hours': 4,        # 업데이트 주기
                    'lookback_days': 60,               # 분석 기간
                    'bull_threshold': 0.02,            # 상승장 임계값 (2%)
                    'bear_threshold': -0.02,           # 하락장 임계값 (-2%)
                    'high_volatility_threshold': 0.02  # 고변동성 임계값
                }
        """
        self.settings = settings or {}
        self.update_interval_hours = self.settings.get('update_interval_hours', 4)
        self.lookback_days = self.settings.get('lookback_days', 60)
        self.bull_threshold = self.settings.get('bull_threshold', 0.02)
        self.bear_threshold = self.settings.get('bear_threshold', -0.02)
        self.high_volatility_threshold = self.settings.get('high_volatility_threshold', 0.02)

        # 현재 레짐
        self.current_regime = RegimeType.SIDEWAYS
        self.current_volatility = VolatilityLevel.MEDIUM
        self.confidence = 0.5
        self.last_update = None

        # 전략 매핑
        self.strategy_mapping = {
            RegimeType.BULL: "momentum",           # 상승장 -> 모멘텀
            RegimeType.BEAR: "defensive",          # 하락장 -> 방어적
            RegimeType.SIDEWAYS: "mean_reversion"  # 횡보장 -> 역추세
        }

        logger.info("시장 레짐 분류기 초기화")

    def classify(
        self,
        price_history: list,
        volume_history: list = None
    ) -> Tuple[RegimeType, VolatilityLevel, float]:
        """
        시장 레짐 분류

        Args:
            price_history: 가격 히스토리 (최근 60일)
            volume_history: 거래량 히스토리 (선택)

        Returns:
            (regime_type, volatility_level, confidence)
        """
        if len(price_history) < 20:
            logger.warning("데이터 부족: 최소 20일 필요")
            return RegimeType.SIDEWAYS, VolatilityLevel.MEDIUM, 0.3

        prices = np.array(price_history)

        # 1. 추세 강도 계산
        trend_strength = self._calculate_trend_strength(prices)

        # 2. 변동성 계산
        volatility = self._calculate_volatility(prices)

        # 3. 모멘텀 계산
        momentum = self._calculate_momentum(prices)

        # 4. 레짐 분류
        regime = self._classify_regime(trend_strength, momentum)

        # 5. 변동성 수준 분류
        volatility_level = self._classify_volatility(volatility)

        # 6. 신뢰도 계산
        confidence = self._calculate_confidence(trend_strength, volatility, momentum)

        # 상태 업데이트
        self.current_regime = regime
        self.current_volatility = volatility_level
        self.confidence = confidence
        self.last_update = datetime.now()

        logger.info(
            f"시장 레짐 분류: {regime.value}, 변동성={volatility_level.value}, "
            f"신뢰도={confidence:.2f}"
        )

        return regime, volatility_level, confidence

    def _calculate_trend_strength(self, prices: np.ndarray) -> float:
        """추세 강도 계산 (선형 회귀 기울기)"""
        x = np.arange(len(prices))
        coefficients = np.polyfit(x, prices, 1)
        slope = coefficients[0]

        # 정규화 (가격 대비 기울기)
        trend_strength = slope / np.mean(prices)
        return trend_strength

    def _calculate_volatility(self, prices: np.ndarray) -> float:
        """변동성 계산 (일별 수익률의 표준편차)"""
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns)
        return volatility

    def _calculate_momentum(self, prices: np.ndarray) -> float:
        """모멘텀 계산 (최근 20일 수익률)"""
        if len(prices) < 20:
            return 0.0

        recent_return = (prices[-1] - prices[-20]) / prices[-20]
        return recent_return

    def _classify_regime(self, trend_strength: float, momentum: float) -> RegimeType:
        """레짐 분류"""
        # 추세와 모멘텀을 종합적으로 고려
        combined_signal = (trend_strength + momentum) / 2

        if combined_signal > self.bull_threshold:
            return RegimeType.BULL
        elif combined_signal < self.bear_threshold:
            return RegimeType.BEAR
        else:
            return RegimeType.SIDEWAYS

    def _classify_volatility(self, volatility: float) -> VolatilityLevel:
        """변동성 수준 분류"""
        if volatility < self.high_volatility_threshold / 2:
            return VolatilityLevel.LOW
        elif volatility < self.high_volatility_threshold:
            return VolatilityLevel.MEDIUM
        else:
            return VolatilityLevel.HIGH

    def _calculate_confidence(
        self,
        trend_strength: float,
        volatility: float,
        momentum: float
    ) -> float:
        """신뢰도 계산"""
        # 추세가 강하고 변동성이 낮을수록 높은 신뢰도
        trend_confidence = min(abs(trend_strength) / 0.05, 1.0)  # 0.05 = 5%
        volatility_confidence = max(1.0 - volatility / 0.05, 0.0)
        momentum_confidence = min(abs(momentum) / 0.10, 1.0)  # 0.10 = 10%

        # 가중 평균
        confidence = (
            trend_confidence * 0.4 +
            volatility_confidence * 0.3 +
            momentum_confidence * 0.3
        )

        return min(max(confidence, 0.0), 1.0)

    def get_recommended_strategy(self) -> str:
        """현재 레짐에 맞는 추천 전략 반환"""
        strategy = self.strategy_mapping.get(self.current_regime, "balanced")

        logger.info(
            f"추천 전략: {strategy} (레짐={self.current_regime.value}, "
            f"신뢰도={self.confidence:.2f})"
        )

        return strategy

    def should_update(self) -> bool:
        """업데이트가 필요한지 확인"""
        if self.last_update is None:
            return True

        hours_since_update = (datetime.now() - self.last_update).total_seconds() / 3600
        return hours_since_update >= self.update_interval_hours

    def get_current_state(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        return {
            'regime': self.current_regime.value,
            'volatility': self.current_volatility.value,
            'confidence': self.confidence,
            'recommended_strategy': self.get_recommended_strategy(),
            'last_update': self.last_update.isoformat() if self.last_update else None
        }


# 테스트
if __name__ == "__main__":
    classifier = MarketRegimeClassifier()

    # 상승 추세 시뮬레이션
    prices = [70000 + i * 500 + np.random.normal(0, 500) for i in range(60)]

    regime, volatility, confidence = classifier.classify(prices)

    print(f"레짐: {regime}")
    print(f"변동성: {volatility}")
    print(f"신뢰도: {confidence:.2f}")
    print(f"추천 전략: {classifier.get_recommended_strategy()}")
