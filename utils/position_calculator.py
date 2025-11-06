utils/position_calculator.py
포지션 사이즈 계산 유틸리티

다양한 포지션 사이징 전략을 제공
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def calculate_position_size_by_ratio(
    capital: float,
    price: float,
    ratio: float,
    commission_rate: float = 0.00015,
    min_quantity: int = 1
) -> int:
    자본 비율 기반 포지션 사이즈 계산

    Args:
        capital: 총 자본금
        price: 현재 가격
        ratio: 투자 비율 (0.0 ~ 1.0)
        commission_rate: 수수료율
        min_quantity: 최소 수량

    Returns:
        매수 수량
    if capital <= 0 or price <= 0 or ratio <= 0:
        logger.warning(f"Invalid parameters: capital={capital}, price={price}, ratio={ratio}")
        return 0

    if ratio > 1.0:
        logger.warning(f"Ratio {ratio} exceeds 1.0, capping at 1.0")
        ratio = 1.0

    invest_amount = capital * ratio

    quantity = int(invest_amount / (price * (1 + commission_rate)))

    quantity = max(min_quantity, quantity)

    logger.debug(
        f"Position size by ratio: Capital={capital:,.0f}원 × {ratio*100:.1f}% = "
        f"{invest_amount:,.0f}원 ÷ {price:,}원 = {quantity}주"
    )

    return quantity


def calculate_position_size_fixed_amount(
    invest_amount: float,
    price: float,
    commission_rate: float = 0.00015,
    min_quantity: int = 1
) -> int:
    고정 금액 기반 포지션 사이즈 계산

    Args:
        invest_amount: 투자 금액
        price: 현재 가격
        commission_rate: 수수료율
        min_quantity: 최소 수량

    Returns:
        매수 수량
    if invest_amount <= 0 or price <= 0:
        logger.warning(f"Invalid parameters: amount={invest_amount}, price={price}")
        return 0

    quantity = int(invest_amount / (price * (1 + commission_rate)))

    quantity = max(min_quantity, quantity)

    logger.debug(
        f"Position size by fixed amount: {invest_amount:,.0f}원 ÷ {price:,}원 = {quantity}주"
    )

    return quantity


def calculate_position_size_by_risk(
    capital: float,
    price: float,
    stop_loss_price: float,
    risk_ratio: float = 0.02,
    min_quantity: int = 1
) -> int:
    위험 기반 포지션 사이즈 계산 (Risk-Based Position Sizing)

    Args:
        capital: 총 자본금
        price: 현재 가격
        stop_loss_price: 손절 가격
        risk_ratio: 위험 비율 (기본: 2%, 총 자본의 최대 손실 허용치)
        min_quantity: 최소 수량

    Returns:
        매수 수량
    if capital <= 0 or price <= 0 or stop_loss_price <= 0:
        logger.warning(f"Invalid parameters: capital={capital}, price={price}, stop_loss={stop_loss_price}")
        return 0

    if stop_loss_price >= price:
        logger.warning(f"Stop loss price ({stop_loss_price}) must be lower than current price ({price})")
        return 0

    risk_per_share = price - stop_loss_price

    total_risk = capital * risk_ratio

    quantity = int(total_risk / risk_per_share)

    quantity = max(min_quantity, quantity)

    logger.debug(
        f"Position size by risk: Capital={capital:,.0f}원 × {risk_ratio*100}% = {total_risk:,.0f}원 위험, "
        f"주당 위험={risk_per_share:,}원, 수량={quantity}주"
    )

    return quantity


