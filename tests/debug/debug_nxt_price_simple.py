NXT 현재가 조회 디버그 - 단순 직접 테스트
목적: API 응답을 직접 확인하고 어떤 방법이 작동하는지 찾기
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import json
from datetime import datetime
from core.rest_client import KiwoomRESTClient

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_json(data, title=""):
    """JSON 데이터를 보기 좋게 출력"""
    if title:
        print(f"\n{BLUE}[{title}]{RESET}")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def test_api_call(client, api_id: str, body: dict, description: str):
    """
    API 호출하고 결과 출력

    Args:
        client: REST 클라이언트
        api_id: API ID (ka10003, ka10004 등)
        body: 요청 바디
        description: 설명
    """
    print(f"\n{'='*80}")
    print(f"{YELLOW}[테스트] {description}{RESET}")
    print(f"{YELLOW}API: {api_id}{RESET}")
    print(f"{YELLOW}Body: {body}{RESET}")
    print(f"{'='*80}")

    try:
        if api_id == "ka10003":
            path = "stkinfo"
        elif api_id == "ka10004":
            path = "mrkcond"
        elif api_id == "ka30002":
            path = "chart"
        else:
            path = None

        response = client.request(api_id=api_id, body=body, path=path)

        if not response:
            print(f"{RED}❌ 응답 없음{RESET}")
            return None

        return_code = response.get('return_code')
        msg_txt = response.get('msg_txt', '')

        print(f"\nreturn_code: {return_code}")
        print(f"msg_txt: {msg_txt}")

        if return_code == 0:
            print(f"{GREEN}✅ 성공{RESET}")

            print_json(response, "전체 응답")

            price = extract_price(response, api_id)
            if price:
                print(f"\n{GREEN}💰 현재가 추출 성공: {price:,}원{RESET}")
            else:
                print(f"\n{RED}⚠️  현재가 추출 실패{RESET}")

            return response
        else:
            print(f"{RED}❌ 실패 (return_code: {return_code}){RESET}")
            print_json(response, "응답 데이터")
            return None

    except Exception as e:
        print(f"{RED}❌ 예외 발생: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return None


def extract_price(response: dict, api_id: str):
    """응답에서 현재가 추출"""
    try:
        if api_id == "ka10003":
            cntr_infr = response.get('cntr_infr', [])
            if cntr_infr and len(cntr_infr) > 0:
                cur_prc_str = cntr_infr[0].get('cur_prc', '0')
                price = abs(int(cur_prc_str.replace('+', '').replace('-', '')))
                if price > 0:
                    return price

        elif api_id == "ka10004":
            cur_prc_str = response.get('cur_prc', '0')
            if cur_prc_str and cur_prc_str != '0':
                price = abs(int(cur_prc_str.replace('+', '').replace('-', '')))
                if price > 0:
                    return price

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

        elif api_id == "ka30002":
            chart_data = response.get('cntr_day_list', [])
            if chart_data and len(chart_data) > 0:
                latest = chart_data[-1]
                close_price_str = latest.get('cncl_prc', '0')
                price = abs(int(close_price_str.replace('+', '').replace('-', '')))
                if price > 0:
                    return price

    except Exception as e:
        print(f"{RED}가격 추출 오류: {e}{RESET}")

    return None


def main():
    """메인 테스트"""
    print(f"\n{'#'*80}")
    print(f"
    print(f"
    print(f"{'#'*80}")

    print(f"\n{BLUE}클라이언트 초기화 중...{RESET}")
    try:
        from main import TradingBotV2
        bot = TradingBotV2()

        if not bot.client:
            print(f"{RED}❌ 클라이언트 초기화 실패{RESET}")
            return

        client = bot.client
        print(f"{GREEN}✅ 클라이언트 초기화 완료 (from TradingBotV2){RESET}")
    except Exception as e:
        print(f"{RED}❌ TradingBot 초기화 실패: {e}{RESET}")
        print(f"\n{YELLOW}Fallback: 직접 클라이언트 초기화 시도...{RESET}")
        try:
            client = KiwoomRESTClient()
            print(f"{GREEN}✅ 클라이언트 직접 초기화 완료{RESET}")
        except Exception as e2:
            print(f"{RED}❌ 클라이언트 직접 초기화도 실패: {e2}{RESET}")
            return

    test_stock = "249420"
    test_name = "일동제약"

    print(f"\n{BLUE}테스트 종목: {test_stock} ({test_name}){RESET}")

    test_api_call(
        client,
        "ka10003",
        {"stk_cd": test_stock},
        f"ka10003 체결정보 - 기본 코드 ({test_stock})"
    )

    test_api_call(
        client,
        "ka10003",
        {"stk_cd": f"{test_stock}_NX"},
        f"ka10003 체결정보 - _NX 코드 ({test_stock}_NX)"
    )

    test_api_call(
        client,
        "ka10004",
        {"stk_cd": test_stock},
        f"ka10004 호가 - 기본 코드 ({test_stock})"
    )

    test_api_call(
        client,
        "ka10004",
        {"stk_cd": f"{test_stock}_NX"},
        f"ka10004 호가 - _NX 코드 ({test_stock}_NX)"
    )

    today = datetime.now().strftime("%Y%m%d")
    test_api_call(
        client,
        "ka30002",
        {
            "stk_cd": test_stock,
            "time_type": "D",
            "inq_strt_dt": today,
            "inq_end_dt": today
        },
        f"ka30002 차트(일봉) - 기본 코드 ({test_stock})"
    )

    test_api_call(
        client,
        "ka30002",
        {
            "stk_cd": f"{test_stock}_NX",
            "time_type": "D",
            "inq_strt_dt": today,
            "inq_end_dt": today
        },
        f"ka30002 차트(일봉) - _NX 코드 ({test_stock}_NX)"
    )

    test_api_call(
        client,
        "ka30002",
        {
            "stk_cd": test_stock,
            "time_type": "m",
            "time_value": "1",
            "inq_strt_dt": today,
            "inq_end_dt": today
        },
        f"ka30002 차트(1분봉) - 기본 코드 ({test_stock})"
    )

    test_api_call(
        client,
        "ka30002",
        {
            "stk_cd": f"{test_stock}_NX",
            "time_type": "m",
            "time_value": "1",
            "inq_strt_dt": today,
            "inq_end_dt": today
        },
        f"ka30002 차트(1분봉) - _NX 코드 ({test_stock}_NX)"
    )

    print(f"\n{'='*80}")
    print(f"{GREEN}테스트 완료{RESET}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
