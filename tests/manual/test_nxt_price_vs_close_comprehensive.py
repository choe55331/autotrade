"""
NXT 종목 종가 vs 현재가 비교 테스트 (종합 버전)
=========================================

목적:
1. NXT 거래 가능 종목 10개 대상
2. 일반시장 종가와 NXT 현재가 비교
3. 5초 간격으로 10번 반복 테스트
4. 다양한 API 조합 시도하여 NXT 현재가 불러오는 조건 파악

테스트 시나리오:
- ka10003 (체결정보) - 기본 코드
- ka10003 (체결정보) - _NX 접미사
- ka10004 (호가) - 기본 코드
- ka10004 (호가) - _NX 접미사
- ka10001 (시세조회) - 기본 코드
- ka10001 (시세조회) - _NX 접미사
- ka10080 (분봉) - 실시간 가격 추출
- 웹소켓 실시간 체결가
"""
import sys
from pathlib import Path
from datetime import datetime
import time
import json
from typing import Dict, Any, List, Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
RESET = '\033[0m'


class NXTPriceTestSuite:
    """NXT 현재가 테스트 스위트"""

    def __init__(self, client):
        self.client = client
        self.test_results = []

    def test_ka10003_basic(self, stock_code: str) -> Optional[int]:
        """ka10003 API - 기본 코드 조회"""
        try:
            response = self.client.request(
                api_id="ka10003",
                body={"stk_cd": stock_code},
                path="stkinfo"
            )

            if response and response.get('return_code') == 0:
                cntr_infr = response.get('cntr_infr', [])
                if cntr_infr and len(cntr_infr) > 0:
                    latest = cntr_infr[0]
                    cur_prc = latest.get('cur_prc', '0')
                    price = abs(int(str(cur_prc).replace('+', '').replace('-', '').replace(',', '')))
                    return price
        except Exception as e:
            print(f"  {RED}[ERROR] ka10003_basic: {e}{RESET}")
        return None

    def test_ka10003_nx(self, stock_code: str) -> Optional[int]:
        """ka10003 API - _NX 접미사"""
        try:
            nx_code = f"{stock_code}_NX" if not stock_code.endswith('_NX') else stock_code
            response = self.client.request(
                api_id="ka10003",
                body={"stk_cd": nx_code},
                path="stkinfo"
            )

            if response and response.get('return_code') == 0:
                cntr_infr = response.get('cntr_infr', [])
                if cntr_infr and len(cntr_infr) > 0:
                    latest = cntr_infr[0]
                    cur_prc = latest.get('cur_prc', '0')
                    price = abs(int(str(cur_prc).replace('+', '').replace('-', '').replace(',', '')))
                    return price
        except Exception as e:
            print(f"  {RED}[ERROR] ka10003_nx: {e}{RESET}")
        return None

    def test_ka10004_basic(self, stock_code: str) -> Optional[int]:
        """ka10004 API - 기본 코드 호가"""
        try:
            response = self.client.request(
                api_id="ka10004",
                body={"stk_cd": stock_code},
                path="mrkcond"
            )

            if response and response.get('return_code') == 0:
                sel_fpr_bid = response.get('sel_fpr_bid', '0').replace('+', '').replace('-', '')
                buy_fpr_bid = response.get('buy_fpr_bid', '0').replace('+', '').replace('-', '')

                sell_price = abs(int(sel_fpr_bid)) if sel_fpr_bid and sel_fpr_bid != '0' else 0
                buy_price = abs(int(buy_fpr_bid)) if buy_fpr_bid and buy_fpr_bid != '0' else 0

                if sell_price > 0 and buy_price > 0:
                    return (sell_price + buy_price) // 2
                elif sell_price > 0:
                    return sell_price
                elif buy_price > 0:
                    return buy_price
        except Exception as e:
            print(f"  {RED}[ERROR] ka10004_basic: {e}{RESET}")
        return None

    def test_ka10004_nx(self, stock_code: str) -> Optional[int]:
        """ka10004 API - _NX 접미사 호가"""
        try:
            nx_code = f"{stock_code}_NX" if not stock_code.endswith('_NX') else stock_code
            response = self.client.request(
                api_id="ka10004",
                body={"stk_cd": nx_code},
                path="mrkcond"
            )

            if response and response.get('return_code') == 0:
                sel_fpr_bid = response.get('sel_fpr_bid', '0').replace('+', '').replace('-', '')
                buy_fpr_bid = response.get('buy_fpr_bid', '0').replace('+', '').replace('-', '')

                sell_price = abs(int(sel_fpr_bid)) if sel_fpr_bid and sel_fpr_bid != '0' else 0
                buy_price = abs(int(buy_fpr_bid)) if buy_fpr_bid and buy_fpr_bid != '0' else 0

                if sell_price > 0 and buy_price > 0:
                    return (sell_price + buy_price) // 2
                elif sell_price > 0:
                    return sell_price
                elif buy_price > 0:
                    return buy_price
        except Exception as e:
            print(f"  {RED}[ERROR] ka10004_nx: {e}{RESET}")
        return None

    def test_ka10001_basic(self, stock_code: str) -> Optional[int]:
        """ka10001 API - 기본 코드 시세"""
        try:
            response = self.client.request(
                api_id="ka10001",
                body={"stk_cd": stock_code},
                path="stkinfo"
            )

            if response and response.get('return_code') == 0:
                price_fields = ['cur_prc', 'crnt_pric', 'stk_pric', 'now_pric', 'current_price']
                for field in price_fields:
                    if field in response:
                        price = abs(int(str(response[field]).replace('+', '').replace('-', '').replace(',', '')))
                        return price
        except Exception as e:
            print(f"  {RED}[ERROR] ka10001_basic: {e}{RESET}")
        return None

    def test_ka10001_nx(self, stock_code: str) -> Optional[int]:
        """ka10001 API - _NX 접미사 시세"""
        try:
            nx_code = f"{stock_code}_NX" if not stock_code.endswith('_NX') else stock_code
            response = self.client.request(
                api_id="ka10001",
                body={"stk_cd": nx_code},
                path="stkinfo"
            )

            if response and response.get('return_code') == 0:
                price_fields = ['cur_prc', 'crnt_pric', 'stk_pric', 'now_pric', 'current_price']
                for field in price_fields:
                    if field in response:
                        price = abs(int(str(response[field]).replace('+', '').replace('-', '').replace(',', '')))
                        return price
        except Exception as e:
            print(f"  {RED}[ERROR] ka10001_nx: {e}{RESET}")
        return None

    def test_ka10080_minute(self, stock_code: str) -> Optional[int]:
        """ka10080 API - 1분봉 마지막 종가"""
        try:
            response = self.client.request(
                api_id="ka10080",
                body={
                    "stk_cd": stock_code,
                    "tic_scope": "1",
                    "upd_stkpc_tp": "1"
                },
                path="chart"
            )

            if response and response.get('return_code') == 0:
                minute_data = response.get('stk_tic_pole_chart_qry', [])
                if minute_data and len(minute_data) > 0:
                    latest = minute_data[0]
                    close_price = int(latest.get('cur_prc', 0))
                    return close_price
        except Exception as e:
            print(f"  {RED}[ERROR] ka10080_minute: {e}{RESET}")
        return None

    def get_daily_close(self, stock_code: str) -> Optional[int]:
        """일봉 차트에서 종가 가져오기"""
        try:
            response = self.client.request(
                api_id="ka10081",
                body={
                    "stk_cd": stock_code,
                    "base_dt": datetime.now().strftime('%Y%m%d'),
                    "upd_stkpc_tp": "1"
                },
                path="chart"
            )

            if response and response.get('return_code') == 0:
                daily_data = response.get('stk_dt_pole_chart_qry', [])
                if daily_data and len(daily_data) > 0:
                    latest = daily_data[0]
                    close_price = int(latest.get('cur_prc', 0))
                    return close_price
        except Exception as e:
            print(f"  {RED}[ERROR] get_daily_close: {e}{RESET}")
        return None

    def run_comprehensive_test(self, stock_code: str, stock_name: str, iteration: int):
        """종합 테스트 실행"""
        print(f"\n{CYAN}{'='*100}{RESET}")
        print(f"{CYAN}[테스트 #{iteration}] {stock_name} ({stock_code}) - {datetime.now().strftime('%H:%M:%S')}{RESET}")
        print(f"{CYAN}{'='*100}{RESET}")

        # 일반 시장 종가
        close_price = self.get_daily_close(stock_code)
        print(f"{WHITE}📊 일반시장 종가: {close_price:,}원{RESET}" if close_price else f"{YELLOW}📊 종가 조회 실패{RESET}")

        # 다양한 API 시도
        results = {
            'ka10003_basic': self.test_ka10003_basic(stock_code),
            'ka10003_nx': self.test_ka10003_nx(stock_code),
            'ka10004_basic': self.test_ka10004_basic(stock_code),
            'ka10004_nx': self.test_ka10004_nx(stock_code),
            'ka10001_basic': self.test_ka10001_basic(stock_code),
            'ka10001_nx': self.test_ka10001_nx(stock_code),
            'ka10080_minute': self.test_ka10080_minute(stock_code),
        }

        # 결과 출력
        print(f"\n{WHITE}{'API 테스트 결과':<30} {'가격':>15} {'종가 비교':>15} {'상태':>15}{RESET}")
        print(f"{WHITE}{'-'*75}{RESET}")

        for api_name, price in results.items():
            if price:
                diff = price - close_price if close_price else 0
                diff_pct = (diff / close_price * 100) if close_price and close_price > 0 else 0

                if abs(diff) < 10:  # 거의 같음
                    status = f"{YELLOW}종가와 동일{RESET}"
                    color = YELLOW
                elif diff > 0:  # 현재가가 더 높음
                    status = f"{GREEN}NXT 현재가!{RESET}"
                    color = GREEN
                else:
                    status = f"{RED}더 낮음{RESET}"
                    color = RED

                print(f"{color}{api_name:<30} {price:>15,}원 {diff:>+13,}원 ({diff_pct:+.2f}%) {status}{RESET}")
            else:
                print(f"{RED}{api_name:<30} {'조회 실패':>15} {'-':>15} {'FAILED':>15}{RESET}")

        # 결과 저장
        test_record = {
            'iteration': iteration,
            'timestamp': datetime.now().isoformat(),
            'stock_code': stock_code,
            'stock_name': stock_name,
            'close_price': close_price,
            'results': results
        }
        self.test_results.append(test_record)

        # 결론 도출
        print(f"\n{MAGENTA}{'='*100}{RESET}")
        print(f"{MAGENTA}💡 분석 결과{RESET}")
        print(f"{MAGENTA}{'='*100}{RESET}")

        if close_price:
            nxt_apis = []
            close_apis = []

            for api_name, price in results.items():
                if price:
                    diff = abs(price - close_price)
                    if diff < 10:
                        close_apis.append(api_name)
                    else:
                        nxt_apis.append(api_name)

            if nxt_apis:
                print(f"{GREEN}✓ NXT 현재가를 불러오는 것으로 보이는 API:{RESET}")
                for api in nxt_apis:
                    print(f"  - {api}: {results[api]:,}원")

            if close_apis:
                print(f"\n{YELLOW}✓ 종가를 반환하는 API:{RESET}")
                for api in close_apis:
                    print(f"  - {api}: {results[api]:,}원")

        print(f"{MAGENTA}{'='*100}{RESET}\n")


