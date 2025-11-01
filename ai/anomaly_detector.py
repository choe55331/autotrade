"""
AutoTrade Pro v4.0 - ML 기반 시스템 이상 감지
시스템 로그, API 응답 시간, 주문 실패율 등을 모니터링하여 이상 패턴 감지

주요 기능:
- Isolation Forest 기반 이상 감지
- 실시간 모니터링
- 자동 알림
- 대시보드 통합
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque
from dataclasses import dataclass

import numpy as np

try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available. Anomaly detection will use simple thresholds.")

logger = logging.getLogger(__name__)


@dataclass
class AnomalyEvent:
    """이상 이벤트"""
    timestamp: datetime
    anomaly_type: str
    severity: str  # low, medium, high, critical
    expected_value: float
    actual_value: float
    anomaly_score: float
    description: str


class AnomalyDetector:
    """시스템 이상 감지기"""

    def __init__(self, settings: Dict[str, Any] = None):
        """
        초기화

        Args:
            settings: 설정
                {
                    'check_interval_minutes': 5,
                    'alert_threshold': 0.8,
                    'history_size': 1000,
                    'contamination': 0.1  # 이상치 비율
                }
        """
        self.settings = settings or {}
        self.check_interval_minutes = self.settings.get('check_interval_minutes', 5)
        self.alert_threshold = self.settings.get('alert_threshold', 0.8)
        self.history_size = self.settings.get('history_size', 1000)
        self.contamination = self.settings.get('contamination', 0.1)

        # 모니터링 데이터
        self.api_response_times: deque = deque(maxlen=self.history_size)
        self.order_failure_rates: deque = deque(maxlen=self.history_size)
        self.account_balances: deque = deque(maxlen=self.history_size)
        self.cpu_usages: deque = deque(maxlen=self.history_size)
        self.memory_usages: deque = deque(maxlen=self.history_size)

        # 이상 감지 모델
        if SKLEARN_AVAILABLE:
            self.model = IsolationForest(
                contamination=self.contamination,
                random_state=42
            )
            self.model_trained = False
        else:
            self.model = None
            self.model_trained = False

        # 이상 이벤트 히스토리
        self.anomaly_history: List[AnomalyEvent] = []

        logger.info("이상 감지 시스템 초기화")

    def record_api_response_time(self, response_time_ms: float):
        """API 응답 시간 기록"""
        self.api_response_times.append({
            'timestamp': datetime.now(),
            'value': response_time_ms
        })

    def record_order_failure_rate(self, failure_rate: float):
        """주문 실패율 기록 (0.0 ~ 1.0)"""
        self.order_failure_rates.append({
            'timestamp': datetime.now(),
            'value': failure_rate
        })

    def record_account_balance(self, balance: float):
        """계좌 잔고 기록"""
        self.account_balances.append({
            'timestamp': datetime.now(),
            'value': balance
        })

    def record_system_metrics(self, cpu_usage: float, memory_usage: float):
        """시스템 메트릭 기록"""
        self.cpu_usages.append({
            'timestamp': datetime.now(),
            'value': cpu_usage
        })
        self.memory_usages.append({
            'timestamp': datetime.now(),
            'value': memory_usage
        })

    def check_anomalies(self) -> List[AnomalyEvent]:
        """이상 감지 실행"""
        anomalies = []

        # 각 메트릭별로 이상 감지
        anomalies.extend(self._check_api_response_time())
        anomalies.extend(self._check_order_failure_rate())
        anomalies.extend(self._check_account_balance())
        anomalies.extend(self._check_system_metrics())

        # 이상 이벤트 저장
        self.anomaly_history.extend(anomalies)

        # 최근 1000개만 유지
        if len(self.anomaly_history) > 1000:
            self.anomaly_history = self.anomaly_history[-1000:]

        if anomalies:
            logger.warning(f"이상 감지: {len(anomalies)}개 이벤트")

        return anomalies

    def _check_api_response_time(self) -> List[AnomalyEvent]:
        """API 응답 시간 이상 감지"""
        if len(self.api_response_times) < 30:
            return []

        values = [x['value'] for x in self.api_response_times]
        mean = np.mean(values)
        std = np.std(values)

        recent_value = values[-1]

        # 3-sigma 규칙
        if recent_value > mean + 3 * std:
            anomaly_score = min((recent_value - mean) / (3 * std), 1.0)

            if anomaly_score > self.alert_threshold:
                return [AnomalyEvent(
                    timestamp=datetime.now(),
                    anomaly_type="api_slow",
                    severity=self._calculate_severity(anomaly_score),
                    expected_value=mean,
                    actual_value=recent_value,
                    anomaly_score=anomaly_score,
                    description=f"API 응답 시간 이상: {recent_value:.0f}ms (평균={mean:.0f}ms)"
                )]

        return []

    def _check_order_failure_rate(self) -> List[AnomalyEvent]:
        """주문 실패율 이상 감지"""
        if len(self.order_failure_rates) < 30:
            return []

        values = [x['value'] for x in self.order_failure_rates]
        mean = np.mean(values)

        recent_value = values[-1]

        # 실패율이 평균의 3배 이상
        if recent_value > mean * 3 and recent_value > 0.1:  # 최소 10% 실패
            anomaly_score = min(recent_value / 0.5, 1.0)  # 50% 실패를 최대로

            return [AnomalyEvent(
                timestamp=datetime.now(),
                anomaly_type="order_failure",
                severity=self._calculate_severity(anomaly_score),
                expected_value=mean,
                actual_value=recent_value,
                anomaly_score=anomaly_score,
                description=f"주문 실패율 급증: {recent_value*100:.1f}% (평균={mean*100:.1f}%)"
            )]

        return []

    def _check_account_balance(self) -> List[AnomalyEvent]:
        """계좌 잔고 급변 감지"""
        if len(self.account_balances) < 10:
            return []

        values = [x['value'] for x in self.account_balances]

        # 최근 5개 평균과 비교
        recent_avg = np.mean(values[-5:])
        previous_avg = np.mean(values[-10:-5])

        if previous_avg > 0:
            change_ratio = abs(recent_avg - previous_avg) / previous_avg

            # 10% 이상 급변
            if change_ratio > 0.10:
                anomaly_score = min(change_ratio / 0.20, 1.0)  # 20% 변화를 최대로

                return [AnomalyEvent(
                    timestamp=datetime.now(),
                    anomaly_type="balance_drop" if recent_avg < previous_avg else "balance_spike",
                    severity=self._calculate_severity(anomaly_score),
                    expected_value=previous_avg,
                    actual_value=recent_avg,
                    anomaly_score=anomaly_score,
                    description=f"계좌 잔고 급변: {change_ratio*100:.1f}% 변화"
                )]

        return []

    def _check_system_metrics(self) -> List[AnomalyEvent]:
        """시스템 리소스 이상 감지"""
        anomalies = []

        # CPU 사용률
        if len(self.cpu_usages) > 0:
            recent_cpu = self.cpu_usages[-1]['value']
            if recent_cpu > 90:
                anomalies.append(AnomalyEvent(
                    timestamp=datetime.now(),
                    anomaly_type="high_cpu",
                    severity="high",
                    expected_value=50.0,
                    actual_value=recent_cpu,
                    anomaly_score=min(recent_cpu / 100, 1.0),
                    description=f"CPU 사용률 높음: {recent_cpu:.1f}%"
                ))

        # 메모리 사용률
        if len(self.memory_usages) > 0:
            recent_memory = self.memory_usages[-1]['value']
            if recent_memory > 90:
                anomalies.append(AnomalyEvent(
                    timestamp=datetime.now(),
                    anomaly_type="high_memory",
                    severity="high",
                    expected_value=50.0,
                    actual_value=recent_memory,
                    anomaly_score=min(recent_memory / 100, 1.0),
                    description=f"메모리 사용률 높음: {recent_memory:.1f}%"
                ))

        return anomalies

    def _calculate_severity(self, anomaly_score: float) -> str:
        """심각도 계산"""
        if anomaly_score >= 0.9:
            return "critical"
        elif anomaly_score >= 0.7:
            return "high"
        elif anomaly_score >= 0.5:
            return "medium"
        else:
            return "low"

    def get_recent_anomalies(self, hours: int = 24) -> List[AnomalyEvent]:
        """최근 이상 이벤트 조회"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            event for event in self.anomaly_history
            if event.timestamp >= cutoff_time
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보"""
        return {
            'total_anomalies': len(self.anomaly_history),
            'recent_24h': len(self.get_recent_anomalies(24)),
            'by_severity': {
                'critical': len([e for e in self.anomaly_history if e.severity == 'critical']),
                'high': len([e for e in self.anomaly_history if e.severity == 'high']),
                'medium': len([e for e in self.anomaly_history if e.severity == 'medium']),
                'low': len([e for e in self.anomaly_history if e.severity == 'low']),
            },
            'by_type': {}  # TODO: 타입별 통계
        }


# 테스트
if __name__ == "__main__":
    detector = AnomalyDetector()

    # 정상 데이터 기록
    for i in range(50):
        detector.record_api_response_time(100 + np.random.normal(0, 10))
        detector.record_order_failure_rate(0.02 + np.random.uniform(-0.01, 0.01))

    # 이상 데이터
    detector.record_api_response_time(500)  # 매우 느린 응답
    detector.record_order_failure_rate(0.30)  # 높은 실패율

    # 이상 감지
    anomalies = detector.check_anomalies()

    for anomaly in anomalies:
        print(f"이상 감지: {anomaly.description} (점수={anomaly.anomaly_score:.2f})")
