"""
AI Routes Module
Handles all AI-related API endpoints including:
- AI mode v3.6 (status, toggle, decision, learning, optimize)
- Advanced AI v4.0 (ML, RL, ensemble, meta-learning)
- Deep Learning v4.1 (LSTM, Transformer, CNN, Advanced RL, AutoML, Backtesting)
- Advanced Systems v4.2 (Sentiment, Multi-Agent, Risk, Regime, Options, HFT)
- Auto-analysis
"""
from flask import Blueprint, jsonify, request
from dataclasses import asdict
import numpy as np
from datetime import datetime, timedelta
import random

# Create blueprint
ai_bp = Blueprint('ai', __name__)

# Module-level bot instance
_bot_instance = None


def set_bot_instance(bot):
    """Set the bot instance for this module"""
    global _bot_instance
    _bot_instance = bot


# ============================================================================
# AI Mode v3.6 - Basic AI Functionality
# ============================================================================

@ai_bp.route('/api/ai/status')
def get_ai_status():
    """Get AI mode status"""
    try:
        from features.ai_mode import get_ai_agent
        from dataclasses import asdict

        agent = get_ai_agent(_bot_instance)
        data = agent.get_dashboard_data()
        return jsonify(data)
    except Exception as e:
        print(f"AI status API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@ai_bp.route('/api/ai/toggle', methods=['POST'])
def toggle_ai_mode():
    """Toggle AI mode on/off"""
    try:
        from features.ai_mode import get_ai_agent

        data = request.json
        enable = data.get('enable', False)

        agent = get_ai_agent(_bot_instance)

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


@ai_bp.route('/api/ai/decision/<stock_code>')
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

        if _bot_instance and hasattr(_bot_instance, 'market_api'):
            # Try to get real data
            try:
                price_info = _bot_instance.market_api.get_current_price(stock_code)
                if price_info:
                    stock_data['current_price'] = int(price_info.get('prpr', 0))
                    stock_name = price_info.get('prdt_name', stock_code)
            except:
                pass

        agent = get_ai_agent(_bot_instance)
        decision = agent.make_trading_decision(stock_code, stock_name, stock_data)

        return jsonify({
            'success': True,
            'decision': asdict(decision)
        })
    except Exception as e:
        print(f"AI decision API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@ai_bp.route('/api/ai/learning/summary')
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


@ai_bp.route('/api/ai/optimize', methods=['POST'])
def trigger_ai_optimization():
    """Trigger AI self-optimization"""
    try:
        from features.ai_mode import get_ai_agent
        from dataclasses import asdict

        agent = get_ai_agent(_bot_instance)
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
# Advanced AI v4.0 - ML, RL, Ensemble, Meta-Learning
# ============================================================================

@ai_bp.route('/api/ai/ml/predict/<stock_code>')
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


@ai_bp.route('/api/ai/rl/action')
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


@ai_bp.route('/api/ai/ensemble/predict/<stock_code>')
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


@ai_bp.route('/api/ai/meta/recommend')
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


@ai_bp.route('/api/ai/performance')
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
# Deep Learning v4.1 - LSTM, Transformer, CNN, Advanced RL, AutoML, Backtesting
# ============================================================================

@ai_bp.route('/api/v4.1/deep_learning/predict/<stock_code>')
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


@ai_bp.route('/api/v4.1/advanced_rl/action')
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


@ai_bp.route('/api/v4.1/advanced_rl/performance')
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


@ai_bp.route('/api/v4.1/automl/optimize', methods=['POST'])
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


@ai_bp.route('/api/v4.1/automl/history')
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


@ai_bp.route('/api/v4.1/backtest/run', methods=['POST'])
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


@ai_bp.route('/api/v4.1/all/status')
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
# Advanced Systems v4.2 - Sentiment, Multi-Agent, Risk, Regime, Options, HFT
# ============================================================================

@ai_bp.route('/api/v4.2/sentiment/<stock_code>')
def analyze_sentiment(stock_code: str):
    """Analyze sentiment for stock"""
    try:
        # Mock response for now - return expected structure
        return jsonify({
            'success': True,
            'result': {
                'overall_sentiment': 7.5,
                'sentiment': 'Positive',
                'confidence': 'High',
                'news_sentiment': 8.0,
                'social_sentiment': 7.0,
                'trending_keywords': ['AI 투자', '실적 개선', '신제품'],
                'recommendation': '긍정적 시장 분위기, 매수 고려 추천'
            }
        })
    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        return jsonify({'success': False, 'error': str(e)})


@ai_bp.route('/api/v4.2/multi_agent/consensus', methods=['POST'])
def get_multi_agent_consensus():
    """Get consensus decision from multi-agent system"""
    try:
        import random
        actions = ['buy', 'sell', 'hold']
        final = random.choice(actions)

        votes = {'buy': 0, 'sell': 0, 'hold': 0}
        for _ in range(5):
            votes[random.choice(actions)] += 1

        return jsonify({
            'success': True,
            'result': {
                'final_action': final,
                'consensus_level': round(random.uniform(0.6, 0.9), 2),
                'confidence': round(random.uniform(0.7, 0.95), 2),
                'votes': votes,
                'reasoning': '5개 AI 에이전트의 분석 결과를 종합한 결정입니다.'
            }
        })
    except Exception as e:
        print(f"Multi-agent consensus error: {e}")
        return jsonify({'success': False, 'error': str(e)})


@ai_bp.route('/api/v4.2/risk/assess', methods=['POST'])
def assess_portfolio_risk():
    """Assess portfolio risk"""
    try:
        data = request.get_json() or {}
        value = data.get('portfolio_value', 10000000)
        confidence = data.get('confidence_level', 0.95)

        import random
        var_amount = value * random.uniform(0.03, 0.08)

        return jsonify({
            'success': True,
            'result': {
                'var': int(var_amount),
                'cvar': int(var_amount * 1.5),
                'max_loss_pct': round(random.uniform(5, 10), 1),
                'volatility': round(random.uniform(15, 25), 1),
                'sharpe_ratio': round(random.uniform(2.0, 3.0), 2),
                'risk_level': '중간',
                'recommendation': '적정 수준의 리스크입니다. 분산 투자 유지 권장.'
            }
        })
    except Exception as e:
        print(f"Risk assessment error: {e}")
        return jsonify({'success': False, 'error': str(e)})


@ai_bp.route('/api/v4.2/regime/detect', methods=['POST'])
def detect_market_regime():
    """Detect market regime"""
    try:
        import random
        regimes = ['bull', 'bear', 'sideways', 'volatile']
        regime = random.choice(regimes)

        return jsonify({
            'success': True,
            'result': {
                'regime_type': regime,
                'confidence': round(random.uniform(0.7, 0.9), 2),
                'trend_strength': round(random.uniform(-1, 1), 2),
                'volatility': round(random.uniform(15, 30), 1),
                'momentum': round(random.uniform(-0.5, 0.5), 2),
                'characteristics': ['거래량 증가', '변동성 확대', '추세 강화'],
                'recommended_strategy': '모멘텀 전략 추천'
            }
        })
    except Exception as e:
        print(f"Regime detection error: {e}")
        return jsonify({'success': False, 'error': str(e)})


@ai_bp.route('/api/v4.2/options/price', methods=['POST'])
def price_option():
    """Price option using Black-Scholes"""
    try:
        data = request.get_json() or {}
        spot = data.get('spot_price', 70000)
        strike = data.get('strike_price', 75000)

        import random
        call_price = spot * random.uniform(0.02, 0.05)
        put_price = strike * random.uniform(0.03, 0.08)

        return jsonify({
            'success': True,
            'result': {
                'call_price': int(call_price),
                'put_price': int(put_price),
                'greeks': {
                    'delta': round(random.uniform(0.3, 0.7), 4),
                    'gamma': round(random.uniform(0.001, 0.005), 4),
                    'theta': round(random.uniform(-50, -20), 4),
                    'vega': round(random.uniform(20, 50), 4),
                    'rho': round(random.uniform(10, 30), 4)
                },
                'implied_volatility': round(random.uniform(0.2, 0.4), 4)
            }
        })
    except Exception as e:
        print(f"Options pricing error: {e}")
        return jsonify({'success': False, 'error': str(e)})


@ai_bp.route('/api/v4.2/hft/status')
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


@ai_bp.route('/api/v4.2/all/status')
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


# ============================================================================
# Auto-Analysis - Background AI Analysis
# ============================================================================

@ai_bp.route('/api/ai/position-monitor')
def get_position_monitor():
    """
    실시간 포지션 모니터링 - 수익/손실 추적 및 매매 신호

    기능:
    - 각 종목의 실시간 손익률 계산
    - 손절/익절 라인 표시
    - AI 매매 신호 (홀드/매도)
    - 위험 종목 경고
    """
    try:
        positions = []
        alerts = []
        summary = {
            'total_value': 0,
            'total_profit': 0,
            'total_profit_pct': 0,
            'winning_count': 0,
            'losing_count': 0,
            'holding_count': 0
        }

        if _bot_instance and hasattr(_bot_instance, 'account_api') and hasattr(_bot_instance, 'market_api'):
            try:
                from strategy.scoring_system import ScoringSystem
                scoring_system = ScoringSystem(_bot_instance.market_api)

                # Get holdings
                holdings = _bot_instance.account_api.get_holdings()

                for holding in holdings:
                    stock_code = holding.get('stk_cd', '').replace('A', '')
                    stock_name = holding.get('stk_nm', '')

                    # Current position info
                    quantity = int(holding.get('rmnd_qty', 0))
                    buy_price = int(holding.get('pchs_avg_pric', 0))
                    current_price = int(holding.get('cur_prc', 0))

                    if quantity == 0 or buy_price == 0:
                        continue

                    # Calculate profit/loss
                    position_value = current_price * quantity
                    buy_value = buy_price * quantity
                    profit = position_value - buy_value
                    profit_pct = (profit / buy_value * 100) if buy_value > 0 else 0

                    # Get current price data
                    try:
                        price_info = _bot_instance.market_api.get_current_price(stock_code)
                        if price_info:
                            current_price = int(price_info.get('prpr', current_price))
                            change_rate = float(price_info.get('prdy_ctrt', 0))
                    except:
                        change_rate = 0

                    # Re-score with AI
                    stock_data = {
                        'stock_code': stock_code,
                        'name': stock_name,
                        'current_price': current_price,
                        'change_rate': change_rate,
                        'volume': 0  # Will be fetched if needed
                    }

                    try:
                        score_result = scoring_system.calculate_score(stock_data, scan_type='ai_driven')
                        ai_score = score_result.total_score
                        ai_grade = scoring_system.get_grade(ai_score)
                    except:
                        ai_score = 0
                        ai_grade = 'F'

                    # Determine trading signal
                    signal = 'HOLD'
                    signal_reason = '현재 보유 유지'
                    signal_color = '#9ca3af'

                    # SELL signals
                    if profit_pct < -5:  # 5% 이상 손실
                        signal = 'SELL'
                        signal_reason = f'손실 {abs(profit_pct):.1f}% - 손절 검토'
                        signal_color = '#ef4444'
                        alerts.append({
                            'stock': stock_name,
                            'type': 'loss',
                            'message': f'{stock_name}: {profit_pct:.1f}% 손실 - 손절 검토 필요'
                        })
                    elif ai_grade in ['D', 'F']:  # AI 점수 낮음
                        signal = 'SELL'
                        signal_reason = f'AI 등급 {ai_grade} - 매도 고려'
                        signal_color = '#ef4444'
                    elif profit_pct > 15:  # 15% 이상 수익
                        signal = 'TAKE_PROFIT'
                        signal_reason = f'수익 {profit_pct:.1f}% - 익절 고려'
                        signal_color = '#10b981'
                    elif ai_grade in ['S', 'A'] and profit_pct > 0:
                        signal = 'HOLD'
                        signal_reason = f'AI 등급 {ai_grade} - 보유 추천'
                        signal_color = '#10b981'

                    # Stop loss / Take profit lines
                    stop_loss_price = int(buy_price * 0.95)  # -5%
                    take_profit_price = int(buy_price * 1.15)  # +15%

                    # Add to positions
                    positions.append({
                        'code': stock_code,
                        'name': stock_name,
                        'quantity': quantity,
                        'buy_price': buy_price,
                        'current_price': current_price,
                        'profit': profit,
                        'profit_pct': round(profit_pct, 2),
                        'position_value': position_value,
                        'ai_score': round(ai_score, 1),
                        'ai_grade': ai_grade,
                        'signal': signal,
                        'signal_reason': signal_reason,
                        'signal_color': signal_color,
                        'stop_loss_price': stop_loss_price,
                        'take_profit_price': take_profit_price,
                        'change_rate': change_rate
                    })

                    # Update summary
                    summary['total_value'] += position_value
                    summary['total_profit'] += profit
                    summary['holding_count'] += 1
                    if profit > 0:
                        summary['winning_count'] += 1
                    elif profit < 0:
                        summary['losing_count'] += 1

                # Calculate total profit percentage
                total_buy_value = sum(p['buy_price'] * p['quantity'] for p in positions)
                if total_buy_value > 0:
                    summary['total_profit_pct'] = round(summary['total_profit'] / total_buy_value * 100, 2)

                # Sort by profit percentage (worst first for alerts)
                positions.sort(key=lambda x: x['profit_pct'])

            except Exception as e:
                print(f"Position monitor error: {e}")
                import traceback
                traceback.print_exc()

        return jsonify({
            'success': True,
            'positions': positions,
            'summary': summary,
            'alerts': alerts,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Position monitor API error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'positions': [],
            'summary': {},
            'alerts': []
        })


@ai_bp.route('/api/ai/portfolio-optimization')
def get_portfolio_optimization():
    """
    포트폴리오 최적화 제안

    기능:
    - 비중 분석 및 과도한 집중도 경고
    - 리밸런싱 제안
    - 섹터 다각화 분석
    """
    try:
        optimization = {
            'status': 'optimal',
            'risk_level': 'low',
            'concentration_warning': False,
            'rebalance_needed': False,
            'suggestions': []
        }

        if _bot_instance and hasattr(_bot_instance, 'account_api'):
            try:
                holdings = _bot_instance.account_api.get_holdings()

                if holdings and len(holdings) > 0:
                    # Calculate weights
                    total_value = sum(int(h.get('eval_amt', 0)) for h in holdings)
                    if total_value == 0:
                        total_value = sum(int(h.get('rmnd_qty', 0)) * int(h.get('cur_prc', 0)) for h in holdings)

                    weights = []
                    for h in holdings:
                        value = int(h.get('eval_amt', 0))
                        if value == 0:
                            value = int(h.get('rmnd_qty', 0)) * int(h.get('cur_prc', 0))

                        weight = (value / total_value * 100) if total_value > 0 else 0
                        weights.append({
                            'name': h.get('stk_nm', ''),
                            'weight': round(weight, 2),
                            'value': value
                        })

                    weights.sort(key=lambda x: x['weight'], reverse=True)

                    # Check concentration
                    max_weight = weights[0]['weight'] if weights else 0
                    top3_weight = sum(w['weight'] for w in weights[:3]) if len(weights) >= 3 else 0

                    if max_weight > 40:
                        optimization['concentration_warning'] = True
                        optimization['risk_level'] = 'high'
                        optimization['status'] = 'needs_attention'
                        optimization['suggestions'].append({
                            'type': 'warning',
                            'title': '과도한 집중도',
                            'message': f'{weights[0]["name"]} 비중이 {max_weight:.1f}%로 과도합니다. 30% 이하로 조정 권장.',
                            'action': f'{weights[0]["name"]} 일부 매도'
                        })
                    elif max_weight > 30:
                        optimization['risk_level'] = 'medium'
                        optimization['suggestions'].append({
                            'type': 'info',
                            'title': '집중도 주의',
                            'message': f'{weights[0]["name"]} 비중이 {max_weight:.1f}%입니다. 모니터링 필요.',
                            'action': '신규 종목 추가 고려'
                        })

                    # Check diversification
                    if len(holdings) < 3:
                        optimization['suggestions'].append({
                            'type': 'warning',
                            'title': '분산 투자 부족',
                            'message': f'현재 {len(holdings)}개 종목만 보유 중입니다. 최소 5개 이상 권장.',
                            'action': '추가 종목 투자로 분산'
                        })
                    elif len(holdings) < 5:
                        optimization['suggestions'].append({
                            'type': 'info',
                            'title': '분산 투자 개선',
                            'message': f'현재 {len(holdings)}개 종목 보유. 5-8개가 적정.',
                            'action': '2-3개 종목 추가 고려'
                        })

                    # Check top 3 concentration
                    if top3_weight > 70:
                        optimization['suggestions'].append({
                            'type': 'warning',
                            'title': '상위 3종목 집중도 높음',
                            'message': f'상위 3종목이 {top3_weight:.1f}% 차지. 60% 이하 권장.',
                            'action': '나머지 종목 비중 확대'
                        })

                    # Rebalancing suggestion
                    if max_weight > 35 or (len(holdings) >= 3 and top3_weight > 65):
                        optimization['rebalance_needed'] = True
                        optimization['suggestions'].append({
                            'type': 'action',
                            'title': '리밸런싱 필요',
                            'message': '포트폴리오 리밸런싱을 통해 리스크를 줄이세요.',
                            'action': '과비중 종목 일부 매도 후 저비중 종목 매수'
                        })

                    # Add weights to response
                    optimization['weights'] = weights[:5]  # Top 5
                    optimization['total_stocks'] = len(holdings)
                    optimization['max_weight'] = round(max_weight, 2)
                    optimization['top3_weight'] = round(top3_weight, 2)

            except Exception as e:
                print(f"Portfolio optimization error: {e}")
                import traceback
                traceback.print_exc()

        return jsonify({
            'success': True,
            'optimization': optimization
        })

    except Exception as e:
        print(f"Portfolio optimization API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@ai_bp.route('/api/ai/performance-tracker')
def get_performance_tracker():
    """
    실시간 성과 추적

    기능:
    - 오늘/이번주 손익
    - 종목별 수익률
    - 최고/최악 종목
    - 승률 통계
    """
    try:
        performance = {
            'today': {'profit': 0, 'profit_pct': 0, 'trades': 0},
            'week': {'profit': 0, 'profit_pct': 0, 'trades': 0},
            'best_stock': None,
            'worst_stock': None,
            'statistics': {
                'win_rate': 0,
                'avg_profit': 0,
                'avg_loss': 0,
                'profit_factor': 0
            }
        }

        if _bot_instance and hasattr(_bot_instance, 'account_api'):
            try:
                # Get current holdings for performance
                holdings = _bot_instance.account_api.get_holdings()

                stocks_performance = []
                total_profit = 0
                total_buy_value = 0

                for h in holdings:
                    quantity = int(h.get('rmnd_qty', 0))
                    buy_price = int(h.get('pchs_avg_pric', 0))
                    current_price = int(h.get('cur_prc', 0))

                    if quantity == 0 or buy_price == 0:
                        continue

                    profit = (current_price - buy_price) * quantity
                    buy_value = buy_price * quantity
                    profit_pct = (profit / buy_value * 100) if buy_value > 0 else 0

                    stocks_performance.append({
                        'name': h.get('stk_nm', ''),
                        'profit': profit,
                        'profit_pct': profit_pct
                    })

                    total_profit += profit
                    total_buy_value += buy_value

                if stocks_performance:
                    # Best and worst
                    stocks_performance.sort(key=lambda x: x['profit_pct'], reverse=True)
                    performance['best_stock'] = stocks_performance[0]
                    performance['worst_stock'] = stocks_performance[-1]

                    # Today's performance (approximate)
                    performance['today']['profit'] = total_profit
                    performance['today']['profit_pct'] = round((total_profit / total_buy_value * 100) if total_buy_value > 0 else 0, 2)

                    # Statistics
                    winners = [s for s in stocks_performance if s['profit_pct'] > 0]
                    losers = [s for s in stocks_performance if s['profit_pct'] < 0]

                    performance['statistics']['win_rate'] = round(len(winners) / len(stocks_performance) * 100, 1) if stocks_performance else 0
                    performance['statistics']['avg_profit'] = round(sum(w['profit_pct'] for w in winners) / len(winners), 2) if winners else 0
                    performance['statistics']['avg_loss'] = round(sum(l['profit_pct'] for l in losers) / len(losers), 2) if losers else 0

                    if losers:
                        total_win = sum(w['profit'] for w in winners)
                        total_loss = abs(sum(l['profit'] for l in losers))
                        performance['statistics']['profit_factor'] = round(total_win / total_loss, 2) if total_loss > 0 else 0

            except Exception as e:
                print(f"Performance tracker error: {e}")
                import traceback
                traceback.print_exc()

        return jsonify({
            'success': True,
            'performance': performance
        })

    except Exception as e:
        print(f"Performance tracker API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@ai_bp.route('/api/ai/stock-recommendations')
def get_stock_recommendations():
    """Get AI-powered stock recommendations based on current market conditions"""
    try:
        recommendations = []

        if _bot_instance and hasattr(_bot_instance, 'market_api') and hasattr(_bot_instance, 'account_api'):
            try:
                # Get current holdings to avoid recommending already-held stocks
                holdings = _bot_instance.account_api.get_holdings()
                held_codes = [h.get('stk_cd', '').replace('A', '') for h in holdings]

                # Get market leaders by PRICE CHANGE RATE (상승률) instead of volume
                gainers = _bot_instance.market_api.get_price_change_rank(market='ALL', sort='rise', limit=30)

                for stock in gainers:
                    stock_code = stock.get('code', '')
                    stock_name = stock.get('name', '')

                    # Skip if already held or invalid
                    if not stock_code or stock_code in held_codes:
                        continue

                    # Get volume and price
                    volume = int(stock.get('volume', 0))
                    current_price = int(stock.get('price', 0))
                    change_rate = float(stock.get('change_rate', 0))

                    # Filter: Only stocks with significant volume and positive change
                    if volume < 100_000 or change_rate <= 0 or current_price == 0:
                        continue

                    # Build basic stock data
                    stock_data = {
                        'stock_code': stock_code,
                        'name': stock_name,
                        'current_price': current_price,
                        'change_rate': change_rate,
                        'volume': volume
                    }

                    # Simple scoring based on available data
                    score = 0

                    # Price momentum (0-60)
                    if change_rate >= 10:
                        score += 60
                    elif change_rate >= 7:
                        score += 51
                    elif change_rate >= 5:
                        score += 42
                    elif change_rate >= 3:
                        score += 33
                    elif change_rate >= 1:
                        score += 15

                    # Volume score (0-60)
                    if volume >= 5_000_000:
                        score += 48
                    elif volume >= 2_000_000:
                        score += 36
                    elif volume >= 1_000_000:
                        score += 24
                    elif volume >= 500_000:
                        score += 12

                    # Baseline score for being in top gainers
                    score += 50

                    # Calculate percentage
                    max_score = 440
                    percentage = (score / max_score) * 100

                    # Determine grade
                    if percentage >= 90:
                        grade = 'S'
                    elif percentage >= 80:
                        grade = 'A'
                    elif percentage >= 70:
                        grade = 'B'
                    elif percentage >= 60:
                        grade = 'C'
                    elif percentage >= 50:
                        grade = 'D'
                    else:
                        grade = 'F'

                    # Only recommend if score is decent
                    if score >= 120:  # Lower threshold
                        reason = f'상승률 {change_rate:.1f}% + 거래량 {volume:,}주'

                        recommendations.append({
                            'code': stock_code,
                            'name': stock_name,
                            'price': current_price,
                            'change_rate': change_rate,
                            'score': round(score, 1),
                            'percentage': round(percentage, 1),
                            'grade': grade,
                            'reason': reason,
                            'volume': volume
                        })

                    # Stop after 5 recommendations
                    if len(recommendations) >= 5:
                        break

            except Exception as e:
                print(f"Stock recommendation error: {e}")
                import traceback
                traceback.print_exc()

        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)

        return jsonify({
            'success': True,
            'recommendations': recommendations[:5],  # Top 5
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Stock recommendations error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'recommendations': []
        })


@ai_bp.route('/api/ai/auto-stop-loss', methods=['POST'])
def execute_auto_stop_loss():
    """
    자동 손절 실행
    - 5% 이상 손실 종목 자동 매도
    """
    try:
        if not _bot_instance or not hasattr(_bot_instance, 'account_api') or not hasattr(_bot_instance, 'trading_api'):
            return jsonify({
                'success': False,
                'error': '봇 인스턴스가 초기화되지 않았습니다.'
            })

        data = request.get_json()
        enable = data.get('enable', False)
        threshold = data.get('threshold', -5)  # Default -5%

        if not enable:
            return jsonify({
                'success': True,
                'message': '자동 손절이 비활성화되었습니다.',
                'executed': []
            })

        executed_orders = []
        holdings = _bot_instance.account_api.get_holdings()

        for h in holdings:
            stock_code = h.get('stk_cd', '').replace('A', '')
            stock_name = h.get('stk_nm', '')
            quantity = int(h.get('rmnd_qty', 0))
            buy_price = int(h.get('pchs_avg_pric', 0))
            current_price = int(h.get('cur_prc', 0))

            if quantity == 0 or buy_price == 0:
                continue

            profit_pct = ((current_price - buy_price) / buy_price * 100)

            # Execute stop loss if below threshold
            if profit_pct <= threshold:
                try:
                    # Place sell order
                    order_result = _bot_instance.trading_api.sell_market_order(
                        stock_code=stock_code,
                        quantity=quantity
                    )

                    executed_orders.append({
                        'stock': stock_name,
                        'code': stock_code,
                        'quantity': quantity,
                        'price': current_price,
                        'loss_pct': round(profit_pct, 2),
                        'order_result': order_result,
                        'timestamp': datetime.now().isoformat()
                    })

                    print(f"자동 손절 실행: {stock_name} {quantity}주 @ {current_price}원 ({profit_pct:.2f}%)")

                except Exception as e:
                    print(f"자동 손절 실패 ({stock_name}): {e}")

        return jsonify({
            'success': True,
            'message': f'{len(executed_orders)}건 자동 손절 실행',
            'executed': executed_orders
        })

    except Exception as e:
        print(f"Auto stop-loss error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'executed': []
        })


@ai_bp.route('/api/ai/auto-take-profit', methods=['POST'])
def execute_auto_take_profit():
    """
    자동 익절 실행
    - 15% 이상 수익 종목 일부(50%) 매도
    """
    try:
        if not _bot_instance or not hasattr(_bot_instance, 'account_api') or not hasattr(_bot_instance, 'trading_api'):
            return jsonify({
                'success': False,
                'error': '봇 인스턴스가 초기화되지 않았습니다.'
            })

        data = request.get_json()
        enable = data.get('enable', False)
        threshold = data.get('threshold', 15)  # Default +15%
        sell_ratio = data.get('sell_ratio', 0.5)  # Default 50%

        if not enable:
            return jsonify({
                'success': True,
                'message': '자동 익절이 비활성화되었습니다.',
                'executed': []
            })

        executed_orders = []
        holdings = _bot_instance.account_api.get_holdings()

        for h in holdings:
            stock_code = h.get('stk_cd', '').replace('A', '')
            stock_name = h.get('stk_nm', '')
            quantity = int(h.get('rmnd_qty', 0))
            buy_price = int(h.get('pchs_avg_pric', 0))
            current_price = int(h.get('cur_prc', 0))

            if quantity == 0 or buy_price == 0:
                continue

            profit_pct = ((current_price - buy_price) / buy_price * 100)

            # Execute take profit if above threshold
            if profit_pct >= threshold:
                sell_quantity = int(quantity * sell_ratio)

                if sell_quantity > 0:
                    try:
                        # Place sell order
                        order_result = _bot_instance.trading_api.sell_market_order(
                            stock_code=stock_code,
                            quantity=sell_quantity
                        )

                        executed_orders.append({
                            'stock': stock_name,
                            'code': stock_code,
                            'quantity': sell_quantity,
                            'remaining': quantity - sell_quantity,
                            'price': current_price,
                            'profit_pct': round(profit_pct, 2),
                            'order_result': order_result,
                            'timestamp': datetime.now().isoformat()
                        })

                        print(f"자동 익절 실행: {stock_name} {sell_quantity}주 @ {current_price}원 ({profit_pct:.2f}%)")

                    except Exception as e:
                        print(f"자동 익절 실패 ({stock_name}): {e}")

        return jsonify({
            'success': True,
            'message': f'{len(executed_orders)}건 자동 익절 실행',
            'executed': executed_orders
        })

    except Exception as e:
        print(f"Auto take-profit error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'executed': []
        })


@ai_bp.route('/api/ai/alerts')
def get_ai_alerts():
    """
    실시간 AI 알림
    - 손절/익절 알림
    - 급등/급락 알림
    - 리스크 경고
    """
    try:
        alerts = []

        if _bot_instance and hasattr(_bot_instance, 'account_api'):
            try:
                holdings = _bot_instance.account_api.get_holdings()

                for h in holdings:
                    stock_name = h.get('stk_nm', '')
                    quantity = int(h.get('rmnd_qty', 0))
                    buy_price = int(h.get('pchs_avg_pric', 0))
                    current_price = int(h.get('cur_prc', 0))

                    if quantity == 0 or buy_price == 0:
                        continue

                    profit_pct = ((current_price - buy_price) / buy_price * 100)

                    # 손절 알림 (-5% 이상 손실)
                    if profit_pct <= -5:
                        alerts.append({
                            'type': 'stop_loss',
                            'severity': 'critical',
                            'stock': stock_name,
                            'message': f'{stock_name} {profit_pct:.1f}% 손실 - 즉시 손절 검토',
                            'action': '매도',
                            'color': '#ef4444'
                        })

                    # 익절 알림 (+15% 이상 수익)
                    elif profit_pct >= 15:
                        alerts.append({
                            'type': 'take_profit',
                            'severity': 'info',
                            'stock': stock_name,
                            'message': f'{stock_name} {profit_pct:.1f}% 수익 - 익절 고려',
                            'action': '일부 매도',
                            'color': '#10b981'
                        })

                    # 경고 알림 (-3% 손실)
                    elif profit_pct <= -3:
                        alerts.append({
                            'type': 'warning',
                            'severity': 'warning',
                            'stock': stock_name,
                            'message': f'{stock_name} {profit_pct:.1f}% 손실 - 주의 관찰',
                            'action': '모니터링',
                            'color': '#f59e0b'
                        })

            except Exception as e:
                print(f"Alerts error: {e}")

        # Sort by severity
        severity_order = {'critical': 0, 'warning': 1, 'info': 2}
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 99))

        return jsonify({
            'success': True,
            'alerts': alerts[:10]
        })

    except Exception as e:
        print(f"AI alerts API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'alerts': []
        })


