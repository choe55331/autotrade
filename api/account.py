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
        계좌 잔고 조회 (kt00018)

        Args:
            account_number: 계좌번호 (None이면 기본 계좌)

        Returns:
            잔고 정보 딕셔너리
        """
        # 키움증권 REST API: kt00018 (계좌평가잔고내역요청)
        # URL: /api/dostk/acnt
        # Body: {"qry_tp": "1", "dmst_stex_tp": "KRX"}  # 1: 합산, KRX: 한국거래소

        body = {
            "qry_tp": "1",           # 합산
            "dmst_stex_tp": "KRX"    # 한국거래소
        }

        response = self.client.request(
            api_id="kt00018",
            body=body,
            path="/api/dostk/acnt"
        )

        if response and response.get('return_code') == 0:
            # 응답이 바로 데이터입니다 (output으로 감싸져 있지 않음)
            logger.info("잔고 조회 성공")
            return response
        else:
            logger.error(f"잔고 조회 실패")
            if response:
                logger.error(f"  return_code: {response.get('return_code')}")
                logger.error(f"  return_msg: {response.get('return_msg')}")
                logger.error(f"  전체 응답: {response}")
            else:
                logger.error("  응답이 None입니다")
            return None
    
    def get_deposit(self, account_number: str = None) -> Optional[Dict[str, Any]]:
        """
        예수금 조회 (kt00001)

        Args:
            account_number: 계좌번호

        Returns:
            예수금 정보
        """
        # 키움증권 REST API: kt00001 (예수금상세현황요청)
        # URL: /api/dostk/acnt
        # Body: {"qry_tp": "2"}  # 2: 일반조회

        body = {
            "qry_tp": "2"  # 일반조회
        }

        response = self.client.request(
            api_id="kt00001",
            body=body,
            path="/api/dostk/acnt"
        )

        if response and response.get('return_code') == 0:
            # 응답이 바로 데이터입니다 (output으로 감싸져 있지 않음)
            # 주요 필드: ord_alow_amt (주문가능금액), pymn_alow_amt (출금가능금액)
            ord_alow_amt = int(response.get('ord_alow_amt', 0))
            logger.info(f"예수금 조회 성공: 주문가능금액 {ord_alow_amt:,}원")
            return response
        else:
            logger.error(f"예수금 조회 실패")
            if response:
                logger.error(f"  return_code: {response.get('return_code')}")
                logger.error(f"  return_msg: {response.get('return_msg')}")
                logger.error(f"  전체 응답: {response}")
            else:
                logger.error("  응답이 None입니다")
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
        # kt00018 응답 구조: acnt_evlt_remn_indv_tot (계좌평가잔고개별합산) 리스트
        output_list = balance.get('acnt_evlt_remn_indv_tot', [])

        for item in output_list:
            holding = {
                'stock_code': item.get('stk_cd', ''),        # 종목번호
                'stock_name': item.get('stk_nm', ''),        # 종목명
                'quantity': int(item.get('rmnd_qty', 0)),    # 보유수량
                'purchase_price': float(item.get('pur_pric', 0)),  # 매입가
                'current_price': float(item.get('cur_prc', 0)),    # 현재가
                'profit_loss': float(item.get('evltv_prft', 0)),   # 평가손익
                'profit_loss_rate': float(item.get('prft_rt', 0)), # 수익률(%)
                'evaluation_amount': float(item.get('evlt_amt', 0)),  # 평가금액
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
            'deposit_available': 0,      # 주문가능금액
            'total_evaluation': 0,       # 총평가금액
            'total_profit_loss': 0,      # 총평가손익금액
            'total_profit_loss_rate': 0.0,  # 총수익률(%)
            'holdings_count': 0,         # 보유종목수
            'total_assets': 0,           # 추정예탁자산
        }

        if deposit:
            # kt00001 응답: ord_alow_amt (주문가능금액)
            summary['deposit_available'] = float(deposit.get('ord_alow_amt', 0))

        if balance:
            # kt00018 응답 필드
            summary['total_evaluation'] = float(balance.get('tot_evlt_amt', 0))     # 총평가금액
            summary['total_profit_loss'] = float(balance.get('tot_evlt_pl', 0))    # 총평가손익금액
            summary['total_profit_loss_rate'] = float(balance.get('tot_prft_rt', 0))  # 총수익률(%)
            summary['total_assets'] = float(balance.get('prsm_dpst_aset_amt', 0))  # 추정예탁자산

            holdings = balance.get('acnt_evlt_remn_indv_tot', [])
            summary['holdings_count'] = len(holdings)

        logger.info(f"계좌 요약 조회 완료: 총 자산 {summary['total_assets']:,.0f}원")
        return summary


__all__ = ['AccountAPI']