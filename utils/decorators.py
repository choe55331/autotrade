"""
utils/decorators.py
공통 데코레이터
"""
import time
import logging
import functools
from typing import Callable, Any

logger = logging.getLogger(__name__)


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    재시도 데코레이터
    
    Args:
        max_attempts: 최대 시도 횟수
        delay: 초기 지연 시간 (초)
        backoff: 지연 시간 배수
    
    Example:
    """
        @retry(max_attempts=3, delay=1.0)
        def api_call():
            ...
    """
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} 최대 재시도 횟수 도달 ({max_attempts}회): {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"{func.__name__} 실패 (시도 {attempt}/{max_attempts}), "
                        f"{current_delay:.1f}초 후 재시도: {e}"
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return None
        
        return wrapper
    
    return decorator


def timing(func: Callable) -> Callable:
    """
    실행 시간 측정 데코레이터
    
    Example:
        @timing
        """
        def slow_function():
            time.sleep(1)
    """
    @functools.wraps(func)
    """
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        
        logger.debug(
            f"{func.__name__} 실행 시간: {elapsed_time:.3f}초"
        )
        
        return result
    
    return wrapper


def log_execution(level: str = 'INFO'):
    """
    함수 실행 로깅 데코레이터
    
    Args:
        level: 로그 레벨 ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    
    Example:
    """
        @log_execution(level='INFO')
        def process_data():
            ...
    """
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            log_level = getattr(logging, level.upper(), logging.INFO)
            
            logger.log(
                log_level,
                f"{func.__name__} 실행 시작 (args: {args}, kwargs: {kwargs})"
            )
            
            try:
                result = func(*args, **kwargs)
                logger.log(
                    log_level,
                    f"{func.__name__} 실행 완료"
                )
                return result
            except Exception as e:
                logger.error(
                    f"{func.__name__} 실행 중 오류: {e}",
                    exc_info=True
                )
                raise
        
        return wrapper
    
    return decorator


def catch_exceptions(
    default_return: Any = None,
    log_traceback: bool = True
):
    """
    예외 처리 데코레이터

    Args:
        default_return: 예외 발생 시 반환할 기본값
        log_traceback: 트레이스백 로깅 여부

    Example:
    """
        @catch_exceptions(default_return=None)
        def risky_function():
            ...
    """
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_traceback:
                    logger.error(
                        f"{func.__name__} 예외 발생: {e}",
                        exc_info=True
                    )
                else:
                    logger.error(f"{func.__name__} 예외 발생: {e}")
                
                return default_return
        
        return wrapper
    
    return decorator


def rate_limit(calls: int, period: float):
    """
    속도 제한 데코레이터
    
    Args:
        calls: 허용 호출 횟수
        period: 기간 (초)
    
    Example:
    """
        @rate_limit(calls=10, period=60.0)  # 분당 10회
        def api_call():
            ...
    """
    """
    def decorator(func: Callable) -> Callable:
        last_reset = [time.time()]
        call_count = [0]
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_time = time.time()
            
            if current_time - last_reset[0] >= period:
                last_reset[0] = current_time
                call_count[0] = 0
            
            if call_count[0] >= calls:
                wait_time = period - (current_time - last_reset[0])
                logger.warning(
                    f"{func.__name__} 속도 제한 도달, "
                    f"{wait_time:.1f}초 대기 필요"
                )
                time.sleep(wait_time)
                last_reset[0] = time.time()
                call_count[0] = 0
            
            call_count[0] += 1
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def validate_args(**validators):
    """
    인자 검증 데코레이터
    
    Args:
        **validators: {arg_name: validator_function}
    
    Example:
        @validate_args(
        """
            stock_code=validate_stock_code,
            price=validate_price
        )
        def place_order(stock_code, price):
            ...
    """
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            for arg_name, validator in validators.items():
                if arg_name in bound_args.arguments:
                    arg_value = bound_args.arguments[arg_name]
                    is_valid, msg = validator(arg_value)
                    
                    if not is_valid:
                        raise ValueError(
                            f"{func.__name__}() 인자 검증 실패 - {arg_name}: {msg}"
                        )
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def cache_result(ttl: float = 60.0):
    """
    결과 캐싱 데코레이터 (TTL 기반)
    
    Args:
        ttl: Time To Live (초)
    
    Example:
    """
        @cache_result(ttl=300.0)  # 5분 캐싱
        def expensive_function():
            ...
    """
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_time = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            key = str(args) + str(kwargs)
            current_time = time.time()
            
            if key in cache:
                if current_time - cache_time[key] < ttl:
                    logger.debug(f"{func.__name__} 캐시 히트")
                    return cache[key]
            
            logger.debug(f"{func.__name__} 캐시 미스")
            result = func(*args, **kwargs)
            
            cache[key] = result
            cache_time[key] = current_time
            
            return result
        
        return wrapper
    
    return decorator


def singleton(cls):
    """
    싱글톤 클래스 데코레이터
    
    Example:
        @singleton
        """
        class Config:
            ...
    """
    """
    instances = {}
    
    @functools.wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return wrapper


__all__ = [
    'retry',
    'timing',
    'log_execution',
    'catch_exceptions',
    'rate_limit',
    'validate_args',
    'cache_result',
    'singleton',
]