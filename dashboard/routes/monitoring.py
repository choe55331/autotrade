"""
Monitoring Routes
시스템 모니터링 API 엔드포인트
"""

from flask import Blueprint, jsonify, request
from utils.advanced_performance_monitor import get_performance_monitor
from core.enhanced_websocket import EnhancedWebSocketManager

monitoring_bp = Blueprint('monitoring', __name__)

_enhanced_ws_manager: EnhancedWebSocketManager = None
_performance_monitor = get_performance_monitor()


def set_enhanced_ws_manager(manager: EnhancedWebSocketManager):
    """Enhanced WebSocket Manager 설정"""
    global _enhanced_ws_manager
    _enhanced_ws_manager = manager


@monitoring_bp.route('/api/monitoring/system', methods=['GET'])
def get_system_metrics():
    """시스템 메트릭 조회"""
    try:
        current_metrics = _performance_monitor.get_current_metrics()
        health = _performance_monitor.get_system_health()

        return jsonify({
            'status': 'success',
            'data': {
                'current': current_metrics,
                'health': {
                    'status': health.status,
                    'cpu_healthy': health.cpu_healthy,
                    'memory_healthy': health.memory_healthy,
                    'disk_healthy': health.disk_healthy,
                    'network_healthy': health.network_healthy,
                    'issues': health.issues,
                    'recommendations': health.recommendations
                }
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/api/monitoring/functions', methods=['GET'])
def get_function_metrics():
    """함수 실행 메트릭 조회"""
    try:
        top_n = request.args.get('top_n', 20, type=int)
        sort_by = request.args.get('sort_by', 'calls')

        if sort_by == 'calls':
            metrics = _performance_monitor.get_function_metrics(top_n=top_n)
        elif sort_by == 'slowest':
            metrics = _performance_monitor.get_slowest_functions(top_n=top_n)
        else:
            metrics = _performance_monitor.get_function_metrics(top_n=top_n)

        return jsonify({
            'status': 'success',
            'data': {
                'metrics': metrics,
                'sort_by': sort_by
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/api/monitoring/statistics', methods=['GET'])
def get_statistics():
    """통계 조회"""
    try:
        minutes = request.args.get('minutes', 60, type=int)
        stats = _performance_monitor.get_statistics(minutes=minutes)

        return jsonify({
            'status': 'success',
            'data': stats
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/api/monitoring/websocket', methods=['GET'])
def get_websocket_status():
    """WebSocket 상태 조회"""
    try:
        if _enhanced_ws_manager is None:
            return jsonify({
                'status': 'success',
                'data': {
                    'enabled': False,
                    'message': 'Enhanced WebSocket Manager not initialized'
                }
            })

        metrics = _enhanced_ws_manager.get_metrics()

        return jsonify({
            'status': 'success',
            'data': {
                'enabled': True,
                **metrics
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/api/monitoring/health', methods=['GET'])
def health_check():
    """종합 헬스 체크"""
    try:
        system_health = _performance_monitor.get_system_health()
        current_metrics = _performance_monitor.get_current_metrics()

        ws_healthy = True
        ws_status = "not_initialized"

        if _enhanced_ws_manager:
            ws_metrics = _enhanced_ws_manager.get_metrics()
            ws_healthy = ws_metrics['health']['is_connected']
            ws_status = ws_metrics['state']

        overall_status = "healthy"
        if system_health.status == "degraded" or not ws_healthy:
            overall_status = "degraded"
        if system_health.status == "critical":
            overall_status = "critical"

        return jsonify({
            'status': 'success',
            'data': {
                'overall_status': overall_status,
                'system': {
                    'status': system_health.status,
                    'cpu_percent': current_metrics.get('cpu_percent'),
                    'memory_percent': current_metrics.get('memory_percent'),
                    'issues': system_health.issues
                },
                'websocket': {
                    'healthy': ws_healthy,
                    'status': ws_status
                },
                'recommendations': system_health.recommendations
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
