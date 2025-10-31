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
    """Serve main Professional Korean dashboard"""
    return render_template('dashboard_pro_korean.html')

@app.route('/classic')
def classic():
    """Serve classic Apple-style dashboard"""
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
    """Get account information from real API"""
    try:
        if bot_instance and hasattr(bot_instance, 'account_api'):
            # 실제 API에서 데이터 가져오기
            deposit = bot_instance.account_api.get_deposit()
            holdings = bot_instance.account_api.get_holdings()

            # 계좌 정보 계산
            cash = int(deposit.get('ord_alow_amt', 0)) if deposit else 0
            stock_value = sum(int(h.get('eval_amt', 0)) for h in holdings) if holdings else 0
            total_assets = cash + stock_value

            # 손익 계산
            total_buy_amount = sum(int(h.get('pchs_amt', 0)) for h in holdings) if holdings else 0
            profit_loss = stock_value - total_buy_amount
            profit_loss_percent = (profit_loss / total_buy_amount * 100) if total_buy_amount > 0 else 0

            return jsonify({
                'total_assets': total_assets,
                'cash': cash,
                'stock_value': stock_value,
                'profit_loss': profit_loss,
                'profit_loss_percent': profit_loss_percent,
                'open_positions': len(holdings) if holdings else 0
            })
        else:
            # Bot이 없으면 mock data
            return jsonify({
                'total_assets': 0,
                'cash': 0,
                'stock_value': 0,
                'profit_loss': 0,
                'profit_loss_percent': 0,
                'open_positions': 0
            })
    except Exception as e:
        print(f"Error getting account info: {e}")
        return jsonify({
            'total_assets': 0,
            'cash': 0,
            'stock_value': 0,
            'profit_loss': 0,
            'profit_loss_percent': 0,
            'open_positions': 0
        })


@app.route('/api/positions')
def get_positions():
    """Get current positions from real API"""
    try:
        if bot_instance and hasattr(bot_instance, 'account_api'):
            holdings = bot_instance.account_api.get_holdings()

            positions = []
            for h in holdings:
                code = h.get('pdno', '')
                name = h.get('prdt_name', '')
                quantity = int(h.get('hldg_qty', 0))
                avg_price = int(h.get('pchs_avg_pric', 0))
                current_price = int(h.get('prpr', 0))
                value = int(h.get('eval_amt', 0))

                profit_loss = value - (avg_price * quantity)
                profit_loss_percent = ((current_price - avg_price) / avg_price * 100) if avg_price > 0 else 0

                positions.append({
                    'code': code,
                    'name': name,
                    'quantity': quantity,
                    'avg_price': avg_price,
                    'current_price': current_price,
                    'profit_loss': profit_loss,
                    'profit_loss_percent': profit_loss_percent,
                    'value': value
                })

            return jsonify(positions)
        else:
            return jsonify([])
    except Exception as e:
        print(f"Error getting positions: {e}")
        return jsonify([])


@app.route('/api/candidates')
def get_candidates():
    """Get AI candidate stocks from scanner pipeline"""
    try:
        if bot_instance and hasattr(bot_instance, 'scanner_pipeline'):
            # 스캐너 파이프라인에서 후보 가져오기
            scanner = bot_instance.scanner_pipeline

            # AI 스캔 결과가 있으면 사용
            if hasattr(scanner, 'final_candidates') and scanner.final_candidates:
                candidates = []
                for candidate in scanner.final_candidates[:10]:  # 상위 10개
                    candidates.append({
                        'code': candidate.code,
                        'name': candidate.name,
                        'price': candidate.price,
                        'ai_score': candidate.final_score,
                        'confidence': getattr(candidate, 'ai_confidence', 0.0),
                        'signal': getattr(candidate, 'ai_signal', 'BUY'),
                        'reason': getattr(candidate, 'ai_reason', '분석 중')
                    })
                return jsonify(candidates)

        # 데이터가 없으면 빈 배열
        return jsonify([])
    except Exception as e:
        print(f"Error getting candidates: {e}")
        return jsonify([])


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

