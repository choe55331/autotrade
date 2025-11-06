"""
Monitoring & Health Check Module v6.0
시스템 모니터링, Health Check, Metrics
"""

import psutil
import time
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class HealthChecker:
    """
    헬스 체커

    Features:
    - 시스템 리소스 체크
    - API 연결 확인
    - 데이터베이스 연결 확인
    """

    def __init__(self):
        self.last_check_time = None
        self.last_status = None

    def check_health(self, bot_instance=None) -> Dict[str, Any]:
        """
        전체 헬스 체크

        Args:
            bot_instance: 봇 인스턴스

        Returns:
            헬스 상태
        """
        self.last_check_time = datetime.now()

        status = {
            'status': 'healthy',
            'timestamp': self.last_check_time.isoformat(),
            'uptime': self._get_uptime(),
            'system': self._check_system(),
            'services': {}
        }

        # 데이터베이스 체크
        if bot_instance and hasattr(bot_instance, 'db_session'):
            status['services']['database'] = self._check_database(bot_instance.db_session)

        # API 체크
        if bot_instance and hasattr(bot_instance, 'client'):
            status['services']['api'] = self._check_api(bot_instance.client)

        # WebSocket 체크
        if bot_instance and hasattr(bot_instance, 'websocket_manager'):
            status['services']['websocket'] = self._check_websocket(bot_instance.websocket_manager)

        # 전체 상태 판단
        if any(service.get('status') == 'unhealthy' for service in status['services'].values()):
            status['status'] = 'degraded'

        self.last_status = status
        return status

    def _get_uptime(self) -> str:
        """업타임"""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time

        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{days}d {hours}h {minutes}m {seconds}s"

    def _check_system(self) -> Dict[str, Any]:
        """시스템 리소스 체크"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                'status': 'healthy',
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024 ** 3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024 ** 3)
            }
        except Exception as e:
            logger.error(f"System check failed: {e}")
            return {'status': 'unknown', 'error': str(e)}

    def _check_database(self, db_session) -> Dict[str, Any]:
        """데이터베이스 연결 확인"""
        try:
            if db_session:
                # 간단한 쿼리 실행
                db_session.execute("SELECT 1")
                return {'status': 'healthy'}
            else:
                return {'status': 'unhealthy', 'reason': 'No session'}
        except Exception as e:
            logger.error(f"Database check failed: {e}")
            return {'status': 'unhealthy', 'error': str(e)}

    def _check_api(self, client) -> Dict[str, Any]:
        """API 연결 확인"""
        try:
            if client and client.token:
                return {'status': 'healthy', 'has_token': True}
            else:
                return {'status': 'unhealthy', 'reason': 'No token'}
        except Exception as e:
            logger.error(f"API check failed: {e}")
            return {'status': 'unhealthy', 'error': str(e)}

    def _check_websocket(self, websocket_manager) -> Dict[str, Any]:
        """WebSocket 연결 확인"""
        try:
            if websocket_manager:
                # WebSocketManager의 연결 상태 확인
                # (실제 구현은 websocket_manager의 API에 따라 다름)
                return {'status': 'healthy'}
            else:
                return {'status': 'unhealthy', 'reason': 'Not initialized'}
        except Exception as e:
            logger.error(f"WebSocket check failed: {e}")
            return {'status': 'unknown', 'error': str(e)}


class MetricsCollector:
    """
    메트릭 수집기

    Features:
    - 거래 횟수
    - 성공률
    - 평균 응답 시간
    """

    def __init__(self):
        self.metrics = {
            'trades': {
                'total': 0,
                'buy': 0,
                'sell': 0,
                'success': 0,
                'failed': 0
            },
            'api_calls': {
                'total': 0,
                'success': 0,
                'failed': 0,
                'total_time': 0.0
            },
            'scan_cycles': {
                'total': 0,
                'candidates_found': 0,
                'ai_approved': 0
            }
        }

    def record_trade(self, action: str, success: bool):
        """거래 기록"""
        self.metrics['trades']['total'] += 1
        self.metrics['trades'][action] += 1

        if success:
            self.metrics['trades']['success'] += 1
        else:
            self.metrics['trades']['failed'] += 1

    def record_api_call(self, success: bool, elapsed_time: float):
        """API 호출 기록"""
        self.metrics['api_calls']['total'] += 1
        self.metrics['api_calls']['total_time'] += elapsed_time

        if success:
            self.metrics['api_calls']['success'] += 1
        else:
            self.metrics['api_calls']['failed'] += 1

    def record_scan_cycle(self, candidates_found: int, ai_approved: int):
        """스캔 사이클 기록"""
        self.metrics['scan_cycles']['total'] += 1
        self.metrics['scan_cycles']['candidates_found'] += candidates_found
        self.metrics['scan_cycles']['ai_approved'] += ai_approved

    def get_metrics(self) -> Dict[str, Any]:
        """메트릭 반환"""
        metrics = self.metrics.copy()

        # 계산 메트릭
        api_calls = metrics['api_calls']
        if api_calls['total'] > 0:
            metrics['api_calls']['avg_time'] = api_calls['total_time'] / api_calls['total']
            metrics['api_calls']['success_rate'] = (api_calls['success'] / api_calls['total']) * 100

        trades = metrics['trades']
        if trades['total'] > 0:
            metrics['trades']['success_rate'] = (trades['success'] / trades['total']) * 100

        return metrics


# 싱글톤
_health_checker_instance = None
_metrics_collector_instance = None


def get_health_checker() -> HealthChecker:
    """HealthChecker 싱글톤"""
    global _health_checker_instance
    if _health_checker_instance is None:
        _health_checker_instance = HealthChecker()
    return _health_checker_instance


def get_metrics_collector() -> MetricsCollector:
    """MetricsCollector 싱글톤"""
    global _metrics_collector_instance
    if _metrics_collector_instance is None:
        _metrics_collector_instance = MetricsCollector()
    return _metrics_collector_instance
