"""
api/market.py
시세 및 시장 정보 API (market_condition, rank_info, sector, theme 등 통합)
"""
import logging
from typing import Dict, Any, Optional, List
from utils.trading_date import get_last_trading_date

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

    ⚠️ 중요: API 응답 파싱 패턴
    ----------------------------------
    키움증권 REST API는 응답 구조가 API마다 다릅니다!

    1. 일반적인 패턴: response['output']
       예: DOSK_XXXX 시리즈

    2. 랭킹 API 패턴: 특정 키 사용
       - ka10031 (거래량순위): response['pred_trde_qty_upper']
       - ka10027 (등락률순위): response['pred_pre_flu_rt_upper']

    3. 데이터 정규화 필요
       API 응답 키 → 표준 키 변환:
       - stk_cd → code (종목코드, _AL 접미사 제거)
       - stk_nm → name (종목명)
       - cur_prc → price (현재가)
       - trde_qty / now_trde_qty → volume (거래량)
       - flu_rt → change_rate (등락률)

    새 API 추가 시:
    1. successful_apis.json에서 실제 응답 구조 확인
    2. 디버그 출력으로 실제 응답 키 확인
    3. 올바른 키로 데이터 추출
    4. 필요시 데이터 정규화
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
            path="inquire/price"
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
            path="inquire/orderbook"
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
            path="inquire/index"
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
        limit: int = 20,
        date: str = None
    ) -> List[Dict[str, Any]]:
        """
        전일 거래량 순위 조회 (ka10031)

        Args:
            market: 시장구분 ('0': 전체, '1': KOSPI, '2': KOSDAQ)
            limit: 조회 건수 (최대 200)
            date: 조회일 (현재 미사용, 자동으로 전일 데이터 조회)

        Returns:
            거래량 순위 리스트
        """
        # 시장 코드 변환 (successful_apis.json 검증된 값)
        market_map = {'ALL': '000', 'KOSPI': '001', 'KOSDAQ': '101'}
        mrkt_tp = market_map.get(market.upper(), '001')

        # 순위 범위 설정 (1위부터 limit까지)
        body = {
            "mrkt_tp": mrkt_tp,        # 시장구분 (000:전체, 001:KOSPI, 101:KOSDAQ)
            "qry_tp": "1",              # 조회구분 (1:거래량, 2:거래대금) - 검증됨
            "stex_tp": "3",             # 증권거래소 (3:전체) - 검증됨
            "rank_strt": "1",           # 시작순위
            "rank_end": str(limit)      # 종료순위
        }

        response = self.client.request(
            api_id="ka10031",
            body=body,
            path="rkinfo"
        )

        if response and response.get('return_code') == 0:
            # ka10031 API는 'pred_trde_qty_upper' 키에 데이터 반환
            rank_list = response.get('pred_trde_qty_upper', [])

            # 데이터 정규화: API 응답 키 -> 표준 키
            normalized_list = []
            for item in rank_list:
                normalized_list.append({
                    'code': item.get('stk_cd', '').replace('_AL', ''),  # _AL 접미사 제거
                    'name': item.get('stk_nm', ''),
                    'price': int(item.get('cur_prc', '0').replace('+', '').replace('-', '')),
                    'volume': int(item.get('trde_qty', '0')),
                    'change': int(item.get('pred_pre', '0').replace('+', '').replace('-', '')),
                    'change_sign': item.get('pred_pre_sig', ''),
                })

            logger.info(f"거래량 순위 {len(normalized_list)}개 조회 완료")
            return normalized_list
        else:
            logger.error(f"거래량 순위 조회 실패: {response.get('return_msg')}")
            logger.error(f"응답 전체: {response}")
            return []
    
    def get_price_change_rank(
        self,
        market: str = 'ALL',
        sort: str = 'rise',
        limit: int = 20,
        date: str = None
    ) -> List[Dict[str, Any]]:
        """
        전일대비 등락률 상위 조회 (ka10027)

        Args:
            market: 시장구분 ('ALL', 'KOSPI', 'KOSDAQ')
            sort: 정렬 ('rise': 상승률, 'fall': 하락률)
            limit: 조회 건수 (최대 200, 실제로는 40개씩 반환)
            date: 조회일 (현재 미사용)

        Returns:
            등락률 순위 리스트
        """
        # 시장 코드 변환 (successful_apis.json 검증된 값)
        market_map = {'ALL': '000', 'KOSPI': '001', 'KOSDAQ': '101'}
        mrkt_tp = market_map.get(market.upper(), '001')

        # 정렬 타입 변환 (검증된 값: 1=상승률, 2=하락률로 추정)
        sort_map = {'rise': '1', 'fall': '2'}
        sort_tp = sort_map.get(sort.lower(), '1')

        body = {
            "mrkt_tp": mrkt_tp,          # 시장구분 (000:전체, 001:KOSPI, 101:KOSDAQ)
            "sort_tp": sort_tp,           # 정렬구분 (1:상승률, 2:하락률)
            "trde_qty_cnd": "0100",       # 거래량 조건 (검증된 값)
            "stk_cnd": "1",               # 종목 조건 (검증된 값)
            "crd_cnd": "0",               # 신용 조건 (0: 전체)
            "updown_incls": "1",          # 상한하한 포함 (0: 제외, 1: 포함)
            "pric_cnd": "0",              # 가격 조건 (0: 전체)
            "trde_prica_cnd": "0",        # 거래대금 조건 (0: 전체)
            "stex_tp": "3"                # 증권거래소 (3: 전체)
        }

        response = self.client.request(
            api_id="ka10027",
            body=body,
            path="rkinfo"
        )

        if response and response.get('return_code') == 0:
            # ka10027 API는 'pred_pre_flu_rt_upper' 키에 데이터 반환
            rank_list = response.get('pred_pre_flu_rt_upper', [])

            # 데이터 정규화: API 응답 키 -> 표준 키
            normalized_list = []
            for item in rank_list[:limit]:
                normalized_list.append({
                    'code': item.get('stk_cd', '').replace('_AL', ''),  # _AL 접미사 제거
                    'name': item.get('stk_nm', ''),
                    'price': int(item.get('cur_prc', '0').replace('+', '').replace('-', '')),
                    'change_rate': float(item.get('flu_rt', '0').replace('+', '').replace('-', '')),
                    'volume': int(item.get('now_trde_qty', '0')),
                    'change': int(item.get('pred_pre', '0').replace('+', '').replace('-', '')),
                    'change_sign': item.get('pred_pre_sig', ''),
                })

            sort_name = "상승률" if sort == 'rise' else "하락률"
            logger.info(f"{sort_name} 순위 {len(normalized_list)}개 조회 완료")
            return normalized_list
        else:
            logger.error(f"등락률 순위 조회 실패: {response.get('return_msg')}")
            logger.error(f"응답 전체: {response}")
            return []

    def get_trading_value_rank(
        self,
        market: str = 'ALL',
        limit: int = 20,
        include_managed: bool = False
    ) -> List[Dict[str, Any]]:
        """
        거래대금 상위 조회 (ka10032)

        Args:
            market: 시장구분 ('ALL', 'KOSPI', 'KOSDAQ')
            limit: 조회 건수 (최대 200)
            include_managed: 관리종목 포함 여부

        Returns:
            거래대금 순위 리스트
        """
        # 시장 코드 변환 (successful_apis.json 검증된 값)
        market_map = {'ALL': '000', 'KOSPI': '001', 'KOSDAQ': '101'}
        mrkt_tp = market_map.get(market.upper(), '001')

        body = {
            "mrkt_tp": mrkt_tp,               # 시장구분
            "mang_stk_incls": "1" if include_managed else "0",  # 관리종목 포함
            "stex_tp": "3"                    # 증권거래소 (3: 전체)
        }

        response = self.client.request(
            api_id="ka10032",
            body=body,
            path="rkinfo"
        )

        if response and response.get('return_code') == 0:
            # 응답 키 찾기 (자동 탐색)
            data_keys = [k for k in response.keys() if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]

            # 첫 번째 리스트 키 사용
            rank_list = []
            for key in data_keys:
                val = response.get(key)
                if isinstance(val, list) and len(val) > 0:
                    rank_list = val
                    break

            # 데이터 정규화
            normalized_list = []
            for item in rank_list[:limit]:
                normalized_list.append({
                    'code': item.get('stk_cd', '').replace('_AL', ''),
                    'name': item.get('stk_nm', ''),
                    'price': int(item.get('cur_prc', '0').replace('+', '').replace('-', '')),
                    'trading_value': int(item.get('trde_prica', '0')),  # 거래대금
                    'volume': int(item.get('trde_qty', '0')),
                    'change': int(item.get('pred_pre', '0').replace('+', '').replace('-', '')),
                    'change_sign': item.get('pred_pre_sig', ''),
                })

            logger.info(f"거래대금 순위 {len(normalized_list)}개 조회 완료")
            return normalized_list
        else:
            logger.error(f"거래대금 순위 조회 실패: {response.get('return_msg')}")
            return []

    def get_volume_surge_rank(
        self,
        market: str = 'ALL',
        limit: int = 20,
        time_interval: int = 5
    ) -> List[Dict[str, Any]]:
        """
        거래량 급증 종목 조회 (ka10023)

        Args:
            market: 시장구분 ('ALL', 'KOSPI', 'KOSDAQ')
            limit: 조회 건수
            time_interval: 시간 간격 (분)

        Returns:
            거래량 급증 순위 리스트
        """
        market_map = {'ALL': '000', 'KOSPI': '001', 'KOSDAQ': '101'}
        mrkt_tp = market_map.get(market.upper(), '000')

        body = {
            "mrkt_tp": mrkt_tp,
            "trde_qty_tp": "100",  # 거래량 조건
            "sort_tp": "2",        # 정렬 타입
            "tm_tp": "1",          # 시간 타입 (1:분, 2:시간)
            "tm": str(time_interval),  # 시간 간격
            "stk_cnd": "0",
            "pric_tp": "0",
            "stex_tp": "3"
        }

        response = self.client.request(
            api_id="ka10023",
            body=body,
            path="rkinfo"
        )

        if response and response.get('return_code') == 0:
            # 응답 키 찾기
            data_keys = [k for k in response.keys() if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]

            rank_list = []
            for key in data_keys:
                val = response.get(key)
                if isinstance(val, list) and len(val) > 0:
                    rank_list = val
                    break

            # 데이터 정규화
            normalized_list = []
            for item in rank_list[:limit]:
                normalized_list.append({
                    'code': item.get('stk_cd', '').replace('_AL', ''),
                    'name': item.get('stk_nm', ''),
                    'price': int(item.get('cur_prc', '0').replace('+', '').replace('-', '')),
                    'volume': int(item.get('trde_qty', '0')),
                    'volume_increase_rate': float(item.get('qty_incrs_rt', '0')),  # 거래량 증가율
                    'change_rate': float(item.get('flu_rt', '0').replace('+', '').replace('-', '')),
                })

            logger.info(f"거래량 급증 {len(normalized_list)}개 조회 완료")
            return normalized_list
        else:
            logger.error(f"거래량 급증 조회 실패: {response.get('return_msg')}")
            return []

    def get_intraday_change_rank(
        self,
        market: str = 'ALL',
        sort: str = 'rise',
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        시가대비 등락률 순위 조회 (ka10028)

        Args:
            market: 시장구분 ('ALL', 'KOSPI', 'KOSDAQ')
            sort: 정렬 ('rise': 상승률, 'fall': 하락률)
            limit: 조회 건수

        Returns:
            시가대비 등락률 순위 리스트
        """
        market_map = {'ALL': '000', 'KOSPI': '001', 'KOSDAQ': '101'}
        mrkt_tp = market_map.get(market.upper(), '000')

        # 정렬 타입 (1:상승률, 2:하락률)
        sort_map = {'rise': '1', 'fall': '2'}
        sort_tp = sort_map.get(sort.lower(), '1')

        body = {
            "sort_tp": sort_tp,
            "trde_qty_cnd": "0000",
            "mrkt_tp": mrkt_tp,
            "updown_incls": "1",
            "stk_cnd": "0",
            "crd_cnd": "0",
            "trde_prica_cnd": "0",
            "flu_cnd": "1",
            "stex_tp": "3"
        }

        response = self.client.request(
            api_id="ka10028",
            body=body,
            path="stkinfo"
        )

        if response and response.get('return_code') == 0:
            # 응답 키 찾기
            data_keys = [k for k in response.keys() if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]

            rank_list = []
            for key in data_keys:
                val = response.get(key)
                if isinstance(val, list) and len(val) > 0:
                    rank_list = val
                    break

            # 데이터 정규화
            normalized_list = []
            for item in rank_list[:limit]:
                normalized_list.append({
                    'code': item.get('stk_cd', '').replace('_AL', ''),
                    'name': item.get('stk_nm', ''),
                    'price': int(item.get('cur_prc', '0').replace('+', '').replace('-', '')),
                    'open_price': int(item.get('open_prc', '0')),  # 시가
                    'intraday_change_rate': float(item.get('flu_rt', '0').replace('+', '').replace('-', '')),
                    'volume': int(item.get('trde_qty', '0')),
                })

            sort_name = "상승률" if sort == 'rise' else "하락률"
            logger.info(f"시가대비 {sort_name} {len(normalized_list)}개 조회 완료")
            return normalized_list
        else:
            logger.error(f"시가대비 등락률 조회 실패: {response.get('return_msg')}")
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
            path="inquire/sector/list"
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
            path="inquire/sector/info"
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
            path="inquire/theme/list"
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
            path="inquire/theme/stocks"
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
            path="inquire/stock/info"
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
            path="inquire/stock/search"
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
            date: 조회일 (YYYYMMDD, None이면 최근 거래일 자동 계산)

        Returns:
            투자자별 매매 동향
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
            path="inquire/investor"
        )

        if response and response.get('return_code') == 0:
            investor_info = response.get('output', {})
            logger.info(f"{stock_code} 투자자별 매매 동향 조회 완료 (날짜: {date})")
            return investor_info
        else:
            logger.error(f"투자자별 매매 동향 조회 실패: {response.get('return_msg')}")
            return None

    def get_investor_data(
        self,
        stock_code: str,
        date: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        투자자 매매 데이터 조회 (get_investor_trading의 별칭)

        Args:
            stock_code: 종목코드
            date: 조회일 (YYYYMMDD, None이면 최근 거래일 자동 계산)

        Returns:
            투자자별 매매 동향
            {
                '기관_순매수': 10000,
                '외국인_순매수': 5000,
                ...
            }
        """
        return self.get_investor_trading(stock_code, date)

    def get_bid_ask(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        호가 데이터 조회 (get_orderbook의 별칭)

        Args:
            stock_code: 종목코드

        Returns:
            호가 정보
            {
                '매수_총잔량': 10000,
                '매도_총잔량': 8000,
                ...
            }
        """
        return self.get_orderbook(stock_code)

    def get_daily_chart(
        self,
        stock_code: str,
        period: int = 20,
        date: str = None
    ) -> List[Dict[str, Any]]:
        """
        일봉 차트 데이터 조회

        Args:
            stock_code: 종목코드
            period: 조회 기간 (일수)
            date: 기준일 (YYYYMMDD, None이면 최근 거래일)

        Returns:
            일봉 데이터 리스트
            [
                {
                    'date': '20231201',
                    'open': 70000,
                    'high': 71000,
                    'low': 69500,
                    'close': 70500,
                    'volume': 1000000
                },
                ...
            ]
        """
        # 날짜 자동 계산
        if not date:
            date = get_last_trading_date()

        body = {
            "stock_code": stock_code,
            "period": str(period),
            "date": date
        }

        response = self.client.request(
            api_id="ka10006",
            body=body,
            path="chart"
        )

        if response and response.get('return_code') == 0:
            # 응답 구조 확인
            output = response.get('output', {})

            # output이 dict이면 리스트로 변환
            if isinstance(output, dict):
                chart_data = output.get('list', [])
            else:
                chart_data = output if isinstance(output, list) else []

            logger.info(f"{stock_code} 일봉 차트 {len(chart_data)}개 조회 완료")
            return chart_data
        else:
            logger.error(f"일봉 차트 조회 실패: {response.get('return_msg')}")
            return []


# Standalone function for backward compatibility
def get_daily_chart(stock_code: str, period: int = 20, date: str = None) -> List[Dict[str, Any]]:
    """
    일봉 차트 데이터 조회 (standalone function)

    Args:
        stock_code: 종목코드
        period: 조회 기간 (일수)
        date: 기준일 (YYYYMMDD, None이면 최근 거래일)

    Returns:
        일봉 데이터 리스트
    """
    from core.rest_client import KiwoomRESTClient

    # Get client instance
    client = KiwoomRESTClient.get_instance()

    # Create MarketAPI instance
    market_api = MarketAPI(client)

    # Call method
    return market_api.get_daily_chart(stock_code, period, date)


__all__ = ['MarketAPI', 'get_daily_chart']