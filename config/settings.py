"""
config/settings.py
기본 설정 파일
"""
import os
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent

LOG_CONFIG = {
    'LOG_FILE_PATH': BASE_DIR / 'logs' / 'bot.log',
    'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
    'LOG_FILE_MAX_BYTES': 5 * 1024 * 1024,
    'LOG_FILE_BACKUP_COUNT': 5,
    'LOG_FORMAT': '%(asctime)s - [%(levelname)s] - %(name)s - %(message)s (%(filename)s:%(lineno)d)'
}

FILE_PATHS = {
    'CONTROL_FILE': BASE_DIR / 'data' / 'control.json',
    'STRATEGY_STATE_FILE': BASE_DIR / 'data' / 'strategy_state.json',
    'WEBSOCKET_STATUS_FILE': BASE_DIR / 'data' / 'websocket_status.txt',
}

API_RATE_LIMIT = {
    'REST_CALL_INTERVAL': 0.3,
    'REST_MAX_RETRIES': 3,
    'REST_RETRY_BACKOFF': 1.0,
    'WEBSOCKET_RECONNECT_DELAY': 5,
    'WEBSOCKET_MAX_RECONNECTS': 10,
}

MAIN_CYCLE_CONFIG = {
    'SLEEP_SECONDS': 60,
    'HEALTH_CHECK_INTERVAL': 300,
}

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

def validate_environment():
    """환경 설정 검증"""
    errors = []
    
    log_dir = LOG_CONFIG['LOG_FILE_PATH'].parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    return errors

__all__ = [
    'LOG_CONFIG',
    'FILE_PATHS',
    'API_RATE_LIMIT',
    'MAIN_CYCLE_CONFIG',
    'get_default_control_state',
    'validate_environment',
]