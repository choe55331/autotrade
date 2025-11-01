"""
strategy 패키지
매매 전략 모듈
"""
from .base_strategy import BaseStrategy
from .momentum_strategy import MomentumStrategy
from .portfolio_manager import PortfolioManager
from .risk_manager import RiskManager

# v4.0 Advanced Strategies
try:
    from .trailing_stop_manager import TrailingStopManager, TrailingStopState
    from .volatility_breakout_strategy import VolatilityBreakoutStrategy, BreakoutState
    from .pairs_trading_strategy import PairsTradingStrategy, PairState
    from .kelly_criterion import KellyCriterion, KellyParameters
    from .institutional_following_strategy import InstitutionalFollowingStrategy, InstitutionalData
except ImportError:
    # numpy 등 의존성 없을 때
    TrailingStopManager = TrailingStopState = None
    VolatilityBreakoutStrategy = BreakoutState = None
    PairsTradingStrategy = PairState = None
    KellyCriterion = KellyParameters = None
    InstitutionalFollowingStrategy = InstitutionalData = None

# v4.0 Utilities
from .position_manager import PositionManager, Position, get_position_manager
from .signal_checker import SignalChecker, SignalType, TradingSignalValidator

__all__ = [
    'BaseStrategy',
    'MomentumStrategy',
    'PortfolioManager',
    'RiskManager',
    # v4.0 Advanced Strategies
    'TrailingStopManager',
    'TrailingStopState',
    'VolatilityBreakoutStrategy',
    'BreakoutState',
    'PairsTradingStrategy',
    'PairState',
    'KellyCriterion',
    'KellyParameters',
    'InstitutionalFollowingStrategy',
    'InstitutionalData',
    # v4.0 Utilities
    'PositionManager',
    'Position',
    'get_position_manager',
    'SignalChecker',
    'SignalType',
    'TradingSignalValidator',
]