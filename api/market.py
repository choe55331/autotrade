api/market.py
시세 및 시장 정보 API (Backward Compatibility Wrapper)

⚠️ 이 파일은 backward compatibility를 위해 유지됩니다.
   실제 구현은 api/market/ 디렉토리의 모듈들로 이동되었습니다.

새 코드에서는 다음을 사용하세요:
    from api.market import MarketAPI

    market_api = MarketAPI(client)
    price = market_api.get_stock_price('005930')

모듈 구조:
- api/market/market_data.py: 시세/호가 데이터
- api/market/chart_data.py: 차트 데이터
- api/market/ranking.py: 순위 정보
- api/market/investor_data.py: 투자자 매매 데이터
- api/market/stock_info.py: 종목/업종/테마 정보
import warnings

from api.market import (
    MarketAPI,
    MarketDataAPI,
    ChartDataAPI,
    RankingAPI,
    InvestorDataAPI,
    StockInfoAPI,
    get_daily_chart,
)

warnings.warn(
    "api.market is now modularized into 5 specialized modules. "
    "Consider updating imports to: from api.market import MarketAPI",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    'MarketAPI',
    'MarketDataAPI',
    'ChartDataAPI',
    'RankingAPI',
    'InvestorDataAPI',
    'StockInfoAPI',
    'get_daily_chart',
]
