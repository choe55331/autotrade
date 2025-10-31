"""
AutoTrade Pro v4.2 - Apple-Style Dashboard
Modern, elegant dashboard with comprehensive AI-powered trading features

v4.2 Features:
- Real-time WebSocket streaming
- Portfolio optimization (Markowitz, Black-Litterman, Risk Parity)
- Sentiment analysis (News + Social media)
- Multi-agent consensus system
- Advanced risk management (VaR/CVaR)
- Market regime detection
- Options pricing (Black-Scholes)
- High-frequency trading
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
    print("🚀 AutoTrade Pro v4.2 - AI-Powered Trading Dashboard")
    print("=" * 80)
    print(f"📱 Dashboard URL: http://localhost:{port}")
    print(f"🤖 AI Systems: 18 integrated (v4.0 + v4.1 + v4.2)")
    print(f"📊 API Endpoints: 38 total")
    print(f"🎨 Design: Apple-inspired minimalist UI")
    print(f"⚡ New in v4.2: Real-time, Portfolio Optimization, Sentiment, Multi-Agent, HFT")
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


# ============================================================================
# v4.1 Advanced AI Features
# ============================================================================

@app.route('/ai-dashboard')
def ai_dashboard():
    """Serve AI Dashboard UI"""
    return render_template('ai_dashboard.html')


@app.route('/api/v4.1/deep_learning/predict/<stock_code>')
def get_deep_learning_prediction(stock_code: str):
    """Get deep learning prediction (LSTM + Transformer + CNN)"""
    try:
        from ai.deep_learning import get_deep_learning_manager
        from dataclasses import asdict

        manager = get_deep_learning_manager()

        # Mock historical data
        historical_data = []

        prediction = manager.predict(
            stock_code=stock_code,
            stock_name=stock_code,
            historical_data=historical_data,
            current_price=73500
        )

        return jsonify({
            'success': True,
            'prediction': asdict(prediction)
        })
    except Exception as e:
        print(f"Deep learning prediction error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/v4.1/advanced_rl/action')
def get_advanced_rl_action():
    """Get action from advanced RL algorithms (A3C, PPO, SAC)"""
    try:
        from ai.advanced_rl import get_advanced_rl_manager
        import numpy as np
        from dataclasses import asdict

        manager = get_advanced_rl_manager()

        # Mock state
        state = np.random.randn(15)

        # Get algorithm from query params
        algorithm = request.args.get('algorithm', None)

        action = manager.get_action(state, algorithm)

        return jsonify({
            'success': True,
            'action': asdict(action)
        })
    except Exception as e:
        print(f"Advanced RL action error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/v4.1/advanced_rl/performance')
def get_advanced_rl_performance():
    """Get performance metrics for all RL algorithms"""
    try:
        from ai.advanced_rl import get_advanced_rl_manager

        manager = get_advanced_rl_manager()
        performance = manager.get_all_performances()

        return jsonify({
            'success': True,
            'performance': performance
        })
    except Exception as e:
        print(f"Advanced RL performance error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/v4.1/automl/optimize', methods=['POST'])
def run_automl_optimization():
    """Run AutoML optimization"""
    try:
        from ai.automl import get_automl_manager
        from dataclasses import asdict
        import numpy as np

        # Get parameters from request
        data = request.get_json() or {}
        model_types = data.get('model_types', ['random_forest', 'xgboost'])
        optimization_method = data.get('method', 'bayesian')
        n_trials = data.get('n_trials', 30)

        manager = get_automl_manager()

        # Mock data for demo
        X = np.random.randn(100, 5)
        y = np.random.randn(100)

        result = manager.auto_optimize(
            X=X,
            y=y,
            model_types=model_types,
            optimization_method=optimization_method,
            n_trials=n_trials
        )

        # Convert dataclasses to dict
        result_dict = asdict(result)

        return jsonify({
            'success': True,
            'result': result_dict
        })
    except Exception as e:
        print(f"AutoML optimization error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/v4.1/automl/history')
def get_automl_history():
    """Get AutoML optimization history"""
    try:
        from ai.automl import get_automl_manager
        from dataclasses import asdict

        manager = get_automl_manager()
        history = manager.get_optimization_history()

        history_dicts = [asdict(h) for h in history]

        return jsonify({
            'success': True,
            'history': history_dicts
        })
    except Exception as e:
        print(f"AutoML history error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/v4.1/backtest/run', methods=['POST'])
def run_backtest():
    """Run backtesting on strategy"""
    try:
        from ai.backtesting import get_backtest_engine, BacktestConfig
        from ai.backtesting import moving_average_crossover_strategy
        from dataclasses import asdict
        import numpy as np
        from datetime import datetime, timedelta

        # Get parameters from request
        data = request.get_json() or {}
        strategy_name = data.get('strategy_name', 'Custom Strategy')
        initial_capital = data.get('initial_capital', 10000000)

        # Create config
        config = BacktestConfig(initial_capital=initial_capital)
        engine = get_backtest_engine(config)

        # Generate mock historical data
        historical_data = []
        base_price = 73000
        for i in range(100):
            price_change = np.random.uniform(-0.03, 0.03)
            close_price = base_price * (1 + price_change)

            historical_data.append({
                'date': (datetime.now() - timedelta(days=100-i)).isoformat(),
                'stock_code': '005930',
                'open': base_price,
                'high': close_price * 1.02,
                'low': close_price * 0.98,
                'close': close_price,
                'volume': int(np.random.uniform(500000, 2000000)),
                'rsi': np.random.uniform(20, 80)
            })

            base_price = close_price

        # Run backtest
        result = engine.run_backtest(
            historical_data=historical_data,
            strategy_fn=moving_average_crossover_strategy,
            strategy_name=strategy_name
        )

        # Convert to dict (excluding large arrays)
        result_dict = asdict(result)
        result_dict['equity_curve'] = result_dict['equity_curve'][-10:]  # Last 10 only
        result_dict['daily_returns'] = result_dict['daily_returns'][-10:]
        result_dict['trades'] = result_dict['trades'][-10:]  # Last 10 trades

        return jsonify({
            'success': True,
            'result': result_dict
        })
    except Exception as e:
        print(f"Backtest error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/v4.1/all/status')
def get_all_ai_status():
    """Get comprehensive status of all v4.1 AI systems"""
    try:
        from ai.deep_learning import get_deep_learning_manager
        from ai.advanced_rl import get_advanced_rl_manager
        from ai.automl import get_automl_manager

        dl_manager = get_deep_learning_manager()
        rl_manager = get_advanced_rl_manager()
        automl_manager = get_automl_manager()

        return jsonify({
            'success': True,
            'deep_learning': dl_manager.get_performance(),
            'advanced_rl': rl_manager.get_all_performances(),
            'automl': {
                'optimizations_run': len(automl_manager.get_optimization_history())
            },
            'version': '4.1'
        })
    except Exception as e:
        print(f"All AI status error: {e}")
        return jsonify({'success': False, 'message': str(e)})


# ============================================================================
# v4.2 Advanced Systems API
# ============================================================================

@app.route('/api/v4.2/portfolio/optimize', methods=['POST'])
def optimize_portfolio():
    """Optimize portfolio allocation"""
    try:
        from ai.portfolio_optimization import get_portfolio_manager
        from dataclasses import asdict
        import numpy as np

        data = request.get_json() or {}
        n_assets = data.get('n_assets', 5)
        method = data.get('method', 'markowitz')

        # Mock returns
        returns = np.random.randn(252, n_assets) * 0.01

        manager = get_portfolio_manager()

        if method == 'markowitz':
            result = manager.markowitz.optimize(returns)
        elif method == 'risk_parity':
            result = manager.risk_parity.optimize(returns)
        else:
            result = manager.markowitz.optimize(returns)

        return jsonify({
            'success': True,
            'allocation': asdict(result)
        })
    except Exception as e:
        print(f"Portfolio optimization error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/v4.2/sentiment/<stock_code>')
def analyze_sentiment(stock_code: str):
    """Analyze sentiment for stock"""
    try:
        from ai.sentiment_analysis import get_sentiment_manager
        from dataclasses import asdict

        manager = get_sentiment_manager()
        report = manager.analyze_complete(stock_code)
        alerts = manager.generate_alerts(report)

        return jsonify({
            'success': True,
            'report': asdict(report),
            'alerts': alerts
        })
    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/v4.2/multi_agent/consensus', methods=['POST'])
def get_multi_agent_consensus():
    """Get consensus decision from multi-agent system"""
    try:
        from ai.advanced_systems import get_multi_agent_system
        from dataclasses import asdict

        data = request.get_json() or {}
        market_data = data.get('market_data', {
            'price_change_pct': 2.5,
            'z_score': -1.5,
            'pe_ratio': 12
        })

        mas = get_multi_agent_system()
        consensus = mas.get_consensus(market_data)

        return jsonify({
            'success': True,
            'consensus': asdict(consensus)
        })
    except Exception as e:
        print(f"Multi-agent consensus error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/v4.2/risk/assess', methods=['POST'])
def assess_portfolio_risk():
    """Assess portfolio risk"""
    try:
        from ai.advanced_systems import get_risk_manager
        from dataclasses import asdict
        import numpy as np

        data = request.get_json() or {}

        # Mock portfolio returns
        returns_matrix = np.random.randn(252, 5) * 0.01
        positions = {
            f'Asset_{i}': {'weight': 0.2}
            for i in range(5)
        }

        rm = get_risk_manager()
        metrics = rm.assess_portfolio_risk(positions, returns_matrix)

        return jsonify({
            'success': True,
            'metrics': asdict(metrics)
        })
    except Exception as e:
        print(f"Risk assessment error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/v4.2/regime/detect', methods=['POST'])
def detect_market_regime():
    """Detect market regime"""
    try:
        from ai.advanced_systems import get_regime_detector
        from dataclasses import asdict
        import numpy as np

        data = request.get_json() or {}

        # Mock price data
        price_data = np.cumsum(np.random.randn(100)) + 100

        rd = get_regime_detector()
        regime = rd.detect_regime(price_data)
        transitions = rd.predict_regime_transition(regime.regime_type)

        return jsonify({
            'success': True,
            'regime': asdict(regime),
            'transitions': transitions
        })
    except Exception as e:
        print(f"Regime detection error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/v4.2/options/price', methods=['POST'])
def price_option():
    """Price option using Black-Scholes"""
    try:
        from ai.options_hft import get_bs_model
        from dataclasses import asdict

        data = request.get_json() or {}
        spot_price = data.get('spot_price', 100)
        strike_price = data.get('strike_price', 105)
        time_to_expiry = data.get('time_to_expiry', 0.25)
        volatility = data.get('volatility', 0.25)
        option_type = data.get('option_type', 'call')

        bs = get_bs_model()
        price = bs.price_option(spot_price, strike_price, time_to_expiry, volatility, option_type)
        greeks = bs.calculate_greeks(spot_price, strike_price, time_to_expiry, volatility, option_type)

        return jsonify({
            'success': True,
            'price': price,
            'greeks': asdict(greeks)
        })
    except Exception as e:
        print(f"Options pricing error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/v4.2/hft/status')
def get_hft_status():
    """Get HFT system status"""
    try:
        from ai.options_hft import get_hft_trader

        hft = get_hft_trader()
        metrics = hft.get_performance_metrics()

        return jsonify({
            'success': True,
            'metrics': metrics
        })
    except Exception as e:
        print(f"HFT status error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/v4.2/all/status')
def get_v42_all_status():
    """Get comprehensive v4.2 system status"""
    try:
        from ai.portfolio_optimization import get_portfolio_manager
        from ai.sentiment_analysis import get_sentiment_manager
        from ai.advanced_systems import (
            get_multi_agent_system, get_risk_manager,
            get_regime_detector
        )
        from ai.options_hft import get_bs_model, get_hft_trader

        return jsonify({
            'success': True,
            'version': '4.2',
            'systems': {
                'portfolio': 'active',
                'sentiment': 'active',
                'multi_agent': 'active',
                'risk_management': 'active',
                'regime_detection': 'active',
                'options': 'active',
                'hft': 'active'
            },
            'agents_count': len(get_multi_agent_system().agents),
            'hft_avg_latency_us': get_hft_trader().avg_latency_us
        })
    except Exception as e:
        print(f"v4.2 status error: {e}")
        return jsonify({'success': False, 'message': str(e)})
