"""
시장탐색 직접 테스트 (최소 의존성)
"""
import sys
import os

# 환경변수 직접 설정 (실제 키로 변경하세요)
os.environ['KIWOOM_REST_APPKEY'] = 'TjgoRS0k_U-EcnCBxwn23EM6wbTxHiFmuMHGpIYObRU'
os.environ['KIWOOM_REST_SECRETKEY'] = 'LAcgLwxqlOduBocdLIDO57t4kHHjoyxVonSe2ghnt3U'

# 간단한 REST 클라이언트
import requests
import json
import datetime

class SimpleClient:
    def __init__(self):
        self.base_url = "https://api.kiwoom.com"
        self.appkey = os.environ['KIWOOM_REST_APPKEY']
        self.secretkey = os.environ['KIWOOM_REST_SECRETKEY']
        self.token = None
        self.get_token()

    def get_token(self):
        url = f"{self.base_url}/oauth2/token"
        payload = {
            "grant_type": "client_credentials",
            "appkey": self.appkey,
            "secretkey": self.secretkey
        }
        headers = {"content-type": "application/json;charset=UTF-8"}

        try:
            res = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
            print(f"토큰 요청 상태: {res.status_code}")

            if res.status_code == 200:
                token_data = res.json()
                self.token = token_data.get('token')
                expires = token_data.get('expires_dt')
                print(f"✓ 토큰 발급 성공 (만료: {expires})")
                return True
            else:
                print(f"✗ 토큰 발급 실패: {res.text}")
                return False
        except Exception as e:
            print(f"✗ 토큰 발급 예외: {e}")
            return False

    def request(self, api_id, body, path):
        if not self.token:
            print("토큰 없음")
            return None

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.token}",
            "api-id": api_id
        }

        url = f"{self.base_url}{path}"

        try:
            res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
            print(f"API 요청 상태: {res.status_code}")

            if res.status_code == 200:
                return res.json()
            else:
                print(f"API 에러: {res.text[:200]}")
                return None
        except Exception as e:
            print(f"API 예외: {e}")
            return None

print("="*70)
print("시장탐색 직접 테스트")
print("="*70)

# 클라이언트 생성
print("\n[1] 클라이언트 초기화")
client = SimpleClient()

if not client.token:
    print("\n❌ API 키가 유효하지 않습니다.")
    print("config/credentials.py에서 실제 API 키를 확인하세요.")
    sys.exit(1)

# 테스트 1: 거래량 순위
print("\n[2] 거래량 순위 조회 (ka10031)")
print("-" * 70)

body = {
    "mrkt_tp": "0",      # 전체
    "qry_tp": "0",       # 거래량
    "stex_tp": "1",      # 전체
    "rank_strt": "1",
    "rank_end": "5"
}

print(f"요청: {body}")
response = client.request("ka10031", body, "/api/dostk/rkinfo")

if response:
    print(f"응답 키: {list(response.keys())}")
    print(f"return_code: {response.get('return_code')}")
    print(f"return_msg: {response.get('return_msg')}")

    if response.get('return_code') == 0:
        output = response.get('output', {})
        if isinstance(output, dict):
            data_list = output.get('list', [])
            print(f"\n✅ 성공: {len(data_list)}개 데이터")
            if len(data_list) > 0:
                print(f"\n첫 번째 종목:")
                print(json.dumps(data_list[0], indent=2, ensure_ascii=False))
        else:
            print(f"\n✅ 성공: {len(output)}개 데이터")
            if len(output) > 0:
                print(f"\n첫 번째 종목:")
                print(json.dumps(output[0], indent=2, ensure_ascii=False))
    else:
        print(f"\n❌ 실패")
else:
    print("\n❌ 응답 없음")

# 테스트 2: 등락률 순위
print("\n[3] 등락률 순위 조회 (ka10027)")
print("-" * 70)

body = {
    "mrkt_tp": "0",
    "sort_tp": "0",        # 상승률
    "trde_qty_cnd": "0",
    "stk_cnd": "0",
    "crd_cnd": "0",
    "updown_incls": "1",
    "pric_cnd": "0",
    "trde_prica_cnd": "0",
    "stex_tp": "1"
}

print(f"요청: {body}")
response = client.request("ka10027", body, "/api/dostk/rkinfo")

if response:
    print(f"응답 키: {list(response.keys())}")
    print(f"return_code: {response.get('return_code')}")
    print(f"return_msg: {response.get('return_msg')}")

    if response.get('return_code') == 0:
        output = response.get('output', {})
        if isinstance(output, dict):
            data_list = output.get('list', [])
            print(f"\n✅ 성공: {len(data_list)}개 데이터")
            if len(data_list) > 0:
                print(f"\n첫 번째 종목:")
                print(json.dumps(data_list[0], indent=2, ensure_ascii=False))
        else:
            print(f"\n✅ 성공: {len(output)}개 데이터")
            if len(output) > 0:
                print(f"\n첫 번째 종목:")
                print(json.dumps(output[0], indent=2, ensure_ascii=False))
    else:
        print(f"\n❌ 실패")
else:
    print("\n❌ 응답 없음")

print("\n" + "="*70)
print("테스트 완료")
print("="*70)
print("\n참고: 실제 API 키가 필요합니다.")
print("config/credentials.py 또는 .env 파일에서 API 키를 설정하세요.")
