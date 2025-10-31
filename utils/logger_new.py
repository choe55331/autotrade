"""
utils/logger_new.py
Loguru 기반 고급 로깅 시스템
"""
import sys
from pathlib import Path
from typing import Optional
from loguru import logger


class LoguruLogger:
    """Loguru 로거 래퍼 클래스 (싱글톤)"""

    _instance: Optional['LoguruLogger'] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """초기화 (한 번만 실행)"""
        if not self._initialized:
            self._setup_logger()
            LoguruLogger._initialized = True

    def _setup_logger(self):
        """로거 초기 설정"""
        try:
            from config.config_manager import get_config
            config = get_config()
            log_config = config.logging
        except ImportError:
            # 기본 설정 사용
            log_config = {
                'level': 'INFO',
                'file_path': 'logs/bot.log',
                'max_file_size': 10485760,  # 10MB
                'backup_count': 30,
                'rotation': '00:00',
                'format': '{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}',
                'console_output': True,
                'colored_output': True,
            }

        # 기존 핸들러 제거
        logger.remove()

        # 콘솔 핸들러 (컬러 출력)
        if log_config.get('console_output', True):
            logger.add(
                sys.stdout,
                format=log_config.get('format'),
                level=log_config.get('level', 'INFO'),
                colorize=log_config.get('colored_output', True),
                backtrace=True,
                diagnose=True,
            )

        # 파일 핸들러 (로테이션)
        log_file = log_config.get('file_path', 'logs/bot.log')
        log_path = Path(log_file)

        # 로그 디렉토리 생성
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_path,
            format=log_config.get('format'),
            level=log_config.get('level', 'INFO'),
            rotation=log_config.get('rotation', '00:00'),  # 매일 자정
            retention=log_config.get('backup_count', 30),  # 30일 보관
            compression='zip',  # 압축
            encoding='utf-8',
            backtrace=True,
            diagnose=True,
        )

        # 에러 전용 파일 핸들러
        error_log_path = log_path.parent / 'error.log'
        logger.add(
            error_log_path,
            format=log_config.get('format'),
            level='ERROR',
            rotation='10 MB',
            retention=60,  # 60일 보관
            compression='zip',
            encoding='utf-8',
            backtrace=True,
            diagnose=True,
        )

    def get_logger(self):
        """로거 인스턴스 반환"""
        return logger

    def bind_context(self, **kwargs):
        """컨텍스트 바인딩"""
        return logger.bind(**kwargs)


# 싱글톤 인스턴스
_loguru_logger = LoguruLogger()


def get_logger():
    """전역 로거 가져오기"""
    return _loguru_logger.get_logger()


def setup_logger(
    name: str = 'trading_bot',
    log_file: Optional[Path] = None,
    level: str = 'INFO',
    **kwargs
):
    """
    기존 호환성을 위한 setup_logger 함수

    Args:
        name: 로거 이름 (현재는 무시됨 - Loguru는 전역 로거 사용)
        log_file: 로그 파일 경로 (현재는 config에서 설정)
        level: 로그 레벨
        **kwargs: 추가 인자 (현재는 무시됨)

    Returns:
        Loguru logger 인스턴스
    """
    return get_logger()


class LoggerMixin:
    """
    로거 믹스인 클래스 (Loguru 버전)
    """

    @property
    def logger(self):
        """로거 프로퍼티"""
        if not hasattr(self, '_logger'):
            # 클래스 이름을 컨텍스트로 바인딩
            self._logger = get_logger().bind(classname=self.__class__.__name__)
        return self._logger


# 편의 함수들
def debug(message: str, **kwargs):
    """DEBUG 로그"""
    get_logger().debug(message, **kwargs)


def info(message: str, **kwargs):
    """INFO 로그"""
    get_logger().info(message, **kwargs)


def warning(message: str, **kwargs):
    """WARNING 로그"""
    get_logger().warning(message, **kwargs)


def error(message: str, **kwargs):
    """ERROR 로그"""
    get_logger().error(message, **kwargs)


def critical(message: str, **kwargs):
    """CRITICAL 로그"""
    get_logger().critical(message, **kwargs)


def exception(message: str, **kwargs):
    """예외 로그 (스택 트레이스 포함)"""
    get_logger().exception(message, **kwargs)


# 기존 호환성을 위한 함수
def configure_default_logger():
    """기본 로거 설정 (기존 호환)"""
    # Loguru는 자동으로 초기화됨
    pass


__all__ = [
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
]
