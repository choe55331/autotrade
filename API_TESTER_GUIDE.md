# 자동 API 테스터 사용 가이드

## 개요

`automated_api_tester.py`는 GUI 없이 CLI로 Kiwoom REST API를 자동으로 테스트하고, 성공한 API 호출 방식을 저장/재사용하는 도구입니다.

### 주요 특징

- ✅ GUI 없이 CLI로 실행 (서버 환경에서도 사용 가능)
- 💾 성공한 API 호출 자동 저장
- 🔄 저장된 검증 API만 빠르게 재테스트
- 📊 JSON 형식으로 결과 저장
- 🚫 주문 API 자동 제외 (안전)

## 파일 구조

```
autotrade/
├── automated_api_tester.py           # 메인 테스터
├── generate_verified_from_results.py # 결과 변환 도구
├── verified_api_calls.json           # 검증된 API 호출 (성공 확인됨)
├── failed_api_calls.json             # 실패한 API 호출
├── api_test_results_YYYYMMDD_HHMMSS.json  # 테스트 결과 (타임스탬프)
└── kiwoom_api_test_results.json      # 기존 테스트 결과 (참고용)
```

## 사용 방법

### 1. 검증된 API 목록 확인

```bash
python automated_api_tester.py list
```

**출력 예시:**
```
검증된 API (17개):
  ka10020: 호가잔량상위요청 - 1개 성공 호출
    마지막 테스트: 2025-11-01T15:30:00
  ka10027: 전일대비등락률상위요청 - 1개 성공 호출
    마지막 테스트: 2025-11-01T15:30:00
  ...
```

### 2. 검증된 API만 빠르게 재테스트

```bash
python automated_api_tester.py verified
```

이미 성공이 확인된 API 호출만 다시 실행하여 현재도 정상 작동하는지 확인합니다.

**특징:**
- 빠른 실행 (성공한 API만)
- 안정적 (검증된 호출만 사용)
- 주기적 모니터링에 적합

### 3. 전체 API 테스트 (새로운 성공 API 찾기)

```bash
python automated_api_tester.py all
```

account.py에 정의된 모든 API의 모든 Variant를 테스트합니다.

**특징:**
- 새로운 성공 API 발견
- verified_api_calls.json 자동 업데이트
- 주문 API 자동 제외

**⚠️ 주의:** 시간이 오래 걸립니다 (수백 개 Variant).

### 4. 디버그 모드 실행

```bash
python automated_api_tester.py all --debug
```

상세한 로그를 확인할 수 있습니다.

## 결과 파일 설명

### verified_api_calls.json (검증된 API)

**형식:**
```json
{
  "ka10027": {
    "api_name": "전일대비등락률상위요청",
    "success_count": 1,
    "total_variants": 1,
    "verified_calls": [
      {
        "path": "rkinfo",
        "body": {
          "mrkt_tp": "0",
          "sort_tp": "0",
          "trde_qty_cnd": "0",
          "stk_cnd": "0"
        },
        "data_count": 200
      }
    ],
    "last_tested": "2025-11-01T15:30:00"
  }
}
```

**용도:**
- 프로그램에서 직접 사용 가능한 API 호출 정보
- 매번 같은 방식으로 데이터 조회 가능
- 자동화 스크립트에 활용

### api_test_results_YYYYMMDD_HHMMSS.json (상세 결과)

전체 테스트 결과를 타임스탬프와 함께 저장합니다.

**형식:**
```json
[
  {
    "api_id": "ka10027",
    "api_name": "전일대비등락률상위요청",
    "path": "rkinfo",
    "body": {...},
    "timestamp": "2025-11-01T15:30:00",
    "status": "success",
    "return_code": 0,
    "return_msg": "정상적으로 처리되었습니다",
    "data_received": true,
    "data_count": 200,
    "sample_data": {...},
    "variant_index": 1,
    "total_variants": 1
  }
]
```

## 실전 활용 예시

### 예시 1: 매일 아침 데이터 수집

```bash
#!/bin/bash
# daily_market_data.sh

echo "=== 시장 데이터 수집 시작 ==="
python automated_api_tester.py verified
echo "=== 완료 ==="
```

cron 등록:
```
0 9 * * 1-5 /path/to/daily_market_data.sh
```

### 예시 2: Python 스크립트에서 검증된 API 사용

```python
import json

# 검증된 API 로드
with open('verified_api_calls.json', 'r') as f:
    verified = json.load(f)

# 특정 API 호출 정보 가져오기
api_info = verified['ka10027']
call = api_info['verified_calls'][0]

# 실제 API 호출
import kiwoom
client = kiwoom.KiwoomRESTClient()
result = client.request(
    api_id='ka10027',
    path_prefix=call['path'],
    body=call['body']
)

print(f"데이터 {len(result['pred_pre_flu_rt_upper'])}개 수신")
```

### 예시 3: 주간 전체 테스트 (새로운 API 발견)

```bash
#!/bin/bash
# weekly_full_test.sh

echo "=== 주간 전체 API 테스트 ==="
python automated_api_tester.py all
echo "=== 새로운 성공 API 확인 ==="
python automated_api_tester.py list
```

## 트러블슈팅

### Q: "API 클라이언트 초기화 실패" 오류

**A:** config.py의 API 키와 계좌번호를 확인하세요.

```python
# config.py
KIWOOM_REST_APPKEY = "your_app_key"
KIWOOM_REST_SECRETKEY = "your_secret_key"
ACCOUNT_NUMBER = "your_account_number"
KIWOOM_REST_BASE_URL = "https://..."
```

### Q: verified_api_calls.json이 없어요

**A:** 처음 실행 시 자동 생성됩니다. 또는:

```bash
python generate_verified_from_results.py
```

### Q: 특정 API만 테스트하고 싶어요

**A:** automated_api_tester.py를 수정하거나:

```python
from automated_api_tester import APITester

tester = APITester()
tester.initialize_client()
results = tester.test_api('ka10027')
print(results)
```

## 고급 활용

### 커스텀 Variant 추가

account.py를 수정하여 새로운 테스트 케이스를 추가할 수 있습니다:

```python
# account.py에서
"ka10027": lambda p: [
    ("rkinfo", {"mrkt_tp": "0", "sort_tp": "0"}),  # 기존
    ("rkinfo", {"mrkt_tp": "1", "sort_tp": "1"}),  # 코스닥, 내림차순 추가
],
```

### 성공률 통계 분석

```bash
# 여러 번 테스트 후 결과 비교
python automated_api_tester.py verified > test1.log
sleep 3600
python automated_api_tester.py verified > test2.log
diff test1.log test2.log
```

## 주의사항

- ⚠️ 주문 API (kt10xxx, kt50xxx)는 자동으로 제외됩니다
- ⚠️ API 요청 제한을 고려하여 간격을 두고 실행하세요
- ⚠️ 시장 시간 외에는 일부 API가 데이터를 반환하지 않을 수 있습니다

## 업데이트

### verified_api_calls.json 수동 편집

필요시 직접 편집하여 특정 파라미터를 고정할 수 있습니다:

```json
{
  "ka10027": {
    "verified_calls": [
      {
        "path": "rkinfo",
        "body": {
          "mrkt_tp": "0",  // <- 이 값들을 원하는 대로 수정 가능
          "sort_tp": "0"
        }
      }
    ]
  }
}
```

## 문의 및 개선

버그 리포트나 개선 제안은 이슈로 등록해주세요.
