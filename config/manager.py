"""
AutoTrade Pro - Unified Configuration Manager
통합 설정 관리자 (v5.6+ Enhanced)
"""

"""
COMPREHENSIVE 개선:
- 5개 설정 시스템을 단일 매니저로 통합
- Singleton pattern으로 전역 접근
- Type-safe with Pydantic validation
- Event listeners for dynamic settings
- JSON/YAML import/export
- Backward compatibility with all legacy systems
"""
from pathlib import Path
from typing import Any, Optional, Callable, Dict, List
from .schemas import AutoTradeConfig
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    통합 설정 관리자 (싱글톤) - Enhanced

    Features:
    - Pydantic-based type-safe configuration
    - Event listeners for configuration changes
    - JSON/YAML import/export
    - Backward compatibility with legacy config systems
    - Dot notation access: get('risk_management.max_position_size')

    Usage:
    """
        from config import get_config, get_setting, set_setting

        # Get full config
        config = get_config()
        max_pos = config.risk_management.max_position_size

        # Get with dot notation
        max_pos = get_setting('risk_management.max_position_size')

        # Set value with event notification
        set_setting('risk_management.max_position_size', 0.25)

        # Register change listener
        def on_risk_change(path, old, new):
            print(f"Risk setting changed: {path} = {new}")

        manager = ConfigManager()
        manager.register_change_listener('risk_management', on_risk_change)
    """

