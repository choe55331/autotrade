"""
api/market/stock_info.py
종목 정보, 업종, 테마 조회 API
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class StockInfoAPI:
    """
    종목 정보, 업종, 테마 조회 API

    주요 기능:
    - 업종 목록 및 정보 조회
    - 테마 목록 및 종목 조회
    - 종목 상세 정보 조회
    - 종목 검색
    """

    def __init__(self, client):
        """
        StockInfoAPI 초기화

        Args:
            client: KiwoomRESTClient 인스턴스
        """
        self.client = client
        logger.debug("StockInfoAPI 초기화 완료")

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


__all__ = ['StockInfoAPI']
