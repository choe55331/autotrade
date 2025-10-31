#!/usr/bin/env python3
"""
키움증권 REST API OAuth 토큰 발급 테스트
.NET 및 Python 레퍼런스 구현을 참조하여 정확한 형식으로 테스트
"""
import sys
import json
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

print("="*80)
print("키움증권 REST API OAuth 토큰 발급 테스트")
print("="*80)

# Credentials 로드
print("\n[1] Credentials 로드")
from config.credentials import credentials

print(f"✓ Base URL: {credentials.KIWOOM_REST_BASE_URL}")
print(f"✓ App Key: {credentials.KIWOOM_REST_APPKEY[:40]}...")
print(f"✓ Secret Key: {credentials.KIWOOM_REST_SECRETKEY[:40]}...")

# 레퍼런스 구현을 참조한 정확한 형식
print("\n[2] OAuth 토큰 발급 시도")

# Base URL 정규화 (trailing slash 추가)
base_url = credentials.KIWOOM_REST_BASE_URL
if not base_url.endswith('/'):
    base_url += '/'

endpoint = "/oauth2/token"
url = f"{base_url.rstrip('/')}{endpoint}"

print(f"URL: {url}")

# 헤더 (레퍼런스 구현 참조)
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "api-id": "au10001",
    "User-Agent": "KiwoomTradingBot/1.0"
}

# 요청 데이터 (레퍼런스 구현 참조)
data = {
    "grant_type": "client_credentials",
    "appkey": credentials.KIWOOM_REST_APPKEY,
    "secretkey": credentials.KIWOOM_REST_SECRETKEY
}

print(f"\n요청 헤더:")
for key, value in headers.items():
    print(f"  {key}: {value}")

print(f"\n요청 데이터:")
print(f"  grant_type: {data['grant_type']}")
print(f"  appkey: {data['appkey'][:40]}...")
print(f"  secretkey: {data['secretkey'][:40]}...")

try:
    print("\n[3] API 호출 중...")
    response = requests.post(url, json=data, headers=headers, timeout=30)

    print(f"\n응답 상태 코드: {response.status_code}")
    print(f"응답 헤더:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")

    print(f"\n응답 내용:")

    # Content-Type 확인
    content_type = response.headers.get('Content-Type', '')

    if 'application/json' in content_type:
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if response.status_code == 200:
            token = result.get('token') or result.get('access_token')
            if token:
                print(f"\n✅ 토큰 발급 성공!")
                print(f"Token: {token[:60]}...")
                print(f"Token Type: {result.get('token_type', 'N/A')}")
                print(f"Expires: {result.get('expires_dt') or result.get('access_token_token_expired', 'N/A')}")
            else:
                print(f"\n❌ 토큰이 응답에 없습니다")
        else:
            print(f"\n❌ HTTP {response.status_code} 오류")
            print(f"메시지: {result}")
    else:
        # JSON이 아닌 응답
        text = response.text[:1000]
        print(text)

        if 'text/html' in content_type:
            print(f"\n❌ HTML 응답 수신 - Mock API 서버 문제일 수 있음")
            print(f"해결 방법:")
            print(f"1. Mock API 서버 상태 확인")
            print(f"2. 실제 운영 API URL 사용: https://api.kiwoom.com")
            print(f"3. 키움증권 고객센터 문의")
        else:
            print(f"\n❌ 예상치 못한 Content-Type: {content_type}")

except requests.exceptions.RequestException as e:
    print(f"\n❌ 네트워크 오류: {e}")
except Exception as e:
    print(f"\n❌ 예외 발생: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("테스트 완료")
print("="*80)
