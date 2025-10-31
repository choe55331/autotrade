"""
AutoTrade Pro v3.0 - Apple-Style Dashboard
Modern, elegant dashboard with comprehensive feature controls
"""
import os
import sys
import time
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import yaml

# Add parent directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Create Flask app
app = Flask(__name__,
           template_folder='templates',
           static_folder='static')
app.config['SECRET_KEY'] = 'autotrade-pro-v3-apple-style'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
bot_instance = None
config_manager = None


def load_features_config() -> Dict[str, Any]:
    """Load features configuration"""
    config_path = BASE_DIR / 'config' / 'features_config.yaml'
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading features config: {e}")
        return {}


def save_features_config(config: Dict[str, Any]) -> bool:
    """Save features configuration"""
    config_path = BASE_DIR / 'config' / 'features_config.yaml'
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        return True
    except Exception as e:
        print(f"Error saving features config: {e}")
        return False


def get_control_status() -> Dict[str, Any]:
    """Get control.json status"""
    control_file = BASE_DIR / 'data' / 'control.json'
    try:
        with open(control_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"trading_enabled": False}


def set_control_status(enabled: bool) -> bool:
    """Set control.json status"""
    control_file = BASE_DIR / 'data' / 'control.json'
    try:
        with open(control_file, 'w', encoding='utf-8') as f:
            json.dump({"trading_enabled": enabled}, f, indent=2)
        return True
    except:
        return False


# ============================================================================
# MAIN ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve main Apple-style dashboard"""
    return render_template('dashboard_apple.html')


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/status')
def get_status():
    """Get system status"""
    control = get_control_status()

    # Mock data for now - will be replaced with real data
    return jsonify({
        'system': {
            'running': True,
            'trading_enabled': control.get('trading_enabled', False),
            'uptime': '2h 34m',
            'last_update': datetime.now().isoformat()
        },
        'risk': {
            'mode': 'NORMAL',
            'description': 'Normal trading conditions'
        },
        'scanning': {
            'fast_scan': {'count': 47, 'last_run': '10s ago'},
            'deep_scan': {'count': 18, 'last_run': '45s ago'},
            'ai_scan': {'count': 3, 'last_run': '2m ago'}
        }
    })


@app.route('/api/account')
def get_account():
    """Get account information"""
    # Mock data for now
    return jsonify({
        'total_assets': 52847500,
        'cash': 15420000,
        'stock_value': 37427500,
        'profit_loss': 2847500,
        'profit_loss_percent': 5.69,
        'open_positions': 7
    })


@app.route('/api/positions')
def get_positions():
    """Get current positions"""
    # Mock data
    positions = [
        {
            'code': '005930',
            'name': '삼성전자',
            'quantity': 150,
            'avg_price': 71000,
            'current_price': 73500,
            'profit_loss': 375000,
            'profit_loss_percent': 3.52,
            'value': 11025000
        },
        {
            'code': '000660',
            'name': 'SK하이닉스',
            'quantity': 80,
            'avg_price': 125000,
            'current_price': 130000,
            'profit_loss': 400000,
            'profit_loss_percent': 4.00,
            'value': 10400000
        }
    ]
    return jsonify(positions)


@app.route('/api/candidates')
def get_candidates():
    """Get AI candidate stocks"""
    # Mock data
    candidates = [
        {
            'code': '035720',
            'name': '카카오',
            'price': 45500,
            'ai_score': 87.5,
            'confidence': 0.92,
            'signal': 'BUY',
            'reason': 'Strong momentum + positive sentiment'
        },
        {
            'code': '035420',
            'name': 'NAVER',
            'price': 215000,
            'ai_score': 82.3,
            'confidence': 0.88,
            'signal': 'BUY',
            'reason': 'Institutional buying + technical breakout'
        }
    ]
    return jsonify(candidates)


@app.route('/api/activities')
def get_activities():
    """Get recent activities"""
    # Mock data
    activities = [
        {
            'time': '14:32:15',
            'type': 'BUY',
            'message': 'Bought 카카오 (035720) 50 shares @ 45,500',
            'level': 'success'
        },
        {
            'time': '14:15:32',
            'type': 'SCAN',
            'message': 'AI Scan completed: 3 high-score candidates found',
            'level': 'info'
        }
    ]
    return jsonify(activities)


