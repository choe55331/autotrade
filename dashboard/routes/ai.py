AI Routes - Backward Compatibility Wrapper

⚠️ DEPRECATED: This file is a backward compatibility wrapper.
The AI routes have been refactored into modular structure.

New structure:
  dashboard/routes/ai/
    __init__.py          - Main module with register_ai_routes()
    common.py            - Shared utilities
    ai_mode.py           - AI Mode v3.6
    advanced_ai.py       - Advanced AI v4.0
    deep_learning.py     - Deep Learning v4.1
    advanced_systems.py  - Advanced Systems v4.2
    auto_analysis.py     - Auto-Analysis
    market_commentary.py - Market Commentary

Refactored from monolithic 2,045-line file to 6 modular files.

For new code, use:
    from dashboard.routes.ai import register_ai_routes, set_bot_instance
    register_ai_routes(app)
    set_bot_instance(bot)

This wrapper maintains backward compatibility with existing code.

from dashboard.routes.ai import (
    ai_bp,
    register_ai_routes,
    set_bot_instance,
    get_bot_instance,
    ai_mode_bp,
    advanced_ai_bp,
    deep_learning_bp,
    advanced_systems_bp,
    auto_analysis_bp,
    market_commentary_bp,
)

__all__ = [
    'ai_bp',
    'set_bot_instance',
    'register_ai_routes',
]

import warnings
warnings.warn(
    "dashboard.routes.ai is now modularized. "
    "Consider updating imports to: from dashboard.routes.ai import register_ai_routes",
    DeprecationWarning,
    stacklevel=2
)
