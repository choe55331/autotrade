"""
virtual_trading/performance_tracker.py
성과 추적 및 분석
"""
from typing import Dict, List
from datetime import datetime, timedelta
import json
from pathlib import Path


class PerformanceTracker:
    """성과 추적기"""

    def __init__(self):
        """
        self.daily_snapshots: List[Dict] = []
        self.start_time = datetime.now()

    def take_snapshot(self, accounts_summary: Dict[str, Dict]):
        """일일 스냅샷"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'accounts': accounts_summary,
        }
        self.daily_snapshots.append(snapshot)

    def get_performance_metrics(self, strategy_name: str) -> Dict:
        """전략별 성과 지표"""
        if not self.daily_snapshots:
            return {}

        snapshots = [
            s['accounts'].get(strategy_name)
            for s in self.daily_snapshots
            if strategy_name in s['accounts']
        ]

        if not snapshots:
            return {}

        pnl_rates = [s['total_pnl_rate'] for s in snapshots]

        max_drawdown = self._calculate_max_drawdown(pnl_rates)

        sharpe_ratio = self._calculate_sharpe(pnl_rates)

        return {
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'volatility': self._calculate_volatility(pnl_rates),
            'best_day': max(pnl_rates) if pnl_rates else 0,
            'worst_day': min(pnl_rates) if pnl_rates else 0,
        }

    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """최대 낙폭 계산"""
        if not returns:
            return 0.0

        peak = returns[0]
        max_dd = 0.0

        for r in returns:
            if r > peak:
                peak = r
            dd = peak - r
            if dd > max_dd:
                max_dd = dd

        return max_dd

    def _calculate_sharpe(self, returns: List[float]) -> float:
        """샤프 비율 (단순화)"""
        if len(returns) < 2:
            return 0.0

        import statistics
        mean_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)

        if std_return == 0:
            return 0.0

        return mean_return / std_return

    def _calculate_volatility(self, returns: List[float]) -> float:
        """변동성"""
        if len(returns) < 2:
            return 0.0

        import statistics
        return statistics.stdev(returns)

    def save(self, filepath: str = "data/virtual_trading/performance.json"):
        """성과 데이터 저장"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        data = {
            'start_time': self.start_time.isoformat(),
            'snapshots': self.daily_snapshots[-30:],
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


__all__ = ['PerformanceTracker']
