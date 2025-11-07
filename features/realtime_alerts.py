"""
features/realtime_alerts.py
실시간 알림 시스템 (v5.10 NEW)
"""

Features:
- 가격 알림 (목표가 도달, 손절가 도달)
- 패턴 알림 (캔들 패턴, 지지/저항 터치)
- 거래량 급증 알림
- AI 신호 알림
- WebSocket을 통한 실시간 푸시
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
from threading import Lock

from utils.logger_new import get_logger

logger = get_logger()


class AlertType(Enum):
    """알림 유형"""
    PRICE_TARGET = "price_target"
    STOP_LOSS = "stop_loss"
    VOLUME_SURGE = "volume_surge"
    PATTERN_DETECTED = "pattern_detected"
    SUPPORT_RESISTANCE = "support_resistance"
    AI_SIGNAL = "ai_signal"
    NEWS = "news"
    PORTFOLIO_RISK = "portfolio_risk"
    MARKET_CHANGE = "market_change"


class AlertPriority(Enum):
    """알림 우선순위"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Alert:
    """알림 데이터 클래스"""
    id: str
    type: AlertType
    priority: AlertPriority
    title: str
    message: str
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
    current_price: Optional[float] = None
    target_price: Optional[float] = None
    action_required: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_read: bool = False
    is_dismissed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'type': self.type.value,
            'priority': self.priority.value,
            'title': self.title,
            'message': self.message,
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'current_price': self.current_price,
            'target_price': self.target_price,
            'action_required': self.action_required,
            'timestamp': self.timestamp,
            'metadata': self.metadata,
            'is_read': self.is_read,
            'is_dismissed': self.is_dismissed
        }


class RealtimeAlertSystem:
    """
    실시간 알림 시스템 (v5.10)

    Features:
    - 다양한 유형의 알림 관리
    - 우선순위 기반 알림
    - WebSocket 실시간 푸시
    - 알림 히스토리 관리
    - 중복 알림 방지
    """

    def __init__(self, max_history: int = 100):
        """
        초기화

        Args:
            max_history: 최대 히스토리 보관 개수
        """
        self.alerts: List[Alert] = []
        self.alert_history: List[Alert] = []
        self.max_history = max_history

        self.callbacks: List[Callable] = []

        self.dedup_cache: Dict[str, datetime] = {}
        self.dedup_ttl = 300

        self.lock = Lock()

        logger.info("Realtime Alert System initialized (v5.10)")

    def register_callback(self, callback: Callable):
        """
        알림 콜백 등록 (WebSocket broadcast용)

        Args:
            callback: 알림 발생 시 호출할 함수
        """
        self.callbacks.append(callback)
        logger.info(f"Alert callback registered: {callback.__name__}")

    def create_alert(
        self,
        alert_type: AlertType,
        priority: AlertPriority,
        title: str,
        message: str,
        **kwargs
    ) -> Alert:
        새 알림 생성 및 발송

        Args:
            alert_type: 알림 유형
            priority: 우선순위
            title: 제목
            message: 메시지
            **kwargs: 추가 파라미터 (stock_code, current_price 등)

        Returns:
            생성된 알림 객체
        if not self._should_create_alert(alert_type, kwargs.get('stock_code'), kwargs.get('current_price')):
            logger.debug(f"Duplicate alert skipped: {alert_type.value} for {kwargs.get('stock_code')}")
            return None

        alert_id = f"{alert_type.value}_{int(datetime.now().timestamp() * 1000)}"

        alert = Alert(
            id=alert_id,
            type=alert_type,
            priority=priority,
            title=title,
            message=message,
            **kwargs
        )

        with self.lock:
            self.alerts.append(alert)

            self.alert_history.append(alert)
            if len(self.alert_history) > self.max_history:
                self.alert_history.pop(0)

        self._trigger_callbacks(alert)

        logger.info(f"Alert created: [{priority.value}] {title}")
        return alert

    def price_target_alert(
        self,
        stock_code: str,
        stock_name: str,
        current_price: float,
        target_price: float,
        direction: str = "reached"
    ):
        목표가 도달 알림

        Args:
            stock_code: 종목 코드
            stock_name: 종목명
            current_price: 현재가
            target_price: 목표가
            direction: "reached", "above", "below"
        message = f"{stock_name} ({stock_code})의 현재가 {current_price:,}원이 목표가 {target_price:,}원에 도달했습니다."

        if direction == "above":
            message = f"{stock_name} ({stock_code})의 현재가 {current_price:,}원이 목표가 {target_price:,}원을 돌파했습니다."
        elif direction == "below":
            message = f"{stock_name} ({stock_code})의 현재가 {current_price:,}원이 목표가 {target_price:,}원 아래로 하락했습니다."

        return self.create_alert(
            alert_type=AlertType.PRICE_TARGET,
            priority=AlertPriority.HIGH,
            title=f"[TARGET] 목표가 도달: {stock_name}",
            message=message,
            stock_code=stock_code,
            stock_name=stock_name,
            current_price=current_price,
            target_price=target_price,
            action_required="익절 또는 추가 매수 검토"
        )

    def stop_loss_alert(
        self,
        stock_code: str,
        stock_name: str,
        current_price: float,
        stop_loss_price: float,
        loss_percent: float
    ):
        손절가 도달 알림

        Args:
            stock_code: 종목 코드
            stock_name: 종목명
            current_price: 현재가
            stop_loss_price: 손절가
            loss_percent: 손실률 (%)
        message = f"{stock_name} ({stock_code})의 현재가 {current_price:,}원이 손절가 {stop_loss_price:,}원에 도달했습니다. (손실: {loss_percent:.1f}%)"

        return self.create_alert(
            alert_type=AlertType.STOP_LOSS,
            priority=AlertPriority.CRITICAL,
            title=f"🔴 손절가 도달: {stock_name}",
            message=message,
            stock_code=stock_code,
            stock_name=stock_name,
            current_price=current_price,
            target_price=stop_loss_price,
            action_required="즉시 매도 검토",
            metadata={'loss_percent': loss_percent}
        )

    def volume_surge_alert(
        self,
        stock_code: str,
        stock_name: str,
        current_volume: int,
        avg_volume: int,
        surge_ratio: float
    ):
        거래량 급증 알림

        Args:
            stock_code: 종목 코드
            stock_name: 종목명
            current_volume: 현재 거래량
            avg_volume: 평균 거래량
            surge_ratio: 급증 비율
        message = f"{stock_name} ({stock_code})의 거래량이 평균 대비 {surge_ratio:.1f}배 급증했습니다. (현재: {current_volume:,}주, 평균: {avg_volume:,}주)"

        return self.create_alert(
            alert_type=AlertType.VOLUME_SURGE,
            priority=AlertPriority.HIGH,
            title=f"[CHART] 거래량 급증: {stock_name}",
            message=message,
            stock_code=stock_code,
            stock_name=stock_name,
            action_required="급등/급락 가능성 - 주시 필요",
            metadata={
                'current_volume': current_volume,
                'avg_volume': avg_volume,
                'surge_ratio': surge_ratio
            }
        )

    def pattern_detected_alert(
        self,
        stock_code: str,
        stock_name: str,
        pattern_name: str,
        pattern_type: str,
        strength: int,
        description: str
    ):
        차트 패턴 감지 알림

        Args:
            stock_code: 종목 코드
            stock_name: 종목명
            pattern_name: 패턴명
            pattern_type: 패턴 유형 (bullish/bearish)
            strength: 강도 (1-10)
            description: 설명
        icon = "🟢" if pattern_type == "bullish" else "🔴" if pattern_type == "bearish" else "⚪"
        message = f"{stock_name} ({stock_code})에서 {pattern_name} 패턴이 감지되었습니다. (강도: {strength}/10)\n{description}"

        priority = AlertPriority.HIGH if strength >= 8 else AlertPriority.MEDIUM

        return self.create_alert(
            alert_type=AlertType.PATTERN_DETECTED,
            priority=priority,
            title=f"{icon} 패턴 감지: {pattern_name} - {stock_name}",
            message=message,
            stock_code=stock_code,
            stock_name=stock_name,
            action_required=f"{'매수' if pattern_type == 'bullish' else '매도'} 기회 검토",
            metadata={
                'pattern_name': pattern_name,
                'pattern_type': pattern_type,
                'strength': strength
            }
        )

    def support_resistance_alert(
        self,
        stock_code: str,
        stock_name: str,
        current_price: float,
        level_price: float,
        level_type: str,
        strength: int
    ):
        지지/저항 레벨 터치 알림

        Args:
            stock_code: 종목 코드
            stock_name: 종목명
            current_price: 현재가
            level_price: 지지/저항 가격
            level_type: 'support' or 'resistance'
            strength: 레벨 강도 (1-10)
        level_name = "지지선" if level_type == "support" else "저항선"
        message = f"{stock_name} ({stock_code})의 현재가 {current_price:,}원이 주요 {level_name} {level_price:,}원에 근접했습니다. (강도: {strength}/10)"

        return self.create_alert(
            alert_type=AlertType.SUPPORT_RESISTANCE,
            priority=AlertPriority.MEDIUM,
            title=f"📍 {level_name} 터치: {stock_name}",
            message=message,
            stock_code=stock_code,
            stock_name=stock_name,
            current_price=current_price,
            target_price=level_price,
            action_required=f"{level_name} {'반등' if level_type == 'support' else '돌파'} 여부 주시",
            metadata={
                'level_type': level_type,
                'strength': strength
            }
        )

    def ai_signal_alert(
        self,
        stock_code: str,
        stock_name: str,
        signal: str,
        confidence: str,
        score: float,
        reasoning: str
    ):
        AI 매매 신호 알림

        Args:
            stock_code: 종목 코드
            stock_name: 종목명
            signal: 신호 (BUY/SELL/HOLD)
            confidence: 신뢰도
            score: 점수
            reasoning: 근거
        icon = "🟢" if signal == "BUY" or signal.startswith("BUY") else "🔴" if signal == "SELL" or signal.startswith("SELL") else "⚪"

        priority_map = {
            "STRONG_BUY": AlertPriority.CRITICAL,
            "BUY": AlertPriority.HIGH,
            "WEAK_BUY": AlertPriority.MEDIUM,
            "HOLD": AlertPriority.LOW,
            "WEAK_SELL": AlertPriority.MEDIUM,
            "SELL": AlertPriority.HIGH,
            "STRONG_SELL": AlertPriority.CRITICAL
        }

        priority = priority_map.get(signal, AlertPriority.MEDIUM)

        message = f"{stock_name} ({stock_code}) AI 분석 결과:\n신호: {signal}\n신뢰도: {confidence}\n점수: {score}/10\n\n{reasoning[:200]}..."

        return self.create_alert(
            alert_type=AlertType.AI_SIGNAL,
            priority=priority,
            title=f"{icon} AI 신호: {signal} - {stock_name}",
            message=message,
            stock_code=stock_code,
            stock_name=stock_name,
            action_required=f"AI {signal} 신호 - 매매 검토",
            metadata={
                'signal': signal,
                'confidence': confidence,
                'score': score
            }
        )

    def portfolio_risk_alert(
        self,
        risk_level: str,
        message: str,
        affected_stocks: List[str] = None
    ):
        포트폴리오 리스크 알림

        Args:
            risk_level: 리스크 레벨 (High/Medium/Low)
            message: 메시지
            affected_stocks: 영향받는 종목 리스트
        priority = AlertPriority.CRITICAL if risk_level == "High" else AlertPriority.HIGH

        return self.create_alert(
            alert_type=AlertType.PORTFOLIO_RISK,
            priority=priority,
            title=f"[WARNING]️ 포트폴리오 리스크 경고: {risk_level}",
            message=message,
            action_required="포트폴리오 리밸런싱 검토",
            metadata={
                'risk_level': risk_level,
                'affected_stocks': affected_stocks or []
            }
        )

    def get_active_alerts(
        self,
        priority_filter: Optional[AlertPriority] = None,
        type_filter: Optional[AlertType] = None,
        unread_only: bool = False
    ) -> List[Alert]:
        활성 알림 조회

        Args:
            priority_filter: 우선순위 필터
            type_filter: 유형 필터
            unread_only: 읽지 않은 알림만

        Returns:
            알림 리스트
        with self.lock:
            filtered = [a for a in self.alerts if not a.is_dismissed]

            if priority_filter:
                filtered = [a for a in filtered if a.priority == priority_filter]

            if type_filter:
                filtered = [a for a in filtered if a.type == type_filter]

            if unread_only:
                filtered = [a for a in filtered if not a.is_read]

            return filtered

    def mark_as_read(self, alert_id: str):
        """알림을 읽음으로 표시"""
        with self.lock:
            for alert in self.alerts:
                if alert.id == alert_id:
                    alert.is_read = True
                    logger.debug(f"Alert marked as read: {alert_id}")
                    return True
        return False

    def dismiss_alert(self, alert_id: str):
        """알림 닫기"""
        with self.lock:
            for alert in self.alerts:
                if alert.id == alert_id:
                    alert.is_dismissed = True
                    logger.debug(f"Alert dismissed: {alert_id}")
                    return True
        return False

    def clear_all_alerts(self):
        """모든 알림 초기화"""
        with self.lock:
            self.alerts.clear()
            logger.info("All alerts cleared")


    def _should_create_alert(
        self,
        alert_type: AlertType,
        stock_code: Optional[str],
        price: Optional[float]
    ) -> bool:
        if not stock_code:
            return True

        cache_key = f"{stock_code}:{alert_type.value}:{int(price) if price else 0}"

        if cache_key in self.dedup_cache:
            last_time = self.dedup_cache[cache_key]
            elapsed = (datetime.now() - last_time).total_seconds()

            if elapsed < self.dedup_ttl:
                return False

        self.dedup_cache[cache_key] = datetime.now()

        self._clean_dedup_cache()

        return True

    def _clean_dedup_cache(self):
        """오래된 캐시 엔트리 정리"""
        now = datetime.now()
        keys_to_delete = []

        for key, timestamp in self.dedup_cache.items():
            if (now - timestamp).total_seconds() > self.dedup_ttl:
                keys_to_delete.append(key)

        for key in keys_to_delete:
            del self.dedup_cache[key]

    def _trigger_callbacks(self, alert: Alert):
        """등록된 콜백 실행"""
        for callback in self.callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")


_alert_system: Optional[RealtimeAlertSystem] = None


def get_alert_system() -> RealtimeAlertSystem:
    """싱글톤 알림 시스템 인스턴스 반환"""
    global _alert_system
    if _alert_system is None:
        _alert_system = RealtimeAlertSystem()
    return _alert_system


__all__ = [
    'RealtimeAlertSystem',
    'Alert',
    'AlertType',
    'AlertPriority',
    'get_alert_system'
]
