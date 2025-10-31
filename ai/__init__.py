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
]
