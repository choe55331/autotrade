"""
AutoTrade Pro - 통합 신호 체크 유틸리티
모든 전략에서 공통으로 사용하는 신호 체크 로직
"""
from enum import Enum
from typing import Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SignalType(Enum):
    """신호 타입"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"
    TRAILING_STOP = "TRAILING_STOP"


class SignalChecker:
    """통합 신호 체커"""

    @staticmethod
    def check_stop_loss(
        current_price: float,
        stop_loss_price: float,
        stock_code: str = "",
        log_level: str = "warning"
    ) -> Tuple[bool, str]:
        손절 신호 체크

        Args:
            current_price: 현재가
            stop_loss_price: 손절가
            stock_code: 종목코드 (로깅용)
            log_level: 로그 레벨

        Returns:
            (신호 발생 여부, 사유)
        if current_price <= stop_loss_price:
            message = f"[{stock_code}] 손절 신호: {current_price:,} <= {stop_loss_price:,}"

            if log_level == "warning":
                logger.warning(message)
            elif log_level == "info":
                logger.info(message)

            return True, "STOP_LOSS"

        return False, ""

    @staticmethod
    def check_take_profit(
        current_price: float,
        take_profit_price: float,
        stock_code: str = "",
        log_level: str = "info"
    ) -> Tuple[bool, str]:
        익절 신호 체크

        Args:
            current_price: 현재가
            take_profit_price: 익절가
            stock_code: 종목코드
            log_level: 로그 레벨

        Returns:
            (신호 발생 여부, 사유)
        if current_price >= take_profit_price:
            message = f"[{stock_code}] 익절 신호: {current_price:,} >= {take_profit_price:,}"

            if log_level == "info":
                logger.info(message)
            elif log_level == "warning":
                logger.warning(message)

            return True, "TAKE_PROFIT"

        return False, ""

    @staticmethod
    def check_stop_loss_by_rate(
        purchase_price: float,
        current_price: float,
        stop_loss_rate: float,
        stock_code: str = ""
    ) -> Tuple[bool, str]:
        손실률 기반 손절 신호 체크

        Args:
            purchase_price: 매수가
            current_price: 현재가
            stop_loss_rate: 손절 비율 (예: 0.05 = -5%)
            stock_code: 종목코드

        Returns:
            (신호 발생 여부, 사유)
        if purchase_price <= 0:
            return False, ""

        loss_rate = (current_price - purchase_price) / purchase_price

        if loss_rate <= -abs(stop_loss_rate):
            message = f"[{stock_code}] 손절 신호 (비율): {loss_rate:.2%} <= -{stop_loss_rate:.2%}"
            logger.warning(message)
            return True, "STOP_LOSS_RATE"

        return False, ""

    @staticmethod
    def check_take_profit_by_rate(
        purchase_price: float,
        current_price: float,
        take_profit_rate: float,
        stock_code: str = ""
    ) -> Tuple[bool, str]:
        수익률 기반 익절 신호 체크

        Args:
            purchase_price: 매수가
            current_price: 현재가
            take_profit_rate: 익절 비율 (예: 0.10 = +10%)
            stock_code: 종목코드

        Returns:
            (신호 발생 여부, 사유)
        if purchase_price <= 0:
            return False, ""

        profit_rate = (current_price - purchase_price) / purchase_price

        if profit_rate >= take_profit_rate:
            message = f"[{stock_code}] 익절 신호 (비율): {profit_rate:.2%} >= {take_profit_rate:.2%}"
            logger.info(message)
            return True, "TAKE_PROFIT_RATE"

        return False, ""

    @staticmethod
    def check_price_threshold(
        current_price: float,
        threshold_price: float,
        direction: str = "above",
        stock_code: str = ""
    ) -> Tuple[bool, str]:
        가격 임계값 체크

        Args:
            current_price: 현재가
            threshold_price: 임계가
            direction: 방향 ("above" or "below")
            stock_code: 종목코드

        Returns:
            (신호 발생 여부, 사유)
        if direction == "above":
            if current_price >= threshold_price:
                logger.info(f"[{stock_code}] 가격 상향 돌파: {current_price:,} >= {threshold_price:,}")
                return True, "PRICE_ABOVE_THRESHOLD"
        elif direction == "below":
            if current_price <= threshold_price:
                logger.info(f"[{stock_code}] 가격 하향 돌파: {current_price:,} <= {threshold_price:,}")
                return True, "PRICE_BELOW_THRESHOLD"

        return False, ""

    @staticmethod
    def check_volume_condition(
        current_volume: int,
        avg_volume: int,
        multiplier: float = 1.5,
        stock_code: str = ""
    ) -> Tuple[bool, str]:
        거래량 조건 체크

        Args:
            current_volume: 현재 거래량
            avg_volume: 평균 거래량
            multiplier: 배수 (예: 1.5 = 평균의 1.5배)
            stock_code: 종목코드

        Returns:
            (조건 만족 여부, 사유)
        threshold_volume = avg_volume * multiplier

        if current_volume >= threshold_volume:
            logger.info(f"[{stock_code}] 거래량 급증: {current_volume:,} >= {threshold_volume:,} (평균 {multiplier}배)")
            return True, "VOLUME_SPIKE"

        return False, ""

    @staticmethod
    def check_trailing_stop(
        current_price: float,
        highest_price: float,
        trailing_distance: float,
        stock_code: str = ""
    ) -> Tuple[bool, float]:
        트레일링 스톱 체크

        Args:
            current_price: 현재가
            highest_price: 최고가
            trailing_distance: 트레일링 거리
            stock_code: 종목코드

        Returns:
            (손절 신호 여부, 새로운 손절가)
        trailing_stop_price = highest_price - trailing_distance

        if current_price <= trailing_stop_price:
            logger.warning(f"[{stock_code}] 트레일링 스톱: {current_price:,} <= {trailing_stop_price:,}")
            return True, trailing_stop_price

        return False, trailing_stop_price

    @staticmethod
    def check_multiple_conditions(
        conditions: list[Tuple[bool, str]],
        logic: str = "AND",
        stock_code: str = ""
    ) -> Tuple[bool, str]:
        복수 조건 체크

        Args:
            conditions: 조건 리스트 [(만족여부, 사유), ...]
            logic: 논리 연산 ("AND" or "OR")
            stock_code: 종목코드

        Returns:
            (전체 조건 만족 여부, 종합 사유)
        if not conditions:
            return False, "NO_CONDITIONS"

        results = [cond[0] for cond in conditions]
        reasons = [cond[1] for cond in conditions if cond[1]]

        if logic == "AND":
            result = all(results)
        elif logic == "OR":
            result = any(results)
        else:
            logger.error(f"잘못된 로직: {logic}")
            return False, "INVALID_LOGIC"

        combined_reason = " & ".join(reasons) if logic == "AND" else " | ".join(reasons)

        if result:
            logger.info(f"[{stock_code}] 조건 만족 ({logic}): {combined_reason}")

        return result, combined_reason

    @staticmethod
    def generate_signal(
        signal_type: SignalType,
        stock_code: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        신호 객체 생성

        Args:
            signal_type: 신호 타입
            stock_code: 종목코드
            reason: 사유
            metadata: 추가 메타데이터

        Returns:
            신호 딕셔너리
        from datetime import datetime

        signal = {
            'signal_type': signal_type.value,
            'stock_code': stock_code,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        logger.info(f"[{stock_code}] 신호 생성: {signal_type.value} - {reason}")

        return signal


class TradingSignalValidator:
    """매매 신호 검증기"""

    @staticmethod
    def validate_buy_signal(
        stock_code: str,
        current_price: float,
        available_cash: float,
        position_limit: int,
        current_positions: int,
        min_price: float = 1000,
        max_price: float = 1000000
    ) -> Tuple[bool, str]:
        매수 신호 검증

        Args:
            stock_code: 종목코드
            current_price: 현재가
            available_cash: 가용 현금
            position_limit: 최대 포지션 수
            current_positions: 현재 포지션 수
            min_price: 최소 매수 가격
            max_price: 최대 매수 가격

        Returns:
            (검증 통과 여부, 사유)
        if current_price < min_price:
            return False, f"가격이 너무 낮음: {current_price:,} < {min_price:,}"

        if current_price > max_price:
            return False, f"가격이 너무 높음: {current_price:,} > {max_price:,}"

        if current_positions >= position_limit:
            return False, f"포지션 한도 초과: {current_positions} >= {position_limit}"

        if available_cash < current_price:
            return False, f"현금 부족: {available_cash:,} < {current_price:,}"

        return True, "VALID"

    @staticmethod
    def validate_sell_signal(
        stock_code: str,
        has_position: bool,
        quantity: int = 0
    ) -> Tuple[bool, str]:
        매도 신호 검증

        Args:
            stock_code: 종목코드
            has_position: 포지션 보유 여부
            quantity: 보유 수량

        Returns:
            (검증 통과 여부, 사유)
        if not has_position:
            return False, "보유 포지션 없음"

        if quantity <= 0:
            return False, f"잘못된 수량: {quantity}"

        return True, "VALID"
