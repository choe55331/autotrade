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

        - institutional_net_buy (일별, ka10008): 40점
        - foreign_net_buy (일별, ka10008): 10점
        - institutional_trend (5일 추이, ka10045): 10점 ⭐ NEW

        Args:
            stock_data: 종목 데이터

        Returns:
            점수 (0~60)
        """
        config = self.criteria_config.get('institutional_buying', {})
        max_score = config.get('weight', 60)

        institutional_net_buy = stock_data.get('institutional_net_buy', 0)
        foreign_net_buy = stock_data.get('foreign_net_buy', 0)
        institutional_trend = stock_data.get('institutional_trend', None)  # ⭐ ka10045 데이터

        min_net_buy = config.get('min_net_buy', 10_000_000)

        score = 0.0

        # 1) 기관 순매수 - 일별 (40점)
        if institutional_net_buy >= min_net_buy * 5:
            score += 40.0  # max_score * 0.67
        elif institutional_net_buy >= min_net_buy * 3:
            score += 30.0  # max_score * 0.5
        elif institutional_net_buy >= min_net_buy:
            score += 20.0  # max_score * 0.33

        # 2) 외국인 순매수 - 일별 (10점)
        if foreign_net_buy >= min_net_buy:
            score += 10.0  # max_score * 0.33 (20점) → 10점으로 조정
        elif foreign_net_buy >= min_net_buy * 0.5:
            score += 5.0   # max_score * 0.2 (12점) → 5점으로 조정

        # 3) 기관/외국인 매매 추이 - 5일 (10점) ⭐ NEW
        if institutional_trend:
            trend_score = 0.0
            try:
                # institutional_trend는 dict 형태: {'stk_orgn_for_trde_trnd': [...], ...}
                for key, values in institutional_trend.items():
                    if isinstance(values, list) and len(values) > 0:
                        recent = values[0]  # 최근 데이터

                        # 기관 순매수량이 양수면 +5점
                        orgn_net = recent.get('orgn_netslmt', '0')
                        if orgn_net and not str(orgn_net).startswith('-'):
                            trend_score += 5.0

                        # 외국인 순매수량이 양수면 +5점
                        for_net = recent.get('for_netslmt', '0')
                        if for_net and not str(for_net).startswith('-'):
                            trend_score += 5.0

                        break  # 첫 번째 키만 사용

                score += trend_score
            except Exception as e:
                logger.debug(f"institutional_trend 파싱 실패: {e}")

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
        min_ratio = 0.8  # 강제 하드코딩: config 무시

        if bid_ask_ratio >= min_ratio * 1.875:  # 1.5
            return max_score
        elif bid_ask_ratio >= min_ratio * 1.5:  # 1.2
            return max_score * 0.75
        elif bid_ask_ratio >= min_ratio:  # 0.8
            return max_score * 0.5
        elif bid_ask_ratio >= min_ratio * 0.625:  # 0.5
            return max_score * 0.25
        else:
            return 0.0

    def _score_execution_intensity(self, stock_data: Dict[str, Any]) -> float:
        """
        5. 체결 강도 점수 (40점)

        ka10047 API로 수집한 실제 체결강도 값 사용

        Args:
            stock_data: 종목 데이터

        Returns:
            점수 (0~40)
        """
        config = self.criteria_config.get('execution_intensity', {})
        max_score = config.get('weight', 40)

        execution_intensity = stock_data.get('execution_intensity')

        # 디버그: 체결강도 값 확인
        stock_code = stock_data.get('stock_code', 'Unknown')
        print(f"[DEBUG 체결강도] {stock_code}: execution_intensity={execution_intensity} (type={type(execution_intensity)})")

        # execution_intensity 데이터가 없으면 0점
        if execution_intensity is None or execution_intensity == 0:
            print(f"[DEBUG 체결강도] {stock_code}: 데이터 없음 또는 0 → 0점")
            return 0.0

        # 체결강도 기준 점수 계산
        min_value = 50  # 강제 하드코딩: config 무시
        print(f"[DEBUG 체결강도] {stock_code}: min_value={min_value} (하드코딩)")

        if execution_intensity >= min_value * 3.0:  # 150 이상
            score = max_score
        elif execution_intensity >= min_value * 2.0:  # 100 이상
            score = max_score * 0.75
        elif execution_intensity >= min_value * 1.4:  # 70 이상
            score = max_score * 0.5
        elif execution_intensity >= min_value:  # 50 이상
            score = max_score * 0.25
        else:
            score = 0.0

        print(f"[DEBUG 체결강도] {stock_code}: {execution_intensity} → {score}점")
        return score

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

        if broker_buy_count >= top_brokers:  # 5개
            return max_score
        elif broker_buy_count >= top_brokers * 0.6:  # 3개
            return max_score * 0.67
        elif broker_buy_count >= top_brokers * 0.4:  # 2개
            return max_score * 0.33
        elif broker_buy_count >= 1:  # 1개라도 있으면
            return max_score * 0.17
        else:
            return 0.0

    def _score_program_trading(self, stock_data: Dict[str, Any]) -> float:
        """
        7. 프로그램 매매 점수 (40점)

        ka90013 API로 수집한 실제 프로그램순매수금액 사용

        Args:
            stock_data: 종목 데이터

        Returns:
            점수 (0~40)
        """
        config = self.criteria_config.get('program_trading', {})
        max_score = config.get('weight', 40)

        program_net_buy = stock_data.get('program_net_buy')

        # 디버그: 프로그램매매 값 확인
        stock_code = stock_data.get('stock_code', 'Unknown')
        print(f"[DEBUG 프로그램] {stock_code}: program_net_buy={program_net_buy} (type={type(program_net_buy)})")

        # 데이터가 없으면 0점
        if program_net_buy is None:
            print(f"[DEBUG 프로그램] {stock_code}: 데이터 없음 → 0점")
            return 0.0

        min_net_buy = 1_000  # 강제 하드코딩: config 무시 (1천원 기준)
        print(f"[DEBUG 프로그램] {stock_code}: min_net_buy={min_net_buy} (하드코딩)")

        # 양수(순매수)만 점수, 음수(순매도)는 0점
        if program_net_buy <= 0:
            print(f"[DEBUG 프로그램] {stock_code}: 음수 또는 0 → 0점")
            return 0.0

        if program_net_buy >= min_net_buy * 5000:  # 500만원 이상
            score = max_score
        elif program_net_buy >= min_net_buy * 3000:  # 300만원 이상
            score = max_score * 0.75
        elif program_net_buy >= min_net_buy * 1000:  # 100만원 이상
            score = max_score * 0.5
        elif program_net_buy >= min_net_buy:  # 1천원 이상
            score = max_score * 0.25
        else:
            score = 0.0

        print(f"[DEBUG 프로그램] {stock_code}: {program_net_buy:,}원 → {score}점")
        return score

    def _score_technical_indicators(self, stock_data: Dict[str, Any]) -> float:
        """
        8. 기술적 지표 점수 (40점)
        RSI, MACD, BB, MA 등 기술지표 반영

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
            if 30 <= rsi <= 70:  # 과매도/과매수 아님
                score += max_score * 0.375
        else:
            # RSI 없으면 상승률로 추정 (강화)
            change_rate = stock_data.get('change_rate', 0)
            if 0.5 <= change_rate <= 20.0:  # 상승 중이면서 과열 아님
                # 상승률에 비례한 점수 (3% = 최고점)
                score_ratio = min(change_rate / 10.0, 1.0)
                score += max_score * 0.375 * score_ratio
            elif change_rate > 0:
                score += max_score * 0.25  # 최소 점수

        # MACD (15점)
        macd_bullish = stock_data.get('macd_bullish_crossover', False)
        macd = stock_data.get('macd', None)
        if macd_bullish or (macd is not None and macd > 0):
            score += max_score * 0.375
        else:
            # MACD 없으면 거래량+상승률로 추정 (강화)
            change_rate = stock_data.get('change_rate', 0)
            volume = stock_data.get('volume', 0)
            if change_rate > 0 and volume > 500_000:  # 거래량 동반 상승
                score += max_score * 0.3
            elif change_rate > 0:
                score += max_score * 0.2

        # 볼린저밴드 (BB) (5점)
        bb_position = stock_data.get('bb_position', None)
        if bb_position is not None and 0.2 <= bb_position <= 0.8:  # 중간 위치
            score += max_score * 0.125
        else:
            # BB 없으면 변동성 기준
            change_rate = stock_data.get('change_rate', 0)
            if abs(change_rate) < 15:  # 과도한 변동 아님
                score += max_score * 0.1

        # 이동평균 (MA) (5점)
        ma5 = stock_data.get('ma5', None)
        ma20 = stock_data.get('ma20', None)
        current_price = stock_data.get('current_price', 0)

        if ma5 and ma20 and ma5 > ma20:
            score += max_score * 0.125
        elif current_price > 0:
            # MA 없으면 가격 건전성으로 추정
            if current_price >= 1000:  # 최소 가격 기준
                score += max_score * 0.1

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

        # 테마 소속 (20점) - 실제로는 "시장 모멘텀" 추정
        is_trending_theme = stock_data.get('is_trending_theme', False)
        if is_trending_theme:
            score += max_score * 0.5
        else:
            # 거래량+상승률 기반 시장 모멘텀 추정
            volume = stock_data.get('volume', 0)
            avg_volume = stock_data.get('avg_volume')
            change_rate = stock_data.get('change_rate', 0)

            # avg_volume이 있고 0보다 큰 경우에만 비율 계산
            if avg_volume and avg_volume > 0:
                volume_ratio = volume / avg_volume

                # 거래량 2배 이상 + 상승률 3% 이상 = 강한 모멘텀
                if volume_ratio >= 2.0 and change_rate >= 3.0:
                    score += max_score * 0.4  # 16점
                elif volume_ratio >= 1.5 and change_rate >= 1.5:
                    score += max_score * 0.25  # 10점
                elif volume_ratio >= 1.2 or change_rate >= 0.5:
                    score += max_score * 0.125  # 5점

        # 긍정 뉴스 (20점) - 실제로는 "가격 강도" 추정
        has_positive_news = stock_data.get('has_positive_news', False)
        if has_positive_news:
            score += max_score * 0.5
        else:
            # 가격 모멘텀+기관 매수 기반 가격 강도 추정
            change_rate = stock_data.get('change_rate', 0)
            institutional_net = stock_data.get('institutional_net_buy')

            # None 체크
            if institutional_net is None:
                institutional_net = 0

            # 상승률 5% 이상 + 기관 순매수 100만원 이상 = 강한 가격 강도
            if change_rate >= 5.0 and institutional_net >= 1_000_000:
                score += max_score * 0.4  # 16점
            elif change_rate >= 2.0 and institutional_net >= 500_000:
                score += max_score * 0.25  # 10점
            elif change_rate >= 0.5 or institutional_net >= 100_000:
                score += max_score * 0.125  # 5점

        return score

    def _score_volatility_pattern(self, stock_data: Dict[str, Any]) -> float:
        """
        10. 변동성 패턴 점수 (20점)

        실제 volatility 데이터만 사용 (일봉 20일 표준편차)

        Args:
            stock_data: 종목 데이터

        Returns:
            점수 (0~20)
        """
        config = self.criteria_config.get('volatility_pattern', {})
        max_score = config.get('weight', 20)

        volatility = stock_data.get('volatility')
        min_volatility = config.get('min_volatility', 0.02)
        max_volatility = config.get('max_volatility', 0.15)

        # volatility 데이터가 없으면 0점
        if volatility is None:
            return 0.0

        # volatility가 있으면 적정 변동성 범위 체크
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
