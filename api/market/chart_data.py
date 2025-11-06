"""
api/market/chart_data.py
차트 및 히스토리컬 데이터 조회 API
"""
import logging
from typing import Dict, Any, List
from utils.trading_date import get_last_trading_date

logger = logging.getLogger(__name__)


class ChartDataAPI:
    """
    차트 및 히스토리컬 데이터 조회 API

    주요 기능:
    - 일봉 차트 데이터 조회
    """

    def __init__(self, client):
        """
        ChartDataAPI 초기화

        Args:
            client: KiwoomRESTClient 인스턴스
        """
        self.client = client
        logger.debug("ChartDataAPI 초기화 완료")

    def get_daily_chart(
        self,
        stock_code: str,
        period: int = 20,
        date: str = None
    ) -> List[Dict[str, Any]]:
        """
        일봉 차트 데이터 조회 (ka10081 사용)

        Args:
            stock_code: 종목코드
            period: 조회 기간 (일수) - 참고용, API는 기준일부터 과거 데이터 반환
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
            "stk_cd": stock_code,
            "base_dt": date,
            "upd_stkpc_tp": "1"  # 수정주가 반영
        }

        response = self.client.request(
            api_id="ka10081",
            body=body,
            path="chart"
        )

        if response and response.get('return_code') == 0:
            # ka10081은 'stk_dt_pole_chart_qry' 키에 데이터 반환
            daily_data = response.get('stk_dt_pole_chart_qry', [])

            # 데이터 표준화
            standardized_data = []
            for item in daily_data:
                try:
                    standardized_data.append({
                        'date': item.get('dt', ''),
                        'open': int(item.get('open_pric', 0)),
                        'high': int(item.get('high_pric', 0)),
                        'low': int(item.get('low_pric', 0)),
                        'close': int(item.get('cur_prc', 0)),
                        'volume': int(item.get('trde_qty', 0))
                    })
                except (ValueError, TypeError):
                    continue

            logger.info(f"{stock_code} 일봉 차트 {len(standardized_data)}개 조회 완료")
            return standardized_data[:period] if period else standardized_data  # period만큼만 반환
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

    # Create ChartDataAPI instance
    chart_api = ChartDataAPI(client)

    # Call method
    return chart_api.get_daily_chart(stock_code, period, date)


__all__ = ['ChartDataAPI', 'get_daily_chart']
