"""
AutoTrade Pro - 표준화된 예외 클래스
일관된 에러 핸들링을 위한 커스텀 예외
"""
from typing import Optional, Dict, Any


class AutoTradeException(Exception):
    """AutoTrade 기본 예외 클래스"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """예외 정보를 딕셔너리로 변환"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'details': self.details
        }



class TradingException(AutoTradeException):
    """거래 관련 기본 예외"""
    pass


class InsufficientFundsException(TradingException):
    """자금 부족 예외"""

    def __init__(self, required: float, available: float, **kwargs):
        super().__init__(
            message=f"자금 부족: 필요 {required:,}원, 가용 {available:,}원",
            error_code="ERR_INSUFFICIENT_FUNDS",
            details={'required': required, 'available': available, **kwargs}
        )


class PositionLimitException(TradingException):
    """포지션 한도 초과 예외"""

    def __init__(self, current: int, limit: int, **kwargs):
        super().__init__(
            message=f"포지션 한도 초과: 현재 {current}개, 한도 {limit}개",
            error_code="ERR_POSITION_LIMIT",
            details={'current': current, 'limit': limit, **kwargs}
        )


class OrderRejectedException(TradingException):
    """주문 거부 예외"""

    def __init__(self, reason: str, **kwargs):
        super().__init__(
            message=f"주문 거부: {reason}",
            error_code="ERR_ORDER_REJECTED",
            details={'reason': reason, **kwargs}
        )


class PositionNotFoundException(TradingException):
    """포지션 미발견 예외"""

    def __init__(self, stock_code: str, **kwargs):
        super().__init__(
            message=f"포지션을 찾을 수 없음: {stock_code}",
            error_code="ERR_POSITION_NOT_FOUND",
            details={'stock_code': stock_code, **kwargs}
        )



class RiskException(AutoTradeException):
    """리스크 관련 기본 예외"""
    pass


class RiskLimitException(RiskException):
    """리스크 한도 초과 예외"""

    def __init__(self, risk_type: str, current: float, limit: float, **kwargs):
        super().__init__(
            message=f"리스크 한도 초과 ({risk_type}): 현재 {current:.2%}, 한도 {limit:.2%}",
            error_code="ERR_RISK_LIMIT",
            details={'risk_type': risk_type, 'current': current, 'limit': limit, **kwargs}
        )


class StopLossTriggered(RiskException):
    """손절 발동 예외"""

    def __init__(self, stock_code: str, current_price: float, stop_loss_price: float, **kwargs):
        super().__init__(
            message=f"손절 발동 [{stock_code}]: 현재가 {current_price:,}원 <= 손절가 {stop_loss_price:,}원",
            error_code="ERR_STOP_LOSS_TRIGGERED",
            details={
                'stock_code': stock_code,
                'current_price': current_price,
                'stop_loss_price': stop_loss_price,
                **kwargs
            }
        )



class DataException(AutoTradeException):
    """데이터 관련 기본 예외"""
    pass


class DataNotAvailableException(DataException):
    """데이터 미제공 예외"""

    def __init__(self, data_type: str, stock_code: Optional[str] = None, **kwargs):
        message = f"데이터 없음: {data_type}"
        if stock_code:
            message += f" ({stock_code})"

        super().__init__(
            message=message,
            error_code="ERR_DATA_NOT_AVAILABLE",
            details={'data_type': data_type, 'stock_code': stock_code, **kwargs}
        )


class InvalidDataException(DataException):
    """잘못된 데이터 예외"""

    def __init__(self, data_type: str, reason: str, **kwargs):
        super().__init__(
            message=f"잘못된 데이터 ({data_type}): {reason}",
            error_code="ERR_INVALID_DATA",
            details={'data_type': data_type, 'reason': reason, **kwargs}
        )



class APIException(AutoTradeException):
    """API 관련 기본 예외"""
    pass


class APIConnectionException(APIException):
    """API 연결 실패 예외"""

    def __init__(self, api_name: str, reason: Optional[str] = None, **kwargs):
        message = f"API 연결 실패: {api_name}"
        if reason:
            message += f" - {reason}"

        super().__init__(
            message=message,
            error_code="ERR_API_CONNECTION",
            details={'api_name': api_name, 'reason': reason, **kwargs}
        )


