utils/statistics.py
통계 계산 유틸리티

금융 데이터 분석에 필요한 통계 함수 제공
import logging
from typing import List, Optional
import math

logger = logging.getLogger(__name__)


def calculate_mean(values: List[float]) -> float:
    """
    평균 계산

    Args:
        values: 값 리스트

    Returns:
        평균값
    """
    if not values:
        logger.warning("Empty list provided to calculate_mean")
        return 0.0

    return sum(values) / len(values)


def calculate_std(values: List[float], ddof: int = 0) -> float:
    """
    표준편차 계산

    Args:
        values: 값 리스트
        ddof: 자유도 (Delta Degrees of Freedom)
              0 = 모집단 표준편차 (기본값)
              1 = 표본 표준편차

    Returns:
        표준편차
    """
    if not values:
        logger.warning("Empty list provided to calculate_std")
        return 0.0

    if len(values) <= ddof:
        logger.warning(f"Not enough values ({len(values)}) for ddof={ddof}")
        return 0.0

    mean = calculate_mean(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - ddof)
    std = math.sqrt(variance)

    return std


def calculate_z_score(value: float, mean: float, std: float) -> float:
    """
    Z-Score (표준점수) 계산

    Args:
        value: 값
        mean: 평균
        std: 표준편차

    Returns:
        Z-Score
    """
    if std == 0:
        logger.warning("Standard deviation is zero, cannot calculate z-score")
        return 0.0

    z_score = (value - mean) / std
    return z_score


def calculate_moving_average(values: List[float], period: int) -> Optional[float]:
    """
    이동평균 계산 (Simple Moving Average)

    Args:
        values: 값 리스트
        period: 기간

    Returns:
        이동평균값 (데이터 부족시 None)
    """
    if not values or len(values) < period:
        logger.warning(f"Not enough data ({len(values) if values else 0}) for MA period {period}")
        return None

    recent_values = values[-period:]
    return calculate_mean(recent_values)


def calculate_exponential_moving_average(
    values: List[float],
    period: int,
    smoothing: float = 2.0
) -> Optional[float]:
    지수 이동평균 계산 (Exponential Moving Average, EMA)

    Args:
        values: 값 리스트
        period: 기간
        smoothing: 평활 상수 (기본: 2.0)

    Returns:
        EMA 값 (데이터 부족시 None)
    if not values or len(values) < period:
        logger.warning(f"Not enough data ({len(values) if values else 0}) for EMA period {period}")
        return None

    k = smoothing / (period + 1)

    ema = calculate_mean(values[:period])

    for value in values[period:]:
        ema = value * k + ema * (1 - k)

    return ema


def calculate_variance(values: List[float], ddof: int = 0) -> float:
    """
    분산 계산

    Args:
        values: 값 리스트
        ddof: 자유도 (0=모집단, 1=표본)

    Returns:
        분산
    """
    if not values or len(values) <= ddof:
        logger.warning(f"Not enough values for variance calculation")
        return 0.0

    mean = calculate_mean(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - ddof)

    return variance


def calculate_covariance(x_values: List[float], y_values: List[float]) -> float:
    """
    공분산 계산

    Args:
        x_values: X 값 리스트
        y_values: Y 값 리스트

    Returns:
        공분산
    """
    if not x_values or not y_values:
        logger.warning("Empty list provided to calculate_covariance")
        return 0.0

    if len(x_values) != len(y_values):
        logger.warning(f"Length mismatch: x={len(x_values)}, y={len(y_values)}")
        return 0.0

    x_mean = calculate_mean(x_values)
    y_mean = calculate_mean(y_values)

    covariance = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values)) / len(x_values)

    return covariance


def calculate_correlation(x_values: List[float], y_values: List[float]) -> float:
    """
    상관계수 계산 (Pearson Correlation Coefficient)

    Args:
        x_values: X 값 리스트
        y_values: Y 값 리스트

    Returns:
        상관계수 (-1.0 ~ 1.0)
    """
    if not x_values or not y_values:
        logger.warning("Empty list provided to calculate_correlation")
        return 0.0

    if len(x_values) != len(y_values):
        logger.warning(f"Length mismatch: x={len(x_values)}, y={len(y_values)}")
        return 0.0

    x_std = calculate_std(x_values)
    y_std = calculate_std(y_values)

    if x_std == 0 or y_std == 0:
        logger.warning("Standard deviation is zero, cannot calculate correlation")
        return 0.0

    covariance = calculate_covariance(x_values, y_values)
    correlation = covariance / (x_std * y_std)

    return correlation


