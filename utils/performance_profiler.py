"""
AutoTrade Pro - 성능 프로파일링 도구
코드 성능 측정 및 최적화 지원
"""
import time
import cProfile
import pstats
import io
from functools import wraps
from typing import Dict, Any, Optional, Callable
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """성능 메트릭"""
    function_name: str
    call_count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0
    last_call_time: Optional[datetime] = None

    def update(self, elapsed_time: float):
        """메트릭 업데이트"""
        self.call_count += 1
        self.total_time += elapsed_time
        self.min_time = min(self.min_time, elapsed_time)
        self.max_time = max(self.max_time, elapsed_time)
        self.avg_time = self.total_time / self.call_count
        self.last_call_time = datetime.now()


class PerformanceProfiler:
    """성능 프로파일러"""

    def __init__(self):
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.enabled = True

    def measure(self, func_name: Optional[str] = None):
        """
        함수 성능 측정 데코레이터

        Usage:
            profiler = PerformanceProfiler()

            @profiler.measure()
            def my_function():
                ...
        """
        def decorator(func: Callable):
            name = func_name or func.__name__

            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)

                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    elapsed_time = time.perf_counter() - start_time

                    if name not in self.metrics:
                        self.metrics[name] = PerformanceMetric(function_name=name)

                    self.metrics[name].update(elapsed_time)

            return wrapper
        return decorator

    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """통계 조회"""
        return {
            name: {
                'call_count': metric.call_count,
                'total_time': f"{metric.total_time:.4f}s",
                'avg_time': f"{metric.avg_time:.4f}s",
                'min_time': f"{metric.min_time:.4f}s",
                'max_time': f"{metric.max_time:.4f}s",
            }
            for name, metric in self.metrics.items()
        }

    def print_stats(self, top_n: int = 10):
        """통계 출력"""
        print("\n" + "="*80)
        print("성능 프로파일링 결과")
        print("="*80)

        sorted_metrics = sorted(
            self.metrics.items(),
            key=lambda x: x[1].total_time,
            reverse=True
        )

        print(f"{'함수명':<40} {'호출':<10} {'총 시간':<12} {'평균':<12} {'최소':<12} {'최대':<12}")
        print("-"*110)

        for name, metric in sorted_metrics[:top_n]:
            print(
                f"{name:<40} "
                f"{metric.call_count:<10} "
                f"{metric.total_time:<12.4f} "
                f"{metric.avg_time:<12.4f} "
                f"{metric.min_time:<12.4f} "
                f"{metric.max_time:<12.4f}"
            )

        print("="*80 + "\n")

    def reset(self):
        """통계 초기화"""
        self.metrics.clear()

    def enable(self):
        """프로파일링 활성화"""
        self.enabled = True

    def disable(self):
        """프로파일링 비활성화"""
        self.enabled = False


class CodeBlockProfiler:
    """코드 블록 성능 측정 (컨텍스트 매니저)"""

    def __init__(self, name: str, profiler: Optional[PerformanceProfiler] = None):
        self.name = name
        self.profiler = profiler
        self.start_time = None
        self.elapsed_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_time = time.perf_counter() - self.start_time

        if self.profiler:
            if self.name not in self.profiler.metrics:
                self.profiler.metrics[self.name] = PerformanceMetric(function_name=self.name)
            self.profiler.metrics[self.name].update(self.elapsed_time)
        else:
            logger.debug(f"[{self.name}] 실행 시간: {self.elapsed_time:.4f}초")


class DetailedProfiler:
    """상세 프로파일러 (cProfile 사용)"""

    @staticmethod
    def profile_function(func: Callable, *args, **kwargs):
        """함수 상세 프로파일링"""
        profiler = cProfile.Profile()
        profiler.enable()

        result = func(*args, **kwargs)

        profiler.disable()

        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.strip_dirs()
        stats.sort_stats('cumulative')
        stats.print_stats(20)

        print("\n" + "="*80)
        print(f"상세 프로파일링: {func.__name__}")
        print("="*80)
        print(stream.getvalue())
        print("="*80 + "\n")

        return result

    @staticmethod
    def profile_code_block(code: str, globals_dict: Optional[Dict] = None):
        """코드 블록 프로파일링"""
        profiler = cProfile.Profile()

        if globals_dict is None:
            globals_dict = globals()

        profiler.enable()
        exec(code, globals_dict)
        profiler.disable()

        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.strip_dirs()
        stats.sort_stats('cumulative')
        stats.print_stats(20)

        print(stream.getvalue())


_global_profiler = PerformanceProfiler()


def measure_performance(func_name: Optional[str] = None):
    """글로벌 프로파일러를 사용한 성능 측정 데코레이터"""
    return _global_profiler.measure(func_name)


def profile_code(name: str):
    """글로벌 프로파일러를 사용한 코드 블록 측정"""
    return CodeBlockProfiler(name, _global_profiler)


def get_performance_stats():
    """글로벌 프로파일러 통계"""
    return _global_profiler.get_stats()


def print_performance_stats(top_n: int = 10):
    """글로벌 프로파일러 통계 출력"""
    _global_profiler.print_stats(top_n)


def reset_performance_stats():
    """글로벌 프로파일러 초기화"""
    _global_profiler.reset()


from utils.performance_profiler import measure_performance

@measure_performance()
def my_slow_function():
    pass

from utils.performance_profiler import profile_code

def process_data():
    with profile_code("데이터 로드"):
        data = load_data()

    with profile_code("데이터 처리"):
        result = process(data)

    return result

from utils.performance_profiler import print_performance_stats

print_performance_stats(top_n=20)

from utils.performance_profiler import DetailedProfiler

def heavy_computation():
    pass

DetailedProfiler.profile_function(heavy_computation)
