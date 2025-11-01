# API 사용 가이드

검증된 키움증권 REST API 사용법

## 📊 검증 통계

- **테스트 날짜**: 2025-11-01 14:16:38
- **총 API**: 133개
- **총 호출 variants**: 370개
- **성공률**: 93.5% (346/370)
- **카테고리**: 7개 (account, market, ranking, search, info, elw, other)

## 🚀 빠른 시작

### 1. 기본 사용법

```python
from core.rest_client import KiwoomRESTClient

# 클라이언트 초기화 (자동으로 credentials 로드)
client = KiwoomRESTClient()

# 검증된 API 호출 (가장 권장)
result = client.call_verified_api('kt00005', variant_idx=1)
print(result)
# {'return_code': 0, 'stk_cntr_remn': [...]}
```

### 2. 수동 API 호출 (고급)

```python
# 직접 파라미터 지정
result = client.request(
    api_id='kt00005',
    body={'dmst_stex_tp': 'KRX'},
    path='acnt'
)
```

### 3. 파라미터 Override

```python
# 검증된 파라미터 기반, 일부만 override
result = client.call_verified_api(
    api_id='kt00005',
    variant_idx=1,
    body_override={'dmst_stex_tp': 'NXT'}  # KRX → NXT 변경
)
```

## 📂 카테고리별 API

### 계좌 관련 (Account)

```python
from config import get_api_loader

loader = get_api_loader()

# 계좌 API 목록 조회
account_apis = loader.get_account_apis()
for api in account_apis:
    print(f"{api['api_id']}: {api['api_name']}")

# 사용 예시
client = KiwoomRESTClient()

# 체결잔고 조회
balance = client.call_verified_api('kt00005')

# 계좌평가잔고 조회
evaluation = client.call_verified_api('kt00018')

# 계좌수익률 조회
profit = client.call_verified_api('ka10085')

# 예수금 조회
deposit = client.call_verified_api('kt00001')
```

### 시세 관련 (Market)

```python
# 시세 API 목록 조회
market_apis = loader.get_market_apis()

# 현재가 조회
current_price = client.call_verified_api('ka10001')

# 일봉 데이터 조회
daily_chart = client.call_verified_api('ka10006')

# 분봉 데이터 조회
minute_chart = client.call_verified_api('ka10009')
```

### 순위 관련 (Ranking)

```python
# 순위 API 목록 조회
ranking_apis = loader.get_ranking_apis()

# 거래량 상위 종목
top_volume = client.call_verified_api('ka10003')

# 등락률 상위 종목
top_rate = client.call_verified_api('ka10004')

# 시가총액 상위 종목
top_cap = client.call_verified_api('ka10034')
```

### 검색 관련 (Search)

```python
# 검색 API 목록 조회
search_apis = loader.get_search_apis()

# 조건검색 종목 조회
search_result = client.call_verified_api('ka10014')

# 섹터 종목 조회
sector_stocks = client.call_verified_api('ka10010')
```

## 🔍 API 탐색

### 사용 가능한 모든 API 조회

```python
from config import load_successful_apis

# 모든 검증된 API 로드
all_apis = load_successful_apis()

print(f"총 {len(all_apis)}개 API 사용 가능")

for api_id, api_info in all_apis.items():
    print(f"\n{api_id}: {api_info['api_name']}")
    print(f"  카테고리: {api_info['category']}")
    print(f"  Variants: {api_info['total_variants']}개")

    # 첫 번째 호출 예시
    if api_info['calls']:
        first_call = api_info['calls'][0]
        print(f"  경로: {first_call['path']}")
        print(f"  파라미터: {first_call['body']}")
```

### 특정 API 검색

```python
from config import search_api, get_api_by_id

# 키워드로 검색
results = search_api('체결')
for api in results:
    print(f"{api['api_id']}: {api['api_name']}")

# API ID로 직접 조회
api_info = get_api_by_id('kt00005')
if api_info:
    print(f"API 이름: {api_info['api_name']}")
    print(f"Variants: {len(api_info['calls'])}개")
```

### 카테고리별 조회

```python
from config import get_api_by_category, APICategory

# 계좌 관련 API
account_apis = get_api_by_category(APICategory.ACCOUNT)
print(f"계좌 API: {len(account_apis)}개")

# 시세 관련 API
market_apis = get_api_by_category(APICategory.MARKET)
print(f"시세 API: {len(market_apis)}개")

# 순위 관련 API
ranking_apis = get_api_by_category(APICategory.RANKING)
print(f"순위 API: {len(ranking_apis)}개")
```

## 💡 고급 사용법

### 1. Context Manager 사용

```python
# 자동 리소스 정리
with KiwoomRESTClient() as client:
    result = client.call_verified_api('kt00005')
    print(result)
# 자동으로 토큰 폐기 및 세션 종료
```

### 2. 에러 처리

