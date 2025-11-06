"""
NXT WebSocket 실시간 현재가 조회 테스트

핵심 발견:
- WebSocket 실시간 구독에서는 _NX 접미사 사용 필수!
- type: 0B (주식체결)
- 필드 10: 현재가
- 필드 9081: 거래소구분

테스트:
- 10개 NXT 종목 구독
- 5초마다 현재가 체크 (10회)
- 가격 변동 추적
"""
import sys
from pathlib import Path
from datetime import datetime
import time
import asyncio
import json

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 색상 코드
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
RESET = '\033[0m'


def is_nxt_hours():
    """NXT 거래 시간 여부 확인"""
    now = datetime.now()
    current_time = now.time()

    # 오전: 08:00-09:00
    morning_start = datetime.strptime("08:00", "%H:%M").time()
    morning_end = datetime.strptime("09:00", "%H:%M").time()

    # 오후: 15:30-20:00
    afternoon_start = datetime.strptime("15:30", "%H:%M").time()
    afternoon_end = datetime.strptime("20:00", "%H:%M").time()

    is_morning = morning_start <= current_time < morning_end
    is_afternoon = afternoon_start <= current_time < afternoon_end

    return is_morning or is_afternoon


async def test_websocket_realtime():
    """WebSocket 실시간 가격 테스트"""
    print(f"\n{BLUE}{'='*100}{RESET}")
    print(f"{BLUE}🔍 NXT WebSocket 실시간 가격 모니터링{RESET}")
    print(f"{BLUE}{'='*100}{RESET}")

    # 테스트 종목 10개 (NXT 거래 활발한 종목)
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
        print(f"  {i:2}. {name:20} ({code}_NX)")

    try:
        # WebSocketManager 초기화
        from core.websocket_manager import WebSocketManager
        from core.rest_client import KiwoomRESTClient

        # REST Client로 토큰 발급
        rest_client = KiwoomRESTClient()
        if not rest_client.token:
            print(f"{RED}❌ REST API 연결 실패{RESET}")
            return

        print(f"{GREEN}✅ REST API 연결 성공{RESET}")

        # WebSocket 연결
        ws_manager = WebSocketManager(rest_client.token)

        print(f"{CYAN}WebSocket 연결 시도...{RESET}")
        await ws_manager.connect()

        if not ws_manager.is_connected:
            print(f"{RED}❌ WebSocket 연결 실패{RESET}")
            return

        print(f"{GREEN}✅ WebSocket 연결 성공{RESET}")

        # 가격 기록 저장소
        price_history = {code: {'name': name, 'prices': [], 'timestamps': []}
                        for code, name in test_stocks}

        # 실시간 데이터 수신 콜백
        received_count = [0]  # 수신된 데이터 카운터

        def on_realtime_data(data):
            """실시간 데이터 수신 시 호출"""
            try:
                if not isinstance(data, dict):
                    return

                data_list = data.get('data', [])
                for item in data_list:
                    item_code = item.get('item', '')
                    values = item.get('values', {})

                    # _NX 제거하여 기본 코드 추출
                    base_code = item_code.replace('_NX', '')

                    if base_code in price_history:
                        # 필드 10: 현재가
                        cur_prc_str = values.get('10', '0')
                        # 필드 9081: 거래소구분
                        stex_tp = values.get('9081', '')
                        # 필드 20: 체결시간
                        time_str = values.get('20', '')

                        try:
                            cur_prc = abs(int(cur_prc_str.replace('+', '').replace('-', '')))

                            # 기록 저장
                            price_history[base_code]['prices'].append(cur_prc)
                            price_history[base_code]['timestamps'].append(datetime.now().strftime('%H:%M:%S'))

                            received_count[0] += 1

                        except:
                            pass
            except Exception as e:
                pass

        # 콜백 등록
        ws_manager.register_callback('test', on_realtime_data)

        # 종목 구독 (0B: 주식체결, _NX 접미사 필수!)
        items_with_nx = [f"{code}_NX" for code, _ in test_stocks]

        print(f"\n{CYAN}종목 구독 중...{RESET}")
        print(f"  Type: 0B (주식체결)")
        print(f"  Items: {len(items_with_nx)}개 (_NX 접미사 포함)")

        success = await ws_manager.subscribe(
            stock_codes=items_with_nx,
            types=["0B"]
        )

        if not success:
            print(f"{RED}❌ 구독 실패{RESET}")
            return

        print(f"{GREEN}✅ 구독 성공!{RESET}")

        # 10회 체크 (5초 간격)
        print(f"\n{MAGENTA}{'='*100}{RESET}")
        print(f"{MAGENTA}📊 실시간 데이터 수신 모니터링 (10회, 5초 간격){RESET}")
        print(f"{MAGENTA}{'='*100}{RESET}")

        for round_num in range(1, 11):
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"\n{BLUE}[{round_num}/10회차] {current_time}{RESET}")
            print(f"  수신된 데이터: {received_count[0]}건")

            # 현재까지 수신된 가격 출력
            stocks_with_data = 0
            for code, data in price_history.items():
                if data['prices']:
                    stocks_with_data += 1
                    latest_price = data['prices'][-1]
                    latest_time = data['timestamps'][-1]

                    # 변동 계산
                    change_symbol = ""
                    if len(data['prices']) > 1:
                        prev_price = data['prices'][-2]
                        diff = latest_price - prev_price
                        if diff > 0:
                            change_symbol = f" 📈 +{diff:,}원"
                        elif diff < 0:
                            change_symbol = f" 📉 {diff:,}원"
                        else:
                            change_symbol = " ➡️  변동없음"

                    print(f"  🟢 {data['name']:15} ({code}_NX) | {latest_price:7,}원 @ {latest_time}{change_symbol}")

            if stocks_with_data == 0:
                print(f"  {YELLOW}⚠️  아직 데이터 수신 없음...{RESET}")

            # 마지막 회차가 아니면 대기
            if round_num < 10:
                await asyncio.sleep(5)

        # 최종 결과 분석
        print(f"\n{BLUE}{'='*100}{RESET}")
        print(f"{BLUE}📊 최종 결과 분석{RESET}")
        print(f"{BLUE}{'='*100}{RESET}")

        total_stocks = len(test_stocks)
        stocks_with_change = 0
        stocks_with_data = 0

        for code, data in price_history.items():
            prices = data['prices']
            name = data['name']

            if not prices:
                print(f"\n{YELLOW}{name} ({code}_NX){RESET}")
                print(f"  ❌ 데이터 수신 없음")
                continue

            stocks_with_data += 1

            # 가격 변동 분석
            unique_prices = set(prices)
            has_change = len(unique_prices) > 1

            if has_change:
                stocks_with_change += 1

            # 개별 종목 요약
            min_price = min(prices)
            max_price = max(prices)
            price_range = max_price - min_price

            change_icon = "✅" if has_change else "❌"

            print(f"\n{WHITE}{name} ({code}_NX){RESET}")
            print(f"  {change_icon} 가격 변동: {'있음' if has_change else '없음'} (최소: {min_price:,}원, 최대: {max_price:,}원, 범위: {price_range:,}원)")
            print(f"  📊 수신 횟수: {len(prices)}회")

        # 전체 통계
        print(f"\n{MAGENTA}{'='*100}{RESET}")
        print(f"{MAGENTA}🎯 최종 결론{RESET}")
        print(f"{MAGENTA}{'='*100}{RESET}")

        print(f"\n{CYAN}수신 통계:{RESET}")
        print(f"  • 총 종목 수: {total_stocks}개")
        print(f"  • 데이터 수신: {stocks_with_data}개 ({stocks_with_data/total_stocks*100:.1f}%)")
        print(f"  • 수신 없음: {total_stocks - stocks_with_data}개")
        print(f"  • 총 수신 건수: {received_count[0]}건")

        print(f"\n{CYAN}가격 변동 분석:{RESET}")
        if stocks_with_data > 0:
            print(f"  • 가격 변동 있음: {stocks_with_change}개 ({stocks_with_change/stocks_with_data*100:.1f}%)")
            print(f"  • 가격 변동 없음: {stocks_with_data - stocks_with_change}개")
        else:
            print(f"  • 데이터 없음")

        # 최종 판정
        if stocks_with_data == 0:
            print(f"\n{RED}❌ WebSocket 실시간 데이터 수신 실패{RESET}")
            print(f"{YELLOW}가능한 원인:{RESET}")
            print(f"  1. _NX 접미사 형식 문제")
            print(f"  2. WebSocket 연결 불안정")
            print(f"  3. 구독 타입(0B) 문제")
            print(f"  4. NXT 시간대가 아님")
        elif stocks_with_change == 0:
            print(f"\n{YELLOW}⚠️  데이터 수신은 됐으나 가격 변동 없음{RESET}")
            print(f"{YELLOW}   → 실시간 가격이 아니거나, 테스트 기간 동안 변동 없음{RESET}")
        elif stocks_with_change > 0:
            print(f"\n{GREEN}✅ WebSocket으로 NXT 실시간 가격 조회 성공!{RESET}")
            print(f"{GREEN}   → _NX 접미사 + type=0B로 실시간 현재가 구독 가능{RESET}")
            print(f"{GREEN}   → {stocks_with_change}개 종목에서 실시간 가격 변동 확인{RESET}")

        # WebSocket 해제
        await ws_manager.disconnect()

    except Exception as e:
        print(f"{RED}❌ 오류 발생: {e}{RESET}")
        import traceback
        traceback.print_exc()


def main():
    """메인 함수"""
    print(f"\n{BLUE}{'='*100}{RESET}")
    print(f"{BLUE}🚀 NXT WebSocket 실시간 가격 테스트{RESET}")
    print(f"{BLUE}{'='*100}{RESET}")

    # 현재 시간 확인
    now = datetime.now()
    in_nxt_hours = is_nxt_hours()

    print(f"\n{CYAN}📅 현재 시간 정보{RESET}")
    print(f"  시간: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  NXT 거래 시간: {'✅ 예' if in_nxt_hours else '❌ 아니오'}")

    if not in_nxt_hours:
        print(f"\n{YELLOW}⚠️  경고: 현재 NXT 거래 시간이 아닙니다!{RESET}")
        print(f"  NXT 거래 시간: 08:00-09:00, 15:30-20:00")
        response = input("\n  계속 진행하시겠습니까? (y/n): ")
        if response.lower() != 'y':
            return

    print(f"\n{GREEN}✅ 테스트를 시작합니다.{RESET}")

    # asyncio 실행
    try:
        asyncio.run(test_websocket_realtime())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}테스트 중단됨{RESET}")
    except Exception as e:
        print(f"\n{RED}오류: {e}{RESET}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
