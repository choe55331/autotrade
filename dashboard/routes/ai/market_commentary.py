"""
Market Commentary Routes
AI real-time market commentary with voice alerts
"""
from flask import Blueprint, jsonify
from datetime import datetime
from .common import get_bot_instance

market_commentary_bp = Blueprint('market_commentary', __name__)



@market_commentary_bp.route('/api/ai/market-commentary')
def get_market_commentary():
    """AI 실시간 시장 코멘터리 (Enhanced v5.8)"""
    try:
        commentary = {
            'market_summary': '',
            'portfolio_advice': '',
            'opportunities': [],
            'risks': [],
            'speak': False,
            'speak_text': '',
            'market_trend': '',
            'key_issues': [],
            'strategy_recommendation': '',
            'expected_volatility': 'Medium',
            'trading_strategy': '',
        }

        account_info = None
        portfolio_info = None

        bot_instance = get_bot_instance()
        if bot_instance and hasattr(bot_instance, 'kis'):
            try:
                account_info = bot_instance.kis.get_account_balance()
                portfolio_info = bot_instance.kis.get_holdings()
            except Exception as e:
                print(f"계좌 정보 조회 오류: {e}")

        market_summary_parts = []

        if account_info:
            total_assets = account_info.get('total_assets', 0)
            profit_loss = account_info.get('profit_loss', 0)
            profit_loss_pct = account_info.get('profit_loss_percent', 0)

            if profit_loss_pct > 5:
                market_summary_parts.append(f"✨ 포트폴리오가 {profit_loss_pct:.1f}% 상승 중입니다. 수익 실현을 고려하세요.")
            elif profit_loss_pct > 2:
                market_summary_parts.append(f"[UP] 포트폴리오가 {profit_loss_pct:.1f}% 상승했습니다. 안정적인 수익률을 유지하고 있습니다.")
            elif profit_loss_pct < -5:
                market_summary_parts.append(f"[WARNING]️ 포트폴리오가 {abs(profit_loss_pct):.1f}% 하락했습니다. 손절 또는 추가 매수를 검토하세요.")
                commentary['speak'] = True
                commentary['speak_text'] = f"경고: 포트폴리오가 {abs(profit_loss_pct):.1f}퍼센트 하락했습니다."
            elif profit_loss_pct < -2:
                market_summary_parts.append(f"[DOWN] 포트폴리오가 {abs(profit_loss_pct):.1f}% 하락 중입니다. 주의가 필요합니다.")
            else:
                market_summary_parts.append(f"[CHART] 포트폴리오가 {profit_loss_pct:+.1f}% 변동 중입니다. 안정적인 상태입니다.")

        current_hour = datetime.now().hour
        is_market_closed = current_hour >= 15 or current_hour < 9

        if 9 <= current_hour < 10:
            market_summary_parts.append("🔔 장 시작 시간입니다. 시가 변동성에 주의하세요.")
        elif 14 <= current_hour < 15:
            market_summary_parts.append("⏰ 장 마감이 가까워집니다. 포지션 정리를 검토하세요.")
        elif is_market_closed:
            if portfolio_info and len(portfolio_info) > 0:
                avg_pl = sum(p.get('profit_loss_percent', 0) for p in portfolio_info) / len(portfolio_info)
                if avg_pl > 3:
                    market_summary_parts.append(f"✨ 장 종료. 오늘 평균 {avg_pl:.1f}% 수익을 기록했습니다. 좋은 하루였습니다!")
                elif avg_pl > 1:
                    market_summary_parts.append(f"[UP] 장 종료. 오늘 평균 {avg_pl:.1f}% 상승으로 마감했습니다.")
                elif avg_pl < -3:
                    market_summary_parts.append(f"[DOWN] 장 종료. 오늘 평균 {avg_pl:.1f}% 하락했습니다. 내일 반등 기회를 노려보세요.")
                else:
                    market_summary_parts.append(f"[CHART] 장 종료. 오늘 평균 {avg_pl:+.1f}% 변동으로 마감했습니다.")

            commentary['key_issues'].append("💡 내일 주요 체크사항: 해외 증시 동향, 환율 변동, 국내외 뉴스")
            commentary['strategy_recommendation'] = "내일 장 전략을 수립하세요. 오늘의 거래를 복기하고 개선점을 찾아보세요."
        else:
            market_summary_parts.append("[CHART] 정규 장 거래 시간입니다.")

        commentary['market_summary'] = ' '.join(market_summary_parts)

        if portfolio_info and len(portfolio_info) > 0:
            holdings_count = len(portfolio_info)

            if holdings_count > 10:
                commentary['portfolio_advice'] = f"현재 {holdings_count}개 종목을 보유 중입니다. 포트폴리오가 과도하게 분산되어 있을 수 있습니다. 핵심 종목 5-7개로 집중하는 것을 권장합니다."
            elif holdings_count < 3:
                commentary['portfolio_advice'] = f"현재 {holdings_count}개 종목을 보유 중입니다. 리스크 분산을 위해 3-5개 종목으로 다각화하는 것을 권장합니다."
            else:
                commentary['portfolio_advice'] = f"현재 {holdings_count}개 종목을 보유 중입니다. 적절한 분산 수준을 유지하고 있습니다."

            profit_stocks = sum(1 for p in portfolio_info if p.get('profit_loss_percent', 0) > 0)
            loss_stocks = sum(1 for p in portfolio_info if p.get('profit_loss_percent', 0) < 0)

            if profit_stocks > loss_stocks * 2:
                commentary['portfolio_advice'] += f" 수익 종목({profit_stocks})이 손실 종목({loss_stocks})보다 많습니다. 좋은 추세입니다."
            elif loss_stocks > profit_stocks * 2:
                commentary['portfolio_advice'] += f" 손실 종목({loss_stocks})이 수익 종목({profit_stocks})보다 많습니다. 포트폴리오 재검토가 필요합니다."

        if portfolio_info:
            for stock in portfolio_info:
                pl_pct = stock.get('profit_loss_percent', 0)
                name = stock.get('name', '종목')

                if 2 < pl_pct < 5:
                    commentary['opportunities'].append(f"{name}: {pl_pct:+.1f}% 수익 중. 추가 매수 적기일 수 있습니다.")

                if pl_pct > 15:
                    commentary['opportunities'].append(f"{name}: {pl_pct:+.1f}% 수익 달성. 일부 수익 실현을 고려하세요.")

        if portfolio_info:
            for stock in portfolio_info:
                pl_pct = stock.get('profit_loss_percent', 0)
                name = stock.get('name', '종목')

                if pl_pct < -7:
                    commentary['risks'].append(f"[WARNING]️ {name}: {pl_pct:.1f}% 손실. 즉시 손절을 검토하세요.")
                    if not commentary['speak']:
                        commentary['speak'] = True
                        commentary['speak_text'] = f"경고: {name} 종목이 {abs(pl_pct):.1f}퍼센트 손실입니다."

                elif pl_pct < -3:
                    commentary['risks'].append(f"⚡ {name}: {pl_pct:.1f}% 손실. 주의가 필요합니다.")

        if 9 <= current_hour < 10:
            commentary['opportunities'].append("장 시작 30분은 변동성이 큽니다. 신중한 진입이 필요합니다.")
            commentary['expected_volatility'] = 'High'
        elif 14 <= current_hour < 15:
            commentary['risks'].append("장 마감 전 물량 정리가 일어날 수 있습니다.")
            commentary['expected_volatility'] = 'Medium-High'
        else:
            commentary['expected_volatility'] = 'Medium'

        try:
            if bot_instance and hasattr(bot_instance, 'market_api'):
                volume_leaders = bot_instance.market_api.get_volume_rank(limit=50)
                gainers_list = bot_instance.market_api.get_price_change_rank(market='ALL', sort='rise', limit=20)

                if volume_leaders:
                    gainers = sum(1 for s in volume_leaders if float(s.get('prdy_ctrt', 0)) > 0)
                    losers = sum(1 for s in volume_leaders if float(s.get('prdy_ctrt', 0)) < 0)
                    gainer_ratio = gainers / len(volume_leaders)

                    if gainer_ratio > 0.6:
                        commentary['market_trend'] = f'[UP] 강세장 (상승종목 {gainers}개 vs 하락종목 {losers}개)'
                        commentary['trading_strategy'] = '적극적 매수 전략 - 모멘텀 종목 위주 투자'
                    elif gainer_ratio < 0.4:
                        commentary['market_trend'] = f'[DOWN] 약세장 (하락종목 {losers}개 vs 상승종목 {gainers}개)'
                        commentary['trading_strategy'] = '방어적 전략 - 보유 종목 손절 검토, 신규 진입 자제'
                    else:
                        commentary['market_trend'] = f'[CHART] 중립장 (상승 {gainers}, 하락 {losers})'
                        commentary['trading_strategy'] = '선별적 투자 - 우량주 위주 투자, 리스크 관리 강화'

                    if gainers_list:
                        sectors = {}
                        for stock in gainers_list[:10]:
                            name = stock.get('name', '')
                            if '바이오' in name or '제약' in name:
                                sectors['바이오/제약'] = sectors.get('바이오/제약', 0) + 1
                            elif '전자' in name or '반도체' in name:
                                sectors['IT/반도체'] = sectors.get('IT/반도체', 0) + 1
                            elif '2차전지' in name or '배터리' in name:
                                sectors['2차전지'] = sectors.get('2차전지', 0) + 1

                        if sectors:
                            top_sector = max(sectors.items(), key=lambda x: x[1])
                            commentary['key_issues'].append(f'🔥 {top_sector[0]} 섹터 강세 ({top_sector[1]}개 종목 상승)')

                        high_momentum = [s for s in gainers_list if float(s.get('change_rate', 0)) > 15]
                        if len(high_momentum) >= 5:
                            commentary['key_issues'].append(f'⚡ 급등주 다수 출현 ({len(high_momentum)}개) - 시장 과열 주의')
                        elif len(high_momentum) >= 3:
                            commentary['key_issues'].append(f'💫 단기 급등주 증가 ({len(high_momentum)}개) - 변동성 확대')

                if portfolio_info and len(portfolio_info) > 0:
                    avg_profit = sum(p.get('profit_loss_percent', 0) for p in portfolio_info) / len(portfolio_info)

                    if avg_profit > 10:
                        commentary['strategy_recommendation'] = '[TARGET] 수익 실현 단계 - 일부 익절 후 재진입 타이밍 포착'
                    elif avg_profit > 5:
                        commentary['strategy_recommendation'] = '[UP] 안정적 수익 유지 - 트레일링 스톱 설정으로 수익 보호'
                    elif avg_profit < -5:
                        commentary['strategy_recommendation'] = '[WARNING]️ 손실 관리 필요 - 손절 또는 분할 매도 검토'
                    elif avg_profit < -2:
                        commentary['strategy_recommendation'] = '[CHART] 관망 모드 - 신규 진입 자제, 보유 종목 모니터링 강화'
                    else:
                        commentary['strategy_recommendation'] = '🔄 리밸런싱 시기 - 수익 종목 일부 익절, 손실 종목 재검토'
                else:
                    if gainer_ratio > 0.6:
                        commentary['strategy_recommendation'] = '[MONEY] 진입 타이밍 - 강세장에서 우량 종목 발굴'
                    else:
                        commentary['strategy_recommendation'] = '⏳ 관망 추천 - 시장 방향성 확인 후 진입'

        except Exception as e:
            print(f"Enhanced market analysis error: {e}")

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
