"""
strategy/scoring_system.py
10가지 기준 스코어링 시스템 (440점 만점)
"""
from typing import Dict, Any, List
from dataclasses import dataclass, field

from utils.logger_new import get_logger

from config.config_manager import get_config


logger = get_logger()


@dataclass
class ScoringResult:
    """스코어링 결과"""

    total_score: float = 0.0
    max_score: float = 440.0
    percentage: float = 0.0

    # 세부 점수
    volume_surge_score: float = 0.0
    price_momentum_score: float = 0.0
    institutional_buying_score: float = 0.0
    bid_strength_score: float = 0.0
    execution_intensity_score: float = 0.0
    broker_activity_score: float = 0.0
    program_trading_score: float = 0.0
    technical_indicators_score: float = 0.0
    theme_news_score: float = 0.0
    volatility_pattern_score: float = 0.0

    # 평가 내역
    details: Dict[str, Any] = field(default_factory=dict)

    def calculate_percentage(self):
        """퍼센티지 계산"""
        self.percentage = (self.total_score / self.max_score) * 100 if self.max_score > 0 else 0

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'total_score': self.total_score,
            'max_score': self.max_score,
            'percentage': self.percentage,
            'breakdown': {
                'volume_surge': self.volume_surge_score,
                'price_momentum': self.price_momentum_score,
                'institutional_buying': self.institutional_buying_score,
                'bid_strength': self.bid_strength_score,
                'execution_intensity': self.execution_intensity_score,
                'broker_activity': self.broker_activity_score,
                'program_trading': self.program_trading_score,
                'technical_indicators': self.technical_indicators_score,
                'theme_news': self.theme_news_score,
                'volatility_pattern': self.volatility_pattern_score,
            },
            'details': self.details,
        }


