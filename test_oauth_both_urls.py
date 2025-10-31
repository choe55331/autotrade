#!/usr/bin/env python3
"""
키움증권 REST API 테스트 - 실제 API와 Mock API 모두 시도
"""
import sys
import json
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config.credentials import credentials

print("="*80)
print("키움증권 REST API - 실제 API와 Mock API 모두 테스트")
print("="*80)

# 테스트할 URL 목록
urls_to_test = [
    {
        "name": "실제 API (Real)",
        "base_url": "https://api.kiwoom.com"
    },
    {
        "name": "Mock API (Test)",
        "base_url": "https://mockapi.kiwoom.com"
    }
]

endpoint = "/oauth2/token"

# 헤더
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "api-id": "au10001",
    "User-Agent": "KiwoomTradingBot/1.0"
}

# 요청 데이터
data = {
    "grant_type": "client_credentials",
    "appkey": credentials.KIWOOM_REST_APPKEY,
    "secretkey": credentials.KIWOOM_REST_SECRETKEY
}

for url_info in urls_to_test:
    print(f"\n{'='*80}")
    print(f"테스트: {url_info['name']}")
    print(f"URL: {url_info['base_url']}{endpoint}")
    print(f"{'='*80}")

    try:
        url = f"{url_info['base_url']}{endpoint}"
        response = requests.post(url, json=data, headers=headers, timeout=30)

        print(f"\n응답 상태: HTTP {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")

        content_type = response.headers.get('Content-Type', '')

        if 'application/json' in content_type:
            result = response.json()
            print(f"\n응답 데이터:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            if response.status_code == 200:
                token = result.get('token') or result.get('access_token')
                if token:
                    print(f"\n✅ {url_info['name']}: 토큰 발급 성공!")
                    print(f"Token: {token[:60]}...")
                else:
                    print(f"\n⚠️ {url_info['name']}: 토큰 없음")
            else:
                print(f"\n❌ {url_info['name']}: HTTP {response.status_code} 오류")
        else:
            text = response.text[:500]
            print(f"\n응답 내용: {text}")
            print(f"\n❌ {url_info['name']}: JSON 응답 아님 ({content_type})")

    except requests.exceptions.Timeout:
        print(f"\n❌ {url_info['name']}: 타임아웃 (30초)")
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ {url_info['name']}: 연결 오류 - {e}")
    except Exception as e:
        print(f"\n❌ {url_info['name']}: 예외 - {e}")

print(f"\n{'='*80}")
print("결론:")
print("="*80)
print("- 두 URL 모두 403 Access denied를 반환하는 경우:")
print("  → 제공된 credentials가 유효하지 않거나 만료되었을 가능성")
print("  → 또는 API 키가 아직 활성화되지 않았을 수 있음")
print()
print("- Mock API가 HTML을 반환하는 경우:")
print("  → Mock API 서버가 다운되었거나 점검 중")
print()
print("- 한쪽만 성공하는 경우:")
print("  → 그쪽 URL을 사용하면 됨")
print("="*80)
