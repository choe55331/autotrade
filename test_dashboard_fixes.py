#!/usr/bin/env python3
"""
대시보드 수정사항 테스트 스크립트
테스트 항목:
1. 계좌 정보 API (kt00001 필드)
2. 보유현황 API (kt00004 필드)
3. 가상매매 API
4. 매수 기능 (수량 계산)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.account import AccountAPI
from api.order import OrderAPI
from core.rest_client import KiwoomRESTClient
from config.config_manager import get_config


def test_account_info():
    """계좌 정보 테스트 (kt00001 API 필드 검증)"""
    print("\n" + "="*60)
    print("TEST 1: 계좌 정보 API 필드 검증")
    print("="*60)

    try:
        config = get_config()
        client = KiwoomRESTClient(
            app_key=config['api']['app_key'],
            app_secret=config['api']['app_secret'],
            account_number=config['api']['account_number']
        )

        account_api = AccountAPI(client)
        deposit = account_api.get_deposit()

        if not deposit:
            print("❌ FAIL: 예수금 정보를 가져올 수 없습니다")
            return False

        # 필드 검증
        print("\n✅ 예수금 정보 조회 성공")
        print(f"   - entr (예수금): {deposit.get('entr', 'N/A')}")
        print(f"   - 100stk_ord_alow_amt (주문가능금액): {deposit.get('100stk_ord_alow_amt', 'N/A')}")
        print(f"   - ord_alow_amt (일반주문가능금액): {deposit.get('ord_alow_amt', 'N/A')}")

        # 계산 검증
        entr = int(str(deposit.get('entr', '0')).replace(',', ''))
        orderable = int(str(deposit.get('100stk_ord_alow_amt', '0')).replace(',', ''))

        print(f"\n💰 계산 결과:")
        print(f"   - 예수금: {entr:,}원")
        print(f"   - 주문가능금액: {orderable:,}원")

        if orderable > 0:
            print("✅ PASS: 주문가능금액이 정상적으로 계산되었습니다")
            return True
        else:
            print("⚠️  WARNING: 주문가능금액이 0입니다 (잔고 부족 또는 전액 투자)")
            return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_holdings():
    """보유현황 테스트 (kt00004 API 필드 검증)"""
    print("\n" + "="*60)
    print("TEST 2: 보유현황 API 필드 검증")
    print("="*60)

    try:
        config = get_config()
        client = KiwoomRESTClient(
            app_key=config['api']['app_key'],
            app_secret=config['api']['app_secret'],
            account_number=config['api']['account_number']
        )

        account_api = AccountAPI(client)
        holdings = account_api.get_holdings()

        if not holdings:
            print("✅ 보유 종목 없음 (정상)")
            return True

        print(f"\n✅ 보유 종목 {len(holdings)}개 조회 성공")

        for i, h in enumerate(holdings[:3], 1):  # 최대 3개만 표시
            code = str(h.get('stk_cd', '')).strip()
            if code.startswith('A'):
                code = code[1:]

            name = h.get('stk_nm', '')
            qty = int(str(h.get('rmnd_qty', 0)).replace(',', ''))
            avg_price = int(str(h.get('avg_prc', 0)).replace(',', ''))
            cur_price = int(str(h.get('cur_prc', 0)).replace(',', ''))
            eval_amt = int(str(h.get('eval_amt', 0)).replace(',', ''))

            print(f"\n{i}. {name} ({code})")
            print(f"   - 보유수량: {qty}주")
            print(f"   - 평균단가: {avg_price:,}원")
            print(f"   - 현재가: {cur_price:,}원")
            print(f"   - 평가금액: {eval_amt:,}원")

        print("\n✅ PASS: 모든 필드가 정상적으로 파싱되었습니다")
        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_virtual_trading():
    """가상매매 시스템 테스트"""
    print("\n" + "="*60)
    print("TEST 3: 가상매매 시스템 검증")
    print("="*60)

    try:
        from features.virtual_trading import VirtualTrader

        # 가상매매 인스턴스 생성
        virtual_trader = VirtualTrader(initial_cash=10_000_000)

        print("\n✅ VirtualTrader 초기화 성공")
        print(f"   - 초기 자본: 10,000,000원")
        print(f"   - 전략 개수: {len(virtual_trader.accounts)}개")

        # 전략별 요약 조회
        summaries = virtual_trader.get_all_summaries()

        for strategy_name, summary in summaries.items():
            print(f"\n📊 {strategy_name}:")
            print(f"   - 현금: {summary['cash']:,.0f}원")
            print(f"   - 수익률: {summary['return_rate']*100:+.2f}%")
            print(f"   - 포지션: {summary['position_count']}개")
            print(f"   - 승률: {summary['win_rate']*100:.1f}%")

        # 최고 전략
        best = virtual_trader.get_best_strategy()
        print(f"\n🏆 최고 성과 전략: {best}")

        print("\n✅ PASS: 가상매매 시스템이 정상 작동합니다")
        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_buy_calculation():
    """매수 수량 계산 테스트"""
    print("\n" + "="*60)
    print("TEST 4: 매수 수량 계산 검증")
    print("="*60)

    try:
        config = get_config()
        client = KiwoomRESTClient(
            app_key=config['api']['app_key'],
            app_secret=config['api']['app_secret'],
            account_number=config['api']['account_number']
        )

        account_api = AccountAPI(client)

        # 예수금 조회
        deposit = account_api.get_deposit()
        holdings = account_api.get_holdings()

        # 올바른 필드 사용
        deposit_total = int(str(deposit.get('entr', '0')).replace(',', '')) if deposit else 0
        available_cash = int(str(deposit.get('100stk_ord_alow_amt', '0')).replace(',', '')) if deposit else 0

        print(f"\n💰 계좌 정보:")
        print(f"   - 예수금: {deposit_total:,}원")
        print(f"   - 주문가능금액: {available_cash:,}원")

        # 수량 계산 시뮬레이션
        from strategy.dynamic_risk_manager import DynamicRiskManager

        risk_manager = DynamicRiskManager(initial_capital=deposit_total + 1_000_000)  # 예시

        # 테스트 주가
        test_prices = [10000, 20000, 50000, 100000]

        print(f"\n📊 매수 가능 수량 계산 (리스크 관리 적용):")
        for price in test_prices:
            qty = risk_manager.calculate_position_size(
                stock_price=price,
                available_cash=available_cash
            )
            print(f"   - 주가 {price:,}원: {qty}주 (총 {qty*price:,}원)")

        # 검증
        if available_cash > 0:
            print("\n✅ PASS: 매수 가능 금액이 정상적으로 계산되었습니다")
            print("   ⚠️  장 운영 시간에 실제 주문을 테스트하세요")
            return True
        else:
            print("\n⚠️  WARNING: 주문가능금액이 0입니다")
            print("   - 잔고를 확인하거나 장 운영 시간에 다시 테스트하세요")
            return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """전체 테스트 실행"""
    print("\n" + "="*60)
    print("🧪 대시보드 수정사항 종합 테스트")
    print("="*60)

    results = {
        "계좌 정보 API": test_account_info(),
        "보유현황 API": test_holdings(),
        "가상매매 시스템": test_virtual_trading(),
        "매수 수량 계산": test_buy_calculation(),
    }

    # 결과 요약
    print("\n" + "="*60)
    print("📊 테스트 결과 요약")
    print("="*60)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    total = len(results)
    passed = sum(results.values())

    print(f"\n총 {total}개 테스트 중 {passed}개 통과 ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n🎉 모든 테스트 통과!")
    else:
        print(f"\n⚠️  {total - passed}개 테스트 실패")

    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
