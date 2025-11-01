"""
AutoTrade Pro - Unified Configuration Manager
통합 설정 관리자 (v4.2 CRITICAL #3)

CRITICAL 개선:
- 5개 설정 시스템을 단일 매니저로 통합
- Singleton pattern으로 전역 접근
- Type-safe with Pydantic validation
"""
from pathlib import Path
from typing import Any, Optional
from .schemas import AutoTradeConfig


class ConfigManager:
    """
    통합 설정 관리자 (싱글톤)

    Usage:
        from config import get_config, get_setting, set_setting

        # Get full config
        config = get_config()
        max_pos = config.risk_management.max_position_size

        # Get with dot notation
        max_pos = get_setting('risk_management.max_position_size')

        # Set value
        set_setting('risk_management.max_position_size', 0.25)
    """

    _instance: Optional['ConfigManager'] = None
    _config: Optional[AutoTradeConfig] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
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
                print(f"✓ 설정 로드 완료: {config_path}")
            except Exception as e:
                print(f"⚠ 설정 로드 실패: {e}, 기본값 사용")
                self._config = AutoTradeConfig()
        else:
            # 설정 파일이 없으면 기본값으로 생성
            self._config = AutoTradeConfig()
            self._save_config()
            print(f"✓ 기본 설정 생성: {config_path}")

    def _save_config(self):
        """설정 파일 저장"""
        config_path = Path('config/settings.yaml')
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

    def set(self, path: str, value: Any):
        """
        Dot notation으로 설정 변경

        Args:
            path: 설정 경로
            value: 새 값
        """
        self._config.set(path, value)

    def save(self):
        """현재 설정을 파일에 저장"""
        self._save_config()

    def reload(self):
        """설정 파일 다시 로드"""
        self._load_config()

    def reset_to_defaults(self):
        """설정을 기본값으로 초기화"""
        self._config = AutoTradeConfig()
        self._save_config()

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

        # Update values
        for key, value in values.items():
            if hasattr(category_obj, key):
                setattr(category_obj, key, value)
            else:
                raise ValueError(f"Unknown setting: {category}.{key}")

        if save_immediately:
            self.save()


# ============================================================================
# Global Functions (편의 함수)
# ============================================================================

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
        max_pos = get_setting('risk_management.max_position_size')
        ai_threshold = get_setting('ai.confidence_threshold', 0.7)
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
        set_setting('ai.enabled', False, save=True)
    """
    _get_manager().set(path, value)
    if save:
        _get_manager().save()


def save_config():
    """현재 설정을 파일에 저장"""
    _get_manager().save()


def reload_config():
    """설정 파일 다시 로드"""
    _get_manager().reload()


def reset_config():
    """설정을 기본값으로 초기화"""
    _get_manager().reset_to_defaults()


# ============================================================================
# Backward Compatibility (기존 코드 호환성)
# ============================================================================

# Alias for unified_settings compatibility
get_unified_settings = get_config


__all__ = [
    'ConfigManager',
    'get_config',
    'get_setting',
    'set_setting',
    'save_config',
    'reload_config',
    'reset_config',
    'get_unified_settings',  # 기존 호환성
]
