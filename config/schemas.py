"""
AutoTrade Pro - Unified Configuration Schema
Pydantic 기반 통합 설정 스키마 (v4.2 CRITICAL #3)

CRITICAL 개선:
- 5개 설정 시스템 통합 → 단일 Pydantic 스키마
- Type-safe configuration with validation
- Dot notation access: config.get('risk_management.max_position_size')
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml


class RiskManagementConfig(BaseModel):
    """리스크 관리 설정"""
    max_position_size: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="최대 포지션 비중 (총 자산 대비)"
    )
    stop_loss_pct: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="손절 비율"
    )
    take_profit_pct: float = Field(
        default=0.10,
        ge=0.0,
        le=2.0,
        description="익절 비율"
    )
    position_limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="최대 동시 포지션 수"
    )
    daily_loss_limit: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="일일 손실 한도 (총 자산 대비)"
    )
    trailing_stop_pct: float = Field(
        default=0.02,
        ge=0.0,
        le=0.5,
        description="트레일링 스톱 비율"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "max_position_size": 0.3,
                "stop_loss_pct": 0.05,
                "take_profit_pct": 0.10,
                "position_limit": 10,
                "daily_loss_limit": 0.05,
                "trailing_stop_pct": 0.02
            }
        }


class TradingConfig(BaseModel):
    """트레이딩 설정"""
    min_price: int = Field(default=1000, ge=0, description="최소 주문 가격")
    max_price: int = Field(default=1000000, ge=0, description="최대 주문 가격")
    min_volume: int = Field(default=10000, ge=0, description="최소 거래량")
    commission_rate: float = Field(default=0.00015, ge=0.0, description="수수료율")
    slippage_pct: float = Field(default=0.0005, ge=0.0, description="슬리피지 비율")
    market_start_time: str = Field(default="09:00", description="장 시작 시간")
    market_end_time: str = Field(default="15:30", description="장 종료 시간")


class AIConfig(BaseModel):
    """AI 설정"""
    enabled: bool = Field(default=True, description="AI 기능 활성화")
    confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="AI 신뢰도 임계값"
    )
    models: List[str] = Field(
        default=["gemini", "ensemble"],
        description="사용할 AI 모델 목록"
    )
    analysis_interval: int = Field(default=300, ge=0, description="분석 주기 (초)")


class LoggingConfig(BaseModel):
    """로깅 설정"""
    level: str = Field(default="INFO", description="로그 레벨")
    file_path: str = Field(default="logs/bot.log", description="로그 파일 경로")
    max_file_size: int = Field(default=10485760, description="최대 파일 크기 (bytes)")
    backup_count: int = Field(default=30, description="백업 파일 수")
    console_output: bool = Field(default=True, description="콘솔 출력 여부")
    colored_output: bool = Field(default=True, description="컬러 출력 여부")


class NotificationConfig(BaseModel):
    """알림 설정"""
    enabled: bool = Field(default=True, description="알림 활성화")
    telegram_enabled: bool = Field(default=False, description="텔레그램 알림")
    telegram_bot_token: Optional[str] = Field(default=None, description="텔레그램 봇 토큰")
    telegram_chat_id: Optional[str] = Field(default=None, description="텔레그램 채팅 ID")
    email_enabled: bool = Field(default=False, description="이메일 알림")
    email_to: Optional[str] = Field(default=None, description="수신 이메일")


class AutoTradeConfig(BaseModel):
    """통합 설정 (루트)"""
    # 하위 설정 그룹
    risk_management: RiskManagementConfig = Field(default_factory=RiskManagementConfig)
    trading: TradingConfig = Field(default_factory=TradingConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    notification: NotificationConfig = Field(default_factory=NotificationConfig)

    # 전역 설정
    environment: str = Field(default="production", description="환경 (production/development/test)")
    debug_mode: bool = Field(default=False, description="디버그 모드")
    initial_capital: float = Field(default=10000000, ge=0, description="초기 자본")

    @classmethod
    def from_yaml(cls, path: str) -> 'AutoTradeConfig':
        """YAML 파일에서 설정 로드"""
        yaml_path = Path(path)
        if not yaml_path.exists():
            # 기본 설정 반환
            return cls()

        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return cls(**data)

    def save_yaml(self, path: str):
        """설정을 YAML 파일로 저장"""
        yaml_path = Path(path)
        yaml_path.parent.mkdir(parents=True, exist_ok=True)

        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                self.model_dump(),
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )

    def get(self, path: str, default=None):
        """
        Dot notation으로 설정 값 가져오기

        Example:
            config.get('risk_management.max_position_size')
            config.get('ai.confidence_threshold', 0.5)
        """
        keys = path.split('.')
        value = self

        for key in keys:
            if hasattr(value, key):
                value = getattr(value, key)
            else:
                return default

        return value

    def set(self, path: str, value: Any):
        """
        Dot notation으로 설정 값 변경

        Example:
            config.set('risk_management.max_position_size', 0.25)
        """
        keys = path.split('.')
        obj = self

        # Navigate to the parent object
        for key in keys[:-1]:
            if hasattr(obj, key):
                obj = getattr(obj, key)
            else:
                raise KeyError(f"Invalid config path: {path}")

        # Set the final key
        if hasattr(obj, keys[-1]):
            setattr(obj, keys[-1], value)
        else:
            raise KeyError(f"Invalid config key: {keys[-1]}")

    class Config:
        json_schema_extra = {
            "title": "AutoTrade Pro Configuration",
            "description": "Unified configuration schema for AutoTrade Pro v4.2"
        }


# Export
__all__ = [
    'AutoTradeConfig',
    'RiskManagementConfig',
    'TradingConfig',
    'AIConfig',
    'LoggingConfig',
    'NotificationConfig',
]
