AutoTrade Pro v4.0 - 켈리 배팅 자금 관리
Kelly Criterion 기반 최적 포지션 사이징

공식: f* = (bp - q) / b
- f*: 최적 베팅 비율
- b: 승리 시 배당률 (평균 수익 / 평균 손실)
- p: 승률
- q: 패율 (1-p)
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class KellyParameters:
    """켈리 공식 파라미터"""
    win_rate: float
    avg_win: float
    avg_loss: float
    kelly_fraction: float = 0.5


class KellyCriterion:
    """켈리 배팅 자금 관리자"""

    def __init__(self, settings: Dict[str, Any] = None):
        """
        초기화

        Args:
            settings: {'kelly_fraction': 0.5, 'max_position_size': 0.30}
        """
        self.settings = settings or {}
        self.kelly_fraction = self.settings.get('kelly_fraction', 0.5)
        self.max_position_size = self.settings.get('max_position_size', 0.30)

        logger.info(f"켈리 배팅 초기화: fraction={self.kelly_fraction}")

    def calculate_kelly_percentage(self, params: KellyParameters) -> float:
        """
        최적 켈리 비율 계산

        Args:
            params: 켈리 파라미터

        Returns:
            최적 베팅 비율 (0.0 ~ 1.0)
        """
        p = params.win_rate
        q = 1 - p

        if params.avg_loss == 0:
            logger.warning("평균 손실이 0입니다")
            return 0.0

        b = params.avg_win / abs(params.avg_loss)

        kelly_pct = (b * p - q) / b

        kelly_pct *= params.kelly_fraction

        kelly_pct = min(kelly_pct, self.max_position_size)

        kelly_pct = max(kelly_pct, 0.0)

        logger.debug(
            f"켈리 비율 계산: 승률={p:.2f}, b={b:.2f}, "
            f"kelly={kelly_pct:.2%}"
        )

        return kelly_pct

    def calculate_position_size(
        self,
        total_capital: float,
        params: KellyParameters,
        current_price: float
    ) -> int:
        포지션 크기 계산

        Args:
            total_capital: 총 자본
            params: 켈리 파라미터
            current_price: 현재가

        Returns:
            매수 수량
        kelly_pct = self.calculate_kelly_percentage(params)

        investment_amount = total_capital * kelly_pct

        quantity = int(investment_amount / current_price)

        logger.info(
            f"포지션 사이징: 켈리={kelly_pct:.2%}, "
            f"금액={investment_amount:,.0f}원, 수량={quantity}"
        )

        return quantity

    def update_parameters_from_history(
        self,
        trade_history: List[Dict[str, Any]]
    ) -> KellyParameters:
        거래 이력에서 켈리 파라미터 계산

        Args:
            trade_history: 거래 기록
                [{'profit_loss': 10000, 'result': 'win'}, ...]

        Returns:
            계산된 켈리 파라미터
        if not trade_history:
            return KellyParameters(
                win_rate=0.5,
                avg_win=0.0,
                avg_loss=0.0,
                kelly_fraction=self.kelly_fraction
            )

        wins = [t['profit_loss'] for t in trade_history if t['profit_loss'] > 0]
        losses = [t['profit_loss'] for t in trade_history if t['profit_loss'] < 0]

        win_count = len(wins)
        total_count = len(trade_history)

        win_rate = win_count / total_count if total_count > 0 else 0.5

        avg_win = sum(wins) / len(wins) if wins else 0.0
        avg_loss = sum(losses) / len(losses) if losses else 0.0

        params = KellyParameters(
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            kelly_fraction=self.kelly_fraction
        )

        logger.info(
            f"켈리 파라미터 업데이트: 승률={win_rate:.2%}, "
            f"평균승={avg_win:,.0f}, 평균패={avg_loss:,.0f}"
        )

        return params


if __name__ == "__main__":
    kelly = KellyCriterion({'kelly_fraction': 0.5})

    trade_history = [
        {'profit_loss': 100000, 'result': 'win'},
        {'profit_loss': -50000, 'result': 'loss'},
        {'profit_loss': 80000, 'result': 'win'},
        {'profit_loss': -40000, 'result': 'loss'},
        {'profit_loss': 120000, 'result': 'win'},
    ]

    params = kelly.update_parameters_from_history(trade_history)

    total_capital = 10000000
    current_price = 70000

    quantity = kelly.calculate_position_size(total_capital, params, current_price)

    print(f"추천 매수 수량: {quantity}주 ({quantity * current_price:,}원)")