"""
    _instance: Optional['ConfigManager'] = None
    _config: Optional[AutoTradeConfig] = None
    _change_listeners: Dict[str, List[Callable]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._change_listeners = {}
        return cls._instance

    def __init__(self):
        """초기화 (한 번만 실행)"""
        if self._config is None:
            self._load_config()

    def _load_config(self):
        """설정 파일 로드"""
        config_path = Path('config/settings.yaml')

        if config_path.exists():
            try:
                self._config = AutoTradeConfig.from_yaml(str(config_path))
                logger.info(f"✓ 설정 로드 완료: {config_path}")
            except Exception as e:
                logger.warning(f"[WARNING]️ 설정 로드 실패: {e}, 기본값 사용")
                self._config = AutoTradeConfig()
        else:
            self._config = AutoTradeConfig()
            self._save_config()
            logger.info(f"✓ 기본 설정 생성: {config_path}")

    def _save_config(self):
        """설정 파일 저장"""
        config_path = Path('config/settings.yaml')
        config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config.save_yaml(str(config_path))

    @property
    def config(self) -> AutoTradeConfig:
        """설정 객체 반환"""
        return self._config

    def get(self, path: str, default=None) -> Any:
        """
        Dot notation으로 설정 가져오기

        Args:
            path: 설정 경로 (예: 'risk_management.max_position_size')
            default: 기본값

        Returns:
            설정 값
        """
        return self._config.get(path, default)

    def set(self, path: str, value: Any, save: bool = True):
        """
        Dot notation으로 설정 변경

        Args:
            path: 설정 경로
            value: 새 값
            save: 즉시 저장 여부
        """
        old_value = self.get(path)

        self._config.set(path, value)

        self._notify_change(path, old_value, value)

        if save:
            self._save_config()

        logger.info(f"✓ 설정 변경: {path} = {value}")

    def save(self):
        """현재 설정을 파일에 저장"""
        self._save_config()
        logger.info("✓ 설정 저장 완료")

    def reload(self):
        """설정 파일 다시 로드"""
        self._load_config()
        logger.info("✓ 설정 재로드 완료")

    def reset_to_defaults(self):
        """설정을 기본값으로 초기화"""
        self._config = AutoTradeConfig()
        self._save_config()
        logger.info("✓ 설정 기본값 복원 완료")

    def get_category(self, category: str) -> Any:
        """
        카테고리별 설정 가져오기

        Args:
            category: 카테고리 이름 (risk_management, trading, ai, etc.)

        Returns:
            카테고리 설정 객체
        """
        return getattr(self._config, category, None)

    def update_category(self, category: str, values: dict, save_immediately: bool = True):
        """
        카테고리별 설정 업데이트

        Args:
            category: 카테고리 이름
            values: 업데이트할 값들
            save_immediately: 즉시 저장 여부
        """
        category_obj = self.get_category(category)
        if category_obj is None:
            raise ValueError(f"Unknown category: {category}")

        for key, value in values.items():
            if hasattr(category_obj, key):
                old_value = getattr(category_obj, key)
                setattr(category_obj, key, value)

                full_path = f"{category}.{key}"
                self._notify_change(full_path, old_value, value)
            else:
                raise ValueError(f"Unknown setting: {category}.{key}")

        if save_immediately:
            self.save()

    def export_to_json(self, file_path: str) -> bool:
        """
        JSON 형식으로 내보내기

        Args:
            file_path: 저장할 파일 경로

        Returns:
            성공 여부
        """
        try:
            self._config.save_json(file_path)
            logger.info(f"✓ JSON 설정 내보내기 완료: {file_path}")
            return True
        except Exception as e:
            logger.error(f"[X] JSON 내보내기 실패: {e}")
            return False

    def import_from_json(self, file_path: str) -> bool:
        """
        JSON 형식에서 가져오기

        Args:
            file_path: 읽을 파일 경로

        Returns:
            성공 여부
        """
        try:
            self._config = AutoTradeConfig.from_json(file_path)
            self._save_config()
            logger.info(f"✓ JSON 설정 가져오기 완료: {file_path}")
            return True
        except Exception as e:
            logger.error(f"[X] JSON 가져오기 실패: {e}")
            return False

    def register_change_listener(self, key_path: str, callback: Callable):
        """
        설정 변경 리스너 등록

        Args:
            key_path: 설정 경로 (예: 'risk_management' 또는 'risk_management.max_position_size')
            callback: 콜백 함수 (path, old_value, new_value)

        Example:
        """
            def on_risk_change(path, old, new):
                print(f"Risk changed: {path} = {new}")

            manager.register_change_listener('risk_management', on_risk_change)
        """
        """
        if key_path not in self._change_listeners:
            self._change_listeners[key_path] = []
        self._change_listeners[key_path].append(callback)
        logger.debug(f"✓ 리스너 등록: {key_path}")

    def unregister_change_listener(self, key_path: str, callback: Callable):
        """
        설정 변경 리스너 제거

        Args:
            key_path: 설정 경로
            callback: 제거할 콜백 함수
        """
        if key_path in self._change_listeners:
            try:
                self._change_listeners[key_path].remove(callback)
                logger.debug(f"✓ 리스너 제거: {key_path}")
            except ValueError:
                pass

    def _notify_change(self, key_path: str, old_value: Any, new_value: Any):
        """
        설정 변경 알림

        Args:
            key_path: 변경된 설정 경로
            old_value: 이전 값
            new_value: 새 값
        """
        if key_path in self._change_listeners:
            for callback in self._change_listeners[key_path]:
                try:
                    callback(key_path, old_value, new_value)
                except Exception as e:
                    logger.error(f"[X] 리스너 실행 실패: {e}")

        parts = key_path.split('.')
        for i in range(len(parts)):
            prefix = '.'.join(parts[:i+1])
            if prefix in self._change_listeners and prefix != key_path:
                for callback in self._change_listeners[prefix]:
                    try:
                        callback(key_path, old_value, new_value)
                    except Exception as e:
                        logger.error(f"[X] 리스너 실행 실패 ({prefix}): {e}")



_manager: Optional[ConfigManager] = None


def _get_manager() -> ConfigManager:
    """Get global ConfigManager instance"""
    global _manager
    if _manager is None:
        _manager = ConfigManager()
    return _manager


def get_config() -> AutoTradeConfig:
    """
    전역 설정 객체 가져오기

    Returns:
        AutoTradeConfig 인스턴스
    """
    return _get_manager().config


def get_setting(path: str, default=None) -> Any:
    """
    Dot notation으로 설정 값 가져오기

    Args:
        path: 설정 경로 (예: 'risk_management.max_position_size')
        default: 기본값

    Returns:
        설정 값

    Example:
    """
        max_pos = get_setting('risk_management.max_position_size')
        ai_threshold = get_setting('ai.confidence_threshold', 0.7)
    """
    """
    return _get_manager().get(path, default)


def set_setting(path: str, value: Any, save: bool = True):
    """
    Dot notation으로 설정 값 변경

    Args:
        path: 설정 경로
        value: 새 값
        save: 즉시 저장 여부

    Example:
        set_setting('risk_management.max_position_size', 0.25)
        """
        set_setting('ai.enabled', False, save=True)
    """
    _get_manager().set(path, value, save)


