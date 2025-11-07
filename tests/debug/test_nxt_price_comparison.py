"""
NXT 거래시간 가격 비교 테스트
"""

목적:
1. NXT 거래 시간 여부 확인
2. 기본 코드로 조회한 가격이 NXT 실시간 가격인지 확인
3. 응답에 거래소 정보(stex_tp) 확인

실행 시간:
- NXT 거래 시간 ("08":"00"-"09":"00", 15:30-20:"00")과
- 일반 시간 모두에서 실행하여 비교
import sys
from pathlib import Path
from datetime import datetime
import json

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

GREEN = '\"033"[92m'
RED = '\"033"[91m'
BLUE = '\"033"[94m'
YELLOW = '\"033"[93m'
CYAN = '\"033"[96m'
MAGENTA = '\"033"[95m'
RESET = '\"033"[0m'


def is_nxt_hours():
    """NXT 거래 시간 여부 확인"""
    from utils.trading_date import is_nxt_trading_hours
    return is_nxt_trading_hours()


def test_price_detail(client, stock_code: str, stock_name: str):
    """상세 가격 조회 및 분석"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}종목: {stock_name} ({stock_code}){RESET}")
    print(f"{BLUE}{'='*80}{RESET}")

    now = datetime.now()
    in_nxt_hours = is_nxt_hours()

    print(f"\n{CYAN}📅 현재 시간 정보{RESET}")
    print(f"  시간: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  NXT 거래 시간: {'[OK] 예 ("08":"00"-"09":"00" 또는 15:30-20:"00")' if in_nxt_hours else '[X] 아니오'}")

    print(f"\n{CYAN}[CHART] ka10001 API - 기본 코드 조회{RESET}")
    response = client.request(
        api_id="ka10001",
        body={"stk_cd": stock_code},
        path="stkinfo"
    )

    if response and response.get('return_code') == 0:
        print(f"{GREEN}[OK] API 호출 성공{RESET}")
        print(f"\n{YELLOW}전체 응답:{RESET}")
        print(json.dumps(response, indent=2, ensure_ascii=False))

        print(f"\n{CYAN}[SEARCH] 주요 정보 분석{RESET}")

        price_fields = ['cur_prc', 'crnt_pric', 'stk_pric', 'now_pric', 'current_price']
        found_price = None
        found_field = None

        for field in price_fields:
            if field in response:
                found_price = response[field]
                found_field = field
                break

        if found_price:
            try:
                price = int(str(found_price).replace('+', '').replace('-', '').replace(',', ''))
                print(f"  [MONEY] 현재가: {price:,}원 (필드: {found_field})")
            except:
                print(f"  [WARNING]️  가격 파싱 실패: {found_price}")
        else:
            print(f"  [X] 현재가 필드를 찾을 수 없음")
            print(f"  사용 가능한 필드: {list(response.keys())}")

        stex_fields = ['stex_tp', 'mrkt_tp', 'market_type', 'exchange']
        for field in stex_fields:
            if field in response:
                print(f"  🏢 거래소: {response[field]} (필드: {field})")
                break

        time_fields = ['tm', 'time', 'cntr_tm', 'trade_time']
        for field in time_fields:
            if field in response:
                print(f"  ⏰ 시간: {response[field]} (필드: {field})")
                break

    else:
        error_msg = response.get('return_msg') if response else 'No response'
        print(f"{RED}[X] API 호출 실패: {error_msg}{RESET}")

    print(f"\n{CYAN}[CHART] ka10003 API - 기본 코드 조회 (비교){RESET}")
    response2 = client.request(
        api_id="ka10003",
        body={"stk_cd": stock_code},
        path="stkinfo"
    )

    if response2 and response2.get('return_code') == 0:
        print(f"{GREEN}[OK] API 호출 성공{RESET}")
        cntr_infr = response2.get('cntr_infr', [])
        if cntr_infr and len(cntr_infr) > 0:
            latest = cntr_infr[0]
            cur_prc = latest.get('cur_prc', '0')
            stex_tp = latest.get('stex_tp', '')
            tm = latest.get('tm', '')

            try:
                price = int(str(cur_prc).replace('+', '').replace('-', '').replace(',', ''))
                print(f"  [MONEY] 현재가: {price:,}원")
                print(f"  🏢 거래소: {stex_tp}")
                print(f"  ⏰ 시간: {tm}")
            except:
                print(f"  [WARNING]️  가격 파싱 실패: {cur_prc}")
    else:
        error_msg = response2.get('return_msg') if response2 else 'No response'
        print(f"{RED}[X] API 호출 실패: {error_msg}{RESET}")


def main():
    """메인 테스트"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}NXT 거래시간 가격 비교 테스트{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")

    try:
        from main import TradingBotV2
        from config.credentials import get_credentials

        credentials = get_credentials()
        bot = TradingBotV2(credentials=credentials)

        if not bot.client.is_connected:
            print(f"{RED}[X] API 연결 실패{RESET}")
            return

        print(f"{GREEN}[OK] API 연결 성공{RESET}")
        client = bot.client

        test_stocks = [
            ("249420", "일동제약"),
            ("052020", "에프엔에스테크"),
        ]

        for code, name in test_stocks:
            test_price_detail(client, code, name)

        print(f"\n{MAGENTA}{'='*80}{RESET}")
        print(f"{MAGENTA}💡 해석 가이드{RESET}")
        print(f"{MAGENTA}{'='*80}{RESET}")

        if is_nxt_hours():
            print(f"\n{GREEN}[OK] 현재 NXT 거래 시간입니다{RESET}")
            print(f"\n만약 기본 코드로 조회한 가격이:")
            print(f"  1️⃣  응답에 stex_tp='NXT' 포함 -> {GREEN}NXT 실시간 가격{RESET}")
            print(f"  2️⃣  응답에 stex_tp='KRX' 포함 -> {YELLOW}KRX 가격 (문제){RESET}")
            print(f"  3️⃣  거래소 정보 없음 -> {YELLOW}추가 확인 필요{RESET}")
        else:
            print(f"\n{YELLOW}[WARNING]️  현재 NXT 거래 시간이 아닙니다{RESET}")
            print(f"\n이 테스트는 다음 시간에 다시 실행해야 합니다:")
            print(f"  • 오전: "08":"00" ~ "09":00")
            print(f"  • 오후: 15:30 ~ 20:00")
            print(f"\n현재 조회된 가격은 전일 종가일 가능성이 높습니다.")

    except Exception as e:
        print(f"{RED}[X] 오류 발생: {e}{RESET}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
