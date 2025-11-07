"""
NXT 실시간 가격 조회 대규모 테스트
"""

"""
목적:
- 10개 종목으로 테스트 확대
- 5초 간격 10회 조회
- 가격 변동 여부 상세 확인
- NXT 시간대에 실시간 가격 조회 가능 여부 최종 판정
"""
import sys
from pathlib import Path
from datetime import datetime
import time

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

GREEN = '\"033"[92m'
RED = '\"033"[91m'
BLUE = '\"033"[94m'
YELLOW = '\"033"[93m'
CYAN = '\"033"[96m'
MAGENTA = '\"033"[95m'
WHITE = '\"033"[97m'
RESET = '\"033"[0m'


def is_nxt_hours():
    """NXT 거래 시간 여부 확인"""
    now = datetime.now()
    current_time = now.time()

    morning_start = datetime.strptime("08:00", "%H:%M").time()
    morning_end = datetime.strptime("09:00", "%H:%M").time()

    afternoon_start = datetime.strptime("15:30", "%H:%M").time()
    afternoon_end = datetime.strptime("20:00", "%H:%M").time()

    is_morning = morning_start <= current_time < morning_end
    is_afternoon = afternoon_start <= current_time < afternoon_end

    return is_morning or is_afternoon


def test_price_monitoring(client, test_stocks, rounds=10, interval=5):
    """
    여러 종목을 여러 번 조회하여 가격 변화 모니터링

    Args:
        client: KiwoomRESTClient 인스턴스
        test_stocks: [(종목코드, 종목명), ...] 리스트
        rounds: 조회 회차 (기본 10회)
        interval: 조회 간격 (기본 5초)
    """
    print(f"\n{BLUE}{'='*100}{RESET}")
    print(f"{BLUE}[SEARCH] 대규모 가격 모니터링 테스트{RESET}")
    print(f"{BLUE}{'='*100}{RESET}")
    print(f"{CYAN}종목 수: {len(test_stocks)}개{RESET}")
    print(f"{CYAN}조회 횟수: {rounds}회{RESET}")
    print(f"{CYAN}조회 간격: {interval}초{RESET}")
    print(f"{CYAN}예상 소요 시간: {rounds * interval}초 ({rounds * interval // 60}분 {rounds * interval % 60}초){RESET}")

    price_history = {code: [] for code, _ in test_stocks}
    stex_tp_history = {code: [] for code, _ in test_stocks}
    time_history = {code: [] for code, _ in test_stocks}

    for round_num in range(1, rounds + 1):
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"\n{MAGENTA}{'='*100}{RESET}")
        print(f"{MAGENTA}[{round_num}/{rounds}회차] {current_time}{RESET}")
        print(f"{MAGENTA}{'='*100}{RESET}")

        for stock_code, stock_name in test_stocks:
            response = client.request(
                api_id="ka10003",
                body={"stk_cd": stock_code},
                path="stkinfo"
            )

            if response and response.get('return_code') == 0:
                cntr_infr = response.get('cntr_infr', [])
                if cntr_infr and len(cntr_infr) > 0:
                    latest = cntr_infr[0]

                    cur_prc_str = latest.get('cur_prc', '0').replace('+', '').replace('-', '')
                    price = int(cur_prc_str) if cur_prc_str else 0

                    stex_tp = latest.get('stex_tp', '')

                    tm = latest.get('tm', '')

                    price_history[stock_code].append(price)
                    stex_tp_history[stock_code].append(stex_tp)
                    time_history[stock_code].append(tm)

                    change_symbol = ""
                    if len(price_history[stock_code]) > 1:
                        prev_price = price_history[stock_code][-2]
                        diff = price - prev_price
                        if diff > 0:
                            change_symbol = f" [UP] +{diff:,}원"
                        elif diff < 0:
                            change_symbol = f" [DOWN] {diff:,}원"
                        else:
                            change_symbol = " ➡️  변동없음"

                    stex_icon = "🟢" if stex_tp == "NXT" else "🔵" if stex_tp == "KRX" else "⚪"
                    print(f"  {stex_icon} {stock_name:15} ({stock_code}) | {price:7,}원 | {stex_tp:3} | {tm:6}{change_symbol}")
                else:
                    print(f"  [X] {stock_name:15} ({stock_code}) | 체결정보 없음")
            else:
                error_msg = response.get('return_msg') if response else 'No response'
                print(f"  [X] {stock_name:15} ({stock_code}) | 실패: {error_msg}")

        if round_num < rounds:
            print(f"\n  {CYAN}⏳ {interval}초 대기 중...{RESET}")
            time.sleep(interval)

    print(f"\n{BLUE}{'='*100}{RESET}")
    print(f"{BLUE}[CHART] 최종 결과 분석{RESET}")
    print(f"{BLUE}{'='*100}{RESET}")

    total_stocks = len(test_stocks)
    stocks_with_change = 0
    nxt_stocks = 0
    krx_stocks = 0

    for stock_code, stock_name in test_stocks:
        prices = price_history[stock_code]
        stex_tps = stex_tp_history[stock_code]
        times = time_history[stock_code]

        if not prices:
            continue

        unique_prices = set(prices)
        has_change = len(unique_prices) > 1

        if has_change:
            stocks_with_change += 1

        if 'NXT' in stex_tps:
            nxt_stocks += 1
        if 'KRX' in stex_tps:
            krx_stocks += 1

        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price

        change_icon = "[OK]" if has_change else "[X]"
        stex_icon = "🟢" if 'NXT' in stex_tps else "🔵" if 'KRX' in stex_tps else "⚪"

        print(f"\n{WHITE}{stock_name} ({stock_code}){RESET}")
        print(f"  {change_icon} 가격 변동: {'있음' if has_change else '없음'} (최소: {min_price:,}원, 최대: {max_price:,}원, 범위: {price_range:,}원)")
        print(f"  {stex_icon} 거래소: {', '.join(set(stex_tps))}")
        print(f"  ⏰ 시간: {', '.join(set(times))}")

    print(f"\n{MAGENTA}{'='*100}{RESET}")
    print(f"{MAGENTA}[UP] 전체 통계{RESET}")
    print(f"{MAGENTA}{'='*100}{RESET}")

    print(f"\n{CYAN}종목 통계:{RESET}")
    print(f"  • 총 종목 수: {total_stocks}개")
    print(f"  • 가격 변동 있음: {stocks_with_change}개 ({stocks_with_change/total_stocks*100:.1f}%)")
    print(f"  • 가격 변동 없음: {total_stocks - stocks_with_change}개 ({(total_stocks - stocks_with_change)/total_stocks*100:.1f}%)")

    print(f"\n{CYAN}거래소 분석:{RESET}")
    print(f"  • NXT 표시 종목: {nxt_stocks}개")
    print(f"  • KRX 표시 종목: {krx_stocks}개")

    print(f"\n{MAGENTA}{'='*100}{RESET}")
    print(f"{MAGENTA}[TARGET] 최종 결론{RESET}")
    print(f"{MAGENTA}{'='*100}{RESET}")

    if stocks_with_change == 0:
        print(f"\n{RED}[X] 모든 종목의 가격이 변동 없음{RESET}")
        print(f"{RED}   -> 실시간 가격 조회가 아닌 것으로 판단됨{RESET}")

        if krx_stocks > 0:
            print(f"\n{YELLOW}[WARNING]️  거래소가 KRX로 표시됨{RESET}")
            print(f"{YELLOW}   -> NXT 시간대임에도 KRX 종가를 반환하고 있음{RESET}")
            print(f"{YELLOW}   -> 기본 코드로는 NXT 실시간 가격 조회 불가{RESET}")
    elif stocks_with_change > 0 and stocks_with_change < total_stocks:
        print(f"\n{YELLOW}[WARNING]️  일부 종목만 가격 변동 감지{RESET}")
        print(f"{YELLOW}   -> {stocks_with_change}개 종목에서 실시간 가격 변동 확인{RESET}")
        print(f"{YELLOW}   -> 종목별로 동작이 다를 수 있음{RESET}")
    else:
        print(f"\n{GREEN}[OK] 모든 종목에서 가격 변동 감지!{RESET}")
        print(f"{GREEN}   -> 실시간 가격 조회가 작동 중{RESET}")

        if nxt_stocks > 0:
            print(f"\n{GREEN}[OK] NXT 거래소로 표시됨{RESET}")
            print(f"{GREEN}   -> NXT 실시간 가격 조회 성공!{RESET}")
        elif krx_stocks > 0:
            print(f"\n{YELLOW}[WARNING]️  KRX로 표시되지만 가격 변동 있음{RESET}")
            print(f"{YELLOW}   -> 실시간 조회는 되지만 거래소 구분 불명확{RESET}")


