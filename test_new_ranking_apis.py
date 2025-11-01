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
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.rest_client import KiwoomRESTClient
from api.market import MarketAPI


class TeeOutput:
    """화면과 파일에 동시 출력하는 클래스"""
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()
        sys.stdout = self.terminal


def print_header(title):
    """헤더 출력"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_trading_value_rank(market_api):
    """거래대금 상위 테스트"""
    print_header("1. 거래대금 상위 (ka10032)")

    print("\n테스트: KOSPI 거래대금 상위 10개")

    try:
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
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_volume_surge_rank(market_api):
    """거래량 급증 테스트"""
    print_header("2. 거래량 급증 (ka10023)")

    print("\n테스트: 전체 시장 거래량 급증 10개")

    try:
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
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_intraday_change_rank(market_api):
    """시가대비 등락률 테스트"""
    print_header("3. 시가대비 등락률 (ka10028)")

    print("\n테스트: KOSDAQ 시가대비 상승률 10개")

    try:
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
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def main():
    """메인 함수"""
    # 결과 파일 경로 설정
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Path(__file__).parent / f"test_ranking_apis_{timestamp}.txt"

    # 화면과 파일에 동시 출력
    tee = TeeOutput(log_file)
    sys.stdout = tee

    try:
        print("=" * 80)
        print("  새로 추가한 Ranking API 테스트")
        print("=" * 80)
        print(f"테스트 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"결과 저장: {log_file}")
        print()

        # 클라이언트 초기화
        print("\n초기화 중...")
        try:
            client = KiwoomRESTClient()
            market_api = MarketAPI(client)
            print("✅ 초기화 완료\n")
        except Exception as e:
            print(f"❌ 초기화 실패: {e}")
            import traceback
            print(traceback.format_exc())
            return 1

        # 테스트 실행
        results = []

        # 기본 ranking
        results.append(("거래대금상위", test_trading_value_rank(market_api)))
        results.append(("거래량급증", test_volume_surge_rank(market_api)))
        results.append(("시가대비등락률", test_intraday_change_rank(market_api)))

        # 외국인/기관 매매 (추가)
        print_header("4. 외국인 5일 순매수 (ka10034)")
        try:
            result = market_api.get_foreign_period_trading_rank(market='KOSPI', period_days=5, limit=5)
            if result and len(result) > 0:
                print(f"✅ {len(result)}개 조회")
                results.append(("외국인5일매매", True))
            else:
                print("❌ 데이터 없음")
                results.append(("외국인5일매매", False))
        except Exception as e:
            print(f"❌ 에러 발생: {e}")
            import traceback
            print(traceback.format_exc())
            results.append(("외국인5일매매", False))

        print_header("5. 외국인/기관 매매상위 (ka90009)")
        try:
            result = market_api.get_foreign_institution_trading_rank(market='KOSPI', limit=5)
            if result and len(result) > 0:
                print(f"✅ {len(result)}개 조회")
                results.append(("외국인기관매매", True))
            else:
                print("❌ 데이터 없음")
                results.append(("외국인기관매매", False))
        except Exception as e:
            print(f"❌ 에러 발생: {e}")
            import traceback
            print(traceback.format_exc())
            results.append(("외국인기관매매", False))

        print_header("6. 장중 투자자별 매매 (ka10065)")
        try:
            result = market_api.get_investor_intraday_trading_rank(market='KOSPI', investor_type='foreign', limit=5)
            if result and len(result) > 0:
                print(f"✅ {len(result)}개 조회")
                results.append(("투자자별매매", True))
            else:
                print("❌ 데이터 없음")
                results.append(("투자자별매매", False))
        except Exception as e:
            print(f"❌ 에러 발생: {e}")
            import traceback
            print(traceback.format_exc())
            results.append(("투자자별매매", False))

        print_header("7. 신용비율 상위 (ka10033)")
        try:
            result = market_api.get_credit_ratio_rank(market='KOSPI', limit=5)
            if result and len(result) > 0:
                print(f"✅ {len(result)}개 조회")
                results.append(("신용비율", True))
            else:
                print("❌ 데이터 없음")
                results.append(("신용비율", False))
        except Exception as e:
            print(f"❌ 에러 발생: {e}")
            import traceback
            print(traceback.format_exc())
            results.append(("신용비율", False))

        # 결과 요약
        print_header("테스트 결과 요약")

        success_count = sum(1 for _, success in results if success)
        total_count = len(results)

        for name, success in results:
            status = "✅ 성공" if success else "❌ 실패"
            print(f"{name:<20} {status}")

        print(f"\n전체: {success_count}/{total_count} 성공")
        print(f"\n테스트 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"결과 파일: {log_file}")

        if success_count == total_count:
            print("\n🎉 모든 API가 정상 작동합니다!")
            return_code = 0
        else:
            print(f"\n⚠️  {total_count - success_count}개 API 실패")
            return_code = 1

        return return_code

    finally:
        # 파일 닫기
        tee.close()


if __name__ == '__main__':
    sys.exit(main())
