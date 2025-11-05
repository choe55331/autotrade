"""
WebSocket connection handlers for real-time dashboard updates
"""
from flask import request
from flask_socketio import emit


def register_websocket_handlers(socketio):
    """Register all WebSocket event handlers"""

    @socketio.on('connect')
    def handle_connect():
        """Client connected"""
        emit('connected', {'message': 'Connected to AutoTrade Pro'})
        print(f"Client connected: {request.sid}")

    @socketio.on('disconnect')
    def handle_disconnect():
        """Client disconnected"""
        print(f"Client disconnected: {request.sid}")
