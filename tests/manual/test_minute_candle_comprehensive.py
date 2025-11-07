"""
종목 분봉 데이터 불러오기 종합 테스트
====================================

목적:
1. 종목의 분봉(1분, 3분, 5분, 15분, 30분, 60분) 데이터 불러오기
2. 다양한 API 조합 및 파라미터로 시도
3. 성공 조건 및 파라미터 찾기

테스트 시나리오:
- ka10080 API (분봉 차트 API)
  - interval: 1, 3, 5, 15, 30, 60분
  - adjusted: True/False (수정주가)
  - 기본 코드 vs _NX 코드
- ka10001 API (시세 조회 - 분봉 데이터 포함 여부 확인)
- WebSocket 실시간 분봉 구독 테스트
- 다양한 body 파라미터 조합
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


class MinuteCandleTestSuite:
    """분봉 데이터 테스트 스위트"""

    def __init__(self, client):
        self.client = client
        self.test_results = []

    def test_ka10080_standard(self, stock_code: str, interval: int, adjusted: bool = True) -> Optional[List[Dict]]:
        """ka10080 API - 표준 분봉 조회"""
        try:
            body = {
                "stk_cd": stock_code,
                "tic_scope": str(interval),
                "upd_stkpc_tp": "1" if adjusted else "0"
            }

            response = self.client.request(
                api_id="ka10080",
                body=body,
                path="chart"
            )

            if response and response.get('return_code') == 0:
                minute_data = response.get('stk_tic_pole_chart_qry', [])
                if minute_data:
                    standardized = []
                    for item in minute_data[:5]:  # 최근 5개만
                        try:
                            standardized.append({
                                'date': item.get('dt', ''),
                                'time': item.get('tm', ''),
                                'open': int(item.get('open_pric', 0)),
                                'high': int(item.get('high_pric', 0)),
                                'low': int(item.get('low_pric', 0)),
                                'close': int(item.get('cur_prc', 0)),
                                'volume': int(item.get('trde_qty', 0))
                            })
                        except:
                            continue
                    return standardized if standardized else None
        except Exception as e:
            print(f"  {RED}[ERROR] ka10080_standard ({interval}분, adjusted={adjusted}): {e}{RESET}")
        return None

    def test_ka10080_nx_code(self, stock_code: str, interval: int, adjusted: bool = True) -> Optional[List[Dict]]:
        """ka10080 API - _NX 코드로 분봉 조회"""
        try:
            nx_code = f"{stock_code}_NX" if not stock_code.endswith('_NX') else stock_code
            body = {
                "stk_cd": nx_code,
                "tic_scope": str(interval),
                "upd_stkpc_tp": "1" if adjusted else "0"
            }

            response = self.client.request(
                api_id="ka10080",
                body=body,
                path="chart"
            )

            if response and response.get('return_code') == 0:
                minute_data = response.get('stk_tic_pole_chart_qry', [])
                if minute_data:
                    standardized = []
                    for item in minute_data[:5]:
                        try:
                            standardized.append({
                                'date': item.get('dt', ''),
                                'time': item.get('tm', ''),
                                'open': int(item.get('open_pric', 0)),
                                'high': int(item.get('high_pric', 0)),
                                'low': int(item.get('low_pric', 0)),
                                'close': int(item.get('cur_prc', 0)),
                                'volume': int(item.get('trde_qty', 0))
                            })
                        except:
                            continue
                    return standardized if standardized else None
        except Exception as e:
            print(f"  {RED}[ERROR] ka10080_nx_code ({interval}분): {e}{RESET}")
        return None

    def test_ka10080_with_count(self, stock_code: str, interval: int, count: int = 100) -> Optional[List[Dict]]:
        """ka10080 API - count 파라미터 포함"""
        try:
            body = {
                "stk_cd": stock_code,
                "tic_scope": str(interval),
                "upd_stkpc_tp": "1",
                "cnt": str(count)
            }

            response = self.client.request(
                api_id="ka10080",
                body=body,
                path="chart"
            )

            if response and response.get('return_code') == 0:
                minute_data = response.get('stk_tic_pole_chart_qry', [])
                if minute_data:
                    return minute_data[:5]
        except Exception as e:
            print(f"  {RED}[ERROR] ka10080_with_count ({interval}분, count={count}): {e}{RESET}")
        return None

    def test_ka10080_with_date_range(self, stock_code: str, interval: int, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """ka10080 API - 날짜 범위 파라미터"""
        try:
            body = {
                "stk_cd": stock_code,
                "tic_scope": str(interval),
                "upd_stkpc_tp": "1",
                "strt_dt": start_date,
                "end_dt": end_date
            }

            response = self.client.request(
                api_id="ka10080",
                body=body,
                path="chart"
            )

            if response and response.get('return_code') == 0:
                minute_data = response.get('stk_tic_pole_chart_qry', [])
                if minute_data:
                    return minute_data[:5]
        except Exception as e:
            print(f"  {RED}[ERROR] ka10080_with_date_range ({interval}분): {e}{RESET}")
        return None

    def test_ka10080_alternative_fields(self, stock_code: str, interval: int) -> Optional[List[Dict]]:
        """ka10080 API - 대체 필드명 시도"""
        try:
            # 다양한 필드명 조합 시도
            field_combinations = [
                {"stk_cd": stock_code, "interval": str(interval), "upd_stkpc_tp": "1"},
                {"stk_cd": stock_code, "minute": str(interval), "upd_stkpc_tp": "1"},
                {"stk_cd": stock_code, "period": str(interval), "upd_stkpc_tp": "1"},
                {"stock_code": stock_code, "tic_scope": str(interval), "upd_stkpc_tp": "1"},
            ]

            for body in field_combinations:
                try:
                    response = self.client.request(
                        api_id="ka10080",
                        body=body,
                        path="chart"
                    )

                    if response and response.get('return_code') == 0:
                        minute_data = response.get('stk_tic_pole_chart_qry', [])
                        if minute_data:
                            return minute_data[:5]
                except:
                    continue

        except Exception as e:
            print(f"  {RED}[ERROR] ka10080_alternative_fields ({interval}분): {e}{RESET}")
        return None

    def test_ka10001_for_minute(self, stock_code: str) -> Optional[Dict]:
        """ka10001 API - 분봉 데이터 포함 여부 확인"""
        try:
            response = self.client.request(
                api_id="ka10001",
                body={"stk_cd": stock_code},
                path="stkinfo"
            )

            if response and response.get('return_code') == 0:
                # 분봉 데이터 필드 검색
                minute_fields = ['minute_data', 'tic_data', 'candle_data', 'chart_data']
                for field in minute_fields:
                    if field in response and response[field]:
                        return response[field]

                # 전체 응답에서 분봉 관련 필드 탐색
                for key, value in response.items():
                    if 'tic' in key.lower() or 'minute' in key.lower() or 'candle' in key.lower():
                        return {key: value}

        except Exception as e:
            print(f"  {RED}[ERROR] ka10001_for_minute: {e}{RESET}")
        return None

    def test_alternative_apis(self, stock_code: str, interval: int) -> Optional[List[Dict]]:
        """대체 API 시도"""
        alternative_apis = [
            ("ka10082", "chart"),  # 주봉/월봉 API
            ("ka10083", "chart"),  # 틱 데이터 API (있다면)
            ("ka10002", "stkinfo"),  # 시세 상세
        ]

        for api_id, path in alternative_apis:
            try:
                body = {
                    "stk_cd": stock_code,
                    "tic_scope": str(interval),
                    "upd_stkpc_tp": "1"
                }

                response = self.client.request(
                    api_id=api_id,
                    body=body,
                    path=path
                )

                if response and response.get('return_code') == 0:
                    # 응답 데이터 확인
                    for key, value in response.items():
                        if isinstance(value, list) and len(value) > 0:
                            return value[:5]
            except:
                continue

        return None

    def run_comprehensive_test(self, stock_code: str, stock_name: str):
        """종합 테스트 실행"""
        print(f"\n{CYAN}{'='*100}{RESET}")
        print(f"{CYAN}종목: {stock_name} ({stock_code}) - {datetime.now().strftime('%H:%M:%S')}{RESET}")
        print(f"{CYAN}{'='*100}{RESET}")

        intervals = [1, 3, 5, 15, 30, 60]
        results = {}

        for interval in intervals:
            print(f"\n{BLUE}[{interval}분봉 테스트]{RESET}")
            print(f"{BLUE}{'-'*100}{RESET}")

            test_methods = {
                f'{interval}분_표준(수정주가)': self.test_ka10080_standard(stock_code, interval, adjusted=True),
                f'{interval}분_표준(미수정)': self.test_ka10080_standard(stock_code, interval, adjusted=False),
                f'{interval}분_NX코드': self.test_ka10080_nx_code(stock_code, interval),
                f'{interval}분_count파라미터': self.test_ka10080_with_count(stock_code, interval, count=50),
                f'{interval}분_날짜범위': self.test_ka10080_with_date_range(
                    stock_code, interval,
                    start_date=datetime.now().strftime('%Y%m%d'),
                    end_date=datetime.now().strftime('%Y%m%d')
                ),
                f'{interval}분_대체필드': self.test_ka10080_alternative_fields(stock_code, interval),
                f'{interval}분_대체API': self.test_alternative_apis(stock_code, interval),
            }

            results[f'{interval}분'] = {}

            for method_name, data in test_methods.items():
                if data:
                    print(f"  {GREEN}✓ {method_name:<30} 성공 - {len(data)}개 캔들{RESET}")
                    results[f'{interval}분'][method_name] = {
                        'success': True,
                        'count': len(data),
                        'sample': data[0] if data else None
                    }

                    # 첫 번째 캔들 상세 정보 출력
                    if data and len(data) > 0:
                        candle = data[0]
                        if isinstance(candle, dict):
                            date_str = candle.get('date', candle.get('dt', ''))
                            time_str = candle.get('time', candle.get('tm', ''))
                            open_price = candle.get('open', candle.get('open_pric', 0))
                            high_price = candle.get('high', candle.get('high_pric', 0))
                            low_price = candle.get('low', candle.get('low_pric', 0))
                            close_price = candle.get('close', candle.get('cur_prc', 0))
                            volume = candle.get('volume', candle.get('trde_qty', 0))

                            print(f"    {WHITE}최근 캔들: {date_str} {time_str} | O:{open_price:,} H:{high_price:,} L:{low_price:,} C:{close_price:,} V:{volume:,}{RESET}")
                else:
                    print(f"  {RED}✗ {method_name:<30} 실패{RESET}")
                    results[f'{interval}분'][method_name] = {
                        'success': False,
                        'count': 0,
                        'sample': None
                    }

        # ka10001 분봉 데이터 확인
        print(f"\n{BLUE}[ka10001 API 분봉 데이터 확인]{RESET}")
        minute_from_ka10001 = self.test_ka10001_for_minute(stock_code)
        if minute_from_ka10001:
            print(f"  {GREEN}✓ ka10001에서 분봉 관련 데이터 발견{RESET}")
            print(f"    {WHITE}{minute_from_ka10001}{RESET}")
        else:
            print(f"  {YELLOW}✗ ka10001에서 분봉 데이터 없음{RESET}")

        # 테스트 결과 저장
        test_record = {
            'timestamp': datetime.now().isoformat(),
            'stock_code': stock_code,
            'stock_name': stock_name,
            'results': results,
            'ka10001_minute_data': minute_from_ka10001 is not None
        }
        self.test_results.append(test_record)

        # 결론 도출
        print(f"\n{MAGENTA}{'='*100}{RESET}")
        print(f"{MAGENTA}💡 분석 결과{RESET}")
        print(f"{MAGENTA}{'='*100}{RESET}")

        success_methods = []
        for interval_key, methods in results.items():
            for method_name, result in methods.items():
                if result['success']:
                    success_methods.append(method_name)

        if success_methods:
            print(f"{GREEN}✓ 성공한 방법:{RESET}")
            for method in success_methods:
                print(f"  - {method}")
        else:
            print(f"{RED}✗ 모든 방법 실패{RESET}")
            print(f"{YELLOW}  가능한 원인:{RESET}")
            print(f"    1. 장 마감 후 또는 주말/공휴일")
            print(f"    2. 해당 종목의 분봉 데이터 미제공")
            print(f"    3. API 파라미터 또는 경로 오류")
            print(f"    4. 모의투자 서버에서 분봉 미지원")

        print(f"{MAGENTA}{'='*100}{RESET}\n")

        return results


def main():
    """메인 테스트 실행"""
    print(f"\n{BLUE}{'='*100}{RESET}")
    print(f"{BLUE}종목 분봉 데이터 불러오기 종합 테스트{RESET}")
    print(f"{BLUE}{'='*100}{RESET}")

    try:
        from core.rest_client import KiwoomRESTClient
        from utils.trading_date import is_market_hours, is_nxt_hours

        client = KiwoomRESTClient()

        if not client.token:
            print(f"{RED}[X] API 연결 실패{RESET}")
            return

        print(f"{GREEN}[OK] API 연결 성공{RESET}")

        # 시장 시간 확인
        is_market = is_market_hours()
        is_nxt = is_nxt_hours()

        print(f"\n{CYAN}📅 현재 시간 정보{RESET}")
        print(f"  시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  정규 장 시간: {'✅ 예' if is_market else '❌ 아니오'}")
        print(f"  NXT 거래 시간: {'✅ 예' if is_nxt else '❌ 아니오'}")

        if not is_market and not is_nxt:
            print(f"\n{YELLOW}⚠️  현재 거래 시간이 아닙니다.{RESET}")
            print(f"{YELLOW}   분봉 데이터는 장 운영 시간에만 업데이트됩니다.{RESET}")
            print(f"{YELLOW}   그래도 계속 진행하시겠습니까? (y/n): {RESET}", end='')
            response = input().strip().lower()
            if response != 'y':
                print(f"{YELLOW}테스트를 중단합니다.{RESET}")
                return

        # 테스트할 종목
        test_stocks = [
            ("005930", "삼성전자"),
            ("000660", "SK하이닉스"),
            ("051910", "LG화학"),
            ("035720", "카카오"),
            ("035420", "NAVER"),
            ("249420", "일동제약"),
            ("052020", "에프엔에스테크"),
            ("215600", "신라젠"),
        ]

        # 테스트 스위트 초기화
        test_suite = MinuteCandleTestSuite(client)

        # 각 종목별 테스트
        for stock_code, stock_name in test_stocks:
            test_suite.run_comprehensive_test(stock_code, stock_name)
            time.sleep(1)  # API 호출 제한 고려

        # 최종 요약
        print(f"\n{MAGENTA}{'='*100}{RESET}")
        print(f"{MAGENTA}📊 전체 테스트 요약{RESET}")
        print(f"{MAGENTA}{'='*100}{RESET}")

        # 결과 파일 저장
        output_file = project_root / 'tests' / 'manual' / 'results' / f'minute_candle_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_suite.test_results, f, indent=2, ensure_ascii=False)

        print(f"{GREEN}✓ 테스트 결과 저장: {output_file}{RESET}")

        # 방법별 성공률 계산
        method_success_rates = {}
        for record in test_suite.test_results:
            for interval_key, methods in record['results'].items():
                for method_name, result in methods.items():
                    if method_name not in method_success_rates:
                        method_success_rates[method_name] = {'success': 0, 'total': 0}
                    method_success_rates[method_name]['total'] += 1
                    if result['success']:
                        method_success_rates[method_name]['success'] += 1

        print(f"\n{WHITE}{'방법':<40} {'성공률':>15} {'성공/전체':>15}{RESET}")
        print(f"{WHITE}{'-'*70}{RESET}")
        for method_name, stats in sorted(method_success_rates.items(), key=lambda x: x[1]['success']/x[1]['total'] if x[1]['total'] > 0 else 0, reverse=True):
            success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            color = GREEN if success_rate >= 80 else YELLOW if success_rate >= 50 else RED
            print(f"{color}{method_name:<40} {success_rate:>14.1f}% {stats['success']:>7}/{stats['total']:<7}{RESET}")

        print(f"\n{GREEN}✅ 테스트 완료!{RESET}")

    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠️  사용자에 의해 중단됨{RESET}")
    except Exception as e:
        print(f"{RED}[X] 오류 발생: {e}{RESET}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
