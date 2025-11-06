"""
utils/performance_monitor.py
실시간 성능 모니터링 시스템 (v5.11 NEW)
"""

"""
Features:
- 함수 실행 시간 측정
- 메모리 사용량 추적
- API 호출 속도 모니터링
- 병목 지점 자동 감지
- 성능 리포트 생성
"""
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import time
import functools
import threading
from collections import defaultdict, deque
import psutil
import os

from utils.logger_new import get_logger

logger = get_logger()


@dataclass
class PerformanceMetric:
    """성능 메트릭"""
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    memory_before: Optional[int] = None
    memory_after: Optional[int] = None
    memory_delta: Optional[int] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def finish(self, success: bool = True, error: Optional[str] = None):
        """메트릭 완료"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error = error

        try:
            process = psutil.Process(os.getpid())
            self.memory_after = process.memory_info().rss
            if self.memory_before:
                self.memory_delta = self.memory_after - self.memory_before
        except:
            pass


class PerformanceMonitor:
    """
    성능 모니터링 시스템 (v5.11)

    Features:
    - 데코레이터 기반 함수 모니터링
    - Context manager 지원
    - 실시간 통계
    - 성능 리포트
    - 병목 지점 감지
    """

    def __init__(self, max_history: int = 1000):
        """
        초기화

        Args:
            max_history: 최대 히스토리 보관 개수
        """
        self.metrics: List[PerformanceMetric] = []
        self.max_history = max_history

        self.function_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0,
            'avg_time': 0,
            'min_time': float('inf'),
            'max_time': 0,
            'errors': 0,
            'last_call': None
        })

        self.recent_metrics = deque(maxlen=100)

        self.lock = threading.Lock()

        self.system_monitor_active = False
        self.system_stats = {
            'cpu_percent': 0,
            'memory_percent': 0,
            'disk_usage': 0
        }

        logger.info("Performance Monitor initialized (v5.11)")

    def measure(self, name: str, metadata: Optional[Dict] = None) -> 'PerformanceContext':
        """
        Context manager for performance measurement

        Usage:
            with monitor.measure('function_name'):
                # code to measure
                pass
        """
        return PerformanceContext(self, name, metadata or {})

    def track(self, func: Optional[Callable] = None, name: Optional[str] = None):
        """
        Decorator for automatic performance tracking

        Usage:
            @monitor.track
            def my_function():
                pass

            @monitor.track(name='custom_name')
            def another_function():
                pass
        """
        def decorator(f):
            metric_name = name or f.__name__

            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                with self.measure(metric_name):
                    return f(*args, **kwargs)

            return wrapper

        if func is None:
            return decorator
        else:
            return decorator(func)

    def record_metric(self, metric: PerformanceMetric):
        """메트릭 기록"""
        with self.lock:
            self.metrics.append(metric)

            if len(self.metrics) > self.max_history:
                self.metrics.pop(0)

            self.recent_metrics.append(metric)

            stats = self.function_stats[metric.name]
            stats['count'] += 1
            stats['last_call'] = datetime.now().isoformat()

            if metric.duration:
                stats['total_time'] += metric.duration
                stats['avg_time'] = stats['total_time'] / stats['count']
                stats['min_time'] = min(stats['min_time'], metric.duration)
                stats['max_time'] = max(stats['max_time'], metric.duration)

            if not metric.success:
                stats['errors'] += 1

    def get_stats(self, func_name: Optional[str] = None) -> Dict[str, Any]:
        """
        통계 조회

        Args:
            func_name: 특정 함수명 (None이면 전체)

        Returns:
            통계 딕셔너리
        """
        with self.lock:
            if func_name:
                return dict(self.function_stats.get(func_name, {}))
            else:
                return {
                    name: dict(stats)
                    for name, stats in self.function_stats.items()
                }

    def get_slowest_functions(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        가장 느린 함수들 조회

        Args:
            top_n: 상위 N개

        Returns:
            함수 리스트 (평균 시간 기준 내림차순)
        """
        with self.lock:
            sorted_funcs = sorted(
                self.function_stats.items(),
                key=lambda x: x[1]['avg_time'],
                reverse=True
            )

            return [
                {
                    'name': name,
                    **stats
                }
                for name, stats in sorted_funcs[:top_n]
            ]

    def get_most_called_functions(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        가장 많이 호출된 함수들

        Args:
            top_n: 상위 N개

        Returns:
            함수 리스트 (호출 횟수 기준 내림차순)
        """
        with self.lock:
            sorted_funcs = sorted(
                self.function_stats.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )

            return [
                {
                    'name': name,
                    **stats
                }
                for name, stats in sorted_funcs[:top_n]
            ]

    def get_error_prone_functions(self) -> List[Dict[str, Any]]:
        """
        에러가 많은 함수들

        Returns:
            함수 리스트 (에러 횟수 기준)
        """
        with self.lock:
            error_funcs = [
                {'name': name, **stats}
                for name, stats in self.function_stats.items()
                if stats['errors'] > 0
            ]

            error_funcs.sort(key=lambda x: x['errors'], reverse=True)
            return error_funcs

    def detect_bottlenecks(self, threshold_seconds: float = 1.0) -> List[Dict[str, Any]]:
        """
        병목 지점 감지

        Args:
            threshold_seconds: 임계값 (초)

        Returns:
            병목 함수 리스트
        """
        with self.lock:
            bottlenecks = []

            for name, stats in self.function_stats.items():
                if stats['avg_time'] > threshold_seconds:
                    bottlenecks.append({
                        'name': name,
                        'avg_time': stats['avg_time'],
                        'max_time': stats['max_time'],
                        'count': stats['count'],
                        'severity': 'critical' if stats['avg_time'] > 5.0 else 'high' if stats['avg_time'] > 2.0 else 'medium'
                    })

            bottlenecks.sort(key=lambda x: x['avg_time'], reverse=True)
            return bottlenecks

    def generate_report(self, include_system: bool = True) -> Dict[str, Any]:
        """
        성능 리포트 생성

        Args:
            include_system: 시스템 리소스 포함 여부

        Returns:
            종합 리포트
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_metrics': len(self.metrics),
            'total_functions': len(self.function_stats),
            'slowest_functions': self.get_slowest_functions(5),
            'most_called_functions': self.get_most_called_functions(5),
            'error_prone_functions': self.get_error_prone_functions(),
            'bottlenecks': self.detect_bottlenecks(1.0),
        }

        if include_system:
            report['system_resources'] = self.get_system_resources()

        return report

    def get_system_resources(self) -> Dict[str, Any]:
        """시스템 리소스 현재 상태"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_mb': memory.available / (1024 * 1024),
                'memory_used_mb': memory.used / (1024 * 1024),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024 * 1024 * 1024)
            }
        except Exception as e:
            logger.error(f"Failed to get system resources: {e}")
            return {}

    def start_system_monitoring(self, interval: int = 60):
        """
        시스템 리소스 주기적 모니터링 시작

        Args:
            interval: 모니터링 간격 (초)
        """
        if self.system_monitor_active:
            logger.warning("System monitoring already active")
            return

        self.system_monitor_active = True

        def monitor_loop():
            while self.system_monitor_active:
                try:
                    self.system_stats = self.get_system_resources()
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"System monitoring error: {e}")

        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        logger.info(f"System monitoring started (interval: {interval}s)")

    def stop_system_monitoring(self):
        """시스템 모니터링 중지"""
        self.system_monitor_active = False
        logger.info("System monitoring stopped")

    def clear_stats(self):
        """통계 초기화"""
        with self.lock:
            self.metrics.clear()
            self.recent_metrics.clear()
            self.function_stats.clear()
            logger.info("Performance stats cleared")

    def export_metrics(self, filepath: str):
        """
        메트릭을 파일로 내보내기

        Args:
            filepath: 출력 파일 경로
        """
        import json

        with self.lock:
            data = {
                'timestamp': datetime.now().isoformat(),
                'metrics': [
                    {
                        'name': m.name,
                        'duration': m.duration,
                        'memory_delta': m.memory_delta,
                        'success': m.success,
                        'error': m.error,
                        'metadata': m.metadata
                    }
                    for m in self.metrics
                ],
                'function_stats': {
                    name: dict(stats)
                    for name, stats in self.function_stats.items()
                }
            }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Metrics exported to {filepath}")


class PerformanceContext:
    """Performance measurement context manager"""

    def __init__(self, monitor: PerformanceMonitor, name: str, metadata: Dict):
        self.monitor = monitor
        self.metric = PerformanceMetric(
            name=name,
            start_time=time.time(),
            metadata=metadata
        )

        try:
            process = psutil.Process(os.getpid())
            self.metric.memory_before = process.memory_info().rss
        except:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        success = exc_type is None
        error = str(exc_val) if exc_val else None

        self.metric.finish(success=success, error=error)
        self.monitor.record_metric(self.metric)

        return False


_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """싱글톤 성능 모니터 인스턴스 반환"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def track_performance(func=None, name=None):
    """
    성능 추적 데코레이터

    Usage:
        @track_performance
        def my_function():
            pass
    """
    monitor = get_performance_monitor()
    return monitor.track(func, name)


__all__ = [
    'PerformanceMonitor',
    'PerformanceMetric',
    'PerformanceContext',
    'get_performance_monitor',
    'track_performance'
]
