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

    def __init__(self, client, dry_run=True):
        """
        OrderAPI 초기화

        Args:
            client: KiwoomRESTClient 인스턴스
            dry_run: True면 실제 주문 없이 시뮬레이션만 수행
        """
        self.client = client
        self.dry_run = dry_run
        self.simulated_orders = []  # dry_run 모드의 주문 기록

        mode = "DRY RUN (시뮬레이션)" if dry_run else "LIVE (실제 주문)"
        logger.info(f"OrderAPI 초기화 완료 - 모드: {mode}")

        if dry_run:
            logger.warning("⚠️  DRY RUN 모드 활성화 - 실제 주문이 실행되지 않습니다")

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

        # 실제 주문 로직 (API ID가 확인되면 활성화)
        logger.warning("실제 주문 API가 아직 구현되지 않았습니다")
        return None

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

        # 실제 주문 로직 (API ID가 확인되면 활성화)
        logger.warning("실제 주문 API가 아직 구현되지 않았습니다")
        return None

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
