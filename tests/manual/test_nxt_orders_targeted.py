"""
NXT 주문 집중 테스트 (타겟팅)

일반 테스트에서 모든 주문이 실패했으므로,
NXT 시간에 실제로 작동할 가능성이 높은 조합만 집중 테스트합니다.

사용법:
    python test_nxt_orders_targeted.py
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


class NXTOrderTargetedTest:
    """NXT 주문 집중 테스트"""

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

        # 결과 저장
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'is_nxt_time': self.is_nxt,
            'is_market_time': self.is_market,
            'current_hour': self.hour,
            'current_minute': self.minute,
            'tests': []
        }

    def get_current_trading_period(self) -> str:
        """현재 거래 시간대 판별"""
        if self.hour == 8:
            return '프리마켓'
        elif 9 <= self.hour < 15 or (self.hour == 15 and self.minute <= 30):
            return '정규장'
        elif (self.hour == 15 and self.minute >= 30) or (16 <= self.hour < 20):
            return '애프터마켓'
        else:
            return '장외시간'

    def get_test_stock(self) -> tuple:
        """테스트용 종목 선택 (보유종목 중 선택)"""
        try:
            holdings = self.account_api.get_holdings()
            if holdings and len(holdings) > 0:
                # 첫 번째 보유종목 사용
                stock = holdings[0]
                stock_code = str(stock.get('stk_cd', '')).strip()
                if stock_code.startswith('A'):
                    stock_code = stock_code[1:]
                stock_name = stock.get('stk_nm', '')

                logger.info(f"✅ 테스트 종목: {stock_name} ({stock_code}) - 보유종목")
                return stock_code, stock_name

        except Exception as e:
            logger.warning(f"보유종목 조회 실패: {e}")

        # 기본값: 삼성전자
        logger.info("✅ 테스트 종목: 삼성전자 (005930) - 기본값")
        return '005930', '삼성전자'

    def get_appropriate_price(self, stock_code: str) -> int:
        """적절한 주문 가격 산정"""
        try:
            # 현재가 조회
            price_info = self.market_api.get_stock_price(stock_code)
            if price_info and price_info.get('current_price', 0) > 0:
                current_price = price_info['current_price']
                # 현재가보다 약간 낮은 가격 (매수 가능성 높임)
                order_price = int(current_price * 0.98)  # 2% 낮게
                logger.info(f"현재가: {current_price:,}원 → 주문가: {order_price:,}원")
                return order_price

        except Exception as e:
            logger.warning(f"현재가 조회 실패: {e}")

        # 기본값
        return 50000

    def test_order(self, dmst_stex_tp: str, trde_tp: str, desc: str,
                   stock_code: str, stock_name: str, price: int, quantity: int = 1) -> Dict[str, Any]:
        """주문 테스트"""

        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 테스트: {desc}")
        logger.info(f"   dmst_stex_tp={dmst_stex_tp}, trde_tp={trde_tp}")
        logger.info(f"   종목: {stock_name} ({stock_code})")
        logger.info(f"   수량: {quantity}주, 가격: {price:,}원")
        logger.info('='*60)

        try:
            body = {
                "dmst_stex_tp": dmst_stex_tp,
                "stk_cd": stock_code,
                "ord_qty": str(quantity),
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
                'stock_name': stock_name,
                'quantity': quantity,
                'price': price,
                'success': success,
                'return_code': return_code,
                'return_msg': return_msg,
                'ord_no': ord_no,
                'full_response': response
            }

            if success:
                logger.info(f"✅ 성공! 주문번호: {ord_no}")
                logger.info(f"   응답: {return_msg}")
            else:
                logger.warning(f"❌ 실패: [{return_code}] {return_msg}")

            return result

        except Exception as e:
            logger.error(f"❌ 오류 발생: {e}")
            return {
                'description': desc,
                'dmst_stex_tp': dmst_stex_tp,
                'trde_tp': trde_tp,
                'success': False,
                'error': str(e)
            }

    def run_premarket_tests(self, stock_code: str, stock_name: str, price: int):
        """프리마켓 테스트 (08:00-09:00)"""
        logger.info("\n" + "="*80)
        logger.info("🌅 프리마켓 주문 테스트 (08:00-09:00)")
        logger.info("="*80)

        test_cases = [
            ('NXT', '10', 'NXT 장전시간외'),
            ('NXT', '20', 'NXT 장전시간외우선'),
            ('NXT', '16', 'NXT 시간외단일가'),
            ('KRX', '10', 'KRX 장전시간외'),
            ('KRX', '16', 'KRX 시간외단일가'),
        ]

        for dmst, trde, desc in test_cases:
            result = self.test_order(dmst, trde, desc, stock_code, stock_name, price)
            self.results['tests'].append(result)

    def run_aftermarket_tests(self, stock_code: str, stock_name: str, price: int):
        """애프터마켓 테스트 (15:30-20:00)"""
        logger.info("\n" + "="*80)
        logger.info("🌆 애프터마켓 주문 테스트 (15:30-20:00)")
        logger.info("="*80)

        test_cases = [
            ('NXT', '13', 'NXT 장후시간외'),
            ('NXT', '23', 'NXT 장후시간외우선'),
            ('NXT', '16', 'NXT 시간외단일가'),
            ('NXT', '26', 'NXT 시간외단일가우선'),
            ('KRX', '13', 'KRX 장후시간외'),
            ('KRX', '16', 'KRX 시간외단일가'),
            ('SOR', '13', 'SOR 장후시간외'),
            ('SOR', '16', 'SOR 시간외단일가'),
        ]

        for dmst, trde, desc in test_cases:
            result = self.test_order(dmst, trde, desc, stock_code, stock_name, price)
            self.results['tests'].append(result)

    def run_regular_market_tests(self, stock_code: str, stock_name: str, price: int):
        """정규장 테스트 (09:00-15:30)"""
        logger.info("\n" + "="*80)
        logger.info("📈 정규장 주문 테스트 (09:00-15:30)")
        logger.info("="*80)

        test_cases = [
            ('KRX', '0', 'KRX 지정가'),
            ('KRX', '3', 'KRX 시장가'),
            ('KRX', '5', 'KRX 조건부지정가'),
            ('KRX', '6', 'KRX 최유리지정가'),
            ('NXT', '0', 'NXT 지정가 (테스트)'),
        ]

        for dmst, trde, desc in test_cases:
            result = self.test_order(dmst, trde, desc, stock_code, stock_name, price)
            self.results['tests'].append(result)

    def run(self):
        """테스트 실행"""
        logger.info("\n" + "="*80)
        logger.info("🎯 NXT 주문 집중 테스트")
        logger.info("="*80)

        now = datetime.now()
        logger.info(f"현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}")

        period = self.get_current_trading_period()
        logger.info(f"거래 시간대: {period}")
        logger.info(f"NXT 시간: {self.is_nxt}")
        logger.info(f"정규장 시간: {self.is_market}")

        # 테스트 종목 및 가격 선택
        stock_code, stock_name = self.get_test_stock()
        price = self.get_appropriate_price(stock_code)

        # 확인
        logger.info("\n" + "="*80)
        logger.info("⚠️  실제 주문이 발생합니다!")
        logger.info("="*80)
        logger.info(f"종목: {stock_name} ({stock_code})")
        logger.info(f"수량: 1주")
        logger.info(f"가격: {price:,}원")
        logger.info(f"예상 금액: 약 {price:,}원\n")

        user_input = input("계속하시겠습니까? (yes/no): ")
        if user_input.lower() != 'yes':
            logger.info("테스트를 취소합니다.")
            return

        # 시간대별 테스트 실행
        if period == '프리마켓':
            self.run_premarket_tests(stock_code, stock_name, price)
        elif period == '애프터마켓':
            self.run_aftermarket_tests(stock_code, stock_name, price)
        elif period == '정규장':
            self.run_regular_market_tests(stock_code, stock_name, price)
        else:
            logger.warning("⚠️  장외 시간입니다. NXT 시간(08:00-09:00, 15:30-20:00) 또는 정규장(09:00-15:30)에 실행하세요.")
            # 그래도 애프터마켓 조합 테스트
            logger.info("\n애프터마켓 조합으로 테스트를 시도합니다...")
            self.run_aftermarket_tests(stock_code, stock_name, price)

        # 결과 요약
        self.print_summary()

        # 결과 저장
        self.save_results()

    def print_summary(self):
        """결과 요약 출력"""
        logger.info("\n" + "="*80)
        logger.info("📊 테스트 결과 요약")
        logger.info("="*80)

        tests = self.results.get('tests', [])
        success_tests = [t for t in tests if t.get('success')]

        logger.info(f"\n총 {len(tests)}개 테스트 중 {len(success_tests)}개 성공")

        if success_tests:
            logger.info("\n✅ 성공한 조합:")
            for test in success_tests:
                logger.info(f"\n   📌 {test['description']}")
                logger.info(f"      dmst_stex_tp={test['dmst_stex_tp']}, trde_tp={test['trde_tp']}")
                logger.info(f"      주문번호: {test['ord_no']}")

            # 권장 코드
            best = success_tests[0]
            logger.info("\n" + "="*80)
            logger.info("🎯 권장 코드")
            logger.info("="*80)
            logger.info(f"""
