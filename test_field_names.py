"""
키움증권 REST API 필드명 테스트
여러 필드명 조합을 시도하여 올바른 형식을 찾습니다
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import logging
from core import KiwoomRESTClient

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)


def test_field_combinations(client):
    """여러 필드명 조합 테스트"""

    # 테스트할 필드명 조합들
    field_combinations = [
        # 조합 1: CANO + ACNT_PRDT_CD (키움증권 OpenAPI+ 표준)
        {
            "name": "CANO + ACNT_PRDT_CD",
            "fields": {
                "CANO": "64523232",
                "ACNT_PRDT_CD": "10"
            }
        },
        # 조합 2: account_no (전체 계좌번호)
        {
            "name": "account_no (전체)",
            "fields": {
                "account_no": "64523232-10"
            }
        },
        # 조합 3: account_number (전체)
        {
            "name": "account_number (전체)",
            "fields": {
                "account_number": "64523232-10"
            }
        },
        # 조합 4: ACNT_NO (전체)
        {
            "name": "ACNT_NO (전체)",
            "fields": {
                "ACNT_NO": "64523232-10"
            }
        },
        # 조합 5: acct_no + acct_prdt_cd
        {
            "name": "acct_no + acct_prdt_cd",
            "fields": {
                "acct_no": "64523232",
                "acct_prdt_cd": "10"
            }
        },
        # 조합 6: 현재 사용 중 (참고용)
        {
            "name": "account_code + account_suffix (현재)",
            "fields": {
                "account_code": "64523232",
                "account_suffix": "10"
            }
        },
    ]

    print("\n" + "="*70)
    print("필드명 조합 테스트 시작".center(70))
    print("="*70 + "\n")

    # 예수금 조회 API로 테스트
    api_id = "DOSK_0085"
    path = "/api/dostk/inquire/deposit"

    for idx, combo in enumerate(field_combinations, 1):
        print(f"\n[테스트 {idx}] {combo['name']}")
        print(f"  필드: {combo['fields']}")

        response = client.request(
            api_id=api_id,
            body=combo['fields'],
            path=path
        )

        if response:
            status_code = response.get('return_code', -999)

            if status_code == 0:
                print(f"  ✅ 성공! 이 필드명이 올바릅니다!")
                print(f"  응답: {response}")
                return combo
            elif str(status_code).startswith('-'):
                # HTTP 에러
                print(f"  ❌ HTTP 에러 ({status_code}): {response.get('return_msg')}")
            else:
                # API 로직 에러
                print(f"  ❌ API 에러 ({status_code}): {response.get('return_msg')}")
        else:
            print(f"  ❌ 응답 없음")

        print()

    print("="*70)
    print("⚠️  모든 필드명 조합이 실패했습니다.".center(70))
    print("="*70)
    return None


def main():
    """메인 함수"""
    print("\n" + "="*70)
    print("키움증권 REST API 필드명 테스트".center(70))
    print("="*70 + "\n")

    try:
        # REST 클라이언트 초기화
        print("REST 클라이언트 초기화 중...")
        client = KiwoomRESTClient()

        if not client.token:
            print("❌ 토큰 발급 실패!")
            return 1

        print("✅ 토큰 발급 성공\n")

        # 필드명 조합 테스트
        result = test_field_combinations(client)

        if result:
            print("\n" + "="*70)
            print("🎉 올바른 필드명을 찾았습니다!".center(70))
            print("="*70)
            print(f"\n필드명: {result['name']}")
            print(f"필드: {result['fields']}\n")
        else:
            print("\n⚠️  API 문서를 확인하여 올바른 필드명을 확인해주세요.")
            print("   혹은 다른 API ID나 경로를 시도해야 할 수 있습니다.")

        # 클라이언트 종료
        client.close()
        return 0

    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")
        logger.exception("예외 발생")
        return 1


if __name__ == '__main__':
    sys.exit(main())
