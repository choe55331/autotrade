"""
Advanced Risk Manager v7.0
Unified risk management system combining all previous implementations

Features:
- Dynamic mode switching based on performance (from DynamicRiskManager)
- Kelly Criterion position sizing (from UnifiedRiskManager)
- VaR (Value at Risk) calculation (from UnifiedRiskManager)
- Comprehensive loss limits and position tracking (from RiskManager)
- Daily/weekly profit tracking
- Emergency stop mechanisms
- State persistence
"""

from enum import Enum
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from pathlib import Path
import numpy as np

from utils.logger_new import get_logger
from config.config_manager import get_config

logger = get_logger()


class RiskMode(Enum):
    """Risk operating modes"""
    AGGRESSIVE = "aggressive"
    NORMAL = "normal"
    CONSERVATIVE = "conservative"
    VERY_CONSERVATIVE = "very_conservative"
    DEFENSIVE = "defensive"


@dataclass
class RiskModeConfig:
    """Configuration for each risk mode"""
    mode: RiskMode
    max_open_positions: int
    risk_per_trade_ratio: float
    max_position_size_pct: float
    take_profit_ratio: float
    stop_loss_ratio: float
    trailing_stop_pct: float
    ai_min_score: float
    max_daily_loss_pct: float
    max_single_loss_pct: float

    trigger_return_min: Optional[float] = None
    trigger_return_max: Optional[float] = None


