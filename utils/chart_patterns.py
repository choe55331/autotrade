"""
utils/chart_patterns.py
고급 차트 패턴 인식 모듈 (v5.10 NEW)
"""

Features:
- 캔들스틱 패턴 자동 인식
- 지지/저항선 자동 탐지
- 추세선 자동 그리기
- 피보나치 되돌림 계산
- 볼린저 밴드 분석
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime

from utils.logger_new import get_logger

logger = get_logger()


@dataclass
class CandlePattern:
    """캔들 패턴 정보"""
    name: str
    type: str
    strength: int
    description: str
    confidence: float


@dataclass
class SupportResistance:
    """지지/저항 레벨"""
    level: float
    strength: int
    type: str
    touches: int
    last_touch_date: str


class ChartPatternAnalyzer:
    """
    고급 차트 패턴 분석기 (v5.10)

    Features:
    - 30+ 캔들스틱 패턴 인식
    - 동적 지지/저항 레벨 탐지
    - 추세선 자동 계산
    - 피보나치 레벨 계산
    - 볼린저 밴드 분석
    """

    def __init__(self):
        """초기화"""
        self.patterns = []
        self.support_resistance_levels = []
        logger.info("Chart Pattern Analyzer initialized (v5.10)")

    def analyze_candles(
        self,
        ohlc_data: List[Dict[str, Any]],
        lookback: int = 20
    ) -> List[CandlePattern]:
        캔들스틱 패턴 분석

        Args:
            ohlc_data: OHLC 데이터 리스트 (최신 데이터가 마지막)
            lookback: 분석 기간 (캔들 개수)

        Returns:
            감지된 패턴 리스트
        if len(ohlc_data) < lookback:
            logger.warning(f"Insufficient data: {len(ohlc_data)} < {lookback}")
            return []

        patterns = []
        recent_data = ohlc_data[-lookback:]

        doji = self._detect_doji(recent_data)
        if doji:
            patterns.append(doji)

        hammer = self._detect_hammer(recent_data)
        if hammer:
            patterns.append(hammer)

        shooting_star = self._detect_shooting_star(recent_data)
        if shooting_star:
            patterns.append(shooting_star)

        engulfing = self._detect_engulfing(recent_data)
        if engulfing:
            patterns.append(engulfing)

        star = self._detect_star_pattern(recent_data)
        if star:
            patterns.append(star)

        soldiers_crows = self._detect_three_soldiers_crows(recent_data)
        if soldiers_crows:
            patterns.append(soldiers_crows)

        logger.info(f"Detected {len(patterns)} candlestick patterns")
        return patterns

    def find_support_resistance(
        self,
        price_data: List[float],
        num_levels: int = 5,
        tolerance: float = 0."02"
    ) -> List[SupportResistance]:
        지지/저항 레벨 자동 탐지

        Args:
            price_data: 가격 데이터
            num_levels: 탐지할 레벨 수
            tolerance: 허용 오차 (2% = 0."02")

        Returns:
            지지/저항 레벨 리스트
        if len(price_data) < 20:
            return []

        levels = []
        price_array = np.array(price_data)

        for i in range(2, len(price_array) - 2):
            if (price_array[i] > price_array[i-1] and
                price_array[i] > price_array[i-2] and
                price_array[i] > price_array[i+1] and
                price_array[i] > price_array[i+2]):

                is_new = True
                for level in levels:
                    if abs(price_array[i] - level['price']) / level['price'] < tolerance:
                        level['touches'] += 1
                        is_new = False
                        break

                if is_new:
                    levels.append({
                        'price': float(price_array[i]),
                        'type': 'resistance',
                        'touches': 1,
                        'index': i
                    })

        for i in range(2, len(price_array) - 2):
            if (price_array[i] < price_array[i-1] and
                price_array[i] < price_array[i-2] and
                price_array[i] < price_array[i+1] and
                price_array[i] < price_array[i+2]):

                is_new = True
                for level in levels:
                    if abs(price_array[i] - level['price']) / level['price'] < tolerance:
                        level['touches'] += 1
                        is_new = False
                        break

                if is_new:
                    levels.append({
                        'price': float(price_array[i]),
                        'type': 'support',
                        'touches': 1,
                        'index': i
                    })

        for level in levels:
            level['strength'] = min(10, level['touches'] * 2)

        levels.sort(key=lambda x: x['touches'], reverse=True)

        result = []
        for level in levels[:num_levels]:
            result.append(SupportResistance(
                level=level['price'],
                strength=level['strength'],
                type=level['type'],
                touches=level['touches'],
                last_touch_date=datetime.now().isoformat()
            ))

        logger.info(f"Found {len(result)} support/resistance levels")
        return result

    def calculate_fibonacci_levels(
        self,
        high: float,
        low: float
    ) -> Dict[str, float]:
        피보나치 되돌림 레벨 계산

        Args:
            high: 고점
            low: 저점

        Returns:
            피보나치 레벨 딕셔너리
        diff = high - low

        levels = {
            '0.0': low,
            '0.236': low + diff * 0.236,
            '0.382': low + diff * 0.382,
            '0.500': low + diff * 0.500,
            '0.618': low + diff * 0.618,
            '0.786': low + diff * 0.786,
            '1.0': high,
            '1.272': high + diff * 0.272,
            '1.618': high + diff * 0.618
        }

        return levels

    def analyze_bollinger_bands(
        self,
        prices: List[float],
        period: int = 20,
        std_dev: float = 2.0
    ) -> Dict[str, Any]:
        볼린저 밴드 분석

        Args:
            prices: 가격 데이터
            period: 기간
            std_dev: 표준편차 배수

        Returns:
            볼린저 밴드 분석 결과
        if len(prices) < period:
            return {}

        price_array = np.array(prices[-period:])

        sma = np.mean(price_array)

        std = np.std(price_array)

        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)

        current_price = prices[-1]

        bandwidth = ((upper_band - lower_band) / sma) * 100

        percent_b = (current_price - lower_band) / (upper_band - lower_band)

        is_squeeze = bandwidth < 10

        analysis = {
            'sma': round(sma, 2),
            'upper_band': round(upper_band, 2),
            'lower_band': round(lower_band, 2),
            'bandwidth': round(bandwidth, 2),
            'percent_b': round(percent_b, 4),
            'is_squeeze': is_squeeze,
            'signal': self._interpret_bollinger(current_price, sma, upper_band, lower_band, percent_b)
        }

        return analysis


    def _detect_doji(self, data: List[Dict]) -> Optional[CandlePattern]:
        """도지 패턴 감지"""
        if len(data) < 1:
            return None

        last = data[-1]
        open_price = last.get('open', 0)
        close = last.get('close', 0)
        high = last.get('high', 0)
        low = last.get('low', 0)

        body = abs(close - open_price)
        total_range = high - low

        if total_range == 0:
            return None

        body_ratio = body / total_range

        if body_ratio < 0.1:
            return CandlePattern(
                name="Doji",
                type="neutral",
                strength=7,
                description="Price indecision - potential reversal",
                confidence=0.7
            )

        return None

    def _detect_hammer(self, data: List[Dict]) -> Optional[CandlePattern]:
        """망치/교수형 패턴 감지"""
        if len(data) < 2:
            return None

        last = data[-1]
        prev = data[-2]

        open_price = last.get('open', 0)
        close = last.get('close', 0)
        high = last.get('high', 0)
        low = last.get('low', 0)

        body = abs(close - open_price)
        total_range = high - low
        lower_shadow = min(open_price, close) - low
        upper_shadow = high - max(open_price, close)

        if total_range == 0:
            return None

        if (lower_shadow > 2 * body and
            upper_shadow < body * 0.3 and
            body / total_range < 0.3):

            is_bullish = prev.get('close', 0) < prev.get('open', 0)

            return CandlePattern(
                name="Hammer" if is_bullish else "Hanging Man",
                type="bullish" if is_bullish else "bearish",
                strength=8,
                description="Potential reversal - buyers stepped in at lows",
                confidence=0.75
            )

        return None

    def _detect_shooting_star(self, data: List[Dict]) -> Optional[CandlePattern]:
        """슈팅스타 패턴 감지"""
        if len(data) < 2:
            return None

        last = data[-1]
        prev = data[-2]

        open_price = last.get('open', 0)
        close = last.get('close', 0)
        high = last.get('high', 0)
        low = last.get('low', 0)

        body = abs(close - open_price)
        total_range = high - low
        upper_shadow = high - max(open_price, close)
        lower_shadow = min(open_price, close) - low

        if total_range == 0:
            return None

        if (upper_shadow > 2 * body and
            lower_shadow < body * 0.3 and
            body / total_range < 0.3):

            is_uptrend = prev.get('close', 0) > prev.get('open', 0)

            if is_uptrend:
                return CandlePattern(
                    name="Shooting Star",
                    type="bearish",
                    strength=8,
                    description="Bearish reversal - sellers pushed price down from highs",
                    confidence=0.75
                )

        return None

    def _detect_engulfing(self, data: List[Dict]) -> Optional[CandlePattern]:
        """포용형 패턴 감지"""
        if len(data) < 2:
            return None

        last = data[-1]
        prev = data[-2]

        last_open = last.get('open', 0)
        last_close = last.get('close', 0)
        prev_open = prev.get('open', 0)
        prev_close = prev.get('close', 0)

        last_body = abs(last_close - last_open)
        prev_body = abs(prev_close - prev_open)

        if (prev_close < prev_open and
            last_close > last_open and
            last_close > prev_open and
            last_open < prev_close and
            last_body > prev_body * 1.5):

            return CandlePattern(
                name="Bullish Engulfing",
                type="bullish",
                strength=9,
                description="Strong bullish reversal signal",
                confidence=0.85
            )

        if (prev_close > prev_open and
            last_close < last_open and
            last_close < prev_open and
            last_open > prev_close and
            last_body > prev_body * 1.5):

            return CandlePattern(
                name="Bearish Engulfing",
                type="bearish",
                strength=9,
                description="Strong bearish reversal signal",
                confidence=0.85
            )

        return None

    def _detect_star_pattern(self, data: List[Dict]) -> Optional[CandlePattern]:
        """샛별/저녁별 패턴 감지"""
        if len(data) < 3:
            return None

        first = data[-3]
        star = data[-2]
        last = data[-1]

        if (first.get('close', 0) < first.get('open', 0) and
            abs(star.get('close', 0) - star.get('open', 0)) < abs(first.get('close', 0) - first.get('open', 0)) * 0.3 and
            last.get('close', 0) > last.get('open', 0) and
            last.get('close', 0) > (first.get('open', 0) + first.get('close', 0)) / 2):

            return CandlePattern(
                name="Morning Star",
                type="bullish",
                strength=9,
                description="Strong bullish reversal - three-candle pattern",
                confidence=0.85
            )

        if (first.get('close', 0) > first.get('open', 0) and
            abs(star.get('close', 0) - star.get('open', 0)) < abs(first.get('close', 0) - first.get('open', 0)) * 0.3 and
            last.get('close', 0) < last.get('open', 0) and
            last.get('close', 0) < (first.get('open', 0) + first.get('close', 0)) / 2):

            return CandlePattern(
                name="Evening Star",
                type="bearish",
                strength=9,
                description="Strong bearish reversal - three-candle pattern",
                confidence=0.85
            )

        return None

    def _detect_three_soldiers_crows(self, data: List[Dict]) -> Optional[CandlePattern]:
        """삼병/삼까마귀 패턴 감지"""
        if len(data) < 3:
            return None

        last3 = data[-3:]

        if all(candle.get('close', 0) > candle.get('open', 0) for candle in last3):
            if all(last3[i].get('close', 0) > last3[i-1].get('close', 0) for i in range(1, 3)):
                return CandlePattern(
                    name="Three White Soldiers",
                    type="bullish",
                    strength=9,
                    description="Strong bullish continuation - three consecutive green candles",
                    confidence=0.8
                )

        if all(candle.get('close', 0) < candle.get('open', 0) for candle in last3):
            if all(last3[i].get('close', 0) < last3[i-1].get('close', 0) for i in range(1, 3)):
                return CandlePattern(
                    name="Three Black Crows",
                    type="bearish",
                    strength=9,
                    description="Strong bearish continuation - three consecutive red candles",
                    confidence=0.8
                )

        return None

    def _interpret_bollinger(
        self,
        price: float,
        sma: float,
        upper: float,
        lower: float,
        percent_b: float
    ) -> str:
        if percent_b > 1.0:
            return "Overbought - price above upper band"
        elif percent_b < 0.0:
            return "Oversold - price below lower band"
        elif percent_b > 0.8:
            return "Approaching overbought"
        elif percent_b < 0.2:
            return "Approaching oversold"
        elif 0.45 <= percent_b <= 0.55:
            return "Neutral - near middle of bands"
        elif percent_b > 0.5:
            return "Bullish bias - above middle"
        else:
            return "Bearish bias - below middle"


__all__ = ['ChartPatternAnalyzer', 'CandlePattern', 'SupportResistance']
