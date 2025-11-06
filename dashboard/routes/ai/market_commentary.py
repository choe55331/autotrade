"""
Market Commentary Routes
AI real-time market commentary with voice alerts
"""
from flask import Blueprint, jsonify
from datetime import datetime
from .common import get_bot_instance

# Create blueprint
market_commentary_bp = Blueprint('market_commentary', __name__)


# ============================================================================
# v5.7.7: AI 실시간 시장 코멘터리
# ============================================================================

@market_commentary_bp.route('/api/ai/market-commentary')
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

        bot_instance = get_bot_instance()
        if bot_instance and hasattr(bot_instance, 'kis'):
            try:
                account_info = bot_instance.kis.get_account_balance()
                portfolio_info = bot_instance.kis.get_holdings()
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
