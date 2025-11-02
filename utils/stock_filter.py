"""
utils/stock_filter.py
종목 필터링 유틸리티
"""


# ETF 제외 키워드
ETF_KEYWORDS = [
    'KODEX',
    'TIGER',
    'KOSEF',
    'ARIRANG',
    'KINDEX',
    'TIMEFOLIO',
    'HANARO',
    'KBSTAR',
    'SMARTBETA',
    '인버스',
    '레버리지',
    'INVERSE',
    'LEVERAGE',
    'ETF',
    'ETN',
]


def is_etf(stock_name: str, stock_code: str = None) -> bool:
    """
    ETF 여부 판별

    Args:
        stock_name: 종목명
        stock_code: 종목코드 (선택)

    Returns:
        ETF 여부
    """
    if not stock_name:
        return False

    stock_name_upper = stock_name.upper()

    # ETF 키워드 체크
    for keyword in ETF_KEYWORDS:
        if keyword.upper() in stock_name_upper:
            return True

    return False


def filter_etfs(stocks: list, name_key: str = 'name', code_key: str = 'code') -> list:
    """
    ETF 제외 필터링

    Args:
        stocks: 종목 리스트
        name_key: 종목명 키
        code_key: 종목코드 키

    Returns:
        ETF 제외된 종목 리스트
    """
    filtered = []
    for stock in stocks:
        stock_name = stock.get(name_key, '')
        stock_code = stock.get(code_key, '')

        if not is_etf(stock_name, stock_code):
            filtered.append(stock)

    return filtered
