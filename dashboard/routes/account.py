"""
Account-related API routes
Handles account balance, positions, and detailed holdings
"""
from flask import Blueprint, jsonify
from typing import Dict, Any
from datetime import datetime

account_bp = Blueprint('account', __name__)

_bot_instance = None


def set_bot_instance(bot):
    """Set the bot instance for this module"""
    global _bot_instance
    _bot_instance = bot


@account_bp.route('/api/account')
def get_account():
    """Get account information from real API"""
    test_mode_active = False
    test_date = None
    if _bot_instance:
        test_mode_active = getattr(_bot_instance, 'test_mode_active', False)
        test_date = getattr(_bot_instance, 'test_date', None)

    try:
        if _bot_instance and hasattr(_bot_instance, 'account_api'):
            deposit = _bot_instance.account_api.get_deposit()

            holdings = _bot_instance.account_api.get_holdings(market_type="KRX+NXT") or []

            if holdings:
                print(f"[ACCOUNT] 보유 종목: {len(holdings)}개")
                for h in holdings:
                    print(f"  - {h.get('stk_cd', 'N/A')} {h.get('stk_nm', 'N/A')}: {h.get('rmnd_qty', 0)}주")
            else:
                print(f"[ACCOUNT] 보유 종목: 없음")

            deposit_amount = int(str(deposit.get('entr', '0')).replace(',', '')) if deposit else 0
            cash = int(str(deposit.get('100stk_ord_alow_amt', '0')).replace(',', '')) if deposit else 0

            stock_value = 0
            if holdings:
                for h in holdings:
                    eval_amt = int(str(h.get('eval_amt', 0)).replace(',', ''))
                    if eval_amt > 0:
                        stock_value += eval_amt
                    else:
                        quantity = int(str(h.get('rmnd_qty', 0)).replace(',', ''))
                        cur_price = int(str(h.get('cur_prc', 0)).replace(',', ''))
                        calculated_value = quantity * cur_price
                        stock_value += calculated_value

            total_assets = stock_value + cash

            print(f"[ACCOUNT] 총자산: {total_assets:,}원 (주식: {stock_value:,}원 + 현금: {cash:,}원)")

            total_buy_amount = 0
            profit_loss_detailed = []

            if holdings:
                for h in holdings:
                    stock_code = h.get('stk_cd', '')
                    stock_name = h.get('stk_nm', '')

                    quantity = int(str(h.get('rmnd_qty', 0)).replace(',', ''))
                    avg_price = int(str(h.get('avg_prc', 0)).replace(',', ''))
                    cur_price = int(str(h.get('cur_prc', 0)).replace(',', ''))

                    buy_amt = avg_price * quantity

                    eval_amt = int(str(h.get('eval_amt', 0)).replace(',', ''))
                    if eval_amt == 0:
                        eval_amt = quantity * cur_price

                    stock_pl = eval_amt - buy_amt
                    total_buy_amount += buy_amt

                    profit_loss_detailed.append({
                        'code': stock_code,
                        'name': stock_name,
                        'buy_amount': buy_amt,
                        'eval_amount': eval_amt,
                        'profit_loss': stock_pl
                    })

                    print(f"[ACCOUNT] {stock_code} ({stock_name}) 손익: {stock_pl:,}원 (매입: {buy_amt:,}원 = {quantity}주 × {avg_price:,}원, 평가: {eval_amt:,}원)")

            profit_loss = stock_value - total_buy_amount
            profit_loss_percent = (profit_loss / total_buy_amount * 100) if total_buy_amount > 0 else 0

            print(f"[ACCOUNT] 총 손익: {profit_loss:,}원 ({profit_loss_percent:+.2f}%)")
            print(f"[ACCOUNT] 총 매입금액: {total_buy_amount:,}원 (정확한 계산: avg_prc × rmnd_qty)")
            print(f"[ACCOUNT] 총 평가금액: {stock_value:,}원")

            return jsonify({
                'total_assets': total_assets,
                'cash': cash,
                'stock_value': stock_value,
                'profit_loss': profit_loss,
                'profit_loss_percent': profit_loss_percent,
                'open_positions': len(holdings) if holdings else 0,
                'test_mode': test_mode_active,
                'test_date': test_date
            })
        else:
            return jsonify({
                'total_assets': 0,
                'cash': 0,
                'stock_value': 0,
                'profit_loss': 0,
                'profit_loss_percent': 0,
                'open_positions': 0,
                'test_mode': test_mode_active,
                'test_date': test_date
            })
    except Exception as e:
        print(f"Error getting account info: {e}")
        return jsonify({
            'total_assets': 0,
            'cash': 0,
            'stock_value': 0,
            'profit_loss': 0,
            'profit_loss_percent': 0,
            'open_positions': 0,
            'test_mode': test_mode_active,
            'test_date': test_date
        })