def main():
    """메인 테스트 실행"""
    print(f"\n{BLUE}{'='*100}{RESET}")
    print(f"{BLUE}NXT 종목 종가 vs 현재가 비교 테스트 (종합 버전){RESET}")
    print(f"{BLUE}{'='*100}{RESET}")

    try:
        from core.rest_client import KiwoomRESTClient
        from utils.trading_date import is_nxt_hours

        client = KiwoomRESTClient()

        if not client.token:
            print(f"{RED}[X] API 연결 실패{RESET}")
            return

        print(f"{GREEN}[OK] API 연결 성공{RESET}")

        # NXT 거래 시간 확인
        is_nxt = is_nxt_hours()
        print(f"\n{CYAN}📅 현재 시간 정보{RESET}")
        print(f"  시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  NXT 거래 시간: {'✅ 예 (08:00-09:00 또는 15:30-20:00)' if is_nxt else '❌ 아니오'}")

        if not is_nxt:
            print(f"\n{YELLOW}⚠️  현재 NXT 거래 시간이 아닙니다.{RESET}")
            print(f"{YELLOW}   이 테스트는 NXT 시간대(08:00-09:00 또는 15:30-20:00)에 실행해야 의미있는 결과를 얻을 수 있습니다.{RESET}")
            print(f"{YELLOW}   그래도 계속 진행하시겠습니까? (y/n): {RESET}", end='')
            response = input().strip().lower()
            if response != 'y':
                print(f"{YELLOW}테스트를 중단합니다.{RESET}")
                return

        # 테스트할 NXT 종목 (실제 NXT 거래 가능 종목으로 수정 필요)
        test_stocks = [
            ("249420", "일동제약"),
            ("052020", "에프엔에스테크"),
            ("215600", "신라젠"),
            ("950140", "잉글우드랩"),
            ("140410", "메지온"),
            ("900140", "엘브이엠씨홀딩스"),
            ("241710", "코스맥스비티아이"),
            ("160600", "이큐셀"),
            ("215200", "메가스터디교육"),
            ("256840", "한국팩키지"),
        ]

        # 테스트 스위트 초기화
        test_suite = NXTPriceTestSuite(client)

        # 10개 종목 * 10회 반복
        for iteration in range(1, 11):
            print(f"\n{BLUE}{'='*100}{RESET}")
            print(f"{BLUE}테스트 반복 #{iteration}/10{RESET}")
            print(f"{BLUE}{'='*100}{RESET}")

            for stock_code, stock_name in test_stocks:
                test_suite.run_comprehensive_test(stock_code, stock_name, iteration)
                time.sleep(0.5)  # API 호출 제한 고려

            if iteration < 10:
                print(f"\n{CYAN}⏳ 다음 테스트까지 5초 대기...{RESET}")
                time.sleep(5)

        # 최종 요약
        print(f"\n{MAGENTA}{'='*100}{RESET}")
        print(f"{MAGENTA}📊 테스트 요약{RESET}")
        print(f"{MAGENTA}{'='*100}{RESET}")

        # 결과 파일 저장
        output_file = project_root / 'tests' / 'manual' / 'results' / f'nxt_price_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_suite.test_results, f, indent=2, ensure_ascii=False)

        print(f"{GREEN}✓ 테스트 결과 저장: {output_file}{RESET}")

        # API별 성공률 계산
        api_success_rates = {}
        for record in test_suite.test_results:
            for api_name, price in record['results'].items():
                if api_name not in api_success_rates:
                    api_success_rates[api_name] = {'success': 0, 'total': 0}
                api_success_rates[api_name]['total'] += 1
                if price is not None:
                    api_success_rates[api_name]['success'] += 1

        print(f"\n{WHITE}{'API':<30} {'성공률':>15} {'성공/전체':>15}{RESET}")
        print(f"{WHITE}{'-'*60}{RESET}")
        for api_name, stats in sorted(api_success_rates.items(), key=lambda x: x[1]['success']/x[1]['total'] if x[1]['total'] > 0 else 0, reverse=True):
            success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            color = GREEN if success_rate >= 80 else YELLOW if success_rate >= 50 else RED
            print(f"{color}{api_name:<30} {success_rate:>14.1f}% {stats['success']:>7}/{stats['total']:<7}{RESET}")

        print(f"\n{GREEN}✅ 테스트 완료!{RESET}")

    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠️  사용자에 의해 중단됨{RESET}")
    except Exception as e:
        print(f"{RED}[X] 오류 발생: {e}{RESET}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
