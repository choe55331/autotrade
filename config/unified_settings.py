"""
AutoTrade Pro - 통합 설정 관리 시스템 (Backward Compatibility Layer)

DEPRECATED: 이 파일은 backward compatibility를 위해 유지됩니다.
새 코드에서는 config.manager를 사용하세요:
    from config.manager import get_config, get_setting, set_setting
"""
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import logging

from .manager import (
    ConfigManager as _UnifiedConfigManager,
    get_config as _get_config,
    get_setting as _get_setting,
    set_setting as _set_setting,
    register_config_listener as _register_listener,
    export_config_to_json as _export_json,
    import_config_from_json as _import_json,
)

logger = logging.getLogger(__name__)


class UnifiedSettingsManager:
    """
    통합 설정 관리자 (Legacy Wrapper)

    [WARNING]️  이 클래스는 backward compatibility를 위해 유지됩니다.
    새 코드에서는 config.manager.ConfigManager를 사용하세요.
    """

    DEFAULT_SETTINGS = {}

    def __init__(self, config_path: Optional[Path] = None):
        """
        통합 설정 관리자 초기화

        Args:
            config_path: 설정 파일 경로 (무시됨 - 호환성을 위해 유지)
        """
        self._manager = _UnifiedConfigManager()
        self.settings = {}
        self.change_listeners: Dict[str, list] = {}
        logger.info("UnifiedSettingsManager initialized (Legacy wrapper)")

    def load(self) -> Dict[str, Any]:
        """설정 파일에서 로드"""
        self.settings = _get_config().model_dump()
        return self.settings

    def save(self) -> bool:
        """설정을 파일에 저장"""
        try:
            self._manager.save()
            return True
        except Exception as e:
            logger.error(f"설정 저장 실패: {e}")
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        설정 값 가져오기

        Args:
            key_path: 점(.)으로 구분된 설정 경로
            default: 기본값

        Returns:
            설정 값
        """
        return _get_setting(key_path, default)

    def set(self, key_path: str, value: Any, save_immediately: bool = True) -> bool:
        """
        설정 값 변경

        Args:
            key_path: 점(.)으로 구분된 설정 경로
            value: 새로운 값
            save_immediately: 즉시 파일에 저장 여부

        Returns:
            성공 여부
        """
        try:
            _set_setting(key_path, value, save=save_immediately)
            return True
        except Exception as e:
            logger.error(f"설정 변경 실패: {e}")
            return False

    def update_setting(self, category: str, key: str, value: Any, save_immediately: bool = True) -> bool:
        """
        특정 카테고리의 설정 값 변경

        Args:
            category: 카테고리 이름
            key: 설정 키
            value: 새로운 값
            save_immediately: 즉시 저장 여부

        Returns:
            성공 여부
        """
        key_path = f"{category}.{key}"
        return self.set(key_path, value, save_immediately)

    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """
        특정 카테고리의 설정 값 조회

        Args:
            category: 카테고리 이름
            key: 설정 키
            default: 기본값

        Returns:
            설정 값
        """
        key_path = f"{category}.{key}"
        return self.get(key_path, default)

    def get_category(self, category: str) -> Dict[str, Any]:
        """카테고리별 설정 가져오기"""
        config = _get_config()
        category_obj = getattr(config, category, None)
        if category_obj:
            if hasattr(category_obj, 'model_dump'):
                return category_obj.model_dump()
            else:
                return category_obj
        return {}

    def update_category(self, category: str, settings: Dict[str, Any], save_immediately: bool = True) -> bool:
        """카테고리별 설정 일괄 업데이트"""
        try:
            self._manager.update_category(category, settings, save_immediately)
            return True
        except Exception as e:
            logger.error(f"카테고리 설정 업데이트 실패: {e}")
            return False

    def reset_to_defaults(self, category: Optional[str] = None) -> bool:
        """기본값으로 리셋"""
        try:
            if category:
                logger.warning(f"Category-specific reset not implemented: {category}")
                return False
            else:
                self._manager.reset_to_defaults()
                return True
        except Exception as e:
            logger.error(f"기본값 복원 실패: {e}")
            return False

    def register_change_listener(self, key_path: str, callback: Callable):
        """설정 변경 리스너 등록"""
        _register_listener(key_path, callback)

        if key_path not in self.change_listeners:
            self.change_listeners[key_path] = []
        self.change_listeners[key_path].append(callback)

    def export_to_json(self, file_path: Path) -> bool:
        """JSON 형식으로 내보내기"""
        return _export_json(str(file_path))

    def import_from_json(self, file_path: Path) -> bool:
        """JSON 형식에서 가져오기"""
        return _import_json(str(file_path))


_unified_settings_manager: Optional[UnifiedSettingsManager] = None


def get_unified_settings() -> UnifiedSettingsManager:
    """
    통합 설정 관리자 인스턴스 가져오기 (싱글톤)

    [WARNING]️  DEPRECATED: 새 코드에서는 다음을 사용하세요:
        from config.manager import ConfigManager
        manager = ConfigManager()
    """
    global _unified_settings_manager
    if _unified_settings_manager is None:
        _unified_settings_manager = UnifiedSettingsManager()
    return _unified_settings_manager


__all__ = [
    'UnifiedSettingsManager',
    'get_unified_settings',
]