class ScoringSystem:
    """10가지 기준 스코어링 시스템"""

    def __init__(self, market_api=None):
        """
        초기화

        Args:
            market_api: 시장 데이터 API (선택)
        """
        self.market_api = market_api

        # 설정 로드
        self.config = get_config()
        self.scoring_config = self.config.scoring
        self.criteria_config = self.scoring_config.get('criteria', {})

        logger.info("📊 10가지 기준 스코어링 시스템 초기화 완료")

    def calculate_score(self, stock_data: Dict[str, Any]) -> ScoringResult:
        """
        종목 종합 점수 계산

        Args:
            stock_data: 종목 데이터

        Returns:
            ScoringResult 객체
        """
        result = ScoringResult()

        # 1. 거래량 급증 (60점)
        result.volume_surge_score = self._score_volume_surge(stock_data)

        # 2. 가격 모멘텀 (60점)
        result.price_momentum_score = self._score_price_momentum(stock_data)

        # 3. 기관 매수세 (60점)
        result.institutional_buying_score = self._score_institutional_buying(stock_data)

        # 4. 매수 호가 강도 (40점)
        result.bid_strength_score = self._score_bid_strength(stock_data)

        # 5. 체결 강도 (40점)
        result.execution_intensity_score = self._score_execution_intensity(stock_data)

        # 6. 주요 증권사 활동 (40점)
        result.broker_activity_score = self._score_broker_activity(stock_data)

        # 7. 프로그램 매매 (40점)
        result.program_trading_score = self._score_program_trading(stock_data)

        # 8. 기술적 지표 (40점)
        result.technical_indicators_score = self._score_technical_indicators(stock_data)

        # 9. 테마/뉴스 (40점)
        result.theme_news_score = self._score_theme_news(stock_data)

        # 10. 변동성 패턴 (20점)
        result.volatility_pattern_score = self._score_volatility_pattern(stock_data)

        # 총점 계산
        result.total_score = (
            result.volume_surge_score +
            result.price_momentum_score +
            result.institutional_buying_score +
            result.bid_strength_score +
            result.execution_intensity_score +
            result.broker_activity_score +
            result.program_trading_score +
            result.technical_indicators_score +
            result.theme_news_score +
            result.volatility_pattern_score
        )

        result.calculate_percentage()

        logger.info(
            f"📊 스코어링 완료: {stock_data.get('name', stock_data.get('code', 'Unknown'))} "
            f"총점 {result.total_score:.1f}/{result.max_score} ({result.percentage:.1f}%)"
        )

        return result

    def _score_volume_surge(self, stock_data: Dict[str, Any]) -> float:
        """
        1. 거래량 급증 점수 (60점)

        Args:
            stock_data: 종목 데이터

        Returns:
            점수 (0~60)
        """
        max_score = 60

        volume = stock_data.get('volume', 0)
        avg_volume = stock_data.get('avg_volume', None)

        # avg_volume이 있으면 비율 계산
        if avg_volume and avg_volume > 0:
            volume_ratio = volume / avg_volume
            if volume_ratio >= 5.0:
                return max_score
            elif volume_ratio >= 3.0:
                return max_score * 0.75
            elif volume_ratio >= 2.0:
                return max_score * 0.5
            elif volume_ratio >= 1.0:
                return max_score * 0.25

        # avg_volume이 없으면 절대값 기준 (강화)
        if volume >= 5_000_000:  # 500만주 이상
            return max_score * 0.8
        elif volume >= 2_000_000:  # 200만주
            return max_score * 0.6
        elif volume >= 1_000_000:  # 100만주
            return max_score * 0.4
        elif volume >= 500_000:  # 50만주
            return max_score * 0.2

        return 0.0

    def _score_price_momentum(self, stock_data: Dict[str, Any]) -> float:
        """
        2. 가격 모멘텀 점수 (60점)

        Args:
            stock_data: 종목 데이터

        Returns:
            점수 (0~60)
        """
        max_score = 60

        # change_rate를 % 단위로 받음 (예: 3.5는 3.5%)
        change_rate = stock_data.get('change_rate', stock_data.get('rate', 0.0))

        # 상승률 기준 점수 (강화)
        if change_rate >= 10.0:  # 10% 이상
            return max_score
        elif change_rate >= 7.0:  # 7% 이상
            return max_score * 0.85
        elif change_rate >= 5.0:  # 5% 이상
            return max_score * 0.7
        elif change_rate >= 3.0:  # 3% 이상
            return max_score * 0.55
        elif change_rate >= 2.0:  # 2% 이상
            return max_score * 0.4
        elif change_rate >= 1.0:  # 1% 이상
            return max_score * 0.25
        else:
            return 0.0

    def _score_institutional_buying(self, stock_data: Dict[str, Any]) -> float:
        """
        3. 기관 매수세 점수 (60점)

        Args:
            stock_data: 종목 데이터

        Returns:
            점수 (0~60)
        """
        config = self.criteria_config.get('institutional_buying', {})
        max_score = config.get('weight', 60)

        institutional_net_buy = stock_data.get('institutional_net_buy', 0)
        foreign_net_buy = stock_data.get('foreign_net_buy', 0)

        min_net_buy = config.get('min_net_buy', 10_000_000)

        score = 0.0

        # 기관 순매수 (40점)
        if institutional_net_buy >= min_net_buy * 5:
            score += max_score * 0.67
        elif institutional_net_buy >= min_net_buy * 3:
            score += max_score * 0.5
        elif institutional_net_buy >= min_net_buy:
            score += max_score * 0.33

        # 외국인 순매수 (20점)
        if foreign_net_buy >= min_net_buy:
            score += max_score * 0.33
        elif foreign_net_buy >= min_net_buy * 0.5:
            score += max_score * 0.2

        return min(score, max_score)

    def _score_bid_strength(self, stock_data: Dict[str, Any]) -> float:
        """
        4. 매수 호가 강도 점수 (40점)

        Args:
            stock_data: 종목 데이터

        Returns:
            점수 (0~40)
        """
        config = self.criteria_config.get('bid_strength', {})
        max_score = config.get('weight', 40)

        bid_ask_ratio = stock_data.get('bid_ask_ratio', 0.0)
        min_ratio = config.get('min_ratio', 1.2)

        if bid_ask_ratio >= min_ratio * 1.5:
            return max_score
        elif bid_ask_ratio >= min_ratio * 1.2:
            return max_score * 0.75
        elif bid_ask_ratio >= min_ratio:
            return max_score * 0.5
        else:
            return 0.0

    def _score_execution_intensity(self, stock_data: Dict[str, Any]) -> float:
        """
        5. 체결 강도 점수 (40점)

        Args:
            stock_data: 종목 데이터

        Returns:
            점수 (0~40)
        """
        config = self.criteria_config.get('execution_intensity', {})
        max_score = config.get('weight', 40)

        execution_intensity = stock_data.get('execution_intensity', 100)
        min_value = config.get('min_value', 120)

        if execution_intensity >= min_value * 1.5:
            return max_score
        elif execution_intensity >= min_value * 1.2:
            return max_score * 0.75
        elif execution_intensity >= min_value:
            return max_score * 0.5
        else:
            return 0.0

    def _score_broker_activity(self, stock_data: Dict[str, Any]) -> float:
        """
        6. 주요 증권사 활동 점수 (40점)

        Args:
            stock_data: 종목 데이터

        Returns:
            점수 (0~40)
        """
        config = self.criteria_config.get('broker_activity', {})
        max_score = config.get('weight', 40)

        broker_buy_count = stock_data.get('top_broker_buy_count', 0)
        top_brokers = config.get('top_brokers', 5)

        if broker_buy_count >= top_brokers:
            return max_score
        elif broker_buy_count >= top_brokers * 0.6:
            return max_score * 0.67
        elif broker_buy_count >= top_brokers * 0.4:
            return max_score * 0.33
        else:
            return 0.0

    def _score_program_trading(self, stock_data: Dict[str, Any]) -> float:
        """
        7. 프로그램 매매 점수 (40점)

        Args:
            stock_data: 종목 데이터

        Returns:
            점수 (0~40)
        """
        config = self.criteria_config.get('program_trading', {})
        max_score = config.get('weight', 40)

        program_net_buy = stock_data.get('program_net_buy', 0)
        min_net_buy = config.get('min_net_buy', 5_000_000)

        if program_net_buy >= min_net_buy * 5:
            return max_score
        elif program_net_buy >= min_net_buy * 3:
            return max_score * 0.75
        elif program_net_buy >= min_net_buy:
            return max_score * 0.5
        else:
            return 0.0

    def _score_technical_indicators(self, stock_data: Dict[str, Any]) -> float:
        """
        8. 기술적 지표 점수 (40점)

        Args:
            stock_data: 종목 데이터

        Returns:
            점수 (0~40)
        """
        max_score = 40
        score = 0.0

        # RSI (15점)
        rsi = stock_data.get('rsi', None)
        if rsi is not None:
            if 30 <= rsi <= 70:
                score += max_score * 0.375
        else:
            # RSI 없으면 상승률 기준 (강화)
            change_rate = stock_data.get('change_rate', 0)
            if 1.0 <= change_rate <= 15.0:  # 과열 아닌 적정 상승
                score += max_score * 0.3

        # MACD (15점)
        macd_bullish = stock_data.get('macd_bullish_crossover', False)
        if macd_bullish:
            score += max_score * 0.375
        else:
            # MACD 없으면 상승 지속성 기준
            change_rate = stock_data.get('change_rate', 0)
            if change_rate > 0:  # 상승 중
                score += max_score * 0.2

        # 이동평균 (10점)
        ma5 = stock_data.get('ma5', None)
        ma20 = stock_data.get('ma20', None)

        if ma5 and ma20 and ma5 > ma20:
            score += max_score * 0.25
        else:
            # MA 없으면 가격 위치 기준
            current_price = stock_data.get('current_price', 0)
            if current_price > 1000:  # 최소 기준
                score += max_score * 0.15

        return score

    def _score_theme_news(self, stock_data: Dict[str, Any]) -> float:
        """
        9. 테마/뉴스 점수 (40점)

        Args:
            stock_data: 종목 데이터

        Returns:
            점수 (0~40)
        """
        config = self.criteria_config.get('theme_news', {})
        max_score = config.get('weight', 40)

        score = 0.0

        # 테마 소속 (20점)
        is_trending_theme = stock_data.get('is_trending_theme', False)
        if is_trending_theme:
            score += max_score * 0.5

        # 긍정 뉴스 (20점)
        has_positive_news = stock_data.get('has_positive_news', False)
        if has_positive_news:
            score += max_score * 0.5

        return score

    def _score_volatility_pattern(self, stock_data: Dict[str, Any]) -> float:
        """
        10. 변동성 패턴 점수 (20점)

        Args:
            stock_data: 종목 데이터

        Returns:
            점수 (0~20)
        """
        config = self.criteria_config.get('volatility_pattern', {})
        max_score = config.get('weight', 20)

        volatility = stock_data.get('volatility', 0.0)
        min_volatility = config.get('min_volatility', 0.02)
        max_volatility = config.get('max_volatility', 0.15)

        # 적정 변동성 범위
        if min_volatility <= volatility <= max_volatility:
            # 중간값에 가까울수록 높은 점수
            mid_volatility = (min_volatility + max_volatility) / 2
            distance_from_mid = abs(volatility - mid_volatility)
            max_distance = (max_volatility - min_volatility) / 2

            score_ratio = 1 - (distance_from_mid / max_distance)
            return max_score * score_ratio
        else:
            return 0.0

    def get_grade(self, total_score: float) -> str:
        """
        점수에 따른 등급 반환

        Args:
            total_score: 총점

        Returns:
            등급 (S, A, B, C, D, F)
        """
        percentage = (total_score / 440) * 100

        if percentage >= 90:
            return 'S'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B'
        elif percentage >= 60:
            return 'C'
        elif percentage >= 50:
            return 'D'
        else:
            return 'F'

    def should_buy(self, scoring_result: ScoringResult, threshold: float = 300) -> bool:
        """
        매수 여부 판단

        Args:
            scoring_result: 스코어링 결과
            threshold: 매수 임계값 (기본 300점)

        Returns:
            매수 여부
        """
        return scoring_result.total_score >= threshold


__all__ = ['ScoringSystem', 'ScoringResult']
