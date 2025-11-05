"""
AutoTrade Pro Dashboard Module
v5.7 - Critical Fixes & Real Functionality

Exports:
- run_dashboard: Main function to start the dashboard server
- create_app: Flask app factory for testing
- app: Flask application instance
- socketio: SocketIO instance
"""
from .app import run_dashboard, create_app, app, socketio

__all__ = ['run_dashboard', 'create_app', 'app', 'socketio']
__version__ = '5.7.0'
