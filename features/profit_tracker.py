수익 추적 및 성과 분석
일간/주간/월간 수익률, 승률, 최대 낙폭 등 분석
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import json


@dataclass
class TradeRecord:
    """거래 기록"""
    trade_id: str
    stock_code: str
    stock_name: str
    action: str
    quantity: int
    price: int
    timestamp: datetime
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None

    def to_dict(self) -> Dict:
        return {
            'trade_id': self.trade_id,
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'action': self.action,
            'quantity': self.quantity,
            'price': self.price,
            'timestamp': self.timestamp.isoformat(),
            'profit_loss': self.profit_loss,
            'profit_loss_percent': self.profit_loss_percent
        }


@dataclass
class PerformanceMetrics:
    """성과 지표"""
    period: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float

    total_profit: float
    total_loss: float
    net_profit: float

    avg_profit_per_trade: float
    avg_winning_trade: float
    avg_losing_trade: float

    largest_win: float
    largest_loss: float

    max_drawdown: float
    sharpe_ratio: Optional[float]

    avg_holding_period: Optional[float]

    def to_dict(self) -> Dict:
        return {
            'period': self.period,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'total_profit': self.total_profit,
            'total_loss': self.total_loss,
            'net_profit': self.net_profit,
            'avg_profit_per_trade': self.avg_profit_per_trade,
            'avg_winning_trade': self.avg_winning_trade,
            'avg_losing_trade': self.avg_losing_trade,
            'largest_win': self.largest_win,
            'largest_loss': self.largest_loss,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio,
            'avg_holding_period': self.avg_holding_period
        }


