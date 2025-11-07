"""
AutoTrade Pro v4.0 - 전략 파라미터 자동 최적화
Grid Search, Random Search, Bayesian Optimization 지원


주요 기능:
- 다양한 최적화 방법 지원
- 병렬 처리로 빠른 최적화
- Optuna 기반 Bayesian Optimization
- 최적화 결과 시각화
"""
import logging
from typing import Dict, Any, List, Callable, Optional, Tuple
from datetime import datetime
import json
from pathlib import Path
from dataclasses import dataclass

import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed

try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    logging.warning("Optuna not available. Bayesian optimization will not work.")

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """최적화 결과"""
    best_params: Dict[str, Any]
    best_score: float
    n_trials: int
    method: str
    duration_seconds: float
    all_trials: List[Dict[str, Any]]


class StrategyOptimizer:
    """전략 파라미터 최적화 엔진"""

    def __init__(
        self,
        objective_function: Callable,
        param_ranges: Dict[str, List],
        method: str = "bayesian",
        n_trials: int = 50,
        n_jobs: int = -1
    ):
        """
        최적화 엔진 초기화

        Args:
            objective_function: 목적 함수 (params -> score)
            param_ranges: 파라미터 범위
                예: {
                    'ma_period': [5, 10, 20, 30, 60],
                    'rsi_threshold': [30, 40, 50, 60, 70]
                }
            method: 최적화 방법 ('grid', 'random', 'bayesian')
            n_trials: 시도 횟수
            """
            n_jobs: 병렬 작업 수 (-1 = 모든 CPU)
        self.objective_function = objective_function
        self.param_ranges = param_ranges
        self.method = method
        self.n_trials = n_trials
        self.n_jobs = n_jobs if n_jobs > 0 else None

        logger.info(f"전략 최적화 엔진 초기화: method={method}, n_trials={n_trials}")

    def optimize(self) -> OptimizationResult:
        """최적화 실행"""
        start_time = datetime.now()

        if self.method == "grid":
            result = self._grid_search()
        elif self.method == "random":
            result = self._random_search()
        elif self.method == "bayesian":
            if not OPTUNA_AVAILABLE:
                logger.warning("Optuna not available. Falling back to random search.")
                result = self._random_search()
            else:
                result = self._bayesian_optimization()
        else:
            raise ValueError(f"Unknown optimization method: {self.method}")

        duration = (datetime.now() - start_time).total_seconds()
        result.duration_seconds = duration

        logger.info(f"최적화 완료: best_score={result.best_score:.4f}, duration={duration:.2f}s")
        return result

    def _grid_search(self) -> OptimizationResult:
        """Grid Search (격자 탐색)"""
        logger.info("Grid Search 시작...")

        import itertools

        param_names = list(self.param_ranges.keys())
        param_values = [self.param_ranges[name] for name in param_names]
        all_combinations = list(itertools.product(*param_values))

        logger.info(f"총 {len(all_combinations)}개 조합 테스트")

        results = []
        for values in all_combinations:
            params = dict(zip(param_names, values))
            score = self.objective_function(params)
            results.append({
                'params': params,
                'score': score
            })

        best_trial = max(results, key=lambda x: x['score'])

        return OptimizationResult(
            best_params=best_trial['params'],
            best_score=best_trial['score'],
            n_trials=len(results),
            method='grid',
            duration_seconds=0,
            all_trials=results
        )

    def _random_search(self) -> OptimizationResult:
        """Random Search (무작위 탐색)"""
        logger.info(f"Random Search 시작... (n_trials={self.n_trials})")

        results = []
        for i in range(self.n_trials):
            params = {}
            """
            for name, values in self.param_ranges.items():
                if isinstance(values, list):
                """
                    params[name] = np.random.choice(values)
                elif isinstance(values, tuple) and len(values) == 2:
                    params[name] = np.random.uniform(values[0], values[1])

            score = self.objective_function(params)
            results.append({
                'params': params,
                'score': score
            })

            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i+1}/{self.n_trials} trials completed")

        best_trial = max(results, key=lambda x: x['score'])

        return OptimizationResult(
            best_params=best_trial['params'],
            best_score=best_trial['score'],
            n_trials=len(results),
            method='random',
            duration_seconds=0,
            all_trials=results
        )

    def _bayesian_optimization(self) -> OptimizationResult:
        """Bayesian Optimization (베이지안 최적화)"""
        logger.info(f"Bayesian Optimization 시작... (n_trials={self.n_trials})")

        def objective(trial):
            """Optuna objective function"""
            params = {}
            for name, values in self.param_ranges.items():
                if isinstance(values, list):
                """
                    params[name] = trial.suggest_categorical(name, values)
                elif isinstance(values, tuple) and len(values) == 2:
                    if isinstance(values[0], int):
                        params[name] = trial.suggest_int(name, values[0], values[1])
                    else:
                    """
                        params[name] = trial.suggest_float(name, values[0], values[1])

            return self.objective_function(params)

        study = optuna.create_study(
            direction='maximize',
            sampler=optuna.samplers.TPESampler(seed=42)
        )

        study.optimize(objective, n_trials=self.n_trials, show_progress_bar=True)

        all_trials = []
        for trial in study.trials:
            all_trials.append({
                'params': trial.params,
                'score': trial.value
            })

        return OptimizationResult(
            best_params=study.best_params,
            best_score=study.best_value,
            n_trials=len(study.trials),
            method='bayesian',
            duration_seconds=0,
            all_trials=all_trials
        )

    def save_results(self, result: OptimizationResult, save_path: Path):
        """최적화 결과 저장"""
        result_dict = {
            'best_params': result.best_params,
            'best_score': result.best_score,
            'n_trials': result.n_trials,
            'method': result.method,
            'duration_seconds': result.duration_seconds,
            'all_trials': result.all_trials,
            'timestamp': datetime.now().isoformat()
        }

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"최적화 결과 저장: {save_path}")


if __name__ == "__main__":
    def dummy_objective(params):
        """더미 목적 함수 (Sharpe Ratio 시뮬레이션)"""
        ma_period = params['ma_period']
        rsi_threshold = params['rsi_threshold']

        score = -((ma_period - 20) ** 2 + (rsi_threshold - 50) ** 2) / 1000
        return score

    optimizer = StrategyOptimizer(
        objective_function=dummy_objective,
        param_ranges={
            'ma_period': [5, 10, 15, 20, 25, 30],
            'rsi_threshold': [30, 40, 50, 60, 70]
        },
        method='bayesian',
        n_trials=30
    )

    result = optimizer.optimize()
    print(f"Best params: {result.best_params}")
    print(f"Best score: {result.best_score:.4f}")
