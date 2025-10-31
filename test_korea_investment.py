#!/usr/bin/env python3
"""
한국투자증권 OpenAPI 연결 테스트
키움증권은 한국투자증권 OpenAPI를 사용합니다
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

print("="*80)
print("한국투자증권 OpenAPI 연결 테스트")
print("(키움증권은 한국투자증권 OpenAPI를 사용)")
print("="*80)

# Credentials 확인
print("\n[1] Credentials")
from config.credentials import credentials

print(f"✓ Base URL: {credentials.KIWOOM_REST_BASE_URL}")
print(f"✓ App Key: {credentials.KIWOOM_REST_APPKEY[:40]}...")
print(f"✓ Secret Key: {credentials.KIWOOM_REST_SECRETKEY[:40]}...")
print(f"✓ Account: {credentials.ACCOUNT_NUMBER}")

# REST Client 초기화
print("\n[2] OAuth 토큰 발급")
try:
    from core.rest_client import KiwoomRESTClient
    client = KiwoomRESTClient()

    if client.token:
        print(f"✅ 토큰 발급 성공!")
        print(f"   Token: {client.token[:60]}...")
        print(f"   만료: {client.token_expiry}")
    else:
        print(f"❌ 토큰 발급 실패!")
        print(f"   에러: {client.last_error_msg}")
        sys.exit(1)

except Exception as e:
    print(f"❌ 예외 발생: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
print("✅ 연결 성공! 한국투자증권 OpenAPI가 정상 작동합니다.")
print("="*80)
