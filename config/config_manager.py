"""
config/config_manager.py
YAML 기반 설정 관리 시스템
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    """통합 설정 클래스"""

    # 원본 설정 딕셔너리
    _config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """설정 초기화 후 처리"""
        self._validate_config()

    def _validate_config(self):
        """설정 유효성 검증"""
        errors = []

        # 필수 섹션 확인
        required_sections = [
            'system', 'logging', 'api', 'position', 'profit_loss',
            'scanning', 'scoring', 'risk_management', 'ai', 'dashboard'
        ]

        for section in required_sections:
            if section not in self._config:
                errors.append(f"필수 섹션 누락: {section}")

        if errors:
            raise ValueError(f"설정 검증 실패:\n" + "\n".join(errors))

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        점(.) 구분 경로로 설정 값 가져오기

        Args:
            key_path: 설정 경로 (예: 'api.kiwoom.timeout')
            default: 기본값

        Returns:
            설정 값
        """
        keys = key_path.split('.')
        value = self._config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any):
        """
        점(.) 구분 경로로 설정 값 변경

        Args:
            key_path: 설정 경로
            value: 새 값
        """
        keys = key_path.split('.')
        config = self._config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

    @property
    def system(self) -> Dict[str, Any]:
        """시스템 설정"""
        return self.get('system', {})

    @property
    def logging(self) -> Dict[str, Any]:
        """로깅 설정"""
        return self.get('logging', {})

    @property
    def database(self) -> Dict[str, Any]:
        """데이터베이스 설정"""
        return self.get('database', {})

    @property
    def api(self) -> Dict[str, Any]:
        """API 설정"""
        return self.get('api', {})

    @property
    def position(self) -> Dict[str, Any]:
        """포지션 관리 설정"""
        return self.get('position', {})

    @property
    def profit_loss(self) -> Dict[str, Any]:
        """손익 관리 설정"""
        return self.get('profit_loss', {})

    @property
    def scanning(self) -> Dict[str, Any]:
        """스캐닝 설정"""
        return self.get('scanning', {})

    @property
    def scoring(self) -> Dict[str, Any]:
        """스코어링 설정"""
        return self.get('scoring', {})

    @property
    def risk_management(self) -> Dict[str, Any]:
        """리스크 관리 설정"""
        return self.get('risk_management', {})

    @property
    def ai(self) -> Dict[str, Any]:
        """AI 설정"""
        return self.get('ai', {})

    @property
    def dashboard(self) -> Dict[str, Any]:
        """대시보드 설정"""
        return self.get('dashboard', {})

    @property
    def notification(self) -> Dict[str, Any]:
        """알림 설정"""
        return self.get('notification', {})

    @property
    def backtesting(self) -> Dict[str, Any]:
        """백테스팅 설정"""
        return self.get('backtesting', {})

    @property
    def main_cycle(self) -> Dict[str, Any]:
        """메인 사이클 설정"""
        return self.get('main_cycle', {})

    @property
    def development(self) -> Dict[str, Any]:
        """개발 설정"""
        return self.get('development', {})

    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 반환"""
        return self._config.copy()

    def get_trading_params_summary(self) -> str:
        """매매 파라미터 요약"""
        pos = self.position
        pl = self.profit_loss
        scan = self.scanning
        ai = self.ai

        return f"""
        === 매매 파라미터 ===
        최대 포지션: {pos.get('max_open_positions', 5)}개
        거래당 리스크: {pos.get('risk_per_trade_ratio', 0.20)*100:.1f}%
        목표 수익률: {pl.get('take_profit_ratio', 0.10)*100:.1f}%
        손절 비율: {pl.get('stop_loss_ratio', -0.05)*100:.1f}%

        스캐닝:
        - Fast Scan: {scan.get('fast_scan', {}).get('max_candidates', 50)}종목
        - Deep Scan: {scan.get('deep_scan', {}).get('max_candidates', 20)}종목
        - AI Scan: {scan.get('ai_scan', {}).get('max_candidates', 5)}종목

        AI 분석: {'활성' if ai.get('enabled', True) else '비활성'}
        - 최소 점수: {scan.get('ai_scan', {}).get('min_analysis_score', 7.0):.1f}점
        - 신뢰도: {scan.get('ai_scan', {}).get('min_confidence', 'Medium')}
        """


class ConfigManager:
    """설정 관리자 (싱글톤)"""

    _instance: Optional['ConfigManager'] = None
    _config: Optional[Config] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """초기화"""
        if self._config is None:
            self.load_config()

    def load_config(self, config_path: Optional[Path] = None):
        """
        YAML 설정 파일 로드

        Args:
            config_path: 설정 파일 경로 (None이면 기본 경로 사용)
        """
        if config_path is None:
            base_dir = Path(__file__).resolve().parent.parent
            config_path = base_dir / 'config' / 'config.yaml'

        if not config_path.exists():
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")

        # YAML 파일 읽기
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)

        # 환경 변수 치환
        config_dict = self._substitute_env_vars(config_dict)

        # Config 객체 생성
        self._config = Config(_config=config_dict)

    def _substitute_env_vars(self, config: Any) -> Any:
        """
        설정에서 환경 변수 치환 (${VAR_NAME} 형식)

        Args:
            config: 설정 딕셔너리 또는 값

        Returns:
            환경 변수가 치환된 설정
        """
        if isinstance(config, dict):
            return {k: self._substitute_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith('${') and config.endswith('}'):
            var_name = config[2:-1]
            return os.getenv(var_name, config)
        else:
            return config

    def get_config(self) -> Config:
        """설정 객체 반환"""
        if self._config is None:
            self.load_config()
        return self._config

    def reload_config(self, config_path: Optional[Path] = None):
        """설정 재로드"""
        self._config = None
        self.load_config(config_path)

    def save_config(self, config_path: Optional[Path] = None):
        """
        현재 설정을 YAML 파일로 저장

        Args:
            config_path: 저장할 경로 (None이면 기본 경로 사용)
        """
        if config_path is None:
            base_dir = Path(__file__).resolve().parent.parent
            config_path = base_dir / 'config' / 'config.yaml'

        config_dict = self._config.to_dict()

        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


# 싱글톤 인스턴스
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


# 기존 호환성을 위한 함수들
def get_trading_params() -> Dict[str, Any]:
    """매매 파라미터 반환 (기존 호환)"""
    config = get_config()
    return {
        'MAX_OPEN_POSITIONS': config.position.get('max_open_positions', 5),
        'RISK_PER_TRADE_RATIO': config.position.get('risk_per_trade_ratio', 0.20),
        'TAKE_PROFIT_RATIO': config.profit_loss.get('take_profit_ratio', 0.10),
        'STOP_LOSS_RATIO': config.profit_loss.get('stop_loss_ratio', -0.05),
        'TRAILING_STOP_ENABLED': config.profit_loss.get('trailing_stop_enabled', False),
        'TRAILING_STOP_RATIO': config.profit_loss.get('trailing_stop_ratio', 0.03),
    }


def validate_trading_params() -> tuple[bool, list[str]]:
    """매매 파라미터 검증 (기존 호환)"""
    errors = []
    config = get_config()

    # 포지션 관리 검증
    max_pos = config.position.get('max_open_positions', 5)
    if not (1 <= max_pos <= 50):
        errors.append("max_open_positions는 1~50 사이여야 합니다")

    risk_ratio = config.position.get('risk_per_trade_ratio', 0.20)
    if not (0 < risk_ratio <= 1.0):
        errors.append("risk_per_trade_ratio는 0~1 사이여야 합니다")

    # 손익 관리 검증
    stop_loss = config.profit_loss.get('stop_loss_ratio', -0.05)
    if not (-1.0 <= stop_loss < 0):
        errors.append("stop_loss_ratio는 -1~0 사이여야 합니다")

    take_profit = config.profit_loss.get('take_profit_ratio', 0.10)
    if not (0 < take_profit <= 1.0):
        errors.append("take_profit_ratio는 0~1 사이여야 합니다")

    return len(errors) == 0, errors


__all__ = [
    'Config',
    'ConfigManager',
    'get_config',
    'reload_config',
    'save_config',
    'get_trading_params',
    'validate_trading_params',
]
