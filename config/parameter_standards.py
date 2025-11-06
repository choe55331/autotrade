AutoTrade Pro - 파라미터 네이밍 표준
모든 모듈에서 사용하는 표준화된 파라미터 이름과 타입 정의
from typing import Dict, Any, Type
from enum import Enum


class ParameterType(Enum):
    """파라미터 타입"""
    PERCENTAGE = "percentage"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    STRING = "string"


class StandardParameters:
    """
    표준 파라미터 정의

    네이밍 규칙:
    - 비율: *_pct (예: stop_loss_pct = 0.05 는 5%)
    - 크기: *_size (예: position_size = 0.30 는 30%)
    - 한도: *_limit (예: position_limit = 5 는 5개)
    - 임계값: *_threshold (예: entry_threshold = 2.0)
    - 배수: *_multiplier (예: atr_multiplier = 2.0)
    """

    POSITION_PARAMS = {
        'max_position_size': {
            'type': ParameterType.PERCENTAGE,
            'range': (0.0, 1.0),
            'default': 0.30,
            'description': '최대 포지션 크기 (전체 자본 대비 비율)',
            'aliases': ['max_position_ratio', 'position_size_rate']
        },
        'min_position_size': {
            'type': ParameterType.PERCENTAGE,
            'range': (0.0, 1.0),
            'default': 0.01,
            'description': '최소 포지션 크기'
        },

        'position_limit': {
            'type': ParameterType.INTEGER,
            'range': (1, 100),
            'default': 5,
            'description': '최대 보유 종목 수',
            'aliases': ['max_positions', 'max_open_positions']
        },
    }

    RISK_PARAMS = {
        'stop_loss_pct': {
            'type': ParameterType.PERCENTAGE,
            'range': (0.0, 1.0),
            'default': 0.05,
            'description': '손절 비율 (5% 손실 시 손절)',
            'aliases': ['stop_loss_rate', 'stop_loss_ratio']
        },
        'emergency_stop_loss_pct': {
            'type': ParameterType.PERCENTAGE,
            'range': (0.0, 1.0),
            'default': 0.15,
            'description': '긴급 손절 비율 (15%)',
        },

        'take_profit_pct': {
            'type': ParameterType.PERCENTAGE,
            'range': (0.0, 10.0),
            'default': 0.10,
            'description': '익절 비율 (10% 수익 시 익절)',
            'aliases': ['take_profit_rate', 'take_profit_ratio']
        },

        'max_daily_loss_pct': {
            'type': ParameterType.PERCENTAGE,
            'range': (0.0, 1.0),
            'default': 0.03,
            'description': '일일 최대 손실 비율 (3%)',
        },
        'max_total_loss_pct': {
            'type': ParameterType.PERCENTAGE,
            'range': (0.0, 1.0),
            'default': 0.10,
            'description': '총 최대 손실 비율 (10%)',
        },

        'max_consecutive_losses': {
            'type': ParameterType.INTEGER,
            'range': (1, 20),
            'default': 3,
            'description': '최대 연속 손실 횟수',
        },
    }

    TRAILING_STOP_PARAMS = {
        'atr_multiplier': {
            'type': ParameterType.FLOAT,
            'range': (0.5, 10.0),
            'default': 2.0,
            'description': 'ATR 배수 (손절선 계산용)',
        },
        'trailing_activation_pct': {
            'type': ParameterType.PERCENTAGE,
            'range': (0.0, 1.0),
            'default': 0.03,
            'description': '트레일링 스톱 활성화 수익률 (3%)',
            'aliases': ['activation_pct']
        },
        'min_profit_lock_pct': {
            'type': ParameterType.PERCENTAGE,
            'range': (0.0, 1.0),
            'default': 0.50,
            'description': '최소 수익 보호 비율 (수익의 50%)',
        },
    }

    STRATEGY_PARAMS = {
        'entry_threshold': {
            'type': ParameterType.FLOAT,
            'range': (-10.0, 10.0),
            'default': 2.0,
            'description': '진입 임계값 (예: Z-score, 표준편차)',
        },
        'exit_threshold': {
            'type': ParameterType.FLOAT,
            'range': (-10.0, 10.0),
            'default': 0.5,
            'description': '청산 임계값',
        },

        'short_ma_period': {
            'type': ParameterType.INTEGER,
            'range': (1, 100),
            'default': 5,
            'description': '단기 이동평균 기간',
        },
        'long_ma_period': {
            'type': ParameterType.INTEGER,
            'range': (10, 200),
            'default': 20,
            'description': '장기 이동평균 기간',
        },

        'rsi_period': {
            'type': ParameterType.INTEGER,
            'range': (5, 50),
            'default': 14,
            'description': 'RSI 계산 기간',
        },
        'rsi_overbought': {
            'type': ParameterType.FLOAT,
            'range': (50, 100),
            'default': 70,
            'description': 'RSI 과매수 기준',
        },
        'rsi_oversold': {
            'type': ParameterType.FLOAT,
            'range': (0, 50),
            'default': 30,
            'description': 'RSI 과매도 기준',
        },

        'k_value': {
            'type': ParameterType.FLOAT,
            'range': (0.1, 1.0),
            'default': 0.5,
            'description': '변동성 돌파 K값 (Larry Williams)',
        },

        'volume_multiplier': {
            'type': ParameterType.FLOAT,
            'range': (1.0, 10.0),
            'default': 1.5,
            'description': '평균 거래량 대비 배수',
        },

        'lookback_period': {
            'type': ParameterType.INTEGER,
            'range': (10, 252),
            'default': 60,
            'description': '과거 데이터 참조 기간 (일)',
            'aliases': ['lookback_days']
        },
    }

    KELLY_PARAMS = {
        'kelly_fraction': {
            'type': ParameterType.PERCENTAGE,
            'range': (0.0, 1.0),
            'default': 0.5,
            'description': 'Kelly Fraction (0.5 = Half Kelly, 보수적)',
        },
        'win_rate': {
            'type': ParameterType.PERCENTAGE,
            'range': (0.0, 1.0),
            'default': 0.55,
            'description': '승률',
        },
    }

    BACKTEST_PARAMS = {
        'initial_capital': {
            'type': ParameterType.FLOAT,
            'range': (100000, 1000000000),
            'default': 10000000,
            'description': '초기 자본 (원)',
        },
        'commission_pct': {
            'type': ParameterType.PERCENTAGE,
            'range': (0.0, 0.01),
            'default': 0.00015,
            'description': '수수료율 (0.015%)',
        },
        'slippage_pct': {
            'type': ParameterType.PERCENTAGE,
            'range': (0.0, 0.01),
            'default': 0.001,
            'description': '슬리피지 (0.1%)',
        },
    }

    OPTIMIZATION_PARAMS = {
        'n_trials': {
            'type': ParameterType.INTEGER,
            'range': (10, 1000),
            'default': 100,
            'description': '최적화 시행 횟수',
        },
        'n_jobs': {
            'type': ParameterType.INTEGER,
            'range': (1, 32),
            'default': 4,
            'description': '병렬 처리 작업 수',
        },
        'timeout_seconds': {
            'type': ParameterType.INTEGER,
            'range': (60, 86400),
            'default': 3600,
            'description': '최적화 타임아웃 (초)',
        },
    }

    @classmethod
    def get_all_parameters(cls) -> Dict[str, Dict[str, Any]]:
        """모든 표준 파라미터 반환"""
        all_params = {}
        all_params.update(cls.POSITION_PARAMS)
        all_params.update(cls.RISK_PARAMS)
        all_params.update(cls.TRAILING_STOP_PARAMS)
        all_params.update(cls.STRATEGY_PARAMS)
        all_params.update(cls.KELLY_PARAMS)
        all_params.update(cls.BACKTEST_PARAMS)
        all_params.update(cls.OPTIMIZATION_PARAMS)
        return all_params

    @classmethod
    def validate_parameter(cls, param_name: str, value: Any) -> tuple[bool, str]:
        """
        파라미터 검증

        Returns:
            (유효 여부, 에러 메시지)
        """
        all_params = cls.get_all_parameters()

        if param_name not in all_params:
            for std_name, config in all_params.items():
                if 'aliases' in config and param_name in config['aliases']:
                    param_name = std_name
                    break
            else:
                return False, f"알 수 없는 파라미터: {param_name}"

        param_config = all_params[param_name]
        param_type = param_config['type']
        param_range = param_config.get('range')

        if param_type == ParameterType.INTEGER:
            if not isinstance(value, int):
                return False, f"{param_name}는 정수여야 합니다"
        elif param_type == ParameterType.FLOAT or param_type == ParameterType.PERCENTAGE:
            if not isinstance(value, (int, float)):
                return False, f"{param_name}는 숫자여야 합니다"
        elif param_type == ParameterType.BOOLEAN:
            if not isinstance(value, bool):
                return False, f"{param_name}는 불리언이어야 합니다"

        if param_range and isinstance(value, (int, float)):
            min_val, max_val = param_range
            if not (min_val <= value <= max_val):
                return False, f"{param_name}는 {min_val} ~ {max_val} 범위여야 합니다 (현재: {value})"

        return True, ""

    @classmethod
    def get_default_value(cls, param_name: str) -> Any:
        """파라미터 기본값 반환"""
        all_params = cls.get_all_parameters()

        for std_name, config in all_params.items():
            if std_name == param_name or (
                'aliases' in config and param_name in config['aliases']
            ):
                return config['default']

        return None

    @classmethod
    def normalize_parameter_name(cls, param_name: str) -> str:
        """별칭을 표준 이름으로 변환"""
        all_params = cls.get_all_parameters()

        for std_name, config in all_params.items():
            if std_name == param_name:
                return std_name
            if 'aliases' in config and param_name in config['aliases']:
                return std_name

        return param_name

    @classmethod
    def get_parameter_info(cls, param_name: str) -> Dict[str, Any]:
        """파라미터 상세 정보 반환"""
        param_name = cls.normalize_parameter_name(param_name)
        all_params = cls.get_all_parameters()
        return all_params.get(param_name, {})


