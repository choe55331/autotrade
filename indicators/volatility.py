Volatility Indicators
- Bollinger Bands
- ATR (Average True Range)
- Volatility Analysis
import numpy as np
import pandas as pd
from typing import Tuple, Dict


def bollinger_bands(data: pd.Series,
                    period: int = 20,
                    std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    Bollinger Bands

    Args:
        data: Price data
        period: Moving average period (default 20)
        std_dev: Standard deviation multiplier (default 2.0)

    Returns:
        Tuple of (upper_band, middle_band, lower_band)
    middle_band = data.rolling(window=period).mean()
    std = data.rolling(window=period).std()

    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)

    return upper_band, middle_band, lower_band


def atr(high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14) -> pd.Series:
    Average True Range

    Args:
        high: High prices
        low: Low prices
        close: Close prices
        period: ATR period (default 14)

    Returns:
        ATR values
    high_low = high - low
    high_close = np.abs(high - close.shift())
    low_close = np.abs(low - close.shift())

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    atr_values = true_range.ewm(span=period, adjust=False).mean()

    return atr_values


def calculate_volatility_score(prices: pd.Series,
                                high: pd.Series = None,
                                low: pd.Series = None,
                                bb_period: int = 20,
                                bb_std: float = 2.0,
                                atr_period: int = 14) -> Dict:
    Calculate comprehensive volatility score

    Args:
        prices: Close prices
        high: High prices (optional, for ATR)
        low: Low prices (optional, for ATR)
        bb_period: Bollinger Bands period
        bb_std: Bollinger Bands standard deviation
        atr_period: ATR period

    Returns:
        Dictionary with volatility analysis
    if len(prices) < max(bb_period, atr_period):
        return {
            'score': 50,
            'level': 'unknown',
            'indicators': {}
        }

    result = {
        'score': 0,
        'level': 'normal',
        'indicators': {}
    }

    scores = []

    upper, middle, lower = bollinger_bands(prices, bb_period, bb_std)
    current_price = prices.iloc[-1]
    current_upper = upper.iloc[-1]
    current_middle = middle.iloc[-1]
    current_lower = lower.iloc[-1]

    bandwidth = current_upper - current_lower
    percent_b = (current_price - current_lower) / bandwidth if bandwidth > 0 else 0.5

    result['indicators']['bollinger'] = {
        'upper': current_upper,
        'middle': current_middle,
        'lower': current_lower,
        'percent_b': percent_b,
        'bandwidth': bandwidth,
        'condition': 'neutral'
    }

    if current_price >= current_upper:
        result['indicators']['bollinger']['condition'] = 'overbought'
        result['indicators']['bollinger']['signal'] = 'SELL'
        scores.append(80)
    elif current_price <= current_lower:
        result['indicators']['bollinger']['condition'] = 'oversold'
        result['indicators']['bollinger']['signal'] = 'BUY'
        scores.append(80)
    elif percent_b > 0.8:
        result['indicators']['bollinger']['condition'] = 'near_upper'
        result['indicators']['bollinger']['signal'] = 'SELL'
        scores.append(65)
    elif percent_b < 0.2:
        result['indicators']['bollinger']['condition'] = 'near_lower'
        result['indicators']['bollinger']['signal'] = 'BUY'
        scores.append(65)
    else:
        result['indicators']['bollinger']['condition'] = 'neutral'
        result['indicators']['bollinger']['signal'] = 'HOLD'
        scores.append(40)

    bb_width_sma = pd.Series(upper - lower).rolling(window=bb_period).mean()
    current_bb_width_sma = bb_width_sma.iloc[-1]

    if bandwidth < current_bb_width_sma * 0.7:
        result['indicators']['bollinger']['squeeze'] = True
        result['indicators']['bollinger']['squeeze_level'] = 'tight'
    elif bandwidth < current_bb_width_sma * 0.85:
        result['indicators']['bollinger']['squeeze'] = True
        result['indicators']['bollinger']['squeeze_level'] = 'moderate'
    else:
        result['indicators']['bollinger']['squeeze'] = False
        result['indicators']['bollinger']['squeeze_level'] = 'none'

    if high is not None and low is not None:
        atr_values = atr(high, low, prices, atr_period)
        current_atr = atr_values.iloc[-1]

        atr_percent = (current_atr / current_price) * 100

        atr_sma = atr_values.rolling(window=atr_period).mean()
        current_atr_sma = atr_sma.iloc[-1]

        result['indicators']['atr'] = {
            'value': current_atr,
            'percent': atr_percent,
            'sma': current_atr_sma,
            'condition': 'normal'
        }

        if current_atr > current_atr_sma * 1.5:
            result['indicators']['atr']['condition'] = 'very_high'
            scores.append(90)
        elif current_atr > current_atr_sma * 1.2:
            result['indicators']['atr']['condition'] = 'high'
            scores.append(70)
        elif current_atr < current_atr_sma * 0.7:
            result['indicators']['atr']['condition'] = 'low'
            scores.append(30)
        else:
            result['indicators']['atr']['condition'] = 'normal'
            scores.append(50)

    if scores:
        result['score'] = sum(scores) / len(scores)

        if result['score'] >= 75:
            result['level'] = 'very_high'
        elif result['score'] >= 60:
            result['level'] = 'high'
        elif result['score'] >= 40:
            result['level'] = 'normal'
        else:
            result['level'] = 'low'

    return result


