"""
NXT 주문 테스트 (키움증권 API 문서 기반)
"""

공식 문서의 정확한 trde_tp 코드 사용:
- 61: 장시작전시간외 (프리마켓 08:00-09:00)
- 62: 시간외단일가 (NXT 시간)
- 81: 장마감후시간외 (애프터마켓 15:30-20:00)

사용법:
    python test_nxt_orders_correct.py

import json
import logging
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


class NXTOrderCorrectTest:
    """키움증권 API 문서 기반 NXT 주문 테스트"""

    def __init__(self):
        from core.rest_client import KiwoomRESTClient
        from api.account import AccountAPI
        from api.market import MarketAPI
        from utils.trading_date import is_nxt_hours, is_market_hours

        self.client = KiwoomRESTClient()
        self.account_api = AccountAPI(self.client)
        self.market_api = MarketAPI(self.client)

        self.is_nxt = is_nxt_hours()
        self.is_market = is_market_hours()

        now = datetime.now()
        self.hour = now.hour
        self.minute = now.minute

        self.results = {
            'timestamp': datetime.now().isoformat(),
            'is_nxt_time': self.is_nxt,
            'is_market_time': self.is_market,
            'current_hour': self.hour,
            'current_minute': self.minute,
            'tests': [],
            'successful_combinations': []
        }

    def get_trading_period(self) -> str:
        """현재 거래 시간대"""
        if self.hour == 8:
            return '프리마켓'
        elif 9 <= self.hour < 15 or (self.hour == 15 and self.minute <= 30):
            return '정규장'
        elif (self.hour == 15 and self.minute >= 30) or (16 <= self.hour < 20):
            return '애프터마켓'
        else:
            return '장외시간'

    def test_order(self, dmst_stex_tp: str, trde_tp: str, desc: str,
                   stock_code: str = '005930', price: int = 50000) -> Dict[str, Any]:

        logger.info(f"\n{'='*70}")
        logger.info(f"🧪 {desc}")
        logger.info(f"   dmst_stex_tp={dmst_stex_tp}, trde_tp={trde_tp}")
        logger.info(f"   종목: {stock_code}, 가격: {price:,}원")
        logger.info('='*70)

        try:
            body = {
                "dmst_stex_tp": dmst_stex_tp,
                "stk_cd": stock_code,
                "ord_qty": "1",
                "ord_uv": str(price),
                "trde_tp": trde_tp
            }

            response = self.client.request(
                api_id='kt10000',
                body=body,
                path='ordr'
            )

            success = response and response.get('return_code') == 0
            return_code = response.get('return_code') if response else None
            return_msg = response.get('return_msg') if response else 'No response'
            ord_no = response.get('ord_no') if response else None

            result = {
                'description': desc,
                'dmst_stex_tp': dmst_stex_tp,
                'trde_tp': trde_tp,
                'stock_code': stock_code,
                'success': success,
                'return_code': return_code,
                'return_msg': return_msg,
                'ord_no': ord_no
            }

            if success:
                logger.info(f"✅ 성공! 주문번호: {ord_no}")
                self.results['successful_combinations'].append({
                    'dmst_stex_tp': dmst_stex_tp,
                    'trde_tp': trde_tp,
                    'description': desc
                })
            else:
                logger.warning(f"❌ 실패: [{return_code}] {return_msg}")

            return result

        except Exception as e:
            logger.error(f"❌ 오류: {e}")
            return {
                'description': desc,
                'dmst_stex_tp': dmst_stex_tp,
                'trde_tp': trde_tp,
                'success': False,
                'error': str(e)
            }

    def run_all_tests(self):
        """모든 테스트 실행"""

        period = self.get_trading_period()

        logger.info("\n" + "="*80)
        logger.info("🎯 키움증권 API 문서 기반 NXT 주문 테스트")
        logger.info("="*80)
        logger.info(f"현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"거래 시간대: {period}")
        logger.info(f"NXT 시간: {self.is_nxt}")
        logger.info(f"정규장: {self.is_market}")

        test_cases = []

        if period == '프리마켓':
            logger.info("\n📌 프리마켓 테스트 (08:00-09:00)")
            test_cases = [
                ('KRX', '61', '📘 문서: KRX + 장시작전시간외(61)'),
                ('NXT', '61', '📘 문서: NXT + 장시작전시간외(61)'),
                ('KRX', '62', '📘 문서: KRX + 시간외단일가(62)'),
                ('NXT', '62', '📘 문서: NXT + 시간외단일가(62)'),
                ('SOR', '61', '📘 문서: SOR + 장시작전시간외(61)'),
                ('SOR', '62', '📘 문서: SOR + 시간외단일가(62)'),
            ]

        elif period == '애프터마켓':
            logger.info("\n📌 애프터마켓 테스트 (15:30-20:00)")
            test_cases = [
                ('KRX', '81', '📘 문서: KRX + 장마감후시간외(81)'),
                ('NXT', '81', '📘 문서: NXT + 장마감후시간외(81)'),
                ('KRX', '62', '📘 문서: KRX + 시간외단일가(62)'),
                ('NXT', '62', '📘 문서: NXT + 시간외단일가(62)'),
                ('SOR', '81', '📘 문서: SOR + 장마감후시간외(81)'),
                ('SOR', '62', '📘 문서: SOR + 시간외단일가(62)'),
            ]

        elif period == '정규장':
            logger.info("\n📌 정규장 테스트 (09:00-15:30)")
            test_cases = [
                ('KRX', '0', '📘 문서: KRX + 보통(0)'),
                ('KRX', '3', '📘 문서: KRX + 시장가(3)'),
                ('NXT', '0', '🧪 실험: NXT + 보통(0)'),
            ]

        else:
            logger.warning("⚠️  장외 시간입니다.")
            logger.info("애프터마켓 조합으로 테스트합니다...")
            test_cases = [
                ('KRX', '81', '📘 문서: KRX + 장마감후시간외(81)'),
                ('NXT', '81', '📘 문서: NXT + 장마감후시간외(81)'),
                ('KRX', '62', '📘 문서: KRX + 시간외단일가(62)'),
                ('NXT', '62', '📘 문서: NXT + 시간외단일가(62)'),
            ]

        logger.info("\n" + "="*80)
        logger.info("⚠️  실제 주문이 발생합니다!")
        logger.info("="*80)
        logger.info(f"테스트 수: {len(test_cases)}개")
        logger.info(f"종목: 삼성전자 (005930)")
        logger.info(f"수량: 1주 × {len(test_cases)}회")
        logger.info(f"예상 금액: 약 {50000 * len(test_cases):,}원\n")

        user_input = input("계속하시겠습니까? (yes/no): ")
        if user_input.lower() != 'yes':
            logger.info("테스트를 취소합니다.")
            return

        for dmst, trde, desc in test_cases:
            result = self.test_order(dmst, trde, desc)
            self.results['tests'].append(result)

        self.print_summary()
        self.save_results()

    def print_summary(self):
        """결과 요약"""
        logger.info("\n" + "="*80)
        logger.info("📊 테스트 결과")
        logger.info("="*80)

        tests = self.results['tests']
        success_tests = [t for t in tests if t.get('success')]

        logger.info(f"\n총 {len(tests)}개 테스트 중 {len(success_tests)}개 성공")

        if success_tests:
            logger.info("\n✅ 성공한 조합:")
            for test in success_tests:
                logger.info(f"\n   🎯 {test['description']}")
                logger.info(f"      dmst_stex_tp={test['dmst_stex_tp']}")
                logger.info(f"      trde_tp={test['trde_tp']}")
                logger.info(f"      주문번호: {test['ord_no']}")

            best = success_tests[0]
            logger.info("\n" + "="*80)
            logger.info("💡 권장 코드 (api/order.py)")
            logger.info("="*80)

            period = self.get_trading_period()

            if period == '프리마켓':
                logger.info(f"""
dmst_stex_tp = "{best['dmst_stex_tp']}"
trde_tp = "{best['trde_tp']}"
            elif period == '애프터마켓':
                logger.info(f"""
dmst_stex_tp = "{best['dmst_stex_tp']}"
trde_tp = "{best['trde_tp']}"
            else:
                logger.info(f"""
dmst_stex_tp = "{best['dmst_stex_tp']}"
trde_tp = "{best['trde_tp']}"

        else:
            logger.warning("\n❌ 성공한 조합이 없습니다.")

            error_msgs = {}
            for test in tests:
                msg = test.get('return_msg', test.get('error', 'Unknown'))
                if msg not in error_msgs:
                    error_msgs[msg] = []
                error_msgs[msg].append(test['description'])

            logger.info("\n오류 메시지:")
            for msg, descs in error_msgs.items():
                logger.info(f"\n   ❌ {msg}")
                for desc in descs:
                    logger.info(f"      - {desc}")

    def save_results(self):
        """결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_nxt_correct_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        logger.info(f"\n💾 결과 저장: {filename}")


def main():
    """메인"""
    print("\n" + "="*80)
    print("📘 키움증권 API 문서 기반 NXT 주문 테스트")
    print("="*80)
    print("\n✅ 공식 문서의 정확한 trde_tp 코드 사용:")
    print("   61: 장시작전시간외 (프리마켓)")
    print("   62: 시간외단일가 (NXT)")
    print("   81: 장마감후시간외 (애프터마켓)")
    print("\n⚠️  이전 테스트에서 사용하지 않은 코드들입니다!")
    print("="*80 + "\n")

    tester = NXTOrderCorrectTest()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
