"""
api/order.py
주문 관련 API
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class OrderAPI:
    """
    주문 관련 API

    주요 기능:
    - 매수/매도 주문
    - 정정/취소 주문
    - 주문 조회
    - DRY RUN 모드 지원 (실제 주문 없이 시뮬레이션)
    """

    def __init__(self, client, dry_run=False):
        """
        OrderAPI 초기화

        Args:
            client: KiwoomRESTClient 인스턴스
            dry_run: True면 실제 주문 없이 시뮬레이션만 수행 (기본값: False - 실제 주문 실행)
        """
        self.client = client
        self.dry_run = dry_run
        self.simulated_orders = []  # dry_run 모드의 주문 기록

        mode = "DRY RUN (시뮬레이션)" if dry_run else "LIVE (실제 주문)"
        logger.info(f"OrderAPI 초기화 완료 - 모드: {mode}")

        if dry_run:
            logger.warning("⚠️  DRY RUN 모드 활성화 - 실제 주문이 실행되지 않습니다")
        else:
            logger.info("✅ LIVE 모드 활성화 - 실제 주문이 API로 전송됩니다")

    def buy(
        self,
        stock_code: str,
        quantity: int,
        price: int,
        order_type: str = '02',  # 02: 지정가
        account_number: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        매수 주문

        Args:
            stock_code: 종목코드
            quantity: 주문수량
            price: 주문가격 (시장가는 0)
            order_type: 주문유형 ('01': 시장가, '02': 지정가)
            account_number: 계좌번호

        Returns:
            주문 결과
        """
        if self.dry_run:
            return self._simulate_buy(stock_code, quantity, price, order_type)

        # 실제 매수 주문 API 호출 (kt10000: 주식매수주문)
        logger.info(f"🔵 실제 매수 주문 실행: {stock_code} {quantity}주 @ {price:,}원")

        try:
            # 주문 파라미터 구성
            # trde_tp: 거래유형 (키움 API 문서 참조)
            # - 0: 보통(지정가)
            # - 3: 시장가
            # - 61: 장시작전시간외
            # - 62: 시간외단일가
            # - 81: 장마감후시간외
            # order_type을 trde_tp로 매핑
            if order_type == '62':
                trde_tp = '62'  # 시간외단일가
            elif order_type == '81':
                trde_tp = '81'  # 장마감후시간외
            elif order_type == '61':
                trde_tp = '61'  # 장시작전시간외
            elif order_type in ['00', '02', '0']:
                trde_tp = '0'  # 보통(지정가) - 앞의 0 제거!
            elif order_type in ['01', '3']:
                trde_tp = '3'  # 시장가 - 3으로 변환!
            else:
                trde_tp = order_type  # 그대로 사용

            # dmst_stex_tp: 시간외 거래(61,62,81)는 NXT, 일반 거래는 KRX
            if trde_tp in ['61', '62', '81']:
                dmst_stex_tp = 'NXT'
            else:
                dmst_stex_tp = 'KRX'

            # ord_uv(주문단가): 시장가(3) 또는 시간외 거래(61,62,81)는 빈 문자열
            # 단일가 매매는 시스템이 자동으로 가격 결정
            if trde_tp in ['3', '61', '62', '81']:
                ord_uv_value = ""
                logger.info(f"⚠️ {trde_tp} 거래유형은 가격 지정 없음 (단일가/시장가)")
            else:
                ord_uv_value = str(price)

            body_params = {
                "dmst_stex_tp": dmst_stex_tp,
                "stk_cd": stock_code,
                "ord_qty": str(quantity),
                "ord_uv": ord_uv_value,
                "trde_tp": trde_tp
            }

            logger.info(f"📋 주문 파라미터: order_type={order_type} → trde_tp={trde_tp}, dmst_stex_tp={dmst_stex_tp}, ord_uv={ord_uv_value}")
            print(f"📋 DEBUG: body_params={body_params}")

            # API 호출
            result = self.client.request(
                api_id='kt10000',
                body=body_params,
                path='/api/dostk/ordr'
            )

            if result and result.get('return_code') == 0:
                order_no = result.get('ord_no', 'N/A')
                logger.info(f"✅ 매수 주문 성공: 주문번호 {order_no}")
                return {
                    'order_no': order_no,
                    'stock_code': stock_code,
                    'quantity': quantity,
                    'price': price,
                    'status': 'ordered',
                    'result': result
                }
            else:
                error_msg = result.get('return_msg', '알 수 없는 오류') if result else '응답 없음'
                logger.error(f"❌ 매수 주문 실패: {error_msg}")
                return {
                    'order_no': None,
                    'stock_code': stock_code,
                    'quantity': quantity,
                    'price': price,
                    'status': 'failed',
                    'error': error_msg,
                    'result': result
                }

        except Exception as e:
            logger.error(f"매수 주문 예외 발생: {e}", exc_info=True)
            return {
                'order_no': None,
                'stock_code': stock_code,
                'quantity': quantity,
                'price': price,
                'status': 'error',
                'error': str(e)
            }

    def sell(
        self,
        stock_code: str,
        quantity: int,
        price: int,
        order_type: str = '02',  # 02: 지정가
        account_number: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        매도 주문

        Args:
            stock_code: 종목코드
            quantity: 주문수량
            price: 주문가격 (시장가는 0)
            order_type: 주문유형 ('01': 시장가, '02': 지정가)
            account_number: 계좌번호

        Returns:
            주문 결과
        """
        if self.dry_run:
            return self._simulate_sell(stock_code, quantity, price, order_type)

        # 실제 매도 주문 API 호출 (kt10001: 주식매도주문)
        logger.info(f"🔴 실제 매도 주문 실행: {stock_code} {quantity}주 @ {price:,}원")

        try:
            # 주문 파라미터 구성
            # trde_tp: 거래유형 (키움 API 문서 참조)
            # - 0: 보통(지정가)
            # - 3: 시장가
            # - 61: 장시작전시간외
            # - 62: 시간외단일가
            # - 81: 장마감후시간외
            # order_type을 trde_tp로 매핑
            if order_type == '62':
                trde_tp = '62'  # 시간외단일가
            elif order_type == '81':
                trde_tp = '81'  # 장마감후시간외
            elif order_type == '61':
                trde_tp = '61'  # 장시작전시간외
            elif order_type in ['00', '02', '0']:
                trde_tp = '0'  # 보통(지정가) - 앞의 0 제거!
            elif order_type in ['01', '3']:
                trde_tp = '3'  # 시장가 - 3으로 변환!
            else:
                trde_tp = order_type  # 그대로 사용

            # dmst_stex_tp: 시간외 거래(61,62,81)는 NXT, 일반 거래는 KRX
            if trde_tp in ['61', '62', '81']:
                dmst_stex_tp = 'NXT'
            else:
                dmst_stex_tp = 'KRX'

            # ord_uv(주문단가): 시장가(3) 또는 시간외 거래(61,62,81)는 빈 문자열
            # 단일가 매매는 시스템이 자동으로 가격 결정
            if trde_tp in ['3', '61', '62', '81']:
                ord_uv_value = ""
                logger.info(f"⚠️ {trde_tp} 거래유형은 가격 지정 없음 (단일가/시장가)")
            else:
                ord_uv_value = str(price)

            body_params = {
                "dmst_stex_tp": dmst_stex_tp,
                "stk_cd": stock_code,
                "ord_qty": str(quantity),
                "ord_uv": ord_uv_value,
                "trde_tp": trde_tp
            }

            logger.info(f"📋 주문 파라미터: order_type={order_type} → trde_tp={trde_tp}, dmst_stex_tp={dmst_stex_tp}, ord_uv={ord_uv_value}")
            print(f"📋 DEBUG: body_params={body_params}")

            # API 호출
            result = self.client.request(
                api_id='kt10001',
                body=body_params,
                path='/api/dostk/ordr'
            )

            if result and result.get('return_code') == 0:
                order_no = result.get('ord_no', 'N/A')
                logger.info(f"✅ 매도 주문 성공: 주문번호 {order_no}")
                return {
                    'order_no': order_no,
                    'stock_code': stock_code,
                    'quantity': quantity,
                    'price': price,
                    'status': 'ordered',
                    'result': result
                }
            else:
                error_msg = result.get('return_msg', '알 수 없는 오류') if result else '응답 없음'
                logger.error(f"❌ 매도 주문 실패: {error_msg}")
                return {
                    'order_no': None,
                    'stock_code': stock_code,
                    'quantity': quantity,
                    'price': price,
                    'status': 'failed',
                    'error': error_msg,
                    'result': result
                }

        except Exception as e:
            logger.error(f"매도 주문 예외 발생: {e}", exc_info=True)
            return {
                'order_no': None,
                'stock_code': stock_code,
                'quantity': quantity,
                'price': price,
                'status': 'error',
                'error': str(e)
            }

    def modify(
        self,
        order_no: str,
        stock_code: str,
        quantity: int,
        price: int,
        account_number: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        주문 정정

        Args:
            order_no: 원주문번호
            stock_code: 종목코드
            quantity: 정정수량
            price: 정정가격
            account_number: 계좌번호

        Returns:
            정정 결과
        """
        logger.warning("주문 정정 API가 아직 구현되지 않았습니다")
        return None

    def cancel(
        self,
        order_no: str,
        stock_code: str,
        quantity: int,
        account_number: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        주문 취소

        Args:
            order_no: 원주문번호
            stock_code: 종목코드
            quantity: 취소수량
            account_number: 계좌번호

        Returns:
            취소 결과
        """
        logger.warning("주문 취소 API가 아직 구현되지 않았습니다")
        return None

    def get_order_status(
        self,
        order_no: str,
        account_number: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        주문 상태 조회

        Args:
            order_no: 주문번호
            account_number: 계좌번호

        Returns:
            주문 상태
        """
        logger.warning("주문 상태 조회 API가 아직 구현되지 않았습니다")
        return None

    # ==================== DRY RUN 모드 메서드 ====================

    def _simulate_buy(self, stock_code: str, quantity: int, price: int, order_type: str):
        """매수 주문 시뮬레이션"""
        order_no = f"SIM{datetime.now().strftime('%Y%m%d%H%M%S')}"

        order = {
            "order_no": order_no,
            "stock_code": stock_code,
            "quantity": quantity,
            "price": price,
            "order_type": order_type,
            "side": "buy",
            "status": "filled",  # 시뮬레이션에서는 즉시 체결
            "timestamp": datetime.now().isoformat()
        }

        self.simulated_orders.append(order)

        logger.info(
            f"[DRY RUN] 매수 주문 시뮬레이션: {stock_code} "
            f"{quantity}주 @ {price:,}원 (주문번호: {order_no})"
        )

        return order

    def _simulate_sell(self, stock_code: str, quantity: int, price: int, order_type: str):
        """매도 주문 시뮬레이션"""
        order_no = f"SIM{datetime.now().strftime('%Y%m%d%H%M%S')}"

        order = {
            "order_no": order_no,
            "stock_code": stock_code,
            "quantity": quantity,
            "price": price,
            "order_type": order_type,
            "side": "sell",
            "status": "filled",  # 시뮬레이션에서는 즉시 체결
            "timestamp": datetime.now().isoformat()
        }

        self.simulated_orders.append(order)

        logger.info(
            f"[DRY RUN] 매도 주문 시뮬레이션: {stock_code} "
            f"{quantity}주 @ {price:,}원 (주문번호: {order_no})"
        )

        return order

    def get_simulated_orders(self):
        """시뮬레이션 주문 내역 조회"""
        return self.simulated_orders.copy()

    def clear_simulated_orders(self):
        """시뮬레이션 주문 내역 초기화"""
        self.simulated_orders.clear()
        logger.info("시뮬레이션 주문 내역 초기화")


__all__ = ['OrderAPI']