class APIRateLimitException(APIException):
    """API Rate Limit 초과 예외"""

    def __init__(self, api_name: str, retry_after: Optional[int] = None, **kwargs):
        message = f"API Rate Limit 초과: {api_name}"
        if retry_after:
            message += f" (재시도까지 {retry_after}초)"

        super().__init__(
            message=message,
            error_code="ERR_API_RATE_LIMIT",
            details={'api_name': api_name, 'retry_after': retry_after, **kwargs}
        )


class APIResponseException(APIException):
    """API 응답 에러 예외"""

    def __init__(self, api_name: str, status_code: int, response_text: str, **kwargs):
        super().__init__(
            message=f"API 응답 에러 ({api_name}): {status_code} - {response_text}",
            error_code="ERR_API_RESPONSE",
            details={
                'api_name': api_name,
                'status_code': status_code,
                'response_text': response_text,
                **kwargs
            }
        )



class ConfigurationException(AutoTradeException):
    """설정 관련 기본 예외"""
    pass


class InvalidParameterException(ConfigurationException):
    """잘못된 파라미터 예외"""

    def __init__(self, param_name: str, value: Any, reason: str, **kwargs):
        super().__init__(
            message=f"잘못된 파라미터 ({param_name}={value}): {reason}",
            error_code="ERR_INVALID_PARAMETER",
            details={'param_name': param_name, 'value': value, 'reason': reason, **kwargs}
        )


class MissingConfigException(ConfigurationException):
    """필수 설정 누락 예외"""

    def __init__(self, config_key: str, **kwargs):
        super().__init__(
            message=f"필수 설정 누락: {config_key}",
            error_code="ERR_MISSING_CONFIG",
            details={'config_key': config_key, **kwargs}
        )



class StrategyException(AutoTradeException):
    """전략 관련 기본 예외"""
    pass


class SignalNotFoundException(StrategyException):
    """신호 미발견 예외"""

    def __init__(self, stock_code: str, signal_type: str, **kwargs):
        super().__init__(
            message=f"신호 없음 [{stock_code}]: {signal_type}",
            error_code="ERR_SIGNAL_NOT_FOUND",
            details={'stock_code': stock_code, 'signal_type': signal_type, **kwargs}
        )


class BacktestException(StrategyException):
    """백테스팅 관련 예외"""

    def __init__(self, reason: str, **kwargs):
        super().__init__(
            message=f"백테스팅 실패: {reason}",
            error_code="ERR_BACKTEST_FAILED",
            details={'reason': reason, **kwargs}
        )



def handle_exception(e: Exception, logger, context: Optional[str] = None) -> Dict[str, Any]:
    """
    예외 핸들링 헬퍼 함수

    Args:
        e: 예외 객체
        logger: 로거
        context: 컨텍스트 정보 (선택)

    Returns:
        에러 정보 딕셔너리
    """
    if isinstance(e, AutoTradeException):
        error_info = e.to_dict()
        if context:
            error_info['context'] = context

        logger.error(f"[{e.error_code}] {e.message}", extra=error_info)
        return error_info
    else:
        error_info = {
            'error_type': type(e).__name__,
            'message': str(e),
            'error_code': 'ERR_UNKNOWN',
            'context': context
        }
        logger.exception(f"예상치 못한 예외: {e}")
        return error_info


def retry_on_exception(
    exceptions: tuple = (Exception,),
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    logger=None
):
    예외 발생 시 재시도 데코레이터

    Args:
        exceptions: 재시도할 예외 타입 튜플
        max_retries: 최대 재시도 횟수
        delay: 초기 대기 시간 (초)
        backoff: 대기 시간 증가 배수
        logger: 로거 (선택)

    Usage:
        @retry_on_exception(exceptions=(APIConnectionException,), max_retries=3)
        def call_api():
            ...
    import time
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        if logger:
                            logger.error(f"{func.__name__} 최대 재시도 횟수 초과: {e}")
                        raise

                    if logger:
                        logger.warning(
                            f"{func.__name__} 재시도 {attempt + 1}/{max_retries}: {e} "
                            f"({current_delay}초 후 재시도)"
                        )

                    time.sleep(current_delay)
                    current_delay *= backoff

        return wrapper
    return decorator
