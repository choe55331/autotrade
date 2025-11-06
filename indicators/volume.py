"""
Volume Indicators
- Volume SMA
- OBV (On-Balance Volume)
- Volume Ratio Analysis
"""
import numpy as np
import pandas as pd
from typing import Dict


def volume_sma(volume: pd.Series, period: int = 20) -> pd.Series:
    """
    Volume Simple Moving Average

    Args:
        volume: Volume data
        period: SMA period (default 20)

    Returns:
        Volume SMA values
    """
    return volume.rolling(window=period).mean()


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    On-Balance Volume

    Args:
        close: Close prices
        volume: Volume data

    Returns:
        OBV values
    """
    obv_values = pd.Series(index=close.index, dtype=float)
    obv_values.iloc[0] = volume.iloc[0]

    for i in range(1, len(close)):
        if close.iloc[i] > close.iloc[i - 1]:
            obv_values.iloc[i] = obv_values.iloc[i - 1] + volume.iloc[i]
        elif close.iloc[i] < close.iloc[i - 1]:
            obv_values.iloc[i] = obv_values.iloc[i - 1] - volume.iloc[i]
        else:
            obv_values.iloc[i] = obv_values.iloc[i - 1]

    return obv_values


def volume_ratio(current_volume: int, avg_volume: float) -> float:
    """
    Calculate volume ratio

    Args:
        current_volume: Current volume
        avg_volume: Average volume

    Returns:
        Volume ratio (current / average)
    """
    if avg_volume == 0:
        return 0

    return current_volume / avg_volume


def calculate_volume_score(volume: pd.Series,
                            prices: pd.Series,
                            period: int = 20) -> Dict:
    Calculate comprehensive volume analysis

    Args:
        volume: Volume data
        prices: Price data
        period: Analysis period

    Returns:
        Dictionary with volume analysis
    if len(volume) < period:
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

    vol_sma = volume_sma(volume, period)
    current_volume = volume.iloc[-1]
    avg_volume = vol_sma.iloc[-1]

    vol_ratio = volume_ratio(current_volume, avg_volume)

    result['indicators']['volume_ratio'] = {
        'current': current_volume,
        'average': avg_volume,
        'ratio': vol_ratio,
        'condition': 'normal'
    }

    if vol_ratio >= 2.0:
        result['indicators']['volume_ratio']['condition'] = 'very_high'
        volume_score = 90
    elif vol_ratio >= 1.5:
        result['indicators']['volume_ratio']['condition'] = 'high'
        volume_score = 70
    elif vol_ratio >= 1.2:
        result['indicators']['volume_ratio']['condition'] = 'above_average'
        volume_score = 60
    elif vol_ratio <= 0.5:
        result['indicators']['volume_ratio']['condition'] = 'very_low'
        volume_score = 20
    elif vol_ratio <= 0.7:
        result['indicators']['volume_ratio']['condition'] = 'low'
        volume_score = 35
    else:
        result['indicators']['volume_ratio']['condition'] = 'normal'
        volume_score = 50

    obv_values = obv(prices, volume)
    current_obv = obv_values.iloc[-1]
    obv_ma = obv_values.rolling(window=period).mean()
    current_obv_ma = obv_ma.iloc[-1]

    result['indicators']['obv'] = {
        'value': current_obv,
        'ma': current_obv_ma,
        'condition': 'neutral'
    }

    if len(obv_values) >= period:
        obv_trend = current_obv - obv_values.iloc[-period]
        price_trend = prices.iloc[-1] - prices.iloc[-period]

        if obv_trend > 0 and price_trend > 0:
            result['indicators']['obv']['condition'] = 'bullish_confirmation'
            obv_score = 70
        elif obv_trend < 0 and price_trend < 0:
            result['indicators']['obv']['condition'] = 'bearish_confirmation'
            obv_score = 30
        elif obv_trend > 0 and price_trend < 0:
            result['indicators']['obv']['condition'] = 'bullish_divergence'
            obv_score = 75
        elif obv_trend < 0 and price_trend > 0:
            result['indicators']['obv']['condition'] = 'bearish_divergence'
            obv_score = 25
        else:
            result['indicators']['obv']['condition'] = 'neutral'
            obv_score = 50
    else:
        obv_score = 50

    result['score'] = (volume_score + obv_score) / 2

    if result['score'] >= 65 and vol_ratio >= 1.5:
        result['signal'] = 'STRONG_BUY'
        result['strength'] = 'strong'
    elif result['score'] >= 55:
        result['signal'] = 'BUY'
        result['strength'] = 'moderate'
    elif result['score'] <= 35 and vol_ratio >= 1.5:
        result['signal'] = 'STRONG_SELL'
        result['strength'] = 'strong'
    elif result['score'] <= 45:
        result['signal'] = 'SELL'
        result['strength'] = 'moderate'
    else:
        result['signal'] = 'NEUTRAL'
        result['strength'] = 'weak'

    return result


def detect_volume_climax(volume: pd.Series,
                          prices: pd.Series,
                          period: int = 20,
                          threshold: float = 2.5) -> Dict:
    Detect volume climax (potential reversal points)

    Args:
        volume: Volume data
        prices: Price data
        period: Analysis period
        threshold: Volume ratio threshold for climax (default 2.5x average)

    Returns:
        Dictionary with climax detection
    if len(volume) < period:
        return {
            'is_climax': False,
            'type': 'none'
        }

    vol_sma = volume_sma(volume, period)
    current_volume = volume.iloc[-1]
    avg_volume = vol_sma.iloc[-1]

    vol_ratio = volume_ratio(current_volume, avg_volume)

    if len(prices) >= 2:
        price_change = ((prices.iloc[-1] / prices.iloc[-2]) - 1) * 100
    else:
        price_change = 0

    if vol_ratio >= threshold and price_change >= 3.0:
        return {
            'is_climax': True,
            'type': 'buying_climax',
            'volume_ratio': vol_ratio,
            'price_change': price_change,
            'signal': 'SELL'
        }

    if vol_ratio >= threshold and price_change <= -3.0:
        return {
            'is_climax': True,
            'type': 'selling_climax',
            'volume_ratio': vol_ratio,
            'price_change': price_change,
            'signal': 'BUY'
        }

    return {
        'is_climax': False,
        'type': 'none',
        'volume_ratio': vol_ratio,
        'price_change': price_change
    }


def calculate_volume_profile(prices: pd.Series,
                              volume: pd.Series,
                              num_bins: int = 10) -> Dict:
    Calculate volume profile (volume distribution by price level)

    Args:
        prices: Price data
        volume: Volume data
        num_bins: Number of price bins

    Returns:
        Dictionary with volume profile analysis
    if len(prices) < 10 or len(volume) < 10:
        return {
            'poc': 0,
            'vah': 0,
            'val': 0,
            'distribution': []
        }

    price_min = prices.min()
    price_max = prices.max()
    bins = np.linspace(price_min, price_max, num_bins + 1)

    volume_profile = []
    for i in range(len(bins) - 1):
        bin_low = bins[i]
        bin_high = bins[i + 1]
        mask = (prices >= bin_low) & (prices < bin_high)
        bin_volume = volume[mask].sum()

        volume_profile.append({
            'price_low': bin_low,
            'price_high': bin_high,
            'price_mid': (bin_low + bin_high) / 2,
            'volume': bin_volume
        })

    max_volume_bin = max(volume_profile, key=lambda x: x['volume'])
    poc = max_volume_bin['price_mid']

    total_volume = sum([b['volume'] for b in volume_profile])
    target_volume = total_volume * 0.7

    sorted_bins = sorted(volume_profile, key=lambda x: x['volume'], reverse=True)

    cumulative_volume = 0
    value_area_bins = []
    for bin_data in sorted_bins:
        value_area_bins.append(bin_data)
        cumulative_volume += bin_data['volume']
        if cumulative_volume >= target_volume:
            break

    value_area_prices = [b['price_mid'] for b in value_area_bins]
    vah = max(value_area_prices)
    val = min(value_area_prices)

    return {
        'poc': poc,
        'vah': vah,
        'val': val,
        'distribution': volume_profile,
        'current_position': 'above_vah' if prices.iloc[-1] > vah else ('below_val' if prices.iloc[-1] < val else 'in_value_area')
    }
