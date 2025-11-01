"""
간단한 시장 API 테스트 (실제 환경)
"""
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# credentials.py에서 API 키 로드 (이제 secrets.json에서 가져옴)
from config import get_credentials

from core import KiwoomRESTClient
from api import MarketAPI
import json

print("="*70)
print("시장 API 실제 데이터 수신 테스트 (수정된 API)")
print("="*70)

# 클라이언트 초기화
print("\n[1] REST 클라이언트 초기화 중...")
client = KiwoomRESTClient()
market_api = MarketAPI(client)
print("✓ 초기화 완료")

# 테스트 1: 거래량 순위 조회 (ka10031)
print("\n[2] 거래량 순위 조회 (ka10031) 테스트")
print("-" * 70)
try:
    print("호출: market_api.get_volume_rank('ALL', 5)")
    volume_rank = market_api.get_volume_rank('ALL', 5)

    if volume_rank and len(volume_rank) > 0:
        print(f"✅ 성공: {len(volume_rank)}개 데이터 수신")
        print("\n첫 번째 종목:")
        print(json.dumps(volume_rank[0], indent=2, ensure_ascii=False))
    else:
        print(f"❌ 실패: 데이터 없음 (응답 길이: {len(volume_rank) if volume_rank else 0})")
except Exception as e:
    print(f"❌ 예외 발생: {e}")
    import traceback
    traceback.print_exc()

# 테스트 2: 등락률 순위 조회 (ka10027)
print("\n[3] 등락률 순위 조회 (ka10027) 테스트")
print("-" * 70)
try:
    print("호출: market_api.get_price_change_rank('ALL', 'rise', 5)")
    price_rank = market_api.get_price_change_rank('ALL', 'rise', 5)

    if price_rank and len(price_rank) > 0:
        print(f"✅ 성공: {len(price_rank)}개 데이터 수신")
        print("\n첫 번째 종목:")
        print(json.dumps(price_rank[0], indent=2, ensure_ascii=False))
    else:
        print(f"❌ 실패: 데이터 없음 (응답 길이: {len(price_rank) if price_rank else 0})")
except Exception as e:
    print(f"❌ 예외 발생: {e}")
    import traceback
    traceback.print_exc()

# 테스트 3: REST API 직접 호출
print("\n[4] REST API 직접 호출 테스트")
print("-" * 70)
try:
    body = {
        "mrkt_tp": "0",        # 전체
        "qry_tp": "0",         # 거래량
        "stex_tp": "1",        # 전체
        "rank_strt": "1",
        "rank_end": "3"
    }
    print(f"API ID: ka10031")
    print(f"Body: {body}")

    response = client.request(
        api_id="ka10031",
        body=body,
        path="/api/dostk/rkinfo"
    )

    if response and response.get('return_code') == 0:
        print(f"✅ 성공!")
        output = response.get('output', {})
        print(f"응답 키: {list(output.keys()) if isinstance(output, dict) else 'list'}")
        print(f"응답 일부:")
        print(json.dumps(output if isinstance(output, dict) else output[:1], indent=2, ensure_ascii=False))
    else:
        print(f"❌ 실패:")
        print(f"return_code: {response.get('return_code')}")
        print(f"return_msg: {response.get('return_msg')}")
except Exception as e:
    print(f"❌ 예외 발생: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("테스트 완료")
print("="*70)