class AdvancedRiskManager:
    """
    Advanced unified risk management system

    Combines features from:
    - DynamicRiskManager: Performance-based mode switching
    - UnifiedRiskManager: Kelly Criterion, VaR, quantitative methods
    - RiskManager: Basic loss limits, emergency stops
    """

    def __init__(self, initial_capital: float, mode: RiskMode = RiskMode.NORMAL):
        """
        Initialize advanced risk manager

        Args:
            initial_capital: Initial capital amount
            mode: Starting risk mode
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.current_mode = mode

        self.config = get_config()
        self.risk_config = self.config.risk_management

        self.daily_profit_loss = 0.0
        self.weekly_profit_loss = 0.0
        self.total_profit_loss = 0.0
        self.consecutive_losses = 0

        self.trading_enabled = True
        self.emergency_stop = False

        self.daily_reset_time = datetime.now().date()
        self.weekly_reset_time = datetime.now() - timedelta(days=datetime.now().weekday())
        self.mode_changed_at = datetime.now()

        self.open_positions = []
        self.position_history = []
        self.trade_history = []

        self.state_file = Path('data/advanced_risk_manager_state.json')

        self._load_mode_configs()

        logger.info(
            f"🛡️ Advanced Risk Manager v7.0 initialized "
            f"(capital: {self.initial_capital:,}원, mode: {self.current_mode.value})"
        )

    def _load_mode_configs(self):
        """Load configuration for all risk modes"""
        self.mode_configs = {}

        aggressive_cfg = self.risk_config.get('aggressive', {})
        self.mode_configs[RiskMode.AGGRESSIVE] = RiskModeConfig(
            mode=RiskMode.AGGRESSIVE,
            max_open_positions=aggressive_cfg.get('max_open_positions', 12),
            risk_per_trade_ratio=aggressive_cfg.get('risk_per_trade_ratio', 0.25),
            max_position_size_pct=15.0,
            take_profit_ratio=aggressive_cfg.get('take_profit_ratio', 0.15),
            stop_loss_ratio=aggressive_cfg.get('stop_loss_ratio', -0."07"),
            trailing_stop_pct=5.0,
            ai_min_score=aggressive_cfg.get('ai_min_score', 6.5),
            max_daily_loss_pct=8.0,
            max_single_loss_pct=5.0,
            trigger_return_min=0."05"
        )

        normal_cfg = self.risk_config.get('normal', {})
        self.mode_configs[RiskMode.NORMAL] = RiskModeConfig(
            mode=RiskMode.NORMAL,
            max_open_positions=normal_cfg.get('max_open_positions', 10),
            risk_per_trade_ratio=normal_cfg.get('risk_per_trade_ratio', 0.20),
            max_position_size_pct=10.0,
            take_profit_ratio=normal_cfg.get('take_profit_ratio', 0.10),
            stop_loss_ratio=normal_cfg.get('stop_loss_ratio', -0."05"),
            trailing_stop_pct=3.0,
            ai_min_score=normal_cfg.get('ai_min_score', 7.0),
            max_daily_loss_pct=5.0,
            max_single_loss_pct=3.0,
            trigger_return_min=-0."05",
            trigger_return_max=0."05"
        )

        conservative_cfg = self.risk_config.get('conservative', {})
        self.mode_configs[RiskMode.CONSERVATIVE] = RiskModeConfig(
            mode=RiskMode.CONSERVATIVE,
            max_open_positions=conservative_cfg.get('max_open_positions', 7),
            risk_per_trade_ratio=conservative_cfg.get('risk_per_trade_ratio', 0.15),
            max_position_size_pct=5.0,
            take_profit_ratio=conservative_cfg.get('take_profit_ratio', 0."08"),
            stop_loss_ratio=conservative_cfg.get('stop_loss_ratio', -0."04"),
            trailing_stop_pct=2.0,
            ai_min_score=conservative_cfg.get('ai_min_score', 7.5),
            max_daily_loss_pct=3.0,
            max_single_loss_pct=2.0,
            trigger_return_min=-0.10,
            trigger_return_max=-0."05"
        )

        very_conservative_cfg = self.risk_config.get('very_conservative', {})
        self.mode_configs[RiskMode.VERY_CONSERVATIVE] = RiskModeConfig(
            mode=RiskMode.VERY_CONSERVATIVE,
            max_open_positions=very_conservative_cfg.get('max_open_positions', 5),
            risk_per_trade_ratio=very_conservative_cfg.get('risk_per_trade_ratio', 0.10),
            max_position_size_pct=3.0,
            take_profit_ratio=very_conservative_cfg.get('take_profit_ratio', 0."05"),
            stop_loss_ratio=very_conservative_cfg.get('stop_loss_ratio', -0."03"),
            trailing_stop_pct=1.5,
            ai_min_score=very_conservative_cfg.get('ai_min_score', 8.0),
            max_daily_loss_pct=2.0,
            max_single_loss_pct=1.5,
            trigger_return_max=-0.10
        )

        self.mode_configs[RiskMode.DEFENSIVE] = RiskModeConfig(
            mode=RiskMode.DEFENSIVE,
            max_open_positions=2,
            risk_per_trade_ratio=0."05",
            max_position_size_pct=3.0,
            take_profit_ratio=0."05",
            stop_loss_ratio=-0."02",
            trailing_stop_pct=1.5,
            ai_min_score=8.5,
            max_daily_loss_pct=2.0,
            max_single_loss_pct=1.5,
            trigger_return_max=-0.15
        )

    def update_capital(self, current_capital: float):
        """
        Update current capital and evaluate mode switching

        Args:
            current_capital: Current capital amount
        """
        previous_capital = self.current_capital
        self.current_capital = current_capital

        return_rate = self.get_return_rate()

        logger.info(
            f"[MONEY] Capital updated: {previous_capital:,}원 -> {current_capital:,}원 "
            f"(return: {return_rate*100:+.2f}%)"
        )

        self._evaluate_mode_switch()

    def get_return_rate(self) -> float:
        """Calculate current return rate"""
        if self.initial_capital == 0:
            return 0.0
        return (self.current_capital - self.initial_capital) / self.initial_capital

    def _evaluate_mode_switch(self):
        """Evaluate and potentially switch risk mode based on performance"""
        return_rate = self.get_return_rate()
        new_mode = self._determine_optimal_mode(return_rate)

        if new_mode != self.current_mode:
            self._switch_mode(new_mode, return_rate)

    def _determine_optimal_mode(self, return_rate: float) -> RiskMode:
        """
        Determine optimal risk mode based on return rate and conditions

        Args:
            return_rate: Current return rate

        Returns:
            Optimal RiskMode
        """
        if return_rate <= -0.15:
            return RiskMode.DEFENSIVE

        if return_rate <= -0.10:
            return RiskMode.VERY_CONSERVATIVE

        if -0.10 < return_rate <= -0."05":
            return RiskMode.CONSERVATIVE

        if return_rate >= 0.10:
            return RiskMode.AGGRESSIVE

        if 0."05" <= return_rate < 0.10:
            return RiskMode.AGGRESSIVE if self.consecutive_losses == 0 else RiskMode.NORMAL

        return RiskMode.NORMAL

    def _switch_mode(self, new_mode: RiskMode, return_rate: float):
        """
        Switch to new risk mode

        Args:
            new_mode: New risk mode
            return_rate: Current return rate
        """
        old_mode = self.current_mode
        self.current_mode = new_mode
        self.mode_changed_at = datetime.now()

        logger.warning(
            f"🔄 Risk mode changed: {old_mode.value} -> {new_mode.value} "
            f"(return: {return_rate*100:+.2f}%)"
        )

        config = self.get_current_mode_config()
        logger.info(
            f"📋 New risk settings:\n"
            f"  - Max positions: {config.max_open_positions}\n"
            f"  - Risk per trade: {config.risk_per_trade_ratio*100:.1f}%\n"
            f"  - Max position size: {config.max_position_size_pct:.1f}%\n"
            f"  - Target profit: {config.take_profit_ratio*100:.1f}%\n"
            f"  - Stop loss: {config.stop_loss_ratio*100:.1f}%\n"
            f"  - AI min score: {config.ai_min_score:.1f}"
        )

    def get_current_mode_config(self) -> RiskModeConfig:
        """Get current risk mode configuration"""
        return self.mode_configs[self.current_mode]

    def should_open_position(self, current_positions: int) -> bool:
        """
        Check if new position can be opened

        Args:
            current_positions: Current number of open positions

        Returns:
            True if position can be opened
        """
        if self.emergency_stop:
            return False

        if not self.trading_enabled:
            return False

        config = self.get_current_mode_config()
        if current_positions >= config.max_open_positions:
            return False

        if self._check_daily_loss_limit():
            return False

        if self._check_weekly_loss_limit():
            return False

        return True

    def calculate_position_size(
        self,
        stock_price: int,
        available_cash: int,
        win_rate: Optional[float] = None,
        risk_reward_ratio: Optional[float] = None
    ) -> int:
        """
        Calculate position size using multiple methods

        Args:
            stock_price: Stock price
            available_cash: Available cash
            win_rate: Win rate for Kelly Criterion (optional)
            risk_reward_ratio: Risk/reward ratio for Kelly Criterion (optional)

        Returns:
            Quantity to purchase
        """
        config = self.get_current_mode_config()

        max_position_value = self.current_capital * (config.max_position_size_pct / 100)

        risk_amount = self.current_capital * config.risk_per_trade_ratio
        position_value = min(risk_amount, max_position_value)

        if win_rate is not None and risk_reward_ratio is not None and win_rate > 0.5:
            kelly_pct = self._calculate_kelly_criterion(win_rate, risk_reward_ratio)
            kelly_position_value = self.current_capital * (kelly_pct / 2)
            position_value = min(position_value, kelly_position_value)

        position_value = min(position_value, available_cash)

        quantity = int(position_value / stock_price)

        return quantity

    def _calculate_kelly_criterion(self, win_rate: float, risk_reward_ratio: float) -> float:
        """
        Calculate Kelly Criterion for optimal position sizing

