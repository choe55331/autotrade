"""
Professional Backtesting Engine
Comprehensive backtesting framework for trading strategies
"""

import numpy as np
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import pandas as pd

from ..utils.logger import setup_logger
from ..strategy.advanced_risk_analytics import AdvancedRiskAnalytics

logger = setup_logger(__name__)


@dataclass
class BacktestConfig:
    """Backtesting configuration"""
    initial_capital: float = 10000000  # 10M KRW
    commission_rate: float = 0.0015  # 0.15%
    slippage_rate: float = 0.001  # 0.1%
    position_size: float = 0.20  # 20% per position
    max_positions: int = 5
    stop_loss: float = -0.05  # -5%
    take_profit: float = 0.10  # +10%


@dataclass
class Trade:
    """Individual trade record"""
    entry_date: datetime
    exit_date: Optional[datetime] = None
    stock_code: str = ""
    entry_price: float = 0
    exit_price: float = 0
    quantity: int = 0
    side: str = "BUY"
    profit_loss: float = 0
    profit_loss_pct: float = 0
    commission: float = 0
    reason: str = ""


@dataclass
class BacktestResults:
    """Backtesting results"""
    # Performance
    total_return: float = 0
    total_return_pct: float = 0
    annualized_return: float = 0

    # Risk metrics
    sharpe_ratio: float = 0
    sortino_ratio: float = 0
    max_drawdown: float = 0
    max_drawdown_pct: float = 0

    # Trading stats
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0

    # Profit stats
    avg_win: float = 0
    avg_loss: float = 0
    largest_win: float = 0
    largest_loss: float = 0
    profit_factor: float = 0

    # Equity curve
    equity_curve: List[float] = field(default_factory=list)
    daily_returns: List[float] = field(default_factory=list)

    # Trades
    trades: List[Trade] = field(default_factory=list)

    # Duration
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration_days: int = 0