def calculate_position_size_kelly_criterion(
    capital: float,
    price: float,
    win_rate: float,
    avg_win: float,
    avg_loss: float,
    kelly_fraction: float = 0.5,
    commission_rate: float = 0.00015,
    min_quantity: int = 1
) -> int:
    켈리 기준 포지션 사이즈 계산 (Kelly Criterion)

    Args:
        capital: 총 자본금
        price: 현재 가격
        win_rate: 승률 (0.0 ~ 1.0)
        avg_win: 평균 수익률 (0.0 ~ 1.0)
        avg_loss: 평균 손실률 (0.0 ~ 1.0, 양수로 입력)
        kelly_fraction: 켈리 조정 비율 (기본: 0.5 = Half Kelly)
        commission_rate: 수수료율
        min_quantity: 최소 수량

    Returns:
        매수 수량
    if capital <= 0 or price <= 0:
        logger.warning(f"Invalid parameters: capital={capital}, price={price}")
        return 0

    if not (0 <= win_rate <= 1):
        logger.warning(f"Invalid win rate: {win_rate}")
        return 0

    if avg_loss == 0:
        logger.warning("Average loss cannot be zero")
        return 0

    p = win_rate
    q = 1 - win_rate
    b = avg_win / avg_loss

    kelly_percentage = (p * b - q) / b

    adjusted_kelly = kelly_percentage * kelly_fraction

    if adjusted_kelly <= 0:
        logger.warning(f"Kelly criterion suggests no position (kelly={kelly_percentage:.2%})")
        return 0

    if adjusted_kelly > 1.0:
        logger.warning(f"Kelly criterion {adjusted_kelly:.2%} exceeds 100%, capping at 100%")
        adjusted_kelly = 1.0

    invest_amount = capital * adjusted_kelly

    quantity = int(invest_amount / (price * (1 + commission_rate)))

    quantity = max(min_quantity, quantity)

    logger.debug(
        f"Kelly Criterion: WinRate={win_rate:.1%}, AvgWin={avg_win:.1%}, AvgLoss={avg_loss:.1%}, "
        f"Kelly={kelly_percentage:.2%}, Adjusted={adjusted_kelly:.2%}, Quantity={quantity}주"
    )

    return quantity


def calculate_position_size_volatility_based(
    capital: float,
    price: float,
    volatility: float,
    target_risk: float = 0.02,
    commission_rate: float = 0.00015,
    min_quantity: int = 1
) -> int:
    변동성 기반 포지션 사이즈 계산

    Args:
        capital: 총 자본금
        price: 현재 가격
        volatility: 일일 변동성 (표준편차, 0.0 ~ 1.0)
        target_risk: 목표 위험 비율 (기본: 2%)
        commission_rate: 수수료율
        min_quantity: 최소 수량

    Returns:
        매수 수량
    if capital <= 0 or price <= 0 or volatility <= 0:
        logger.warning(f"Invalid parameters: capital={capital}, price={price}, volatility={volatility}")
        return 0

    total_risk = capital * target_risk

    risk_per_share = price * volatility

    if risk_per_share == 0:
        logger.warning("Risk per share is zero")
        return 0

    quantity = int(total_risk / risk_per_share)

    quantity = max(min_quantity, quantity)

    logger.debug(
        f"Volatility-based sizing: Capital={capital:,.0f}원 × {target_risk*100}% = {total_risk:,.0f}원, "
        f"Volatility={volatility:.2%}, Risk/Share={risk_per_share:,.0f}원, Quantity={quantity}주"
    )

    return quantity


def calculate_max_position_size(
    capital: float,
    price: float,
    max_position_ratio: float = 0.20,
    commission_rate: float = 0.00015,
    min_quantity: int = 1
) -> int:
    최대 포지션 사이즈 계산 (단일 종목 최대 투자 비율 제한)

    Args:
        capital: 총 자본금
        price: 현재 가격
        max_position_ratio: 최대 포지션 비율 (기본: 20%)
        commission_rate: 수수료율
        min_quantity: 최소 수량

    Returns:
        최대 매수 수량
    return calculate_position_size_by_ratio(
        capital=capital,
        price=price,
        ratio=max_position_ratio,
        commission_rate=commission_rate,
        min_quantity=min_quantity
    )


def validate_position_size(
    quantity: int,
    price: float,
    capital: float,
    max_position_ratio: float = 0.30
) -> bool:
    포지션 사이즈 유효성 검증

    Args:
        quantity: 수량
        price: 가격
        capital: 총 자본금
        max_position_ratio: 최대 포지션 비율

    Returns:
        유효 여부
    if quantity <= 0:
        logger.warning(f"Invalid quantity: {quantity}")
        return False

    if price <= 0:
        logger.warning(f"Invalid price: {price}")
        return False

    if capital <= 0:
        logger.warning(f"Invalid capital: {capital}")
        return False

    total_investment = quantity * price

    position_ratio = total_investment / capital

    if position_ratio > max_position_ratio:
        logger.warning(
            f"Position size {quantity}주 × {price:,}원 = {total_investment:,.0f}원 "
            f"exceeds max ratio {max_position_ratio:.1%} of capital {capital:,.0f}원"
        )
        return False

    logger.debug(f"Position size validation passed: {position_ratio:.1%} of capital")
    return True


__all__ = [
    'calculate_position_size_by_ratio',
    'calculate_position_size_fixed_amount',
    'calculate_position_size_by_risk',
    'calculate_position_size_kelly_criterion',
    'calculate_position_size_volatility_based',
    'calculate_max_position_size',
    'validate_position_size',
]
