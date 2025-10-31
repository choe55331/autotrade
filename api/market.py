"""
api/market.py
시세 및 시장 정보 API (market_condition, rank_info, sector, theme 등 통합)
"""
import logging
import random
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
        self.test_mode = getattr(client, 'test_mode', False)
        mode_str = "(테스트 모드 - Mock 데이터)" if self.test_mode else "(실전 모드)"
        logger.info(f"MarketAPI 초기화 완료 {mode_str}")
    
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
    
    def _generate_mock_stock_data(self, count: int = 20, rank_type: str = "volume") -> List[Dict[str, Any]]:
        """테스트용 Mock 종목 데이터 생성"""
        mock_stocks = [
            ("005930", "삼성전자"), ("000660", "SK하이닉스"), ("035420", "NAVER"),
            ("051910", "LG화학"), ("006400", "삼성SDI"), ("035720", "카카오"),
            ("207940", "삼성바이오로직스"), ("068270", "셀트리온"), ("005380", "현대차"),
            ("012330", "현대모비스"), ("105560", "KB금융"), ("055550", "신한지주"),
            ("000270", "기아"), ("017670", "SK텔레콤"), ("032830", "삼성생명"),
            ("028260", "삼성물산"), ("096770", "SK이노베이션"), ("018260", "삼성에스디에스"),
            ("051900", "LG생활건강"), ("009150", "삼성전기"), ("003550", "LG"),
            ("034730", "SK"), ("011170", "롯데케미칼"), ("010130", "고려아연"),
            ("086790", "하나금융지주"), ("316140", "우리금융지주"), ("003670", "포스코퓨처엠"),
            ("034220", "LG디스플레이"), ("015760", "한국전력"), ("010140", "삼성중공업")
        ]

        result = []
        for i, (code, name) in enumerate(mock_stocks[:count]):
            base_price = random.randint(20000, 100000)
            change_rate = random.uniform(-5.0, 8.0)

            if rank_type == "volume":
                volume = random.randint(5000000, 50000000)
                trading_value = base_price * volume
            elif rank_type == "price_change":
                volume = random.randint(1000000, 20000000)
                trading_value = base_price * volume
                # 상승률 순위면 양수 비중 높이기
                change_rate = random.uniform(3.0, 15.0)
            else:  # trading_value
                volume = random.randint(3000000, 30000000)
                trading_value = random.randint(10000000000, 100000000000)

            result.append({
                "code": code,
                "name": name,
                "price": base_price,
                "price_change": round(change_rate, 2),
                "volume": volume,
                "trading_value": trading_value,
                "rank": i + 1
            })

        return result

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
        # 테스트 모드: Mock 데이터 반환
        if self.test_mode:
            logger.info(f"🧪 테스트 모드: Mock 거래량 순위 데이터 생성 (limit={limit})")
            return self._generate_mock_stock_data(limit, "volume")

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
        # 테스트 모드: Mock 데이터 반환
        if self.test_mode:
            sort_name = "상승률" if sort == 'rise' else "하락률"
            logger.info(f"🧪 테스트 모드: Mock {sort_name} 순위 데이터 생성 (limit={limit})")
            return self._generate_mock_stock_data(limit, "price_change")

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

    def get_trading_value_rank(
        self,
        market: str = 'ALL',
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        거래대금 순위 조회

        Args:
            market: 시장구분 ('ALL', 'KOSPI', 'KOSDAQ')
            limit: 조회 건수

        Returns:
            거래대금 순위 리스트
        """
        # 테스트 모드: Mock 데이터 반환
        if self.test_mode:
            logger.info(f"🧪 테스트 모드: Mock 거래대금 순위 데이터 생성 (limit={limit})")
            return self._generate_mock_stock_data(limit, "trading_value")

        body = {
            "market": market,
            "limit": limit,
            "sort": "trading_value"
        }

        response = self.client.request(
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