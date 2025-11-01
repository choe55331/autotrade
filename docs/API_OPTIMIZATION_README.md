# Kiwoom REST API 최적화 결과

## 📊 최종 결과

- **검증된 API**: 132개
- **검증된 호출**: 347개 (모두 실제 데이터 수신 확인)
- **신규 발견 API**: 28개 (문서에서 발견, 테스트 필요)

## 🎯 최적화 개요

### 입력 데이터
- `comprehensive_api_debugger.py 결과 로그.txt`: 394개 API 호출 결과
- `all_394_api_calls.json`: 394개 API 호출의 파라미터 정보
- `kiwoom_docs/`: 키움증권 공식 문서 (16개 파일, 25,188 라인)

### 최적화 프로세스
1. ✅ **완전 성공 API (121개)**: 모든 variant가 데이터 수신 성공 → 모두 포함
2. ⚠️ **부분 성공 API (11개)**: 일부 variant만 성공 → 성공한 것만 포함 (20개 제거)
3. ❌ **전체 실패 API (12개)**: 모든 variant 실패 → 목록에서 제외
4. 🆕 **신규 API (28개)**: 문서에서 발견 → 향후 테스트 필요

## 📁 생성된 파일

### 1. `production_api_config.json` (117KB) ⭐️ **프로덕션용**
프로덕션 환경에서 사용할 최종 API 설정
- 132개 검증된 API
- 카테고리별 분류 (account, market, stock_info 등)
- 각 variant의 검증 상태 포함

### 2. `optimized_api_calls.json` (209KB)
전체 최적화 데이터 (메타데이터 포함)
- 최적화 통계
- 최적화 규칙
- 문서 기반 최적화 제안

### 3. `optimized_api_calls_simple.json` (77KB)
간소화된 API 목록
- API ID별 name, variants, parameters만 포함
- 빠른 참조용

### 4. `api_usage_examples.json` (2KB)
API 사용 예제
- 카테고리별 대표 API 호출 예제
- Request header, body 샘플

### 5. `api_optimization_report.txt` (4KB)
최종 요약 보고서
- 최적화 프로세스 상세 설명
- 부분 성공 API 목록
- 권장 사항

## 🔧 부분 성공 API 상세

다음 11개 API는 일부 variant가 실패하여 성공한 것만 포함:

| API ID | API 명 | 유지 | 제거 |
|--------|--------|------|------|
| kt00010 | 주문인출가능금액요청 | Var 1, 3 | 1개 |
| ka10073 | 일자별종목별실현손익요청_기간 | Var 1, 2 | 1개 |
| ka10072 | 일자별종목별실현손익요청_일자 | Var 1 | 2개 |
| kt00007 | 계좌별주문체결내역상세요청 | Var 4, 5 | 3개 |
| ka10054 | 변동성완화장치 | Var 1, 2 | 1개 |
| ka10064 | 장중투자자별매매차트요청 | Var 2 | 2개 |
| ka10021 | 호가잔량급증요청 | Var 1, 2, 4 | 1개 |
| ka90001 | 테마그룹별요청 | Var 1, 2 | 2개 |
| ka30003 | ELWLP보유일별추이요청 | Var 1 | 2개 |
| ka30004 | ELW괴리율요청 | Var 1 | 3개 |
| ka30005 | ELW조건검색요청 | Var 1 | 2개 |

**총**: 18개 variant 유지, 20개 variant 제거

## 📋 카테고리별 분류

```
account        :  21개 API  (계좌 관련)
market         :   8개 API  (시세/차트)
stock_info     :  27개 API  (종목정보)
ranking        :  22개 API  (순위정보)
theme          :   2개 API  (테마)
elw            :   8개 API  (ELW)
etf            :   9개 API  (ETF)
other          :  35개 API  (기타)
```

## 🚀 사용 방법

### Python에서 사용

```python
import json

# 프로덕션 설정 로드
with open('production_api_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 특정 API 조회
api_id = 'kt00005'  # 체결잔고요청
api_info = config['apis'][api_id]

print(f"API 명: {api_info['name']}")
print(f"Variant 수: {len(api_info['variants'])}")

# 첫 번째 variant 사용
variant = api_info['variants'][0]
print(f"Path: {variant['path']}")
print(f"Parameters: {variant['parameters']}")
```

### API 호출 예제

```python
import requests

# 토큰 발급 (사전에 필요)
token = "your_bearer_token"

# API 호출
api_id = "kt00005"
variant = config['apis'][api_id]['variants'][0]

headers = {
    "Content-Type": "application/json; charset=utf-8",
    "authorization": f"Bearer {token}",
    "api-id": api_id
}

url = f"https://api.kiwoom.com/api/dostk/{variant['path']}"
response = requests.post(url, headers=headers, json=variant['parameters'])

print(response.json())
```

## 📌 권장 사항

1. **프로덕션 배포**: `production_api_config.json` 사용
2. **신규 API 테스트**: 28개 신규 API는 8:00-20:00 시간대에 테스트
3. **부분 성공 API**: 검증된 variant만 사용 (위 표 참조)
4. **실패 API 재검토**: 12개 전체 실패 API는 파라미터 재검토 필요

## 🔍 전체 실패 API 목록 (제외됨)

다음 12개 API는 모든 variant가 실패하여 제외:

1. kt00012 - 신용보증금율별주문가능수량조회요청
2. kt00009 - 계좌별주문체결현황요청
3. kt50020 - 금현물 잔고확인
4. kt50021 - 금현물 예수금
5. kt50032 - 금현물 거래내역조회
6. ka10075 - 미체결요청
7. ka10076 - 체결요청
8. ka10088 - 미체결 분할주문 상세
9. ka10010 - 업종프로그램요청
10. kt50030 - 금현물 주문체결전체조회
11. kt50031 - 금현물 주문체결조회
12. kt50075 - 금현물 미체결조회

**원인**: no_data 또는 api_error → 추후 파라미터 재검토 필요

## 📊 통계 요약

| 항목 | 개수 |
|------|------|
| 원본 API 호출 | 394개 |
| 성공 (데이터 확인) | 347개 |
| 실패/no_data | 47개 |
| 최종 검증된 API | 132개 |
| 최종 검증된 호출 | 347개 |
| 제거된 API | 12개 |
| 제거된 variant | 20개 |
| 신규 발견 API | 28개 |

## 🛠️ 관련 스크립트

- `test_all_394_calls.py`: 394개 전체 API 테스트 (8:00-20:00 실행)
- `optimize_with_docs.py`: 문서 기반 API 최적화
- `create_optimized_api_list.py`: 최적화 목록 생성
- `create_production_config.py`: 프로덕션 설정 및 보고서 생성

## 📅 생성 일시

2025-11-01 04:05:37

---

**모든 API 호출은 실제 데이터 수신이 확인되었습니다.** ✅