"""
def save_config():
    """현재 설정을 파일에 저장"""
    _get_manager().save()


def reload_config():
    """설정 파일 다시 로드"""
    _get_manager().reload()


def reset_config():
    """설정을 기본값으로 초기화"""
    _get_manager().reset_to_defaults()


def register_config_listener(path: str, callback: Callable):
    """
    설정 변경 리스너 등록

    Args:
        path: 설정 경로
        callback: 콜백 함수 (path, old_value, new_value)
    """
    _get_manager().register_change_listener(path, callback)


def unregister_config_listener(path: str, callback: Callable):
    """
    설정 변경 리스너 제거

    Args:
        path: 설정 경로
        callback: 제거할 콜백 함수
    """
    _get_manager().unregister_change_listener(path, callback)


def export_config_to_json(file_path: str) -> bool:
    """
    설정을 JSON 파일로 내보내기

    Args:
        file_path: 저장할 파일 경로

    Returns:
        성공 여부
    """
    return _get_manager().export_to_json(file_path)


def import_config_from_json(file_path: str) -> bool:
    """
    JSON 파일에서 설정 가져오기

    Args:
        file_path: 읽을 파일 경로

    Returns:
        성공 여부
    """
    return _get_manager().import_from_json(file_path)



get_unified_settings = lambda: _get_manager()


def get_trading_params() -> Dict[str, Any]:
    """Legacy: 매매 파라미터 반환"""
    config = get_config()
    return {
        'MAX_OPEN_POSITIONS': config.risk_management.position_limit,
        'RISK_PER_TRADE_RATIO': config.risk_management.max_position_size,
        'TAKE_PROFIT_RATIO': config.risk_management.take_profit_pct,
        'STOP_LOSS_RATIO': config.risk_management.stop_loss_pct,
        'TRAILING_STOP_ENABLED': config.risk_management.enable_trailing_stop,
        'TRAILING_STOP_RATIO': config.risk_management.trailing_stop_pct,
    }


def validate_trading_params() -> tuple:
    """Legacy: 매매 파라미터 검증"""
    errors = []
    config = get_config()

    max_pos = config.risk_management.position_limit
    if not (1 <= max_pos <= 50):
        errors.append("position_limit는 1~50 사이여야 합니다")

    risk_ratio = config.risk_management.max_position_size
    if not (0 < risk_ratio <= 1.0):
        errors.append("max_position_size는 0~1 사이여야 합니다")

    stop_loss = config.risk_management.stop_loss_pct
    if not (0 < stop_loss <= 1.0):
        errors.append("stop_loss_pct는 0~1 사이여야 합니다")

    take_profit = config.risk_management.take_profit_pct
    if not (0 < take_profit <= 2.0):
        errors.append("take_profit_pct는 0~2 사이여야 합니다")

    return len(errors) == 0, errors


__all__ = [
    'ConfigManager',

    'get_config',
    'get_setting',
    'set_setting',
    'save_config',
    'reload_config',
    'reset_config',

    'register_config_listener',
    'unregister_config_listener',

    'export_config_to_json',
    'import_config_from_json',

    'get_unified_settings',
    'get_trading_params',
    'validate_trading_params',
]
