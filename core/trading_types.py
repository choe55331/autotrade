AutoTrade Pro - Core Type Definitions
표준 데이터 타입 정의 (v4.2 CRITICAL

CRITICAL 개선:
- 4개의 Position 클래스 통합 → 단일 표준 Position
- 모든 모듈에서 이 타입 사용
- Type safety 향상
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class OrderAction(Enum):
    """주문 액션"""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """주문 타입"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"


class PositionStatus(Enum):
    """포지션 상태"""
    OPEN = "open"
    CLOSED = "closed"
    PARTIAL = "partial"


@dataclass
class Position:
    """
    표준 Position 클래스 (CANONICAL)

    모든 모듈에서 이 클래스를 사용:
    - strategy/position_manager.py ✓
    - database/models.py (ORM 변환 함수 제공)
    - ai/backtesting.py (이 클래스로 대체)
    - features/paper_trading.py (이 클래스로 대체)

    특징:
    - 완전한 손익 추적
    - Stop-loss/Take-profit 지원
    - 메타데이터 확장 가능
    - 직렬화/역직렬화 지원
    """
    stock_code: str
    quantity: int
    purchase_price: float

    stock_name: str = ""
    current_price: float = 0.0
    evaluation_amount: float = 0.0
    profit_loss: float = 0.0
    profit_loss_rate: float = 0.0

    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None

    status: PositionStatus = PositionStatus.OPEN
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def avg_price(self) -> float:
        """별칭: purchase_price (백테스팅 호환성)"""
        return self.purchase_price

    @avg_price.setter
    def avg_price(self, value: float):
        """별칭: purchase_price setter"""
        self.purchase_price = value

    @property
    def unrealized_pnl(self) -> float:
        """별칭: profit_loss (백테스팅 호환성)"""
        return self.profit_loss

    @property
    def unrealized_pnl_pct(self) -> float:
        """별칭: profit_loss_rate (백테스팅 호환성)"""
        return self.profit_loss_rate

    def update_current_price(self, price: float):
        """
        현재가 업데이트 및 손익 자동 계산

        Args:
            price: 현재 가격
        """
        self.current_price = price
        self.evaluation_amount = self.quantity * price
        self.profit_loss = self.evaluation_amount - (self.quantity * self.purchase_price)
        self.profit_loss_rate = (
            (self.profit_loss / (self.quantity * self.purchase_price)) * 100
            if self.purchase_price > 0 else 0.0
        )

    def check_stop_loss(self) -> bool:
        """손절가 도달 여부 확인"""
        if self.stop_loss_price and self.current_price > 0:
            return self.current_price <= self.stop_loss_price
        return False

    def check_take_profit(self) -> bool:
        """익절가 도달 여부 확인"""
        if self.take_profit_price and self.current_price > 0:
            return self.current_price >= self.take_profit_price
        return False

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환 (직렬화)"""
        data = asdict(self)
        if isinstance(self.status, PositionStatus):
            data['status'] = self.status.value
        if self.entry_time:
            data['entry_time'] = self.entry_time.isoformat()
        if self.exit_time:
            data['exit_time'] = self.exit_time.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Position':
        """딕셔너리에서 생성 (역직렬화)"""
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = PositionStatus(data['status'])
        if 'entry_time' in data and isinstance(data['entry_time'], str):
            data['entry_time'] = datetime.fromisoformat(data['entry_time'])
        if 'exit_time' in data and isinstance(data['exit_time'], str):
            data['exit_time'] = datetime.fromisoformat(data['exit_time'])
        return cls(**data)

    def __repr__(self) -> str:
        """문자열 표현"""
        return (
            f"Position(code={self.stock_code}, qty={self.quantity}, "
            f"price={self.purchase_price:,.0f}, "
            f"P&L={self.profit_loss:+,.0f}원 ({self.profit_loss_rate:+.2f}%))"
        )


@dataclass
class Trade:
    """
    거래 기록 (체결 내역)

    Position은 현재 보유 상태를 나타내고,
    Trade는 과거 체결 내역을 기록합니다.
    """
    stock_code: str
    stock_name: str
    action: OrderAction
    quantity: int
    price: float
    timestamp: datetime
    commission: float = 0.0
    tax: float = 0.0
    reason: str = ""
    strategy: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_amount(self) -> float:
        """총 금액 (수수료 + 세금 포함)"""
        base = self.quantity * self.price
        if self.action == OrderAction.BUY:
            return base + self.commission
        else:
            return base - self.commission - self.tax

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        if isinstance(self.action, OrderAction):
            data['action'] = self.action.value
        if self.timestamp:
            data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class MarketSnapshot:
    """
    시장 스냅샷 (특정 시점의 시장 데이터)

    백테스팅, 리플레이, 실시간 분석 등에 사용
    """
    timestamp: datetime
    stock_code: str
    price: float
    volume: int = 0
    bid_prices: list = field(default_factory=list)
    ask_prices: list = field(default_factory=list)
    bid_volumes: list = field(default_factory=list)
    ask_volumes: list = field(default_factory=list)
    market_cap: Optional[float] = None
    indicators: Dict[str, float] = field(default_factory=dict)


__all__ = [
    'OrderAction',
    'OrderType',
    'PositionStatus',
    'Position',
    'Trade',
    'MarketSnapshot',
]
