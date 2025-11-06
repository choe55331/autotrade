"""
Multi-Model AI Analysis Routes
멀티모델 AI 분석 API 엔드포인트
"""

from flask import Blueprint, jsonify, request
from ai.multi_model_orchestrator import get_multi_model_orchestrator

multi_model_bp = Blueprint('multi_model', __name__)

_bot_instance = None


def set_bot_instance(bot):
    """Bot 인스턴스 설정"""
    global _bot_instance
    _bot_instance = bot


@multi_model_bp.route('/api/ai/multi-model/analyze/<stock_code>', methods=['POST'])
async def analyze_with_multi_model(stock_code: str):
    """멀티모델 분석 수행"""
    try:
        if not _bot_instance:
            return jsonify({
                'status': 'error',
                'message': 'Bot instance not initialized'
            }), 500

        orchestrator = get_multi_model_orchestrator()

        data = request.get_json() or {}

        stock_data = data.get('stock_data', {})
        technical_indicators = data.get('technical_indicators', {})
        market_data = data.get('market_data', {})
        portfolio_info = data.get('portfolio_info')

        if not stock_data:
            stock_info = await _bot_instance.get_stock_info(stock_code)
            stock_data = {
                'stock_code': stock_code,
                'stock_name': stock_info.get('name', ''),
                'current_price': stock_info.get('price', 0),
                'change_rate': stock_info.get('change_rate', 0),
                'volume': stock_info.get('volume', 0)
            }

        consensus = await orchestrator.analyze_stock_consensus(
            stock_data=stock_data,
            technical_indicators=technical_indicators,
            market_data=market_data,
            portfolio_info=portfolio_info
        )

        response_data = {
            'final_signal': consensus.final_signal,
            'consensus_confidence': consensus.consensus_confidence,
            'consensus_score': consensus.consensus_score,
            'agreement_level': consensus.agreement_level,
            'recommendation': consensus.recommendation,
            'combined_reasons': consensus.combined_reasons,
            'combined_risks': consensus.combined_risks,
            'target_price_range': {
                'min': consensus.target_price_range[0],
                'max': consensus.target_price_range[1]
            },
            'stop_loss_consensus': consensus.stop_loss_consensus,
            'disagreement_factors': consensus.disagreement_factors,
            'model_predictions': [
                {
                    'model': pred.model_name,
                    'signal': pred.signal,
                    'confidence': pred.confidence_score,
                    'score': pred.overall_score,
                    'execution_time': pred.execution_time
                }
                for pred in consensus.model_predictions
            ]
        }

        return jsonify({
            'status': 'success',
            'data': response_data
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@multi_model_bp.route('/api/ai/multi-model/performance', methods=['GET'])
def get_model_performance():
    """모델 성능 조회"""
    try:
        orchestrator = get_multi_model_orchestrator()
        performance = orchestrator.get_model_performance()

        return jsonify({
            'status': 'success',
            'data': performance
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@multi_model_bp.route('/api/ai/multi-model/configure', methods=['POST'])
def configure_models():
    """모델 설정 변경"""
    try:
        data = request.get_json()

        model_name = data.get('model_name')
        if not model_name:
            return jsonify({
                'status': 'error',
                'message': 'model_name is required'
            }), 400

        orchestrator = get_multi_model_orchestrator()

        if 'enabled' in data:
            orchestrator.set_model_enabled(model_name, data['enabled'])

        if 'weight' in data:
            orchestrator.update_model_weight(model_name, data['weight'])

        return jsonify({
            'status': 'success',
            'message': f'Model {model_name} configured successfully'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@multi_model_bp.route('/api/ai/multi-model/batch-analyze', methods=['POST'])
async def batch_analyze():
    """여러 종목 일괄 분석"""
    try:
        data = request.get_json()
        stock_codes = data.get('stock_codes', [])

        if not stock_codes:
            return jsonify({
                'status': 'error',
                'message': 'stock_codes is required'
            }), 400

        if len(stock_codes) > 20:
            return jsonify({
                'status': 'error',
                'message': 'Maximum 20 stocks per request'
            }), 400

        orchestrator = get_multi_model_orchestrator()
        results = {}

        for stock_code in stock_codes:
            try:
                stock_info = await _bot_instance.get_stock_info(stock_code)

                stock_data = {
                    'stock_code': stock_code,
                    'stock_name': stock_info.get('name', ''),
                    'current_price': stock_info.get('price', 0),
                    'change_rate': stock_info.get('change_rate', 0),
                    'volume': stock_info.get('volume', 0)
                }

                consensus = await orchestrator.analyze_stock_consensus(
                    stock_data=stock_data,
                    technical_indicators={},
                    market_data={},
                    portfolio_info=None
                )

                results[stock_code] = {
                    'signal': consensus.final_signal,
                    'confidence': consensus.consensus_confidence,
                    'score': consensus.consensus_score,
                    'agreement': consensus.agreement_level,
                    'recommendation': consensus.recommendation
                }

            except Exception as e:
                results[stock_code] = {
                    'error': str(e)
                }

        return jsonify({
            'status': 'success',
            'data': results
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
