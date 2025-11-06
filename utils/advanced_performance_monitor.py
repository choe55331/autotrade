"""
Advanced Performance Monitor v2.0
시스템 성능 실시간 모니터링 및 최적화 제안
"""

import time
import psutil
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
from threading import Lock

from utils.logger_new import get_logger

logger = get_logger()


@dataclass
class PerformanceMetric:
    """성능 메트릭"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    active_threads: int
    active_connections: int


@dataclass
class FunctionMetric:
    """함수 실행 메트릭"""
    function_name: str
    call_count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0
    last_call: Optional[datetime] = None
    errors: int = 0


@dataclass
class SystemHealth:
    """시스템 헬스 상태"""
    status: str
    cpu_healthy: bool
    memory_healthy: bool
    disk_healthy: bool
    network_healthy: bool
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class AdvancedPerformanceMonitor:
    """
    고급 성능 모니터링 시스템

    Features:
    - Real-time system resource monitoring
    - Function execution profiling
    - Automatic performance optimization recommendations
    - Historical metrics storage
    - Alerting on performance degradation
    """

    def __init__(self, history_size: int = 3600, alert_cpu_threshold: float = 80.0,
                 alert_memory_threshold: float = 85.0):
        self.history_size = history_size
        self.alert_cpu_threshold = alert_cpu_threshold
        self.alert_memory_threshold = alert_memory_threshold

        self.metrics_history: deque = deque(maxlen=history_size)
        self.function_metrics: Dict[str, FunctionMetric] = {}

        self._lock = Lock()
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_monitoring = False

        self._last_disk_io = psutil.disk_io_counters()
        self._last_network_io = psutil.net_io_counters()
        self._last_check_time = time.time()

        logger.info("AdvancedPerformanceMonitor initialized")

    async def start_monitoring(self, interval: float = 1.0):
        """모니터링 시작"""
        if self._is_monitoring:
            logger.warning("Monitoring already running")
            return

        self._is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop(interval))
        logger.info(f"Performance monitoring started (interval={interval}s)")

    async def stop_monitoring(self):
        """모니터링 중지"""
        if not self._is_monitoring:
            return

        self._is_monitoring = False

        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("Performance monitoring stopped")

    async def _monitoring_loop(self, interval: float):
        """모니터링 루프"""
        while self._is_monitoring:
            try:
                metric = self._collect_metrics()

                with self._lock:
                    self.metrics_history.append(metric)

                await self._check_thresholds(metric)

                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(interval)

    def _collect_metrics(self) -> PerformanceMetric:
        """시스템 메트릭 수집"""
        current_time = time.time()
        time_delta = current_time - self._last_check_time

        cpu_percent = psutil.cpu_percent(interval=0.1)

        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_mb = memory.used / (1024 * 1024)

        current_disk_io = psutil.disk_io_counters()
        disk_read_mb = (
            (current_disk_io.read_bytes - self._last_disk_io.read_bytes)
            / (1024 * 1024) / time_delta
        )
        disk_write_mb = (
            (current_disk_io.write_bytes - self._last_disk_io.write_bytes)
            / (1024 * 1024) / time_delta
        )
        self._last_disk_io = current_disk_io

        current_network_io = psutil.net_io_counters()
        network_sent_mb = (
            (current_network_io.bytes_sent - self._last_network_io.bytes_sent)
            / (1024 * 1024) / time_delta
        )
        network_recv_mb = (
            (current_network_io.bytes_recv - self._last_network_io.bytes_recv)
            / (1024 * 1024) / time_delta
        )
        self._last_network_io = current_network_io

        active_threads = psutil.Process().num_threads()

        try:
            active_connections = len(psutil.net_connections())
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            active_connections = 0

        self._last_check_time = current_time

        return PerformanceMetric(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_mb=memory_mb,
            disk_io_read_mb=disk_read_mb,
            disk_io_write_mb=disk_write_mb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            active_threads=active_threads,
            active_connections=active_connections
        )

    async def _check_thresholds(self, metric: PerformanceMetric):
        """임계값 확인 및 알람"""
        if metric.cpu_percent > self.alert_cpu_threshold:
            logger.warning(
                f"High CPU usage: {metric.cpu_percent:.1f}% "
                f"(threshold: {self.alert_cpu_threshold}%)"
            )

        if metric.memory_percent > self.alert_memory_threshold:
            logger.warning(
                f"High memory usage: {metric.memory_percent:.1f}% "
                f"(threshold: {self.alert_memory_threshold}%)"
            )

    def track_function(self, function_name: str, execution_time: float, error: bool = False):
        """함수 실행 추적"""
        with self._lock:
            if function_name not in self.function_metrics:
                self.function_metrics[function_name] = FunctionMetric(function_name=function_name)

            metric = self.function_metrics[function_name]
            metric.call_count += 1
            metric.total_time += execution_time
            metric.min_time = min(metric.min_time, execution_time)
            metric.max_time = max(metric.max_time, execution_time)
            metric.avg_time = metric.total_time / metric.call_count
            metric.last_call = datetime.now()

            if error:
                metric.errors += 1

    def get_current_metrics(self) -> Dict[str, Any]:
        """현재 메트릭 조회"""
        if not self.metrics_history:
            return {}

        latest = self.metrics_history[-1]

        return {
            'timestamp': latest.timestamp.isoformat(),
            'cpu_percent': latest.cpu_percent,
            'memory_percent': latest.memory_percent,
            'memory_mb': latest.memory_mb,
            'disk_io': {
                'read_mb_s': latest.disk_io_read_mb,
                'write_mb_s': latest.disk_io_write_mb
            },
            'network': {
                'sent_mb_s': latest.network_sent_mb,
                'recv_mb_s': latest.network_recv_mb
            },
            'threads': latest.active_threads,
            'connections': latest.active_connections
        }

    def get_function_metrics(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """함수 메트릭 조회 (호출 빈도 순)"""
        with self._lock:
            sorted_metrics = sorted(
                self.function_metrics.values(),
                key=lambda x: x.call_count,
                reverse=True
            )

            return [
                {
                    'function': m.function_name,
                    'call_count': m.call_count,
                    'total_time': f"{m.total_time:.3f}s",
                    'avg_time': f"{m.avg_time * 1000:.2f}ms",
                    'min_time': f"{m.min_time * 1000:.2f}ms",
                    'max_time': f"{m.max_time * 1000:.2f}ms",
                    'errors': m.errors,
                    'last_call': m.last_call.isoformat() if m.last_call else None
                }
                for m in sorted_metrics[:top_n]
            ]

    def get_slowest_functions(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """가장 느린 함수 조회"""
        with self._lock:
            sorted_metrics = sorted(
                self.function_metrics.values(),
                key=lambda x: x.avg_time,
                reverse=True
            )

            return [
                {
                    'function': m.function_name,
                    'avg_time': f"{m.avg_time * 1000:.2f}ms",
                    'call_count': m.call_count,
                    'total_time': f"{m.total_time:.3f}s"
                }
                for m in sorted_metrics[:top_n]
            ]

    def get_system_health(self) -> SystemHealth:
        """시스템 헬스 체크"""
        if not self.metrics_history:
            return SystemHealth(
                status="unknown",
                cpu_healthy=True,
                memory_healthy=True,
                disk_healthy=True,
                network_healthy=True
            )

        recent_metrics = list(self.metrics_history)[-60:]

        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)

        cpu_healthy = avg_cpu < 70
        memory_healthy = avg_memory < 80
        disk_healthy = True
        network_healthy = True

        issues = []
        recommendations = []

        if not cpu_healthy:
            issues.append(f"High CPU usage: {avg_cpu:.1f}%")
            recommendations.append("Consider optimizing CPU-intensive operations")

        if not memory_healthy:
            issues.append(f"High memory usage: {avg_memory:.1f}%")
            recommendations.append("Review memory allocations and implement caching strategies")

        if self.function_metrics:
            slow_functions = self.get_slowest_functions(top_n=3)
            if slow_functions and float(slow_functions[0]['avg_time'].replace('ms', '')) > 1000:
                recommendations.append(
                    f"Optimize slow function: {slow_functions[0]['function']} "
                    f"({slow_functions[0]['avg_time']})"
                )

        status = "healthy" if all([cpu_healthy, memory_healthy, disk_healthy, network_healthy]) else "degraded"
        if len(issues) >= 3:
            status = "critical"

        return SystemHealth(
            status=status,
            cpu_healthy=cpu_healthy,
            memory_healthy=memory_healthy,
            disk_healthy=disk_healthy,
            network_healthy=network_healthy,
            issues=issues,
            recommendations=recommendations
        )

    def get_statistics(self, minutes: int = 60) -> Dict[str, Any]:
        """통계 조회"""
        if not self.metrics_history:
            return {}

        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [
            m for m in self.metrics_history
            if m.timestamp >= cutoff_time
        ]

        if not recent_metrics:
            return {}

        return {
            'period_minutes': minutes,
            'samples': len(recent_metrics),
            'cpu': {
                'avg': sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
                'min': min(m.cpu_percent for m in recent_metrics),
                'max': max(m.cpu_percent for m in recent_metrics)
            },
            'memory': {
                'avg': sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
                'min': min(m.memory_percent for m in recent_metrics),
                'max': max(m.memory_percent for m in recent_metrics)
            },
            'network': {
                'total_sent_mb': sum(m.network_sent_mb for m in recent_metrics) * (minutes * 60 / len(recent_metrics)),
                'total_recv_mb': sum(m.network_recv_mb for m in recent_metrics) * (minutes * 60 / len(recent_metrics))
            }
        }


_global_monitor: Optional[AdvancedPerformanceMonitor] = None


def get_performance_monitor() -> AdvancedPerformanceMonitor:
    """전역 성능 모니터 인스턴스 반환"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = AdvancedPerformanceMonitor()
    return _global_monitor


def track_execution_time(function_name: Optional[str] = None):
    """함수 실행 시간 추적 데코레이터"""
    def decorator(func):
        import functools

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = function_name or f"{func.__module__}.{func.__name__}"
            monitor = get_performance_monitor()

            start_time = time.time()
            error = False

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = True
                raise e
            finally:
                execution_time = time.time() - start_time
                monitor.track_function(name, execution_time, error)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            name = function_name or f"{func.__module__}.{func.__name__}"
            monitor = get_performance_monitor()

            start_time = time.time()
            error = False

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = True
                raise e
            finally:
                execution_time = time.time() - start_time
                monitor.track_function(name, execution_time, error)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
