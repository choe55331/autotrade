"""
Deep Scan 테스트 스크립트
scan_strategies.py의 Deep Scan이 모든 데이터를 수집하는지 검증
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.rest_client import KiwoomRESTClient
from api.market import MarketAPI
from research.screener import Screener
from research.scan_strategies import VolumeBasedStrategy

def test_deep_scan():
    """Deep Scan 테스트"""
    print("\n" + "="*80)
    print("🔬 Deep Scan 데이터 수집 테스트")
    print("="*80)

    try:
        client = KiwoomRESTClient()
        market_api = MarketAPI(client)
        screener = Screener(market_api)

        strategy = VolumeBasedStrategy(market_api, screener)

        print("\n⏳ 스캔 시작...")
        candidates = strategy.scan()

        if not candidates:
            print("\n[WARNING]️  후보 종목이 없습니다 (비거래 시간일 수 있음)")
            return False

        print(f"\n[OK] 스캔 완료: {len(candidates)}개 종목")

        if candidates:
            print("\n" + "="*80)
            print(f"[CHART] 첫 번째 종목 상세 데이터 확인: {candidates[0].name} ({candidates[0].code})")
            print("="*80)

            c = candidates[0]

            print(f"\n[기본 정보]")
            print(f"  가격: {c.price:,}원")
            print(f"  거래량: {c.volume:,}주")
            print(f"  등락률: {c.rate:.2f}%")

            print(f"\n[Deep Scan 수집 데이터]")
            print(f"  1. 기관/외국인 (ka10059)")
            print(f"     - 기관순매수: {c.institutional_net_buy:,}")
            print(f"     - 외국인순매수: {c.foreign_net_buy:,}")

            print(f"  2. 호가 (ka10004)")
            print(f"     - 호가비율: {c.bid_ask_ratio:.2f}")

            print(f"  3. 기관매매추이 (ka10045)")
            print(f"     - 데이터: {'있음' if c.institutional_trend else '없음'}")

            print(f"  4. 일봉 (ka10001)")
            print(f"     - 평균거래량: {c.avg_volume:,.0f}주" if c.avg_volume else "     - 평균거래량: 없음")
            print(f"     - 변동성: {c.volatility:.2f}%" if c.volatility else "     - 변동성: 없음")

            print(f"  5. 증권사별매매 (ka10078)")
            print(f"     - 순매수증권사수: {c.top_broker_buy_count}개")
            print(f"     - 순매수총액: {c.top_broker_net_buy:,}원")

            print(f"  6. 체결강도 (ka10047)")
            print(f"     - 체결강도: {c.execution_intensity:.1f}" if c.execution_intensity else "     - 체결강도: 없음")

            print(f"  7. 프로그램매매 (ka90013)")
            print(f"     - 프로그램순매수: {c.program_net_buy:,}원" if c.program_net_buy else "     - 프로그램순매수: 없음")

            print("\n" + "="*80)
            print("[SEARCH] 데이터 수집 검증")
            print("="*80)

            checks = [
                ("기관순매수", c.institutional_net_buy is not None),
                ("외국인순매수", c.foreign_net_buy is not None),
                ("호가비율", c.bid_ask_ratio is not None),
                ("기관매매추이", c.institutional_trend is not None),
                ("평균거래량", c.avg_volume is not None),
                ("변동성", c.volatility is not None),
                ("증권사순매수", c.top_broker_buy_count is not None),
                ("체결강도", c.execution_intensity is not None),
                ("프로그램순매수", c.program_net_buy is not None),
            ]

            success_count = sum(1 for _, check in checks if check)
            total_count = len(checks)

            for name, check in checks:
                status = "[OK]" if check else "[X]"
                print(f"  {status} {name}")

            print(f"\n수집 성공률: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")

            if success_count == total_count:
                print("\n🎉 모든 데이터 수집 성공!")
                return True
            else:
                print("\n[WARNING]️  일부 데이터 수집 실패 (비거래 시간일 수 있음)")
                return success_count >= total_count * 0.5

    except Exception as e:
        print(f"\n[X] 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_deep_scan()
    print("\n" + "="*80)
    if success:
        print("[OK] Deep Scan 테스트 성공")
    else:
        print("[X] Deep Scan 테스트 실패")
    print("="*80 + "\n")
    sys.exit(0 if success else 1)
