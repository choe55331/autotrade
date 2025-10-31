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

# v4.0 modules
from .ml_predictor import MLPricePredictor, PricePrediction, get_ml_predictor
from .rl_agent import DQNAgent, RLState, RLAction, get_rl_agent
from .ensemble_ai import EnsembleAI, EnsemblePrediction, get_ensemble_ai
from .meta_learning import MetaLearningEngine, MetaKnowledge, get_meta_learning_engine

# v4.1 modules
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
    Trade, Position, get_backtest_engine
)

# v4.2 modules
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

__all__ = [
    # v4.0 - ML Predictor
    'MLPricePredictor',
    'PricePrediction',
    'get_ml_predictor',

    # v4.0 - RL Agent
    'DQNAgent',
    'RLState',
    'RLAction',
    'get_rl_agent',

    # v4.0 - Ensemble AI
    'EnsembleAI',
    'EnsemblePrediction',
    'get_ensemble_ai',

    # v4.0 - Meta Learning
    'MetaLearningEngine',
    'MetaKnowledge',
    'get_meta_learning_engine',

    # v4.1 - Deep Learning
    'DeepLearningManager',
    'DeepLearningPrediction',
    'LSTMPricePredictor',
    'TransformerPricePredictor',
    'CNNPatternRecognizer',
    'get_deep_learning_manager',

    # v4.1 - Advanced RL
    'AdvancedRLManager',
    'AdvancedRLAction',
    'A3CAgent',
    'PPOAgent',
    'SACAgent',
    'get_advanced_rl_manager',

    # v4.1 - AutoML
    'AutoMLManager',
    'AutoMLResult',
    'HyperparameterConfig',
    'FeatureImportance',
    'get_automl_manager',

    # v4.1 - Backtesting
    'BacktestEngine',
    'BacktestResult',
    'BacktestConfig',
    'Trade',
    'Position',
    'get_backtest_engine',

    # v4.2 - Real-time System
    'RealTimeDataStream',
    'EventDrivenTradingEngine',
    'StreamingTick',
    'StreamingCandle',
    'StreamingEvent',
    'get_data_stream',
    'get_trading_engine',

    # v4.2 - Portfolio Optimization
    'PortfolioOptimizationManager',
    'PortfolioAllocation',
    'PortfolioMetrics',
    'MarkowitzOptimizer',
    'BlackLittermanOptimizer',
    'RiskParityOptimizer',
    'MonteCarloSimulator',
    'get_portfolio_manager',

    # v4.2 - Sentiment Analysis
    'SentimentAnalysisManager',
    'SentimentReport',
    'NewsSentimentAnalyzer',
    'SocialMediaAnalyzer',
    'NewsArticle',
    'SocialMediaPost',
    'get_sentiment_manager',

    # v4.2 - Advanced Systems
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

    # v4.2 - Options & HFT
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
]
