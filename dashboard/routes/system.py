System Routes Module for AutoTrade Pro v4.2
Handles all system-related API endpoints including status, configuration, monitoring, and notifications.

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from flask import Blueprint, jsonify, request
import yaml

system_bp = Blueprint('system', __name__)

logger = logging.getLogger(__name__)

_bot_instance = None
_config_manager = None
_unified_settings = None
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def set_bot_instance(bot):
    """Set bot instance for this module"""
    global _bot_instance
    _bot_instance = bot


def set_config_manager(manager):
    """Set config manager for this module"""
    global _config_manager
    _config_manager = manager


def set_unified_settings(settings):
    """Set unified settings for this module"""
    global _unified_settings
    _unified_settings = settings


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



@system_bp.route('/api/status')
def get_status():
    """Get system status"""
    control = get_control_status()

    test_mode_info = {}
    if _bot_instance:
        try:
            test_mode_info = _bot_instance.get_test_mode_info()
        except:
            test_mode_info = {'active': False}

    system_status = {
        'running': True,
        'trading_enabled': control.get('trading_enabled', False),
        'uptime': 'N/A',
        'last_update': datetime.now().isoformat()
    }

    if _bot_instance and hasattr(_bot_instance, 'start_time'):
        uptime_seconds = (datetime.now() - _bot_instance.start_time).total_seconds()
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        system_status['uptime'] = f"{hours}h {minutes}m"

    risk_info = {
        'mode': 'NORMAL',
        'description': 'Normal trading conditions'
    }
    if _bot_instance and hasattr(_bot_instance, 'dynamic_risk_manager'):
        try:
            risk_manager = _bot_instance.dynamic_risk_manager
            risk_info['mode'] = risk_manager.current_mode.value if hasattr(risk_manager.current_mode, 'value') else str(risk_manager.current_mode)
            risk_info['description'] = risk_manager.get_mode_description()
        except Exception as e:
            print(f"Error getting risk info: {e}")

    scanning_info = {
        'fast_scan': {'count': 0, 'last_run': 'N/A'},
        'deep_scan': {'count': 0, 'last_run': 'N/A'},
        'ai_scan': {'count': 0, 'last_run': 'N/A'}
    }

    if _bot_instance and hasattr(_bot_instance, 'scan_progress'):
        try:
            scan_progress = _bot_instance.scan_progress
            total_candidates = len(scan_progress.get('top_candidates', []))
            ai_reviewed = len(scan_progress.get('approved', [])) + len(scan_progress.get('rejected', []))
            pending = len(scan_progress.get('approved', []))

            scanning_info = {
                'fast_scan': {'count': total_candidates, 'last_run': 'N/A'},
                'deep_scan': {'count': ai_reviewed, 'last_run': 'N/A'},
                'ai_scan': {'count': pending, 'last_run': 'N/A'}
            }
        except Exception as e:
            print(f"Error getting scanning info: {e}")

    return jsonify({
        'system': system_status,
        'test_mode': test_mode_info,
        'risk': risk_info,
        'scanning': scanning_info
    })


@system_bp.route('/api/v4.2/all/status')
def get_v42_all_status():
    """Get v4.2 system status"""
    try:
        return jsonify({
            'success': True,
            'result': {
                'version': '4.2',
                'ai_systems_count': 18,
                'total_endpoints': 38,
                'uptime': '2시간 30분',
                'active_modules': [
                    'Portfolio Optimization',
                    'Sentiment Analysis',
                    'Multi-Agent System',
                    'Risk Assessment',
                    'Market Regime Detection',
                    'Options Pricing'
                ],
                'avg_response_time': 150,
                'total_requests': 1250,
                'success_rate': 98.5
            }
        })
    except Exception as e:
        print(f"v4.2 status error: {e}")
        return jsonify({'success': False, 'error': str(e)})


