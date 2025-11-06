"""
api/api_definitions.py
키움증권 REST API 통합 정의 모듈
"""

전체 100개 이상의 키움증권 REST API를 통합 관리합니다.
공식 문서: https://github.com/kiwoom-retail/Kiwoom-Securities

from .kiwoom_api_specs import (
    ENVIRONMENTS,
    COMMON_HEADERS,
    ACCOUNT_APIS,
    ORDER_APIS,
)

from .kiwoom_api_specs_extended import (
    MARKET_DATA_APIS,
    RANKING_APIS,
    STOCK_INFO_APIS,
    SECTOR_APIS,
    CHART_APIS,
    CONDITION_SEARCH_APIS,
)


ALL_APIS = {
    **ACCOUNT_APIS,
    **ORDER_APIS,
    **MARKET_DATA_APIS,
    **RANKING_APIS,
    **STOCK_INFO_APIS,
    **SECTOR_APIS,
    **CHART_APIS,
    **CONDITION_SEARCH_APIS,
}


API_CATEGORIES = {
    "account": {
        "name": "계좌",
        "apis": ACCOUNT_APIS,
        "count": len(ACCOUNT_APIS)
    },
    "order": {
        "name": "주문",
        "apis": ORDER_APIS,
        "count": len(ORDER_APIS)
    },
    "market_data": {
        "name": "시세",
        "apis": MARKET_DATA_APIS,
        "count": len(MARKET_DATA_APIS)
    },
    "ranking": {
        "name": "순위정보",
        "apis": RANKING_APIS,
        "count": len(RANKING_APIS)
    },
    "stock_info": {
        "name": "종목정보",
        "apis": STOCK_INFO_APIS,
        "count": len(STOCK_INFO_APIS)
    },
    "sector": {
        "name": "업종",
        "apis": SECTOR_APIS,
        "count": len(SECTOR_APIS)
    },
    "chart": {
        "name": "차트",
        "apis": CHART_APIS,
        "count": len(CHART_APIS)
    },
    "condition": {
        "name": "조건검색",
        "apis": CONDITION_SEARCH_APIS,
        "count": len(CONDITION_SEARCH_APIS)
    },
}


def get_api_spec(api_id: str):
    """
    API ID로 사양 조회

    Args:
        api_id: API ID (예: "kt00001", "kt10000", "ka10030")

    Returns:
        API 사양 딕셔너리 또는 None
    """
    return ALL_APIS.get(api_id)


def search_apis(keyword: str):
    """
    키워드로 API 검색

    Args:
        keyword: 검색 키워드 (API 이름에 포함)

    Returns:
        검색된 API 리스트
    """
    results = []
    for api_id, spec in ALL_APIS.items():
        if keyword in spec.get("name", "") or keyword in spec.get("description", ""):
            results.append({
                "api_id": api_id,
                **spec
            })
    return results


def list_apis_by_category(category: str):
    """
    카테고리별 API 목록

    Args:
        category: 카테고리 (account, order, market_data, ranking, stock_info, sector, chart, condition)

    Returns:
        API 딕셔너리
    """
    cat = API_CATEGORIES.get(category)
    return cat["apis"] if cat else {}


def get_api_categories():
    """모든 API 카테고리 정보 반환"""
    return API_CATEGORIES


def get_api_count():
    """전체 API 개수 반환"""
    return len(ALL_APIS)


def get_api_summary():
    """
    API 요약 정보

    Returns:
        카테고리별 API 개수 및 총계
    """
    summary = {
        "total": len(ALL_APIS),
        "categories": {}
    }

    for cat_id, cat_info in API_CATEGORIES.items():
        summary["categories"][cat_id] = {
            "name": cat_info["name"],
            "count": cat_info["count"]
        }

    return summary


def get_popular_apis():
    """
    자주 사용되는 API 목록

    Returns:
        인기 API 리스트
    """
    popular = [
        "kt00001",
        "kt00018",
        "kt10000",
        "kt10001",
        "ka10030",
        "ka10027",
        "ka10001",
        "ka10004",
        "ka10005",
    ]

    return [
        {
            "api_id": api_id,
            **get_api_spec(api_id)
        }
        for api_id in popular
        if get_api_spec(api_id)
    ]



def get_apis_by_endpoint(endpoint: str):
    """
    엔드포인트별 API 목록

    Args:
        endpoint: 엔드포인트 경로 (예: "/api/dostk/acnt")

    Returns:
        해당 엔드포인트를 사용하는 API 리스트
    """
    results = []
    for api_id, spec in ALL_APIS.items():
        if spec.get("endpoint") == endpoint:
            results.append({
                "api_id": api_id,
                **spec
            })
    return results


ENDPOINTS = {
    "/api/dostk/acnt": "계좌",
    "/api/dostk/ordr": "현물주문",
    "/api/dostk/crdordr": "신용주문",
    "/api/dostk/mrkcond": "시세",
    "/api/dostk/rkinfo": "순위정보",
    "/api/dostk/stkinfo": "종목정보",
    "/api/dostk/sect": "업종",
    "/api/dostk/chart": "차트",
    "wss://api.kiwoom.com:10000/api/dostk/websocket": "조건검색(WebSocket)"
}


def list_endpoints():
    """사용 가능한 모든 엔드포인트 목록"""
    return ENDPOINTS



__all__ = [
    'ENVIRONMENTS',
    'COMMON_HEADERS',

    'ALL_APIS',
    'ACCOUNT_APIS',
    'ORDER_APIS',
    'MARKET_DATA_APIS',
    'RANKING_APIS',
    'STOCK_INFO_APIS',
    'SECTOR_APIS',
    'CHART_APIS',
    'CONDITION_SEARCH_APIS',

    'API_CATEGORIES',
    'ENDPOINTS',

    'get_api_spec',
    'search_apis',
    'list_apis_by_category',
    'get_api_categories',
    'get_api_count',
    'get_api_summary',
    'get_popular_apis',
    'get_apis_by_endpoint',
    'list_endpoints',
]
