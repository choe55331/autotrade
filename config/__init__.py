"""
config 패키지 - 설정 관리 모듈

v4.2 Changes:
- New unified config system with Pydantic (schemas.py + manager.py)
- Backward compatible with all existing config systems
"""
from .settings import (
    LOG_CONFIG,
    FILE_PATHS,
    API_RATE_LIMIT,
    MAIN_CYCLE_CONFIG,
    get_default_control_state,
    validate_environment,
)
from .credentials import (
    Credentials,
    get_credentials,
    credentials,
    ACCOUNT_NUMBER,
    KIWOOM_REST_BASE_URL,
    KIWOOM_REST_APPKEY,
    KIWOOM_REST_SECRETKEY,
    GEMINI_API_KEY,
)
from .trading_params import (
    POSITION_CONFIG,
    PROFIT_LOSS_CONFIG,
    FILTER_CONFIG,
    AI_CONFIG,
    validate_trading_params,
    get_trading_params_summary,
)

__all__ = [
    'LOG_CONFIG',
    'FILE_PATHS',
    'API_RATE_LIMIT',
    'MAIN_CYCLE_CONFIG',
    'get_default_control_state',
    'validate_environment',
    'Credentials',
    'get_credentials',
    'credentials',
    'ACCOUNT_NUMBER',
    'KIWOOM_REST_BASE_URL',
    'KIWOOM_REST_APPKEY',
    'KIWOOM_REST_SECRETKEY',
    'GEMINI_API_KEY',
    'POSITION_CONFIG',
    'PROFIT_LOSS_CONFIG',
    'FILTER_CONFIG',
    'AI_CONFIG',
    'validate_trading_params',
    'get_trading_params_summary',
]
