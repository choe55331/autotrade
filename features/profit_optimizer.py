features/profit_optimizer.py
수익 최적화 엔진 - 자동 손절/익절, 포지션 사이징, 트레일링 스톱

v5.7.2: 실질적인 수익 증대 및 손실 감소 기능
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import math


@dataclass
class OptimizationRule:
    """최적화 규칙"""
    name: str
    stop_loss_rate: float
    take_profit_rate: float
    trailing_stop_enabled: bool
    trailing_stop_trigger: float
    trailing_stop_distance: float
    max_holding_days: int
    partial_profit_enabled: bool
    partial_profit_rate: float
    partial_profit_sell_ratio: float


@dataclass
class PositionAnalysis:
    """포지션 분석 결과"""
    should_close: bool
    reason: str
    action: str
    sell_ratio: float
    new_stop_loss: Optional[float] = None


class ProfitOptimizer:
    """
    수익 최적화 엔진

    기능:
    1. 자동 손절 (Stop Loss)
    2. 자동 익절 (Take Profit)
    3. 트레일링 스톱 (Trailing Stop)
    4. 부분 익절 (Partial Profit Taking)
    5. 동적 포지션 사이징 (Kelly Criterion)
    """

    def __init__(self):
        self.rules: Dict[str, OptimizationRule] = {}
        self._create_default_rules()

    def _create_default_rules(self):
        """기본 최적화 규칙 생성"""

        self.rules['aggressive'] = OptimizationRule(
            name='공격적',
            stop_loss_rate=0.05,
            take_profit_rate=0.15,
            trailing_stop_enabled=True,
            trailing_stop_trigger=0.08,
            trailing_stop_distance=0.05,
            max_holding_days=5,
            partial_profit_enabled=True,
            partial_profit_rate=0.10,
            partial_profit_sell_ratio=0.5
        )

        self.rules['conservative'] = OptimizationRule(
            name='보수적',
            stop_loss_rate=0.08,
            take_profit_rate=0.12,
            trailing_stop_enabled=True,
            trailing_stop_trigger=0.10,
            trailing_stop_distance=0.06,
            max_holding_days=15,
            partial_profit_enabled=False,
            partial_profit_rate=0.0,
            partial_profit_sell_ratio=0.0
        )

        self.rules['balanced'] = OptimizationRule(
            name='균형',
            stop_loss_rate=0.06,
            take_profit_rate=0.12,
            trailing_stop_enabled=True,
            trailing_stop_trigger=0.08,
            trailing_stop_distance=0.04,
            max_holding_days=10,
            partial_profit_enabled=True,
            partial_profit_rate=0.08,
            partial_profit_sell_ratio=0.3
        )

        self.rules['daytrading'] = OptimizationRule(
            name='단타',
            stop_loss_rate=0.03,
            take_profit_rate=0.05,
            trailing_stop_enabled=False,
            trailing_stop_trigger=0.0,
            trailing_stop_distance=0.0,
            max_holding_days=1,
            partial_profit_enabled=False,
            partial_profit_rate=0.0,
            partial_profit_sell_ratio=0.0
        )

    def analyze_position(
        self,
        entry_price: float,
        current_price: float,
        highest_price: float,
        quantity: int,
        days_held: int,
        rule_name: str = 'balanced',
        current_stop_loss: Optional[float] = None
    ) -> PositionAnalysis:
        포지션 분석 및 최적화 액션 결정

        Args:
            entry_price: 진입 가격
            current_price: 현재 가격
            highest_price: 보유 기간 중 최고가
            quantity: 보유 수량
            days_held: 보유 일수
            rule_name: 적용할 규칙 이름
            current_stop_loss: 현재 손절가 (트레일링 스톱용)

        Returns:
            PositionAnalysis: 분석 결과 및 권장 액션
        rule = self.rules.get(rule_name, self.rules['balanced'])

        pnl_rate = (current_price - entry_price) / entry_price
        highest_rate = (highest_price - entry_price) / entry_price

        if pnl_rate <= -rule.stop_loss_rate:
            return PositionAnalysis(
                should_close=True,
                reason=f"손절 {pnl_rate*100:.1f}% (기준: -{rule.stop_loss_rate*100:.0f}%)",
                action='full_sell',
                sell_ratio=1.0
            )

        if pnl_rate >= rule.take_profit_rate:
            return PositionAnalysis(
                should_close=True,
                reason=f"익절 {pnl_rate*100:.1f}% (기준: +{rule.take_profit_rate*100:.0f}%)",
                action='full_sell',
                sell_ratio=1.0
            )

        if rule.partial_profit_enabled and pnl_rate >= rule.partial_profit_rate:
            return PositionAnalysis(
                should_close=True,
                reason=f"부분 익절 {pnl_rate*100:.1f}% ({rule.partial_profit_sell_ratio*100:.0f}% 매도)",
                action='partial_sell',
                sell_ratio=rule.partial_profit_sell_ratio
            )

        if rule.trailing_stop_enabled and highest_rate >= rule.trailing_stop_trigger:
            trailing_stop_price = highest_price * (1 - rule.trailing_stop_distance)

            if current_price <= trailing_stop_price:
                return PositionAnalysis(
                    should_close=True,
                    reason=f"트레일링 스톱 (최고 {highest_rate*100:.1f}% → 현재 {pnl_rate*100:.1f}%)",
                    action='full_sell',
                    sell_ratio=1.0
                )

            return PositionAnalysis(
                should_close=False,
                reason=f"트레일링 스톱 활성 (손절가: {trailing_stop_price:,.0f}원)",
                action='hold',
                sell_ratio=0.0,
                new_stop_loss=trailing_stop_price
            )

        if days_held >= rule.max_holding_days:
            return PositionAnalysis(
                should_close=True,
                reason=f"최대 보유 기간 {days_held}일 초과 ({pnl_rate*100:.1f}%)",
                action='full_sell',
                sell_ratio=1.0
            )

        return PositionAnalysis(
            should_close=False,
            reason=f"보유 유지 ({pnl_rate*100:.1f}%)",
            action='hold',
            sell_ratio=0.0
        )

    def calculate_position_size(
        self,
        available_cash: float,
        stock_price: float,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        method: str = 'kelly'
    ) -> Tuple[int, float]:
        최적 포지션 크기 계산

        Args:
            available_cash: 사용 가능 현금
            stock_price: 주가
            win_rate: 승률 (0.0 ~ 1.0)
            avg_win: 평균 수익률
            avg_loss: 평균 손실률
            method: 계산 방법 ('kelly', 'fixed', 'volatility')

        Returns:
            (수량, 투자금액)
        if method == 'kelly':

            if avg_loss == 0 or win_rate == 0:
                kelly_fraction = 0.15
            else:
                b = abs(avg_win / avg_loss)
                kelly_fraction = (win_rate * b - (1 - win_rate)) / b

                kelly_fraction = max(0.0, min(kelly_fraction, 0.25))

                kelly_fraction = kelly_fraction * 0.5

        elif method == 'fixed':
            kelly_fraction = 0.15

        elif method == 'volatility':
            kelly_fraction = 0.15

        else:
            kelly_fraction = 0.15

        investment_amount = available_cash * kelly_fraction

        quantity = int(investment_amount / stock_price)

        quantity = max(1, quantity)

        actual_investment = quantity * stock_price

        return quantity, actual_investment

    def get_risk_reward_ratio(
        self,
        entry_price: float,
        stop_loss_price: float,
        take_profit_price: float
    ) -> float:
        리스크/리워드 비율 계산

        Args:
            entry_price: 진입 가격
            stop_loss_price: 손절 가격
            take_profit_price: 익절 가격

        Returns:
            리스크/리워드 비율 (높을수록 좋음)
        risk = entry_price - stop_loss_price
        reward = take_profit_price - entry_price

        if risk <= 0:
            return 0.0

        return reward / risk

    def optimize_exit_levels(
        self,
        entry_price: float,
        atr: float,
        rule_name: str = 'balanced'
    ) -> Dict[str, float]:
        ATR 기반 손절/익절 레벨 최적화

        Args:
            entry_price: 진입 가격
            atr: 평균 실제 범위
            rule_name: 적용할 규칙 이름

        Returns:
            {'stop_loss': 손절가, 'take_profit': 익절가}
        rule = self.rules.get(rule_name, self.rules['balanced'])

        stop_loss = entry_price - (atr * 2)
        take_profit = entry_price + (atr * 3)

        rule_stop_loss = entry_price * (1 - rule.stop_loss_rate)
        rule_take_profit = entry_price * (1 + rule.take_profit_rate)

        final_stop_loss = max(stop_loss, rule_stop_loss)
        final_take_profit = min(take_profit, rule_take_profit)

        return {
            'stop_loss': final_stop_loss,
            'take_profit': final_take_profit,
            'risk_reward_ratio': self.get_risk_reward_ratio(
                entry_price, final_stop_loss, final_take_profit
            )
        }

    def get_rule(self, rule_name: str) -> OptimizationRule:
        """규칙 가져오기"""
        return self.rules.get(rule_name, self.rules['balanced'])

    def add_rule(self, rule: OptimizationRule):
        """규칙 추가"""
        self.rules[rule.name] = rule


_profit_optimizer = None

def get_profit_optimizer() -> ProfitOptimizer:
    """전역 ProfitOptimizer 인스턴스 반환"""
    global _profit_optimizer
    if _profit_optimizer is None:
        _profit_optimizer = ProfitOptimizer()
    return _profit_optimizer