@app.route('/api/performance')
def get_performance():
    """Get performance history for chart"""
    # Mock data - 24 hours of data
    now = datetime.now()
    data = []
    base_value = 50000000

    for i in range(24):
        timestamp = (now.timestamp() - (24 - i) * 3600) * 1000
        value = base_value + (i * 100000) + ((i % 3) * 50000)
        data.append({
            'timestamp': int(timestamp),
            'value': value
        })

    return jsonify(data)


# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@app.route('/api/config/features', methods=['GET'])
def get_features_config():
    """Get all features configuration"""
    config = load_features_config()
    return jsonify(config)


@app.route('/api/config/features', methods=['POST'])
def update_features_config():
    """Update features configuration"""
    try:
        new_config = request.json
        if save_features_config(new_config):
            socketio.emit('config_updated', {'success': True})
            return jsonify({'success': True, 'message': 'Configuration updated'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save configuration'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/config/feature/<path:feature_path>', methods=['PATCH'])
def update_feature_toggle(feature_path: str):
    """Toggle a specific feature on/off"""
    try:
        data = request.json
        enabled = data.get('enabled', True)

        config = load_features_config()

        # Navigate to the feature using path (e.g., "ui.realtime_updates.enabled")
        keys = feature_path.split('.')
        current = config
        for key in keys[:-1]:
            if key not in current:
                return jsonify({'success': False, 'message': f'Invalid path: {feature_path}'}), 400
            current = current[key]

        # Set the value
        current[keys[-1]] = enabled

        if save_features_config(config):
            socketio.emit('feature_toggled', {'path': feature_path, 'enabled': enabled})
            return jsonify({'success': True, 'message': f'Feature {feature_path} updated'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# CONTROL ENDPOINTS
# ============================================================================

@app.route('/api/control/start', methods=['POST'])
def start_trading():
    """Start trading"""
    if set_control_status(True):
        socketio.emit('trading_status', {'enabled': True})
        return jsonify({'success': True, 'message': 'Trading started'})
    return jsonify({'success': False, 'message': 'Failed to start'}), 500


@app.route('/api/control/stop', methods=['POST'])
def stop_trading():
    """Stop trading"""
    if set_control_status(False):
        socketio.emit('trading_status', {'enabled': False})
        return jsonify({'success': True, 'message': 'Trading stopped'})
    return jsonify({'success': False, 'message': 'Failed to stop'}), 500


# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Client connected"""
    emit('connected', {'message': 'Connected to AutoTrade Pro'})
    print(f"Client connected: {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print(f"Client disconnected: {request.sid}")


# ============================================================================
# REAL-TIME UPDATE THREAD
# ============================================================================

def realtime_update_thread():
    """Background thread for pushing real-time updates"""
    while True:
        time.sleep(3)  # Update every 3 seconds

        try:
            # Push status update
            control = get_control_status()
            socketio.emit('status_update', {
                'timestamp': datetime.now().isoformat(),
                'trading_enabled': control.get('trading_enabled', False)
            })
        except Exception as e:
            print(f"Error in realtime update: {e}")


# Start real-time update thread
update_thread = threading.Thread(target=realtime_update_thread, daemon=True)
update_thread.start()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def run_dashboard(port: int = 5000, debug: bool = False, bot=None):
    """Run the Apple-style dashboard"""
    global bot_instance
    bot_instance = bot

    print("=" * 80)
    print("🍎 AutoTrade Pro v3.0 - Apple Style Dashboard")
    print("=" * 80)
    print(f"📱 Dashboard URL: http://localhost:{port}")
    print(f"⚙️  Features: 40+ configurable trading features")
    print(f"🎨 Design: Apple-inspired minimalist UI")
    print("=" * 80)

    socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)


def create_app():
    """Create Flask app (for testing)"""
    return app


if __name__ == '__main__':
    run_dashboard(port=5000, debug=True)
