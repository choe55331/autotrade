"""
Advanced AI Package
Next-generation AI trading system

Modules:
- ML Predictor: Machine learning price prediction
- RL Agent: Reinforcement learning trading agent
- Ensemble AI: Combined multi-model predictions
- Meta Learning: Learning how to learn
"""
from .ml_predictor import MLPricePredictor, PricePrediction, get_ml_predictor
from .rl_agent import DQNAgent, RLState, RLAction, get_rl_agent
from .ensemble_ai import EnsembleAI, EnsemblePrediction, get_ensemble_ai
from .meta_learning import MetaLearningEngine, MetaKnowledge, get_meta_learning_engine

__all__ = [
    # ML Predictor
    'MLPricePredictor',
    'PricePrediction',
    'get_ml_predictor',
    # RL Agent
    'DQNAgent',
    'RLState',
    'RLAction',
    'get_rl_agent',
    # Ensemble AI
    'EnsembleAI',
    'EnsemblePrediction',
    'get_ensemble_ai',
    # Meta Learning
    'MetaLearningEngine',
    'MetaKnowledge',
    'get_meta_learning_engine',
]
