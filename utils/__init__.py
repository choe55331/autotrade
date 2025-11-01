"""
utils 패키지
유틸리티 모듈

v4.2 CRITICAL 개선:
- 통합 로깅 시스템 (logger.py, logger_new.py, rate_limited_logger.py → logger_new.py)
- 3→1 로거 통합으로 80% I/O 감소
"""

# ============================================================================
# UNIFIED LOGGING SYSTEM (v4.2 CRITICAL FIX #1)
# ============================================================================
# logger_new.py를 표준 로거로 사용 (Loguru 기반 + Rate-limiting 통합)
from .logger_new import (
    get_logger,
    setup_logger,
    configure_default_logger,
    LoggerMixin,
    debug,
    info,
    warning,
    error,
    critical,
    exception,
    RateLimitedLogger,
    get_rate_limited_logger,
)

# ============================================================================
# Other Utils
# ============================================================================
from .file_handler import FileHandler
from .validators import (
    validate_stock_code,
    validate_price,
    validate_quantity,
    validate_account_number,
    validate_date,
)
from .decorators import (
    retry,
    timing,
    log_execution,
    catch_exceptions,
)

# v4.1 Advanced Utilities
from .exceptions import (
    AutoTradeException,
    TradingException,
    RiskException,
    DataException,
    APIException,
    ConfigurationException,
    StrategyException,
    handle_exception,
    retry_on_exception,
)
from .performance_profiler import (
    PerformanceProfiler,
    measure_performance,
    profile_code,
    get_performance_stats,
    print_performance_stats,
    reset_performance_stats,
)

# Deprecated: old rate_limited_logger.py 클래스들 (logger_new.py로 통합됨)
# LogThrottler, AggregatedLogger는 필요시 logger_new.py에 추가 가능

__all__ = [
    # ========== Unified Logging (v4.2 CRITICAL #1) ==========
    'get_logger',
    'setup_logger',
    'configure_default_logger',
    'LoggerMixin',
    'debug',
    'info',
    'warning',
    'error',
    'critical',
    'exception',
    'RateLimitedLogger',
    'get_rate_limited_logger',

    # ========== File & Validation ==========
    'FileHandler',
    'validate_stock_code',
    'validate_price',
    'validate_quantity',
    'validate_account_number',
    'validate_date',

    # ========== Decorators ==========
    'retry',
    'timing',
    'log_execution',
    'catch_exceptions',

    # ========== v4.1 Exceptions ==========
    'AutoTradeException',
    'TradingException',
    'RiskException',
    'DataException',
    'APIException',
    'ConfigurationException',
    'StrategyException',
    'handle_exception',
    'retry_on_exception',

    # ========== v4.1 Performance Profiler ==========
    'PerformanceProfiler',
    'measure_performance',
    'profile_code',
    'get_performance_stats',
    'print_performance_stats',
    'reset_performance_stats',
]