def run_dashboard(bot=None, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """Run the Apple-style dashboard

    Args:
        bot: Trading bot instance
        host: Host to bind to (default: '0.0.0.0')
        port: Port to bind to (default: 5000)
        debug: Enable debug mode (default: False)
    """
    global bot_instance
    bot_instance = bot

    print("=" * 80)
    print("🍎 AutoTrade Pro v3.0 - Apple Style Dashboard")
    print("=" * 80)
    print(f"📱 Dashboard URL: http://localhost:{port}")
    print(f"⚙️  Features: 40+ configurable trading features")
    print(f"🎨 Design: Apple-inspired minimalist UI")
    print("=" * 80)

    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


def create_app():
    """Create Flask app (for testing)"""
    return app


# ============================================================================
# AI MODE API (v3.6) - 진정한 AI 자율 트레이딩
# ============================================================================

@app.route('/api/ai/status')
def get_ai_status():
    """Get AI mode status"""
    try:
        from features.ai_mode import get_ai_agent
        from dataclasses import asdict

        agent = get_ai_agent(bot_instance)
        data = agent.get_dashboard_data()
        return jsonify(data)
    except Exception as e:
        print(f"AI status API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/ai/toggle', methods=['POST'])
def toggle_ai_mode():
    """Toggle AI mode on/off"""
    try:
        from features.ai_mode import get_ai_agent

        data = request.json
        enable = data.get('enable', False)

        agent = get_ai_agent(bot_instance)

        if enable:
            agent.enable_ai_mode()
            message = 'AI 모드 활성화됨 - 자율 트레이딩 시작'
        else:
            agent.disable_ai_mode()
            message = 'AI 모드 비활성화됨 - 수동 제어로 전환'

        return jsonify({
            'success': True,
            'enabled': agent.is_enabled(),
            'message': message
        })
    except Exception as e:
        print(f"AI toggle API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/ai/decision/<stock_code>')
def get_ai_decision(stock_code: str):
    """Get AI decision for a stock"""
    try:
        from features.ai_mode import get_ai_agent
        from dataclasses import asdict

        # Get stock data
        stock_name = stock_code  # Fallback
        stock_data = {
            'current_price': 0,
            'rsi': 50,
            'volume_ratio': 1.0,
            'total_score': 0
        }

        if bot_instance and hasattr(bot_instance, 'market_api'):
            # Try to get real data
            try:
                price_info = bot_instance.market_api.get_current_price(stock_code)
                if price_info:
                    stock_data['current_price'] = int(price_info.get('prpr', 0))
                    stock_name = price_info.get('prdt_name', stock_code)
            except:
                pass

        agent = get_ai_agent(bot_instance)
        decision = agent.make_trading_decision(stock_code, stock_name, stock_data)

        return jsonify({
            'success': True,
            'decision': asdict(decision)
        })
    except Exception as e:
        print(f"AI decision API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/ai/learning/summary')
def get_ai_learning_summary():
    """Get AI learning summary"""
    try:
        from features.ai_learning import AILearningEngine

        engine = AILearningEngine()
        summary = engine.get_learning_summary()

        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        print(f"AI learning API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/ai/optimize', methods=['POST'])
def trigger_ai_optimization():
    """Trigger AI self-optimization"""
    try:
        from features.ai_mode import get_ai_agent
        from dataclasses import asdict

        agent = get_ai_agent(bot_instance)
        agent.optimize_parameters()

        return jsonify({
            'success': True,
            'message': 'AI 자기 최적화 완료',
            'performance': asdict(agent.performance)
        })
    except Exception as e:
        print(f"AI optimization API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


# ============================================================================
# NEW FEATURES API (v3.5)
# ============================================================================

@app.route('/api/orderbook/<stock_code>')
def get_orderbook_api(stock_code: str):
    """Get real-time order book for stock"""
    try:
        from features.order_book import OrderBookService

        if bot_instance and hasattr(bot_instance, 'market_api'):
            service = OrderBookService(bot_instance.market_api)
            data = service.get_order_book_for_dashboard(stock_code)
            return jsonify(data)
        else:
            return jsonify({'success': False, 'message': 'Bot not initialized'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/performance')
def get_performance_api():
    """Get performance metrics"""
    try:
        from features.profit_tracker import ProfitTracker

        tracker = ProfitTracker()
        summary = tracker.get_performance_summary()
        return jsonify(summary)
    except Exception as e:
        print(f"Performance API error: {e}")
        return jsonify({})


@app.route('/api/portfolio/optimize')
def get_portfolio_optimization():
    """Get portfolio optimization analysis"""
    try:
        from features.portfolio_optimizer import PortfolioOptimizer

        if bot_instance and hasattr(bot_instance, 'account_api'):
            holdings = bot_instance.account_api.get_holdings()

            # Convert holdings to position format
            positions = []
            for h in holdings:
                positions.append({
                    'code': h.get('pdno', ''),
                    'name': h.get('prdt_name', ''),
                    'quantity': int(h.get('hldg_qty', 0)),
                    'avg_price': int(h.get('pchs_avg_pric', 0)),
                    'current_price': int(h.get('prpr', 0)),
                    'value': int(h.get('eval_amt', 0))
                })

            optimizer = PortfolioOptimizer()
            result = optimizer.get_optimization_for_dashboard(positions)
            return jsonify(result)
        else:
            return jsonify({'success': False, 'message': 'Bot not initialized'})
    except Exception as e:
        print(f"Portfolio optimization API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/news/<stock_code>')
def get_news_api(stock_code: str):
    """Get news feed for stock with sentiment analysis"""
    try:
        from features.news_feed import NewsFeedService

        # Get stock name from bot if available
        stock_name = stock_code
        if bot_instance and hasattr(bot_instance, 'market_api'):
            # Try to get stock name from market API
            # For now, use code as fallback
            pass

        service = NewsFeedService()
        result = service.get_news_for_dashboard(stock_code, stock_name, limit=10)
        return jsonify(result)
    except Exception as e:
        print(f"News API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/risk/analysis')
def get_risk_analysis():
    """Get portfolio risk analysis with correlation heatmap"""
    try:
        from features.risk_analyzer import RiskAnalyzer

        if bot_instance and hasattr(bot_instance, 'account_api'):
            holdings = bot_instance.account_api.get_holdings()

            # Convert holdings to position format with sector info
            positions = []
            for h in holdings:
                code = h.get('pdno', '')
                positions.append({
                    'code': code,
                    'name': h.get('prdt_name', ''),
                    'value': int(h.get('eval_amt', 0)),
                    'weight': 0,  # Will be calculated
                    'sector': '기타'  # Will be determined by analyzer
                })

            # Calculate weights
            total_value = sum(p['value'] for p in positions)
            for p in positions:
                p['weight'] = (p['value'] / total_value * 100) if total_value > 0 else 0

            analyzer = RiskAnalyzer()
            result = analyzer.get_risk_analysis_for_dashboard(positions)
            return jsonify(result)
        else:
            return jsonify({'success': False, 'message': 'Bot not initialized'})
    except Exception as e:
        print(f"Risk analysis API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


if __name__ == '__main__':
    run_dashboard(port=5000, debug=True)

# ============================================================================
# PAPER TRADING API (v3.7)
# ============================================================================

@app.route('/api/paper_trading/status')
def get_paper_trading_status():
    """Get paper trading engine status"""
    try:
        from features.paper_trading import get_paper_trading_engine
        
        engine = get_paper_trading_engine(
            getattr(bot_instance, 'market_api', None),
            None  # Will integrate with AI agent later
        )
        
        data = engine.get_dashboard_data()
        return jsonify(data)
    except Exception as e:
        print(f"Paper trading status API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/paper_trading/start', methods=['POST'])
def start_paper_trading():
    """Start paper trading engine"""
    try:
        from features.paper_trading import get_paper_trading_engine
        from features.ai_mode import get_ai_agent
        
        engine = get_paper_trading_engine(
            getattr(bot_instance, 'market_api', None),
            get_ai_agent(bot_instance)
        )
        
        engine.start()
        
        return jsonify({
            'success': True,
            'message': 'Paper trading engine started',
            'is_running': engine.is_running
        })
    except Exception as e:
        print(f"Start paper trading API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/paper_trading/stop', methods=['POST'])
def stop_paper_trading():
    """Stop paper trading engine"""
    try:
        from features.paper_trading import get_paper_trading_engine
        
        engine = get_paper_trading_engine()
        engine.stop()
        
        return jsonify({
            'success': True,
            'message': 'Paper trading engine stopped',
            'is_running': engine.is_running
        })
    except Exception as e:
        print(f"Stop paper trading API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/paper_trading/account/<strategy_name>')
def get_paper_trading_account(strategy_name: str):
    """Get paper trading account for specific strategy"""
    try:
        from features.paper_trading import get_paper_trading_engine
        from dataclasses import asdict
        
        engine = get_paper_trading_engine()
        
        if strategy_name in engine.accounts:
            account = engine.accounts[strategy_name]
            return jsonify({
                'success': True,
                'account': asdict(account)
            })
        else:
            return jsonify({'success': False, 'message': 'Strategy not found'})
    except Exception as e:
        print(f"Paper trading account API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


# ============================================================================
# TRADING JOURNAL API (v3.7)
# ============================================================================

@app.route('/api/journal/entries')
def get_journal_entries():
    """Get journal entries"""
    try:
        from features.trading_journal import get_trading_journal
        
        journal = get_trading_journal()
        data = journal.get_dashboard_data()
        
        return jsonify(data)
    except Exception as e:
        print(f"Journal entries API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/journal/statistics')
def get_journal_statistics():
    """Get journal statistics"""
    try:
        from features.trading_journal import get_trading_journal
        
        period = request.args.get('period', 'month')
        journal = get_trading_journal()
        stats = journal.get_statistics(period)
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        print(f"Journal statistics API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/journal/insights')
def get_journal_insights():
    """Get journal insights"""
    try:
        from features.trading_journal import get_trading_journal
        from dataclasses import asdict
        
        journal = get_trading_journal()
        insights = journal.generate_insights()
        
        return jsonify({
            'success': True,
            'insights': [asdict(i) for i in insights]
        })
    except Exception as e:
        print(f"Journal insights API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


# ============================================================================
# NOTIFICATION API (v3.7)
# ============================================================================

@app.route('/api/notifications')
def get_notifications():
    """Get notifications"""
    try:
        from features.notification import get_notification_manager
        
        manager = get_notification_manager()
        data = manager.get_dashboard_data()
        
        return jsonify(data)
    except Exception as e:
        print(f"Notifications API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/notifications/mark_read/<notification_id>', methods=['POST'])
def mark_notification_read(notification_id: str):
    """Mark notification as read"""
    try:
        from features.notification import get_notification_manager
        
        manager = get_notification_manager()
        manager.mark_as_read(notification_id)
        
        return jsonify({
            'success': True,
            'message': 'Notification marked as read'
        })
    except Exception as e:
        print(f"Mark notification API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/notifications/configure/telegram', methods=['POST'])
def configure_telegram():
    """Configure Telegram notifications"""
    try:
        from features.notification import get_notification_manager
        
        data = request.json
        bot_token = data.get('bot_token')
        chat_id = data.get('chat_id')
        
        manager = get_notification_manager()
        manager.configure_telegram(bot_token, chat_id)
        
        return jsonify({
            'success': True,
            'message': 'Telegram configured successfully'
        })
    except Exception as e:
        print(f"Configure Telegram API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/notifications/send', methods=['POST'])
def send_notification():
    """Send custom notification"""
    try:
        from features.notification import get_notification_manager
        
        data = request.json
        manager = get_notification_manager()
        
        notification = manager.send(
            title=data.get('title', 'Notification'),
            message=data.get('message', ''),
            priority=data.get('priority', 'medium'),
            category=data.get('category', 'system'),
            channels=data.get('channels')
        )
        
        return jsonify({
            'success': True,
            'notification_id': notification.id if notification else None
        })
    except Exception as e:
        print(f"Send notification API error: {e}")
        return jsonify({'success': False, 'message': str(e)})

# ============================================================================
# ADVANCED AI API (v4.0) - 차세대 AI 시스템
# ============================================================================

@app.route('/api/ai/ml/predict/<stock_code>')
def get_ml_prediction(stock_code: str):
    """Get ML price prediction"""
    try:
        from ai.ml_predictor import get_ml_predictor
        from dataclasses import asdict
        
        # Get current data
        current_data = {
            'price': 73500,  # Would fetch real data
            'rsi': 55,
            'macd': 100,
            'volume_ratio': 1.3
        }
        
        predictor = get_ml_predictor()
        prediction = predictor.predict(stock_code, stock_code, current_data)
        
        return jsonify({
            'success': True,
            'prediction': asdict(prediction)
        })
    except Exception as e:
        print(f"ML prediction API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/ai/rl/action')
def get_rl_action():
    """Get RL agent action"""
    try:
        from ai.rl_agent import get_rl_agent, RLState
        from dataclasses import asdict
        
        # Create state from current data
        state = RLState(
            portfolio_value=10000000,
            cash_balance=5000000,
            position_count=2,
            current_price=73500,
            price_change_5m=0.5,
            price_change_1h=1.2,
            rsi=55,
            macd=100,
            volume_ratio=1.3,
            market_trend=0.6,
            time_of_day=0.5
        )
        
        agent = get_rl_agent()
        state_vec = agent._state_to_vector(state)
        action_idx = agent.act(state_vec)
        action = agent.get_action_interpretation(action_idx)
        
        return jsonify({
            'success': True,
            'action': asdict(action),
            'performance': agent.get_performance()
        })
    except Exception as e:
        print(f"RL action API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/ai/ensemble/predict/<stock_code>')
def get_ensemble_prediction(stock_code: str):
    """Get ensemble AI prediction"""
    try:
        from ai.ensemble_ai import get_ensemble_ai
        from dataclasses import asdict
        
        # Get market data
        market_data = {
            'price': 73500,
            'rsi': 55,
            'macd': 100,
            'volume_ratio': 1.3,
            'portfolio_value': 10000000,
            'cash_balance': 5000000,
            'position_count': 2
        }
        
        ensemble = get_ensemble_ai()
        prediction = ensemble.predict(stock_code, stock_code, market_data)
        
        return jsonify({
            'success': True,
            'prediction': asdict(prediction)
        })
    except Exception as e:
        print(f"Ensemble prediction API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/ai/meta/recommend')
def get_meta_recommendation():
    """Get meta-learning strategy recommendation"""
    try:
        from ai.meta_learning import get_meta_learning_engine
        
        # Current conditions
        conditions = {
            'regime': 'bullish',
            'volatility': 'medium'
        }
        
        engine = get_meta_learning_engine()
        recommendation = engine.recommend_strategy(conditions)
        insights = engine.get_meta_insights()
        
        return jsonify({
            'success': True,
            'recommendation': recommendation,
            'insights': insights
        })
    except Exception as e:
        print(f"Meta recommendation API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/ai/performance')
def get_ai_performance():
    """Get all AI systems performance"""
    try:
        from ai.ml_predictor import get_ml_predictor
        from ai.rl_agent import get_rl_agent
        from ai.ensemble_ai import get_ensemble_ai
        
        return jsonify({
            'success': True,
            'ml_predictor': get_ml_predictor().get_model_performance(),
            'rl_agent': get_rl_agent().get_performance(),
            'ensemble': get_ensemble_ai().get_performance_report()
        })
    except Exception as e:
        print(f"AI performance API error: {e}")
        return jsonify({'success': False, 'message': str(e)})
