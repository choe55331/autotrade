"""
api/account.py
계좌 관련 API (검증된 API 로더 통합)
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AccountAPI:
    """
    계좌 관련 API (93.5% 성공률 검증 완료)

    검증된 API 사용:
    - kt00005: 체결잔고요청
    - kt00018: 계좌평가잔고내역요청
    - ka10085: 계좌수익률요청
    - kt00001: 예수금상세현황요청
    - kt00004: 계좌평가현황요청
    - kt00010: 주문인출가능금액요청
    - 등 31개 계좌 관련 API
    """

    def __init__(self, client):
        """
        AccountAPI 초기화

        Args:
            client: KiwoomRESTClient 인스턴스
        """
        self.client = client
        logger.info("AccountAPI 초기화 완료 (검증된 API 사용)")

    def get_balance(self, market_type: str = "KRX") -> Optional[Dict[str, Any]]:
        """
        체결잔고 조회

        Args:
            market_type: 시장 구분 (KRX, NXT)

        Returns:
            체결잔고 정보
        """
        try:
            result = self.client.call_verified_api(
                api_id='kt00005',
                variant_idx=1 if market_type == "KRX" else 2
            )

            if result.get('return_code') == 0:
                logger.info(f"체결잔고 조회 성공 ({market_type})")
                return result
            else:
                logger.error(f"체결잔고 조회 실패: {result.get('return_msg')}")
                return None

        except Exception as e:
            logger.error(f"체결잔고 조회 오류: {e}")
            return None

    def get_account_balance(
        self,
        query_type: str = "2",
        market_type: str = "KRX"
    ) -> Optional[Dict[str, Any]]:
        """
        계좌평가잔고내역 조회

        Args:
            query_type: 조회구분 (1: 합산, 2: 개별)
            market_type: 시장구분 (KRX, NXT)

        Returns:
            계좌평가잔고 정보
        """
        try:
            # variant 선택
            if query_type == "2" and market_type == "KRX":
                variant_idx = 1
            elif query_type == "1" and market_type == "KRX":
                variant_idx = 2
            elif query_type == "2" and market_type == "NXT":
                variant_idx = 3
            else:  # query_type == "1" and market_type == "NXT"
                variant_idx = 4

            result = self.client.call_verified_api(
                api_id='kt00018',
                variant_idx=variant_idx
            )

            if result.get('return_code') == 0:
                logger.info(f"계좌평가잔고 조회 성공 (query={query_type}, market={market_type})")
                return result
            else:
                logger.error(f"계좌평가잔고 조회 실패: {result.get('return_msg')}")
                return None

        except Exception as e:
            logger.error(f"계좌평가잔고 조회 오류: {e}")
            return None

    def get_profit_rate(self, market_type: str = "0") -> Optional[Dict[str, Any]]:
        """
        계좌 수익률 조회

        Args:
            market_type: 시장구분 (0: 전체, 1: KOSPI, 2: KOSDAQ)

        Returns:
            계좌 수익률 정보
        """
        try:
            variant_map = {"0": 1, "1": 2, "2": 3}
            variant_idx = variant_map.get(market_type, 1)

            result = self.client.call_verified_api(
                api_id='ka10085',
                variant_idx=variant_idx
            )

            if result.get('return_code') == 0:
                logger.info(f"계좌수익률 조회 성공 (market={market_type})")
                return result
            else:
                logger.error(f"계좌수익률 조회 실패: {result.get('return_msg')}")
                return None

        except Exception as e:
            logger.error(f"계좌수익률 조회 오류: {e}")
            return None

    def get_deposit(self, query_type: str = "3") -> Optional[Dict[str, Any]]:
        """
        예수금 상세현황 조회

        Args:
            query_type: 조회구분 (2: 일반조회, 3: 추정조회)

        Returns:
            예수금 정보
        """
        try:
            variant_idx = 1 if query_type == "3" else 2

            result = self.client.call_verified_api(
                api_id='kt00001',
                variant_idx=variant_idx
            )

            if result.get('return_code') == 0:
                logger.info(f"예수금 조회 성공 (query={query_type})")
                return result
            else:
                logger.error(f"예수금 조회 실패: {result.get('return_msg')}")
                return None

        except Exception as e:
            logger.error(f"예수금 조회 오류: {e}")
            return None

    def get_account_evaluation(self, market_type: str = "KRX") -> Optional[Dict[str, Any]]:
        """
        계좌평가현황 조회

        Args:
            market_type: 시장구분 (KRX, NXT, KRX+NXT)

        Returns:
            계좌평가현황 정보
        """
        try:
            variant_map = {"KRX": 1, "NXT": 2, "KRX+NXT": 3}
            variant_idx = variant_map.get(market_type, 1)

            result = self.client.call_verified_api(
                api_id='kt00004',
                variant_idx=variant_idx
            )

            if result.get('return_code') == 0:
                logger.info(f"계좌평가현황 조회 성공 (market={market_type})")
                return result
            else:
                logger.error(f"계좌평가현황 조회 실패: {result.get('return_msg')}")
                return None

        except Exception as e:
            logger.error(f"계좌평가현황 조회 오류: {e}")
            return None

    def get_orderable_amount(
        self,
        stock_code: str,
        order_type: str = "02",
        price: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        주문가능금액 조회

        Args:
            stock_code: 종목코드
            order_type: 주문유형 (01: 시장가, 02: 지정가)
            price: 주문가격

        Returns:
            주문가능금액 정보
        """
        try:
            result = self.client.call_verified_api(
                api_id='kt00010',
                variant_idx=1,
                body_override={
                    'stk_cd': stock_code,
                    'ord_tp': order_type,
                    'ord_price': str(price)
                }
            )

            if result.get('return_code') == 0:
                logger.info(f"주문가능금액 조회 성공 ({stock_code})")
                return result
            else:
                logger.error(f"주문가능금액 조회 실패: {result.get('return_msg')}")
                return None

        except Exception as e:
            logger.error(f"주문가능금액 조회 오류: {e}")
            return None

    def get_daily_profit_loss(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        일자별 실현손익 조회

        Args:
            start_date: 시작일자 (YYYYMMDD)
            end_date: 종료일자 (YYYYMMDD)

        Returns:
            일자별 실현손익 정보
        """
        try:
            # 기본값: 오늘
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')

            # 기본값: 1주일 전
            if not start_date:
                start_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')

            # 기간에 따라 variant 선택
            days_diff = (datetime.strptime(end_date, '%Y%m%d') -
                        datetime.strptime(start_date, '%Y%m%d')).days

            if days_diff == 0:
                variant_idx = 1  # 당일
            elif days_diff <= 7:
                variant_idx = 2  # 1주일
            else:
                variant_idx = 3  # 1개월

            result = self.client.call_verified_api(
                api_id='ka10074',
                variant_idx=variant_idx,
                body_override={
                    'strt_dt': start_date,
                    'end_dt': end_date
                }
            )

            if result.get('return_code') == 0:
                logger.info(f"일자별 실현손익 조회 성공 ({start_date}~{end_date})")
                return result
            else:
                logger.error(f"일자별 실현손익 조회 실패: {result.get('return_msg')}")
                return None

        except Exception as e:
            logger.error(f"일자별 실현손익 조회 오류: {e}")
            return None

    def get_stock_profit_loss(
        self,
        stock_code: str = None,
        start_date: str = None,
        end_date: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        일자별 종목별 실현손익 조회

        Args:
            stock_code: 종목코드 (선택)
            start_date: 시작일자 (YYYYMMDD)
            end_date: 종료일자 (YYYYMMDD)

        Returns:
            종목별 실현손익 정보
        """
        try:
            # 기본값 설정
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')

            override = {
                'strt_dt': start_date,
                'end_dt': end_date
            }

            if stock_code:
                override['stk_cd'] = stock_code

            result = self.client.call_verified_api(
                api_id='ka10073',
                variant_idx=1,
                body_override=override
            )

            if result.get('return_code') == 0:
                logger.info(f"종목별 실현손익 조회 성공")
                return result
            else:
                logger.error(f"종목별 실현손익 조회 실패: {result.get('return_msg')}")
                return None

        except Exception as e:
            logger.error(f"종목별 실현손익 조회 오류: {e}")
            return None

    def get_today_profit_loss_detail(self, stock_code: str = None) -> Optional[Dict[str, Any]]:
        """
        당일 실현손익 상세 조회

        Args:
            stock_code: 종목코드 (선택)

        Returns:
            당일 실현손익 상세 정보
        """
        try:
            override = {}
            if stock_code:
                override['stk_cd'] = stock_code

            result = self.client.call_verified_api(
                api_id='ka10077',
                variant_idx=1,
                body_override=override if override else None
            )

            if result.get('return_code') == 0:
                logger.info("당일 실현손익 상세 조회 성공")
                return result
            else:
                logger.error(f"당일 실현손익 상세 조회 실패: {result.get('return_msg')}")
                return None

        except Exception as e:
            logger.error(f"당일 실현손익 상세 조회 오류: {e}")
            return None

    def get_outstanding_orders(
        self,
        stock_code: str = None,
        order_type: str = "0"
    ) -> Optional[Dict[str, Any]]:
        """
        미체결 주문 조회

        Args:
            stock_code: 종목코드 (선택)
            order_type: 거래구분 (0: 전체, 1: 매도, 2: 매수)

        Returns:
            미체결 주문 정보
        """
        try:
            override = {'trde_tp': order_type}
            if stock_code:
                override['stk_cd'] = stock_code
                override['all_stk_tp'] = '1'
            else:
                override['all_stk_tp'] = '0'

            result = self.client.call_verified_api(
                api_id='ka10075',
                variant_idx=1 if not stock_code else 2,
                body_override=override
            )

            if result.get('return_code') == 0:
                logger.info("미체결 주문 조회 성공")
                return result
            else:
                logger.error(f"미체결 주문 조회 실패: {result.get('return_msg')}")
                return None

        except Exception as e:
            logger.error(f"미체결 주문 조회 오류: {e}")
            return None

    def get_executed_orders(
        self,
        stock_code: str = None,
        query_type: str = "0"
    ) -> Optional[Dict[str, Any]]:
        """
        체결 주문 조회

        Args:
            stock_code: 종목코드 (선택)
            query_type: 조회구분 (0: 전체, 1: 종목별)

        Returns:
            체결 주문 정보
        """
        try:
            override = {'qry_tp': query_type}
            if stock_code:
                override['stk_cd'] = stock_code

            result = self.client.call_verified_api(
                api_id='ka10076',
                variant_idx=1 if not stock_code else 2,
                body_override=override
            )

            if result.get('return_code') == 0:
                logger.info("체결 주문 조회 성공")
                return result
            else:
                logger.error(f"체결 주문 조회 실패: {result.get('return_msg')}")
                return None

        except Exception as e:
            logger.error(f"체결 주문 조회 오류: {e}")
            return None

    def get_holdings(self, market_type: str = "KRX") -> List[Dict[str, Any]]:
        """
        보유 종목 정보 조회 (main.py 호환)

        kt00004 (계좌평가현황요청) 사용 - avg_prc (평균단가) 필드 포함

        Args:
            market_type: 시장구분 (KRX, NXT)

        Returns:
            보유 종목 리스트 (stk_cd, stk_nm, rmnd_qty, avg_prc, cur_prc 등)
        """
        try:
            # kt00004 사용 (계좌평가현황요청)
            result = self.get_account_evaluation(market_type=market_type)

            if result and result.get('return_code') == 0:
                # 응답에서 보유 종목 리스트 추출
                # kt00004 응답 구조: stk_acnt_evlt_prst 리스트
                holdings_key = 'stk_acnt_evlt_prst'  # 종목별계좌평가현황
                holdings = result.get(holdings_key, [])

                if holdings:
                    logger.info(f"보유 종목 조회 성공 (kt00004): {len(holdings)}개")
                    return holdings
                else:
                    logger.info("보유 종목 없음")
                    return []
            else:
                logger.warning("보유 종목 조회 실패, 빈 리스트 반환")
                return []

        except Exception as e:
            logger.error(f"보유 종목 조회 오류: {e}")
            return []


__all__ = ['AccountAPI']
