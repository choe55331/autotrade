"""
config/demo_stocks.py
데모/테스트용 종목 리스트
"""

시세 API가 구현되기 전까지 사용할 고정 종목 리스트

DEMO_STOCKS = [
    {
        "stock_code": "005930",
        "stock_name": "삼성전자",
        "market": "KOSPI",
        "sector": "전기전자"
    },
    {
        "stock_code": "000660",
        "stock_name": "SK하이닉스",
        "market": "KOSPI",
        "sector": "전기전자"
    },
    {
        "stock_code": "035420",
        "stock_name": "NAVER",
        "market": "KOSPI",
        "sector": "서비스업"
    },
    {
        "stock_code": "005380",
        "stock_name": "현대차",
        "market": "KOSPI",
        "sector": "운수장비"
    },
    {
        "stock_code": "051910",
        "stock_name": "LG화학",
        "market": "KOSPI",
        "sector": "화학"
    },
    {
        "stock_code": "006400",
        "stock_name": "삼성SDI",
        "market": "KOSPI",
        "sector": "전기전자"
    },
    {
        "stock_code": "035720",
        "stock_name": "카카오",
        "market": "KOSPI",
        "sector": "서비스업"
    },
    {
        "stock_code": "068270",
        "stock_name": "셀트리온",
        "market": "KOSPI",
        "sector": "의약품"
    },
    {
        "stock_code": "207940",
        "stock_name": "삼성바이오로직스",
        "market": "KOSPI",
        "sector": "의약품"
    },
    {
        "stock_code": "000270",
        "stock_name": "기아",
        "market": "KOSPI",
        "sector": "운수장비"
    },
]


def get_demo_stock_list():
    """데모 종목 리스트 반환"""
    return DEMO_STOCKS.copy()


def get_stock_by_code(stock_code: str):
    """종목코드로 종목 정보 조회"""
    for stock in DEMO_STOCKS:
        if stock["stock_code"] == stock_code:
            return stock.copy()
    return None


def get_stocks_by_sector(sector: str):
    """업종별 종목 조회"""
    return [s for s in DEMO_STOCKS if s["sector"] == sector]


__all__ = [
    'DEMO_STOCKS',
    'get_demo_stock_list',
    'get_stock_by_code',
    'get_stocks_by_sector',
]