class ParameterConverter:
    """파라미터 변환 유틸리티"""

    @staticmethod
    def pct_to_rate(pct: float) -> float:
        """퍼센트를 비율로 변환 (예: 0.05 -> 5.0)"""
        return pct * 100

    @staticmethod
    def rate_to_pct(rate: float) -> float:
        """비율을 퍼센트로 변환 (예: 5.0 -> 0.05)"""
        return rate / 100

    @staticmethod
    def normalize_dict_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        딕셔너리의 파라미터 이름을 표준 이름으로 변환

        Args:
            params: 원본 파라미터 딕셔너리

        Returns:
            정규화된 파라미터 딕셔너리
        """
        normalized = {}

        for key, value in params.items():
            std_name = StandardParameters.normalize_parameter_name(key)
            normalized[std_name] = value

        return normalized


LEGACY_PARAMETER_MAPPING = {
    'max_position_ratio': 'max_position_size',
    'position_size_rate': 'max_position_size',
    'max_positions': 'position_limit',
    'max_open_positions': 'position_limit',
    'stop_loss_rate': 'stop_loss_pct',
    'stop_loss_ratio': 'stop_loss_pct',
    'take_profit_rate': 'take_profit_pct',
    'take_profit_ratio': 'take_profit_pct',
    'activation_pct': 'trailing_activation_pct',
    'lookback_days': 'lookback_period',
}


def migrate_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    기존 파라미터를 표준 이름으로 마이그레이션

    Args:
        params: 원본 파라미터 딕셔너리

    Returns:
        마이그레이션된 파라미터 딕셔너리
    """
    migrated = {}

    for key, value in params.items():
        std_name = LEGACY_PARAMETER_MAPPING.get(key, key)
        migrated[std_name] = value

    return migrated
