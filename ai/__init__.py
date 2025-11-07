"""
Advanced AI Package
Next-generation AI trading system


v4.0 Modules:
- ML Predictor: Machine learning price prediction
- RL Agent: Reinforcement learning trading agent
- Ensemble AI: Combined multi-model predictions
- Meta Learning: Learning how to learn

v4.1 Modules:
- Deep Learning: LSTM, Transformer, CNN models
- Advanced RL: A3C, PPO, SAC algorithms
- AutoML: Automatic hyperparameter optimization
- Backtesting: Strategy validation engine

v4.2 Modules:
- Real-time System: WebSocket streaming, event-driven trading
- Portfolio Optimization: Markowitz, Black-Litterman, Risk Parity, Monte Carlo
- Sentiment Analysis: News and social media analysis
- Multi-Agent System: Consensus-based decision making
- Advanced Risk Management: VaR, CVaR, stress testing
- Market Regime Detection: Bull/bear/sideways classification
- Performance Optimization: Multi-processing, caching
- Options Pricing: Black-Scholes, Greeks, strategies
- High-Frequency Trading: Microsecond latency, arbitrage

"""
from .ensemble_analyzer import EnsembleAnalyzer, get_analyzer

from .ml_predictor import MLPricePredictor, PricePrediction, get_ml_predictor
from .rl_agent import DQNAgent, RLState, RLAction, get_rl_agent
from .ensemble_ai import EnsembleAI, EnsemblePrediction, get_ensemble_ai
from .meta_learning import MetaLearningEngine, MetaKnowledge, get_meta_learning_engine

from .deep_learning import (
    DeepLearningManager, DeepLearningPrediction,
    LSTMPricePredictor, TransformerPricePredictor, CNNPatternRecognizer,
    get_deep_learning_manager
)
from .advanced_rl import (
    AdvancedRLManager, RLAction as AdvancedRLAction,
    A3CAgent, PPOAgent, SACAgent,
    get_advanced_rl_manager
)
from .automl import (
    AutoMLManager, AutoMLResult, HyperparameterConfig,
    FeatureImportance, get_automl_manager
)
from .backtesting import (
    BacktestEngine, BacktestResult, BacktestConfig,
    BacktestTrade, get_backtest_engine
)
from core import Position

from .realtime_system import (
    RealTimeDataStream, EventDrivenTradingEngine,
    StreamingTick, StreamingCandle, StreamingEvent,
    get_data_stream, get_trading_engine
)
from .portfolio_optimization import (
    PortfolioOptimizationManager, PortfolioAllocation, PortfolioMetrics,
    MarkowitzOptimizer, BlackLittermanOptimizer, RiskParityOptimizer,
    MonteCarloSimulator, get_portfolio_manager
)
from .sentiment_analysis import (
    SentimentAnalysisManager, SentimentReport,
    NewsSentimentAnalyzer, SocialMediaAnalyzer,
    NewsArticle, SocialMediaPost,
    get_sentiment_manager
)
from .advanced_systems import (
    MultiAgentSystem, AdvancedRiskManager, MarketRegimeDetector,
    PerformanceOptimizer, AgentDecision, ConsensusDecision,
    RiskMetrics, MarketRegime,
    get_multi_agent_system, get_risk_manager,
    get_regime_detector, get_performance_optimizer
)
from .options_hft import (
    BlackScholesModel, OptionsStrategyAnalyzer, HighFrequencyTrader,
    OptionContract, OptionGreeks, HFTOrder, HFTSignal,
    get_bs_model, get_options_analyzer, get_hft_trader
)

try:
    from .backtest_report_generator import BacktestReportGenerator, BacktestReport
    from .strategy_optimizer import StrategyOptimizer, OptimizationResult
    from .market_regime_classifier import MarketRegimeClassifier, RegimeType, VolatilityLevel
    from .anomaly_detector import AnomalyDetector, AnomalyEvent, AnomalyType
except ImportError as e:
    import warnings
    warnings.warn(f"v4.0 Advanced Features could not be imported: {e}")
    BacktestReportGenerator = BacktestReport = None
    StrategyOptimizer = OptimizationResult = None
    MarketRegimeClassifier = RegimeType = VolatilityLevel = None
    AnomalyDetector = AnomalyEvent = AnomalyType = None

__all__ = [
    'EnsembleAnalyzer',
    'get_analyzer',

    'MLPricePredictor',
    'PricePrediction',
    'get_ml_predictor',

    'DQNAgent',
    'RLState',
    'RLAction',
    'get_rl_agent',

    'EnsembleAI',
    'EnsemblePrediction',
    'get_ensemble_ai',

    'MetaLearningEngine',
    'MetaKnowledge',
    'get_meta_learning_engine',

    'DeepLearningManager',
    'DeepLearningPrediction',
    'LSTMPricePredictor',
    'TransformerPricePredictor',
    'CNNPatternRecognizer',
    'get_deep_learning_manager',

    'AdvancedRLManager',
    'AdvancedRLAction',
    'A3CAgent',
    'PPOAgent',
    'SACAgent',
    'get_advanced_rl_manager',

    'AutoMLManager',
    'AutoMLResult',
    'HyperparameterConfig',
    'FeatureImportance',
    'get_automl_manager',

    'BacktestEngine',
    'BacktestResult',
    'BacktestConfig',
    'BacktestTrade',
    'Position',
    'get_backtest_engine',

    'RealTimeDataStream',
    'EventDrivenTradingEngine',
    'StreamingTick',
    'StreamingCandle',
    'StreamingEvent',
    'get_data_stream',
    'get_trading_engine',

    'PortfolioOptimizationManager',
    'PortfolioAllocation',
    'PortfolioMetrics',
    'MarkowitzOptimizer',
    'BlackLittermanOptimizer',
    'RiskParityOptimizer',
    'MonteCarloSimulator',
    'get_portfolio_manager',

    'SentimentAnalysisManager',
    'SentimentReport',
    'NewsSentimentAnalyzer',
    'SocialMediaAnalyzer',
    'NewsArticle',
    'SocialMediaPost',
    'get_sentiment_manager',

    'MultiAgentSystem',
    'AdvancedRiskManager',
    'MarketRegimeDetector',
    'PerformanceOptimizer',
    'AgentDecision',
    'ConsensusDecision',
    'RiskMetrics',
    'MarketRegime',
    'get_multi_agent_system',
    'get_risk_manager',
    'get_regime_detector',
    'get_performance_optimizer',

    'BlackScholesModel',
    'OptionsStrategyAnalyzer',
    'HighFrequencyTrader',
    'OptionContract',
    'OptionGreeks',
    'HFTOrder',
    'HFTSignal',
    'get_bs_model',
    'get_options_analyzer',
    'get_hft_trader',

    'BacktestReportGenerator',
    'BacktestReport',
    'StrategyOptimizer',
    'OptimizationResult',
    'MarketRegimeClassifier',
    'RegimeType',
    'VolatilityLevel',
    'AnomalyDetector',
    'AnomalyEvent',
    'AnomalyType',
]