class ProfitTracker:
    """수익 추적 서비스"""

    def __init__(self, data_dir: Path = Path('data')):
        """
        Args:
            data_dir: 데이터 저장 폴더
        """
        self.data_dir = data_dir
        self.trades_file = data_dir / 'trade_history.json'
        self.performance_file = data_dir / 'performance_cache.json'

        self._trades: List[TradeRecord] = []
        self._load_trades()

    def _load_trades(self):
        """저장된 거래 기록 로드"""
        if self.trades_file.exists():
            try:
                with open(self.trades_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._trades = [
                        TradeRecord(
                            trade_id=t['trade_id'],
                            stock_code=t['stock_code'],
                            stock_name=t['stock_name'],
                            action=t['action'],
                            quantity=t['quantity'],
                            price=t['price'],
                            timestamp=datetime.fromisoformat(t['timestamp']),
                            profit_loss=t.get('profit_loss'),
                            profit_loss_percent=t.get('profit_loss_percent')
                        )
                        for t in data
                    ]
            except Exception as e:
                print(f"거래 기록 로드 실패: {e}")

    def _save_trades(self):
        """거래 기록 저장"""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with open(self.trades_file, 'w', encoding='utf-8') as f:
                json.dump([t.to_dict() for t in self._trades], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"거래 기록 저장 실패: {e}")

    def add_trade(self, trade: TradeRecord):
        """거래 추가"""
        self._trades.append(trade)
        self._save_trades()

    def get_trades(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[TradeRecord]:
        """
        기간별 거래 가져오기

        Args:
            start_date: 시작일 (없으면 전체)
            end_date: 종료일 (없으면 현재)

        Returns:
            거래 기록 리스트
        """
        trades = self._trades

        if start_date:
            trades = [t for t in trades if t.timestamp >= start_date]

        if end_date:
            trades = [t for t in trades if t.timestamp <= end_date]

        return trades

    def calculate_metrics(self, period: str = 'daily') -> PerformanceMetrics:
        """
        성과 지표 계산

        Args:
            period: 'daily', 'weekly', 'monthly', 'all'

        Returns:
            성과 지표
        """
        now = datetime.now()
        if period == 'daily':
            start_date = now - timedelta(days=1)
        elif period == 'weekly':
            start_date = now - timedelta(days=7)
        elif period == 'monthly':
            start_date = now - timedelta(days=30)
        else:
            start_date = None

        trades = self.get_trades(start_date=start_date)

        sell_trades = [t for t in trades if t.action == 'sell' and t.profit_loss is not None]

        if not sell_trades:
            return PerformanceMetrics(
                period=period,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_profit=0.0,
                total_loss=0.0,
                net_profit=0.0,
                avg_profit_per_trade=0.0,
                avg_winning_trade=0.0,
                avg_losing_trade=0.0,
                largest_win=0.0,
                largest_loss=0.0,
                max_drawdown=0.0,
                sharpe_ratio=None,
                avg_holding_period=None
            )

        winning_trades = [t for t in sell_trades if t.profit_loss > 0]
        losing_trades = [t for t in sell_trades if t.profit_loss < 0]

        win_rate = (len(winning_trades) / len(sell_trades)) * 100 if sell_trades else 0

        total_profit = sum(t.profit_loss for t in winning_trades)
        total_loss = abs(sum(t.profit_loss for t in losing_trades))
        net_profit = total_profit - total_loss

        avg_profit_per_trade = net_profit / len(sell_trades) if sell_trades else 0
        avg_winning_trade = total_profit / len(winning_trades) if winning_trades else 0
        avg_losing_trade = total_loss / len(losing_trades) if losing_trades else 0

        largest_win = max((t.profit_loss for t in winning_trades), default=0)
        largest_loss = abs(min((t.profit_loss for t in losing_trades), default=0))

        max_drawdown = self._calculate_max_drawdown(sell_trades)

        sharpe_ratio = self._calculate_sharpe_ratio(sell_trades)

        avg_holding_period = self._calculate_avg_holding_period(trades)

        return PerformanceMetrics(
            period=period,
            total_trades=len(sell_trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            total_profit=total_profit,
            total_loss=total_loss,
            net_profit=net_profit,
            avg_profit_per_trade=avg_profit_per_trade,
            avg_winning_trade=avg_winning_trade,
            avg_losing_trade=avg_losing_trade,
            largest_win=largest_win,
            largest_loss=largest_loss,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            avg_holding_period=avg_holding_period
        )

    def _calculate_max_drawdown(self, trades: List[TradeRecord]) -> float:
        """최대 낙폭 계산 (간단 버전)"""
        if not trades:
            return 0.0

        cumulative = []
        total = 0
        for trade in sorted(trades, key=lambda t: t.timestamp):
            total += trade.profit_loss
            cumulative.append(total)

        if not cumulative:
            return 0.0

        peak = cumulative[0]
        max_dd = 0

        for value in cumulative:
            if value > peak:
                peak = value
            dd = (peak - value) / peak * 100 if peak > 0 else 0
            max_dd = max(max_dd, dd)

        return max_dd

    def _calculate_sharpe_ratio(self, trades: List[TradeRecord]) -> Optional[float]:
        """샤프 비율 계산 (간단 버전)"""
        if not trades or len(trades) < 2:
            return None

        returns = [t.profit_loss_percent for t in trades if t.profit_loss_percent is not None]

        if not returns:
            return None

        avg_return = sum(returns) / len(returns)

        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5

        if std_dev == 0:
            return None

        sharpe = avg_return / std_dev

        return sharpe

    def _calculate_avg_holding_period(self, trades: List[TradeRecord]) -> Optional[float]:
        """평균 보유 기간 계산 (시간)"""
        buy_trades = {t.stock_code: t for t in trades if t.action == 'buy'}
        sell_trades = [t for t in trades if t.action == 'sell']

        holding_periods = []
        for sell in sell_trades:
            if sell.stock_code in buy_trades:
                buy = buy_trades[sell.stock_code]
                period = (sell.timestamp - buy.timestamp).total_seconds() / 3600
                holding_periods.append(period)

        if not holding_periods:
            return None

        return sum(holding_periods) / len(holding_periods)

    def get_performance_summary(self) -> Dict[str, Any]:
        """대시보드용 성과 요약"""
        daily = self.calculate_metrics('daily')
        weekly = self.calculate_metrics('weekly')
        monthly = self.calculate_metrics('monthly')
        all_time = self.calculate_metrics('all')

        return {
            'daily': daily.to_dict(),
            'weekly': weekly.to_dict(),
            'monthly': monthly.to_dict(),
            'all_time': all_time.to_dict()
        }
