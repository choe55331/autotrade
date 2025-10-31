"""
Advanced Trading Dashboard
Professional-grade dashboard with TradingView/Bloomberg-style features
"""

import logging
from flask import Flask, render_template, jsonify, request, send_from_directory
from pathlib import Path
import json
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)


def create_advanced_app(bot_instance=None):
    """
    Create advanced Flask app with professional features

    Args:
        bot_instance: Trading bot instance

    Returns:
        Flask app
    """
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    app.config['bot'] = bot_instance

    # ==================== Routes ====================

    @app.route('/')
    def index():
        """Advanced dashboard main page"""
        return render_template('advanced_dashboard.html')

    @app.route('/api/status')
    def api_status():
        """Enhanced bot status API"""
        bot = app.config.get('bot')

        if bot is None:
            return jsonify({
                'is_running': False,
                'error': 'Bot instance not available'
            })

        try:
            status = {
                'is_running': getattr(bot, 'is_running', False),
                'account': _get_account_info(bot),
                'positions': _get_positions(bot),
                'holdings': _get_holdings(bot),
                'max_positions': _get_max_positions(bot),
                'stats': _get_statistics(bot),
                'risk_metrics': _get_risk_metrics(bot),
                'timestamp': datetime.now().isoformat()
            }

            return jsonify(status)

        except Exception as e:
            logger.error(f"Status error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/ai-insights')
    def api_ai_insights():
        """AI model insights and predictions"""
        bot = app.config.get('bot')

        if bot is None or not hasattr(bot, 'ai_analyzer'):
            return jsonify({
                'available': False,
                'message': 'AI analyzer not available'
            })

        try:
            insights = {
                'market_sentiment': _get_market_sentiment(bot),
                'top_predictions': _get_top_predictions(bot),
                'model_performance': _get_model_performance(bot),
                'signals_today': _get_signals_today(bot),
                'timestamp': datetime.now().isoformat()
            }

            return jsonify(insights)

        except Exception as e:
            logger.error(f"AI insights error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/performance')
    def api_performance():
        """Performance analytics"""
        bot = app.config.get('bot')

        if bot is None:
            return jsonify({'error': 'Bot not available'}), 400

        try:
            performance = {
                'daily_returns': _calculate_daily_returns(bot),
                'cumulative_returns': _calculate_cumulative_returns(bot),
                'sharpe_ratio': _calculate_sharpe_ratio(bot),
                'sortino_ratio': _calculate_sortino_ratio(bot),
                'max_drawdown': _calculate_max_drawdown(bot),
                'win_rate': _calculate_win_rate(bot),
                'profit_factor': _calculate_profit_factor(bot),
                'benchmark_comparison': _get_benchmark_comparison(bot),
                'timestamp': datetime.now().isoformat()
            }

            return jsonify(performance)

        except Exception as e:
            logger.error(f"Performance error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/chart-data/<stock_code>')
    def api_chart_data(stock_code):
        """Get chart data for a stock"""
        bot = app.config.get('bot')
        period = request.args.get('period', '1D')  # 1D, 5D, 1M, 3M, 1Y

        if bot is None or not hasattr(bot, 'account_api'):
            return jsonify({'error': 'Bot not available'}), 400

        try:
            # Get historical data
            chart_data = bot.account_api.get_chart_data(stock_code, period=period)

            # Add technical indicators
            if chart_data and len(chart_data) > 0:
                chart_data = _add_technical_indicators(chart_data)

            return jsonify({
                'stock_code': stock_code,
                'period': period,
                'data': chart_data,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Chart data error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/heatmap')
    def api_heatmap():
        """Market heatmap data"""
        bot = app.config.get('bot')

        if bot is None:
            return jsonify({'error': 'Bot not available'}), 400

        try:
            # Get top stocks by volume or market cap
            heatmap_data = _generate_heatmap_data(bot)

            return jsonify({
                'data': heatmap_data,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Heatmap error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/correlation-matrix')
    def api_correlation_matrix():
        """Correlation matrix for portfolio"""
        bot = app.config.get('bot')

        if bot is None:
            return jsonify({'error': 'Bot not available'}), 400

        try:
            correlation_data = _calculate_correlation_matrix(bot)

            return jsonify({
                'matrix': correlation_data,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Correlation error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/backtest')
    def api_backtest():
        """Backtesting results"""
        bot = app.config.get('bot')

        if bot is None:
            return jsonify({'error': 'Bot not available'}), 400

        try:
            # Get backtest results if available
            backtest_results = _get_backtest_results(bot)

            return jsonify({
                'results': backtest_results,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Backtest error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/control', methods=['POST'])
    def api_control():
        """Enhanced bot control API"""
        bot = app.config.get('bot')

        if bot is None:
            return jsonify({'error': 'Bot not available'}), 400

        data = request.json
        action = data.get('action')

        try:
            if action == 'start':
                bot.start()
                return jsonify({'success': True, 'message': 'Bot started'})

            elif action == 'stop':
                bot.stop()
                return jsonify({'success': True, 'message': 'Bot stopped'})

            elif action == 'pause_buy':
                bot.pause_buy = True
                return jsonify({'success': True, 'message': 'Buy paused'})

            elif action == 'resume_buy':
                bot.pause_buy = False
                return jsonify({'success': True, 'message': 'Buy resumed'})

            elif action == 'emergency_stop':
                bot.stop()
                # Close all positions
                if hasattr(bot, 'strategy'):
                    bot.strategy.close_all_positions()
                return jsonify({'success': True, 'message': 'Emergency stop executed'})

            else:
                return jsonify({'error': 'Unknown action'}), 400

        except Exception as e:
            logger.error(f"Control error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/orders/history')
    def api_order_history():
        """Get order history"""
        bot = app.config.get('bot')
        limit = int(request.args.get('limit', 50))

        if bot is None or not hasattr(bot, 'account_api'):
            return jsonify({'error': 'Bot not available'}), 400

        try:
            orders = bot.account_api.get_order_history()

            # Sort by timestamp and limit
            if orders:
                orders = sorted(orders, key=lambda x: x.get('timestamp', ''), reverse=True)
                orders = orders[:limit]

            return jsonify({
                'orders': orders,
                'total': len(orders),
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Order history error: {e}")
            return jsonify({'error': str(e)}), 500

    # ==================== Helper Functions ====================

    def _get_account_info(bot):
        """Get account information"""
        if hasattr(bot, 'portfolio_manager'):
            return bot.portfolio_manager.get_portfolio_summary()
        return {}

    def _get_positions(bot):
        """Get current positions"""
        if hasattr(bot, 'strategy'):
            return list(bot.strategy.get_all_positions().values())
        return []

    def _get_holdings(bot):
        """Get detailed holdings"""
        if hasattr(bot, 'portfolio_manager'):
            return bot.portfolio_manager.get_position_details()
        return []

    def _get_max_positions(bot):
        """Get maximum positions"""
        if hasattr(bot, 'strategy'):
            return bot.strategy.get_config('max_positions', 5)
        return 5

    def _get_statistics(bot):
        """Get trading statistics"""
        if hasattr(bot, 'strategy'):
            return bot.strategy.get_statistics()
        return {}

    def _get_risk_metrics(bot):
        """Get risk management metrics"""
        if hasattr(bot, 'risk_manager'):
            return {
                'risk_level': bot.risk_manager.get_risk_level(),
                'daily_loss': bot.risk_manager.daily_loss,
                'max_daily_loss': bot.risk_manager.max_daily_loss,
                'trading_enabled': bot.risk_manager.can_trade(),
                'risk_factors': bot.risk_manager.get_risk_factors()
            }
        return {}

    def _get_market_sentiment(bot):
        """Get market sentiment from AI"""
        if hasattr(bot, 'ai_analyzer'):
            market_data = {}  # Would get from market API
            return bot.ai_analyzer.analyze_market(market_data)
        return {'sentiment': 'Neutral', 'score': 5}

    def _get_top_predictions(bot):
        """Get top AI predictions"""
        # Would get from AI prediction history
        return []

    def _get_model_performance(bot):
        """Get AI model performance"""
        if hasattr(bot, 'ai_analyzer') and hasattr(bot.ai_analyzer, 'get_model_rankings'):
            return bot.ai_analyzer.get_model_rankings()
        return []

    def _get_signals_today(bot):
        """Get today's trading signals"""
        # Would get from signal history
        return []

    def _calculate_daily_returns(bot):
        """Calculate daily returns"""
        if hasattr(bot, 'portfolio_manager'):
            history = bot.portfolio_manager.portfolio_history
            if len(history) < 2:
                return []

            returns = []
            for i in range(1, len(history)):
                prev_value = history[i-1].get('total_value', 0)
                curr_value = history[i].get('total_value', 0)
                if prev_value > 0:
                    ret = ((curr_value - prev_value) / prev_value) * 100
                    returns.append({
                        'date': history[i].get('timestamp', ''),
                        'return': round(ret, 2)
                    })
            return returns
        return []

    def _calculate_cumulative_returns(bot):
        """Calculate cumulative returns"""
        daily_returns = _calculate_daily_returns(bot)
        if not daily_returns:
            return []

        cumulative = []
        cum_return = 0
        for day in daily_returns:
            cum_return += day['return']
            cumulative.append({
                'date': day['date'],
                'cumulative_return': round(cum_return, 2)
            })
        return cumulative

    def _calculate_sharpe_ratio(bot):
        """Calculate Sharpe ratio"""
        daily_returns = _calculate_daily_returns(bot)
        if len(daily_returns) < 2:
            return 0

        returns = [r['return'] for r in daily_returns]
        avg_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return 0

        # Assuming 252 trading days per year
        risk_free_rate = 0.03  # 3% annual
        daily_rf = risk_free_rate / 252

        sharpe = (avg_return - daily_rf) / std_return * np.sqrt(252)
        return round(sharpe, 2)

    def _calculate_sortino_ratio(bot):
        """Calculate Sortino ratio (downside risk)"""
        daily_returns = _calculate_daily_returns(bot)
        if len(daily_returns) < 2:
            return 0

        returns = [r['return'] for r in daily_returns]
        avg_return = np.mean(returns)

        # Only downside returns
        downside_returns = [r for r in returns if r < 0]
        if len(downside_returns) == 0:
            return 0

        downside_std = np.std(downside_returns)
        if downside_std == 0:
            return 0

        risk_free_rate = 0.03 / 252
        sortino = (avg_return - risk_free_rate) / downside_std * np.sqrt(252)
        return round(sortino, 2)

    def _calculate_max_drawdown(bot):
        """Calculate maximum drawdown"""
        cumulative = _calculate_cumulative_returns(bot)
        if not cumulative:
            return 0

        returns = [c['cumulative_return'] for c in cumulative]
        peak = returns[0]
        max_dd = 0

        for ret in returns:
            if ret > peak:
                peak = ret
            dd = peak - ret
            if dd > max_dd:
                max_dd = dd

        return round(max_dd, 2)

    def _calculate_win_rate(bot):
        """Calculate win rate"""
        if hasattr(bot, 'strategy'):
            stats = bot.strategy.get_statistics()
            total = stats.get('total_trades', 0)
            winning = stats.get('winning_trades', 0)
            return round((winning / total * 100), 2) if total > 0 else 0
        return 0

    def _calculate_profit_factor(bot):
        """Calculate profit factor"""
        if hasattr(bot, 'strategy'):
            # Would calculate from trade history
            return 0
        return 0

    def _get_benchmark_comparison(bot):
        """Compare with benchmark (KOSPI)"""
        # Would compare with KOSPI returns
        return {
            'alpha': 0,
            'beta': 1.0,
            'excess_return': 0
        }

    def _add_technical_indicators(chart_data):
        """Add technical indicators to chart data"""
        if not chart_data or len(chart_data) < 20:
            return chart_data

        # Calculate MA20
        closes = [c['close'] for c in chart_data]
        ma20 = []
        for i in range(len(closes)):
            if i < 19:
                ma20.append(None)
            else:
                ma20.append(sum(closes[i-19:i+1]) / 20)

        # Add to chart data
        for i, candle in enumerate(chart_data):
            candle['ma20'] = ma20[i]

        return chart_data

    def _generate_heatmap_data(bot):
        """Generate market heatmap data"""
        # Would get from market API
        return []

    def _calculate_correlation_matrix(bot):
        """Calculate portfolio correlation matrix"""
        # Would calculate from holdings price history
        return {}

    def _get_backtest_results(bot):
        """Get backtesting results"""
        # Would get from backtest engine
        return {}

    return app


def run_advanced_dashboard(bot_instance=None, host='0.0.0.0', port=5000, debug=False):
    """
    Run advanced dashboard

    Args:
        bot_instance: Trading bot instance
        host: Host address
        port: Port number
        debug: Debug mode
    """
    app = create_advanced_app(bot_instance)
    logger.info(f"Advanced Dashboard starting: http://{host}:{port}")

    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=False,
        threaded=True
    )


__all__ = ['run_advanced_dashboard', 'create_advanced_app']
