#!/usr/bin/env python3
"""
대시보드 이슈 원클릭 테스트

사용법:
    python test_dashboard.py

모든 테스트를 자동으로 실행하고 결과를 표시합니다.
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.rest_client import KiwoomRESTClient
from api.market import MarketAPI
from api.account import AccountAPI
import traceback


def init_apis():
    """API 초기화"""
    print("🔧 API 초기화 중...")

    try:
        # REST Client 초기화 (내부에서 자동으로 설정 로드)
        client = KiwoomRESTClient()

        # API 초기화
        market_api = MarketAPI(client)
        account_api = AccountAPI(client)

        print("✅ API 초기화 완료\n")
        return market_api, account_api

    except Exception as e:
        print(f"❌ API 초기화 실패: {e}")
        traceback.print_exc()
        return None, None


def test_account_balance(account_api):
    """계좌 잔고 계산 테스트"""
    print("=" * 80)
    print("📊 테스트 1: 계좌 잔고 계산")
    print("=" * 80)

    if not account_api:
        print("⚠️  account_api 없음\n")
        return False

    try:
        from tests.manual_tests.patches.fix_account_balance import AccountBalanceFix

        print("📍 예수금 조회 중...")
        deposit = account_api.get_deposit()

        print("📍 보유종목 조회 중...")
        holdings = account_api.get_holdings()

        if not deposit:
            print("❌ 예수금 조회 실패\n")
            return False

        if holdings is None:
            print("❌ 보유종목 조회 실패\n")
            return False

        print("📍 계좌 잔고 계산 중...\n")

        # 접근법 1 (추천)
        result1 = AccountBalanceFix.approach_1_deposit_minus_purchase(deposit, holdings)

        print("✅ [접근법 1] 예수금 - 구매원가 (추천)")
        print(f"   예수금: {result1['_debug']['deposit_amount']:,}원")
        print(f"   구매원가: {result1['_debug']['total_purchase_cost']:,}원")
        print(f"   💰 실제 사용가능액: {result1['cash']:,}원")
        print(f"   총 자산: {result1['total_assets']:,}원")
        print(f"   보유주식: {result1['stock_value']:,}원")
        print(f"   손익: {result1['profit_loss']:,}원 ({result1['profit_loss_percent']:.2f}%)")

        print()

        # 접근법 2
        result2 = AccountBalanceFix.approach_2_manual_calculation(deposit, holdings)
        print("✅ [접근법 2] 수동 계산")
        print(f"   💰 실제 사용가능액: {result2['cash']:,}원")

        print()

        # 기존 방식 (비교용)
        old_cash = int(deposit.get('ord_alow_amt', 0))
        print("⚠️  [기존 방식] 인출가능액 사용")
        print(f"   인출가능액: {old_cash:,}원")
        print(f"   차이: {result1['cash'] - old_cash:,}원")

        print()
        return True

    except Exception as e:
        print(f"❌ 계좌 잔고 테스트 실패: {e}")
        traceback.print_exc()
        print()
        return False


def test_nxt_price(market_api, account_api):
    """NXT 시장가격 조회 테스트"""
    print("=" * 80)
    print("💰 테스트 2: NXT 시장가격 조회")
    print("=" * 80)

    if not market_api:
        print("⚠️  market_api 없음\n")
        return False

    try:
        from tests.manual_tests.patches.fix_nxt_price import MarketAPIExtended, NXTPriceFix

        # 현재 시간 정보
        is_regular = NXTPriceFix.is_regular_market_time()
        is_nxt = NXTPriceFix.is_nxt_time()

        print(f"📍 현재 시간 정보:")
        print(f"   정규시장 시간: {'예' if is_regular else '아니오'}")
        print(f"   NXT 거래시간: {'예' if is_nxt else '아니오'}")
        print()

        # 테스트 종목 (삼성전자, SK하이닉스)
        test_stocks = [
            ('005930', '삼성전자'),
            ('000660', 'SK하이닉스')
        ]

        market_api_ext = MarketAPIExtended(market_api, account_api)

        success_count = 0

        for stock_code, stock_name in test_stocks:
            print(f"📍 {stock_name} ({stock_code}) 가격 조회 중...")

            # 접근법 4 (여러 소스 시도)
            price_info = market_api_ext.get_current_price_with_source(stock_code)

            if price_info['price'] > 0:
                print(f"✅ 가격 조회 성공")
                print(f"   💰 현재가: {price_info['price']:,}원")
                print(f"   출처: {price_info['source']}")
                print(f"   시도한 소스: {', '.join(price_info.get('sources_tried', []))}")
                success_count += 1
            else:
                print(f"❌ 가격 조회 실패")
                print(f"   시도한 소스: {', '.join(price_info.get('sources_tried', []))}")

            print()

        if success_count > 0:
            print(f"✅ {success_count}/{len(test_stocks)}개 종목 가격 조회 성공")
            print()
            return True
        else:
            print(f"❌ 모든 종목 가격 조회 실패")
            print()
            return False

    except Exception as e:
        print(f"❌ NXT 가격 조회 테스트 실패: {e}")
        traceback.print_exc()
        print()
        return False


def test_ai_scanning():
    """AI 스캐닝 연동 테스트"""
    print("=" * 80)
    print("🤖 테스트 3: AI 스캐닝 종목 연동")
    print("=" * 80)

    # 이 테스트는 봇이 실행 중일 때만 가능
    print("⚠️  이 테스트는 main.py가 실행 중일 때만 작동합니다.")
    print()
    print("봇 실행 후 다음 명령으로 테스트하세요:")
    print("  python -c \"from tests.manual_tests.run_dashboard_tests import quick_test; import main; quick_test(main.bot)\"")
    print()

    # 또는 파일 기반으로 확인
    print("또는 scanner_pipeline 파일 확인:")

    try:
        # main.py에서 bot 인스턴스를 가져올 수 있는지 확인
        import importlib.util

        # main 모듈이 로드되어 있는지 확인
        if 'main' in sys.modules:
            main_module = sys.modules['main']
            if hasattr(main_module, 'bot'):
                bot = main_module.bot

                from tests.manual_tests.patches.fix_ai_scanning import get_scanning_info

                scanning_info = get_scanning_info(bot, method='combined')

                print("✅ AI 스캐닝 정보 조회 성공")
                print(f"   Fast Scan (스캐닝 종목): {scanning_info['fast_scan']['count']}개")
                print(f"   Deep Scan (AI 분석 완료): {scanning_info['deep_scan']['count']}개")
                print(f"   AI Scan (매수 대기): {scanning_info['ai_scan']['count']}개")
                print()
                return True
            else:
                print("⚠️  main.bot 인스턴스를 찾을 수 없습니다.")
                print()
                return False
        else:
            print("⚠️  main 모듈이 로드되지 않았습니다.")
            print()
            return False

    except Exception as e:
        print(f"⚠️  AI 스캐닝 테스트 스킵: {e}")
        print()
        return False


def main():
    """메인 테스트 실행"""
    print("\n" + "=" * 80)
    print("🚀 대시보드 이슈 원클릭 테스트")
    print("=" * 80)
    print()

    # API 초기화
    market_api, account_api = init_apis()

    if not market_api or not account_api:
        print("❌ API 초기화 실패. 테스트를 중단합니다.")
        return 1

    # 테스트 결과
    results = {
        'account_balance': False,
        'nxt_price': False,
        'ai_scanning': False
    }

    # 테스트 1: 계좌 잔고
    results['account_balance'] = test_account_balance(account_api)

    # 테스트 2: NXT 가격
    results['nxt_price'] = test_nxt_price(market_api, account_api)

    # 테스트 3: AI 스캐닝
    results['ai_scanning'] = test_ai_scanning()

    # 결과 요약
    print("=" * 80)
    print("📊 테스트 결과 요약")
    print("=" * 80)
    print()

    total = len(results)
    success = sum(1 for v in results.values() if v)

    for test_name, success_flag in results.items():
        status = "✅ 성공" if success_flag else "❌ 실패"
        print(f"  {status}: {test_name}")

    print()
    print(f"총 {success}/{total}개 테스트 성공")
    print()

    if success == total:
        print("🎉 모든 테스트 성공!")
        print()
        print("다음 단계:")
        print("  1. tests/manual_tests/README_DASHBOARD_FIXES.md 참고")
        print("  2. dashboard/app_apple.py에 패치 적용")
        print()
        return 0
    else:
        print("⚠️  일부 테스트 실패")
        print()
        print("해결 방법:")
        print("  - API 키 확인: config/config.yaml")
        print("  - 네트워크 연결 확인")
        print("  - 상세 로그 확인")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
