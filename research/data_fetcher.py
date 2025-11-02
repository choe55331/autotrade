"""
research/data_fetcher.py
데이터 수집 모듈
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.trading_date import get_last_trading_date

logger = logging.getLogger(__name__)


class DataFetcher:
    """
    키움증권 REST API 데이터 수집 클래스
    
    주요 기능:
    - 계좌 정보 조회
    - 시세 데이터 조회
    - 종목 검색
    - 순위 정보 조회
    """
    
    def __init__(self, client):
        """
        DataFetcher 초기화
        
        Args:
            client: KiwoomRESTClient 인스턴스
        """
        self.client = client
        logger.info("DataFetcher 초기화 완료")
    
    # ==================== 계좌 정보 조회 ====================
    
    def get_balance(self, account_number: str = None) -> Optional[Dict[str, Any]]:
        """
        계좌 잔고 조회 (kt00018)

        Args:
            account_number: 계좌번호 (None이면 기본 계좌)

        Returns:
            잔고 정보 딕셔너리
            {
                'acnt_evlt_remn_indv_tot': [  # 보유 종목 리스트
                    {
                        'stk_cd': '005930',
                        'stk_nm': '삼성전자',
                        'rmnd_qty': '10',
                        'pur_pric': '70000',
                        'cur_prc': '72000',
                        'evltv_prft': '20000',
                        'prft_rt': '2.86',
                        'evlt_amt': '720000'
                    }
                ],
                'tot_evlt_amt': '720000',      # 총 평가금액
                'tot_evlt_pl': '20000',        # 총 평가손익
                'tot_prft_rt': '2.86',         # 총 수익률
                'prsm_dpst_aset_amt': '1000000'  # 추정예탁자산
            }
        """
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
            logger.info("잔고 조회 성공")
            return response  # Response is data directly, no 'output' wrapper
        else:
            logger.error(f"잔고 조회 실패: {response.get('return_msg')}")
            return None
    
    def get_deposit(self, account_number: str = None) -> Optional[Dict[str, Any]]:
        """
        예수금 조회 (kt00001)

        Args:
            account_number: 계좌번호 (무시됨, 토큰에서 자동 추출)

        Returns:
            예수금 정보
            {
                'ord_alow_amt': '1000000',   # 주문 가능 금액
                'pymn_alow_amt': '1000000'   # 출금 가능 금액
            }
        """
        body = {"qry_tp": "2"}  # 일반조회

        response = self.client.request(
            api_id="kt00001",
            body=body,
            path="/api/dostk/acnt"
        )

        if response and response.get('return_code') == 0:
            ord_alow_amt = int(response.get('ord_alow_amt', 0))
            logger.info(f"예수금 조회 성공: 주문가능금액 {ord_alow_amt:,}원")
            return response  # Response is data directly, no 'output' wrapper
        else:
            logger.error(f"예수금 조회 실패: {response.get('return_msg')}")
            return None
    
    def get_holdings(self, account_number: str = None) -> List[Dict[str, Any]]:
        """
        보유 종목 리스트 조회

        Args:
            account_number: 계좌번호

        Returns:
            보유 종목 리스트
        """
        balance = self.get_balance(account_number)

        if not balance:
            return []

        holdings = []
        output_list = balance.get('acnt_evlt_remn_indv_tot', [])

        for item in output_list:
            holding = {
                'stock_code': item.get('stk_cd', ''),
                'stock_name': item.get('stk_nm', ''),
                'quantity': int(item.get('rmnd_qty', 0)),
                'purchase_price': float(item.get('pur_pric', 0)),
                'current_price': float(item.get('cur_prc', 0)),
                'profit_loss': float(item.get('evltv_prft', 0)),
                'profit_loss_rate': float(item.get('prft_rt', 0)),
                'evaluation_amount': float(item.get('evlt_amt', 0)),
            }
            holdings.append(holding)

        logger.info(f"보유 종목 {len(holdings)}개 조회 완료")
        return holdings
    
    # ==================== 시세 조회 ====================
    
    def get_current_price(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        종목 현재가 조회
        
        Args:
            stock_code: 종목코드 (6자리)
        
        Returns:
            현재가 정보
            {
                'stock_code': '005930',
                'stock_name': '삼성전자',
                'current_price': 72000,
                'change_price': 1000,
                'change_rate': 1.41,
                'volume': 10000000,
                'trading_value': 720000000000,
                'open_price': 71000,
                'high_price': 72500,
                'low_price': 70500,
                'prev_close': 71000
            }
        """
        body = {
            "stock_code": stock_code
        }
        
        response = self.client.request(
            api_id="DOSK_0002",
            body=body,
            path="/api/dostk/inquire/price"
        )
        
        if response and response.get('return_code') == 0:
            price_info = response.get('output', {})
            current_price = int(price_info.get('current_price', 0))
            logger.info(f"{stock_code} 현재가: {current_price:,}원")
            return price_info
        else:
            logger.error(f"현재가 조회 실패: {response.get('return_msg')}")
            return None
    
    def get_orderbook(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        호가 조회
        
        Args:
            stock_code: 종목코드
        
        Returns:
            호가 정보 (매도/매수 10호가)
            {
                'sell_hoga': [  # 매도 호가 (10개)
                    {'price': 72500, 'quantity': 1000},
                    {'price': 72400, 'quantity': 2000},
                    ...
                ],
                'buy_hoga': [  # 매수 호가 (10개)
                    {'price': 72300, 'quantity': 1500},
                    {'price': 72200, 'quantity': 2500},
                    ...
                ]
            }
        """
        body = {
            "stock_code": stock_code
        }
        
        response = self.client.request(
            api_id="DOSK_0003",
            body=body,
            path="/api/dostk/inquire/orderbook"
        )
        
        if response and response.get('return_code') == 0:
            orderbook = response.get('output', {})
            logger.info(f"{stock_code} 호가 조회 완료")
            return orderbook
        else:
            logger.error(f"호가 조회 실패: {response.get('return_msg')}")
            return None
    
    def get_daily_price(
        self,
        stock_code: str,
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict[str, Any]]:
        """
        일봉 데이터 조회 (검증된 API 사용: ka10081)

        Args:
            stock_code: 종목코드
            start_date: 시작일 (YYYYMMDD) - 사용되지 않음 (base_dt만 사용)
            end_date: 종료일 (YYYYMMDD) - base_dt로 사용

        Returns:
            일봉 데이터 리스트
            [
                {
                    'stck_bsop_date': '20251101',
                    'stck_oprc': 71000,
                    'stck_hgpr': 72500,
                    'stck_lwpr': 70500,
                    'stck_clpr': 72000,
                    'acml_vol': 10000000
                },
                ...
            ]
        """
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')

        # Use verified API: ka10081 (주식일봉차트조회요청)
        response = self.client.call_verified_api(
            api_id="ka10081",
            variant_idx=1,
            body_override={
                "stk_cd": stock_code,
                "base_dt": end_date,  # 조회 기준일
                "upd_stkpc_tp": "1"    # 수정주가 반영
            }
        )

        if response and response.get('return_code') == 0:
            daily_data = response.get('output', [])
            logger.info(f"{stock_code} 일봉 데이터 {len(daily_data)}개 조회 완료")

            # Convert to standard format
            standardized_data = []
            for item in daily_data:
                standardized_data.append({
                    'date': item.get('stck_bsop_date', ''),
                    'open': int(item.get('stck_oprc', 0)),
                    'high': int(item.get('stck_hgpr', 0)),
                    'low': int(item.get('stck_lwpr', 0)),
                    'close': int(item.get('stck_clpr', 0)),
                    'volume': int(item.get('acml_vol', 0))
                })

            return standardized_data
        else:
            logger.error(f"일봉 조회 실패: {response.get('return_msg')}")
            return []
    
    def get_minute_price(
        self,
        stock_code: str,
        minute_type: str = '1'
    ) -> List[Dict[str, Any]]:
        """
        분봉 데이터 조회
        
        Args:
            stock_code: 종목코드
            minute_type: 분봉 타입 ('1', '3', '5', '10', '30', '60')
        
        Returns:
            분봉 데이터 리스트
        """
        body = {
            "stock_code": stock_code,
            "period_code": minute_type
        }
        
        response = self.client.request(
            api_id="DOSK_0001",
            body=body,
            path="/api/dostk/inquire/minuteprice"
        )
        
        if response and response.get('return_code') == 0:
            minute_data = response.get('output', [])
            logger.info(f"{stock_code} {minute_type}분봉 데이터 {len(minute_data)}개 조회 완료")
            return minute_data
        else:
            logger.error(f"분봉 조회 실패: {response.get('return_msg')}")
            return []
    
    # ==================== 종목 검색/순위 ====================
    
    def search_stock(self, keyword: str) -> List[Dict[str, Any]]:
        """
        종목 검색
        
        Args:
            keyword: 검색어 (종목명 또는 종목코드)
        
        Returns:
            검색 결과 리스트
            [
                {
                    'stock_code': '005930',
                    'stock_name': '삼성전자',
                    'market': 'KOSPI'
                },
                ...
            ]
        """
        body = {
            "keyword": keyword
        }
        
        response = self.client.request(
            api_id="DOSK_0006",
            body=body,
            path="/api/dostk/inquire/search"
        )
        
        if response and response.get('return_code') == 0:
            results = response.get('output', [])
            logger.info(f"'{keyword}' 검색 결과 {len(results)}개")
            return results
        else:
            logger.error(f"종목 검색 실패: {response.get('return_msg')}")
            return []
    
    def get_volume_rank(
        self,
        market: str = 'ALL',
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        거래량 순위 조회

        Args:
            market: 시장구분 ('ALL', 'KOSPI', 'KOSDAQ')
            limit: 조회 건수

        Returns:
            거래량 순위 리스트
        """
        try:
            from api.market import MarketAPI
            market_api = MarketAPI(self.client)
            rank_list = market_api.get_volume_rank(market, limit)
            logger.info(f"거래량 순위 {len(rank_list)}개 조회 완료")
            return rank_list
        except Exception as e:
            logger.error(f"거래량 순위 조회 실패: {e}")
            return []
    
    def get_price_change_rank(
        self,
        market: str = 'ALL',
        sort: str = 'rise',
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        등락률 순위 조회

        Args:
            market: 시장구분 ('ALL', 'KOSPI', 'KOSDAQ')
            sort: 정렬 ('rise': 상승률, 'fall': 하락률)
            limit: 조회 건수

        Returns:
            등락률 순위 리스트
        """
        try:
            from api.market import MarketAPI
            market_api = MarketAPI(self.client)
            rank_list = market_api.get_price_change_rank(market, sort, limit)
            logger.info(f"등락률 순위 {len(rank_list)}개 조회 완료")
            return rank_list
        except Exception as e:
            logger.error(f"등락률 순위 조회 실패: {e}")
            return []
    
    def get_trading_value_rank(
        self,
        market: str = 'ALL',
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        거래대금 순위 조회

        Args:
            market: 시장구분
            limit: 조회 건수

        Returns:
            거래대금 순위 리스트
        """
        try:
            from api.market import MarketAPI
            market_api = MarketAPI(self.client)
            # 거래대금은 거래량 API에서 sort 타입을 변경하여 조회
            body = {
                "market": market,
                "limit": limit,
                "sort": "trading_value"
            }
            response = market_api.client.request(
                api_id="DOSK_0010",
                body=body,
                path="/api/dostk/inquire/rank"
            )

            if response and response.get('return_code') == 0:
                rank_list = response.get('output', [])
                logger.info(f"거래대금 순위 {len(rank_list)}개 조회 완료")
                return rank_list
            else:
                logger.error(f"거래대금 순위 조회 실패: {response.get('return_msg')}")
                return []
        except Exception as e:
            logger.error(f"거래대금 순위 조회 실패: {e}")
            return []
    
    # ==================== 투자자별 매매 동향 ====================
    
    def get_investor_trading(
        self,
        stock_code: str,
        date: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        투자자별 매매 동향 조회 (외국인, 기관)

        Args:
            stock_code: 종목코드
            date: 조회일 (YYYYMMDD, None이면 최근 거래일 자동 계산)

        Returns:
            투자자별 매매 동향
            {
                'foreign_net': 10000,      # 외국인 순매수
                'institution_net': 5000,   # 기관 순매수
                'individual_net': -15000,  # 개인 순매수
                'foreign_hold_rate': 52.5  # 외국인 보유 비율
            }
        """
        # 날짜 자동 계산
        if not date:
            date = get_last_trading_date()

        body = {
            "stock_code": stock_code,
            "date": date
        }

        response = self.client.request(
            api_id="DOSK_0040",
            body=body,
            path="/api/dostk/inquire/investor"
        )

        if response and response.get('return_code') == 0:
            investor_info = response.get('output', {})
            logger.info(f"{stock_code} 투자자별 매매 동향 조회 완료 (날짜: {date})")
            return investor_info
        else:
            logger.error(f"투자자별 매매 동향 조회 실패: {response.get('return_msg')}")
            return None
    
    # ==================== 종목 상세 정보 ====================
    
    def get_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        종목 상세 정보 조회
        
        Args:
            stock_code: 종목코드
        
        Returns:
            종목 상세 정보
            {
                'stock_code': '005930',
                'stock_name': '삼성전자',
                'market_cap': 500000000000000,  # 시가총액
                'per': 15.5,                     # PER
                'pbr': 1.2,                      # PBR
                'eps': 5000,                     # EPS
                'bps': 60000,                    # BPS
                'dividend_yield': 2.5,           # 배당수익률
                'listed_shares': 5000000000      # 상장주식수
            }
        """
        body = {
            "stock_code": stock_code
        }
        
        response = self.client.request(
            api_id="DOSK_0005",
            body=body,
            path="/api/dostk/inquire/stockinfo"
        )
        
        if response and response.get('return_code') == 0:
            stock_info = response.get('output', {})
            logger.info(f"{stock_code} 상세 정보 조회 완료")
            return stock_info
        else:
            logger.error(f"종목 정보 조회 실패: {response.get('return_msg')}")
            return None
    
    # ==================== 유틸리티 ====================
    
    def _get_market_code(self, market: str) -> str:
        """
        시장 코드 변환
        
        Args:
            market: 시장 문자열 ('ALL', 'KOSPI', 'KOSDAQ')
        
        Returns:
            시장 코드
        """
        market_map = {
            'ALL': '0',
            'KOSPI': '0',
            'KOSDAQ': '1'
        }
        return market_map.get(market.upper(), '0')


__all__ = ['DataFetcher']