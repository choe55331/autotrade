"""
utils/logger.py
로깅 설정
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(
    name: str = 'trading_bot',
    log_file: Optional[Path] = None,
    level: str = 'INFO',
    max_bytes: int = 5 * 1024 * 1024,  # 5MB
    backup_count: int = 5,
    console: bool = True
) -> logging.Logger:
    """
    로거 설정
    
    Args:
        name: 로거 이름
        log_file: 로그 파일 경로
        level: 로그 레벨 ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        max_bytes: 로그 파일 최대 크기
        backup_count: 백업 파일 개수
        console: 콘솔 출력 여부
    
    Returns:
        설정된 Logger 인스턴스
    """
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 기존 핸들러 제거
    logger.handlers.clear()
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s - [%(levelname)s] - %(name)s - %(message)s '
        '(%(filename)s:%(lineno)d)',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 파일 핸들러
    if log_file:
        # 로그 디렉토리 생성
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # 콘솔 핸들러
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    로거 가져오기
    
    Args:
        name: 로거 이름 (None이면 루트 로거)
    
    Returns:
        Logger 인스턴스
    """
    if name:
        return logging.getLogger(name)
    else:
        return logging.getLogger()


# 기본 로거 설정
def configure_default_logger():
    """기본 로거 설정"""
    try:
        from config import LOG_CONFIG
        
        setup_logger(
            name='trading_bot',
            log_file=LOG_CONFIG.get('LOG_FILE_PATH'),
            level=LOG_CONFIG.get('LOG_LEVEL', 'INFO'),
            max_bytes=LOG_CONFIG.get('LOG_FILE_MAX_BYTES', 5 * 1024 * 1024),
            backup_count=LOG_CONFIG.get('LOG_FILE_BACKUP_COUNT', 5),
            console=True
        )
    except ImportError:
        # config 모듈이 없을 경우 기본 설정
        setup_logger(
            name='trading_bot',
            log_file=Path('logs/bot.log'),
            level='INFO',
            console=True
        )


class LoggerMixin:
    """
    로거 믹스인 클래스
    """
    
    def setup_logger(self, name: str = None):
        """로거 설정"""
        if name is None:
            name = self.__class__.__name__
        self._logger = logging.getLogger(name)
    
    @property
    def logger(self):
        """로거 프로퍼티"""
        if not hasattr(self, '_logger'):
            self.setup_logger()
        return self._logger
    
    @logger.setter
    def logger(self, value):
        """로거 설정"""
        self._logger = value


__all__ = ['setup_logger', 'get_logger', 'configure_default_logger', 'LoggerMixin']