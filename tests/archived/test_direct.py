"""
시장탐색 직접 테스트 (최소 의존성) - 전체 응답 출력 버전
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# credentials.py에서 API 키 로드
from config import get_credentials

# 간단한 REST 클라이언트
import requests
import json
import datetime

class SimpleClient:
    def __init__(self):
        # secrets.json에서 설정 로드
        credentials = get_credentials()
        kiwoom_config = credentials.get_kiwoom_config()

        self.base_url = kiwoom_config['base_url']
        self.appkey = kiwoom_config['appkey']
        self.secretkey = kiwoom_config['secretkey']
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
print("시장탐색 직접 테스트 (전체 응답 출력)")
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
    print(f"return_code: {response.get('return_code')}")
    print(f"return_msg: {response.get('return_msg')}")

    print(f"\n📋 전체 응답 구조:")
    print(json.dumps(response, indent=2, ensure_ascii=False))

    if response.get('return_code') == 0:
        # 모든 키를 순회하면서 리스트 형태의 데이터 찾기
        found_data = False
        for key, value in response.items():
            if isinstance(value, list) and len(value) > 0:
                print(f"\n✅ '{key}' 키에서 {len(value)}개 데이터 발견!")
                print(f"첫 번째 항목:")
                print(json.dumps(value[0], indent=2, ensure_ascii=False))
                found_data = True
                break

        if not found_data:
            print(f"\n⚠️ 리스트 형태의 데이터를 찾을 수 없습니다")
            print(f"응답 키: {list(response.keys())}")
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
    print(f"return_code: {response.get('return_code')}")
    print(f"return_msg: {response.get('return_msg')}")

    print(f"\n📋 전체 응답 구조:")
    print(json.dumps(response, indent=2, ensure_ascii=False))

    if response.get('return_code') == 0:
        # 모든 키를 순회하면서 리스트 형태의 데이터 찾기
        found_data = False
        for key, value in response.items():
            if isinstance(value, list) and len(value) > 0:
                print(f"\n✅ '{key}' 키에서 {len(value)}개 데이터 발견!")
                print(f"첫 번째 항목:")
                print(json.dumps(value[0], indent=2, ensure_ascii=False))
                found_data = True
                break

        if not found_data:
            print(f"\n⚠️ 리스트 형태의 데이터를 찾을 수 없습니다")
            print(f"응답 키: {list(response.keys())}")
else:
    print("\n❌ 응답 없음")

print("\n" + "="*70)
print("테스트 완료")
print("="*70)
print("\n💡 힌트:")
print("- 주말이나 장마감 후에는 데이터가 없을 수 있습니다")
print("- 응답 구조를 확인하고 올바른 키로 데이터를 추출해야 합니다")
