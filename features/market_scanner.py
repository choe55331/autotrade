"""
Real-Time Market Scanner - v5.14
Advanced market scanning with anomaly detection, pattern recognition, and opportunity discovery
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import logging
from collections import deque

logger = logging.getLogger(__name__)


class ScannerSignal(Enum):
    """스캐너 시그널 타입"""
    VOLUME_SPIKE = "volume_spike"
    PRICE_BREAKOUT = "price_breakout"
    UNUSUAL_VOLATILITY = "unusual_volatility"
    LARGE_ORDER = "large_order"
    MOMENTUM_SHIFT = "momentum_shift"
    PATTERN_DETECTED = "pattern_detected"
    CORRELATION_BREAK = "correlation_break"
    ARBITRAGE_OPPORTUNITY = "arbitrage_opportunity"


class SignalStrength(Enum):
    """시그널 강도"""
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    VERY_STRONG = 4


@dataclass
class MarketSignal:
    """시장 시그널"""
    signal_id: str
    stock_code: str
    stock_name: str
    signal_type: ScannerSignal
    strength: SignalStrength
    confidence: float  # 0-1
    current_price: float
    trigger_value: float
    reference_value: float
    deviation_percent: float
    timestamp: str
    metadata: Dict[str, Any]


@dataclass
class ScannerStatistics:
    """스캐너 통계"""
    total_signals: int
    signals_by_type: Dict[str, int]
    signals_by_strength: Dict[str, int]
    avg_confidence: float
    stocks_scanned: int
    scan_duration_ms: float
    opportunities_found: int


class MarketScanner:
    """
    실시간 시장 스캐너

    Features:
    - Volume spike detection
    - Price breakout detection
    - Unusual volatility detection
    - Pattern recognition
    - Momentum shift detection
    - Correlation analysis
    - Opportunity discovery
    """

    def __init__(self,
                 volume_spike_threshold: float = 2.0,
                 volatility_threshold: float = 2.5,
                 breakout_lookback: int = 20,
                 scan_interval_seconds: int = 60):
        """
        Args:
            volume_spike_threshold: 거래량 급증 임계값 (평균 대비 배수)
            volatility_threshold: 변동성 임계값 (표준편차 배수)
            breakout_lookback: 돌파 감지 기간 (일)
            scan_interval_seconds: 스캔 간격 (초)
        """
        self.volume_spike_threshold = volume_spike_threshold
        self.volatility_threshold = volatility_threshold
        self.breakout_lookback = breakout_lookback
        self.scan_interval_seconds = scan_interval_seconds

        # Signal history
        self.signal_history: deque = deque(maxlen=1000)
        self.last_scan_time: Optional[datetime] = None

        # Statistics
        self.stats = {
            'total_signals': 0,
            'signals_by_type': {},
            'signals_by_strength': {}
        }

        logger.info(f"Market Scanner initialized: "
                   f"volume_threshold={volume_spike_threshold}, "
                   f"volatility_threshold={volatility_threshold}")

    def scan_market(self,
                    market_data: Dict[str, Dict[str, Any]],
                    price_histories: Dict[str, List[Dict[str, Any]]]) -> List[MarketSignal]:
        """
        시장 스캔

        Args:
            market_data: 실시간 시장 데이터
                {
                    'stock_code': {
                        'price': float,
                        'volume': int,
                        'bid': float,
                        'ask': float,
                        ...
                    }
                }
            price_histories: 가격 히스토리
                {
                    'stock_code': [
                        {'date': str, 'open': float, 'high': float, 'low': float, 'close': float, 'volume': int},
                        ...
                    ]
                }

        Returns:
            List[MarketSignal]
        """
        scan_start = datetime.now()
        signals = []

        logger.info(f"Scanning {len(market_data)} stocks...")

        for stock_code, current_data in market_data.items():
            if stock_code not in price_histories:
                continue

            history = price_histories[stock_code]
            if len(history) < 20:
                continue

            stock_name = current_data.get('stock_name', stock_code)

            # Check multiple signals
            stock_signals = []

            # 1. Volume spike
            vol_signal = self._detect_volume_spike(
                stock_code, stock_name, current_data, history
            )
            if vol_signal:
                stock_signals.append(vol_signal)

            # 2. Price breakout
            breakout_signal = self._detect_price_breakout(
                stock_code, stock_name, current_data, history
            )
            if breakout_signal:
                stock_signals.append(breakout_signal)

            # 3. Unusual volatility
            vol_signal = self._detect_unusual_volatility(
                stock_code, stock_name, current_data, history
            )
            if vol_signal:
                stock_signals.append(vol_signal)

            # 4. Momentum shift
            momentum_signal = self._detect_momentum_shift(
                stock_code, stock_name, current_data, history
            )
            if momentum_signal:
                stock_signals.append(momentum_signal)

            # 5. Pattern detection
            pattern_signal = self._detect_patterns(
                stock_code, stock_name, current_data, history
            )
            if pattern_signal:
                stock_signals.append(pattern_signal)

            signals.extend(stock_signals)

        # Update statistics
        self._update_statistics(signals)
        self.last_scan_time = datetime.now()

        scan_duration = (datetime.now() - scan_start).total_seconds() * 1000

        logger.info(f"Scan complete: {len(signals)} signals found in {scan_duration:.0f}ms")

        return signals

    def get_top_opportunities(self,
                             signals: List[MarketSignal],
                             min_confidence: float = 0.7,
                             min_strength: SignalStrength = SignalStrength.MODERATE,
                             top_n: int = 10) -> List[MarketSignal]:
        """
        상위 기회 추출

        Args:
            signals: 시그널 목록
            min_confidence: 최소 신뢰도
            min_strength: 최소 강도
            top_n: 상위 N개

        Returns:
            List[MarketSignal]
        """
        # Filter by confidence and strength
        filtered = [
            s for s in signals
            if s.confidence >= min_confidence and s.strength.value >= min_strength.value
        ]

        # Sort by confidence * strength
        sorted_signals = sorted(
            filtered,
            key=lambda s: s.confidence * s.strength.value,
            reverse=True
        )

        return sorted_signals[:top_n]

    def get_statistics(self) -> ScannerStatistics:
        """스캐너 통계"""
        total = self.stats['total_signals']

        avg_confidence = 0.0
        if self.signal_history:
            avg_confidence = np.mean([s.confidence for s in self.signal_history])

        return ScannerStatistics(
            total_signals=total,
            signals_by_type=self.stats['signals_by_type'].copy(),
            signals_by_strength=self.stats['signals_by_strength'].copy(),
            avg_confidence=avg_confidence,
            stocks_scanned=0,  # Updated during scan
            scan_duration_ms=0,  # Updated during scan
            opportunities_found=len([s for s in self.signal_history if s.confidence > 0.7])
        )

    # ===== DETECTION METHODS =====

    def _detect_volume_spike(self, stock_code: str, stock_name: str,
                            current_data: Dict[str, Any],
                            history: List[Dict[str, Any]]) -> Optional[MarketSignal]:
        """거래량 급증 감지"""
        current_volume = current_data.get('volume', 0)
        if current_volume == 0:
            return None

        # Calculate average volume (20 days)
        recent_volumes = [h['volume'] for h in history[-20:] if h.get('volume', 0) > 0]
        if not recent_volumes:
            return None

        avg_volume = np.mean(recent_volumes)
        if avg_volume == 0:
            return None

        volume_ratio = current_volume / avg_volume

        # Check threshold
        if volume_ratio < self.volume_spike_threshold:
            return None

        # Determine strength
        if volume_ratio > 5.0:
            strength = SignalStrength.VERY_STRONG
            confidence = 0.95
        elif volume_ratio > 3.0:
            strength = SignalStrength.STRONG
            confidence = 0.85
        elif volume_ratio > 2.0:
            strength = SignalStrength.MODERATE
            confidence = 0.75
        else:
            strength = SignalStrength.WEAK
            confidence = 0.60

        signal = MarketSignal(
            signal_id=f"vol_spike_{stock_code}_{int(datetime.now().timestamp())}",
            stock_code=stock_code,
            stock_name=stock_name,
            signal_type=ScannerSignal.VOLUME_SPIKE,
            strength=strength,
            confidence=confidence,
            current_price=current_data.get('price', 0),
            trigger_value=current_volume,
            reference_value=avg_volume,
            deviation_percent=(volume_ratio - 1) * 100,
            timestamp=datetime.now().isoformat(),
            metadata={
                'volume_ratio': volume_ratio,
                '20d_avg_volume': avg_volume
            }
        )

        return signal

    def _detect_price_breakout(self, stock_code: str, stock_name: str,
                               current_data: Dict[str, Any],
                               history: List[Dict[str, Any]]) -> Optional[MarketSignal]:
        """가격 돌파 감지"""
        current_price = current_data.get('price', 0)
        if current_price == 0:
            return None

        lookback = min(self.breakout_lookback, len(history))
        if lookback < 10:
            return None

        recent_history = history[-lookback:]
        highs = [h['high'] for h in recent_history]
        lows = [h['low'] for h in recent_history]

        resistance = max(highs)
        support = min(lows)

        # Upward breakout
        if current_price > resistance * 1.01:  # 1% above resistance
            breakout_pct = ((current_price - resistance) / resistance) * 100

            if breakout_pct > 5:
                strength = SignalStrength.VERY_STRONG
                confidence = 0.90
            elif breakout_pct > 3:
                strength = SignalStrength.STRONG
                confidence = 0.80
            elif breakout_pct > 1:
                strength = SignalStrength.MODERATE
                confidence = 0.70
            else:
                strength = SignalStrength.WEAK
                confidence = 0.60

            return MarketSignal(
                signal_id=f"breakout_up_{stock_code}_{int(datetime.now().timestamp())}",
                stock_code=stock_code,
                stock_name=stock_name,
                signal_type=ScannerSignal.PRICE_BREAKOUT,
                strength=strength,
                confidence=confidence,
                current_price=current_price,
                trigger_value=current_price,
                reference_value=resistance,
                deviation_percent=breakout_pct,
                timestamp=datetime.now().isoformat(),
                metadata={
                    'direction': 'upward',
                    'resistance': resistance,
                    'support': support
                }
            )

        # Downward breakout
        elif current_price < support * 0.99:  # 1% below support
            breakout_pct = ((support - current_price) / support) * 100

            strength = SignalStrength.MODERATE if breakout_pct > 2 else SignalStrength.WEAK
            confidence = 0.70 if breakout_pct > 2 else 0.60

            return MarketSignal(
                signal_id=f"breakout_down_{stock_code}_{int(datetime.now().timestamp())}",
                stock_code=stock_code,
                stock_name=stock_name,
                signal_type=ScannerSignal.PRICE_BREAKOUT,
                strength=strength,
                confidence=confidence,
                current_price=current_price,
                trigger_value=current_price,
                reference_value=support,
                deviation_percent=-breakout_pct,
                timestamp=datetime.now().isoformat(),
                metadata={
                    'direction': 'downward',
                    'resistance': resistance,
                    'support': support
                }
            )

        return None

    def _detect_unusual_volatility(self, stock_code: str, stock_name: str,
                                   current_data: Dict[str, Any],
                                   history: List[Dict[str, Any]]) -> Optional[MarketSignal]:
        """비정상 변동성 감지"""
        if len(history) < 20:
            return None

        # Calculate recent volatility
        recent_closes = [h['close'] for h in history[-20:]]
        returns = np.diff(recent_closes) / recent_closes[:-1]

        # Current intraday volatility
        current_high = current_data.get('high', current_data.get('price', 0))
        current_low = current_data.get('low', current_data.get('price', 0))
        current_price = current_data.get('price', 0)

        if current_price == 0 or current_high == current_low:
            return None

        intraday_range = (current_high - current_low) / current_price

        # Historical average range
        avg_range = np.mean([(h['high'] - h['low']) / h['close'] for h in history[-20:]])

        if avg_range == 0:
            return None

        range_ratio = intraday_range / avg_range

        # Check threshold
        if range_ratio < self.volatility_threshold:
            return None

        # Determine strength
        if range_ratio > 4.0:
            strength = SignalStrength.VERY_STRONG
            confidence = 0.90
        elif range_ratio > 3.0:
            strength = SignalStrength.STRONG
            confidence = 0.80
        elif range_ratio > 2.5:
            strength = SignalStrength.MODERATE
            confidence = 0.70
        else:
            strength = SignalStrength.WEAK
            confidence = 0.60

        return MarketSignal(
            signal_id=f"volatility_{stock_code}_{int(datetime.now().timestamp())}",
            stock_code=stock_code,
            stock_name=stock_name,
            signal_type=ScannerSignal.UNUSUAL_VOLATILITY,
            strength=strength,
            confidence=confidence,
            current_price=current_price,
            trigger_value=intraday_range,
            reference_value=avg_range,
            deviation_percent=(range_ratio - 1) * 100,
            timestamp=datetime.now().isoformat(),
            metadata={
                'range_ratio': range_ratio,
                'intraday_range_pct': intraday_range * 100,
                'avg_range_pct': avg_range * 100
            }
        )

    def _detect_momentum_shift(self, stock_code: str, stock_name: str,
                               current_data: Dict[str, Any],
                               history: List[Dict[str, Any]]) -> Optional[MarketSignal]:
        """모멘텀 전환 감지"""
        if len(history) < 10:
            return None

        closes = np.array([h['close'] for h in history[-10:]])

        # Calculate short-term momentum
        short_returns = (closes[-1] - closes[-3]) / closes[-3]

        # Calculate medium-term momentum
        medium_returns = (closes[-3] - closes[0]) / closes[0]

        # Momentum shift detection
        # Positive shift: short-term reverses from negative medium-term
        if short_returns > 0.02 and medium_returns < -0.05:
            strength = SignalStrength.STRONG if short_returns > 0.05 else SignalStrength.MODERATE
            confidence = 0.75

            return MarketSignal(
                signal_id=f"momentum_up_{stock_code}_{int(datetime.now().timestamp())}",
                stock_code=stock_code,
                stock_name=stock_name,
                signal_type=ScannerSignal.MOMENTUM_SHIFT,
                strength=strength,
                confidence=confidence,
                current_price=current_data.get('price', 0),
                trigger_value=short_returns,
                reference_value=medium_returns,
                deviation_percent=short_returns * 100,
                timestamp=datetime.now().isoformat(),
                metadata={
                    'direction': 'upward',
                    'short_term_return': short_returns * 100,
                    'medium_term_return': medium_returns * 100
                }
            )

        # Negative shift: short-term reverses from positive medium-term
        elif short_returns < -0.02 and medium_returns > 0.05:
            strength = SignalStrength.MODERATE
            confidence = 0.70

            return MarketSignal(
                signal_id=f"momentum_down_{stock_code}_{int(datetime.now().timestamp())}",
                stock_code=stock_code,
                stock_name=stock_name,
                signal_type=ScannerSignal.MOMENTUM_SHIFT,
                strength=strength,
                confidence=confidence,
                current_price=current_data.get('price', 0),
                trigger_value=short_returns,
                reference_value=medium_returns,
                deviation_percent=short_returns * 100,
                timestamp=datetime.now().isoformat(),
                metadata={
                    'direction': 'downward',
                    'short_term_return': short_returns * 100,
                    'medium_term_return': medium_returns * 100
                }
            )

        return None

    def _detect_patterns(self, stock_code: str, stock_name: str,
                        current_data: Dict[str, Any],
                        history: List[Dict[str, Any]]) -> Optional[MarketSignal]:
        """차트 패턴 감지"""
        if len(history) < 5:
            return None

        recent = history[-5:]
        closes = [h['close'] for h in recent]

        # Simple pattern: Higher lows (bullish)
        lows = [h['low'] for h in recent]
        if all(lows[i] <= lows[i+1] for i in range(len(lows)-1)):
            strength = SignalStrength.MODERATE
            confidence = 0.65

            return MarketSignal(
                signal_id=f"pattern_bullish_{stock_code}_{int(datetime.now().timestamp())}",
                stock_code=stock_code,
                stock_name=stock_name,
                signal_type=ScannerSignal.PATTERN_DETECTED,
                strength=strength,
                confidence=confidence,
                current_price=current_data.get('price', 0),
                trigger_value=lows[-1],
                reference_value=lows[0],
                deviation_percent=((lows[-1] - lows[0]) / lows[0]) * 100,
                timestamp=datetime.now().isoformat(),
                metadata={
                    'pattern_type': 'higher_lows',
                    'direction': 'bullish'
                }
            )

        # Simple pattern: Lower highs (bearish)
        highs = [h['high'] for h in recent]
        if all(highs[i] >= highs[i+1] for i in range(len(highs)-1)):
            strength = SignalStrength.MODERATE
            confidence = 0.65

            return MarketSignal(
                signal_id=f"pattern_bearish_{stock_code}_{int(datetime.now().timestamp())}",
                stock_code=stock_code,
                stock_name=stock_name,
                signal_type=ScannerSignal.PATTERN_DETECTED,
                strength=strength,
                confidence=confidence,
                current_price=current_data.get('price', 0),
                trigger_value=highs[-1],
                reference_value=highs[0],
                deviation_percent=((highs[-1] - highs[0]) / highs[0]) * 100,
                timestamp=datetime.now().isoformat(),
                metadata={
                    'pattern_type': 'lower_highs',
                    'direction': 'bearish'
                }
            )

        return None

    def _update_statistics(self, signals: List[MarketSignal]):
        """통계 업데이트"""
        self.stats['total_signals'] += len(signals)

        for signal in signals:
            # By type
            signal_type = signal.signal_type.value
            self.stats['signals_by_type'][signal_type] = \
                self.stats['signals_by_type'].get(signal_type, 0) + 1

            # By strength
            strength = signal.strength.name
            self.stats['signals_by_strength'][strength] = \
                self.stats['signals_by_strength'].get(strength, 0) + 1

            # Add to history
            self.signal_history.append(signal)


# Global singleton
_market_scanner: Optional[MarketScanner] = None


def get_market_scanner() -> MarketScanner:
    """마켓 스캐너 싱글톤"""
    global _market_scanner
    if _market_scanner is None:
        _market_scanner = MarketScanner(
            volume_spike_threshold=2.0,
            volatility_threshold=2.5,
            breakout_lookback=20,
            scan_interval_seconds=60
        )
    return _market_scanner
