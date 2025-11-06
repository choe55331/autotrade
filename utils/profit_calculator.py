utils/profit_calculator.py
수익률 및 손익 계산 유틸리티

모든 전략에서 공통으로 사용하는 수익/손실 계산 로직을 통합
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def calculate_profit_loss(
    entry_price: float,
    exit_price: float,
    quantity: int
) -> float:
    손익 계산 (금액)

    Args:
        entry_price: 진입 가격
        exit_price: 청산 가격
        quantity: 수량

    Returns:
        손익 금액 (원)
    if entry_price <= 0 or exit_price <= 0 or quantity <= 0:
        logger.warning(f"Invalid parameters: entry={entry_price}, exit={exit_price}, qty={quantity}")
        return 0.0

    profit_loss = (exit_price - entry_price) * quantity
    return profit_loss


def calculate_profit_loss_rate(
    entry_price: float,
    exit_price: float
) -> float:
    손익률 계산 (%)

    Args:
        entry_price: 진입 가격
        exit_price: 청산 가격

    Returns:
        손익률 (%)
    if entry_price <= 0:
        logger.warning(f"Invalid entry price: {entry_price}")
        return 0.0

    profit_loss_rate = ((exit_price - entry_price) / entry_price) * 100
    return profit_loss_rate


def calculate_profit_loss_with_commission(
    entry_price: float,
    exit_price: float,
    quantity: int,
    commission_rate: float = 0.00015,
    tax_rate: float = 0.0023
) -> Tuple[float, float]:
    수수료 및 세금을 고려한 손익 계산

    Args:
        entry_price: 진입 가격
        exit_price: 청산 가격
        quantity: 수량
        commission_rate: 수수료율 (기본: 0.015%)
        tax_rate: 거래세율 (기본: 0.23%, 매도시만 적용)

    Returns:
        (실손익 금액, 실손익률)
    if entry_price <= 0 or exit_price <= 0 or quantity <= 0:
        logger.warning(f"Invalid parameters for commission calculation")
        return 0.0, 0.0

    buy_amount = entry_price * quantity
    buy_commission = buy_amount * commission_rate
    total_buy_cost = buy_amount + buy_commission

    sell_amount = exit_price * quantity
    sell_commission = sell_amount * commission_rate
    sell_tax = sell_amount * tax_rate if exit_price > entry_price else 0
    total_sell_revenue = sell_amount - sell_commission - sell_tax

    net_profit_loss = total_sell_revenue - total_buy_cost
    net_profit_loss_rate = (net_profit_loss / total_buy_cost) * 100

    logger.debug(
        f"Profit calculation: Buy={total_buy_cost:,.0f}원 (수수료={buy_commission:,.0f}원), "
        f"Sell={total_sell_revenue:,.0f}원 (수수료={sell_commission:,.0f}원, 세금={sell_tax:,.0f}원), "
        f"순손익={net_profit_loss:,.0f}원 ({net_profit_loss_rate:.2f}%)"
    )

    return net_profit_loss, net_profit_loss_rate


def calculate_expected_profit_with_slippage(
    entry_price: float,
    exit_price: float,
    quantity: int,
    slippage_rate: float = 0.001
) -> float:
    슬리피지를 고려한 예상 손익 계산

    Args:
        entry_price: 진입 가격
        exit_price: 청산 가격
        quantity: 수량
        slippage_rate: 슬리피지율 (기본: 0.1%)

    Returns:
        슬리피지 반영 손익 금액
    if entry_price <= 0 or exit_price <= 0 or quantity <= 0:
        return 0.0

    actual_entry_price = entry_price * (1 + slippage_rate)
    actual_exit_price = exit_price * (1 - slippage_rate)

    profit_loss = (actual_exit_price - actual_entry_price) * quantity

    logger.debug(
        f"Expected profit with slippage: "
        f"Entry {entry_price:,}→{actual_entry_price:,}, "
        f"Exit {exit_price:,}→{actual_exit_price:,}, "
        f"Profit={profit_loss:,.0f}원"
    )

    return profit_loss


def calculate_breakeven_price(
    entry_price: float,
    commission_rate: float = 0.00015,
    tax_rate: float = 0.0023
) -> float:
    손익분기점 가격 계산

    Args:
        entry_price: 진입 가격
        commission_rate: 수수료율
        tax_rate: 거래세율

    Returns:
        손익분기점 가격
    if entry_price <= 0:
        return 0.0

    buy_commission = commission_rate

    sell_cost = commission_rate + tax_rate

    breakeven_price = entry_price * (1 + buy_commission + sell_cost)

    logger.debug(f"Breakeven price for {entry_price:,}원: {breakeven_price:,.0f}원 (+{(breakeven_price/entry_price-1)*100:.2f}%)")

    return breakeven_price


def calculate_risk_reward_ratio(
    entry_price: float,
    target_price: float,
    stop_loss_price: float
) -> float:
    위험-보상 비율 (Risk-Reward Ratio) 계산

    Args:
        entry_price: 진입 가격
        target_price: 목표 가격
        stop_loss_price: 손절 가격

    Returns:
        위험-보상 비율 (reward / risk)
    if entry_price <= 0 or target_price <= 0 or stop_loss_price <= 0:
        return 0.0

    potential_reward = abs(target_price - entry_price)
    potential_risk = abs(entry_price - stop_loss_price)

    if potential_risk == 0:
        logger.warning("Risk is zero - invalid stop loss price")
        return 0.0

    risk_reward_ratio = potential_reward / potential_risk

    logger.debug(
        f"Risk-Reward: Entry={entry_price:,}, Target={target_price:,}, "
        f"StopLoss={stop_loss_price:,}, RRR={risk_reward_ratio:.2f}"
    )

    return risk_reward_ratio


__all__ = [
    'calculate_profit_loss',
    'calculate_profit_loss_rate',
    'calculate_profit_loss_with_commission',
    'calculate_expected_profit_with_slippage',
    'calculate_breakeven_price',
    'calculate_risk_reward_ratio',
]
