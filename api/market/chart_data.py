"""
api/market/chart_data.py
차트 및 히스토리컬 데이터 조회 API (Enhanced v5.9)
"""

v5.9 개선사항:
- 분봉 차트 데이터 조회 추가 (1/5/15/30/60분)
- 다양한 시간프레임 지원
- 데이터 검증 및 에러 핸들링 강화
import logging
from typing import Dict, Any, List, Literal
from utils.trading_date import get_last_trading_date

logger = logging.getLogger(__name__)


class ChartDataAPI:
    """
    차트 및 히스토리컬 데이터 조회 API (Enhanced v5.9)

    주요 기능:
    - 일봉 차트 데이터 조회
    - 분봉 차트 데이터 조회 (1/5/15/30/60분)
    """

    def __init__(self, client):
        """
        ChartDataAPI 초기화

        Args:
            client: KiwoomRESTClient 인스턴스
        """
        self.client = client
        logger.debug("ChartDataAPI 초기화 완료 (v5.9 - 분봉 지원)")

    def get_daily_chart(
        self,
        stock_code: str,
        period: int = 20,
        date: str = None
    ) -> List[Dict[str, Any]]:
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
        if not date:
            date = get_last_trading_date()

        body = {
            "stk_cd": stock_code,
            "base_dt": date,
            "upd_stkpc_tp": "1"
        }

        response = self.client.request(
            api_id="ka10081",
            body=body,
            path="chart"
        )

        if response and response.get('return_code') == 0:
            daily_data = response.get('stk_dt_pole_chart_qry', [])

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
            return standardized_data[:period] if period else standardized_data
        else:
            logger.error(f"일봉 차트 조회 실패: {response.get('return_msg')}")
            return []

    def get_minute_chart(
        self,
        stock_code: str,
        interval: Literal[1, 5, 15, 30, 60] = 1,
        count: int = 100,
        adjusted: bool = True
    ) -> List[Dict[str, Any]]:
        분봉 차트 데이터 조회 (ka10080 사용) - v5.9 NEW

        Args:
            stock_code: 종목코드
            interval: 분봉 간격 (1, 5, 15, 30, 60분)
            count: 조회할 데이터 개수 (기본 100개)
            adjusted: 수정주가 반영 여부 (기본 True)

        Returns:
            분봉 데이터 리스트
            [
                {
                    'date': '20231201',
                    'time': '093000',
                    'open': 70000,
                    'high': 71000,
                    'low': 69500,
                    'close': 70500,
                    'volume': 100000
                },
                ...
            ]
        valid_intervals = [1, 5, 15, 30, 60]
        if interval not in valid_intervals:
            logger.error(f"유효하지 않은 분봉 간격: {interval}분. 유효한 값: {valid_intervals}")
            return []

        body = {
            "stk_cd": stock_code,
            "tic_scope": str(interval),
            "upd_stkpc_tp": "1" if adjusted else "0"
        }

        try:
            response = self.client.request(
                api_id="ka10080",
                body=body,
                path="chart"
            )

            if response and response.get('return_code') == 0:
                minute_data = response.get('stk_tic_pole_chart_qry', [])

                standardized_data = []
                for item in minute_data:
                    try:
                        standardized_data.append({
                            'date': item.get('dt', ''),
                            'time': item.get('tm', ''),
                            'open': int(item.get('open_pric', 0)),
                            'high': int(item.get('high_pric', 0)),
                            'low': int(item.get('low_pric', 0)),
                            'close': int(item.get('cur_prc', 0)),
                            'volume': int(item.get('trde_qty', 0))
                        })
                    except (ValueError, TypeError) as e:
                        logger.warning(f"분봉 데이터 파싱 실패: {e}")
                        continue

                logger.info(f"{stock_code} {interval}분봉 {len(standardized_data)}개 조회 완료")
                return standardized_data[:count] if count else standardized_data
            else:
                error_msg = response.get('return_msg', 'Unknown error') if response else 'No response'
                logger.error(f"분봉 차트 조회 실패: {error_msg}")
                return []

        except Exception as e:
            logger.error(f"분봉 차트 조회 중 예외 발생: {e}")
            return []

    def get_multi_timeframe_data(
        self,
        stock_code: str,
        timeframes: List[Literal[1, 5, 15, 30, 60, 'daily']] = [1, 5, 15, 'daily']
    ) -> Dict[str, List[Dict[str, Any]]]:
        다중 시간프레임 차트 데이터 한번에 조회 - v5.9 NEW

        Args:
            stock_code: 종목코드
            timeframes: 조회할 시간프레임 리스트
                        숫자는 분봉 간격, 'daily'는 일봉

        Returns:
            시간프레임별 데이터 딕셔너리
            {
                '1': [...],
                '5': [...],
                '15': [...],
                'daily': [...]
            }
        result = {}

        for tf in timeframes:
            try:
                if tf == 'daily':
                    data = self.get_daily_chart(stock_code, period=20)
                    result['daily'] = data
                    logger.info(f"{stock_code} 일봉 {len(data)}개 조회")
                else:
                    data = self.get_minute_chart(stock_code, interval=tf, count=100)
                    result[str(tf)] = data
                    logger.info(f"{stock_code} {tf}분봉 {len(data)}개 조회")
            except Exception as e:
                logger.error(f"{stock_code} {tf} 타임프레임 조회 실패: {e}")
                result[str(tf) if tf != 'daily' else 'daily'] = []

        logger.info(f"{stock_code} 다중 시간프레임 조회 완료: {list(result.keys())}")
        return result


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

    client = KiwoomRESTClient.get_instance()

    chart_api = ChartDataAPI(client)

    return chart_api.get_daily_chart(stock_code, period, date)


def get_minute_chart(
    stock_code: str,
    interval: Literal[1, 5, 15, 30, 60] = 1,
    count: int = 100,
    adjusted: bool = True
) -> List[Dict[str, Any]]:
    분봉 차트 데이터 조회 (standalone function) - v5.9 NEW

    Args:
        stock_code: 종목코드
        interval: 분봉 간격 (1, 5, 15, 30, 60분)
        count: 조회할 데이터 개수
        adjusted: 수정주가 반영 여부

    Returns:
        분봉 데이터 리스트
    from core.rest_client import KiwoomRESTClient

    client = KiwoomRESTClient.get_instance()
    chart_api = ChartDataAPI(client)
    return chart_api.get_minute_chart(stock_code, interval, count, adjusted)


def get_multi_timeframe_data(
    stock_code: str,
    timeframes: List[Literal[1, 5, 15, 30, 60, 'daily']] = [1, 5, 15, 'daily']
) -> Dict[str, List[Dict[str, Any]]]:
    다중 시간프레임 데이터 조회 (standalone function) - v5.9 NEW

    Args:
        stock_code: 종목코드
        timeframes: 조회할 시간프레임 리스트

    Returns:
        시간프레임별 데이터 딕셔너리
    from core.rest_client import KiwoomRESTClient

    client = KiwoomRESTClient.get_instance()
    chart_api = ChartDataAPI(client)
    return chart_api.get_multi_timeframe_data(stock_code, timeframes)


__all__ = [
    'ChartDataAPI',
    'get_daily_chart',
    'get_minute_chart',
    'get_multi_timeframe_data',
]
