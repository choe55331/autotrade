#!/usr/bin/env python3
"""
키움증권 REST API OAuth 테스트 - 레퍼런스 저장소의 테스트 credentials 사용
"""
import sys
import json
import requests

print("="*80)
print("키움증권 REST API OAuth 테스트 (레퍼런스 저장소 credentials)")
print("="*80)

# test_api_curl.sh에서 발견한 테스트 credentials
test_credentials = {
    "name": "Reference repo test credentials",
    "appkey": "hpgmwXghUAL5-NciJDy9AU7_fj0IbFc4S4gJxM-WbmM",
    "secretkey": "VQTkpTT0gWaSdOcL7XTvPeIPi4BhNyYDBDho68VD5gI",
    "base_url": "https://mockapi.kiwoom.com"
}

print(f"\n테스트 credentials: {test_credentials['name']}")
print(f"App Key: {test_credentials['appkey'][:40]}...")
print(f"Secret Key: {test_credentials['secretkey'][:40]}...")
print(f"Base URL: {test_credentials['base_url']}")

endpoint = "/oauth2/token"
url = f"{test_credentials['base_url']}{endpoint}"

headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "api-id": "au10001",
    "User-Agent": "KiwoomTradingBot/1.0"
}

data = {
    "grant_type": "client_credentials",
    "appkey": test_credentials['appkey'],
    "secretkey": test_credentials['secretkey']
}

print(f"\n[OAuth 토큰 요청]")
print(f"URL: {url}")

try:
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
                print(f"\n✅ 토큰 발급 성공!")
                print(f"Token: {token[:60]}...")
                print(f"Token Type: {result.get('token_type', 'N/A')}")
                print(f"Expires: {result.get('expires_dt') or result.get('access_token_token_expired', 'N/A')}")

                # 이제 실제 API 테스트 - 시장 랭킹 조회
                print(f"\n{'='*80}")
                print("실제 데이터 테스트 - 거래량 순위 조회")
                print(f"{'='*80}")

                ranking_url = f"{test_credentials['base_url']}/api/dostk/rkinfo"
                ranking_headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json;charset=UTF-8",
                    "api-id": "ka10030",
                    "User-Agent": "KiwoomTradingBot/1.0"
                }

                ranking_data = {
                    "mrkt_tp": "000",
                    "sort_tp": "1",
                    "mang_stk_incls": "0",
                    "crd_tp": "0",
                    "trde_qty_tp": "0",
                    "pric_tp": "0",
                    "trde_prica_tp": "0",
                    "mrkt_open_tp": "0",
                    "stex_tp": "1"
                }

                print(f"\n요청 URL: {ranking_url}")
                print(f"API ID: ka10030 (거래량 상위)")

                ranking_response = requests.post(
                    ranking_url,
                    json=ranking_data,
                    headers=ranking_headers,
                    timeout=30
                )

                print(f"\n응답 상태: HTTP {ranking_response.status_code}")

                if ranking_response.status_code == 200:
                    ranking_result = ranking_response.json()
                    print(f"\n✅ 실제 데이터 조회 성공!")
                    print(f"\n응답 데이터 구조:")
                    print(json.dumps(ranking_result, indent=2, ensure_ascii=False)[:1000])
                    print("...")
                else:
                    print(f"\n❌ 데이터 조회 실패:")
                    print(ranking_response.text[:500])
            else:
                print(f"\n❌ 토큰이 응답에 없습니다")
        else:
            print(f"\n❌ HTTP {response.status_code} 오류")
    else:
        text = response.text[:1000]
        print(f"\n응답 내용:")
        print(text)

        if 'text/html' in content_type:
            print(f"\n❌ HTML 응답 - Mock API 서버 문제")
        elif '403' in text or 'Access denied' in text:
            print(f"\n❌ 403 Access denied - credentials 문제")
        else:
            print(f"\n❌ 예상치 못한 Content-Type: {content_type}")

except requests.exceptions.Timeout:
    print(f"\n❌ 타임아웃 (30초)")
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ 연결 오류: {e}")
except Exception as e:
    print(f"\n❌ 예외: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*80}")
print("테스트 완료")
print("="*80)
