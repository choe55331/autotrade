"""
Momentum Indicators
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Stochastic Oscillator
"""
import numpy as np
import pandas as pd
from typing import Tuple, Dict


def rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index

    Args:
        data: Price data
        period: RSI period (default 14)

    Returns:
        RSI values (0-100)
    """
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi_values = 100 - (100 / (1 + rs))

    return rsi_values


def macd(data: pd.Series,
         fast_period: int = 12,
         slow_period: int = 26,
         signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    MACD (Moving Average Convergence Divergence)

    Args:
        data: Price data
        fast_period: Fast EMA period (default 12)
        slow_period: Slow EMA period (default 26)
        signal_period: Signal line period (default 9)

    Returns:
        Tuple of (macd_line, signal_line, histogram)
    """
    # Calculate EMAs
    fast_ema = data.ewm(span=fast_period, adjust=False).mean()
    slow_ema = data.ewm(span=slow_period, adjust=False).mean()

    # MACD line
    macd_line = fast_ema - slow_ema

    # Signal line
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

    # Histogram
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def stochastic(high: pd.Series,
               low: pd.Series,
               close: pd.Series,
               k_period: int = 14,
               d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
    """
    Stochastic Oscillator

    Args:
        high: High prices
        low: Low prices
        close: Close prices
        k_period: %K period (default 14)
        d_period: %D period (default 3)

    Returns:
        Tuple of (%K, %D)
    """
    # Calculate %K
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()

    k_values = 100 * (close - lowest_low) / (highest_high - lowest_low)

    # Calculate %D (smoothed %K)
    d_values = k_values.rolling(window=d_period).mean()

    return k_values, d_values


def calculate_momentum_score(prices: pd.Series,
                              high: pd.Series = None,
                              low: pd.Series = None,
                              rsi_period: int = 14,
                              macd_fast: int = 12,
                              macd_slow: int = 26,
                              macd_signal: int = 9,
                              stoch_k: int = 14,
                              stoch_d: int = 3) -> Dict:
    """
    Calculate comprehensive momentum score

    Args:
        prices: Close prices
        high: High prices (optional, for stochastic)
        low: Low prices (optional, for stochastic)
        rsi_period: RSI period
        macd_fast: MACD fast period
        macd_slow: MACD slow period
        macd_signal: MACD signal period
        stoch_k: Stochastic %K period
        stoch_d: Stochastic %D period

    Returns:
        Dictionary with momentum analysis
    """
    if len(prices) < max(rsi_period, macd_slow, stoch_k):
        return {
            'score': 50,
            'signal': 'NEUTRAL',
            'strength': 'weak',
            'indicators': {}
        }

    result = {
        'score': 0,
        'signal': 'NEUTRAL',
        'strength': 'weak',
        'indicators': {}
    }

    signals = []
    scores = []

    # RSI Analysis
    rsi_values = rsi(prices, rsi_period)
    current_rsi = rsi_values.iloc[-1]

    result['indicators']['rsi'] = {
        'value': current_rsi,
        'condition': 'neutral'
    }

    if current_rsi < 30:
        result['indicators']['rsi']['condition'] = 'oversold'
        signals.append('BUY')
        scores.append(80)  # Strong buy signal
    elif current_rsi < 40:
        result['indicators']['rsi']['condition'] = 'weak'
        signals.append('BUY')
        scores.append(60)
    elif current_rsi > 70:
        result['indicators']['rsi']['condition'] = 'overbought'
        signals.append('SELL')
        scores.append(20)  # Strong sell signal
    elif current_rsi > 60:
        result['indicators']['rsi']['condition'] = 'strong'
        signals.append('SELL')
        scores.append(40)
    else:
        signals.append('NEUTRAL')
        scores.append(50)

    # MACD Analysis
    macd_line, signal_line, histogram = macd(prices, macd_fast, macd_slow, macd_signal)
    current_macd = macd_line.iloc[-1]
    current_signal = signal_line.iloc[-1]
    current_hist = histogram.iloc[-1]

    result['indicators']['macd'] = {
        'macd': current_macd,
        'signal': current_signal,
        'histogram': current_hist,
        'condition': 'neutral'
    }

    # MACD crossover
    if len(macd_line) >= 2:
        prev_hist = histogram.iloc[-2]

        if current_hist > 0 and prev_hist <= 0:
            # Bullish crossover
            result['indicators']['macd']['condition'] = 'bullish_cross'
            signals.append('BUY')
            scores.append(75)
        elif current_hist < 0 and prev_hist >= 0:
            # Bearish crossover
            result['indicators']['macd']['condition'] = 'bearish_cross'
            signals.append('SELL')
            scores.append(25)
        elif current_hist > 0:
            result['indicators']['macd']['condition'] = 'bullish'
            signals.append('BUY')
            scores.append(60)
        else:
            result['indicators']['macd']['condition'] = 'bearish'
            signals.append('SELL')
            scores.append(40)
    else:
        signals.append('NEUTRAL')
        scores.append(50)

    # Stochastic Analysis (if high/low provided)
    if high is not None and low is not None:
        k_values, d_values = stochastic(high, low, prices, stoch_k, stoch_d)
        current_k = k_values.iloc[-1]
        current_d = d_values.iloc[-1]

        result['indicators']['stochastic'] = {
            'k': current_k,
            'd': current_d,
            'condition': 'neutral'
        }

        if current_k < 20 and current_d < 20:
            result['indicators']['stochastic']['condition'] = 'oversold'
            signals.append('BUY')
            scores.append(75)
        elif current_k > 80 and current_d > 80:
            result['indicators']['stochastic']['condition'] = 'overbought'
            signals.append('SELL')
            scores.append(25)
        elif current_k > current_d and current_k < 80:
            result['indicators']['stochastic']['condition'] = 'bullish'
            signals.append('BUY')
            scores.append(60)
        elif current_k < current_d and current_k > 20:
            result['indicators']['stochastic']['condition'] = 'bearish'
            signals.append('SELL')
            scores.append(40)
        else:
            signals.append('NEUTRAL')
            scores.append(50)

    # Calculate overall score
    if scores:
        result['score'] = sum(scores) / len(scores)

        # Determine signal
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')

        if buy_count > sell_count:
            result['signal'] = 'BUY'
            if buy_count >= len(signals) * 0.75:
                result['strength'] = 'strong'
            else:
                result['strength'] = 'moderate'
        elif sell_count > buy_count:
            result['signal'] = 'SELL'
            if sell_count >= len(signals) * 0.75:
                result['strength'] = 'strong'
            else:
                result['strength'] = 'moderate'
        else:
            result['signal'] = 'NEUTRAL'
            result['strength'] = 'weak'

    return result


def calculate_momentum_divergence(prices: pd.Series, indicator: pd.Series, lookback: int = 20) -> str:
    """
    Detect bullish/bearish divergence between price and indicator

    Args:
        prices: Price data
        indicator: Indicator data (RSI, MACD, etc.)
        lookback: Periods to look back

    Returns:
        'bullish_divergence', 'bearish_divergence', or 'none'
    """
    if len(prices) < lookback or len(indicator) < lookback:
        return 'none'

    recent_prices = prices.iloc[-lookback:]
    recent_indicator = indicator.iloc[-lookback:]

    price_trend = recent_prices.iloc[-1] - recent_prices.iloc[0]
    indicator_trend = recent_indicator.iloc[-1] - recent_indicator.iloc[0]

    # Bullish divergence: price making lower lows, indicator making higher lows
    if price_trend < 0 and indicator_trend > 0:
        return 'bullish_divergence'

    # Bearish divergence: price making higher highs, indicator making lower highs
    if price_trend > 0 and indicator_trend < 0:
        return 'bearish_divergence'

    return 'none'
