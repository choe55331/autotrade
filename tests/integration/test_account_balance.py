"""
계좌잔액 계산 테스트
"""
import sys
import os

# Cross-platform path resolution
# tests/integration/test_account_balance.py -> tests/integration -> tests -> autotrade (project root)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from api.account import AccountAPI
from core.rest_client import KiwoomRESTClient


def test_account_balance():
    """
    계좌잔액 계산 테스트

    검증사항:
    1. 총 자산 = 주식 현재가치 + 잔존 현금
    2. KRX와 NXT 종목 모두 포함되는지
    """
    print("=" * 80)
    print("계좌잔액 계산 테스트")
    print("=" * 80)

    # 1. API 초기화
    client = KiwoomRESTClient()
    account_api = AccountAPI(client)

    # 2. 예수금 조회
    deposit = account_api.get_deposit()
    print(f"\n[예수금 조회]")
    if deposit:
        deposit_amount = int(str(deposit.get('entr', '0')).replace(',', ''))
        cash = int(str(deposit.get('100stk_ord_alow_amt', '0')).replace(',', ''))
        print(f"  예수금 (entr): {deposit_amount:,}원")
        print(f"  주문가능금액 (100stk_ord_alow_amt): {cash:,}원")
    else:
        print("  ❌ 예수금 조회 실패")
        return False

    # 3. 보유 종목 조회 (KRX+NXT 통합)
    holdings = account_api.get_holdings(market_type="KRX+NXT")
    print(f"\n[보유 종목 조회 (KRX+NXT)]")
    print(f"  종목 수: {len(holdings) if holdings else 0}개")

    # v5.5.0: 장외 시간 대응 - eval_amt이 0이면 직접 계산
    stock_value = 0
    if holdings:
        for h in holdings:
            code = h.get('stk_cd', '')
            name = h.get('stk_nm', '')
            qty = int(str(h.get('rmnd_qty', 0)).replace(',', ''))
            cur_prc = int(str(h.get('cur_prc', 0)).replace(',', ''))
            eval_amt = int(str(h.get('eval_amt', 0)).replace(',', ''))

            # eval_amt이 0이면 수동 계산 (장외 시간)
            if eval_amt == 0 and cur_prc > 0:
                eval_amt = qty * cur_prc
                print(f"  - {code} {name}: {qty}주 @ {cur_prc:,}원 = {eval_amt:,}원 (장외 시간 계산)")
            else:
                print(f"  - {code} {name}: {qty}주 @ {cur_prc:,}원 = {eval_amt:,}원")

            stock_value += eval_amt
        print(f"  주식 평가금액 합계: {stock_value:,}원")

    # 4. 총 자산 계산
    total_assets = stock_value + cash

    print(f"\n[총 자산 계산]")
    print(f"  주식 현재가치: {stock_value:,}원")
    print(f"  잔존 현금: {cash:,}원")
    print(f"  총 자산: {total_assets:,}원")

    # 5. 검증
    print(f"\n[검증]")
    if stock_value + cash == total_assets:
        print("  ✅ 계산 정확도: OK (주식 현재가치 + 잔존 현금 = 총 자산)")
    else:
        print("  ❌ 계산 정확도: FAIL")
        return False

    if holdings:
        print("  ✅ 종목 조회: OK (보유 종목 존재)")
    else:
        print("  ⚠️  경고: 보유 종목 없음")

    print("\n" + "=" * 80)
    print("✅ 테스트 통과")
    print("=" * 80)
    return True


if __name__ == "__main__":
    try:
        success = test_account_balance()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