def buy_stock_nxt(self, stock_code: str, quantity: int, price: int):
    \"\"\"NXT 시간대 매수 주문\"\"\"
    body = {{
        "dmst_stex_tp": "{best['dmst_stex_tp']}",
        "stk_cd": stock_code,
        "ord_qty": str(quantity),
        "ord_uv": str(price),
        "trde_tp": "{best['trde_tp']}"
    }}

    response = self.client.request(
        api_id='kt10000',
        body=body,
        path='ordr'
    )

    return response.get('ord_no') if response.get('return_code') == 0 else None
            """)
        else:
            logger.warning("\n❌ 성공한 조합이 없습니다.")

            # 오류 분석
            error_groups = {}
            for test in tests:
                msg = test.get('return_msg', test.get('error', 'Unknown'))
                if msg not in error_groups:
                    error_groups[msg] = []
                error_groups[msg].append(test['description'])

            logger.info("\n오류 메시지별 그룹:")
            for msg, descs in error_groups.items():
                logger.info(f"\n   ❌ {msg}")
                logger.info(f"      ({len(descs)}개 조합)")

    def save_results(self):
        """결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_nxt_targeted_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        logger.info(f"\n💾 결과 저장: {filename}")


def main():
    tester = NXTOrderTargetedTest()
    tester.run()


if __name__ == "__main__":
    main()
