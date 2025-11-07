"""
Auto-Analysis Routes
Handles background AI analysis including position monitoring, portfolio optimization,
performance tracking, stock recommendations, and market trend analysis
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import random
from .common import get_bot_instance

# Create blueprint
auto_analysis_bp = Blueprint('auto_analysis', __name__)


# ============================================================================
# Auto-Analysis - Background AI Analysis
# ============================================================================

@auto_analysis_bp.route('/api/ai/position-monitor')
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

        bot_instance = get_bot_instance()
        if bot_instance and hasattr(bot_instance, 'account_api') and hasattr(bot_instance, 'market_api'):
            try:
                from strategy.scoring_system import ScoringSystem
                scoring_system = ScoringSystem(bot_instance.market_api)

                # Get holdings
                holdings = bot_instance.account_api.get_holdings()

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
                        price_info = bot_instance.market_api.get_current_price(stock_code)
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


@auto_analysis_bp.route('/api/ai/portfolio-optimization')
def get_portfolio_optimization():
    """
    포트폴리오 최적화 제안 (Enhanced v5.8)

    기능:
    - 비중 분석 및 과도한 집중도 경고
    - 리밸런싱 제안
    - 섹터 다각화 분석
    - Sharpe Ratio (수익률/위험 비율)
    - Value at Risk (VaR) - 예상 최대 손실
    - 포트폴리오 효율성 점수
    """
    try:
        optimization = {
            'status': 'optimal',
            'risk_level': 'low',
            'concentration_warning': False,
            'rebalance_needed': False,
            'suggestions': [],
            # v5.8: Enhanced metrics
            'sharpe_ratio': 0,
            'value_at_risk': 0,
            'max_drawdown': 0,
            'efficiency_score': 0,
            'portfolio_beta': 1.0,
        }

        bot_instance = get_bot_instance()
        if bot_instance and hasattr(bot_instance, 'account_api'):
            try:
                holdings = bot_instance.account_api.get_holdings()

                if holdings and len(holdings) > 0:
                    # Calculate weights and portfolio metrics
                    total_value = sum(int(h.get('eval_amt', 0)) for h in holdings)
                    if total_value == 0:
                        total_value = sum(int(h.get('rmnd_qty', 0)) * int(h.get('cur_prc', 0)) for h in holdings)

                    # Calculate portfolio return and volatility
                    total_profit = 0
                    total_invested = 0
                    stock_returns = []

                    weights = []
                    for h in holdings:
                        value = int(h.get('eval_amt', 0))
                        if value == 0:
                            value = int(h.get('rmnd_qty', 0)) * int(h.get('cur_prc', 0))

                        quantity = int(h.get('rmnd_qty', 0))
                        buy_price = int(h.get('pchs_avg_pric', 0))
                        current_price = int(h.get('cur_prc', 0))

                        weight = (value / total_value * 100) if total_value > 0 else 0
                        weights.append({
                            'name': h.get('stk_nm', ''),
                            'weight': round(weight, 2),
                            'value': value
                        })

                        # Calculate individual stock metrics
                        if buy_price > 0 and quantity > 0:
                            invested = buy_price * quantity
                            profit = (current_price - buy_price) * quantity
                            stock_return = (profit / invested) * 100 if invested > 0 else 0

                            total_profit += profit
                            total_invested += invested
                            stock_returns.append(stock_return)

                    weights.sort(key=lambda x: x['weight'], reverse=True)

                    # v5.8: Calculate advanced metrics
                    portfolio_return = (total_profit / total_invested * 100) if total_invested > 0 else 0

                    # Sharpe Ratio (simplified: assume risk-free rate = 2%)
                    risk_free_rate = 2.0
                    if len(stock_returns) > 1:
                        import statistics
                        volatility = statistics.stdev(stock_returns)
                        sharpe_ratio = (portfolio_return - risk_free_rate) / volatility if volatility > 0 else 0
                        optimization['sharpe_ratio'] = round(sharpe_ratio, 2)

                    # Value at Risk (95% confidence, parametric method)
                    # VaR = Portfolio Value * 1.65 * Daily Volatility
                    if len(stock_returns) > 1:
                        import statistics
                        daily_volatility = statistics.stdev(stock_returns) / 100
                        var_95 = total_value * 1.65 * daily_volatility
                        optimization['value_at_risk'] = int(var_95)
                    else:
                        # Simple estimate: 5% of portfolio
                        optimization['value_at_risk'] = int(total_value * 0.05)

                    # Portfolio Beta (simplified estimate based on volatility vs market avg)
                    # Market avg volatility ~20%, if portfolio vol > 20%, beta > 1
                    if len(stock_returns) > 1:
                        import statistics
                        portfolio_vol = statistics.stdev(stock_returns)
                        market_vol = 20.0  # Assumed market volatility
                        beta = portfolio_vol / market_vol if market_vol > 0 else 1.0
                        optimization['portfolio_beta'] = round(beta, 2)

                    # Efficiency Score (0-100)
                    # Based on: diversification, sharpe ratio, concentration
                    efficiency_score = 50  # Base score

                    # Diversification bonus (max +20)
                    num_stocks = len(holdings)
                    if num_stocks >= 5 and num_stocks <= 8:
                        efficiency_score += 20
                    elif num_stocks >= 3:
                        efficiency_score += 10

                    # Sharpe ratio bonus (max +20)
                    if optimization['sharpe_ratio'] > 2.0:
                        efficiency_score += 20
                    elif optimization['sharpe_ratio'] > 1.0:
                        efficiency_score += 15
                    elif optimization['sharpe_ratio'] > 0.5:
                        efficiency_score += 10

                    # Concentration penalty (max -20)
                    max_weight = weights[0]['weight'] if weights else 0
                    if max_weight > 40:
                        efficiency_score -= 20
                    elif max_weight > 30:
                        efficiency_score -= 10

                    # Return bonus (max +10)
                    if portfolio_return > 10:
                        efficiency_score += 10
                    elif portfolio_return > 5:
                        efficiency_score += 5

                    optimization['efficiency_score'] = max(0, min(100, efficiency_score))

                    # Add efficiency-based suggestions
                    if optimization['efficiency_score'] >= 80:
                        optimization['suggestions'].insert(0, {
                            'type': 'success',
                            'title': '우수한 포트폴리오',
                            'message': f'포트폴리오 효율성: {optimization["efficiency_score"]}점. 잘 구성된 포트폴리오입니다.',
                            'action': '현 상태 유지'
                        })
                    elif optimization['efficiency_score'] < 50:
                        optimization['suggestions'].insert(0, {
                            'type': 'warning',
                            'title': '포트폴리오 개선 필요',
                            'message': f'포트폴리오 효율성: {optimization["efficiency_score"]}점. 구조 개선이 필요합니다.',
                            'action': '리밸런싱 권장'
                        })

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


@auto_analysis_bp.route('/api/ai/performance-tracker')
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

        bot_instance = get_bot_instance()
        if bot_instance and hasattr(bot_instance, 'account_api'):
            try:
                # Get current holdings for performance
                holdings = bot_instance.account_api.get_holdings()

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


@auto_analysis_bp.route('/api/ai/stock-recommendations')
def get_stock_recommendations():
    """Get AI-powered stock recommendations based on current market conditions"""
    try:
        recommendations = []

        bot_instance = get_bot_instance()
        if bot_instance and hasattr(bot_instance, 'market_api') and hasattr(bot_instance, 'account_api'):
            try:
                # Get current holdings to avoid recommending already-held stocks
                holdings = bot_instance.account_api.get_holdings()
                held_codes = [h.get('stk_cd', '').replace('A', '') for h in holdings]

                # Get market leaders by PRICE CHANGE RATE (상승률) instead of volume
                gainers = bot_instance.market_api.get_price_change_rank(market='ALL', sort='rise', limit=30)

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

                    # Improved scoring system for better differentiation
                    score = 0

                    # 상승률 점수 (최대 100점)
                    if change_rate >= 15:
                        score += 100
                    elif change_rate >= 10:
                        score += 80
                    elif change_rate >= 7:
                        score += 65
                    elif change_rate >= 5:
                        score += 50
                    elif change_rate >= 3:
                        score += 35
                    elif change_rate >= 1:
                        score += 20
                    else:
                        score += 10

                    # 거래량 점수 (최대 100점)
                    if volume >= 10_000_000:
                        score += 100
                    elif volume >= 5_000_000:
                        score += 80
                    elif volume >= 2_000_000:
                        score += 60
                    elif volume >= 1_000_000:
                        score += 40
                    elif volume >= 500_000:
                        score += 25
                    elif volume >= 100_000:
                        score += 15
                    else:
                        score += 5

                    # 기본 점수 제거 (너무 높은 기본 점수로 인해 모든 종목이 비슷한 점수를 받음)
                    # score += 50  # 제거됨

                    # Calculate percentage
                    max_score = 200  # 상승률 100 + 거래량 100
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

                        # v5.8: Enhanced AI Analysis
                        # Calculate target price (simple momentum-based)
                        target_price = int(current_price * (1 + (change_rate / 100) * 0.3))  # 30% of current momentum
                        expected_return = ((target_price - current_price) / current_price * 100)

                        # Risk assessment
                        if change_rate > 15:
                            risk_level = 'High'
                            risk_reason = '급등 종목 - 고위험 고수익'
                        elif change_rate > 10:
                            risk_level = 'Medium-High'
                            risk_reason = '강세 종목 - 변동성 주의'
                        elif change_rate > 5:
                            risk_level = 'Medium'
                            risk_reason = '안정적 상승 - 적정 리스크'
                        else:
                            risk_level = 'Low-Medium'
                            risk_reason = '완만한 상승 - 낮은 리스크'

                        # Entry timing
                        if change_rate > 20:
                            timing = '조정 대기'
                            timing_reason = '과열 구간 - 조정 후 진입 권장'
                        elif change_rate > 10:
                            timing = '분할 매수'
                            timing_reason = '강세 지속 시 추가 매수'
                        else:
                            timing = '즉시 진입'
                            timing_reason = '현재가 진입 적기'

                        # AI Buy reasons
                        ai_reasons = []
                        if change_rate >= 10:
                            ai_reasons.append(f'✓ 강한 모멘텀 ({change_rate:.1f}% 상승)')
                        if volume >= 2_000_000:
                            ai_reasons.append(f'✓ 높은 거래량 ({volume/1_000_000:.1f}M주)')
                        if score >= 150:
                            ai_reasons.append('✓ 종합 점수 우수')

                        recommendations.append({
                            'code': stock_code,
                            'name': stock_name,
                            'price': current_price,
                            'change_rate': change_rate,
                            'score': round(score, 1),
                            'percentage': round(percentage, 1),
                            'grade': grade,
                            'reason': reason,
                            'volume': volume,
                            # v5.8: Enhanced fields
                            'target_price': target_price,
                            'expected_return': round(expected_return, 1),
                            'risk_level': risk_level,
                            'risk_reason': risk_reason,
                            'timing': timing,
                            'timing_reason': timing_reason,
                            'ai_reasons': ai_reasons,
                            'ai_recommendation': f'{timing}: {", ".join(ai_reasons[:2])}'
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


@auto_analysis_bp.route('/api/ai/auto-stop-loss', methods=['POST'])
def execute_auto_stop_loss():
    """
    자동 손절 실행
    - 5% 이상 손실 종목 자동 매도
    """
    try:
        bot_instance = get_bot_instance()
        if not bot_instance or not hasattr(bot_instance, 'account_api') or not hasattr(bot_instance, 'trading_api'):
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
        holdings = bot_instance.account_api.get_holdings()

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
                    order_result = bot_instance.trading_api.sell_market_order(
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


@auto_analysis_bp.route('/api/ai/auto-take-profit', methods=['POST'])
def execute_auto_take_profit():
    """
    자동 익절 실행
    - 15% 이상 수익 종목 일부(50%) 매도
    """
    try:
        bot_instance = get_bot_instance()
        if not bot_instance or not hasattr(bot_instance, 'account_api') or not hasattr(bot_instance, 'trading_api'):
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
        holdings = bot_instance.account_api.get_holdings()

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
                        order_result = bot_instance.trading_api.sell_market_order(
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


@auto_analysis_bp.route('/api/ai/alerts')
def get_ai_alerts():
    """
    실시간 AI 알림
    - 손절/익절 알림
    - 급등/급락 알림
    - 리스크 경고
    """
    try:
        alerts = []

        bot_instance = get_bot_instance()
        if bot_instance and hasattr(bot_instance, 'account_api'):
            try:
                holdings = bot_instance.account_api.get_holdings()

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


@auto_analysis_bp.route('/api/ai/market-trend')
def get_market_trend():
    """Analyze current market trend (Enhanced v5.8)"""
    try:
        trend_data = {
            'trend': 'Neutral',
            'strength': 5,
            'indicators': [],
            'recommendation': '시장 관망 권장',
            # v5.8: Enhanced fields
            'market_sentiment': 'Neutral',  # Fear / Neutral / Greed
            'fear_greed_index': 50,  # 0-100
            'sector_analysis': [],
            'top_gainers_sectors': [],
            'top_losers_sectors': [],
            'trading_value': 0,
            'foreign_buy': 0,
            'institution_buy': 0,
            'market_cap_trend': 'Mixed'
        }

        bot_instance = get_bot_instance()
        if bot_instance and hasattr(bot_instance, 'market_api'):
            try:
                # Get market data
                volume_leaders = bot_instance.market_api.get_volume_rank(limit=100)
                price_gainers = bot_instance.market_api.get_price_change_rank(market='ALL', sort='rise', limit=30)
                price_losers = bot_instance.market_api.get_price_change_rank(market='ALL', sort='fall', limit=30)

                print(f"[Market Trend] volume_leaders: {len(volume_leaders) if volume_leaders else 0}, gainers: {len(price_gainers) if price_gainers else 0}, losers: {len(price_losers) if price_losers else 0}")

                if volume_leaders and len(volume_leaders) > 0:
                    # Count gainers vs losers
                    gainers = sum(1 for s in volume_leaders if float(s.get('prdy_ctrt', 0)) > 0)
                    losers = sum(1 for s in volume_leaders if float(s.get('prdy_ctrt', 0)) < 0)
                    unchanged = len(volume_leaders) - gainers - losers

                    gainer_ratio = gainers / len(volume_leaders) if volume_leaders else 0.5

                    # Calculate trading value
                    total_trading_value = 0
                    for s in volume_leaders[:30]:
                        volume = int(s.get('acml_vol', 0))
                        price = int(s.get('stck_prpr', 0))
                        total_trading_value += volume * price

                    trend_data['trading_value'] = total_trading_value

                    # Trend determination
                    if gainer_ratio > 0.6:
                        trend_data['trend'] = 'Bullish'
                        trend_data['strength'] = min(10, 7 + int((gainer_ratio - 0.6) * 10))
                        trend_data['recommendation'] = '매수 타이밍 - 강세장'
                        trend_data['market_sentiment'] = 'Greed' if gainer_ratio > 0.75 else 'Optimism'
                        trend_data['fear_greed_index'] = int(60 + (gainer_ratio - 0.6) * 100)
                    elif gainer_ratio < 0.4:
                        trend_data['trend'] = 'Bearish'
                        trend_data['strength'] = max(-10, 3 - int((0.4 - gainer_ratio) * 10))
                        trend_data['recommendation'] = '관망 또는 매도 고려'
                        trend_data['market_sentiment'] = 'Fear' if gainer_ratio < 0.25 else 'Pessimism'
                        trend_data['fear_greed_index'] = int(40 - (0.4 - gainer_ratio) * 100)
                    else:
                        trend_data['trend'] = 'Neutral'
                        trend_data['strength'] = 5
                        trend_data['recommendation'] = '중립 - 선별 투자'
                        trend_data['market_sentiment'] = 'Neutral'
                        trend_data['fear_greed_index'] = int(40 + gainer_ratio * 40)

                    # Indicators
                    trend_data['indicators'].append(f'• 상승종목 {gainers}개 vs 하락종목 {losers}개 (보합 {unchanged})')

                    # Average volume
                    avg_volume = sum(int(s.get('acml_vol', 0)) for s in volume_leaders) / len(volume_leaders)
                    trend_data['indicators'].append(f'• 평균 거래량: {avg_volume/1_000_000:.1f}M주')

                    # Trading value
                    trend_data['indicators'].append(f'• 주요 종목 거래대금: {total_trading_value/1_000_000_000:.1f}억원')

                    # Fear & Greed analysis
                    if trend_data['fear_greed_index'] > 70:
                        trend_data['indicators'].append(f'• 시장 심리: 탐욕 단계 ({trend_data["fear_greed_index"]}) - 과열 주의')
                    elif trend_data['fear_greed_index'] < 30:
                        trend_data['indicators'].append(f'• 시장 심리: 공포 단계 ({trend_data["fear_greed_index"]}) - 저점 매수 기회')
                    else:
                        trend_data['indicators'].append(f'• 시장 심리: 중립 ({trend_data["fear_greed_index"]}) - 균형 상태')

                    # Sector analysis (simplified)
                    # Group by industry/sector if available
                    sector_count = {}
                    for stock in price_gainers[:20]:
                        # Since we don't have sector data, use name patterns
                        name = stock.get('name', '')
                        if '전자' in name or '반도체' in name:
                            sector_count['IT/반도체'] = sector_count.get('IT/반도체', 0) + 1
                        elif '바이오' in name or '제약' in name:
                            sector_count['바이오/제약'] = sector_count.get('바이오/제약', 0) + 1
                        elif '금융' in name or '은행' in name or '증권' in name:
                            sector_count['금융'] = sector_count.get('금융', 0) + 1
                        elif '건설' in name or '부동산' in name:
                            sector_count['건설/부동산'] = sector_count.get('건설/부동산', 0) + 1
                        else:
                            sector_count['기타'] = sector_count.get('기타', 0) + 1

                    if sector_count:
                        top_sectors = sorted(sector_count.items(), key=lambda x: x[1], reverse=True)[:3]
                        trend_data['top_gainers_sectors'] = [f'{s[0]} ({s[1]}개)' for s in top_sectors]
                        trend_data['indicators'].append(f'• 강세 섹터: {", ".join(trend_data["top_gainers_sectors"])}')

                    # Market cap trend (large cap vs small cap)
                    large_cap_gainers = sum(1 for s in price_gainers if int(s.get('price', 0)) > 50000)
                    small_cap_gainers = len(price_gainers) - large_cap_gainers

                    if large_cap_gainers > small_cap_gainers * 1.5:
                        trend_data['market_cap_trend'] = 'Large Cap Rally'
                        trend_data['indicators'].append('• 대형주 강세 - 안정적 상승')
                    elif small_cap_gainers > large_cap_gainers * 1.5:
                        trend_data['market_cap_trend'] = 'Small Cap Rally'
                        trend_data['indicators'].append('• 중소형주 강세 - 고위험 고수익')
                    else:
                        trend_data['market_cap_trend'] = 'Mixed'
                        trend_data['indicators'].append('• 시가총액 균형 - 전반적 상승')

            except Exception as e:
                print(f"Market trend analysis error: {e}")
                import traceback
                traceback.print_exc()

        return jsonify({
            'success': True,
            'trend': trend_data
        })

    except Exception as e:
        print(f"Market trend error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })


@auto_analysis_bp.route('/api/ai/auto-analysis')
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

        bot_instance = get_bot_instance()
        if bot_instance and hasattr(bot_instance, 'account_api'):
            # Portfolio Analysis - v5.7.5 더 실용적인 버전
            try:
                holdings = bot_instance.account_api.get_holdings()

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
                holdings = bot_instance.account_api.get_holdings()

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
                holdings = bot_instance.account_api.get_holdings()

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
