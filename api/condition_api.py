api/condition_api.py
조건검색 API
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ConditionAPI:
    """
    조건검색 API 클래스
    
    주요 기능:
    - 조건검색 목록 조회
    - 조건검색 실행 (일반/실시간)
    """
    
    def __init__(self, client):
        """
        Args:
            client: KiwoomRESTClient 인스턴스
        """
        self.client = client
        logger.info("ConditionAPI 초기화")
    
    def get_condition_list(self) -> List[Dict[str, Any]]:
        """
        조건검색 목록 조회
        
        Returns:
            조건검색식 목록
            [
                {'seq': '0', 'name': '조건1'},
                {'seq': '1', 'name': '조건2'},
                ...
            ]
        """
        try:
            logger.warning("조건검색 목록 조회는 WebSocket API 필요")
            return []
            
        except Exception as e:
            logger.error(f"조건검색 목록 조회 실패: {e}")
            return []
    
    def search_by_condition(
        self,
        seq: str,
        search_type: str = '0',
        stex_tp: str = 'K',
        cont_yn: str = 'N',
        next_key: str = ''
    ) -> Dict[str, Any]:
        조건검색 실행 (일반)
        
        Args:
            seq: 조건검색식 일련번호
            search_type: 0:조건검색, 1:조건검색+실시간
            stex_tp: K:KRX
            cont_yn: 연속조회여부
            next_key: 연속조회키
        
        Returns:
            검색 결과
        try:
            logger.warning("조건검색은 WebSocket API 필요")
            return {}
            
        except Exception as e:
            logger.error(f"조건검색 실패: {e}")
            return {}


__all__ = ['ConditionAPI']