"""
        Formula: f* = (p * b - q) / b
        where:
        - f* = optimal position size (% of capital)
        - p = win probability
        - q = loss probability (1 - p)
        - b = win/loss ratio

        Args:
            win_rate: Win probability (0-1)
            risk_reward_ratio: Reward/risk ratio

        Returns:
            Optimal position size percentage
        """
        """
        if win_rate <= 0 or win_rate >= 1 or risk_reward_ratio <= 0:
            return 0.0

        p = win_rate
        q = 1 - win_rate
        b = risk_reward_ratio

        kelly = (p * b - q) / b

        if kelly < 0:
            return 0.0

        return min(kelly * 100, 25.0)

    def get_exit_thresholds(self, entry_price: int) -> Dict[str, Any]:
        """
        Calculate exit thresholds for position

        Args:
            entry_price: Entry price

        Returns:
            Dictionary with stop_loss, take_profit, trailing_stop_pct
        """
        config = self.get_current_mode_config()

        stop_loss = int(entry_price * (1 + config.stop_loss_ratio))
        take_profit = int(entry_price * (1 + config.take_profit_ratio))
        trailing_stop_pct = config.trailing_stop_pct

        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'trailing_stop_pct': trailing_stop_pct
        }

    def calculate_var(
        self,
        positions: List[Dict[str, Any]],
        confidence_level: float = 0.95
    ) -> float:
        """
        Calculate Value at Risk (VaR) for portfolio

        Args:
            positions: List of position dictionaries
            confidence_level: Confidence level (default 95%)

        Returns:
            VaR amount in currency units
        """
        if not positions:
            return 0.0

        config = self.get_current_mode_config()
        losses = []

        for position in positions:
            entry_price = position.get('entry_price', 0)
            quantity = position.get('quantity', 0)
            max_loss = entry_price * quantity * abs(config.stop_loss_ratio)
            losses.append(max_loss)

        total_var = sum(losses)

        return total_var

    def check_stop_loss(
        self,
        purchase_price: float,
        current_price: float
    ) -> Tuple[bool, str]:
        """
        Check if stop loss should trigger

        Args:
            purchase_price: Purchase price
            current_price: Current price

        Returns:
            (should_stop, reason)
        """
        if purchase_price == 0:
            return False, "No purchase price"

        loss_rate = (current_price - purchase_price) / purchase_price

        config = self.get_current_mode_config()
        emergency_threshold = config.stop_loss_ratio * 2

        if loss_rate <= emergency_threshold:
            return True, f"Emergency stop loss triggered ({loss_rate*100:.2f}% loss)"

        if loss_rate <= config.stop_loss_ratio:
            return True, f"Stop loss triggered ({loss_rate*100:.2f}% loss)"

        return False, "No stop loss"

    def update_profit_loss(self, profit_loss: float, is_win: bool):
        """
        Update profit/loss tracking

        Args:
            profit_loss: Profit or loss amount
            is_win: True if profitable trade
        """
        self.daily_profit_loss += profit_loss
        self.weekly_profit_loss += profit_loss
        self.total_profit_loss += profit_loss

        if is_win:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            if self.consecutive_losses >= 3:
                logger.warning(f"[WARNING]️ Consecutive losses: {self.consecutive_losses}")

        logger.info(
            f"P/L updated: {profit_loss:+,.0f}원 "
            f"(daily: {self.daily_profit_loss:+,.0f}원, total: {self.total_profit_loss:+,.0f}원)"
        )

    def _check_daily_loss_limit(self) -> bool:
        """Check if daily loss limit exceeded"""
        self._check_daily_reset()

        config = self.get_current_mode_config()
        max_daily_loss = self.current_capital * (config.max_daily_loss_pct / 100)

        if self.daily_profit_loss < -max_daily_loss:
            logger.warning(f"[WARNING]️ Daily loss limit reached: {self.daily_profit_loss:,.0f}원")
            return True

        return False

    def _check_weekly_loss_limit(self) -> bool:
        """Check if weekly loss limit exceeded"""
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())

        if week_start > self.weekly_reset_time:
            self.weekly_profit_loss = 0
            self.weekly_reset_time = week_start

        config = self.get_current_mode_config()
        max_weekly_loss = self.current_capital * (config.max_daily_loss_pct * 3 / 100)

        if self.weekly_profit_loss < -max_weekly_loss:
            logger.warning(f"[WARNING]️ Weekly loss limit reached: {self.weekly_profit_loss:,.0f}원")
            return True

        return False

    def _check_daily_reset(self):
        """Check and perform daily reset if needed"""
        today = datetime.now().date()

        if today > self.daily_reset_time:
            logger.info(f"Daily P/L reset (previous: {self.daily_profit_loss:+,.0f}원)")
            self.daily_profit_loss = 0.0
            self.daily_reset_time = today

    def should_approve_ai_signal(self, ai_score: float, ai_confidence: str) -> bool:
        """
        Check if AI signal meets current mode requirements

        Args:
            ai_score: AI score (0-10)
            ai_confidence: AI confidence level string

        Returns:
            True if signal approved
        """
        config = self.get_current_mode_config()

        if ai_score < config.ai_min_score:
            return False

        confidence_requirements = {
            RiskMode.AGGRESSIVE: 'Low',
            RiskMode.NORMAL: 'Medium',
            RiskMode.CONSERVATIVE: 'Medium',
            RiskMode.VERY_CONSERVATIVE: 'High',
            RiskMode.DEFENSIVE: 'High',
        }

        required_confidence = confidence_requirements[self.current_mode]
        confidence_levels = {'Low': 1, 'Medium': 2, 'High': 3}

        return confidence_levels.get(ai_confidence, 0) >= confidence_levels.get(required_confidence, 2)

    def can_trade(self, reason: str = "") -> Tuple[bool, str]:
        """
        Check if trading is allowed

        Args:
            reason: Reason for check

        Returns:
            (can_trade, message)
        """
        if self.emergency_stop:
            return False, "Emergency stop active"

        if not self.trading_enabled:
            return False, "Trading disabled"

        if self._check_daily_loss_limit():
            return False, "Daily loss limit exceeded"

        if self.consecutive_losses >= 5:
            return False, f"Too many consecutive losses: {self.consecutive_losses}"

        return True, "Trading allowed"

    def enable_trading(self):
        """Enable trading"""
        self.trading_enabled = True
        logger.info("[OK] Trading enabled")

    def disable_trading(self, reason: str = ""):
        """Disable trading"""
        self.trading_enabled = False
        logger.warning(f"🚫 Trading disabled: {reason}")

    def reset_emergency_stop(self):
        """Reset emergency stop (use with caution)"""
        self.emergency_stop = False
        logger.warning("[WARNING]️ Emergency stop reset")

    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary"""
        config = self.get_current_mode_config()
        return_rate = self.get_return_rate()

        return {
            'mode': self.current_mode.value,
            'mode_description': self.get_mode_description(),
            'mode_changed_at': self.mode_changed_at.isoformat(),
            'trading_enabled': self.trading_enabled,
            'emergency_stop': self.emergency_stop,
            'capital': {
                'initial': self.initial_capital,
                'current': self.current_capital,
                'profit_loss': self.total_profit_loss,
                'return_rate': return_rate,
                'return_percentage': return_rate * 100
            },
            'limits': {
                'daily_pnl': self.daily_profit_loss,
                'daily_limit': self.current_capital * (config.max_daily_loss_pct / 100),
                'weekly_pnl': self.weekly_profit_loss,
                'consecutive_losses': self.consecutive_losses
            },
            'config': {
                'max_open_positions': config.max_open_positions,
                'risk_per_trade_ratio': config.risk_per_trade_ratio,
                'max_position_size_pct': config.max_position_size_pct,
                'take_profit_ratio': config.take_profit_ratio,
                'stop_loss_ratio': config.stop_loss_ratio,
                'ai_min_score': config.ai_min_score
            }
        }

    def get_mode_description(self) -> str:
        """Get description of current mode"""
        descriptions = {
            RiskMode.AGGRESSIVE: "🔥 Aggressive - Profit expansion strategy",
            RiskMode.NORMAL: "⚖️ Normal - Balanced strategy",
            RiskMode.CONSERVATIVE: "🛡️ Conservative - Loss minimization",
            RiskMode.VERY_CONSERVATIVE: "🔒 Very Conservative - Capital protection priority",
            RiskMode.DEFENSIVE: "🚨 Defensive - Emergency capital preservation"
        }
        return descriptions.get(self.current_mode, "Unknown mode")

    def record_trade(
        self,
        stock_code: str,
        action: str,
        quantity: int,
        price: float,
        profit_loss: float = 0.0
    ):
        """
        Record trade in history

        Args:
            stock_code: Stock code
            action: 'buy' or 'sell'
            quantity: Quantity
            price: Price
            profit_loss: Profit/loss amount (for sell)
        """
        trade = {
            'timestamp': datetime.now(),
            'stock_code': stock_code,
            'action': action,
            'quantity': quantity,
            'price': price,
            'profit_loss': profit_loss,
            'mode': self.current_mode.value
        }

        self.trade_history.append(trade)
        self.position_history.append({
            'timestamp': datetime.now().isoformat(),
            'trade': trade
        })

        if len(self.trade_history) > 100:
            self.trade_history = self.trade_history[-100:]

    def save_state(self):
        """Save state to file"""
        state = {
            'current_capital': self.current_capital,
            'current_mode': self.current_mode.value,
            'daily_profit_loss': self.daily_profit_loss,
            'weekly_profit_loss': self.weekly_profit_loss,
            'total_profit_loss': self.total_profit_loss,
            'consecutive_losses': self.consecutive_losses,
            'trading_enabled': self.trading_enabled,
            'emergency_stop': self.emergency_stop,
            'daily_reset_time': self.daily_reset_time.isoformat(),
            'weekly_reset_time': self.weekly_reset_time.isoformat(),
            'mode_changed_at': self.mode_changed_at.isoformat()
        }

        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

        logger.info("💾 Risk manager state saved")

    def load_state(self):
        """Load state from file"""
        if not self.state_file.exists():
            return

        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)

            self.current_capital = state.get('current_capital', self.initial_capital)
            self.current_mode = RiskMode(state.get('current_mode', 'normal'))
            self.daily_profit_loss = state.get('daily_profit_loss', 0)
            self.weekly_profit_loss = state.get('weekly_profit_loss', 0)
            self.total_profit_loss = state.get('total_profit_loss', 0)
            self.consecutive_losses = state.get('consecutive_losses', 0)
            self.trading_enabled = state.get('trading_enabled', True)
            self.emergency_stop = state.get('emergency_stop', False)

            logger.info("✓ Risk manager state loaded")

        except Exception as e:
            logger.error(f"[WARNING]️ Failed to load state: {e}")

    def reset(self):
        """Reset risk manager state"""
        self.daily_profit_loss = 0.0
        self.weekly_profit_loss = 0.0
        self.total_profit_loss = 0.0
        self.consecutive_losses = 0
        self.trading_enabled = True
        self.emergency_stop = False
        self.daily_reset_time = datetime.now().date()
        self.weekly_reset_time = datetime.now() - timedelta(days=datetime.now().weekday())

        logger.info("🔄 Risk manager reset complete")


_advanced_risk_manager_instance = None


def get_advanced_risk_manager(
    initial_capital: Optional[float] = None,
    mode: RiskMode = RiskMode.NORMAL
) -> AdvancedRiskManager:
    """
    Get or create singleton instance of advanced risk manager

    Args:
        initial_capital: Initial capital (only used on first creation)
        mode: Starting risk mode (only used on first creation)

    Returns:
        AdvancedRiskManager singleton instance
    """
    global _advanced_risk_manager_instance

    if _advanced_risk_manager_instance is None:
        if initial_capital is None:
            initial_capital = 10_000_000

        _advanced_risk_manager_instance = AdvancedRiskManager(initial_capital, mode)
        _advanced_risk_manager_instance.load_state()

    return _advanced_risk_manager_instance


__all__ = ['AdvancedRiskManager', 'RiskMode', 'RiskModeConfig', 'get_advanced_risk_manager']
