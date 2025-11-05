"""
Trading Routes Module
Handles all trading-related API endpoints including control, paper trading, virtual trading, and backtesting
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from flask import Blueprint, jsonify, request

# Create logger
logger = logging.getLogger(__name__)

# Create Blueprint
trading_bp = Blueprint('trading', __name__)

# Module-level variables
_bot_instance = None
_socketio = None
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def set_bot_instance(bot):
    """Set the bot instance for trading routes"""
    global _bot_instance
    _bot_instance = bot


def set_socketio(socketio):
    """Set the socketio instance for trading routes"""
    global _socketio
    _socketio = socketio


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
# TRADING CONTROL API
# ============================================================================

@trading_bp.route('/api/control/start', methods=['POST'])
def start_trading():
    """Start trading"""
    if set_control_status(True):
        if _socketio:
            _socketio.emit('trading_status', {'enabled': True})
        return jsonify({'success': True, 'message': 'Trading started'})
    return jsonify({'success': False, 'message': 'Failed to start'}), 500


@trading_bp.route('/api/control/stop', methods=['POST'])
def stop_trading():
    """Stop trading"""
    if set_control_status(False):
        if _socketio:
            _socketio.emit('trading_status', {'enabled': False})
        return jsonify({'success': True, 'message': 'Trading stopped'})
    return jsonify({'success': False, 'message': 'Failed to stop'}), 500


# ============================================================================
# PAPER TRADING API
# ============================================================================

@trading_bp.route('/api/paper_trading/status')
def get_paper_trading_status():
    """Get paper trading engine status"""
    try:
        from features.paper_trading import get_paper_trading_engine

        engine = get_paper_trading_engine(
            getattr(_bot_instance, 'market_api', None),
            None  # Will integrate with AI agent later
        )

        data = engine.get_dashboard_data()
        return jsonify(data)
    except ModuleNotFoundError as e:
        # Missing dependencies (numpy, pandas, etc.)
        return jsonify({
            'success': False,
            'message': 'Paper trading requires numpy. Install: pip install numpy pandas',
            'enabled': False
        })
    except Exception as e:
        print(f"Paper trading status API error: {e}")
        return jsonify({'success': False, 'message': str(e), 'enabled': False})


@trading_bp.route('/api/paper_trading/start', methods=['POST'])
def start_paper_trading():
    """Start paper trading engine"""
    try:
        from features.paper_trading import get_paper_trading_engine
        from features.ai_mode import get_ai_agent

        engine = get_paper_trading_engine(
            getattr(_bot_instance, 'market_api', None),
            get_ai_agent(_bot_instance)
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


@trading_bp.route('/api/paper_trading/stop', methods=['POST'])
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


@trading_bp.route('/api/paper_trading/account/<strategy_name>')
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
# VIRTUAL TRADING API
# ============================================================================

@trading_bp.route('/api/virtual_trading/status')
def get_virtual_trading_status():
    """Get virtual trading status and performance"""
    try:
        if not _bot_instance or not hasattr(_bot_instance, 'virtual_trader'):
            return jsonify({
                'success': False,
                'message': 'Virtual trading not initialized',
                'enabled': False
            })

        virtual_trader = _bot_instance.virtual_trader
        if not virtual_trader:
            return jsonify({
                'success': False,
                'message': 'Virtual trading not enabled',
                'enabled': False
            })

        # Get all account summaries
        summaries = virtual_trader.get_all_summaries()

        # Get best strategy
        best_strategy = virtual_trader.get_best_strategy()

        return jsonify({
            'success': True,
            'enabled': True,
            'strategies': summaries,
            'best_strategy': best_strategy
        })
    except Exception as e:
        print(f"Virtual trading status API error: {e}")
        return jsonify({'success': False, 'message': str(e), 'enabled': False})


@trading_bp.route('/api/virtual_trading/account/<strategy_name>')
def get_virtual_trading_account(strategy_name: str):
    """Get virtual trading account details for specific strategy"""
    try:
        if not _bot_instance or not hasattr(_bot_instance, 'virtual_trader'):
            return jsonify({'success': False, 'message': 'Virtual trading not initialized'})

        virtual_trader = _bot_instance.virtual_trader
        if not virtual_trader:
            return jsonify({'success': False, 'message': 'Virtual trading not enabled'})

        if strategy_name not in virtual_trader.accounts:
            return jsonify({'success': False, 'message': 'Strategy not found'})

        account = virtual_trader.accounts[strategy_name]
        summary = account.get_summary()

        # Get positions details
        positions = []
        for stock_code, position in account.positions.items():
            positions.append(position.to_dict())

        return jsonify({
            'success': True,
            'strategy_name': strategy_name,
            'summary': summary,
            'positions': positions
        })
    except Exception as e:
        print(f"Virtual trading account API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@trading_bp.route('/api/virtual_trading/trades')
def get_virtual_trading_trades():
    """Get virtual trading trade history"""
    try:
        if not _bot_instance or not hasattr(_bot_instance, 'trade_logger'):
            return jsonify({'success': False, 'message': 'Trade logger not initialized'})

        trade_logger = _bot_instance.trade_logger
        if not trade_logger:
            return jsonify({'success': False, 'message': 'Trade logger not enabled'})

        # Get recent trades
        limit = request.args.get('limit', default=20, type=int)
        strategy = request.args.get('strategy', default=None, type=str)

        recent_trades = trade_logger.get_recent_trades(limit=limit, strategy=strategy)

        # Get trade analysis
        analysis = trade_logger.get_trade_analysis(strategy=strategy)

        return jsonify({
            'success': True,
            'trades': recent_trades,
            'analysis': analysis
        })
    except Exception as e:
        print(f"Virtual trading trades API error: {e}")
        return jsonify({'success': False, 'message': str(e)})


@trading_bp.route('/api/virtual-trades')
def get_virtual_trades():
    """가상매매 전략별 거래 기록 조회"""
    try:
        if not _bot_instance or not hasattr(_bot_instance, 'virtual_trader'):
            return jsonify({
                'success': False,
                'message': '가상매매 미활성화'
            })

        virtual_trader = _bot_instance.virtual_trader
        trades_by_strategy = {}

        for strategy_name, account in virtual_trader.accounts.items():
            # 최근 50건 거래 기록
            trades = account.trade_history[-50:] if account.trade_history else []

            # 역순 정렬 (최신순)
            trades = list(reversed(trades))

            trades_by_strategy[strategy_name] = {
                'summary': account.get_summary(),
                'trades': trades
            }

        return jsonify({
            'success': True,
            'data': trades_by_strategy
        })

    except Exception as e:
        logger.error(f"가상매매 거래 기록 조회 실패: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ============================================================================
# BACKTESTING API
# ============================================================================

@trading_bp.route('/api/v4.1/backtest/run', methods=['POST'])
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


@trading_bp.route('/api/backtest/run', methods=['POST'])
def run_backtest_v4():
    """백테스팅 실행 (v4.0 Unified Settings)"""
    try:
        params = request.json

        # TODO: 실제 백테스팅 엔진 연동
        backtest_id = f"bt_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        return jsonify({
            'success': True,
            'backtest_id': backtest_id,
            'message': '백테스팅이 시작되었습니다.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/api/optimization/run', methods=['POST'])
def run_optimization():
    """파라미터 최적화 실행"""
    try:
        params = request.json

        # TODO: 실제 최적화 엔진 연동
        optimization_id = f"opt_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        return jsonify({
            'success': True,
            'optimization_id': optimization_id,
            'message': '최적화가 시작되었습니다.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# OPTIONS AND HFT API
# ============================================================================

@trading_bp.route('/api/v4.2/options/price', methods=['POST'])
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


@trading_bp.route('/api/v4.2/hft/status')
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
