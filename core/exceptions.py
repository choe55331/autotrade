core/exceptions.py
커스텀 예외 정의

class KiwoomAPIError(Exception):
    """Kiwoom API 기본 예외"""
    def __init__(self, message: str, error_code: int = -1, details: dict = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        base_msg = super().__str__()
        if self.error_code != -1:
            return f"[Error {self.error_code}] {base_msg}"
        return base_msg


class AuthenticationError(KiwoomAPIError):
    """인증 오류"""
    pass


class TokenExpiredError(AuthenticationError):
    """토큰 만료 오류"""
    pass


class RateLimitError(KiwoomAPIError):
    """API 호출 제한 오류"""
    pass


class NetworkError(KiwoomAPIError):
    """네트워크 오류"""
    pass


class InvalidResponseError(KiwoomAPIError):
    """잘못된 응답 오류"""
    pass


class WebSocketError(KiwoomAPIError):
    """WebSocket 오류"""
    pass


class WebSocketConnectionError(WebSocketError):
    """WebSocket 연결 오류"""
    pass


class WebSocketMessageError(WebSocketError):
    """WebSocket 메시지 오류"""
    pass


class ConfigurationError(Exception):
    """설정 오류"""
    pass


class ValidationError(Exception):
    """데이터 검증 오류"""
    pass


class StrategyError(Exception):
    """전략 실행 오류"""
    pass


class OrderError(Exception):
    """주문 오류"""
    def __init__(self, message: str, order_id: str = None, stock_code: str = None):
        super().__init__(message)
        self.order_id = order_id
        self.stock_code = stock_code


__all__ = [
    'KiwoomAPIError',
    'AuthenticationError',
    'TokenExpiredError',
    'RateLimitError',
    'NetworkError',
    'InvalidResponseError',
    'WebSocketError',
    'WebSocketConnectionError',
    'WebSocketMessageError',
    'ConfigurationError',
    'ValidationError',
    'StrategyError',
    'OrderError',
]