"""
api/theme_api.py
테마 API
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ThemeAPI:
    """
    테마 API 클래스
    
    주요 기능:
    - 테마 그룹별 정보 조회
    - 테마 구성종목 조회
    """
    
    def __init__(self, client):
        """
        Args:
            client: KiwoomRESTClient 인스턴스
        """
        self.client = client
        self.base_url = "/api/dostk/thme"
        logger.info("ThemeAPI 초기화")
    
    def get_theme_groups(
        self,
        qry_tp: str = '0',
        stk_cd: str = '',
        date_tp: str = '10',
        thema_nm: str = '',
        flu_pl_amt_tp: str = '1',
        stex_tp: str = '1'
    ) -> List[Dict[str, Any]]:
        """
        테마 그룹별 정보 조회 (ka90001)
        
        Args:
            qry_tp: 검색구분 (0:전체, 1:테마검색, 2:종목검색)
            stk_cd: 종목코드
            date_tp: n일전 (1~99)
            thema_nm: 테마명
            flu_pl_amt_tp: 등락수익구분 (1:상위기간수익률, 2:하위기간수익률, 3:상위등락률, 4:하위등락률)
            stex_tp: 거래소구분 (1:KRX, 2:NXT, 3:통합)
        
        Returns:
            테마 그룹 리스트
        """
        try:
            headers = {
                'api-id': 'ka90001'
            }
            
            data = {
                'qry_tp': qry_tp,
                'stk_cd': stk_cd,
                'date_tp': date_tp,
                'thema_nm': thema_nm,
                'flu_pl_amt_tp': flu_pl_amt_tp,
                'stex_tp': stex_tp
            }
            
            response = self.client.post(self.base_url, headers=headers, json=data)
            
            if response and response.get('return_code') == 0:
                themes = response.get('thema_grp', [])
                logger.info(f"테마 그룹 {len(themes)}개 조회 성공")
                return themes
            
            return []
            
        except Exception as e:
            logger.error(f"테마 그룹 조회 실패: {e}")
            return []
    
    def get_theme_stocks(
        self,
        thema_grp_cd: str,
        date_tp: str = '10',
        stex_tp: str = '1'
    ) -> Dict[str, Any]:
        """
        테마 구성종목 조회 (ka90002)
        
        Args:
            thema_grp_cd: 테마그룹코드
            date_tp: n일전 (1~99)
            stex_tp: 거래소구분 (1:KRX, 2:NXT, 3:통합)
        
        Returns:
            테마 구성종목 정보
        """
        try:
            headers = {
                'api-id': 'ka90002'
            }
            
            data = {
                'date_tp': date_tp,
                'thema_grp_cd': thema_grp_cd,
                'stex_tp': stex_tp
            }
            
            response = self.client.post(self.base_url, headers=headers, json=data)
            
            if response and response.get('return_code') == 0:
                result = {
                    'flu_rt': response.get('flu_rt', '0.00'),
                    'dt_prft_rt': response.get('dt_prft_rt', '0.00'),
                    'stocks': response.get('thema_comp_stk', [])
                }
                logger.info(f"테마 구성종목 {len(result['stocks'])}개 조회 성공")
                return result
            
            return {'stocks': []}
            
        except Exception as e:
            logger.error(f"테마 구성종목 조회 실패: {e}")
            return {'stocks': []}
    
    def get_top_themes(
        self,
        limit: int = 10,
        date_tp: str = '10',
        sort_by: str = 'profit'
    ) -> List[Dict[str, Any]]:
        """
        상위 테마 조회
        
        Args:
            limit: 조회 개수
            date_tp: n일전
            sort_by: 정렬 기준 ('profit': 수익률, 'change': 등락률)
        
        Returns:
            상위 테마 리스트
        """
        flu_pl_amt_tp = '1' if sort_by == 'profit' else '3'
        
        themes = self.get_theme_groups(
            qry_tp='0',
            date_tp=date_tp,
            flu_pl_amt_tp=flu_pl_amt_tp
        )
        
        return themes[:limit]


__all__ = ['ThemeAPI']