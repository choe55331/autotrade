strategy/risk/__init__.py
통합 위험 관리 시스템

기존 5개 risk 파일을 통합하는 인터페이스 제공
import warnings

try:
    from ..risk_manager import RiskManager
except ImportError:
    RiskManager = None

try:
    from ..dynamic_risk_manager import DynamicRiskManager, RiskMode, RiskModeConfig
except ImportError:
    DynamicRiskManager = None
    RiskMode = None
    RiskModeConfig = None

try:
    from ..risk_orchestrator import RiskOrchestrator, RiskLevel, RiskCheck, RiskAssessment
except ImportError:
    RiskOrchestrator = None
    RiskLevel = None
    RiskCheck = None
    RiskAssessment = None

try:
    from ..advanced_risk_analytics import AdvancedRiskAnalytics
except ImportError:
    AdvancedRiskAnalytics = None

try:
    from ...features.risk_analyzer import RiskAnalyzer, RiskAnalysis, StockRisk, PortfolioRisk
except ImportError:
    RiskAnalyzer = None
    RiskAnalysis = None
    StockRisk = None
    PortfolioRisk = None

warnings.warn(
    "위험 관리 시스템이 통합되었습니다. "
    "strategy.risk를 통해 모든 risk 관련 클래스에 접근하세요.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    'RiskManager',
    'DynamicRiskManager',
    'RiskMode',
    'RiskModeConfig',
    'RiskOrchestrator',
    'RiskLevel',
    'RiskCheck',
    'RiskAssessment',
    'AdvancedRiskAnalytics',
    'RiskAnalyzer',
    'RiskAnalysis',
    'StockRisk',
    'PortfolioRisk',
]