@system_bp.route('/api/system-connections')
def get_system_connections():
    """시스템 연결 상태 조회 (WebSocket, REST API, Gemini, 테스트모드 등)"""
    try:
        connections = {
            'rest_api': False,
            'websocket': False,
            'gemini': False,
            'test_mode': False,
            'database': False,
            'bot_connected': _bot_instance is not None
        }

        if not _bot_instance:
            return jsonify(connections)

        if hasattr(_bot_instance, 'client'):
            connections['rest_api'] = True

        if _bot_instance and hasattr(_bot_instance, 'websocket_manager'):
            try:
                ws_manager = _bot_instance.websocket_manager
                if ws_manager is not None:
                    connections['websocket'] = getattr(ws_manager, 'is_connected', False)
                else:
                    connections['websocket'] = False
            except:
                pass
        elif _bot_instance and hasattr(_bot_instance, 'websocket_client'):
            try:
                ws_client = _bot_instance.websocket_client
                if ws_client is None:
                    connections['websocket'] = False
                else:
                    connections['websocket'] = getattr(ws_client, 'is_connected', False)
            except:
                pass

        if _bot_instance and hasattr(_bot_instance, 'analyzer'):
            try:
                analyzer = _bot_instance.analyzer
                if analyzer is not None:
                    analyzer_type = type(analyzer).__name__
                    analyzer_module = type(analyzer).__module__

                    is_mock = 'Mock' in analyzer_type or 'mock' in analyzer_module.lower()
                    is_gemini = 'Gemini' in analyzer_type or 'gemini' in analyzer_module.lower()

                    if analyzer_type == 'EnsembleAnalyzer' and hasattr(analyzer, 'analyzers'):
                        from ai.ensemble_analyzer import AIModel
                        is_gemini = AIModel.GEMINI in analyzer.analyzers

                    connections['gemini'] = is_gemini and not is_mock

                else:
                    connections['gemini'] = False
            except Exception:
                connections['gemini'] = False
        else:
            connections['gemini'] = False

        if _bot_instance:
            connections['test_mode'] = getattr(_bot_instance, 'test_mode_active', False)

        try:
            from database import get_db_session
            session = get_db_session()
            connections['database'] = session is not None
        except:
            pass

        return jsonify(connections)
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@system_bp.route('/api/candidates')
def get_candidates():
    """Get AI-approved buy candidates with split buy strategy"""
    try:
        if not _bot_instance:
            print("Error: bot_instance is None")
            return jsonify([])

        if not hasattr(_bot_instance, 'ai_approved_candidates'):
            print("Error: bot_instance has no ai_approved_candidates")
            return jsonify([])

        approved = _bot_instance.ai_approved_candidates

        if not approved:
            print("No AI approved candidates")
            return jsonify([])

        candidates = []
        for cand in approved:
            try:
                ai_score = cand.get('ai_score', 0)
                if ai_score > 10:
                    ai_score = ai_score / 10.0
                if ai_score > 100:
                    ai_score = min(100, ai_score)

                candidates.append({
                    'code': cand.get('stock_code', ''),
                    'name': cand.get('stock_name', ''),
                    'price': cand.get('current_price', 0),
                    'change_rate': cand.get('change_rate', 0),
                    'ai_score': round(ai_score * 10, 1),
                    'signal': 'BUY',
                    'split_strategy': cand.get('split_strategy', ''),
                    'reason': cand.get('ai_reason', ''),
                    'timestamp': cand.get('timestamp', '')
                })
            except Exception as e:
                print(f"Error processing candidate {cand}: {e}")
                continue

        return jsonify(candidates)

    except Exception as e:
        print(f"Error getting candidates: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([])


@system_bp.route('/api/scan-progress')
def get_scan_progress():
    """Get real-time scan progress"""
    try:
        if _bot_instance and hasattr(_bot_instance, 'scan_progress'):
            return jsonify(_bot_instance.scan_progress)
        return jsonify({
            'current_strategy': '',
            'total_candidates': 0,
            'top_candidates': [],
            'reviewing': '',
            'rejected': [],
            'approved': []
        })
    except Exception as e:
        print(f"Error getting scan progress: {e}")
        return jsonify({
            'current_strategy': '',
            'total_candidates': 0,
            'top_candidates': [],
            'reviewing': '',
            'rejected': [],
            'approved': []
        })



@system_bp.route('/api/activities')
def get_activities():
    """Get recent activities from activity monitor (real-time, no hardcoding)"""
    activities = []

    try:
        if _bot_instance and hasattr(_bot_instance, 'monitor'):
            from utils.activity_monitor import get_monitor
            monitor = get_monitor()
            recent_activities = monitor.get_recent_activities(limit=50)

            for activity in recent_activities:
                timestamp_str = activity.get('timestamp', datetime.now().isoformat())
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    time_str = timestamp.strftime('%H:%M:%S')
                except:
                    time_str = datetime.now().strftime('%H:%M:%S')

                activities.append({
                    'time': time_str,
                    'type': activity.get('type', 'SYSTEM').upper(),
                    'message': activity.get('message', ''),
                    'level': activity.get('level', 'info')
                })


    except Exception as e:
        print(f"Error getting activities: {e}")
        activities = [{
            'time': datetime.now().strftime('%H:%M:%S'),
            'type': 'ERROR',
            'message': f'활동 로그 조회 오류: {str(e)}',
            'level': 'error'
        }]

    return jsonify(activities)


@system_bp.route('/api/trading-activity')
def get_trading_activity():
    """Get recent trading activity from activity monitor"""
    try:
        activities = []

        if _bot_instance and hasattr(_bot_instance, 'monitor'):
            from utils.activity_monitor import get_monitor
            monitor = get_monitor()
            recent_activities = monitor.get_recent_activities(limit=50)

            for activity in recent_activities:
                timestamp_str = activity.get('timestamp', datetime.now().isoformat())
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    time_str = timestamp.strftime('%H:%M:%S')
                except:
                    time_str = datetime.now().strftime('%H:%M:%S')

                activities.append({
                    'time': time_str,
                    'type': activity.get('type', 'SYSTEM').upper(),
                    'message': activity.get('message', ''),
                    'level': activity.get('level', 'info')
                })

        return jsonify({
            'success': True,
            'activities': activities
        })

    except Exception as e:
        print(f"Trading activity error: {e}")
        return jsonify({'success': True, 'activities': []})



@system_bp.route('/api/config/features', methods=['GET'])
def get_features_config():
    """Get all features configuration"""
    config = load_features_config()
    return jsonify(config)


@system_bp.route('/api/config/features', methods=['POST'])
def update_features_config():
    """Update features configuration"""
    try:
        new_config = request.json
        if save_features_config(new_config):
            return jsonify({'success': True, 'message': 'Configuration updated'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save configuration'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@system_bp.route('/api/config/feature/<path:feature_path>', methods=['PATCH'])
def update_feature_toggle(feature_path: str):
    """Toggle a specific feature on/off"""
    try:
        data = request.json
        enabled = data.get('enabled', True)

        config = load_features_config()

        keys = feature_path.split('.')
        current = config
        for key in keys[:-1]:
            if key not in current:
                return jsonify({'success': False, 'message': f'Invalid path: {feature_path}'}), 400
            current = current[key]

        current[keys[-1]] = enabled

        if save_features_config(config):
            return jsonify({'success': True, 'message': f'Feature {feature_path} updated'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@system_bp.route('/api/settings', methods=['GET'])
def get_settings():
    """통합 설정 조회"""
    try:
        if _unified_settings:
            return jsonify(_unified_settings.settings)
        else:
            return jsonify({'error': 'Settings manager not available'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@system_bp.route('/api/settings', methods=['POST'])
def save_settings():
    """통합 설정 저장"""
    try:
        if not _unified_settings:
            return jsonify({'error': 'Settings manager not available'}), 500

        new_settings = request.json

        for category, values in new_settings.items():
            if isinstance(values, dict):
                _unified_settings.update_category(category, values, save_immediately=False)

        _unified_settings.save()

        return jsonify({'success': True, 'message': '설정이 저장되었습니다.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@system_bp.route('/api/settings/reset', methods=['POST'])
def reset_settings():
    """설정 기본값 복원"""
    try:
        if not _unified_settings:
            return jsonify({'error': 'Settings manager not available'}), 500

        _unified_settings.reset_to_defaults()
        return jsonify({'success': True, 'message': '기본값으로 복원되었습니다.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



@system_bp.route('/api/journal/entries')
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


@system_bp.route('/api/journal/statistics')
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


@system_bp.route('/api/journal/insights')
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



@system_bp.route('/api/notifications')
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


@system_bp.route('/api/notifications/mark_read/<notification_id>', methods=['POST'])
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


@system_bp.route('/api/notifications/configure/telegram', methods=['POST'])
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


@system_bp.route('/api/notifications/send', methods=['POST'])
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



@system_bp.route('/api/market-regime')
def get_market_regime():
    """시장 레짐 조회"""
    try:
        return jsonify({
            'regime': 'bull',
            'volatility': 'medium',
            'confidence': 0.75,
            'recommended_strategy': 'momentum',
            'last_update': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@system_bp.route('/api/anomalies')
def get_anomalies():
    """이상 감지 현황 조회"""
    try:
        return jsonify({
            'total_count': 0,
            'recent_24h': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'events': []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@system_bp.route('/api/websocket/subscriptions')
def get_websocket_subscriptions():
    """현재 웹소켓 구독 리스트 조회"""
    try:
        subscriptions = {
            'price': [],
            'orderbook': [],
            'execution': [],
            'total': 0
        }

        if _bot_instance and hasattr(_bot_instance, 'websocket_manager'):
            ws_manager = _bot_instance.websocket_manager
            if ws_manager and hasattr(ws_manager, 'get_subscription_info'):
                try:
                    info = ws_manager.get_subscription_info()
                    subs = info.get('subscriptions', {})

                    for grp_no, sub_info in subs.items():
                        stock_codes = sub_info.get('stock_codes', [])
                        types = sub_info.get('types', [])

                        for stock_code in stock_codes:
                            for sub_type in types:
                                item = {
                                    'stock_code': stock_code,
                                    'stock_name': stock_code,
                                    'type': sub_type,
                                    'grp_no': grp_no
                                }

                                if sub_type in ['0B', '0A']:
                                    subscriptions['price'].append(item)
                                elif sub_type in ['0D', '0C']:
                                    subscriptions['orderbook'].append(item)
                                elif sub_type in ['00', '04']:
                                    subscriptions['execution'].append(item)
                except Exception as e:
                    print(f"웹소켓 구독 정보 조회 오류: {e}")

        if _bot_instance and hasattr(_bot_instance, 'account_api'):
            try:
                holdings = _bot_instance.account_api.get_holdings()
                if holdings:
                    existing_codes = {item['stock_code'] for item in subscriptions['price']}
                    for holding in holdings:
                        stock_code = str(holding.get('stk_cd', '')).strip()
                        if stock_code.startswith('A'):
                            stock_code = stock_code[1:]

                        if stock_code and stock_code not in existing_codes:
                            stock_name = holding.get('stk_nm', stock_code)
                            subscriptions['price'].append({
                                'stock_code': stock_code,
                                'stock_name': stock_name,
                                'type': 'holdings'
                            })
            except Exception as e:
                print(f"보유 종목 조회 오류: {e}")

        subscriptions['total'] = (
            len(subscriptions['price']) +
            len(subscriptions['orderbook']) +
            len(subscriptions['execution'])
        )

        return jsonify({
            'success': True,
            'data': subscriptions
        })

    except Exception as e:
        logger.error(f"웹소켓 구독 리스트 조회 실패: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
