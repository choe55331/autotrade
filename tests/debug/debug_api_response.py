API 응답 디버그 스크립트
실제 API 응답을 확인하여 문제를 진단합니다.
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core import KiwoomRESTClient

def test_api_response():
    """API 응답 상세 확인"""
    print("="*80)
    print("API 응답 디버그 테스트")
    print("="*80)

    print("\n1. REST 클라이언트 초기화...")
    try:
        client = KiwoomRESTClient()
        print(f"✅ 초기화 완료")
        print(f"   - Base URL: {client.base_url}")
        print(f"   - App Key: {client.appkey[:10]}..." if client.appkey else "   - App Key: None")
        print(f"   - Token: {'발급됨' if client.token else '없음'}")
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n2. 거래량 순위 API 호출 테스트...")
    print("   API: ka10030 (당일거래량상위요청)")

    body = {
        "stk_knd_cd": "0",
        "cndt_vol": "100000",
        "stk_cnt": "20"
    }

    try:
        response = client.request(
            api_id="ka10030",
            body=body,
            path="ka10030"
        )

        print("\n✅ API 호출 완료")
        print("\n" + "="*80)
        print("전체 응답 내용:")
        print("="*80)
        print(json.dumps(response, indent=2, ensure_ascii=False))

        print("\n" + "="*80)
        print("응답 분석:")
        print("="*80)

        if response:
            return_code = response.get('return_code')
            return_msg = response.get('return_msg', '')

            print(f"Return Code: {return_code}")
            print(f"Return Message: {return_msg}")

            data_keys = [k for k in response.keys() if k not in ['return_code', 'return_msg']]
            print(f"\nData Keys: {data_keys}")

            if data_keys:
                for key in data_keys:
                    data = response.get(key)
                    if isinstance(data, list):
                        print(f"\n'{key}': 리스트 ({len(data)}개 항목)")
                        if len(data) > 0:
                            print(f"첫 번째 항목 구조:")
                            print(json.dumps(data[0], indent=2, ensure_ascii=False))
                    elif isinstance(data, dict):
                        print(f"\n'{key}': 딕셔너리 ({len(data)}개 키)")
                        print(json.dumps(data, indent=2, ensure_ascii=False))
                    else:
                        print(f"\n'{key}': {type(data).__name__} = {data}")
            else:
                print("\n⚠️ 데이터 키가 없습니다.")

            if return_code == 0:
                print(f"\n✅ API 호출 성공")
                if not data_keys or all(not response.get(k) for k in data_keys):
                    print(f"⚠️ 하지만 데이터가 비어있습니다.")
                    print(f"\n가능한 원인:")
                    print(f"   1. 장 마감 후 또는 주말")
                    print(f"   2. 조건에 맞는 종목이 없음")
                    print(f"   3. API 파라미터 오류")
            else:
                print(f"\n❌ API 오류 발생")
                print(f"   오류 코드: {return_code}")
                print(f"   오류 메시지: {return_msg}")
        else:
            print("❌ 응답이 None입니다")

    except Exception as e:
        print(f"\n❌ API 호출 실패: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)
    print("토큰 정보:")
    print("="*80)
    if client.token:
        print(f"Token: {client.token[:20]}...")
        print(f"Expiry: {client.token_expiry}")
    else:
        print("❌ 토큰이 없습니다")

if __name__ == '__main__':
    test_api_response()
