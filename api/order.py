"""
api/order.py
주문 관련 API
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class OrderAPI:
    """
    주문 관련 API
    
    주요 기능:
    - 매수/매도 주문
    - 정정/취소 주문
    - 주문 조회
    """
    
    def __init__(self, client):
        """
        OrderAPI 초기화
        
        Args:
            client: KiwoomRESTClient 인스턴스
        """
        self.client = client
        logger.info("OrderAPI 초기화 완료")
    
    def buy(
        self,
        stock_code: str,
        quantity: int,
        price: int,
        order_type: str = '00',
        account_number: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        매수 주문
        
        Args:
            stock_code: 종목코드
            quantity: 주문수량
            price: 주문가격 (시장가는 0)
            order_type: 주문유형 ('00': 지정가, '03': 시장가)
            account_number: 계좌번호
        
        Returns:
            주문 결과
        """
        if not account_number:
            account_info = self.client.get_account_info()
            account_number = account_info['account_number']
        
        parts = account_number.split('-')
        account_prefix = parts[0]
        account_suffix = parts[1] if len(parts) > 1 else '01'
        
        body = {
            "account_code": account_prefix,
            "account_suffix": account_suffix,
            "stock_code": stock_code,
            "order_quantity": quantity,
            "order_price": price,
            "order_type": order_type,
            "buy_sell_code": "2"  # 2: 매수
        }
        
        response = self.client.request(
            api_id="DOSK_0050",
            body=body,
            path="/api/dostk/order"
        )
        
        if response and response.get('return_code') == 0:
            order_result = response.get('output', {})
            order_no = order_result.get('order_no', '')
            logger.info(f"매수 주문 성공: {stock_code} {quantity}주 @ {price:,}원 (주문번호: {order_no})")
            return order_result
        else:
            logger.error(f"매수 주문 실패: {response.get('return_msg')}")
            return None
    
    def sell(
        self,
        stock_code: str,
        quantity: int,
        price: int,
        order_type: str = '00',
        account_number: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        매도 주문
        
        Args:
            stock_code: 종목코드
            quantity: 주문수량
            price: 주문가격 (시장가는 0)
            order_type: 주문유형 ('00': 지정가, '03': 시장가)
            account_number: 계좌번호
        
        Returns:
            주문 결과
        """
        if not account_number:
            account_info = self.client.get_account_info()
            account_number = account_info['account_number']
        
        parts = account_number.split('-')
        account_prefix = parts[0]
        account_suffix = parts[1] if len(parts) > 1 else '01'
        
        body = {
            "account_code": account_prefix,
            "account_suffix": account_suffix,
            "stock_code": stock_code,
            "order_quantity": quantity,
            "order_price": price,
            "order_type": order_type,
            "buy_sell_code": "1"  # 1: 매도
        }
        
        response = self.client.request(
            api_id="DOSK_0050",
            body=body,
            path="/api/dostk/order"
        )
        
        if response and response.get('return_code') == 0:
            order_result = response.get('output', {})
            order_no = order_result.get('order_no', '')
            logger.info(f"매도 주문 성공: {stock_code} {quantity}주 @ {price:,}원 (주문번호: {order_no})")
            return order_result
        else:
            logger.error(f"매도 주문 실패: {response.get('return_msg')}")
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
        if not account_number:
            account_info = self.client.get_account_info()
            account_number = account_info['account_number']
        
        parts = account_number.split('-')
        account_prefix = parts[0]
        account_suffix = parts[1] if len(parts) > 1 else '01'
        
        body = {
            "account_code": account_prefix,
            "account_suffix": account_suffix,
            "original_order_no": order_no,
            "stock_code": stock_code,
            "order_quantity": quantity,
            "order_price": price
        }
        
        response = self.client.request(
            api_id="DOSK_0051",
            body=body,
            path="/api/dostk/order/modify"
        )
        
        if response and response.get('return_code') == 0:
            modify_result = response.get('output', {})
            logger.info(f"주문 정정 성공: {order_no}")
            return modify_result
        else:
            logger.error(f"주문 정정 실패: {response.get('return_msg')}")
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
        if not account_number:
            account_info = self.client.get_account_info()
            account_number = account_info['account_number']
        
        parts = account_number.split('-')
        account_prefix = parts[0]
        account_suffix = parts[1] if len(parts) > 1 else '01'
        
        body = {
            "account_code": account_prefix,
            "account_suffix": account_suffix,
            "original_order_no": order_no,
            "stock_code": stock_code,
            "order_quantity": quantity
        }
        
        response = self.client.request(
            api_id="DOSK_0052",
            body=body,
            path="/api/dostk/order/cancel"
        )
        
        if response and response.get('return_code') == 0:
            cancel_result = response.get('output', {})
            logger.info(f"주문 취소 성공: {order_no}")
            return cancel_result
        else:
            logger.error(f"주문 취소 실패: {response.get('return_msg')}")
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
        if not account_number:
            account_info = self.client.get_account_info()
            account_number = account_info['account_number']
        
        parts = account_number.split('-')
        account_prefix = parts[0]
        account_suffix = parts[1] if len(parts) > 1 else '01'
        
        body = {
            "account_code": account_prefix,
            "account_suffix": account_suffix,
            "order_no": order_no
        }
        
        response = self.client.request(
            api_id="DOSK_0053",
            body=body,
            path="/api/dostk/inquire/order/status"
        )
        
        if response and response.get('return_code') == 0:
            order_status = response.get('output', {})
            logger.info(f"주문 상태 조회 완료: {order_no}")
            return order_status
        else:
            logger.error(f"주문 상태 조회 실패: {response.get('return_msg')}")
            return None


__all__ = ['OrderAPI']