"""
AI Routes - Common Utilities
Shared utilities and bot instance management for AI routes
"""

_bot_instance = None


def set_bot_instance(bot):
    """Set the bot instance for AI routes"""
    global _bot_instance
    _bot_instance = bot


def get_bot_instance():
    """Get the bot instance"""
    return _bot_instance
