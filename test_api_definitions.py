"""
test_api_definitions.py
키움증권 API 정의 탐색 스크립트

모든 API를 탐색하고 검색하는 예제
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from api.api_definitions import (
    get_api_spec,
    search_apis,
    list_apis_by_category,
    get_api_summary,
    get_popular_apis,
    get_apis_by_endpoint,
    list_endpoints,
    ALL_APIS
)


def main():
    print("\n" + "="*80)
    print("키움증권 REST API 정의 탐색".center(80))
    print("="*80 + "\n")

    # 1. API 요약 정보
    print("1️⃣ API 요약 정보")
    print("-" * 80)
    summary = get_api_summary()
    print(f"총 API 개수: {summary['total']}개\n")

    print("카테고리별 API 개수:")
    for cat_id, cat_data in summary['categories'].items():
        print(f"   - {cat_data['name']}: {cat_data['count']}개")

    print()

    # 2. 인기 API
    print("2️⃣ 자주 사용되는 API")
    print("-" * 80)
    popular = get_popular_apis()
    for api in popular[:5]:
        print(f"   [{api['api_id']}] {api['name']}")
        print(f"      → {api['description']}")

    print()

    # 3. 카테고리별 API (예: 주문)
    print("3️⃣ 주문 관련 API")
    print("-" * 80)
    order_apis = list_apis_by_category("order")
    for api_id, spec in order_apis.items():
        print(f"   [{api_id}] {spec['name']}")

    print()

    # 4. API 검색
    print("4️⃣ API 검색 (키워드: '거래량')")
    print("-" * 80)
    results = search_apis("거래량")
    for api in results[:5]:
        print(f"   [{api['api_id']}] {api['name']}")

    print()

    # 5. 특정 API 상세 정보
    print("5️⃣ API 상세 정보 (kt00018 - 계좌평가잔고)")
    print("-" * 80)
    spec = get_api_spec("kt00018")
    if spec:
        print(f"   이름: {spec['name']}")
        print(f"   엔드포인트: {spec['endpoint']}")
        print(f"   메서드: {spec['method']}")
        print(f"   설명: {spec['description']}")

        if 'request' in spec:
            print("\n   요청 파라미터:")
            for param, info in spec['request'].items():
                desc = info.get('description', '') if isinstance(info, dict) else info
                print(f"      - {param}: {desc}")

        if 'response' in spec:
            print("\n   응답 필드:")
            if isinstance(spec['response'], dict):
                for field, desc in spec['response'].items():
                    print(f"      - {field}: {desc}")
            else:
                for field in spec['response']:
                    print(f"      - {field}")

    print()

    # 6. 엔드포인트별 API
    print("6️⃣ 엔드포인트별 API 개수")
    print("-" * 80)
    endpoints = list_endpoints()
    for endpoint, name in endpoints.items():
        apis = get_apis_by_endpoint(endpoint)
        if endpoint.startswith("http") or endpoint.startswith("wss"):
            endpoint_display = "WebSocket"
        else:
            endpoint_display = endpoint
        print(f"   {name:15s} ({endpoint_display:30s}): {len(apis)}개 API")

    print()

    # 7. 카테고리별 상세 정보
    print("7️⃣ 계좌 API 상세 목록")
    print("-" * 80)
    account_apis = list_apis_by_category("account")
    for api_id in sorted(account_apis.keys())[:10]:  # 처음 10개만
        spec = account_apis[api_id]
        print(f"   [{api_id}] {spec['name']}")

    print()

    print("="*80)
    print(f"✅ 총 {len(ALL_APIS)}개의 API가 정의되어 있습니다!".center(80))
    print("="*80 + "\n")

    # 사용 예제
    print("💡 사용 예제:")
    print("-" * 80)
    print("""
from api.api_definitions import get_api_spec

# API 사양 조회
spec = get_api_spec("kt00001")  # 예수금 조회
print(f"API 이름: {spec['name']}")
print(f"엔드포인트: {spec['endpoint']}")

# API 검색
from api.api_definitions import search_apis
results = search_apis("주문")
for api in results:
    print(f"{api['api_id']}: {api['name']}")

# 카테고리별 조회
from api.api_definitions import list_apis_by_category
order_apis = list_apis_by_category("order")
    """)

    print()


if __name__ == '__main__':
    main()
