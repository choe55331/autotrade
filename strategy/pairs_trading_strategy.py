AutoTrade Pro v4.0 - 페어 트레이딩 전략
상관관계가 높은 두 종목의 스프레드 회귀를 이용한 통계적 차익거래

전략 개요:
- 두 종목의 가격 스프레드 계산
- 스프레드가 평균에서 크게 이탈하면 매매
- 스프레드 회귀 시 포지션 청산
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
from collections import deque

import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PairState:
    """페어 상태"""
    pair_name: str
    stock_a: str
    stock_b: str
    spread_mean: float
    spread_std: float
    current_spread: float
    z_score: float
    position: Optional[str]
    entry_spread: Optional[float]
    entry_time: Optional[datetime]


class PairsTradingStrategy:
    """페어 트레이딩 전략"""

    def __init__(self, settings: Dict[str, Any] = None):
        """
        초기화

        Args:
            settings: 전략 설정
                {
                    'pairs': [['005930', '000660'], ...],  # 페어 목록
                    'lookback_period': 60,                  # 롤백 기간 (일)
                    'entry_threshold': 2.0,                 # 진입 임계값 (표준편차)
                    'exit_threshold': 0.5,                  # 청산 임계값
                    'stop_loss_threshold': 3.0              # 손절 임계값
                }
        """
        self.settings = settings or {}
        self.pairs = self.settings.get('pairs', [])
        self.lookback_period = self.settings.get('lookback_period', 60)
        self.entry_threshold = self.settings.get('entry_threshold', 2.0)
        self.exit_threshold = self.settings.get('exit_threshold', 0.5)
        self.stop_loss_threshold = self.settings.get('stop_loss_threshold', 3.0)

        self.spread_history: Dict[str, deque] = {}

        self.pair_states: Dict[str, PairState] = {}

        for pair in self.pairs:
            pair_name = f"{pair[0]}-{pair[1]}"
            self.spread_history[pair_name] = deque(maxlen=self.lookback_period)
            self.pair_states[pair_name] = PairState(
                pair_name=pair_name,
                stock_a=pair[0],
                stock_b=pair[1],
                spread_mean=0.0,
                spread_std=1.0,
                current_spread=0.0,
                z_score=0.0,
                position=None,
                entry_spread=None,
                entry_time=None
            )

        logger.info(f"페어 트레이딩 전략 초기화: {len(self.pairs)}개 페어")

    def update_spread(
        self,
        stock_a: str,
        stock_b: str,
        price_a: float,
        price_b: float
    ):
        스프레드 업데이트

        Args:
            stock_a: 종목A 코드
            stock_b: 종목B 코드
            price_a: 종목A 가격
            price_b: 종목B 가격
        pair_name = f"{stock_a}-{stock_b}"

        if pair_name not in self.spread_history:
            logger.warning(f"[{pair_name}] 등록되지 않은 페어")
            return

        spread = np.log(price_a / price_b) if price_b > 0 else 0.0

        self.spread_history[pair_name].append(spread)

        if len(self.spread_history[pair_name]) >= 20:
            spreads = list(self.spread_history[pair_name])
            spread_mean = np.mean(spreads)
            spread_std = np.std(spreads)
            z_score = (spread - spread_mean) / spread_std if spread_std > 0 else 0.0

            state = self.pair_states[pair_name]
            state.spread_mean = spread_mean
            state.spread_std = spread_std
            state.current_spread = spread
            state.z_score = z_score

            logger.debug(
                f"[{pair_name}] 스프레드={spread:.4f}, "
                f"평균={spread_mean:.4f}, Z-Score={z_score:.2f}"
            )

    def check_entry_signal(self, pair_name: str) -> Tuple[bool, Optional[str]]:
        """
        진입 신호 체크

        Args:
            pair_name: 페어 이름

        Returns:
            (should_trade, direction)
                direction: 'LONG_A_SHORT_B' or 'LONG_B_SHORT_A'
        """
        if pair_name not in self.pair_states:
            return False, None

        state = self.pair_states[pair_name]

        if state.position is not None:
            return False, None

        if len(self.spread_history[pair_name]) < self.lookback_period:
            return False, None

        if state.z_score > self.entry_threshold:
            logger.info(
                f"[{pair_name}] 페어 매매 신호: LONG B, SHORT A "
                f"(Z-Score={state.z_score:.2f})"
            )
            return True, "LONG_B_SHORT_A"

        elif state.z_score < -self.entry_threshold:
            logger.info(
                f"[{pair_name}] 페어 매매 신호: LONG A, SHORT B "
                f"(Z-Score={state.z_score:.2f})"
            )
            return True, "LONG_A_SHORT_B"

        return False, None

    def enter_position(self, pair_name: str, direction: str):
        """
        포지션 진입

        Args:
            pair_name: 페어 이름
            direction: 'LONG_A_SHORT_B' or 'LONG_B_SHORT_A'
        """
        if pair_name not in self.pair_states:
            return

        state = self.pair_states[pair_name]
        state.position = direction
        state.entry_spread = state.current_spread
        state.entry_time = datetime.now()

        logger.info(
            f"[{pair_name}] 페어 포지션 진입: {direction}, "
            f"진입 스프레드={state.entry_spread:.4f}"
        )

    def check_exit_signal(self, pair_name: str) -> Tuple[bool, Optional[str]]:
        """
        청산 신호 체크

        Args:
            pair_name: 페어 이름

        Returns:
            (should_exit, reason)
        """
        if pair_name not in self.pair_states:
            return False, None

        state = self.pair_states[pair_name]

        if state.position is None:
            return False, None

        if abs(state.z_score) > self.stop_loss_threshold:
            logger.warning(
                f"[{pair_name}] 손절 신호! Z-Score={state.z_score:.2f}"
            )
            return True, "STOP_LOSS"

        if abs(state.z_score) < self.exit_threshold:
            logger.info(
                f"[{pair_name}] 스프레드 회귀 청산! Z-Score={state.z_score:.2f}"
            )
            return True, "MEAN_REVERSION"

        return False, None

    def exit_position(self, pair_name: str):
        """포지션 청산"""
        if pair_name not in self.pair_states:
            return

        state = self.pair_states[pair_name]

        if state.position is None:
            return

        spread_change = state.current_spread - state.entry_spread

        logger.info(
            f"[{pair_name}] 페어 포지션 청산: "
            f"포지션={state.position}, 스프레드 변화={spread_change:.4f}"
        )

        state.position = None
        state.entry_spread = None
        state.entry_time = None

    def get_state(self, pair_name: str) -> Optional[PairState]:
        """페어 상태 조회"""
        return self.pair_states.get(pair_name)

    def get_all_states(self) -> Dict[str, PairState]:
        """모든 페어 상태 조회"""
        return self.pair_states.copy()


if __name__ == "__main__":
    strategy = PairsTradingStrategy({
        'pairs': [['005930', '000660']],
        'entry_threshold': 2.0
    })

    for i in range(100):
        price_a = 70000 + np.random.normal(0, 1000)
        price_b = 120000 + np.random.normal(0, 2000)

        strategy.update_spread('005930', '000660', price_a, price_b)

        should_trade, direction = strategy.check_entry_signal('005930-000660')
        if should_trade:
            print(f"진입 신호: {direction}")
            strategy.enter_position('005930-000660', direction)

        should_exit, reason = strategy.check_exit_signal('005930-000660')
        if should_exit:
            print(f"청산 신호: {reason}")
            strategy.exit_position('005930-000660')
