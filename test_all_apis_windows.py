"""
키움증권 REST API 전체 기능 테스트 (Windows용)
실제 데이터가 들어오는지 확인
"""
import sys
from pathlib import Path

# Add parent directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from core.rest_client import KiwoomRESTClient
from api.account import AccountAPI
from api.market import MarketAPI
from api.order import OrderAPI
from research.data_fetcher import DataFetcher

def print_section(title):
    """섹션 제목 출력"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_account_apis():
    """계좌 API 테스트"""
    print_section("1. 계좌 API 테스트")

    try:
        client = KiwoomRESTClient()
        account_api = AccountAPI(client)

        # 1-1. 예수금 조회
        print("\n[1-1] 예수금 조회 테스트...")
        deposit = account_api.get_deposit()
        if deposit:
            print(f"✅ 성공!")
            print(f"   주문가능금액: {deposit.get('ord_alow_amt', 'N/A'):,}원")
            print(f"   출금가능금액: {deposit.get('pymn_alow_amt', 'N/A'):,}원")
        else:
            print(f"❌ 실패 - deposit이 None")

        # 1-2. 잔고 조회
        print("\n[1-2] 계좌 잔고 조회 테스트...")
        balance = account_api.get_balance()
        if balance:
            print(f"✅ 성공!")
            holdings = balance.get('acnt_evlt_remn_indv_tot', [])
            print(f"   보유 종목 수: {len(holdings)}개")
            if holdings:
                print(f"   첫 번째 종목: {holdings[0].get('stk_nm', 'N/A')}")
        else:
            print(f"❌ 실패 - balance가 None")

        # 1-3. 보유 종목 리스트
        print("\n[1-3] 보유 종목 리스트 테스트...")
        holdings = account_api.get_holdings()
        if holdings is not None:
            print(f"✅ 성공!")
            print(f"   보유 종목: {len(holdings)}개")
            for i, holding in enumerate(holdings[:3], 1):
                print(f"   {i}. {holding.get('stock_name', 'N/A')} ({holding.get('stock_code', 'N/A')}): {holding.get('quantity', 0)}주")
        else:
            print(f"❌ 실패 - holdings가 None")

        return True

    except Exception as e:
        print(f"❌ 계좌 API 테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_market_apis():
    """시장 API 테스트"""
    print_section("2. 시장 탐색 API 테스트")

    try:
        client = KiwoomRESTClient()
        fetcher = DataFetcher(client)

        # 2-1. 거래량 순위
        print("\n[2-1] 거래량 순위 조회 테스트...")
        volume_rank = fetcher.get_volume_rank(market='ALL', limit=5)
        if volume_rank:
            print(f"✅ 성공! {len(volume_rank)}개 조회")
            for i, stock in enumerate(volume_rank, 1):
                print(f"   {i}. {stock.get('stock_name', 'N/A')} ({stock.get('stock_code', 'N/A')})")
                print(f"      현재가: {stock.get('current_price', 0):,}원, 거래량: {stock.get('volume', 0):,}")
        else:
            print(f"❌ 실패 - 빈 리스트 또는 None")
            print(f"   반환값: {volume_rank}")

        # 2-2. 등락률 순위 (상승)
        print("\n[2-2] 등락률 상승 순위 조회 테스트...")
        rise_rank = fetcher.get_price_change_rank(market='ALL', sort='rise', limit=5)
        if rise_rank:
            print(f"✅ 성공! {len(rise_rank)}개 조회")
            for i, stock in enumerate(rise_rank, 1):
                print(f"   {i}. {stock.get('stock_name', 'N/A')} ({stock.get('stock_code', 'N/A')})")
                print(f"      등락률: {stock.get('change_rate', 0):+.2f}%")
        else:
            print(f"❌ 실패 - 빈 리스트 또는 None")

        # 2-3. 등락률 순위 (하락)
        print("\n[2-3] 등락률 하락 순위 조회 테스트...")
        fall_rank = fetcher.get_price_change_rank(market='ALL', sort='fall', limit=5)
        if fall_rank:
            print(f"✅ 성공! {len(fall_rank)}개 조회")
            for i, stock in enumerate(fall_rank, 1):
                print(f"   {i}. {stock.get('stock_name', 'N/A')} ({stock.get('stock_code', 'N/A')})")
                print(f"      등락률: {stock.get('change_rate', 0):+.2f}%")
        else:
            print(f"❌ 실패 - 빈 리스트 또는 None")

        # 2-4. 거래대금 순위
        print("\n[2-4] 거래대금 순위 조회 테스트...")
        value_rank = fetcher.get_trading_value_rank(market='ALL', limit=5)
        if value_rank:
            print(f"✅ 성공! {len(value_rank)}개 조회")
            for i, stock in enumerate(value_rank, 1):
                print(f"   {i}. {stock.get('stock_name', 'N/A')} ({stock.get('stock_code', 'N/A')})")
                print(f"      거래대금: {stock.get('trading_value', 0):,}원")
        else:
            print(f"❌ 실패 - 빈 리스트 또는 None")

        # 2-5. 현재가 조회 (삼성전자)
        print("\n[2-5] 현재가 조회 테스트 (삼성전자 005930)...")
        price = fetcher.get_current_price("005930")
        if price:
            print(f"✅ 성공!")
            print(f"   종목명: {price.get('stock_name', 'N/A')}")
            print(f"   현재가: {price.get('current_price', 0):,}원")
            print(f"   등락률: {price.get('change_rate', 0):+.2f}%")
            print(f"   거래량: {price.get('volume', 0):,}")
        else:
            print(f"❌ 실패 - None")

        return True

    except Exception as e:
        print(f"❌ 시장 API 테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_order_apis():
    """주문 API 테스트 (DRY RUN)"""
    print_section("3. 주문 API 테스트 (실제 주문 안함)")

    try:
        client = KiwoomRESTClient()
        order_api = OrderAPI(client)

        print("\n⚠️  실제 주문을 테스트하지 않습니다.")
        print("   OrderAPI 클래스가 정상적으로 초기화되었는지만 확인합니다.")

        # API 메서드가 존재하는지 확인
        has_buy = hasattr(order_api, 'place_buy_order')
        has_sell = hasattr(order_api, 'place_sell_order')
        has_cancel = hasattr(order_api, 'cancel_order')

        print(f"\n   매수 주문 메서드: {'✅ 존재' if has_buy else '❌ 없음'}")
        print(f"   매도 주문 메서드: {'✅ 존재' if has_sell else '❌ 없음'}")
        print(f"   주문 취소 메서드: {'✅ 존재' if has_cancel else '❌ 없음'}")

        return has_buy and has_sell and has_cancel

    except Exception as e:
        print(f"❌ 주문 API 테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """전체 테스트 실행"""
    print("\n" + "="*80)
    print("  키움증권 REST API 전체 기능 테스트 (Windows)")
    print("="*80)
    print("\n📌 실제 데이터가 제대로 들어오는지 확인합니다.\n")

    results = []

    # 1. 계좌 API
    success = test_account_apis()
    results.append(("계좌 API", success))

    # 2. 시장 API
    success = test_market_apis()
    results.append(("시장 탐색 API", success))

    # 3. 주문 API
    success = test_order_apis()
    results.append(("주문 API (구조)", success))

    # 결과 요약
    print_section("테스트 결과 요약")

    for test_name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{test_name:20s}: {status}")

    success_count = sum(1 for _, s in results if s)
    total_count = len(results)

    print(f"\n총 {total_count}개 중 {success_count}개 성공")

    if success_count == total_count:
        print("\n🎉 모든 테스트 통과!")
    else:
        print(f"\n⚠️  {total_count - success_count}개 테스트 실패")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()
