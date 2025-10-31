"""
dashboard/dashboard_ultra.py
AutoTrade Pro v2.0 - 미래지향적 프리미엄 대시보드
"""
import logging
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from pathlib import Path
import json
from datetime import datetime
import threading
import time

logger = logging.getLogger(__name__)


def create_app(bot_instance=None):
    """Flask 앱 생성"""
    # 템플릿 디렉토리 설정
    template_folder = Path(__file__).parent / 'templates'
    template_folder.mkdir(exist_ok=True)

    app = Flask(__name__, template_folder=str(template_folder))
    app.config['SECRET_KEY'] = 'autotrade-pro-v2-secret-key'
    app.config['bot'] = bot_instance

    # SocketIO 초기화
    socketio = SocketIO(app, cors_allowed_origins="*")

    # ==================== 메인 페이지 ====================

    @app.route('/')
    def index():
        """메인 대시보드"""
        return render_template('dashboard_ultra.html')

    # ==================== API 엔드포인트 ====================

    @app.route('/api/status')
    def get_status():
        """시스템 상태"""
        try:
            bot = app.config.get('bot')

            if hasattr(bot, 'dynamic_risk_manager'):
                risk_status = bot.dynamic_risk_manager.get_status_summary()
                risk_mode = bot.dynamic_risk_manager.current_mode.value
                risk_description = bot.dynamic_risk_manager.get_mode_description()
            else:
                risk_status = {}
                risk_mode = 'normal'
                risk_description = '일반 모드'

            if hasattr(bot, 'scanner_pipeline'):
                scan_summary = bot.scanner_pipeline.get_scan_summary()
            else:
                scan_summary = {
                    'fast_scan': {'count': 0},
                    'deep_scan': {'count': 0},
                    'ai_scan': {'count': 0}
                }

            return jsonify({
                'status': 'running' if bot.is_running else 'stopped',
                'is_running': bot.is_running,
                'pause_buy': getattr(bot, 'pause_buy', False),
                'pause_sell': getattr(bot, 'pause_sell', False),
                'risk_mode': risk_mode,
                'risk_description': risk_description,
                'scan_summary': scan_summary,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Status error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/account')
    def get_account():
        """계좌 정보"""
        try:
            bot = app.config.get('bot')

            if hasattr(bot, 'portfolio_manager'):
                summary = bot.portfolio_manager.get_portfolio_summary()
            else:
                summary = {
                    'total_assets': 0,
                    'cash': 0,
                    'stock_value': 0,
                    'total_profit_loss': 0,
                    'total_profit_loss_rate': 0,
                    'position_count': 0
                }

            return jsonify(summary)
        except Exception as e:
            logger.error(f"Account error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/positions')
    def get_positions():
        """보유 포지션"""
        try:
            bot = app.config.get('bot')

            if hasattr(bot, 'account_api'):
                holdings = bot.account_api.get_holdings()
                positions = []

                for h in holdings:
                    positions.append({
                        'stock_code': h.get('pdno', ''),
                        'stock_name': h.get('prdt_name', ''),
                        'quantity': int(h.get('hldg_qty', 0)),
                        'buy_price': int(h.get('pchs_avg_pric', 0)),
                        'current_price': int(h.get('prpr', 0)),
                        'profit_loss': int(h.get('evlu_pfls_amt', 0)),
                        'profit_loss_rate': float(h.get('evlu_pfls_rt', 0))
                    })

                return jsonify(positions)
            else:
                return jsonify([])
        except Exception as e:
            logger.error(f"Positions error: {e}")
            return jsonify([])

    @app.route('/api/candidates')
    def get_candidates():
        """후보 종목"""
        try:
            bot = app.config.get('bot')

            if hasattr(bot, 'scanner_pipeline'):
                ai_results = bot.scanner_pipeline.ai_scan_results
                candidates = []

                for candidate in ai_results[:10]:
                    candidates.append({
                        'stock_code': candidate.code,
                        'stock_name': candidate.name,
                        'price': candidate.price,
                        'rate': candidate.rate,
                        'ai_score': candidate.ai_score,
                        'ai_signal': candidate.ai_signal,
                        'ai_confidence': candidate.ai_confidence,
                        'final_score': candidate.final_score
                    })

                return jsonify(candidates)
            else:
                return jsonify([])
        except Exception as e:
            logger.error(f"Candidates error: {e}")
            return jsonify([])

    @app.route('/api/activities')
    def get_activities():
        """활동 로그"""
        try:
            bot = app.config.get('bot')

            if hasattr(bot, 'monitor'):
                activities = bot.monitor.get_recent_activities(50)
                return jsonify(activities)
            else:
                return jsonify([])
        except Exception as e:
            logger.error(f"Activities error: {e}")
            return jsonify([])

    @app.route('/api/trades/recent')
    def get_recent_trades():
        """최근 거래"""
        try:
            bot = app.config.get('bot')

            if hasattr(bot, 'db_session'):
                from database import Trade
                trades = bot.db_session.query(Trade).order_by(Trade.timestamp.desc()).limit(20).all()

                return jsonify([{
                    'timestamp': t.timestamp.isoformat(),
                    'action': t.action,
                    'stock_code': t.stock_code,
                    'stock_name': t.stock_name,
                    'quantity': t.quantity,
                    'price': t.price,
                    'total_amount': t.total_amount,
                    'profit_loss': t.profit_loss,
                    'ai_score': t.ai_score,
                    'scoring_total': t.scoring_total
                } for t in trades])
            else:
                return jsonify([])
        except Exception as e:
            logger.error(f"Trades error: {e}")
            return jsonify([])

    @app.route('/api/config', methods=['GET', 'POST'])
    def config_endpoint():
        """설정 관리"""
        try:
            if request.method == 'GET':
                # 설정 조회
                from config.config_manager import get_config
                config = get_config()

                return jsonify({
                    'position': config.position,
                    'profit_loss': config.profit_loss,
                    'scanning': config.scanning,
                    'risk_management': config.risk_management
                })

            elif request.method == 'POST':
                # 설정 업데이트
                data = request.json
                from config.config_manager import get_config, save_config
                config = get_config()

                # 설정 변경
                if 'max_open_positions' in data:
                    config.set('position.max_open_positions', data['max_open_positions'])

                if 'take_profit_ratio' in data:
                    config.set('profit_loss.take_profit_ratio', data['take_profit_ratio'])

                if 'stop_loss_ratio' in data:
                    config.set('profit_loss.stop_loss_ratio', data['stop_loss_ratio'])

                # 저장
                save_config()

                return jsonify({'success': True})

        except Exception as e:
            logger.error(f"Config error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/control', methods=['POST'])
    def control():
        """봇 제어"""
        try:
            data = request.json
            action = data.get('action')

            control_file = Path('data/control.json')

            if control_file.exists():
                with open(control_file, 'r') as f:
                    control_data = json.load(f)
            else:
                control_data = {}

            if action == 'pause_buy':
                control_data['pause_buy'] = not control_data.get('pause_buy', False)
            elif action == 'pause_sell':
                control_data['pause_sell'] = not control_data.get('pause_sell', False)
            elif action == 'stop':
                control_data['run'] = False
            elif action == 'start':
                control_data['run'] = True

            with open(control_file, 'w') as f:
                json.dump(control_data, f, indent=2)

            return jsonify({'success': True, 'control': control_data})

        except Exception as e:
            logger.error(f"Control error: {e}")
            return jsonify({'error': str(e)}), 500

    # ==================== WebSocket 이벤트 ====================

    @socketio.on('connect')
    def handle_connect():
        """클라이언트 연결"""
        logger.info("Client connected")
        emit('connected', {'data': 'Connected to AutoTrade Pro v2.0'})

    @socketio.on('disconnect')
    def handle_disconnect():
        """클라이언트 연결 해제"""
        logger.info("Client disconnected")

    # 실시간 업데이트 스레드
    def realtime_updates():
        """실시간 데이터 푸시"""
        while True:
            try:
                time.sleep(2)  # 2초마다 업데이트

                bot = app.config.get('bot')
                if not bot:
                    continue

                # 상태 업데이트
                with app.app_context():
                    socketio.emit('status_update', {
                        'timestamp': datetime.now().isoformat()
                    })

            except Exception as e:
                logger.error(f"Realtime update error: {e}")

    # 실시간 업데이트 스레드 시작
    update_thread = threading.Thread(target=realtime_updates, daemon=True)
    update_thread.start()

    app.socketio = socketio
    return app


def run_dashboard(bot_instance, host='0.0.0.0', port=5000, debug=False):
    """대시보드 실행"""
    app = create_app(bot_instance)

    logger.info(f"대시보드 시작: http://{host}:{port}")

    # SocketIO로 실행
    app.socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
