"""
api/account.py
계좌 관련 API (account_info, chart 등 통합)
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class AccountAPI:
    """
    계좌 관련 API
    
    통합된 기능:
    - 계좌 정보 조회
    - 잔고 조회
    - 주문 체결 내역
    - 예수금 조회
    - 차트 데이터 조회
    """
    
    def __init__(self, client):
        """
        AccountAPI 초기화
        
        Args:
            client: KiwoomRESTClient 인스턴스
        """
        self.client = client
        logger.info("AccountAPI 초기화 완료")
    
    def get_balance(self, account_number: str = None) -> Optional[Dict[str, Any]]:
        """
        계좌 잔고 조회
        
        Args:
            account_number: 계좌번호 (None이면 기본 계좌)
        
        Returns:
            잔고 정보 딕셔너리
        """
        if not account_number:
            account_info = self.client.get_account_info()
            account_number = account_info['account_number']
        
        # 계좌번호 파싱
        parts = account_number.split('-')
        account_prefix = parts[0]
        account_suffix = parts[1] if len(parts) > 1 else '01'
        
        body = {
            "account_code": account_prefix,
            "account_suffix": account_suffix
        }
        
        response = self.client.request(
            api_id="DOSK_0059",
            body=body,
            path="/api/dostk/inquire/balance"
        )
        
        if response and response.get('return_code') == 0:
            logger.info("잔고 조회 성공")
            return response.get('output', {})
        else:
            logger.error(f"잔고 조회 실패: {response.get('return_msg')}")
            return None
    
    def get_deposit(self, account_number: str = None) -> Optional[Dict[str, Any]]:
        """
        예수금 조회
        
        Args:
            account_number: 계좌번호
        
        Returns:
            예수금 정보
        """
        if not account_number:
            account_info = self.client.get_account_info()
            account_number = account_info['account_number']
        
        parts = account_number.split('-')
        account_prefix = parts[0]
        account_suffix = parts[1] if len(parts) > 1 else '01'
        
        body = {
            "account_code": account_prefix,
            "account_suffix": account_suffix
        }
        
        response = self.client.request(
            api_id="DOSK_0085",
            body=body,
            path="/api/dostk/inquire/deposit"
        )
        
        if response and response.get('return_code') == 0:
            output = response.get('output', {})
            logger.info(f"예수금 조회 성공: {output.get('deposit_available', 0):,}원")
            return output
        else:
            logger.error(f"예수금 조회 실패: {response.get('return_msg')}")
            return None
    
    def get_holdings(self, account_number: str = None) -> List[Dict[str, Any]]:
        """
        보유 종목 조회
        
        Args:
            account_number: 계좌번호
        
        Returns:
            보유 종목 리스트
        """
        balance = self.get_balance(account_number)
        
        if not balance:
            return []
        
        holdings = []
        output_list = balance.get('output1', [])
        
        for item in output_list:
            holding = {
                'stock_code': item.get('stock_code', ''),
                'stock_name': item.get('stock_name', ''),
                'quantity': int(item.get('quantity', 0)),
                'purchase_price': float(item.get('purchase_price', 0)),
                'current_price': float(item.get('current_price', 0)),
                'profit_loss': float(item.get('profit_loss', 0)),
                'profit_loss_rate': float(item.get('profit_loss_rate', 0)),
                'evaluation_amount': float(item.get('evaluation_amount', 0)),
            }
            holdings.append(holding)
        
        logger.info(f"보유 종목 {len(holdings)}개 조회 완료")
        return holdings
    
    def get_execution_history(
        self,
        account_number: str = None,
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict[str, Any]]:
        """
        주문 체결 내역 조회
        
        Args:
            account_number: 계좌번호
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)
        
        Returns:
            체결 내역 리스트
        """
        if not account_number:
            account_info = self.client.get_account_info()
            account_number = account_info['account_number']
        
        parts = account_number.split('-')
        account_prefix = parts[0]
        account_suffix = parts[1] if len(parts) > 1 else '01'
        
        # 날짜 기본값 설정
        if not start_date:
            start_date = datetime.now().strftime('%Y%m%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        
        body = {
            "account_code": account_prefix,
            "account_suffix": account_suffix,
            "start_date": start_date,
            "end_date": end_date
        }
        
        response = self.client.request(
            api_id="DOSK_0058",
            body=body,
            path="/api/dostk/inquire/execution"
        )
        
        if response and response.get('return_code') == 0:
            executions = response.get('output', [])
            logger.info(f"체결 내역 {len(executions)}건 조회 완료")
            return executions
        else:
            logger.error(f"체결 내역 조회 실패: {response.get('return_msg')}")
            return []
    
    def get_order_history(
        self,
        account_number: str = None,
        order_date: str = None
    ) -> List[Dict[str, Any]]:
        """
        주문 내역 조회
        
        Args:
            account_number: 계좌번호
            order_date: 주문일 (YYYYMMDD)
        
        Returns:
            주문 내역 리스트
        """
        if not account_number:
            account_info = self.client.get_account_info()
            account_number = account_info['account_number']
        
        parts = account_number.split('-')
        account_prefix = parts[0]
        account_suffix = parts[1] if len(parts) > 1 else '01'
        
        if not order_date:
            order_date = datetime.now().strftime('%Y%m%d')
        
        body = {
            "account_code": account_prefix,
            "account_suffix": account_suffix,
            "order_date": order_date
        }
        
        response = self.client.request(
            api_id="DOSK_0057",
            body=body,
            path="/api/dostk/inquire/order"
        )
        
        if response and response.get('return_code') == 0:
            orders = response.get('output', [])
            logger.info(f"주문 내역 {len(orders)}건 조회 완료")
            return orders
        else:
            logger.error(f"주문 내역 조회 실패: {response.get('return_msg')}")
            return []
    
    def get_chart_data(
        self,
        stock_code: str,
        period: str = 'D',
        count: int = 100
    ) -> List[Dict[str, Any]]:
        """
        차트 데이터 조회
        
        Args:
            stock_code: 종목코드
            period: 기간 ('D': 일봉, 'W': 주봉, 'M': 월봉, '1': 1분, '5': 5분 등)
            count: 조회 개수
        
        Returns:
            차트 데이터 리스트
        """
        body = {
            "stock_code": stock_code,
            "period_code": period,
            "count": count
        }
        
        response = self.client.request(
            api_id="DOSK_0001",
            body=body,
            path="/api/dostk/inquire/chart"
        )
        
        if response and response.get('return_code') == 0:
            chart_data = response.get('output', [])
            logger.info(f"{stock_code} 차트 데이터 {len(chart_data)}개 조회 완료")
            return chart_data
        else:
            logger.error(f"차트 데이터 조회 실패: {response.get('return_msg')}")
            return []
    
    def get_daily_profit_loss(
        self,
        account_number: str = None,
        date: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        일별 손익 조회
        
        Args:
            account_number: 계좌번호
            date: 조회일 (YYYYMMDD)
        
        Returns:
            손익 정보
        """
        if not account_number:
            account_info = self.client.get_account_info()
            account_number = account_info['account_number']
        
        parts = account_number.split('-')
        account_prefix = parts[0]
        account_suffix = parts[1] if len(parts) > 1 else '01'
        
        if not date:
            date = datetime.now().strftime('%Y%m%d')
        
        body = {
            "account_code": account_prefix,
            "account_suffix": account_suffix,
            "date": date
        }
        
        response = self.client.request(
            api_id="DOSK_0086",
            body=body,
            path="/api/dostk/inquire/daily_profit_loss"
        )
        
        if response and response.get('return_code') == 0:
            profit_loss = response.get('output', {})
            logger.info(f"일별 손익 조회 완료: {profit_loss.get('profit_loss', 0):,}원")
            return profit_loss
        else:
            logger.error(f"일별 손익 조회 실패: {response.get('return_msg')}")
            return None
    
    def get_account_summary(self, account_number: str = None) -> Dict[str, Any]:
        """
        계좌 요약 정보 조회 (예수금 + 잔고)
        
        Args:
            account_number: 계좌번호
        
        Returns:
            계좌 요약 정보
        """
        deposit = self.get_deposit(account_number)
        balance = self.get_balance(account_number)
        
        summary = {
            'deposit_available': 0,
            'total_evaluation': 0,
            'total_profit_loss': 0,
            'total_profit_loss_rate': 0.0,
            'holdings_count': 0,
        }
        
        if deposit:
            summary['deposit_available'] = float(deposit.get('deposit_available', 0))
        
        if balance:
            output2 = balance.get('output2', {})
            summary['total_evaluation'] = float(output2.get('total_evaluation', 0))
            summary['total_profit_loss'] = float(output2.get('total_profit_loss', 0))
            summary['total_profit_loss_rate'] = float(output2.get('total_profit_loss_rate', 0))
            
            holdings = balance.get('output1', [])
            summary['holdings_count'] = len(holdings)
        
        summary['total_assets'] = summary['deposit_available'] + summary['total_evaluation']
        
        logger.info(f"계좌 요약 조회 완료: 총 자산 {summary['total_assets']:,.0f}원")
        return summary


__all__ = ['AccountAPI']