class BacktestEngine:
    """
    Professional backtesting engine

    Features:
    - Historical data simulation
    - Realistic execution (slippage, commission)
    - Multiple strategies support
    - Comprehensive performance analytics
    - Equity curve visualization
    - Risk metrics calculation
    - Trade-by-trade analysis
    """

    def __init__(self, config: Optional[BacktestConfig] = None):
        """
        Initialize backtest engine

        Args:
            config: Backtesting configuration
        """
        self.config = config or BacktestConfig()
        self.risk_analytics = AdvancedRiskAnalytics()

        # State
        self.cash = self.config.initial_capital
        self.positions: Dict[str, Dict] = {}
        self.equity_curve = [self.config.initial_capital]
        self.trades: List[Trade] = []

        logger.info(
            f"Backtest Engine initialized: "
            f"Initial capital={self.config.initial_capital:,.0f}원"
        )

    def run_backtest(
        self,
        strategy: Any,
        historical_data: Dict[str, pd.DataFrame],
        start_date: datetime,
        end_date: datetime
    ) -> BacktestResults:
        """
        Run backtest on historical data

        Args:
            strategy: Trading strategy instance
            historical_data: Dict of {stock_code: DataFrame with OHLCV}
            start_date: Start date
            end_date: End date

        Returns:
            Backtesting results
        """
        logger.info(
            f"Starting backtest: {start_date.date()} to {end_date.date()}"
        )

        # Reset state
        self._reset_state()

        # Get all trading dates
        sample_data = list(historical_data.values())[0]
        trading_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        trading_dates = [d for d in trading_dates if d in sample_data.index]

        # Run simulation day by day
        for current_date in trading_dates:
            self._simulate_day(strategy, historical_data, current_date)

        # Close remaining positions
        self._close_all_positions(historical_data, trading_dates[-1])

        # Calculate results
        results = self._calculate_results(start_date, end_date)

        logger.info(
            f"Backtest complete: Return={results.total_return_pct:.2f}%, "
            f"Sharpe={results.sharpe_ratio:.2f}, "
            f"Win Rate={results.win_rate:.1f}%"
        )

        return results

    def _simulate_day(
        self,
        strategy: Any,
        historical_data: Dict[str, pd.DataFrame],
        current_date: datetime
    ):
        """
        Simulate one trading day
        """
        # Update positions with current prices
        self._update_positions(historical_data, current_date)

        # Check exit conditions for existing positions
        self._check_exit_conditions(historical_data, current_date)

        # Generate new signals
        signals = self._generate_signals(strategy, historical_data, current_date)

        # Execute buy signals
        for signal in signals:
            if signal['action'] == 'BUY':
                self._execute_buy(
                    stock_code=signal['stock_code'],
                    price=signal['price'],
                    date=current_date
                )

        # Update equity curve
        total_equity = self._calculate_total_equity(historical_data, current_date)
        self.equity_curve.append(total_equity)

    def _update_positions(
        self,
        historical_data: Dict[str, pd.DataFrame],
        current_date: datetime
    ):
        """
        Update all positions with current prices
        """
        for stock_code, position in self.positions.items():
            if stock_code in historical_data:
                data = historical_data[stock_code]
                if current_date in data.index:
                    current_price = data.loc[current_date, 'close']
                    position['current_price'] = current_price

                    # Calculate P&L
                    cost = position['entry_price'] * position['quantity']
                    value = current_price * position['quantity']
                    position['profit_loss'] = value - cost
                    position['profit_loss_pct'] = (
                        (current_price - position['entry_price']) / position['entry_price']
                    ) * 100

    def _check_exit_conditions(
        self,
        historical_data: Dict[str, pd.DataFrame],
        current_date: datetime
    ):
        """
        Check if any positions should be closed
        """
        to_close = []

        for stock_code, position in self.positions.items():
            pl_pct = position.get('profit_loss_pct', 0)

            # Stop loss
            if pl_pct <= self.config.stop_loss * 100:
                to_close.append((stock_code, 'STOP_LOSS'))

            # Take profit
            elif pl_pct >= self.config.take_profit * 100:
                to_close.append((stock_code, 'TAKE_PROFIT'))

        # Execute closes
        for stock_code, reason in to_close:
            self._execute_sell(
                stock_code=stock_code,
                date=current_date,
                reason=reason,
                historical_data=historical_data
            )

    def _generate_signals(
        self,
        strategy: Any,
        historical_data: Dict[str, pd.DataFrame],
        current_date: datetime
    ) -> List[Dict]:
        """
        Generate trading signals from strategy
        """
        signals = []

        # Can only buy if we have available slots
        if len(self.positions) >= self.config.max_positions:
            return signals

        # Get signals from strategy for each stock
        for stock_code, data in historical_data.items():
            if current_date not in data.index:
                continue

            # Get historical window up to current date
            hist_window = data.loc[:current_date].tail(60)

            if len(hist_window) < 20:
                continue

            # Prepare stock data for strategy
            stock_data = {
                'stock_code': stock_code,
                'current_price': hist_window['close'].iloc[-1],
                'volume': hist_window['volume'].iloc[-1],
                'price_history': hist_window['close'].tolist(),
                'volume_history': hist_window['volume'].tolist()
            }

            # Get strategy signal
            try:
                signal = strategy.generate_signal(stock_data)

                if signal and signal.get('action') == 'BUY':
                    signals.append({
                        'stock_code': stock_code,
                        'action': 'BUY',
                        'price': stock_data['current_price'],
                        'score': signal.get('score', 0)
                    })
            except Exception as e:
                logger.error(f"Signal generation error for {stock_code}: {e}")

        # Sort by score and take top signals
        signals.sort(key=lambda x: x['score'], reverse=True)

        # Limit to available slots
        available_slots = self.config.max_positions - len(self.positions)
        signals = signals[:available_slots]

        return signals

    def _execute_buy(
        self,
        stock_code: str,
        price: float,
        date: datetime
    ):
        """
        Execute buy order
        """
        # Check if already have position
        if stock_code in self.positions:
            return

        # Calculate position size
        position_value = self.cash * self.config.position_size
        quantity = int(position_value / price)

        if quantity <= 0:
            return

        # Apply slippage (pay more when buying)
        execution_price = price * (1 + self.config.slippage_rate)

        # Calculate costs
        total_cost = execution_price * quantity
        commission = total_cost * self.config.commission_rate
        total_cost += commission

        # Check if we have enough cash
        if total_cost > self.cash:
            return

        # Execute
        self.cash -= total_cost

        self.positions[stock_code] = {
            'stock_code': stock_code,
            'quantity': quantity,
            'entry_price': execution_price,
            'current_price': execution_price,
            'entry_date': date,
            'commission': commission,
            'profit_loss': 0,
            'profit_loss_pct': 0
        }

        logger.debug(
            f"BUY: {stock_code} x{quantity} @ {execution_price:,.0f}원 "
            f"({date.date()})"
        )

    def _execute_sell(
        self,
        stock_code: str,
        date: datetime,
        reason: str,
        historical_data: Dict[str, pd.DataFrame]
    ):
        """
        Execute sell order
        """
        if stock_code not in self.positions:
            return

        position = self.positions[stock_code]

        # Get current price
        if stock_code in historical_data and date in historical_data[stock_code].index:
            exit_price = historical_data[stock_code].loc[date, 'close']
        else:
            exit_price = position['current_price']

        # Apply slippage (receive less when selling)
        execution_price = exit_price * (1 - self.config.slippage_rate)

        # Calculate proceeds
        proceeds = execution_price * position['quantity']
        commission = proceeds * self.config.commission_rate
        net_proceeds = proceeds - commission

        # Update cash
        self.cash += net_proceeds

        # Calculate P&L
        cost = position['entry_price'] * position['quantity'] + position['commission']
        profit_loss = net_proceeds - cost
        profit_loss_pct = (profit_loss / cost) * 100

        # Record trade
        trade = Trade(
            entry_date=position['entry_date'],
            exit_date=date,
            stock_code=stock_code,
            entry_price=position['entry_price'],
            exit_price=execution_price,
            quantity=position['quantity'],
            side='BUY',
            profit_loss=profit_loss,
            profit_loss_pct=profit_loss_pct,
            commission=position['commission'] + commission,
            reason=reason
        )

        self.trades.append(trade)

        logger.debug(
            f"SELL: {stock_code} x{position['quantity']} @ {execution_price:,.0f}원 "
            f"P&L={profit_loss:+,.0f}원 ({profit_loss_pct:+.1f}%) - {reason}"
        )

        # Remove position
        del self.positions[stock_code]

    def _close_all_positions(
        self,
        historical_data: Dict[str, pd.DataFrame],
        final_date: datetime
    ):
        """
        Close all remaining positions at end of backtest
        """
        for stock_code in list(self.positions.keys()):
            self._execute_sell(
                stock_code=stock_code,
                date=final_date,
                reason='BACKTEST_END',
                historical_data=historical_data
            )

    def _calculate_total_equity(
        self,
        historical_data: Dict[str, pd.DataFrame],
        current_date: datetime
    ) -> float:
        """
        Calculate total equity (cash + positions value)
        """
        total = self.cash

        for stock_code, position in self.positions.items():
            if stock_code in historical_data and current_date in historical_data[stock_code].index:
                price = historical_data[stock_code].loc[current_date, 'close']
                total += price * position['quantity']

        return total

    def _calculate_results(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> BacktestResults:
        """
        Calculate comprehensive backtest results
        """
        results = BacktestResults()

        # Basic info
        results.start_date = start_date
        results.end_date = end_date
        results.duration_days = (end_date - start_date).days

        # Equity curve
        results.equity_curve = self.equity_curve

        # Returns
        final_equity = self.equity_curve[-1]
        initial_equity = self.equity_curve[0]
        results.total_return = final_equity - initial_equity
        results.total_return_pct = (results.total_return / initial_equity) * 100

        # Annualized return
        years = results.duration_days / 365.25
        if years > 0:
            results.annualized_return = (
                ((final_equity / initial_equity) ** (1 / years)) - 1
            ) * 100

        # Daily returns
        daily_returns = []
        for i in range(1, len(self.equity_curve)):
            ret = (
                (self.equity_curve[i] - self.equity_curve[i-1]) / self.equity_curve[i-1]
            )
            daily_returns.append(ret)
        results.daily_returns = daily_returns

        # Risk metrics
        if len(daily_returns) > 1:
            results.sharpe_ratio = self.risk_analytics.calculate_sharpe_ratio(daily_returns)
            results.sortino_ratio = self.risk_analytics.calculate_sortino_ratio(daily_returns)

            dd_info = self.risk_analytics.calculate_maximum_drawdown(self.equity_curve)
            results.max_drawdown = dd_info['max_drawdown']
            results.max_drawdown_pct = dd_info['max_drawdown_pct']

        # Trading statistics
        results.trades = self.trades
        results.total_trades = len(self.trades)

        winning_trades = [t for t in self.trades if t.profit_loss > 0]
        losing_trades = [t for t in self.trades if t.profit_loss < 0]

        results.winning_trades = len(winning_trades)
        results.losing_trades = len(losing_trades)

        if results.total_trades > 0:
            results.win_rate = (results.winning_trades / results.total_trades) * 100

        # Profit statistics
        if winning_trades:
            results.avg_win = np.mean([t.profit_loss for t in winning_trades])
            results.largest_win = max([t.profit_loss for t in winning_trades])

        if losing_trades:
            results.avg_loss = np.mean([t.profit_loss for t in losing_trades])
            results.largest_loss = min([t.profit_loss for t in losing_trades])

        # Profit factor
        total_wins = sum([t.profit_loss for t in winning_trades])
        total_losses = abs(sum([t.profit_loss for t in losing_trades]))

        if total_losses > 0:
            results.profit_factor = total_wins / total_losses

        return results

    def _reset_state(self):
        """Reset backtest state"""
        self.cash = self.config.initial_capital
        self.positions = {}
        self.equity_curve = [self.config.initial_capital]
        self.trades = []

    def generate_report(self, results: BacktestResults) -> str:
        """
        Generate text report

        Args:
            results: Backtest results

        Returns:
            Formatted report string
        """
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║              BACKTESTING RESULTS REPORT                     ║
╚══════════════════════════════════════════════════════════════╝

PERIOD: {results.start_date.date()} to {results.end_date.date()} ({results.duration_days} days)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERFORMANCE METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Return:           {results.total_return:>15,.0f}원 ({results.total_return_pct:+.2f}%)
Annualized Return:      {results.annualized_return:>15.2f}%
Initial Capital:        {self.config.initial_capital:>15,.0f}원
Final Equity:           {results.equity_curve[-1]:>15,.0f}원

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RISK METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sharpe Ratio:           {results.sharpe_ratio:>15.2f}
Sortino Ratio:          {results.sortino_ratio:>15.2f}
Maximum Drawdown:       {results.max_drawdown:>15,.0f}원 ({results.max_drawdown_pct:.2f}%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRADING STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Trades:           {results.total_trades:>15,}
Winning Trades:         {results.winning_trades:>15,}
Losing Trades:          {results.losing_trades:>15,}
Win Rate:               {results.win_rate:>15.1f}%

Average Win:            {results.avg_win:>15,.0f}원
Average Loss:           {results.avg_loss:>15,.0f}원
Largest Win:            {results.largest_win:>15,.0f}원
Largest Loss:           {results.largest_loss:>15,.0f}원
Profit Factor:          {results.profit_factor:>15.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return report