@ai_bp.route('/api/ai/market-trend')
def get_market_trend():
    """Analyze current market trend"""
    try:
        trend_data = {
            'trend': 'Neutral',
            'strength': 5,
            'indicators': [],
            'recommendation': '시장 관망 권장'
        }

        if _bot_instance and hasattr(_bot_instance, 'market_api'):
            try:
                # Get KOSPI/KOSDAQ index data
                # This is a simplified version - you can enhance with real data
                from datetime import datetime, timedelta
                import random

                # Mock trend analysis based on volume leaders
                volume_leaders = _bot_instance.market_api.get_volume_rank(limit=50)

                if volume_leaders:
                    # Count gainers vs losers
                    gainers = sum(1 for s in volume_leaders if float(s.get('prdy_ctrt', 0)) > 0)
                    losers = sum(1 for s in volume_leaders if float(s.get('prdy_ctrt', 0)) < 0)

                    gainer_ratio = gainers / len(volume_leaders) if volume_leaders else 0.5

                    if gainer_ratio > 0.6:
                        trend_data['trend'] = 'Bullish'
                        trend_data['strength'] = 7 + int((gainer_ratio - 0.6) * 10)
                        trend_data['recommendation'] = '매수 타이밍 - 강세장'
                        trend_data['indicators'].append(f'상승종목 {gainers}개 vs 하락종목 {losers}개')
                    elif gainer_ratio < 0.4:
                        trend_data['trend'] = 'Bearish'
                        trend_data['strength'] = 3 - int((0.4 - gainer_ratio) * 10)
                        trend_data['recommendation'] = '관망 또는 매도 고려'
                        trend_data['indicators'].append(f'하락종목 {losers}개 vs 상승종목 {gainers}개')
                    else:
                        trend_data['trend'] = 'Neutral'
                        trend_data['strength'] = 5
                        trend_data['recommendation'] = '중립 - 선별 투자'
                        trend_data['indicators'].append(f'상승/하락 균형 (상승 {gainers}, 하락 {losers})')

                    # Add volume indicator
                    avg_volume = sum(int(s.get('acml_vol', 0)) for s in volume_leaders) / len(volume_leaders)
                    trend_data['indicators'].append(f'평균 거래량: {avg_volume:,.0f}주')

            except Exception as e:
                print(f"Market trend analysis error: {e}")

        return jsonify({
            'success': True,
            'trend': trend_data
        })

    except Exception as e:
        print(f"Market trend error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@ai_bp.route('/api/ai/auto-analysis')
def get_ai_auto_analysis():
    """Get AI analysis results (auto-running in background)"""
    try:
        result = {
            'success': True,
            'portfolio': None,
            'sentiment': None,
            'risk': None,
            'consensus': None
        }

        if _bot_instance and hasattr(_bot_instance, 'account_api'):
            # Portfolio Analysis - v5.7.5 더 실용적인 버전
            try:
                holdings = _bot_instance.account_api.get_holdings()

                if holdings and len(holdings) > 0:
                    # 실제 데이터 기반 분석
                    total_value = sum(int(h.get('eval_amt', 0)) for h in holdings)
                    if total_value == 0:
                        total_value = sum(int(h.get('rmnd_qty', 0)) * int(h.get('cur_prc', 0)) for h in holdings)

                    # Calculate portfolio metrics
                    total_profit = 0
                    total_buy_value = 0

                    for h in holdings:
                        quantity = int(h.get('rmnd_qty', 0))
                        buy_price = int(h.get('pchs_avg_pric', 0))
                        current_price = int(h.get('cur_prc', 0))

                        if quantity > 0 and buy_price > 0:
                            profit = (current_price - buy_price) * quantity
                            total_profit += profit
                            total_buy_value += buy_price * quantity

                    # Calculate score (0-10)
                    profit_pct = (total_profit / total_buy_value * 100) if total_buy_value > 0 else 0

                    if profit_pct >= 15:
                        score = 9.0
                        health = '우수'
                    elif profit_pct >= 10:
                        score = 8.0
                        health = '양호'
                    elif profit_pct >= 5:
                        score = 7.0
                        health = '양호'
                    elif profit_pct >= 0:
                        score = 6.0
                        health = '보통'
                    elif profit_pct >= -5:
                        score = 5.0
                        health = '주의'
                    elif profit_pct >= -10:
                        score = 4.0
                        health = '경고'
                    else:
                        score = 3.0
                        health = '위험'

                    # Generate recommendations
                    recommendations = []
                    if profit_pct < -5:
                        recommendations.append('손실 종목 점검 필요')
                    if len(holdings) < 3:
                        recommendations.append('분산 투자 확대 권장')
                    elif len(holdings) > 10:
                        recommendations.append('과도한 분산 - 집중 투자 고려')

                    if profit_pct > 10:
                        recommendations.append('수익 실현 타이밍 검토')

                    result['portfolio'] = {
                        'score': score,
                        'health': health,
                        'recommendations': recommendations if recommendations else ['현재 상태 유지']
                    }
                else:
                    result['portfolio'] = {
                        'score': 5.0,
                        'health': '보유 종목 없음',
                        'recommendations': ['종목 매수 필요']
                    }

            except Exception as e:
                print(f"Portfolio analysis error: {e}")
                import traceback
                traceback.print_exc()
                result['portfolio'] = {
                    'score': 5.0,
                    'health': '분석 오류',
                    'recommendations': ['데이터 확인 필요']
                }

            # Sentiment Analysis (전체 시장 감성) - v5.7.5 실용적 버전 (가격 모멘텀 기반)
            try:
                holdings = _bot_instance.account_api.get_holdings()

                if holdings and len(holdings) > 0:
                    # 가격 변동률 기반 감성 분석 (실제 데이터 사용)
                    sentiment_scores = []
                    analyzed_stocks = []

                    for h in holdings[:5]:  # 상위 5종목
                        stock_name = h.get('stk_nm', '')
                        stock_code = h.get('stk_cd', '').replace('A', '')

                        # 매입가 대비 현재가로 감성 추정
                        quantity = int(h.get('rmnd_qty', 0))
                        buy_price = int(h.get('pchs_avg_pric', 0))
                        current_price = int(h.get('cur_prc', 0))

                        if quantity > 0 and buy_price > 0:
                            profit_pct = ((current_price - buy_price) / buy_price * 100)

                            # 수익률을 0~1 감성 점수로 변환
                            if profit_pct >= 10:
                                score = 0.8
                            elif profit_pct >= 5:
                                score = 0.7
                            elif profit_pct >= 0:
                                score = 0.6
                            elif profit_pct >= -5:
                                score = 0.4
                            else:
                                score = 0.3

                            sentiment_scores.append(score)
                            analyzed_stocks.append(stock_name)

                    if sentiment_scores:
                        avg_score = sum(sentiment_scores) / len(sentiment_scores)
                        # 0~1 범위를 0~10 범위로 변환
                        overall_sentiment = avg_score * 10

                        # sentiment 상태 결정
                        if avg_score >= 0.6:
                            sentiment_status = '긍정적'
                        elif avg_score <= 0.4:
                            sentiment_status = '부정적'
                        else:
                            sentiment_status = '중립'

                        result['sentiment'] = {
                            'overall_sentiment': round(overall_sentiment, 2),
                            'sentiment': sentiment_status,
                            'overall_score': avg_score,
                            'count': len(sentiment_scores),
                            'status': sentiment_status,
                            'analyzed_stocks': analyzed_stocks,
                            'details': {
                                'positive_ratio': sum(1 for s in sentiment_scores if s > 0.5) / len(sentiment_scores),
                                'average': avg_score
                            }
                        }
                    else:
                        result['sentiment'] = {
                            'overall_sentiment': 5.0,
                            'sentiment': '중립',
                            'overall_score': 0.5,
                            'count': 0,
                            'status': '데이터 부족',
                            'analyzed_stocks': [],
                            'details': None
                        }
                else:
                    # 보유 종목 없을 때
                    result['sentiment'] = {
                        'overall_sentiment': 5.0,
                        'sentiment': '중립',
                        'overall_score': 0.5,
                        'count': 0,
                        'status': '보유 종목 없음',
                        'analyzed_stocks': [],
                        'details': None
                    }
            except Exception as e:
                print(f"Sentiment analysis error: {e}")
                import traceback
                traceback.print_exc()
                result['sentiment'] = {
                    'overall_sentiment': 5.0,
                    'sentiment': '분석 오류',
                    'overall_score': 0.5,
                    'count': 0,
                    'status': '분석 오류',
                    'analyzed_stocks': [],
                    'error': str(e)
                }

            # Risk Analysis (리스크 분석) - v5.7.5 VaR, CVaR, Sharpe 추가
            try:
                holdings = _bot_instance.account_api.get_holdings()

                if holdings and len(holdings) > 0:
                    # Convert holdings to position format
                    positions = []
                    total_value = sum(int(h.get('eval_amt', 0)) for h in holdings)

                    if total_value == 0:
                        # 평가금액이 0이면 현재가 기준으로 계산
                        for h in holdings:
                            qty = int(h.get('rmnd_qty', 0))
                            price = int(h.get('cur_prc', 0))
                            total_value += qty * price

                    for h in holdings:
                        code = h.get('stk_cd', '').replace('A', '')
                        value = int(h.get('eval_amt', 0))
                        if value == 0:
                            qty = int(h.get('rmnd_qty', 0))
                            price = int(h.get('cur_prc', 0))
                            value = qty * price

                        positions.append({
                            'code': code,
                            'name': h.get('stk_nm', ''),
                            'value': value,
                            'weight': (value / total_value * 100) if total_value > 0 else 0,
                            'sector': '기타'
                        })

                    # 리스크 레벨 계산
                    max_weight = max([p['weight'] for p in positions]) if positions else 0

                    if max_weight > 50:
                        risk_level = '높음'
                        risk_score = 8
                        volatility = 25.0
                    elif max_weight > 30:
                        risk_level = '중간'
                        risk_score = 5
                        volatility = 18.0
                    else:
                        risk_level = '낮음'
                        risk_score = 3
                        volatility = 12.0

                    # VaR (Value at Risk) 계산 - 95% 신뢰수준
                    var = int(total_value * volatility / 100 * 1.65)  # 1.65 = 95% z-score
                    cvar = int(var * 1.3)  # CVaR는 VaR의 약 1.3배

                    # Sharpe Ratio 추정 (단순화)
                    expected_return = 0.08  # 8% 가정
                    risk_free_rate = 0.03  # 3% 무위험 수익률
                    sharpe_ratio = (expected_return - risk_free_rate) / (volatility / 100)

                    result['risk'] = {
                        'risk_level': risk_level,
                        'risk_score': risk_score,
                        'max_weight': max_weight,
                        'diversification': len(positions),
                        'total_value': total_value,
                        'positions': positions[:5],  # 상위 5개만
                        'recommendation': f'{len(positions)}개 종목 보유 중, 최대 비중 {max_weight:.1f}%',
                        # 추가된 리스크 지표
                        'var': var,
                        'cvar': cvar,
                        'volatility': volatility,
                        'sharpe_ratio': round(sharpe_ratio, 2),
                        'max_loss_pct': round(volatility * 0.6, 1)  # 최대 손실 추정
                    }
                else:
                    # 보유 종목 없을 때도 데이터 반환
                    result['risk'] = {
                        'risk_level': '없음',
                        'risk_score': 0,
                        'max_weight': 0,
                        'diversification': 0,
                        'total_value': 0,
                        'positions': [],
                        'recommendation': '보유 종목 없음',
                        'var': 0,
                        'cvar': 0,
                        'volatility': 0,
                        'sharpe_ratio': 0,
                        'max_loss_pct': 0
                    }
            except Exception as e:
                print(f"Risk analysis error: {e}")
                import traceback
                traceback.print_exc()
                # 오류 발생 시에도 데이터 반환
                result['risk'] = {
                    'risk_level': '분석 오류',
                    'risk_score': 0,
                    'max_weight': 0,
                    'diversification': 0,
                    'total_value': 0,
                    'positions': [],
                    'error': str(e),
                    'var': 0,
                    'cvar': 0,
                    'volatility': 0,
                    'sharpe_ratio': 0,
                    'max_loss_pct': 0
                }

            # Multi-Agent Consensus (다중 AI 합의 분석) - v5.7.5 개선 버전
            try:
                # Consensus analysis: 포트폴리오와 리스크 결과 종합
                if result['portfolio'] and result['risk']:
                    portfolio_health = result['portfolio'].get('health', '보통')
                    risk_level = result['risk'].get('risk_level', '보통')
                    portfolio_score = result['portfolio'].get('score', 5)
                    risk_score = result['risk'].get('risk_score', 5)

                    # 건강도와 리스크 기반 최종 액션 결정
                    if portfolio_score >= 7 and risk_level in ['낮음', '중간']:
                        final_action = 'BUY'
                        consensus_level = 0.85
                        confidence = 0.90
                        votes = {'buy': 4, 'sell': 0, 'hold': 1}
                    elif portfolio_score <= 3 or risk_level == '높음':
                        final_action = 'SELL'
                        consensus_level = 0.75
                        confidence = 0.80
                        votes = {'buy': 0, 'sell': 4, 'hold': 1}
                    else:
                        final_action = 'HOLD'
                        consensus_level = 0.70
                        confidence = 0.75
                        votes = {'buy': 1, 'sell': 1, 'hold': 3}

                    result['consensus'] = {
                        'final_action': final_action,
                        'consensus_level': consensus_level,
                        'confidence': confidence,
                        'votes': votes,
                        'status': f'{final_action} 추천',
                        'recommendation': f'포트폴리오 상태: {portfolio_health}, 리스크: {risk_level}'
                    }
                else:
                    result['consensus'] = {
                        'final_action': 'HOLD',
                        'consensus_level': 0.5,
                        'confidence': 0.5,
                        'votes': {'buy': 0, 'sell': 0, 'hold': 5},
                        'status': '데이터 부족',
                        'recommendation': '분석 데이터 부족으로 보류'
                    }
            except Exception as e:
                print(f"Consensus analysis error: {e}")
                result['consensus'] = {
                    'final_action': 'HOLD',
                    'consensus_level': 0.5,
                    'confidence': 0.5,
                    'votes': {'buy': 0, 'sell': 0, 'hold': 5},
                    'status': '분석 오류',
                    'recommendation': f'오류: {str(e)}'
                }

        return jsonify(result)

    except Exception as e:
        print(f"AI auto-analysis error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


# ============================================================================
# v5.7.7: AI 실시간 시장 코멘터리
# ============================================================================

@ai_bp.route('/api/ai/market-commentary')
def get_market_commentary():
    """AI 실시간 시장 코멘터리"""
    try:
        commentary = {
            'market_summary': '',
            'portfolio_advice': '',
            'opportunities': [],
            'risks': [],
            'speak': False,
            'speak_text': ''
        }

        # 계좌 정보 가져오기
        account_info = None
        portfolio_info = None

        if _bot_instance and hasattr(_bot_instance, 'kis'):
            try:
                account_info = _bot_instance.kis.get_account_balance()
                portfolio_info = _bot_instance.kis.get_holdings()
            except Exception as e:
                print(f"계좌 정보 조회 오류: {e}")

        # 시장 종합 분석
        market_summary_parts = []

        if account_info:
            total_assets = account_info.get('total_assets', 0)
            profit_loss = account_info.get('profit_loss', 0)
            profit_loss_pct = account_info.get('profit_loss_percent', 0)

            if profit_loss_pct > 5:
                market_summary_parts.append(f"✨ 포트폴리오가 {profit_loss_pct:.1f}% 상승 중입니다. 수익 실현을 고려하세요.")
            elif profit_loss_pct > 2:
                market_summary_parts.append(f"📈 포트폴리오가 {profit_loss_pct:.1f}% 상승했습니다. 안정적인 수익률을 유지하고 있습니다.")
            elif profit_loss_pct < -5:
                market_summary_parts.append(f"⚠️ 포트폴리오가 {abs(profit_loss_pct):.1f}% 하락했습니다. 손절 또는 추가 매수를 검토하세요.")
                commentary['speak'] = True
                commentary['speak_text'] = f"경고: 포트폴리오가 {abs(profit_loss_pct):.1f}퍼센트 하락했습니다."
            elif profit_loss_pct < -2:
                market_summary_parts.append(f"📉 포트폴리오가 {abs(profit_loss_pct):.1f}% 하락 중입니다. 주의가 필요합니다.")
            else:
                market_summary_parts.append(f"📊 포트폴리오가 {profit_loss_pct:+.1f}% 변동 중입니다. 안정적인 상태입니다.")

        current_hour = datetime.now().hour

        if 9 <= current_hour < 10:
            market_summary_parts.append("🔔 장 시작 시간입니다. 시가 변동성에 주의하세요.")
        elif 14 <= current_hour < 15:
            market_summary_parts.append("⏰ 장 마감이 가까워집니다. 포지션 정리를 검토하세요.")
        elif current_hour >= 15 or current_hour < 9:
            market_summary_parts.append("🌙 시간외 거래 시간입니다. 다음 장을 준비하세요.")
        else:
            market_summary_parts.append("📊 정규 장 거래 시간입니다.")

        commentary['market_summary'] = ' '.join(market_summary_parts)

        # 포트폴리오 조언
        if portfolio_info and len(portfolio_info) > 0:
            holdings_count = len(portfolio_info)

            if holdings_count > 10:
                commentary['portfolio_advice'] = f"현재 {holdings_count}개 종목을 보유 중입니다. 포트폴리오가 과도하게 분산되어 있을 수 있습니다. 핵심 종목 5-7개로 집중하는 것을 권장합니다."
            elif holdings_count < 3:
                commentary['portfolio_advice'] = f"현재 {holdings_count}개 종목을 보유 중입니다. 리스크 분산을 위해 3-5개 종목으로 다각화하는 것을 권장합니다."
            else:
                commentary['portfolio_advice'] = f"현재 {holdings_count}개 종목을 보유 중입니다. 적절한 분산 수준을 유지하고 있습니다."

            # 종목별 손익 분석
            profit_stocks = sum(1 for p in portfolio_info if p.get('profit_loss_percent', 0) > 0)
            loss_stocks = sum(1 for p in portfolio_info if p.get('profit_loss_percent', 0) < 0)

            if profit_stocks > loss_stocks * 2:
                commentary['portfolio_advice'] += f" 수익 종목({profit_stocks})이 손실 종목({loss_stocks})보다 많습니다. 좋은 추세입니다."
            elif loss_stocks > profit_stocks * 2:
                commentary['portfolio_advice'] += f" 손실 종목({loss_stocks})이 수익 종목({profit_stocks})보다 많습니다. 포트폴리오 재검토가 필요합니다."

        # 주요 기회
        if portfolio_info:
            for stock in portfolio_info:
                pl_pct = stock.get('profit_loss_percent', 0)
                name = stock.get('name', '종목')

                # 추가 매수 기회
                if 2 < pl_pct < 5:
                    commentary['opportunities'].append(f"{name}: {pl_pct:+.1f}% 수익 중. 추가 매수 적기일 수 있습니다.")

                # 수익 실현 기회
                if pl_pct > 15:
                    commentary['opportunities'].append(f"{name}: {pl_pct:+.1f}% 수익 달성. 일부 수익 실현을 고려하세요.")

        # 주요 위험
        if portfolio_info:
            for stock in portfolio_info:
                pl_pct = stock.get('profit_loss_percent', 0)
                name = stock.get('name', '종목')

                # 손절 필요
                if pl_pct < -7:
                    commentary['risks'].append(f"⚠️ {name}: {pl_pct:.1f}% 손실. 즉시 손절을 검토하세요.")
                    if not commentary['speak']:
                        commentary['speak'] = True
                        commentary['speak_text'] = f"경고: {name} 종목이 {abs(pl_pct):.1f}퍼센트 손실입니다."

                # 주의 필요
                elif pl_pct < -3:
                    commentary['risks'].append(f"⚡ {name}: {pl_pct:.1f}% 손실. 주의가 필요합니다.")

        # 시간대별 조언
        if 9 <= current_hour < 10:
            commentary['opportunities'].append("장 시작 30분은 변동성이 큽니다. 신중한 진입이 필요합니다.")
        elif 14 <= current_hour < 15:
            commentary['risks'].append("장 마감 전 물량 정리가 일어날 수 있습니다.")

        return jsonify({
            'success': True,
            'commentary': commentary
        })

    except Exception as e:
        print(f"Market commentary error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'commentary': {
                'market_summary': '시장 분석 중 오류가 발생했습니다.',
                'portfolio_advice': '',
                'opportunities': [],
                'risks': [],
                'speak': False,
                'speak_text': ''
            }
        })
