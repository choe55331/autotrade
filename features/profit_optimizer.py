"""
features/profit_optimizer.py
수익 최적화 엔진 - 자동 손절/익절, 포지션 사이징, 트레일링 스톱

v5.7.2: 실질적인 수익 증대 및 손실 감소 기능
"""
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import math


@dataclass
class OptimizationRule:
    """최적화 규칙"""
    name: str
    stop_loss_rate: float          # 손절 비율 (예: 0.05 = -5%)
    take_profit_rate: float        # 익절 비율 (예: 0.10 = +10%)
    trailing_stop_enabled: bool    # 트레일링 스톱 사용 여부
    trailing_stop_trigger: float   # 트레일링 스톱 시작 수익률
    trailing_stop_distance: float  # 트레일링 스톱 거리
    max_holding_days: int          # 최대 보유 일수
    partial_profit_enabled: bool   # 부분 익절 사용 여부
    partial_profit_rate: float     # 부분 익절 비율
    partial_profit_sell_ratio: float  # 부분 익절 시 매도 비율


@dataclass
class PositionAnalysis:
    """포지션 분석 결과"""
    should_close: bool
    reason: str
    action: str  # 'full_sell', 'partial_sell', 'hold'
    sell_ratio: float  # 매도 비율 (0.0 ~ 1.0)
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

        # 1. 공격적 규칙 (높은 수익, 빠른 손절)
        self.rules['aggressive'] = OptimizationRule(
            name='공격적',
            stop_loss_rate=0.05,        # -5% 손절
            take_profit_rate=0.15,      # +15% 익절
            trailing_stop_enabled=True,
            trailing_stop_trigger=0.08,  # +8%부터 트레일링 시작
            trailing_stop_distance=0.05, # 최고가 대비 -5%
            max_holding_days=5,
            partial_profit_enabled=True,
            partial_profit_rate=0.10,    # +10%에서 부분 익절
            partial_profit_sell_ratio=0.5  # 50% 매도
        )

        # 2. 보수적 규칙 (안정적 수익, 여유 있는 손절)
        self.rules['conservative'] = OptimizationRule(
            name='보수적',
            stop_loss_rate=0.08,        # -8% 손절
            take_profit_rate=0.12,      # +12% 익절
            trailing_stop_enabled=True,
            trailing_stop_trigger=0.10,  # +10%부터 트레일링 시작
            trailing_stop_distance=0.06, # 최고가 대비 -6%
            max_holding_days=15,
            partial_profit_enabled=False,
            partial_profit_rate=0.0,
            partial_profit_sell_ratio=0.0
        )

        # 3. 균형 규칙 (중도)
        self.rules['balanced'] = OptimizationRule(
            name='균형',
            stop_loss_rate=0.06,        # -6% 손절
            take_profit_rate=0.12,      # +12% 익절
            trailing_stop_enabled=True,
            trailing_stop_trigger=0.08,  # +8%부터 트레일링 시작
            trailing_stop_distance=0.04, # 최고가 대비 -4%
            max_holding_days=10,
            partial_profit_enabled=True,
            partial_profit_rate=0.08,    # +8%에서 부분 익절
            partial_profit_sell_ratio=0.3  # 30% 매도
        )

        # 4. 단타 규칙 (빠른 회전)
        self.rules['daytrading'] = OptimizationRule(
            name='단타',
            stop_loss_rate=0.03,        # -3% 손절
            take_profit_rate=0.05,      # +5% 익절
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
        """
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
        """
        rule = self.rules.get(rule_name, self.rules['balanced'])

        # 손익률 계산
        pnl_rate = (current_price - entry_price) / entry_price
        highest_rate = (highest_price - entry_price) / entry_price

        # 1. 손절 확인
        if pnl_rate <= -rule.stop_loss_rate:
            return PositionAnalysis(
                should_close=True,
                reason=f"손절 {pnl_rate*100:.1f}% (기준: -{rule.stop_loss_rate*100:.0f}%)",
                action='full_sell',
                sell_ratio=1.0
            )

        # 2. 익절 확인
        if pnl_rate >= rule.take_profit_rate:
            return PositionAnalysis(
                should_close=True,
                reason=f"익절 {pnl_rate*100:.1f}% (기준: +{rule.take_profit_rate*100:.0f}%)",
                action='full_sell',
                sell_ratio=1.0
            )

        # 3. 부분 익절 확인
        if rule.partial_profit_enabled and pnl_rate >= rule.partial_profit_rate:
            # 이미 부분 익절했는지 확인 (수량으로 판단)
            # 여기서는 단순 로직으로 처리
            return PositionAnalysis(
                should_close=True,
                reason=f"부분 익절 {pnl_rate*100:.1f}% ({rule.partial_profit_sell_ratio*100:.0f}% 매도)",
                action='partial_sell',
                sell_ratio=rule.partial_profit_sell_ratio
            )

        # 4. 트레일링 스톱 확인
        if rule.trailing_stop_enabled and highest_rate >= rule.trailing_stop_trigger:
            # 트레일링 스톱 가격 계산
            trailing_stop_price = highest_price * (1 - rule.trailing_stop_distance)

            if current_price <= trailing_stop_price:
                return PositionAnalysis(
                    should_close=True,
                    reason=f"트레일링 스톱 (최고 {highest_rate*100:.1f}% → 현재 {pnl_rate*100:.1f}%)",
                    action='full_sell',
                    sell_ratio=1.0
                )

            # 트레일링 스톱 업데이트
            return PositionAnalysis(
                should_close=False,
                reason=f"트레일링 스톱 활성 (손절가: {trailing_stop_price:,.0f}원)",
                action='hold',
                sell_ratio=0.0,
                new_stop_loss=trailing_stop_price
            )

        # 5. 최대 보유 기간 확인
        if days_held >= rule.max_holding_days:
            return PositionAnalysis(
                should_close=True,
                reason=f"최대 보유 기간 {days_held}일 초과 ({pnl_rate*100:.1f}%)",
                action='full_sell',
                sell_ratio=1.0
            )

        # 6. 보유 유지
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
        """
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
        """
        if method == 'kelly':
            # Kelly Criterion: f = (p*b - q) / b
            # f: 투자 비율
            # p: 승률
            # q: 패율 (1-p)
            # b: 평균 수익 / 평균 손실

            if avg_loss == 0 or win_rate == 0:
                # 데이터 부족 시 고정 비율
                kelly_fraction = 0.15
            else:
                b = abs(avg_win / avg_loss)
                kelly_fraction = (win_rate * b - (1 - win_rate)) / b

                # Kelly 비율 제한 (0 ~ 0.25)
                kelly_fraction = max(0.0, min(kelly_fraction, 0.25))

                # 보수적 적용 (Half Kelly)
                kelly_fraction = kelly_fraction * 0.5

        elif method == 'fixed':
            # 고정 비율 (15%)
            kelly_fraction = 0.15

        elif method == 'volatility':
            # 변동성 기반 (구현 필요)
            kelly_fraction = 0.15

        else:
            kelly_fraction = 0.15

        # 투자 금액 계산
        investment_amount = available_cash * kelly_fraction

        # 수량 계산
        quantity = int(investment_amount / stock_price)

        # 최소 1주
        quantity = max(1, quantity)

        # 실제 투자 금액
        actual_investment = quantity * stock_price

        return quantity, actual_investment

    def get_risk_reward_ratio(
        self,
        entry_price: float,
        stop_loss_price: float,
        take_profit_price: float
    ) -> float:
        """
        리스크/리워드 비율 계산

        Args:
            entry_price: 진입 가격
            stop_loss_price: 손절 가격
            take_profit_price: 익절 가격

        Returns:
            리스크/리워드 비율 (높을수록 좋음)
        """
        risk = entry_price - stop_loss_price
        reward = take_profit_price - entry_price

        if risk <= 0:
            return 0.0

        return reward / risk

    def optimize_exit_levels(
        self,
        entry_price: float,
        atr: float,  # Average True Range
        rule_name: str = 'balanced'
    ) -> Dict[str, float]:
        """
        ATR 기반 손절/익절 레벨 최적화

        Args:
            entry_price: 진입 가격
            atr: 평균 실제 범위
            rule_name: 적용할 규칙 이름

        Returns:
            {'stop_loss': 손절가, 'take_profit': 익절가}
        """
        rule = self.rules.get(rule_name, self.rules['balanced'])

        # ATR 기반 손절/익절
        # 일반적으로 손절: 2 ATR, 익절: 3-4 ATR
        stop_loss = entry_price - (atr * 2)
        take_profit = entry_price + (atr * 3)

        # 규칙의 비율과 비교하여 더 보수적인 값 선택
        rule_stop_loss = entry_price * (1 - rule.stop_loss_rate)
        rule_take_profit = entry_price * (1 + rule.take_profit_rate)

        # 최종 값 (더 가까운 것 선택 - 안전)
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


# 전역 인스턴스
_profit_optimizer = None

def get_profit_optimizer() -> ProfitOptimizer:
    """전역 ProfitOptimizer 인스턴스 반환"""
    global _profit_optimizer
    if _profit_optimizer is None:
        _profit_optimizer = ProfitOptimizer()
    return _profit_optimizer
