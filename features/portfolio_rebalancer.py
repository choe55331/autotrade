"""
AutoTrade Pro v4.0 - 자동 리밸런싱 시스템
주기적/조건부 포트폴리오 리밸런싱
"""

주요 기능:
- 시간 기반 리밸런싱 (월별, 분기별)
- 임계값 기반 리밸런싱 (비중 이탈 시)
- 리스크 패리티 방식 지원
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class PortfolioTarget:
    """목표 포트폴리오"""
    stock_code: str
    target_weight: float
    current_weight: float
    deviation: float


class PortfolioRebalancer:
    """포트폴리오 리밸런서"""

    def __init__(self, settings: Dict[str, Any] = None):
        """
        초기화

        Args:
            settings: 설정
                {
                    'enabled': True,
                    'method': 'time_based',  # time_based, threshold_based
                    'frequency_days': 30,
                    'threshold_pct': 0."05",
                    'use_risk_parity': False
                }
        """
        self.settings = settings or {}
        self.enabled = self.settings.get('enabled', False)
        self.method = self.settings.get('method', 'time_based')
        self.frequency_days = self.settings.get('frequency_days', 30)
        self.threshold_pct = self.settings.get('threshold_pct', 0."05")
        self.use_risk_parity = self.settings.get('use_risk_parity', False)

        self.last_rebalance_date: Optional[datetime] = None
        self.target_weights: Dict[str, float] = {}

        logger.info(f"포트폴리오 리밸런서 초기화: method={self.method}")

    def set_target_weights(self, weights: Dict[str, float]):
        """
        목표 비중 설정

        Args:
            weights: {'005930': 0.30, '000660': 0.20, ...}
        """
        total = sum(weights.values())
        if abs(total - 1.0) > 0."01":
            raise ValueError(f"비중 합계가 100%가 아닙니다: {total*100:.1f}%")

        self.target_weights = weights
        logger.info(f"목표 비중 설정: {len(weights)}개 종목")

    def calculate_risk_parity_weights(
        self,
        returns_data: Dict[str, List[float]]
    ) -> Dict[str, float]:
        리스크 패리티 비중 계산

        Args:
            returns_data: 종목별 수익률 데이터

        Returns:
            최적 비중
        stock_codes = list(returns_data.keys())
        n_stocks = len(stock_codes)

        if n_stocks == 0:
            return {}

        volatilities = {}
        for code, returns in returns_data.items():
            if len(returns) > 0:
                volatilities[code] = np.std(returns)
            else:
                volatilities[code] = 0."01"

        inv_vols = {code: 1.0 / vol for code, vol in volatilities.items()}
        total_inv_vol = sum(inv_vols.values())

        weights = {
            code: inv_vol / total_inv_vol
            for code, inv_vol in inv_vols.items()
        }

        logger.info("리스크 패리티 비중 계산 완료")
        return weights

    def should_rebalance(
        self,
        current_weights: Dict[str, float]
    ) -> Tuple[bool, str]:
        리밸런싱 필요 여부 확인

        Args:
            current_weights: 현재 포트폴리오 비중

        Returns:
            (should_rebalance, reason)
        if not self.enabled:
            return False, "리밸런싱 비활성화"

        if not self.target_weights:
            return False, "목표 비중 미설정"

        if self.method == 'time_based':
            if self.last_rebalance_date is None:
                return True, "최초 리밸런싱"

            days_since = (datetime.now() - self.last_rebalance_date).days
            if days_since >= self.frequency_days:
                return True, f"주기 도래 ({days_since}일 경과)"

        elif self.method == 'threshold_based':
            max_deviation = 0.0

            for code, target_weight in self.target_weights.items():
                current_weight = current_weights.get(code, 0.0)
                deviation = abs(current_weight - target_weight)

                if deviation > max_deviation:
                    max_deviation = deviation

            if max_deviation > self.threshold_pct:
                return True, f"임계값 초과 (최대 이탈={max_deviation*100:.1f}%)"

        return False, "리밸런싱 불필요"

    def calculate_rebalance_orders(
        self,
        current_portfolio: Dict[str, Dict[str, Any]],
        total_assets: float
    ) -> List[Dict[str, Any]]:
        리밸런싱 주문 계산

        Args:
            current_portfolio: 현재 포트폴리오
                {
                    '005930': {
                        'quantity': 10,
                        'price': 70000,
                        'value': 700000
                    }
                }
            total_assets: 총 자산

        Returns:
            주문 리스트
        orders = []

        current_weights = {}
        for code, info in current_portfolio.items():
            current_weights[code] = info['value'] / total_assets if total_assets > 0 else 0

        for code, target_weight in self.target_weights.items():
            target_value = total_assets * target_weight
            current_value = current_portfolio.get(code, {}).get('value', 0)
            diff_value = target_value - current_value

            if abs(diff_value) < 10000:
                continue

            current_price = current_portfolio.get(code, {}).get('price', 0)
            if current_price == 0:
                continue

            quantity = int(abs(diff_value) / current_price)

            if quantity > 0:
                order = {
                    'stock_code': code,
                    'action': 'buy' if diff_value > 0 else 'sell',
                    'quantity': quantity,
                    'price': current_price,
                    'reason': 'rebalancing'
                }
                orders.append(order)

        logger.info(f"리밸런싱 주문 계산: {len(orders)}개")
        return orders

    def execute_rebalance(
        self,
        orders: List[Dict[str, Any]],
        dry_run: bool = True
    ) -> bool:
        리밸런싱 실행

        Args:
            orders: 주문 리스트
            dry_run: 실제 실행 여부

        Returns:
            성공 여부
        if dry_run:
            logger.info("DRY RUN: 리밸런싱 시뮬레이션")
            for order in orders:
                logger.info(f"  {order['action'].upper()} {order['stock_code']} x{order['quantity']}")
            return True

        logger.info("실제 리밸런싱 실행 (TODO)")

        self.last_rebalance_date = datetime.now()
        return True

    def get_status(self) -> Dict[str, Any]:
        """리밸런서 상태 조회"""
        return {
            'enabled': self.enabled,
            'method': self.method,
            'last_rebalance': self.last_rebalance_date.isoformat() if self.last_rebalance_date else None,
            'target_weights': self.target_weights
        }


if __name__ == "__main__":
    rebalancer = PortfolioRebalancer({
        'enabled': True,
        'method': 'threshold_based',
        'threshold_pct': 0."05"
    })

    rebalancer.set_target_weights({
        '005930': 0.40,
        '000660': 0.30,
        '035720': 0.30
    })

    current_portfolio = {
        '005930': {'quantity': 10, 'price': 70000, 'value': 700000},
        '000660': {'quantity': 5, 'price': 120000, 'value': 600000},
        '035720': {'quantity': 20, 'price': 50000, 'value': 1000000}
    }

    total_assets = sum(p['value'] for p in current_portfolio.values())

    current_weights = {
        code: info['value'] / total_assets
        for code, info in current_portfolio.items()
    }

    should_rebalance, reason = rebalancer.should_rebalance(current_weights)
    print(f"리밸런싱 필요: {should_rebalance} ({reason})")

    if should_rebalance:
        orders = rebalancer.calculate_rebalance_orders(current_portfolio, total_assets)
        rebalancer.execute_rebalance(orders, dry_run=True)
