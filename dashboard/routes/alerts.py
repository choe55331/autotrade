"""
dashboard/routes/alerts.py
v5.7.5: 알림 시스템 API 라우트
"""
from flask import Blueprint, jsonify, request
from utils.alert_manager import get_alert_manager

# Create blueprint
alerts_bp = Blueprint('alerts', __name__)

# Module-level bot instance
_bot_instance = None


def set_bot_instance(bot):
    """Set the bot instance for this module"""
    global _bot_instance
    _bot_instance = bot


@alerts_bp.route('/api/alerts')
def get_alerts():
    """알림 목록 조회"""
    try:
        alert_manager = get_alert_manager()

        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 50))

        alerts = alert_manager.get_alerts(unread_only=unread_only, limit=limit)

        return jsonify({
            'success': True,
            'alerts': [alert.to_dict() for alert in alerts],
            'unread_count': alert_manager.get_unread_count(),
            'total_count': len(alert_manager.alerts)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@alerts_bp.route('/api/alerts/<alert_id>/read', methods=['POST'])
def mark_alert_read(alert_id: str):
    """알림 읽음 처리"""
    try:
        alert_manager = get_alert_manager()
        alert_manager.mark_as_read(alert_id)

        return jsonify({'success': True, 'message': '알림이 읽음 처리되었습니다.'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@alerts_bp.route('/api/alerts/read-all', methods=['POST'])
def mark_all_alerts_read():
    """모든 알림 읽음 처리"""
    try:
        alert_manager = get_alert_manager()
        alert_manager.mark_all_as_read()

        return jsonify({'success': True, 'message': '모든 알림이 읽음 처리되었습니다.'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@alerts_bp.route('/api/alerts/settings', methods=['GET', 'POST'])
def alert_settings():
    """알림 설정 조회/변경"""
    try:
        alert_manager = get_alert_manager()

        if request.method == 'POST':
            data = request.json
            alert_manager.set_thresholds(
                profit_target=data.get('profit_target'),
                stop_loss=data.get('stop_loss'),
                big_profit=data.get('big_profit'),
                big_loss=data.get('big_loss')
            )
            return jsonify({
                'success': True,
                'message': '알림 설정이 변경되었습니다.',
                'thresholds': alert_manager.thresholds
            })
        else:
            return jsonify({
                'success': True,
                'thresholds': alert_manager.thresholds
            })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@alerts_bp.route('/api/alerts/stats')
def alert_stats():
    """알림 통계"""
    try:
        alert_manager = get_alert_manager()

        # 알림 타입별 집계
        type_counts = {}
        level_counts = {}

        for alert in alert_manager.alerts:
            alert_type = alert.alert_type.value
            alert_level = alert.level.value

            type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
            level_counts[alert_level] = level_counts.get(alert_level, 0) + 1

        return jsonify({
            'success': True,
            'stats': {
                'total_count': len(alert_manager.alerts),
                'unread_count': alert_manager.get_unread_count(),
                'type_counts': type_counts,
                'level_counts': level_counts
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
