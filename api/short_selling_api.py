api/short_selling_api.py
공매도 API
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ShortSellingAPI:
    """
    공매도 API 클래스
    
    주요 기능:
    - 공매도 추이 조회
    """
    
    def __init__(self, client):
        """
        Args:
            client: KiwoomRESTClient 인스턴스
        """
        self.client = client
        self.base_url = "/api/dostk/shsa"
        logger.info("ShortSellingAPI 초기화")
    
    def get_short_selling_trend(
        self,
        stk_cd: str,
        strt_dt: str,
        end_dt: str,
        tm_tp: str = '1'
    ) -> List[Dict[str, Any]]:
        공매도 추이 조회 (ka10014)
        
        Args:
            stk_cd: 종목코드 (예: 005930, 039490_NX, 039490_AL)
            strt_dt: 시작일자 (YYYYMMDD)
            end_dt: 종료일자 (YYYYMMDD)
            tm_tp: 시간구분 (0:시작일, 1:기간)
        
        Returns:
            공매도 추이 리스트
        try:
            headers = {
                'api-id': 'ka10014'
            }
            
            data = {
                'stk_cd': stk_cd,
                'tm_tp': tm_tp,
                'strt_dt': strt_dt,
                'end_dt': end_dt
            }
            
            response = self.client.post(self.base_url, headers=headers, json=data)
            
            if response and response.get('return_code') == 0:
                trends = response.get('shrts_trnsn', [])
                logger.info(f"{stk_cd} 공매도 추이 {len(trends)}건 조회 성공")
                return trends
            
            return []
            
        except Exception as e:
            logger.error(f"공매도 추이 조회 실패: {e}")
            return []
    
    def analyze_short_selling(
        self,
        stk_cd: str,
        strt_dt: str,
        end_dt: str
    ) -> Dict[str, Any]:
        공매도 분석
        
        Args:
            stk_cd: 종목코드
            strt_dt: 시작일자
            end_dt: 종료일자
        
        Returns:
            공매도 분석 결과
        trends = self.get_short_selling_trend(stk_cd, strt_dt, end_dt)
        
        if not trends:
            return {}
        
        total_short_qty = sum(int(t.get('shrts_qty', 0)) for t in trends)
        
        avg_weight = sum(float(t.get('trde_wght', 0)) for t in trends) / len(trends)
        
        recent = trends[0] if trends else {}
        
        return {
            'stock_code': stk_cd,
            'period': f"{strt_dt}~{end_dt}",
            'total_short_quantity': total_short_qty,
            'average_trade_weight': round(avg_weight, 2),
            'recent_short_quantity': int(recent.get('shrts_qty', 0)),
            'recent_trade_weight': float(recent.get('trde_wght', 0)),
            'recent_avg_price': int(recent.get('shrts_avg_pric', 0)),
            'data_count': len(trends),
            'high_short_selling': avg_weight > 5.0,
        }


__all__ = ['ShortSellingAPI']