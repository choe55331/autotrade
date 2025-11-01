"""
시장 API 실제 데이터 수신 테스트
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core import KiwoomRESTClient
from api import MarketAPI
from utils.trading_date import get_last_trading_date
import json

print("="*70)
print("시장 API 데이터 수신 테스트")
print("="*70)

# 클라이언트 초기화
print("\n[1] REST 클라이언트 초기화 중...")
client = KiwoomRESTClient()
market_api = MarketAPI(client)
print("✓ 초기화 완료")

# 최근 거래일
trading_date = get_last_trading_date()
print(f"\n[2] 최근 거래일: {trading_date}")

# 테스트 1: 거래량 순위 조회
print("\n[3] 거래량 순위 조회 테스트")
print("-" * 70)
try:
    # 날짜 파라미터 없이 호출 (자동 계산)
    print("호출: market_api.get_volume_rank('ALL', 10)")
    volume_rank = market_api.get_volume_rank('ALL', 10)

    if volume_rank:
        print(f"✓ 성공: {len(volume_rank)}개 데이터 수신")
        if len(volume_rank) > 0:
            print("\n첫 번째 종목 데이터:")
            print(json.dumps(volume_rank[0], indent=2, ensure_ascii=False))
    else:
        print("✗ 실패: 데이터 없음")
        print(f"응답: {volume_rank}")
except Exception as e:
    print(f"✗ 예외 발생: {e}")
    import traceback
    traceback.print_exc()

# 테스트 2: 등락률 순위 조회
print("\n[4] 등락률 순위 조회 테스트")
print("-" * 70)
try:
    # 날짜 파라미터 없이 호출 (자동 계산)
    print("호출: market_api.get_price_change_rank('ALL', 'rise', 10)")
    price_rank = market_api.get_price_change_rank('ALL', 'rise', 10)

    if price_rank:
        print(f"✓ 성공: {len(price_rank)}개 데이터 수신")
        if len(price_rank) > 0:
            print("\n첫 번째 종목 데이터:")
            print(json.dumps(price_rank[0], indent=2, ensure_ascii=False))
    else:
        print("✗ 실패: 데이터 없음")
        print(f"응답: {price_rank}")
except Exception as e:
    print(f"✗ 예외 발생: {e}")
    import traceback
    traceback.print_exc()

# 테스트 3: 날짜 파라미터와 함께 호출
print(f"\n[5] 날짜 지정 조회 테스트 (date={trading_date})")
print("-" * 70)
try:
    print(f"호출: market_api.get_volume_rank('ALL', 5, date='{trading_date}')")
    volume_rank_with_date = market_api.get_volume_rank('ALL', 5, date=trading_date)

    if volume_rank_with_date:
        print(f"✓ 성공: {len(volume_rank_with_date)}개 데이터 수신")
    else:
        print("✗ 실패: 데이터 없음")
except Exception as e:
    print(f"✗ 예외 발생: {e}")
    import traceback
    traceback.print_exc()

# 테스트 4: 실제 REST API 직접 호출 (디버깅)
print("\n[6] REST API 직접 호출 테스트")
print("-" * 70)
try:
    # API ID와 경로를 여러 가지 조합으로 테스트
    test_cases = [
        ("DOSK_0010", "/api/dostk/inquire/rank", {"market": "ALL", "limit": 5, "sort": "volume", "date": trading_date}),
        ("DOSK_0010", "/api/dostk/inquire/rank", {"market": "ALL", "limit": 5, "sort": "volume"}),
        ("kt00103", "/api/dostk/inquire", {"tr_cd": "HHDFS76240000", "inqr_dvsn": "0"}),  # 거래량 순위 가능한 TR
    ]

    for i, (api_id, path, body) in enumerate(test_cases, 1):
        print(f"\n테스트 케이스 {i}:")
        print(f"  API ID: {api_id}")
        print(f"  Path: {path}")
        print(f"  Body: {body}")

        response = client.request(api_id=api_id, body=body, path=path)

        if response and response.get('return_code') == 0:
            output = response.get('output', [])
            print(f"  ✓ 성공: return_code={response.get('return_code')}")
            if isinstance(output, list) and len(output) > 0:
                print(f"  데이터 개수: {len(output)}")
                print(f"  첫 번째 항목: {output[0]}")
            elif isinstance(output, dict):
                print(f"  응답 데이터: {output}")
            else:
                print(f"  응답: {response}")
        else:
            print(f"  ✗ 실패:")
            print(f"  return_code: {response.get('return_code')}")
            print(f"  return_msg: {response.get('return_msg')}")

except Exception as e:
    print(f"✗ 예외 발생: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("테스트 완료")
print("="*70)
