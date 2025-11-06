"""
Unified Risk Manager v6.0
통합 리스크 관리자 - 5개 Risk Manager 통합
"""

from enum import Enum
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from pathlib import Path


class RiskMode(Enum):
    """리스크 모드"""
    CONSERVATIVE = "conservative"  # 보수적
    MODERATE = "moderate"          # 중립적
    AGGRESSIVE = "aggressive"      # 공격적
    DEFENSIVE = "defensive"        # 방어적


@dataclass
class RiskConfig:
    """리스크 설정"""
    max_position_size_pct: float  # 최대 포지션 크기 (총 자본 대비 %)
    max_open_positions: int       # 최대 동시 포지션 수
    max_single_loss_pct: float    # 단일 종목 최대 손실률 (%)
    max_daily_loss_pct: float     # 일일 최대 손실률 (%)
    stop_loss_pct: float          # 손절 비율 (%)
    take_profit_pct: float        # 익절 비율 (%)
    trailing_stop_pct: float      # 추적 손절 비율 (%)


class UnifiedRiskManager:
    """
    통합 리스크 관리자

    Features:
    - 4가지 리스크 모드 (보수적, 중립적, 공격적, 방어적)
    - 동적 포지션 크기 조정
    - 손익 기반 자동 모드 전환
    - 일일/주간 손실 제한
    - Kelly Criterion 포지션 사이징
    - VaR (Value at Risk) 계산
    """

    # 리스크 모드별 설정
    RISK_CONFIGS = {
        RiskMode.CONSERVATIVE: RiskConfig(
            max_position_size_pct=5.0,
            max_open_positions=3,
            max_single_loss_pct=2.0,
            max_daily_loss_pct=3.0,
            stop_loss_pct=3.0,
            take_profit_pct=8.0,
            trailing_stop_pct=2.0
        ),
        RiskMode.MODERATE: RiskConfig(
            max_position_size_pct=10.0,
            max_open_positions=5,
            max_single_loss_pct=3.0,
            max_daily_loss_pct=5.0,
            stop_loss_pct=5.0,
            take_profit_pct=12.0,
            trailing_stop_pct=3.0
        ),
        RiskMode.AGGRESSIVE: RiskConfig(
            max_position_size_pct=15.0,
            max_open_positions=8,
            max_single_loss_pct=5.0,
            max_daily_loss_pct=8.0,
            stop_loss_pct=7.0,
            take_profit_pct=20.0,
            trailing_stop_pct=5.0
        ),
        RiskMode.DEFENSIVE: RiskConfig(
            max_position_size_pct=3.0,
            max_open_positions=2,
            max_single_loss_pct=1.5,
            max_daily_loss_pct=2.0,
            stop_loss_pct=2.0,
            take_profit_pct=5.0,
            trailing_stop_pct=1.5
        ),
    }

    def __init__(self, initial_capital: int, mode: RiskMode = RiskMode.MODERATE):
        """
        초기화

        Args:
            initial_capital: 초기 자본금
            mode: 리스크 모드
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.current_mode = mode
        self.config = self.RISK_CONFIGS[mode]

        # 손익 추적
        self.daily_profit_loss = 0
        self.weekly_profit_loss = 0
        self.total_profit_loss = 0
        self.daily_reset_time = datetime.now().date()
        self.weekly_reset_time = datetime.now() - timedelta(days=datetime.now().weekday())

        # 포지션 추적
        self.open_positions = []
        self.position_history = []

        # 상태 저장 경로
        self.state_file = Path('data/risk_manager_state.json')

    def update_capital(self, current_capital: int):
        """현재 자본 업데이트"""
        self.current_capital = current_capital
        self.total_profit_loss = current_capital - self.initial_capital
        self._check_auto_mode_switch()

    def calculate_position_size(
        self,
        stock_price: int,
        available_cash: int,
        win_rate: Optional[float] = None,
        risk_reward_ratio: Optional[float] = None
    ) -> int:
        """
        포지션 크기 계산

        Args:
            stock_price: 주가
            available_cash: 사용 가능 현금
            win_rate: 승률 (Kelly Criterion 사용 시)
            risk_reward_ratio: 리스크-보상 비율 (Kelly Criterion 사용 시)

        Returns:
            매수 수량
        """

        # 1. 기본 포지션 크기 (자본 대비 %)
        max_position_value = self.current_capital * (self.config.max_position_size_pct / 100)

        # 2. Kelly Criterion (승률과 손익비가 있을 경우)
        if win_rate is not None and risk_reward_ratio is not None:
            kelly_pct = self._calculate_kelly_criterion(win_rate, risk_reward_ratio)
            # Kelly의 절반만 사용 (안전하게)
            kelly_position_value = self.current_capital * (kelly_pct / 2)
            max_position_value = min(max_position_value, kelly_position_value)

        # 3. 가용 현금 제한
        max_position_value = min(max_position_value, available_cash)

        # 4. 수량 계산
        quantity = int(max_position_value / stock_price)

        # 5. 최대 포지션 수 제한 확인
        if len(self.open_positions) >= self.config.max_open_positions:
            return 0

        # 6. 일일 손실 제한 확인
        if self._check_daily_loss_limit():
            return 0

        return quantity

    def _calculate_kelly_criterion(self, win_rate: float, risk_reward_ratio: float) -> float:
        """
        Kelly Criterion 계산

        f* = (p * b - q) / b
        where:
        - f* = 최적 포지션 크기 (자본의 비율)
        - p = 승률
        - q = 1 - p (패배 확률)
        - b = 손익비 (reward/risk)
        """
        if win_rate <= 0 or win_rate >= 1:
            return 0.0

        p = win_rate
        q = 1 - win_rate
        b = risk_reward_ratio

        kelly = (p * b - q) / b

        # Kelly가 음수면 0 반환 (베팅하지 않음)
        if kelly < 0:
            return 0.0

        # Kelly가 너무 크면 제한 (최대 25%)
        return min(kelly * 100, 25.0)

    def should_open_position(self, current_positions: int) -> bool:
        """포지션 진입 가능 여부"""

        # 1. 최대 포지션 수 확인
        if current_positions >= self.config.max_open_positions:
            return False

        # 2. 일일 손실 제한 확인
        if self._check_daily_loss_limit():
            return False

        # 3. 주간 손실 제한 확인
        if self._check_weekly_loss_limit():
            return False

        return True

    def get_exit_thresholds(self, entry_price: int) -> Dict[str, int]:
        """
        청산 임계값 계산

        Args:
            entry_price: 진입 가격

        Returns:
            {'stop_loss': 손절가, 'take_profit': 익절가, 'trailing_stop': 추적손절}
        """

        stop_loss = int(entry_price * (1 - self.config.stop_loss_pct / 100))
        take_profit = int(entry_price * (1 + self.config.take_profit_pct / 100))
        trailing_stop_pct = self.config.trailing_stop_pct

        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'trailing_stop_pct': trailing_stop_pct
        }

    def calculate_var(self, positions: list, confidence_level: float = 0.95) -> float:
        """
        VaR (Value at Risk) 계산

        Args:
            positions: 포지션 리스트
            confidence_level: 신뢰 수준 (기본 95%)

        Returns:
            VaR 금액 (원)
        """

        if not positions:
            return 0.0

        # 각 포지션의 최대 손실 계산
        losses = []
        for position in positions:
            entry_price = position.get('entry_price', 0)
            quantity = position.get('quantity', 0)
            max_loss = entry_price * quantity * (self.config.stop_loss_pct / 100)
            losses.append(max_loss)

        # 총 VaR (단순 합산, 상관관계 미고려)
        total_var = sum(losses)

        return total_var

    def _check_daily_loss_limit(self) -> bool:
        """일일 손실 제한 확인"""

        # 날짜 변경 확인
        today = datetime.now().date()
        if today > self.daily_reset_time:
            self.daily_profit_loss = 0
            self.daily_reset_time = today

        max_daily_loss = self.current_capital * (self.config.max_daily_loss_pct / 100)

        if self.daily_profit_loss < -max_daily_loss:
            return True  # 제한 초과

        return False

    def _check_weekly_loss_limit(self) -> bool:
        """주간 손실 제한 확인"""

        # 주 변경 확인 (월요일 기준)
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())

        if week_start > self.weekly_reset_time:
            self.weekly_profit_loss = 0
            self.weekly_reset_time = week_start

        max_weekly_loss = self.current_capital * (self.config.max_daily_loss_pct * 3 / 100)

        if self.weekly_profit_loss < -max_weekly_loss:
            return True  # 제한 초과

        return False

    def _check_auto_mode_switch(self):
        """손익 기반 자동 모드 전환"""

        profit_loss_pct = (self.total_profit_loss / self.initial_capital) * 100

        # 큰 손실 (-10% 이상) → DEFENSIVE
        if profit_loss_pct <= -10:
            if self.current_mode != RiskMode.DEFENSIVE:
                self.switch_mode(RiskMode.DEFENSIVE, reason="큰 손실 발생")

        # 손실 (-5% ~ -10%) → CONSERVATIVE
        elif -10 < profit_loss_pct <= -5:
            if self.current_mode not in [RiskMode.DEFENSIVE, RiskMode.CONSERVATIVE]:
                self.switch_mode(RiskMode.CONSERVATIVE, reason="손실 발생")

        # 중립 (-5% ~ +10%) → MODERATE
        elif -5 < profit_loss_pct < 10:
            if self.current_mode != RiskMode.MODERATE:
                self.switch_mode(RiskMode.MODERATE, reason="중립 상태")

        # 수익 (+10% 이상) → AGGRESSIVE
        elif profit_loss_pct >= 10:
            if self.current_mode != RiskMode.AGGRESSIVE:
                self.switch_mode(RiskMode.AGGRESSIVE, reason="높은 수익")

    def switch_mode(self, new_mode: RiskMode, reason: str = ""):
        """리스크 모드 전환"""

        old_mode = self.current_mode
        self.current_mode = new_mode
        self.config = self.RISK_CONFIGS[new_mode]

        print(f"🛡️  리스크 모드 전환: {old_mode.value} → {new_mode.value}")
        if reason:
            print(f"   사유: {reason}")

    def get_mode_description(self) -> str:
        """현재 모드 설명"""

        mode_descriptions = {
            RiskMode.CONSERVATIVE: "보수적 (낮은 리스크)",
            RiskMode.MODERATE: "중립적 (균형)",
            RiskMode.AGGRESSIVE: "공격적 (높은 리스크)",
            RiskMode.DEFENSIVE: "방어적 (최소 리스크)"
        }

        return mode_descriptions.get(self.current_mode, "알 수 없음")

    def get_status_summary(self) -> Dict[str, Any]:
        """상태 요약"""

        return {
            'mode': self.current_mode.value,
            'mode_description': self.get_mode_description(),
            'config': {
                'max_position_size_pct': self.config.max_position_size_pct,
                'max_open_positions': self.config.max_open_positions,
                'stop_loss_pct': self.config.stop_loss_pct,
                'take_profit_pct': self.config.take_profit_pct,
            },
            'capital': {
                'initial': self.initial_capital,
                'current': self.current_capital,
                'profit_loss': self.total_profit_loss,
                'profit_loss_pct': (self.total_profit_loss / self.initial_capital) * 100
            },
            'limits': {
                'daily_pnl': self.daily_profit_loss,
                'daily_limit': self.current_capital * (self.config.max_daily_loss_pct / 100),
                'weekly_pnl': self.weekly_profit_loss
            }
        }

    def record_trade(self, trade: Dict[str, Any]):
        """거래 기록"""

        profit_loss = trade.get('profit_loss', 0)

        self.daily_profit_loss += profit_loss
        self.weekly_profit_loss += profit_loss
        self.total_profit_loss += profit_loss

        self.position_history.append({
            'timestamp': datetime.now().isoformat(),
            'trade': trade
        })

    def save_state(self):
        """상태 저장"""

        state = {
            'current_capital': self.current_capital,
            'current_mode': self.current_mode.value,
            'daily_profit_loss': self.daily_profit_loss,
            'weekly_profit_loss': self.weekly_profit_loss,
            'total_profit_loss': self.total_profit_loss,
            'daily_reset_time': self.daily_reset_time.isoformat(),
            'weekly_reset_time': self.weekly_reset_time.isoformat()
        }

        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def load_state(self):
        """상태 복원"""

        if not self.state_file.exists():
            return

        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)

            self.current_capital = state.get('current_capital', self.initial_capital)
            self.current_mode = RiskMode(state.get('current_mode', 'moderate'))
            self.config = self.RISK_CONFIGS[self.current_mode]
            self.daily_profit_loss = state.get('daily_profit_loss', 0)
            self.weekly_profit_loss = state.get('weekly_profit_loss', 0)
            self.total_profit_loss = state.get('total_profit_loss', 0)

            print("✓ Risk Manager 상태 복원 완료")

        except Exception as e:
            print(f"⚠️ Risk Manager 상태 복원 실패: {e}")


# 싱글톤 인스턴스
_unified_risk_manager_instance = None


def get_unified_risk_manager(initial_capital: Optional[int] = None) -> UnifiedRiskManager:
    """통합 Risk Manager 싱글톤 인스턴스 반환"""
    global _unified_risk_manager_instance

    if _unified_risk_manager_instance is None:
        if initial_capital is None:
            initial_capital = 10_000_000  # 기본값

        _unified_risk_manager_instance = UnifiedRiskManager(initial_capital)
        _unified_risk_manager_instance.load_state()

    return _unified_risk_manager_instance
