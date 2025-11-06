"""
config/config_manager.py
YAML 기반 설정 관리 시스템 (Backward Compatibility Layer)
"""

⚠️  DEPRECATED: 이 파일은 backward compatibility를 위해 유지됩니다.
새 코드에서는 config.manager를 사용하세요:
    from config.manager import get_config, get_setting, set_setting
from typing import Dict, Any, Optional
from pathlib import Path
from .manager import (
    get_config as _get_config,
    get_setting as _get_setting,
    set_setting as _set_setting,
    save_config as _save_config,
    reload_config as _reload_config,
    ConfigManager as _ConfigManager,
)


class Config:
    """통합 설정 클래스 (Legacy Wrapper)"""

    def __init__(self):
        """설정 초기화"""
        self._config_manager = _get_config()

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        점(.) 구분 경로로 설정 값 가져오기

        Args:
            key_path: 설정 경로 (예: 'api.kiwoom.timeout')
            default: 기본값

        Returns:
            설정 값
        """
        return _get_setting(key_path, default)

    def set(self, key_path: str, value: Any):
        """
        점(.) 구분 경로로 설정 값 변경

        Args:
            key_path: 설정 경로
            value: 새 값
        """
        _set_setting(key_path, value, save=True)

    @property
    def system(self) -> Dict[str, Any]:
        """시스템 설정"""
        config = _get_config()
        return {
            'trading_enabled': config.system.trading_enabled,
            'test_mode': config.system.test_mode,
            'auto_start': config.system.auto_start,
            'logging_level': config.system.logging_level,
            'max_concurrent_analysis': config.system.max_concurrent_analysis,
        }

    @property
    def logging(self) -> Dict[str, Any]:
        """로깅 설정"""
        config = _get_config()
        return {
            'level': config.logging.level,
            'console_level': config.logging.console_level,
            'file_path': config.logging.file_path,
            'max_file_size': config.logging.max_file_size,
            'backup_count': config.logging.backup_count,
            'rotation': config.logging.rotation,
            'format': config.logging.format,
            'console_output': config.logging.console_output,
            'colored_output': config.logging.colored_output,
        }

    @property
    def database(self) -> Dict[str, Any]:
        """데이터베이스 설정"""
        return _get_config().database

    @property
    def api(self) -> Dict[str, Any]:
        """API 설정"""
        return _get_config().api

    @property
    def position(self) -> Dict[str, Any]:
        """포지션 관리 설정"""
        return _get_config().position

    @property
    def profit_loss(self) -> Dict[str, Any]:
        """손익 관리 설정"""
        return _get_config().profit_loss

    @property
    def scanning(self) -> Dict[str, Any]:
        """스캐닝 설정"""
        return _get_config().scanning

    @property
    def scoring(self) -> Dict[str, Any]:
        """스코어링 설정"""
        return _get_config().scoring

    @property
    def risk_management(self) -> Dict[str, Any]:
        """리스크 관리 설정"""
        config = _get_config()
        rm = config.risk_management
        return {
            'max_position_size': rm.max_position_size,
            'stop_loss_pct': rm.stop_loss_pct,
            'take_profit_pct': rm.take_profit_pct,
            'position_limit': rm.position_limit,
            'max_daily_loss': rm.max_daily_loss,
            'enable_trailing_stop': rm.enable_trailing_stop,
            'trailing_stop_pct': rm.trailing_stop_pct,
        }

    @property
    def ai(self) -> Dict[str, Any]:
        """AI 설정"""
        config = _get_config()
        ai = config.ai_analysis
        return {
            'enabled': ai.enabled,
            'default_analyzer': ai.default_analyzer,
            'confidence_threshold': ai.confidence_threshold,
            'timeout_seconds': ai.timeout_seconds,
            'models': ai.models,
        }

    @property
    def dashboard(self) -> Dict[str, Any]:
        """대시보드 설정"""
        return _get_config().dashboard

    @property
    def notification(self) -> Dict[str, Any]:
        """알림 설정"""
        config = _get_config()
        notif = config.notification
        return {
            'enabled': notif.enabled,
            'telegram_enabled': notif.telegram_enabled,
            'email_enabled': notif.email_enabled,
        }

    @property
    def backtesting(self) -> Dict[str, Any]:
        """백테스팅 설정"""
        config = _get_config()
        bt = config.backtesting
        return {
            'default_initial_capital': bt.default_initial_capital,
            'commission_rate': bt.commission_rate,
            'slippage_pct': bt.slippage_pct,
            'generate_report': bt.generate_report,
            'report_format': bt.report_format,
        }

    @property
    def main_cycle(self) -> Dict[str, Any]:
        """메인 사이클 설정"""
        config = _get_config()
        mc = config.main_cycle
        return {
            'sleep_seconds': mc.sleep_seconds,
            'health_check_interval': mc.health_check_interval,
        }

    @property
    def development(self) -> Dict[str, Any]:
        """개발 설정"""
        return _get_config().development

    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 반환"""
        return _get_config().model_dump()

    def get_trading_params_summary(self) -> str:
        """매매 파라미터 요약"""
        config = _get_config()
        pos = config.position
        pl = config.profit_loss

        return f"""
        === 매매 파라미터 ===
        최대 포지션: {pos.get('max_open_positions', 5)}개
        거래당 리스크: {pos.get('risk_per_trade_ratio', 0.20)*100:.1f}%
        목표 수익률: {pl.get('take_profit_ratio', 0.10)*100:.1f}%
        손절 비율: {pl.get('stop_loss_ratio', -0.05)*100:.1f}%

        AI 분석: {'활성' if config.ai_analysis.enabled else '비활성'}
        - 신뢰도: {config.ai_analysis.confidence_threshold:.2f}


class ConfigManager:
    """설정 관리자 (Legacy Wrapper)"""

    _instance: Optional['ConfigManager'] = None
    _config: Optional[Config] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """초기화"""
        if self._config is None:
            self._config = Config()

    def get_config(self) -> Config:
        """설정 객체 반환"""
        if self._config is None:
            self._config = Config()
        return self._config

    def reload_config(self, config_path: Optional[Path] = None):
        """설정 재로드"""
        _reload_config()
        self._config = Config()

    def save_config(self, config_path: Optional[Path] = None):
        """현재 설정을 YAML 파일로 저장"""
        _save_config()


_config_manager = ConfigManager()


def get_config() -> Config:
    """전역 설정 객체 가져오기"""
    return _config_manager.get_config()


def reload_config(config_path: Optional[Path] = None):
    """설정 재로드"""
    _config_manager.reload_config(config_path)


def save_config(config_path: Optional[Path] = None):
    """설정 저장"""
    _config_manager.save_config(config_path)


def get_trading_params() -> Dict[str, Any]:
    """매매 파라미터 반환 (기존 호환)"""
    from .manager import get_trading_params as _get_trading_params
    return _get_trading_params()


def validate_trading_params() -> tuple:
    """매매 파라미터 검증 (기존 호환)"""
    from .manager import validate_trading_params as _validate_trading_params
    return _validate_trading_params()


__all__ = [
    'Config',
    'ConfigManager',
    'get_config',
    'reload_config',
    'save_config',
    'get_trading_params',
    'validate_trading_params',
]