def calculate_percentile(values: List[float], percentile: float) -> Optional[float]:
    """
    백분위수 계산

    Args:
        values: 값 리스트
        percentile: 백분위 (0 ~ 100)

    Returns:
        백분위수 값
    """
    if not values:
        logger.warning("Empty list provided to calculate_percentile")
        return None

    if not 0 <= percentile <= 100:
        logger.warning(f"Invalid percentile: {percentile}")
        return None

    sorted_values = sorted(values)
    index = (len(sorted_values) - 1) * (percentile / 100)

    lower = math.floor(index)
    upper = math.ceil(index)

    if lower == upper:
        return sorted_values[int(index)]

    weight = index - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def calculate_median(values: List[float]) -> Optional[float]:
    """
    중앙값 계산

    Args:
        values: 값 리스트

    Returns:
        중앙값
    """
    return calculate_percentile(values, 50)


def calculate_sharpe_ratio(
    returns: List[float],
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252
) -> float:
    샤프 비율 (Sharpe Ratio) 계산

    Args:
        returns: 수익률 리스트 (일별)
        risk_free_rate: 무위험 수익률 (연율)
        periods_per_year: 연간 거래일 수 (기본: 252)

    Returns:
        샤프 비율
    if not returns:
        logger.warning("Empty returns list")
        return 0.0

    mean_return = calculate_mean(returns) * periods_per_year

    std_return = calculate_std(returns, ddof=1) * math.sqrt(periods_per_year)

    if std_return == 0:
        logger.warning("Return standard deviation is zero")
        return 0.0

    sharpe_ratio = (mean_return - risk_free_rate) / std_return

    logger.debug(
        f"Sharpe Ratio: Mean Return={mean_return:.2%}, Std={std_return:.2%}, "
        f"Risk-Free={risk_free_rate:.2%}, Sharpe={sharpe_ratio:.2f}"
    )

    return sharpe_ratio


def calculate_max_drawdown(equity_curve: List[float]) -> float:
    """
    최대 낙폭 (Maximum Drawdown) 계산

    Args:
        equity_curve: 자산 곡선 (시간 순서)

    Returns:
        최대 낙폭 (%)
    """
    if not equity_curve or len(equity_curve) < 2:
        logger.warning("Not enough data for max drawdown calculation")
        return 0.0

    max_drawdown = 0.0
    peak = equity_curve[0]

    for value in equity_curve:
        if value > peak:
            peak = value

        drawdown = (peak - value) / peak if peak > 0 else 0.0
        max_drawdown = max(max_drawdown, drawdown)

    logger.debug(f"Max Drawdown: {max_drawdown:.2%}")

    return max_drawdown * 100


def calculate_bollinger_bands(
    prices: List[float],
    period: int = 20,
    num_std: float = 2.0
) -> Optional[tuple]:
    볼린저 밴드 계산

    Args:
        prices: 가격 리스트
        period: 기간 (기본: 20)
        num_std: 표준편차 배수 (기본: 2.0)

    Returns:
        (상단밴드, 중간밴드, 하단밴드) 또는 None
    if not prices or len(prices) < period:
        logger.warning(f"Not enough data ({len(prices) if prices else 0}) for Bollinger Bands")
        return None

    middle_band = calculate_moving_average(prices, period)
    if middle_band is None:
        return None

    recent_prices = prices[-period:]
    std = calculate_std(recent_prices, ddof=1)

    upper_band = middle_band + (num_std * std)
    lower_band = middle_band - (num_std * std)

    logger.debug(
        f"Bollinger Bands: Upper={upper_band:.2f}, Middle={middle_band:.2f}, "
        f"Lower={lower_band:.2f}"
    )

    return (upper_band, middle_band, lower_band)


__all__ = [
    'calculate_mean',
    'calculate_std',
    'calculate_z_score',
    'calculate_moving_average',
    'calculate_exponential_moving_average',
    'calculate_variance',
    'calculate_covariance',
    'calculate_correlation',
    'calculate_percentile',
    'calculate_median',
    'calculate_sharpe_ratio',
    'calculate_max_drawdown',
    'calculate_bollinger_bands',
]
