"""
키움증권 REST API 계좌 조회 테스트
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import logging
from core import KiwoomRESTClient
from api import AccountAPI

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)


def main():
    """메인 테스트 함수"""
    print("\n" + "="*60)
    print("키움증권 REST API 테스트".center(60))
    print("="*60 + "\n")

    try:
        # 1. REST 클라이언트 초기화
        print("1️⃣ REST 클라이언트 초기화 중...")
        client = KiwoomRESTClient()

        if not client.token:
            print("❌ 토큰 발급 실패!")
            print(f"   에러: {client.last_error_msg}")
            return 1

        print(f"✅ 토큰 발급 성공")
        print(f"   만료 시간: {client.token_expiry.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   계좌번호: {client.account_number_full}\n")

        # 2. AccountAPI 초기화
        print("2️⃣ AccountAPI 초기화 중...")
        account_api = AccountAPI(client)
        print("✅ AccountAPI 초기화 완료\n")

        # 3. 예수금 조회
        print("3️⃣ 예수금 조회 중...")
        deposit = account_api.get_deposit()

        if deposit:
            print("✅ 예수금 조회 성공")
            print(f"   예수금: {deposit.get('deposit_available', 0):,}원")
            print(f"   출금 가능 금액: {deposit.get('withdraw_available', 0):,}원")
        else:
            print("❌ 예수금 조회 실패")
            print(f"   마지막 에러: {client.last_error_msg}")

        print()

        # 4. 잔고 조회
        print("4️⃣ 잔고 조회 중...")
        balance = account_api.get_balance()

        if balance:
            print("✅ 잔고 조회 성공")

            # 보유 종목
            holdings = balance.get('output1', [])
            print(f"   보유 종목: {len(holdings)}개")

            for holding in holdings[:3]:  # 최대 3개만 출력
                print(f"     - {holding.get('stock_name')} ({holding.get('stock_code')}): "
                      f"{holding.get('quantity')}주 @ {holding.get('current_price'):,}원")

            # 계좌 요약
            summary = balance.get('output2', {})
            print(f"   총 평가금액: {summary.get('total_evaluation', 0):,}원")
            print(f"   총 손익: {summary.get('total_profit_loss', 0):+,}원")
        else:
            print("❌ 잔고 조회 실패")
            print(f"   마지막 에러: {client.last_error_msg}")

        print()

        # 5. 계좌 요약
        print("5️⃣ 계좌 요약 조회 중...")
        summary = account_api.get_account_summary()

        print("✅ 계좌 요약:")
        print(f"   총 자산: {summary.get('total_assets', 0):,}원")
        print(f"   예수금: {summary.get('deposit_available', 0):,}원")
        print(f"   평가금액: {summary.get('total_evaluation', 0):,}원")
        print(f"   총 손익: {summary.get('total_profit_loss', 0):+,}원")
        print(f"   수익률: {summary.get('total_profit_loss_rate', 0):+.2f}%")
        print(f"   보유 종목: {summary.get('holdings_count', 0)}개")

        print("\n" + "="*60)
        print("✅ 모든 테스트 완료!".center(60))
        print("="*60 + "\n")

        # 클라이언트 종료
        client.close()
        return 0

    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")
        logger.exception("예외 발생")
        return 1


if __name__ == '__main__':
    sys.exit(main())
