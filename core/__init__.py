core 패키지
핵심 API 클라이언트 + 표준 타입 시스템

v4.2 CRITICAL
- Position 클래스 통합 (4 → 1)
- Trade, MarketSnapshot 표준화
from .rest_client import KiwoomRESTClient
from .exceptions import (
    KiwoomAPIError,
    AuthenticationError,
    TokenExpiredError,
    RateLimitError,
    NetworkError,
    InvalidResponseError,
    WebSocketError,
    WebSocketConnectionError,
    WebSocketMessageError,
    ConfigurationError,
    ValidationError,
    StrategyError,
    OrderError,
)

from .trading_types import (
    OrderAction,
    OrderType,
    PositionStatus,
    Position,
    Trade,
    MarketSnapshot,
)

__all__ = [
    'KiwoomRESTClient',

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

    'OrderAction',
    'OrderType',
    'PositionStatus',
    'Position',
    'Trade',
    'MarketSnapshot',
]