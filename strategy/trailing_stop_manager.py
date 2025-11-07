"""
AutoTrade Pro v4.0 - 동적 손절/익절 관리자 (Trailing Stop with ATR)
ATR 기반 변동성을 고려한 동적 손절/익절


주요 기능:
- ATR 기반 손절선 동적 조정
- Trailing Stop (수익 증가 시 손절선 상향)
- 종목별 개별 관리
- 실시간 업데이트
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class TrailingStopState:
    """Trailing Stop 상태"""
    stock_code: str
    entry_price: float
    current_price: float
    stop_loss_price: float
    take_profit_price: float
    highest_price: float
    activated: bool
    atr_value: float
    updated_at: datetime


class TrailingStopManager:
    """동적 손절/익절 관리자"""

    def __init__(self, settings: Dict[str, Any] = None):
        """
        초기화

        Args:
            settings: 설정
                {
                    'atr_multiplier': 2.0,           # ATR 승수
                    'activation_pct': 0.03,          # 활성화 수익률 (3%)
                    'min_profit_lock_pct': 0.50,     # 최소 수익 보호 비율 (50%)
                    'update_frequency_seconds': 60    # 업데이트 빈도
                }
        """
        self.settings = settings or {}
        self.atr_multiplier = self.settings.get('atr_multiplier', 2.0)
        self.activation_pct = self.settings.get('activation_pct', 0.03)
        self.min_profit_lock_pct = self.settings.get('min_profit_lock_pct', 0.50)

        self.states: Dict[str, TrailingStopState] = {}

        logger.info(f"Trailing Stop Manager 초기화: ATR x{self.atr_multiplier}")

    def add_position(
        self,
        stock_code: str,
        entry_price: float,
        atr_value: float,
        initial_stop_loss_pct: float = 0.05,
        initial_take_profit_pct: float = 0.10
    ):
        """
        포지션 추가 및 초기 손절/익절 설정

        Args:
            stock_code: 종목 코드
            entry_price: 진입 가격
            atr_value: ATR 값
            initial_stop_loss_pct: 초기 손절 비율
            initial_take_profit_pct: 초기 익절 비율
        atr_based_stop = entry_price - (atr_value * self.atr_multiplier)
        percentage_based_stop = entry_price * (1 - initial_stop_loss_pct)

        stop_loss_price = max(atr_based_stop, percentage_based_stop)

        take_profit_price = entry_price * (1 + initial_take_profit_pct)

        state = TrailingStopState(
            stock_code=stock_code,
            entry_price=entry_price,
            current_price=entry_price,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            highest_price=entry_price,
            activated=False,
            atr_value=atr_value,
            updated_at=datetime.now()
        )

        self.states[stock_code] = state

        logger.info(
            f"[{stock_code}] Trailing Stop 설정: "
            f"진입={entry_price:,}, 손절={stop_loss_price:,}, 익절={take_profit_price:,}"
        )

    def update(self, stock_code: str, current_price: float, atr_value: Optional[float] = None):
        """
        현재가 업데이트 및 Trailing Stop 조정

        Args:
            stock_code: 종목 코드
            current_price: 현재가
            atr_value: 최신 ATR 값 (선택)

        Returns:
            (should_sell, reason)
        """
        if stock_code not in self.states:
            logger.warning(f"[{stock_code}] Trailing Stop 상태 없음")
            return False, None

        state = self.states[stock_code]
        state.current_price = current_price

        if atr_value is not None:
            state.atr_value = atr_value

        if current_price > state.highest_price:
            state.highest_price = current_price

        profit_pct = (current_price - state.entry_price) / state.entry_price

        if not state.activated and profit_pct >= self.activation_pct:
            state.activated = True
            logger.info(
                f"[{stock_code}] Trailing Stop 활성화! "
                f"수익률={profit_pct*100:.2f}%"
            )

        if state.activated:
            new_stop_loss = state.highest_price - (state.atr_value * self.atr_multiplier)

            if new_stop_loss > state.stop_loss_price:
                old_stop_loss = state.stop_loss_price
                state.stop_loss_price = new_stop_loss
                logger.info(
                    f"[{stock_code}] 손절선 상향: "
                    f"{old_stop_loss:,} -> {new_stop_loss:,}"
                )

            min_profit_price = state.entry_price * (
                1 + self.activation_pct * self.min_profit_lock_pct
            )
            state.stop_loss_price = max(state.stop_loss_price, min_profit_price)

        if current_price <= state.stop_loss_price:
            logger.warning(
                f"[{stock_code}] 손절 신호! "
                f"현재가={current_price:,} <= 손절가={state.stop_loss_price:,}"
            )
            return True, "STOP_LOSS"

        if current_price >= state.take_profit_price:
            logger.info(
                f"[{stock_code}] 익절 신호! "
                f"현재가={current_price:,} >= 익절가={state.take_profit_price:,}"
            )
            return True, "TAKE_PROFIT"

        state.updated_at = datetime.now()
        return False, None

    def remove_position(self, stock_code: str):
        """포지션 제거"""
        if stock_code in self.states:
            del self.states[stock_code]
            logger.info(f"[{stock_code}] Trailing Stop 제거")

    def get_state(self, stock_code: str) -> Optional[TrailingStopState]:
        """상태 조회"""
        return self.states.get(stock_code)

    def get_all_states(self) -> Dict[str, TrailingStopState]:
        """모든 상태 조회"""
        return self.states.copy()


if __name__ == "__main__":
    manager = TrailingStopManager()

    manager.add_position("005930", 70000, 1000)

    test_prices = [71000, 72000, 73000, 74000, 73500, 72800]

    for price in test_prices:
        should_sell, reason = manager.update("005930", price)
        if should_sell:
            print(f"매도 신호: {reason}")
            break

        state = manager.get_state("005930")
        print(f"가격={price:,}, 손절={state.stop_loss_price:,}, 활성화={state.activated}")