```python
client = KiwoomRESTClient()

result = client.call_verified_api('kt00005')

if result.get('return_code') == 0:
    # 성공
    data = result.get('stk_cntr_remn', [])
    print(f"데이터 {len(data)}건 조회 성공")
elif result.get('return_code') == -404:
    # 검증되지 않은 API
    print(f"오류: {result.get('return_msg')}")
else:
    # 기타 오류
    print(f"API 오류 ({result.get('return_code')}): {result.get('return_msg')}")
```

### 3. 여러 Variant 호출

```python
# API의 모든 variant 테스트
api_info = get_api_by_id('kt00005')

for call in api_info['calls']:
    variant_idx = call['variant_idx']
    result = client.call_verified_api('kt00005', variant_idx=variant_idx)

    if result.get('return_code') == 0:
        print(f"Variant {variant_idx}: 성공")
    else:
        print(f"Variant {variant_idx}: 실패 - {result.get('return_msg')}")
```

### 4. 실시간 데이터 활용

```python
import time

client = KiwoomRESTClient()

while True:
    # 현재가 조회
    price = client.call_verified_api('ka10001')

    if price.get('return_code') == 0:
        stocks = price.get('stk_price', [])
        for stock in stocks[:5]:  # 상위 5개만
            print(f"{stock.get('stk_nm')}: {stock.get('cur_price')}원")

    time.sleep(5)  # 5초마다 조회
```

## 📝 주요 API 목록

### 계좌 API

| API ID | 이름 | 설명 |
|--------|------|------|
| kt00005 | 체결잔고요청 | 체결된 잔고 조회 |
| kt00018 | 계좌평가잔고내역요청 | 계좌 평가 잔고 |
| ka10085 | 계좌수익률요청 | 계좌 수익률 |
| kt00001 | 예수금상세현황요청 | 예수금 조회 |
| kt00004 | 계좌평가현황요청 | 계좌 평가 현황 |

### 시세 API

| API ID | 이름 | 설명 |
|--------|------|------|
| ka10001 | 현재가요청 | 주식 현재가 |
| ka10006 | 일봉요청 | 일봉 차트 데이터 |
| ka10009 | 분봉요청 | 분봉 차트 데이터 |
| ka10007 | 주봉요청 | 주봉 차트 데이터 |
| ka10008 | 월봉요청 | 월봉 차트 데이터 |

### 순위 API

| API ID | 이름 | 설명 |
|--------|------|------|
| ka10003 | 거래량상위요청 | 거래량 TOP |
| ka10004 | 등락률상위요청 | 등락률 TOP |
| ka10034 | 시가총액상위요청 | 시가총액 TOP |
| ka10035 | 외인연속순매매상위요청 | 외국인 매매 TOP |

## ⚠️ 주의사항

### 1. 검증되지 않은 API 사용

```python
# ❌ 나쁜 예: 검증되지 않은 API 직접 호출
result = client.request('unknown_api', {}, 'path')

# ✅ 좋은 예: 검증된 API 사용
result = client.call_verified_api('kt00005')
```

### 2. 파라미터 임의 수정

```python
# ❌ 나쁜 예: 검증되지 않은 파라미터
result = client.request('kt00005', {'wrong_param': 'value'}, 'acnt')

# ✅ 좋은 예: 검증된 파라미터 사용
result = client.call_verified_api('kt00005', variant_idx=1)
```

### 3. API 호출 빈도

```python
# API 호출 제한을 고려하세요
# 기본: 0.3초 간격 (config.API_RATE_LIMIT)

import time

for i in range(10):
    result = client.call_verified_api('kt00005')
    # 클라이언트가 자동으로 속도 제한 처리
    # 추가 sleep 불필요
```

## 🔧 문제 해결

### API 목록이 로드되지 않음

```python
# _immutable/api_specs/successful_apis.json 파일 확인
from pathlib import Path

api_file = Path('_immutable/api_specs/successful_apis.json')
if not api_file.exists():
    print("❌ API 사양 파일이 없습니다")
    print("테스트를 먼저 실행하세요: python tests/api_tests/test_verified_and_corrected_apis_fixed.py")
else:
    print("✅ API 사양 파일 존재")
```

### credentials 오류

```python
# _immutable/credentials/secrets.json 확인
from config import get_credentials

creds = get_credentials()
is_valid, errors = creds.validate()

if not is_valid:
    print("❌ 자격증명 오류:")
    for error in errors:
        print(f"  - {error}")
else:
    print("✅ 자격증명 정상")
```

## 📚 추가 리소스

- [API 최적화 가이드](../../../docs/API_OPTIMIZATION_README.md)
- [테스트 가이드](../../../docs/FINAL_TEST_GUIDE.md)
- [프로젝트 README](../../../README.md)
- [테스트 결과](../../../test_results/)

## 🤝 기여

새로운 API를 발견하거나 개선사항이 있다면:

1. API 테스트 실행
2. 성공 확인 (return_code=0, 실제 데이터 존재)
3. `_immutable/api_specs/successful_apis.json` 업데이트
4. 이 가이드에 사용 예시 추가

---

**마지막 업데이트**: 2025-11-01
**검증 기준**: 346/370 API 성공 (93.5%)