def calculate_dynamic_stop_loss(entry_price: float,
                                 atr_value: float,
                                 direction: str = 'long',
                                 atr_multiplier: float = 2.0,
                                 min_percent: float = 3.0,
                                 max_percent: float = 10.0) -> float:
    Calculate dynamic stop-loss based on ATR

    Args:
        entry_price: Entry price
        atr_value: Current ATR value
        direction: 'long' or 'short'
        atr_multiplier: ATR multiplier (default 2.0)
        min_percent: Minimum stop-loss percent (default 3%)
        max_percent: Maximum stop-loss percent (default 10%)

    Returns:
        Stop-loss price
    atr_stop_distance = atr_value * atr_multiplier

    atr_stop_percent = (atr_stop_distance / entry_price) * 100

    stop_percent = max(min_percent, min(atr_stop_percent, max_percent))

    if direction == 'long':
        stop_price = entry_price * (1 - stop_percent / 100)
    else:
        stop_price = entry_price * (1 + stop_percent / 100)

    return stop_price


def calculate_dynamic_take_profit(entry_price: float,
                                   atr_value: float,
                                   direction: str = 'long',
                                   atr_multiplier: float = 3.0,
                                   min_percent: float = 5.0,
                                   max_percent: float = 20.0) -> float:
    Calculate dynamic take-profit based on ATR

    Args:
        entry_price: Entry price
        atr_value: Current ATR value
        direction: 'long' or 'short'
        atr_multiplier: ATR multiplier (default 3.0)
        min_percent: Minimum take-profit percent (default 5%)
        max_percent: Maximum take-profit percent (default 20%)

    Returns:
        Take-profit price
    atr_profit_distance = atr_value * atr_multiplier

    atr_profit_percent = (atr_profit_distance / entry_price) * 100

    profit_percent = max(min_percent, min(atr_profit_percent, max_percent))

    if direction == 'long':
        take_profit_price = entry_price * (1 + profit_percent / 100)
    else:
        take_profit_price = entry_price * (1 - profit_percent / 100)

    return take_profit_price


def calculate_volatility_breakout(prices: pd.Series,
                                   high: pd.Series,
                                   low: pd.Series,
                                   lookback_period: int = 20,
                                   k_value: float = 0.5) -> Dict:
    Calculate volatility breakout levels (Larry Williams style)

    Args:
        prices: Close prices
        high: High prices
        low: Low prices
        lookback_period: Lookback period (default 20)
        k_value: K value (default 0.5)

    Returns:
        Dictionary with breakout levels
    if len(prices) < lookback_period:
        return {
            'entry_long': 0,
            'entry_short': 0,
            'range': 0,
            'signal': 'NONE'
        }

    prev_high = high.iloc[-2]
    prev_low = low.iloc[-2]
    prev_close = prices.iloc[-2]

    range_value = prev_high - prev_low

    entry_long = prev_close + (range_value * k_value)
    entry_short = prev_close - (range_value * k_value)

    current_price = prices.iloc[-1]

    signal = 'NONE'
    if current_price >= entry_long:
        signal = 'LONG'
    elif current_price <= entry_short:
        signal = 'SHORT'

    return {
        'entry_long': entry_long,
        'entry_short': entry_short,
        'range': range_value,
        'signal': signal,
        'current_price': current_price
    }
