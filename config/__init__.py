"""
config 패키지
설정 관리 모듈

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
    KIWOOM_REST_BASE_URL,
    KIWOOM_REST_APPKEY,
    KIWOOM_REST_SECRETKEY,
    ACCOUNT_NUMBER,
    KIWOOM_WEBSOCKET_URL,
    GEMINI_API_KEY,
    GEMINI_MODEL_NAME,
    GEMINI_ENABLE_CROSS_CHECK,
)
from .trading_params import (
    TRADING_PARAMS,
    POSITION_CONFIG,
    PROFIT_LOSS_CONFIG,
    FILTER_CONFIG,
    AI_CONFIG,
    validate_trading_params,
    get_trading_params_summary,
)
from .api_loader import (
    APILoader,
    get_api_loader,
    load_successful_apis,
    get_api_by_id,
    get_api_by_category,
    search_api,
    is_api_tested,
    APICategory,
)
from .unified_settings import UnifiedSettingsManager, get_unified_settings

from .parameter_standards import (
    StandardParameters,
    ParameterConverter,
    migrate_parameters,
    LEGACY_PARAMETER_MAPPING
)

try:
    from .manager import (
        ConfigManager,
        get_config,
        get_setting,
        set_setting,
        save_config,
        reload_config,
        reset_config,
    )
    from .schemas import (
        AutoTradeConfig,
        RiskManagementConfig,
        TradingConfig,
        AIConfig,
        LoggingConfig,
        NotificationConfig,
        MainCycleConfig,
    )
except ImportError:
    ConfigManager = None
    get_config = None
    get_setting = None
    set_setting = None
    save_config = None
    reload_config = None
    reset_config = None
    AutoTradeConfig = None
    RiskManagementConfig = None
    TradingConfig = None
    AIConfig = None
    LoggingConfig = None
    NotificationConfig = None
    MainCycleConfig = None

LOG_FILE_PATH = LOG_CONFIG['LOG_FILE_PATH']
LOG_LEVEL = LOG_CONFIG['LOG_LEVEL']
LOG_FILE_MAX_BYTES = LOG_CONFIG['LOG_FILE_MAX_BYTES']
LOG_FILE_BACKUP_COUNT = LOG_CONFIG['LOG_FILE_BACKUP_COUNT']

CONTROL_FILE_PATH = FILE_PATHS['CONTROL_FILE']
STRATEGY_STATE_FILE = FILE_PATHS['STRATEGY_STATE_FILE']
WEBSOCKET_STATUS_FILE = FILE_PATHS['WEBSOCKET_STATUS_FILE']

API_RATE_LIMIT_SECONDS = API_RATE_LIMIT['REST_CALL_INTERVAL']
MAIN_CYCLE_SLEEP_SECONDS = MAIN_CYCLE_CONFIG['SLEEP_SECONDS']

DEFAULT_CONTROL_STATE = get_default_control_state()

MAX_OPEN_POSITIONS = POSITION_CONFIG['MAX_OPEN_POSITIONS']
RISK_PER_TRADE_RATIO = POSITION_CONFIG['RISK_PER_TRADE_RATIO']
TAKE_PROFIT_RATIO = PROFIT_LOSS_CONFIG['TAKE_PROFIT_RATIO']
STOP_LOSS_RATIO = PROFIT_LOSS_CONFIG['STOP_LOSS_RATIO']

FILTER_MIN_PRICE = FILTER_CONFIG['FILTER_MIN_PRICE']
FILTER_MIN_VOLUME = FILTER_CONFIG['FILTER_MIN_VOLUME']
FILTER_MIN_RATE = FILTER_CONFIG['FILTER_MIN_RATE']
FILTER_MAX_RATE = FILTER_CONFIG['FILTER_MAX_RATE']

AI_ANALYSIS_ENABLED = AI_CONFIG['AI_ANALYSIS_ENABLED']
AI_MIN_ANALYSIS_SCORE = AI_CONFIG['AI_MIN_ANALYSIS_SCORE']
AI_CONFIDENCE_THRESHOLD = AI_CONFIG['AI_CONFIDENCE_THRESHOLD']
AI_MARKET_ANALYSIS_INTERVAL = AI_CONFIG['AI_MARKET_ANALYSIS_INTERVAL']
AI_ADJUST_FILTERS_AUTOMATICALLY = AI_CONFIG['AI_ADJUST_FILTERS_AUTOMATICALLY']

def validate_config():
    """전체 설정 검증"""
    errors = []
    
    env_errors = validate_environment()
    errors.extend(env_errors)
    
    is_valid, cred_errors = credentials.validate()
    errors.extend(cred_errors)
    
    is_valid, param_errors = validate_trading_params()
    errors.extend(param_errors)
    
    if errors:
        error_msg = "\n".join(f"- {err}" for err in errors)
        raise ValueError(f"설정 오류:\n{error_msg}")
    
    return True

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
    'KIWOOM_REST_BASE_URL',
    'KIWOOM_REST_APPKEY',
    'KIWOOM_REST_SECRETKEY',
    'ACCOUNT_NUMBER',
    'KIWOOM_WEBSOCKET_URL',
    'GEMINI_API_KEY',
    'GEMINI_MODEL_NAME',
    'GEMINI_ENABLE_CROSS_CHECK',

    'TRADING_PARAMS',
    'POSITION_CONFIG',
    'PROFIT_LOSS_CONFIG',
    'FILTER_CONFIG',
    'AI_CONFIG',
    'validate_trading_params',
    'get_trading_params_summary',

    'APILoader',
    'get_api_loader',
    'load_successful_apis',
    'get_api_by_id',
    'get_api_by_category',
    'search_api',
    'is_api_tested',
    'APICategory',

    'UnifiedSettingsManager',
    'get_unified_settings',

    'StandardParameters',
    'ParameterConverter',
    'migrate_parameters',
    'LEGACY_PARAMETER_MAPPING',

    'ConfigManager',
    'get_config',
    'get_setting',
    'set_setting',
    'save_config',
    'reload_config',
    'reset_config',
    'AutoTradeConfig',
    'RiskManagementConfig',
    'TradingConfig',
    'AIConfig',
    'LoggingConfig',
    'NotificationConfig',
    'MainCycleConfig',

    'LOG_FILE_PATH',
    'LOG_LEVEL',
    'LOG_FILE_MAX_BYTES',
    'LOG_FILE_BACKUP_COUNT',
    'CONTROL_FILE_PATH',
    'STRATEGY_STATE_FILE',
    'WEBSOCKET_STATUS_FILE',
    'API_RATE_LIMIT_SECONDS',
    'MAIN_CYCLE_SLEEP_SECONDS',
    'DEFAULT_CONTROL_STATE',
    'MAX_OPEN_POSITIONS',
    'RISK_PER_TRADE_RATIO',
    'TAKE_PROFIT_RATIO',
    'STOP_LOSS_RATIO',
    'FILTER_MIN_PRICE',
    'FILTER_MIN_VOLUME',
    'FILTER_MIN_RATE',
    'FILTER_MAX_RATE',
    'AI_ANALYSIS_ENABLED',
    'AI_MIN_ANALYSIS_SCORE',
    'AI_CONFIDENCE_THRESHOLD',
    'AI_MARKET_ANALYSIS_INTERVAL',
    'AI_ADJUST_FILTERS_AUTOMATICALLY',
    'validate_config',
]