"""
AutoTrade Pro Dashboard Module
v5.7.3 - Production Ready (Complete Overhaul)

Major Features:
- 10 Diverse Trading Strategies (Real Methodologies)
- Profit Optimization Engine (Auto Stop-Loss/Take-Profit)
- WebSocket-Style Seamless Updates
- Real AI Analysis (Not Mock Data)
- Strategy-based Trade Filtering
- Enhanced Safety (YES Confirmation)

Exports:
- run_dashboard: Main function to start the dashboard server
- create_app: Flask app factory for testing
- app: Flask application instance
- socketio: SocketIO instance
"""
from .app import run_dashboard, create_app, app, socketio

__all__ = ['run_dashboard', 'create_app', 'app', 'socketio']
__version__ = '5.7.3'
