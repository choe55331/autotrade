strategy 패키지
매매 전략 모듈

v4.2 Changes:
- Position now imported from core (standardized)
- PositionManager still available for backward compatibility
from .base_strategy import BaseStrategy
from .momentum_strategy import MomentumStrategy
from .portfolio_manager import PortfolioManager
from .risk_manager import RiskManager

try:
    from .trailing_stop_manager import TrailingStopManager, TrailingStopState
    from .volatility_breakout_strategy import VolatilityBreakoutStrategy, BreakoutState
    from .pairs_trading_strategy import PairsTradingStrategy, PairState
    from .kelly_criterion import KellyCriterion, KellyParameters
    from .institutional_following_strategy import InstitutionalFollowingStrategy, InstitutionalData
except ImportError:
    TrailingStopManager = TrailingStopState = None
    VolatilityBreakoutStrategy = BreakoutState = None
    PairsTradingStrategy = PairState = None
    KellyCriterion = KellyParameters = None
    InstitutionalFollowingStrategy = InstitutionalData = None

from core import Position
from .position_manager import PositionManager, get_position_manager
from .signal_checker import SignalChecker, SignalType, TradingSignalValidator

from .risk_orchestrator import RiskOrchestrator, RiskLevel, RiskAssessment, get_risk_orchestrator

__all__ = [
    'BaseStrategy',
    'MomentumStrategy',
    'PortfolioManager',
    'RiskManager',
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
    'PositionManager',
    'Position',
    'get_position_manager',
    'SignalChecker',
    'SignalType',
    'TradingSignalValidator',
    'RiskOrchestrator',
    'RiskLevel',
    'RiskAssessment',
    'get_risk_orchestrator',
]