@account_bp.route('/api/positions')
def get_positions():
    """Get current positions from real API (kt00004 API 응답 필드 사용)"""
    try:
        if not _bot_instance:
            print("Error: bot_instance is None")
            return jsonify([])

        if not hasattr(_bot_instance, 'account_api'):
            print("Error: bot_instance has no account_api")
            return jsonify([])

        holdings = _bot_instance.account_api.get_holdings(market_type="KRX+NXT")

        if not holdings:
            print("[POSITIONS] 보유 종목 없음")
            return jsonify([])

        positions = []
        for h in holdings:
            try:
                code = str(h.get('stk_cd', '')).strip()
                if code.startswith('A'):
                    code = code[1:]

                name = h.get('stk_nm', '')
                quantity = int(str(h.get('rmnd_qty', 0)).replace(',', ''))

                if quantity <= 0:
                    continue

                avg_price = int(str(h.get('avg_prc', 0)).replace(',', ''))
                current_price = int(str(h.get('cur_prc', 0)).replace(',', ''))

                value = int(str(h.get('eval_amt', 0)).replace(',', ''))
                if value == 0 and current_price > 0:
                    value = quantity * current_price

                profit_loss = value - (avg_price * quantity)
                profit_loss_percent = ((current_price - avg_price) / avg_price * 100) if avg_price > 0 else 0

                optimization_info = {}
                try:
                    from features.profit_optimizer import get_profit_optimizer

                    optimizer = get_profit_optimizer()

                    highest_price = max(current_price, avg_price)
                    if profit_loss_percent > 0:
                        highest_price = current_price

                    days_held = 5

                    analysis = optimizer.analyze_position(
                        entry_price=avg_price,
                        current_price=current_price,
                        highest_price=highest_price,
                        quantity=quantity,
                        days_held=days_held,
                        rule_name='balanced'
                    )

                    estimated_atr = current_price * 0.02
                    exit_levels = optimizer.optimize_exit_levels(
                        entry_price=avg_price,
                        atr=estimated_atr,
                        rule_name='balanced'
                    )

                    optimization_info = {
                        'action': analysis.action,
                        'reason': analysis.reason,
                        'sell_ratio': analysis.sell_ratio,
                        'optimized_stop_loss': exit_levels['stop_loss'],
                        'optimized_take_profit': exit_levels['take_profit'],
                        'risk_reward_ratio': exit_levels['risk_reward_ratio'],
                        'trailing_stop': analysis.new_stop_loss if analysis.new_stop_loss else None
                    }

                except Exception as e:
                    print(f"Error in profit optimization for {code}: {e}")
                    optimization_info = {
                        'action': 'hold',
                        'reason': '분석 불가',
                        'sell_ratio': 0.0
                    }

                stop_loss_price = avg_price
                if _bot_instance and hasattr(_bot_instance, 'dynamic_risk_manager'):
                    try:
                        thresholds = _bot_instance.dynamic_risk_manager.get_exit_thresholds(avg_price)
                        stop_loss_price = thresholds.get('stop_loss', avg_price)
                    except Exception as e:
                        print(f"Error getting exit thresholds for {code}: {e}")

                positions.append({
                    'code': code,
                    'name': name,
                    'quantity': quantity,
                    'avg_price': avg_price,
                    'current_price': current_price,
                    'profit_loss': profit_loss,
                    'profit_loss_percent': profit_loss_percent,
                    'value': value,
                    'stop_loss_price': stop_loss_price,
                    'optimization': optimization_info
                })
            except Exception as e:
                print(f"Error processing holding {h}: {e}")
                continue

        return jsonify(positions)

    except Exception as e:
        print(f"Error getting positions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([])


@account_bp.route('/api/portfolio/real-holdings')
def get_real_holdings():
    """실제 보유 종목 상세 정보 (수익률, ATR 기반 손절/익절)"""
    try:
        if not _bot_instance:
            print("Error: bot_instance is None")
            return jsonify({
                'success': False,
                'message': 'Bot not initialized'
            })

        holdings = []

        if not hasattr(_bot_instance, 'account_api'):
            print("Error: bot_instance has no account_api")
            return jsonify({
                'success': False,
                'message': 'Account API not available'
            })

        raw_holdings = _bot_instance.account_api.get_holdings(market_type="KRX+NXT")

        if not raw_holdings:
            print("[HOLDINGS] 보유 종목 없음")
            return jsonify({
                'success': True,
                'data': []
            })

        print(f"[HOLDINGS] {len(raw_holdings)}개 종목 분석 중...")

        for idx, holding in enumerate(raw_holdings):
            try:
                stock_code = str(holding.get('stk_cd', '')).strip()
                if stock_code.startswith('A'):
                    stock_code = stock_code[1:]

                stock_name = holding.get('stk_nm', stock_code)
                quantity = int(str(holding.get('rmnd_qty', 0)).replace(',', ''))

                if quantity <= 0:
                    continue

                avg_price = int(str(holding.get('avg_prc', 0)).replace(',', ''))
                current_price = int(str(holding.get('cur_prc', 0)).replace(',', ''))

                eval_amount = int(str(holding.get('eval_amt', 0)).replace(',', ''))
                if eval_amount == 0 and current_price > 0:
                    eval_amount = quantity * current_price

                pnl = (current_price - avg_price) * quantity
                pnl_rate = ((current_price - avg_price) / avg_price * 100) if avg_price > 0 else 0

                stop_loss_price = int(avg_price * 0.95)
                take_profit_price = int(avg_price * 1.10)
                kelly_fraction = 0.10
                sharpe_ratio = 0
                max_dd = 0
                rsi = 50
                bb_position = 0.5
                risk_reward_ratio = 2.0

                try:
                    if hasattr(_bot_instance, 'market_api'):
                        print(f"  [{idx+1}/{len(raw_holdings)}] Fetching daily data for {stock_code}...")
                        daily_data = _bot_instance.market_api.get_daily_chart(stock_code, period=20)

                        if daily_data and len(daily_data) >= 14:
                            atr_values = []
                            for i in range(1, min(15, len(daily_data))):
                                high = daily_data[i].get('high', 0)
                                low = daily_data[i].get('low', 0)
                                prev_close = daily_data[i-1].get('close', 0)

                                tr = max(
                                    high - low,
                                    abs(high - prev_close),
                                    abs(low - prev_close)
                                )
                                atr_values.append(tr)

                            if atr_values:
                                atr = sum(atr_values) / len(atr_values)

                                stop_loss_price = int(avg_price - (atr * 2))
                                take_profit_price = int(avg_price + (atr * 3))

                                win_rate = 0.60
                                avg_win_loss_ratio = 1.5
                                kelly_fraction = (win_rate * avg_win_loss_ratio - (1 - win_rate)) / avg_win_loss_ratio
                                kelly_fraction = max(0, min(kelly_fraction, 0.25))

                                returns = []
                                for j in range(1, len(daily_data)):
                                    close_today = daily_data[j-1].get('close', 0)
                                    close_yesterday = daily_data[j].get('close', 0)
                                    if close_yesterday > 0:
                                        ret = (close_today - close_yesterday) / close_yesterday
                                        returns.append(ret)

                                if returns:
                                    avg_return = sum(returns) / len(returns)
                                    variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
                                    std_return = variance ** 0.5
                                    sharpe_ratio = (avg_return / std_return * (252 ** 0.5)) if std_return > 0 else 0
                                else:
                                    sharpe_ratio = 0

                                peak = daily_data[0].get('close', current_price)
                                max_dd = 0
                                for data in daily_data:
                                    price = data.get('close', 0)
                                    if price > peak:
                                        peak = price
                                    dd = (peak - price) / peak if peak > 0 else 0
                                    if dd > max_dd:
                                        max_dd = dd

                                gains = []
                                losses = []
                                for k in range(1, min(15, len(daily_data))):
                                    change = daily_data[k-1].get('close', 0) - daily_data[k].get('close', 0)
                                    if change > 0:
                                        gains.append(change)
                                        losses.append(0)
                                    else:
                                        gains.append(0)
                                        losses.append(abs(change))

                                avg_gain = sum(gains) / len(gains) if gains else 0
                                avg_loss = sum(losses) / len(losses) if losses else 0.01
                                rs = avg_gain / avg_loss if avg_loss > 0 else 0
                                rsi = 100 - (100 / (1 + rs)) if rs > 0 else 50

                                closes = [d.get('close', 0) for d in daily_data[:20]]
                                sma_20 = sum(closes) / len(closes) if closes else current_price
                                variance_bb = sum((c - sma_20) ** 2 for c in closes) / len(closes) if closes else 0
                                std_20 = variance_bb ** 0.5
                                bb_upper = sma_20 + (std_20 * 2)
                                bb_lower = sma_20 - (std_20 * 2)
                                bb_position = ((current_price - bb_lower) / (bb_upper - bb_lower)) if (bb_upper - bb_lower) > 0 else 0.5

                                potential_loss = current_price - stop_loss_price
                                potential_gain = take_profit_price - current_price
                                risk_reward_ratio = potential_gain / potential_loss if potential_loss > 0 else 0

                                print(f"    ✓ ATR-based metrics calculated for {stock_code}")

                except Exception as e:
                    print(f"⚠️ Advanced metrics calculation failed ({stock_code}): {e}")

                distance_to_stop = ((stop_loss_price - current_price) / current_price * 100) if current_price > 0 else 0
                distance_to_target = ((take_profit_price - current_price) / current_price * 100) if current_price > 0 else 0

                holdings.append({
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'quantity': quantity,
                    'avg_price': avg_price,
                    'current_price': current_price,
                    'eval_amount': eval_amount,
                    'pnl': pnl,
                    'pnl_rate': round(pnl_rate, 2),
                    'stop_loss_price': stop_loss_price,
                    'take_profit_price': take_profit_price,
                    'distance_to_stop': round(distance_to_stop, 2),
                    'distance_to_target': round(distance_to_target, 2),
                    'atr_based': True,
                    'kelly_fraction': round(kelly_fraction, 3),
                    'sharpe_ratio': round(sharpe_ratio, 2),
                    'max_drawdown': round(max_dd * 100, 2),
                    'rsi': round(rsi, 1),
                    'bb_position': round(bb_position, 2),
                    'risk_reward_ratio': round(risk_reward_ratio, 2)
                })

                print(f"  [{idx+1}/{len(raw_holdings)}] ✓ {stock_code} processed")

            except Exception as e:
                print(f"  [{idx+1}/{len(raw_holdings)}] ❌ Error processing holding: {e}")
                continue

        print(f"Successfully processed {len(holdings)} holdings")

        return jsonify({
            'success': True,
            'data': holdings
        })

    except Exception as e:
        print(f"❌ 실제 보유 종목 조회 실패: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@account_bp.route('/api/profit-optimization/rules')
def get_optimization_rules():
    """수익 최적화 규칙 조회"""
    try:
        from features.profit_optimizer import get_profit_optimizer

        optimizer = get_profit_optimizer()

        rules_info = []
        for name, rule in optimizer.rules.items():
            rules_info.append({
                'name': name,
                'display_name': rule.name,
                'stop_loss_rate': rule.stop_loss_rate * 100,
                'take_profit_rate': rule.take_profit_rate * 100,
                'trailing_stop_enabled': rule.trailing_stop_enabled,
                'trailing_stop_trigger': rule.trailing_stop_trigger * 100,
                'trailing_stop_distance': rule.trailing_stop_distance * 100,
                'max_holding_days': rule.max_holding_days,
                'partial_profit_enabled': rule.partial_profit_enabled,
                'partial_profit_rate': rule.partial_profit_rate * 100,
                'partial_profit_sell_ratio': rule.partial_profit_sell_ratio * 100
            })

        return jsonify({
            'success': True,
            'rules': rules_info
        })

    except Exception as e:
        print(f"Error getting optimization rules: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@account_bp.route('/api/profit-optimization/summary')
def get_optimization_summary():
    """현재 보유 종목의 수익 최적화 요약"""
    try:
        from features.profit_optimizer import get_profit_optimizer

        if not _bot_instance or not hasattr(_bot_instance, 'account_api'):
            return jsonify({
                'success': False,
                'message': 'Bot not initialized'
            })

        optimizer = get_profit_optimizer()
        holdings = _bot_instance.account_api.get_holdings(market_type="KRX+NXT")

        if not holdings:
            return jsonify({
                'success': True,
                'summary': {
                    'total_positions': 0,
                    'sell_recommended': 0,
                    'hold_recommended': 0,
                    'partial_sell_recommended': 0,
                    'actions': []
                }
            })

        actions = []
        sell_count = 0
        hold_count = 0
        partial_sell_count = 0

        for h in holdings:
            code = str(h.get('stk_cd', '')).replace('A', '')
            name = h.get('stk_nm', '')
            quantity = int(str(h.get('rmnd_qty', 0)).replace(',', ''))

            if quantity <= 0:
                continue

            avg_price = int(str(h.get('avg_prc', 0)).replace(',', ''))
            current_price = int(str(h.get('cur_prc', 0)).replace(',', ''))

            highest_price = max(current_price, avg_price)
            pnl_percent = ((current_price - avg_price) / avg_price * 100) if avg_price > 0 else 0

            if pnl_percent > 0:
                highest_price = current_price

            analysis = optimizer.analyze_position(
                entry_price=avg_price,
                current_price=current_price,
                highest_price=highest_price,
                quantity=quantity,
                days_held=5,
                rule_name='balanced'
            )

            if analysis.action == 'full_sell':
                sell_count += 1
            elif analysis.action == 'partial_sell':
                partial_sell_count += 1
            else:
                hold_count += 1

            actions.append({
                'code': code,
                'name': name,
                'action': analysis.action,
                'reason': analysis.reason,
                'pnl_percent': pnl_percent
            })

        return jsonify({
            'success': True,
            'summary': {
                'total_positions': len(actions),
                'sell_recommended': sell_count,
                'hold_recommended': hold_count,
                'partial_sell_recommended': partial_sell_count,
                'actions': actions
            }
        })

    except Exception as e:
        print(f"Error getting optimization summary: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })
