#!/usr/bin/env python3
"""
새로 추가한 ranking API 테스트 스크립트

테스트 대상:
- get_trading_value_rank (거래대금상위)
- get_volume_surge_rank (거래량급증)
- get_intraday_change_rank (시가대비등락률)

목적: 실제 데이터를 받아오는지 확인
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.rest_client import KiwoomRESTClient
from api.market import MarketAPI


def print_header(title):
    """헤더 출력"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_trading_value_rank(market_api):
    """거래대금 상위 테스트"""
    print_header("1. 거래대금 상위 (ka10032)")

    print("\n테스트: KOSPI 거래대금 상위 10개")
    result = market_api.get_trading_value_rank(market='KOSPI', limit=10)

    if result:
        print(f"✅ 성공! {len(result)}개 종목 조회")
        print("\n상위 5개:")
        print(f"{'순위':<6}{'종목명':<20}{'현재가':>12}{'거래대금':>15}{'거래량':>15}")
        print("-" * 80)

        for i, item in enumerate(result[:5], 1):
            print(f"{i:<6}{item['name']:<20}{item['price']:>12,}원 "
                  f"{item['trading_value']:>14,}원 {item['volume']:>14,}")

        return True
    else:
        print("❌ 실패: 데이터 없음")
        return False


def test_volume_surge_rank(market_api):
    """거래량 급증 테스트"""
    print_header("2. 거래량 급증 (ka10023)")

    print("\n테스트: 전체 시장 거래량 급증 10개")
    result = market_api.get_volume_surge_rank(market='ALL', limit=10, time_interval=5)

    if result:
        print(f"✅ 성공! {len(result)}개 종목 조회")
        print("\n상위 5개:")
        print(f"{'순위':<6}{'종목명':<20}{'현재가':>12}{'거래량증가율':>12}{'등락률':>10}")
        print("-" * 80)

        for i, item in enumerate(result[:5], 1):
            print(f"{i:<6}{item['name']:<20}{item['price']:>12,}원 "
                  f"{item.get('volume_increase_rate', 0):>11.2f}% "
                  f"{item.get('change_rate', 0):>9.2f}%")

        return True
    else:
        print("❌ 실패: 데이터 없음")
        return False


def test_intraday_change_rank(market_api):
    """시가대비 등락률 테스트"""
    print_header("3. 시가대비 등락률 (ka10028)")

    print("\n테스트: KOSDAQ 시가대비 상승률 10개")
    result = market_api.get_intraday_change_rank(market='KOSDAQ', sort='rise', limit=10)

    if result:
        print(f"✅ 성공! {len(result)}개 종목 조회")
        print("\n상위 5개:")
        print(f"{'순위':<6}{'종목명':<20}{'현재가':>12}{'시가':>12}{'시가대비등락률':>15}")
        print("-" * 80)

        for i, item in enumerate(result[:5], 1):
            print(f"{i:<6}{item['name']:<20}{item['price']:>12,}원 "
                  f"{item.get('open_price', 0):>12,}원 "
                  f"{item.get('intraday_change_rate', 0):>14.2f}%")

        return True
    else:
        print("❌ 실패: 데이터 없음")
        return False


def main():
    """메인 함수"""
    print("=" * 80)
    print("  새로 추가한 Ranking API 테스트")
    print("=" * 80)

    # 클라이언트 초기화
    print("\n초기화 중...")
    try:
        client = KiwoomRESTClient()
        market_api = MarketAPI(client)
        print("✅ 초기화 완료\n")
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        return 1

    # 테스트 실행
    results = []

    results.append(("거래대금상위", test_trading_value_rank(market_api)))
    results.append(("거래량급증", test_volume_surge_rank(market_api)))
    results.append(("시가대비등락률", test_intraday_change_rank(market_api)))

    # 결과 요약
    print_header("테스트 결과 요약")

    success_count = sum(1 for _, success in results if success)
    total_count = len(results)

    for name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{name:<20} {status}")

    print(f"\n전체: {success_count}/{total_count} 성공")

    if success_count == total_count:
        print("\n🎉 모든 API가 정상 작동합니다!")
        return 0
    else:
        print(f"\n⚠️  {total_count - success_count}개 API 실패")
        return 1


if __name__ == '__main__':
    sys.exit(main())
