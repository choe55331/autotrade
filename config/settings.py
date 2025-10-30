"""
config/settings.py
기본 설정 파일
"""
import os
from pathlib import Path
from typing import Dict, Any

# 프로젝트 루트 경로
BASE_DIR = Path(__file__).resolve().parent.parent

# 로그 설정
LOG_CONFIG = {
    'LOG_FILE_PATH': BASE_DIR / 'logs' / 'bot.log',
    'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
    'LOG_FILE_MAX_BYTES': 5 * 1024 * 1024,  # 5MB
    'LOG_FILE_BACKUP_COUNT': 5,
    'LOG_FORMAT': '%(asctime)s - [%(levelname)s] - %(name)s - %(message)s (%(filename)s:%(lineno)d)'
}

# 파일 경로
FILE_PATHS = {
    'CONTROL_FILE': BASE_DIR / 'control.json',
    'STRATEGY_STATE_FILE': BASE_DIR / 'strategy_state.json',
    'WEBSOCKET_STATUS_FILE': BASE_DIR / 'websocket_status.txt',
}

# API 호출 제한
API_RATE_LIMIT = {
    'REST_CALL_INTERVAL': 0.3,  # 초
    'REST_MAX_RETRIES': 3,
    'REST_RETRY_BACKOFF': 1.0,
    'WEBSOCKET_RECONNECT_DELAY': 5,
    'WEBSOCKET_MAX_RECONNECTS': 10,
}

# 메인 사이클 설정
MAIN_CYCLE_CONFIG = {
    'SLEEP_SECONDS': 60,
    'HEALTH_CHECK_INTERVAL': 300,  # 5분
}

# 기본 제어 상태
def get_default_control_state() -> Dict[str, Any]:
    """기본 제어 상태 반환"""
    from .trading_params import TRADING_PARAMS
    
    return {
        'run': True,
        'pause_buy': False,
        'pause_sell': False,
        **TRADING_PARAMS,
        'AI_ANALYSIS_ENABLED': True,
        'AI_MIN_ANALYSIS_SCORE': 7.0,
        'AI_CONFIDENCE_THRESHOLD': 'Medium',
        'AI_ADJUST_FILTERS_AUTOMATICALLY': False,
    }

# 환경 검증
def validate_environment():
    """환경 설정 검증"""
    errors = []
    
    # 로그 디렉토리 생성
    log_dir = LOG_CONFIG['LOG_FILE_PATH'].parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    return errors

# 설정 내보내기
__all__ = [
    'LOG_CONFIG',
    'FILE_PATHS',
    'API_RATE_LIMIT',
    'MAIN_CYCLE_CONFIG',
    'get_default_control_state',
    'validate_environment',
]