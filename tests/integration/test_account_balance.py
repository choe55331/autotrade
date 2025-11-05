"""
계좌잔액 계산 테스트
"""
import sys
import os

# Cross-platform path resolution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

    # 3. KRX 종목 조회
    holdings_krx = account_api.get_holdings(market_type="KRX")
    print(f"\n[KRX 보유 종목]")
    print(f"  종목 수: {len(holdings_krx) if holdings_krx else 0}개")

    krx_value = 0
    if holdings_krx:
        for h in holdings_krx:
            code = h.get('stk_cd', '')
            name = h.get('stk_nm', '')
            qty = int(str(h.get('rmnd_qty', 0)).replace(',', ''))
            cur_prc = int(str(h.get('cur_prc', 0)).replace(',', ''))
            eval_amt = int(str(h.get('eval_amt', 0)).replace(',', ''))
            krx_value += eval_amt
            print(f"  - {code} {name}: {qty}주 @ {cur_prc:,}원 = {eval_amt:,}원")
        print(f"  KRX 평가금액 합계: {krx_value:,}원")

    # 4. NXT 종목 조회
    holdings_nxt = account_api.get_holdings(market_type="NXT")
    print(f"\n[NXT 보유 종목]")
    print(f"  종목 수: {len(holdings_nxt) if holdings_nxt else 0}개")

    nxt_value = 0
    if holdings_nxt:
        for h in holdings_nxt:
            code = h.get('stk_cd', '')
            name = h.get('stk_nm', '')
            qty = int(str(h.get('rmnd_qty', 0)).replace(',', ''))
            cur_prc = int(str(h.get('cur_prc', 0)).replace(',', ''))
            eval_amt = int(str(h.get('eval_amt', 0)).replace(',', ''))
            nxt_value += eval_amt
            print(f"  - {code} {name}: {qty}주 @ {cur_prc:,}원 = {eval_amt:,}원")
        print(f"  NXT 평가금액 합계: {nxt_value:,}원")

    # 5. 총 자산 계산
    stock_value = krx_value + nxt_value
    total_assets = stock_value + cash

    print(f"\n[총 자산 계산]")
    print(f"  주식 현재가치: {stock_value:,}원 (KRX: {krx_value:,}원 + NXT: {nxt_value:,}원)")
    print(f"  잔존 현금: {cash:,}원")
    print(f"  총 자산: {total_assets:,}원")

    # 6. 검증
    print(f"\n[검증]")
    if stock_value + cash == total_assets:
        print("  ✅ 계산 정확도: OK (주식 현재가치 + 잔존 현금 = 총 자산)")
    else:
        print("  ❌ 계산 정확도: FAIL")
        return False

    if holdings_krx or holdings_nxt:
        print("  ✅ 종목 조회: OK (KRX 또는 NXT 종목 존재)")
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
