ai/advanced_backtester.py
고급 백테스팅 엔진 (v5.11 NEW)

Features:
- 다양한 전략 백테스팅
- 슬리피지 & 수수료 반영
- 리스크 메트릭 계산
- Monte Carlo 시뮬레이션
- 워크포워드 분석
- 성능 리포트 생성
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import statistics

from utils.logger_new import get_logger

logger = get_logger()


class OrderType(Enum):
    """주문 유형"""
    MARKET = "market"
    LIMIT = "limit"


class OrderSide(Enum):
    """주문 방향"""
    BUY = "buy"
    SELL = "sell"


@dataclass
class BacktestOrder:
    """백테스트 주문"""
    timestamp: datetime
    stock_code: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: float
    filled_price: Optional[float] = None
    filled: bool = False
    commission: float = 0
    slippage: float = 0


@dataclass
class BacktestTrade:
    """백테스트 거래"""
    entry_time: datetime
    exit_time: datetime
    stock_code: str
    quantity: int
    entry_price: float
    exit_price: float
    pnl: float
    pnl_percent: float
    commission: float
    holding_days: int
    win: bool


@dataclass
class BacktestResult:
    """백테스트 결과"""
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_percent: float
    max_drawdown: float
    max_drawdown_percent: float
    sharpe_ratio: float
    sortino_ratio: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    max_win: float
    max_loss: float
    avg_holding_days: float
    total_commission: float
    trades: List[BacktestTrade] = field(default_factory=list)
    equity_curve: List[Tuple[datetime, float]] = field(default_factory=list)
    drawdown_curve: List[Tuple[datetime, float]] = field(default_factory=list)


