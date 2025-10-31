"""
test_trading.py
자동매매 시뮬레이션 테스트
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import logging
from core import KiwoomRESTClient
from api import AccountAPI, OrderAPI
from config.demo_stocks import get_demo_stock_list

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)


def test_trading_flow():
    """자동매매 플로우 테스트"""

    print("\n" + "="*60)
    print("자동매매 시뮬레이션 테스트".center(60))
    print("="*60 + "\n")

    # 1. API 초기화
    print("1️⃣ API 초기화...")
    client = KiwoomRESTClient()
    account_api = AccountAPI(client)
    order_api = OrderAPI(client, dry_run=True)  # DRY RUN 모드
    print("✅ API 초기화 완료\n")

    # 2. 계좌 정보 조회
    print("2️⃣ 계좌 정보 조회...")
    deposit = account_api.get_deposit()
    if deposit:
        cash = int(deposit.get('ord_alow_amt', 0))
        print(f"✅ 주문 가능 금액: {cash:,}원\n")
    else:
        print("❌ 계좌 조회 실패\n")
        cash = 0

    # 3. 데모 종목 리스트 조회
    print("3️⃣ 종목 리스트 조회...")
    stocks = get_demo_stock_list()
    print(f"✅ 종목 수: {len(stocks)}개")
    for stock in stocks[:5]:
        print(f"   - {stock['stock_name']} ({stock['stock_code']})")
    print()

    # 4. 매수 시뮬레이션
    print("4️⃣ 매수 시뮬레이션...")

    # 가상의 매수 조건: 첫 3개 종목을 매수
    buy_targets = stocks[:3]

    for stock in buy_targets:
        stock_code = stock['stock_code']
        stock_name = stock['stock_name']

        # 가상의 현재가 (실제로는 시세 API로 조회)
        price = 50000  # 임의의 가격

        # 매수 수량 계산 (가용 금액의 10%씩 투자)
        invest_amount = cash * 0.1
        quantity = int(invest_amount / price)

        if quantity > 0:
            result = order_api.buy(
                stock_code=stock_code,
                quantity=quantity,
                price=price
            )

            if result:
                print(f"   ✅ {stock_name} 매수: {quantity}주 @ {price:,}원")
        else:
            print(f"   ⚠️  {stock_name} 매수 불가 (수량 부족)")

    print()

    # 5. 시뮬레이션 주문 내역 확인
    print("5️⃣ 시뮬레이션 주문 내역...")
    orders = order_api.get_simulated_orders()
    print(f"총 {len(orders)}건의 시뮬레이션 주문")

    for order in orders:
        print(
            f"   - [{order['side'].upper()}] {order['stock_code']} "
            f"{order['quantity']}주 @ {order['price']:,}원 "
            f"(주문번호: {order['order_no']})"
        )

    print()

    # 6. 매도 시뮬레이션
    print("6️⃣ 매도 시뮬레이션...")

    # 첫 번째 매수 주문을 매도
    if orders:
        first_order = orders[0]
        sell_result = order_api.sell(
            stock_code=first_order['stock_code'],
            quantity=first_order['quantity'],
            price=first_order['price'] + 1000  # 1000원 이익
        )

        if sell_result:
            print(f"   ✅ 매도 완료: {sell_result['stock_code']}")

    print()

    # 7. 최종 주문 내역
    print("7️⃣ 최종 주문 내역...")
    final_orders = order_api.get_simulated_orders()
    print(f"총 {len(final_orders)}건의 주문")

    buy_count = sum(1 for o in final_orders if o['side'] == 'buy')
    sell_count = sum(1 for o in final_orders if o['side'] == 'sell')

    print(f"   - 매수: {buy_count}건")
    print(f"   - 매도: {sell_count}건")

    print("\n" + "="*60)
    print("✅ 시뮬레이션 테스트 완료!".center(60))
    print("="*60 + "\n")

    # 클라이언트 종료
    client.close()


if __name__ == '__main__':
    test_trading_flow()
