Trend Indicators
- SMA (Simple Moving Average)
- EMA (Exponential Moving Average)
- Trend Detection
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional


def sma(data: pd.Series, period: int) -> pd.Series:
    """
    Simple Moving Average

    Args:
        data: Price data (Series)
        period: Period for SMA

    Returns:
        SMA values as Series
    """
    return data.rolling(window=period).mean()


def ema(data: pd.Series, period: int) -> pd.Series:
    """
    Exponential Moving Average

    Args:
        data: Price data (Series)
        period: Period for EMA

    Returns:
        EMA values as Series
    """
    return data.ewm(span=period, adjust=False).mean()


def calculate_trend(prices: pd.Series, short_period: int = 20, long_period: int = 60) -> dict:
    """
    Calculate trend information

    Args:
        prices: Price data
        short_period: Short-term MA period
        long_period: Long-term MA period

    Returns:
        Dictionary with trend analysis:
        - direction: 'uptrend', 'downtrend', 'sideways'
        - strength: 0-100
        - short_ma: Current short MA value
        - long_ma: Current long MA value
        - crossover: True if recent golden/death cross
    """
    if len(prices) < long_period:
        return {
            'direction': 'unknown',
            'strength': 0,
            'short_ma': 0,
            'long_ma': 0,
            'crossover': False
        }

    short_ma = sma(prices, short_period)
    long_ma = sma(prices, long_period)

    current_price = prices.iloc[-1]
    current_short_ma = short_ma.iloc[-1]
    current_long_ma = long_ma.iloc[-1]

    if current_short_ma > current_long_ma and current_price > current_short_ma:
        direction = 'uptrend'
        strength = min(100, ((current_short_ma / current_long_ma) - 1) * 100)
    elif current_short_ma < current_long_ma and current_price < current_short_ma:
        direction = 'downtrend'
        strength = min(100, ((current_long_ma / current_short_ma) - 1) * 100)
    else:
        direction = 'sideways'
        strength = 50

    crossover = False
    if len(short_ma) >= 3 and len(long_ma) >= 3:
        prev_short = short_ma.iloc[-3]
        prev_long = long_ma.iloc[-3]

        if current_short_ma > current_long_ma and prev_short <= prev_long:
            crossover = True
        elif current_short_ma < current_long_ma and prev_short >= prev_long:
            crossover = True

    return {
        'direction': direction,
        'strength': abs(strength),
        'short_ma': current_short_ma,
        'long_ma': current_long_ma,
        'crossover': crossover
    }


def calculate_ma_position(price: float, mas: List[float]) -> dict:
    """
    Calculate price position relative to multiple MAs

    Args:
        price: Current price
        mas: List of MA values

    Returns:
        Position analysis
    """
    above_count = sum(1 for ma in mas if price > ma)
    below_count = sum(1 for ma in mas if price < ma)

    if above_count == len(mas):
        position = 'strong_uptrend'
        score = 100
    elif above_count > below_count:
        position = 'uptrend'
        score = (above_count / len(mas)) * 100
    elif below_count > above_count:
        position = 'downtrend'
        score = (below_count / len(mas)) * 100
    elif below_count == len(mas):
        position = 'strong_downtrend'
        score = 100
    else:
        position = 'neutral'
        score = 50

    return {
        'position': position,
        'score': score,
        'above_count': above_count,
        'below_count': below_count
    }
