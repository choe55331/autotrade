"""
NXT 실시간 가격 변동 확인
목적: 시간차를 두고 여러 번 조회해서 실시간 변동 확인
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import time
from datetime import datetime
from core.rest_client import KiwoomRESTClient

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'


def get_price(client, stock_code: str):
    """현재가 조회"""
    try:
        response = client.request(
            api_id="ka10003",
            body={"stk_cd": stock_code},
            path="stkinfo"
        )

        if response and response.get('return_code') == 0:
            cntr_infr = response.get('cntr_infr', [])
            if cntr_infr:
                cur_prc = cntr_infr[0].get('cur_prc', '0')
                return abs(int(cur_prc.replace('+', '').replace('-', '')))
    except:
        pass
    return None


def main():
    """메인 실행"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}NXT 실시간 가격 변동 확인{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    from main import TradingBotV2
    bot = TradingBotV2()
    client = bot.client

    code, name = "249420", "일동제약"

    print(f"{CYAN}종목: {code} ({name}){RESET}")
    print(f"{CYAN}방법: ka10003 (체결정보){RESET}")
    print(f"{CYAN}조회 간격: 10초{RESET}\n")

    prices = []

    for i in range(5):
        now = datetime.now().strftime('%H:%M:%S')
        price = get_price(client, code)

        if price:
            prices.append(price)

            if len(prices) > 1:
                diff = price - prices[-2]
                if diff != 0:
                    color = GREEN if diff > 0 else RED
                    print(f"[{now}] {color}{price:,}원 ({diff:+,}원){RESET}")
                else:
                    print(f"[{now}] {price:,}원 (변동 없음)")
            else:
                print(f"[{now}] {price:,}원")
        else:
            print(f"[{now}] {RED}조회 실패{RESET}")

        if i < 4:
            time.sleep(10)

    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}결과 요약{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    if prices:
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) // len(prices)

        print(f"최저가: {min_price:,}원")
        print(f"최고가: {max_price:,}원")
        print(f"평균가: {avg_price:,}원")
        print(f"변동폭: {max_price - min_price:,}원")

        if max_price > min_price:
            print(f"\n{GREEN}✅ 실시간 가격 변동 확인됨!{RESET}")
        else:
            print(f"\n{YELLOW}⚠️  가격 변동 없음 (거래 없거나 종가 고정){RESET}")

    print(f"\n{BLUE}{'='*80}{RESET}\n")


if __name__ == "__main__":
    main()
