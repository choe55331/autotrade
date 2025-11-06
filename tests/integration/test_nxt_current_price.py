"""
NXT 현재가 조회 테스트
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from datetime import datetime
from api.account import AccountAPI
from core.rest_client import KiwoomRESTClient


def test_nxt_current_price():
    """
    NXT 현재가 조회 테스트

    검증사항:
    1. NXT 시장 종목의 현재가가 조회되는지
    2. cur_prc 필드가 0이 아닌 실제 값인지
    """
    print("=" * 80)
    print("NXT 현재가 조회 테스트")
    print("=" * 80)

    now = datetime.now()
    print(f"\n[현재 시간]")
    print(f"  {now.strftime('%Y-%m-%d %H:%M:%S')}")

    nxt_open_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
    nxt_close_time = now.replace(hour=15, minute=30, second=0, microsecond=0)

    is_nxt_time = nxt_open_time <= now <= nxt_close_time
    print(f"  NXT 장 시간: {'✅ 예 (09:00-15:30)' if is_nxt_time else '❌ 아니오 (장외 시간)'}")

    client = KiwoomRESTClient()
    account_api = AccountAPI(client)

    holdings = account_api.get_holdings(market_type="KRX+NXT")
    print(f"\n[보유 종목 조회 (KRX+NXT)]")
    print(f"  종목 수: {len(holdings) if holdings else 0}개")

    if not holdings:
        print("\n⚠️  경고: 보유 종목이 없습니다.")
        print("  - 종목을 보유하고 있어야 테스트를 진행할 수 있습니다.")
        return True

    print(f"\n[종목 현재가]")
    all_prices_valid = True

    for h in holdings:
        code = h.get('stk_cd', '')
        name = h.get('stk_nm', '')
        qty = int(str(h.get('rmnd_qty', 0)).replace(',', ''))
        avg_prc = int(str(h.get('avg_prc', 0)).replace(',', ''))
        cur_prc = int(str(h.get('cur_prc', 0)).replace(',', ''))
        eval_amt = int(str(h.get('eval_amt', 0)).replace(',', ''))

        if eval_amt == 0 and cur_prc > 0:
            eval_amt = qty * cur_prc
            market_hours_note = " (장외 시간 계산)"
        else:
            market_hours_note = ""

        if cur_prc > 0:
            status = "✅"
        else:
            status = "❌"
            all_prices_valid = False

        print(f"  {status} {code} {name}:")
        print(f"      수량: {qty}주")
        print(f"      평균단가: {avg_prc:,}원")
        print(f"      현재가: {cur_prc:,}원")
        print(f"      평가금액: {eval_amt:,}원{market_hours_note}")

    print(f"\n[검증 결과]")
    if all_prices_valid:
        print("  ✅ 모든 종목의 현재가가 정상 조회됨")
    else:
        print("  ❌ 일부 종목의 현재가가 0원 또는 조회 안됨")
        print("  - 장외 시간일 수 있습니다. (09:00-15:30 장중에 테스트하세요)")
        if not is_nxt_time:
            print("  - 현재는 장외 시간입니다.")

    print("\n" + "=" * 80)
    if all_prices_valid:
        print("✅ 테스트 통과")
    else:
        print("⚠️  현재가 조회 실패 (장외 시간일 수 있음)")
    print("=" * 80)

    return all_prices_valid


if __name__ == "__main__":
    try:
        success = test_nxt_current_price()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
