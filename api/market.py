"""
api/market.py
시세 및 시장 정보 API (market_condition, rank_info, sector, theme 등 통합)
"""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class MarketAPI:
    """
    시세 및 시장 정보 API
    
    통합된 기능:
    - 시세 조회
    - 호가 조회
    - 시장 상황
    - 순위 정보
    - 업종 정보
    - 테마 정보
    """
    
    def __init__(self, client):
        """
        MarketAPI 초기화
        
        Args:
            client: KiwoomRESTClient 인스턴스
        """
        self.client = client
        logger.info("MarketAPI 초기화 완료")
    
    def get_stock_price(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        종목 현재가 조회
        
        Args:
            stock_code: 종목코드
        
        Returns:
            현재가 정보
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
            logger.info(f"{stock_code} 현재가: {price_info.get('current_price', 0):,}원")
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
            호가 정보
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
    
    def get_market_index(self, market_code: str = '001') -> Optional[Dict[str, Any]]:
        """
        시장 지수 조회
        
        Args:
            market_code: 시장코드 ('001': 코스피, '101': 코스닥)
        
        Returns:
            지수 정보
        """
        body = {
            "market_code": market_code
        }
        
        response = self.client.request(
            api_id="DOSK_0004",
            body=body,
            path="/api/dostk/inquire/index"
        )
        
        if response and response.get('return_code') == 0:
            index_info = response.get('output', {})
            market_name = "코스피" if market_code == '001' else "코스닥"
            logger.info(f"{market_name} 지수: {index_info.get('index', 0):.2f}")
            return index_info
        else:
            logger.error(f"지수 조회 실패: {response.get('return_msg')}")
            return None
    
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
        body = {
            "market": market,
            "limit": limit,
            "sort": "volume"
        }
        
        response = self.client.request(
            api_id="DOSK_0010",
            body=body,
            path="/api/dostk/inquire/rank"
        )
        
        if response and response.get('return_code') == 0:
            rank_list = response.get('output', [])
            logger.info(f"거래량 순위 {len(rank_list)}개 조회 완료")
            return rank_list
        else:
            logger.error(f"거래량 순위 조회 실패: {response.get('return_msg')}")
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
        body = {
            "market": market,
            "limit": limit,
            "sort": sort
        }
        
        response = self.client.request(
            api_id="DOSK_0011",
            body=body,
            path="/api/dostk/inquire/rank"
        )
        
        if response and response.get('return_code') == 0:
            rank_list = response.get('output', [])
            sort_name = "상승률" if sort == 'rise' else "하락률"
            logger.info(f"{sort_name} 순위 {len(rank_list)}개 조회 완료")
            return rank_list
        else:
            logger.error(f"등락률 순위 조회 실패: {response.get('return_msg')}")
            return []
    
    def get_sector_list(self) -> List[Dict[str, Any]]:
        """
        업종 목록 조회
        
        Returns:
            업종 목록
        """
        response = self.client.request(
            api_id="DOSK_0020",
            body={},
            path="/api/dostk/inquire/sector/list"
        )
        
        if response and response.get('return_code') == 0:
            sectors = response.get('output', [])
            logger.info(f"업종 {len(sectors)}개 조회 완료")
            return sectors
        else:
            logger.error(f"업종 목록 조회 실패: {response.get('return_msg')}")
            return []
    
    def get_sector_info(self, sector_code: str) -> Optional[Dict[str, Any]]:
        """
        업종 정보 조회
        
        Args:
            sector_code: 업종코드
        
        Returns:
            업종 정보
        """
        body = {
            "sector_code": sector_code
        }
        
        response = self.client.request(
            api_id="DOSK_0021",
            body=body,
            path="/api/dostk/inquire/sector/info"
        )
        
        if response and response.get('return_code') == 0:
            sector_info = response.get('output', {})
            logger.info(f"업종 정보 조회 완료: {sector_info.get('sector_name', '')}")
            return sector_info
        else:
            logger.error(f"업종 정보 조회 실패: {response.get('return_msg')}")
            return None
    
    def get_theme_list(self) -> List[Dict[str, Any]]:
        """
        테마 목록 조회
        
        Returns:
            테마 목록
        """
        response = self.client.request(
            api_id="DOSK_0030",
            body={},
            path="/api/dostk/inquire/theme/list"
        )
        
        if response and response.get('return_code') == 0:
            themes = response.get('output', [])
            logger.info(f"테마 {len(themes)}개 조회 완료")
            return themes
        else:
            logger.error(f"테마 목록 조회 실패: {response.get('return_msg')}")
            return []
    
    def get_theme_stocks(self, theme_code: str) -> List[Dict[str, Any]]:
        """
        테마 종목 조회
        
        Args:
            theme_code: 테마코드
        
        Returns:
            테마 종목 리스트
        """
        body = {
            "theme_code": theme_code
        }
        
        response = self.client.request(
            api_id="DOSK_0031",
            body=body,
            path="/api/dostk/inquire/theme/stocks"
        )
        
        if response and response.get('return_code') == 0:
            stocks = response.get('output', [])
            logger.info(f"테마 종목 {len(stocks)}개 조회 완료")
            return stocks
        else:
            logger.error(f"테마 종목 조회 실패: {response.get('return_msg')}")
            return []
    
    def get_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        종목 상세 정보 조회
        
        Args:
            stock_code: 종목코드
        
        Returns:
            종목 상세 정보
        """
        body = {
            "stock_code": stock_code
        }
        
        response = self.client.request(
            api_id="DOSK_0005",
            body=body,
            path="/api/dostk/inquire/stock/info"
        )
        
        if response and response.get('return_code') == 0:
            stock_info = response.get('output', {})
            logger.info(f"{stock_code} 상세 정보 조회 완료")
            return stock_info
        else:
            logger.error(f"종목 정보 조회 실패: {response.get('return_msg')}")
            return None
    
    def search_stock(self, keyword: str) -> List[Dict[str, Any]]:
        """
        종목 검색
        
        Args:
            keyword: 검색어
        
        Returns:
            검색 결과 리스트
        """
        body = {
            "keyword": keyword
        }
        
        response = self.client.request(
            api_id="DOSK_0006",
            body=body,
            path="/api/dostk/inquire/stock/search"
        )
        
        if response and response.get('return_code') == 0:
            results = response.get('output', [])
            logger.info(f"'{keyword}' 검색 결과 {len(results)}개")
            return results
        else:
            logger.error(f"종목 검색 실패: {response.get('return_msg')}")
            return []
    
    def get_investor_trading(
        self,
        stock_code: str,
        date: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        투자자별 매매 동향 조회
        
        Args:
            stock_code: 종목코드
            date: 조회일 (YYYYMMDD, None이면 오늘)
        
        Returns:
            투자자별 매매 동향
        """
        from datetime import datetime
        
        if not date:
            date = datetime.now().strftime('%Y%m%d')
        
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
            logger.info(f"{stock_code} 투자자별 매매 동향 조회 완료")
            return investor_info
        else:
            logger.error(f"투자자별 매매 동향 조회 실패: {response.get('return_msg')}")
            return None


__all__ = ['MarketAPI']