def main():
    """메인 테스트"""
    print(f"\n{BLUE}{'='*100}{RESET}")
    print(f"{BLUE}🚀 NXT 대규모 가격 모니터링 테스트{RESET}")
    print(f"{BLUE}{'='*100}{RESET}")

    now = datetime.now()
    in_nxt_hours = is_nxt_hours()

    print(f"\n{CYAN}📅 현재 시간 정보{RESET}")
    print(f"  시간: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  NXT 거래 시간: {'[OK] 예' if in_nxt_hours else '[X] 아니오'}")

    if not in_nxt_hours:
        print(f"\n{YELLOW}[WARNING]️  경고: 현재 NXT 거래 시간이 아닙니다!{RESET}")
        print(f"  NXT 거래 시간: "08":"00"-"09":"00", 15:30-20:00")
        print(f"  이 시간대에 테스트해야 정확한 결과를 얻을 수 있습니다.")
        return

    print(f"\n{GREEN}[OK] 지금이 NXT 거래 시간입니다! 테스트를 시작합니다.{RESET}")

    try:
        from core.rest_client import KiwoomRESTClient

        client = KiwoomRESTClient()

        if not client.token:
            print(f"{RED}[X] API 연결 실패{RESET}")
            return

        print(f"{GREEN}[OK] API 연결 성공{RESET}")

        test_stocks = [
            ("249420", "일동제약"),
            ("052020", "에프엔에스테크"),
            ("900290", "GRT"),
            ("900340", "윙입푸드"),
            ("900250", "크리스탈신소재"),
            ("900270", "헝셩그룹"),
            ("217270", "넵튠"),
            ("900300", "오가닉티코스메틱"),
            ("900110", "이스트아시아홀딩스"),
            ("900260", "로스웰"),
        ]

        print(f"\n{CYAN}테스트 종목 ({len(test_stocks)}개):{RESET}")
        for i, (code, name) in enumerate(test_stocks, 1):
            print(f"  {i:2}. {name:20} ({code})")

        test_price_monitoring(
            client=client,
            test_stocks=test_stocks,
            rounds=10,
            interval=5
        )

    except Exception as e:
        print(f"{RED}[X] 오류 발생: {e}{RESET}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
