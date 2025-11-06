AI Routes Module - Modularized Structure
Handles all AI-related API endpoints

Modules:
- ai_mode: AI Mode v3.6 (status, toggle, decision, learning, optimize)
- advanced_ai: Advanced AI v4.0 (ML, RL, ensemble, meta-learning)
- deep_learning: Deep Learning v4.1 (LSTM, Transformer, CNN, Advanced RL, AutoML, Backtesting)
- advanced_systems: Advanced Systems v4.2 (Sentiment, Multi-Agent, Risk, Regime, Options, HFT)
- auto_analysis: Auto-Analysis (position monitor, portfolio optimization, alerts)
- market_commentary: Real-time AI market commentary

Refactored from monolithic ai.py (2,045 lines) to modular structure (6 modules)
from flask import Blueprint

from .ai_mode import ai_mode_bp
from .advanced_ai import advanced_ai_bp
from .deep_learning import deep_learning_bp
from .advanced_systems import advanced_systems_bp
from .auto_analysis import auto_analysis_bp
from .market_commentary import market_commentary_bp

from .common import set_bot_instance, get_bot_instance

ai_bp = Blueprint('ai', __name__)


def register_ai_routes(app):
    """
    Register all AI route blueprints with the Flask app

    Args:
        app: Flask application instance

    Usage:
        from dashboard.routes.ai import register_ai_routes
        register_ai_routes(app)
    """
    app.register_blueprint(ai_mode_bp)
    app.register_blueprint(advanced_ai_bp)
    app.register_blueprint(deep_learning_bp)
    app.register_blueprint(advanced_systems_bp)
    app.register_blueprint(auto_analysis_bp)
    app.register_blueprint(market_commentary_bp)

    print("✓ Registered 6 AI route modules:")
    print("  - AI Mode v3.6 (5 endpoints)")
    print("  - Advanced AI v4.0 (5 endpoints)")
    print("  - Deep Learning v4.1 (7 endpoints)")
    print("  - Advanced Systems v4.2 (7 endpoints)")
    print("  - Auto-Analysis (9 endpoints)")
    print("  - Market Commentary (1 endpoint)")
    print("  Total: 34 AI endpoints")


__all__ = [
    'ai_bp',
    'register_ai_routes',
    'set_bot_instance',
    'get_bot_instance',
    'ai_mode_bp',
    'advanced_ai_bp',
    'deep_learning_bp',
    'advanced_systems_bp',
    'auto_analysis_bp',
    'market_commentary_bp',
]