class AdvancedBacktester:
    """
    고급 백테스팅 엔진 (v5.11)

    Features:
    - 실제 거래 비용 반영 (슬리피지, 수수료)
    - 포지션 관리
    - 리스크 메트릭
    - Monte Carlo 시뮬레이션
    - 성능 분석
    """

    def __init__(
        self,
        initial_capital: float = 10000000,
        commission_rate: float = 0.00015,
        slippage_rate: float = 0.001,
        tax_rate: float = 0.0023,
        risk_free_rate: float = 0.02
    ):
        초기화

        Args:
            initial_capital: 초기 자본
            commission_rate: 수수료율
            slippage_rate: 슬리피지율
            tax_rate: 세율 (매도세)
            risk_free_rate: 무위험 수익률
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.tax_rate = tax_rate
        self.risk_free_rate = risk_free_rate

        self.cash = initial_capital
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.orders: List[BacktestOrder] = []
        self.trades: List[BacktestTrade] = []
        self.equity_curve: List[Tuple[datetime, float]] = []
        self.current_time: Optional[datetime] = None

        logger.info(f"Advanced Backtester initialized - Capital: {initial_capital:,}")

    def run_backtest(
        self,
        strategy: Callable,
        data: Dict[str, List[Dict]],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> BacktestResult:
        백테스트 실행

        Args:
            strategy: 전략 함수 (context, data) -> signals
            data: 주가 데이터
            start_date: 시작일
            end_date: 종료일

        Returns:
            백테스트 결과
        self._reset()

        all_dates = self._get_all_dates(data, start_date, end_date)

        logger.info(f"Running backtest: {len(all_dates)} days, {len(data)} stocks")

        for i, date in enumerate(all_dates):
            self.current_time = date

            current_data = self._get_data_until(data, date)

            try:
                signals = strategy(self, current_data)

                if signals:
                    self._execute_signals(signals, current_data)

            except Exception as e:
                logger.error(f"Strategy error on {date}: {e}")

            equity = self._calculate_equity(current_data)
            self.equity_curve.append((date, equity))

            if i % 30 == 0:
                logger.debug(f"Backtest progress: {i}/{len(all_dates)} days, Equity: {equity:,.0f}")

        self._close_all_positions(data)

        result = self._calculate_results()

        logger.info(f"Backtest complete: Return {result.total_return_percent:.2f}%, Sharpe {result.sharpe_ratio:.2f}")

        return result

    def buy(
        self,
        stock_code: str,
        quantity: int,
        price: Optional[float] = None,
        order_type: OrderType = OrderType.MARKET
    ) -> BacktestOrder:
        매수 주문

        Args:
            stock_code: 종목 코드
            quantity: 수량
            price: 가격 (None이면 시장가)
            order_type: 주문 유형

        Returns:
            주문 객체
        order = BacktestOrder(
            timestamp=self.current_time,
            stock_code=stock_code,
            side=OrderSide.BUY,
            order_type=order_type,
            quantity=quantity,
            price=price
        )

        self.orders.append(order)
        return order

    def sell(
        self,
        stock_code: str,
        quantity: int,
        price: Optional[float] = None,
        order_type: OrderType = OrderType.MARKET
    ) -> BacktestOrder:
        매도 주문

        Args:
            stock_code: 종목 코드
            quantity: 수량
            price: 가격 (None이면 시장가)
            order_type: 주문 유형

        Returns:
            주문 객체
        order = BacktestOrder(
            timestamp=self.current_time,
            stock_code=stock_code,
            side=OrderSide.SELL,
            order_type=order_type,
            quantity=quantity,
            price=price
        )

        self.orders.append(order)
        return order

    def get_position(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """포지션 조회"""
        return self.positions.get(stock_code)

    def has_position(self, stock_code: str) -> bool:
        """포지션 보유 여부"""
        return stock_code in self.positions

    def get_equity(self) -> float:
        """현재 자산 조회"""
        return self.cash + sum(
            pos['quantity'] * pos['current_price']
            for pos in self.positions.values()
        )

    def monte_carlo_simulation(
        self,
        result: BacktestResult,
        num_simulations: int = 1000,
        num_trades: Optional[int] = None
    ) -> Dict[str, Any]:
        Monte Carlo 시뮬레이션

        Args:
            result: 백테스트 결과
            num_simulations: 시뮬레이션 횟수
            num_trades: 거래 수 (None이면 원래 거래 수)

        Returns:
            시뮬레이션 결과
        if not result.trades:
            return {'error': 'No trades to simulate'}

        returns = [trade.pnl_percent for trade in result.trades]

        if num_trades is None:
            num_trades = len(returns)

        logger.info(f"Running Monte Carlo simulation: {num_simulations} simulations, {num_trades} trades each")

        final_equities = []

        for _ in range(num_simulations):
            simulated_returns = np.random.choice(returns, size=num_trades, replace=True)

            equity = self.initial_capital
            for ret in simulated_returns:
                equity *= (1 + ret / 100)

            final_equities.append(equity)

        final_returns = [(eq - self.initial_capital) / self.initial_capital * 100 for eq in final_equities]

        return {
            'num_simulations': num_simulations,
            'num_trades': num_trades,
            'mean_final_equity': statistics.mean(final_equities),
            'median_final_equity': statistics.median(final_equities),
            'std_final_equity': statistics.stdev(final_equities) if len(final_equities) > 1 else 0,
            'min_final_equity': min(final_equities),
            'max_final_equity': max(final_equities),
            'mean_return_pct': statistics.mean(final_returns),
            'percentile_5': np.percentile(final_returns, 5),
            'percentile_25': np.percentile(final_returns, 25),
            'percentile_50': np.percentile(final_returns, 50),
            'percentile_75': np.percentile(final_returns, 75),
            'percentile_95': np.percentile(final_returns, 95),
            'probability_of_profit': sum(1 for r in final_returns if r > 0) / len(final_returns) * 100
        }


    def _reset(self):
        """상태 초기화"""
        self.cash = self.initial_capital
        self.positions.clear()
        self.orders.clear()
        self.trades.clear()
        self.equity_curve.clear()
        self.current_time = None

    def _get_all_dates(
        self,
        data: Dict[str, List[Dict]],
        start: Optional[datetime],
        end: Optional[datetime]
    ) -> List[datetime]:
        all_dates = set()

        for stock_data in data.values():
            for bar in stock_data:
                date = bar.get('date')
                if isinstance(date, str):
                    date = datetime.fromisoformat(date)

                if start and date < start:
                    continue
                if end and date > end:
                    continue

                all_dates.add(date)

        return sorted(list(all_dates))

    def _get_data_until(
        self,
        data: Dict[str, List[Dict]],
        date: datetime
    ) -> Dict[str, List[Dict]]:
        result = {}

        for stock_code, bars in data.items():
            filtered = [
                bar for bar in bars
                if self._parse_date(bar.get('date')) <= date
            ]
            if filtered:
                result[stock_code] = filtered

        return result

    def _parse_date(self, date) -> datetime:
        """날짜 파싱"""
        if isinstance(date, datetime):
            return date
        elif isinstance(date, str):
            return datetime.fromisoformat(date)
        else:
            return datetime.now()

    def _execute_signals(self, signals: List[Dict], data: Dict[str, List[Dict]]):
        """신호 실행"""
        for signal in signals:
            action = signal.get('action')
            stock_code = signal.get('stock_code')
            quantity = signal.get('quantity', 0)

            if action == 'buy':
                self._execute_buy(stock_code, quantity, data)
            elif action == 'sell':
                self._execute_sell(stock_code, quantity, data)

    def _execute_buy(self, stock_code: str, quantity: int, data: Dict[str, List[Dict]]):
        """매수 실행"""
        if stock_code not in data or not data[stock_code]:
            return

        current_bar = data[stock_code][-1]
        price = current_bar.get('close', 0)

        if price <= 0:
            return

        filled_price = price * (1 + self.slippage_rate)

        cost = filled_price * quantity
        commission = cost * self.commission_rate
        total_cost = cost + commission

        if total_cost > self.cash:
            logger.debug(f"Insufficient cash for buy: {total_cost:,.0f} > {self.cash:,.0f}")
            return

        self.cash -= total_cost

        if stock_code in self.positions:
            pos = self.positions[stock_code]
            total_quantity = pos['quantity'] + quantity
            avg_price = (pos['avg_price'] * pos['quantity'] + filled_price * quantity) / total_quantity

            pos['quantity'] = total_quantity
            pos['avg_price'] = avg_price
            pos['current_price'] = price
        else:
            self.positions[stock_code] = {
                'quantity': quantity,
                'avg_price': filled_price,
                'entry_time': self.current_time,
                'current_price': price
            }

        logger.debug(f"Buy executed: {stock_code} x{quantity} @ {filled_price:.2f}")

    def _execute_sell(self, stock_code: str, quantity: int, data: Dict[str, List[Dict]]):
        """매도 실행"""
        if stock_code not in self.positions:
            return

        position = self.positions[stock_code]
        quantity = min(quantity, position['quantity'])

        if quantity <= 0:
            return

        if stock_code not in data or not data[stock_code]:
            return

        current_bar = data[stock_code][-1]
        price = current_bar.get('close', 0)

        if price <= 0:
            return

        filled_price = price * (1 - self.slippage_rate)

        proceeds = filled_price * quantity
        commission = proceeds * self.commission_rate
        tax = proceeds * self.tax_rate
        net_proceeds = proceeds - commission - tax

        self.cash += net_proceeds

        entry_price = position['avg_price']
        pnl = (filled_price - entry_price) * quantity - commission - tax
        pnl_percent = (filled_price - entry_price) / entry_price * 100

        holding_days = (self.current_time - position['entry_time']).days

        trade = BacktestTrade(
            entry_time=position['entry_time'],
            exit_time=self.current_time,
            stock_code=stock_code,
            quantity=quantity,
            entry_price=entry_price,
            exit_price=filled_price,
            pnl=pnl,
            pnl_percent=pnl_percent,
            commission=commission + tax,
            holding_days=holding_days,
            win=pnl > 0
        )

        self.trades.append(trade)

        position['quantity'] -= quantity

        if position['quantity'] <= 0:
            del self.positions[stock_code]

        logger.debug(f"Sell executed: {stock_code} x{quantity} @ {filled_price:.2f}, P&L: {pnl:,.0f}")

    def _calculate_equity(self, data: Dict[str, List[Dict]]) -> float:
        """현재 자산 계산"""
        position_value = 0

        for stock_code, position in self.positions.items():
            if stock_code in data and data[stock_code]:
                current_price = data[stock_code][-1].get('close', 0)
                position['current_price'] = current_price
                position_value += current_price * position['quantity']

        return self.cash + position_value

    def _close_all_positions(self, data: Dict[str, List[Dict]]):
        """모든 포지션 청산"""
        for stock_code in list(self.positions.keys()):
            position = self.positions[stock_code]
            self._execute_sell(stock_code, position['quantity'], data)

    def _calculate_results(self) -> BacktestResult:
        """결과 계산"""
        final_capital = self.cash

        total_return = final_capital - self.initial_capital
        total_return_percent = (total_return / self.initial_capital) * 100

        max_drawdown, max_drawdown_percent = self._calculate_max_drawdown()

        if self.trades:
            winning_trades = [t for t in self.trades if t.win]
            losing_trades = [t for t in self.trades if not t.win]

            win_rate = len(winning_trades) / len(self.trades) * 100

            avg_win = statistics.mean([t.pnl for t in winning_trades]) if winning_trades else 0
            avg_loss = statistics.mean([t.pnl for t in losing_trades]) if losing_trades else 0
            max_win = max([t.pnl for t in winning_trades]) if winning_trades else 0
            max_loss = min([t.pnl for t in losing_trades]) if losing_trades else 0

            total_wins = sum(t.pnl for t in winning_trades)
            total_losses = abs(sum(t.pnl for t in losing_trades))
            profit_factor = total_wins / total_losses if total_losses > 0 else 0

            avg_holding_days = statistics.mean([t.holding_days for t in self.trades])
            total_commission = sum(t.commission for t in self.trades)
        else:
            win_rate = 0
            avg_win = avg_loss = max_win = max_loss = 0
            profit_factor = 0
            avg_holding_days = 0
            total_commission = 0
            winning_trades = []
            losing_trades = []

        sharpe_ratio = self._calculate_sharpe_ratio()
        sortino_ratio = self._calculate_sortino_ratio()

        drawdown_curve = self._calculate_drawdown_curve()

        return BacktestResult(
            initial_capital=self.initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            total_return_percent=total_return_percent,
            max_drawdown=max_drawdown,
            max_drawdown_percent=max_drawdown_percent,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=len(self.trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            avg_win=avg_win,
            avg_loss=avg_loss,
            max_win=max_win,
            max_loss=max_loss,
            avg_holding_days=avg_holding_days,
            total_commission=total_commission,
            trades=self.trades,
            equity_curve=self.equity_curve,
            drawdown_curve=drawdown_curve
        )

    def _calculate_max_drawdown(self) -> Tuple[float, float]:
        """최대 낙폭 계산"""
        if not self.equity_curve:
            return 0, 0

        peak = self.equity_curve[0][1]
        max_dd = 0
        max_dd_percent = 0

        for _, equity in self.equity_curve:
            if equity > peak:
                peak = equity

            dd = peak - equity
            dd_percent = (dd / peak) * 100

            if dd > max_dd:
                max_dd = dd
                max_dd_percent = dd_percent

        return max_dd, max_dd_percent

    def _calculate_drawdown_curve(self) -> List[Tuple[datetime, float]]:
        """낙폭 곡선 계산"""
        if not self.equity_curve:
            return []

        drawdown_curve = []
        peak = self.equity_curve[0][1]

        for date, equity in self.equity_curve:
            if equity > peak:
                peak = equity

            dd_percent = ((peak - equity) / peak) * 100
            drawdown_curve.append((date, dd_percent))

        return drawdown_curve

    def _calculate_sharpe_ratio(self) -> float:
        """Sharpe Ratio 계산"""
        if len(self.equity_curve) < 2:
            return 0

        returns = []
        for i in range(1, len(self.equity_curve)):
            prev_equity = self.equity_curve[i-1][1]
            curr_equity = self.equity_curve[i][1]
            daily_return = (curr_equity - prev_equity) / prev_equity
            returns.append(daily_return)

        if not returns:
            return 0

        avg_return = statistics.mean(returns)
        std_return = statistics.stdev(returns) if len(returns) > 1 else 0

        if std_return == 0:
            return 0

        daily_rf_rate = self.risk_free_rate / 252
        sharpe = (avg_return - daily_rf_rate) / std_return * np.sqrt(252)

        return sharpe

    def _calculate_sortino_ratio(self) -> float:
        """Sortino Ratio 계산 (하방 변동성만 고려)"""
        if len(self.equity_curve) < 2:
            return 0

        returns = []
        for i in range(1, len(self.equity_curve)):
            prev_equity = self.equity_curve[i-1][1]
            curr_equity = self.equity_curve[i][1]
            daily_return = (curr_equity - prev_equity) / prev_equity
            returns.append(daily_return)

        if not returns:
            return 0

        avg_return = statistics.mean(returns)

        downside_returns = [r for r in returns if r < 0]

        if not downside_returns:
            return 0

        downside_std = statistics.stdev(downside_returns) if len(downside_returns) > 1 else 0

        if downside_std == 0:
            return 0

        daily_rf_rate = self.risk_free_rate / 252
        sortino = (avg_return - daily_rf_rate) / downside_std * np.sqrt(252)

        return sortino


__all__ = [
    'AdvancedBacktester',
    'BacktestResult',
    'BacktestTrade',
    'BacktestOrder',
    'OrderType',
    'OrderSide'
]
