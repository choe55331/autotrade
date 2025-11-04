# NXT 시간대 종합 테스트 가이드

## 개요

NXT 시간(08:00-09:00, 15:30-20:00)에 현재가 조회와 매수 주문이 실패하는 문제를 해결하기 위한 종합 테스트입니다.

**테스트하는 것:**
1. 현재가 조회 10가지 접근법
2. 주문 파라미터 조합 (dmst_stex_tp × trde_tp)

## 실행 방법

### 1. NXT 시간대에 실행 (권장)

```bash
# NXT 시간: 오전 8:00-9:00 또는 오후 3:30-8:00
python test_nxt_comprehensive.py
```

### 2. 정규장 시간에도 비교 테스트 가능

```bash
# 정규장 시간: 오전 9:00-오후 3:30
python test_nxt_comprehensive.py
```

## 테스트 내용

### 📊 현재가 조회 테스트 (10가지)

| 접근법 | 설명 | API |
|--------|------|-----|
| 1 | ka10003 기본 체결정보 | ka10003 |
| 2 | ka10003 + 호가 fallback | ka10003 → ka10004 |
| 3 | ka10004 호가정보 | ka10004 |
| 4 | 시간외단일가 API | ka10087 |
| 5 | 보유종목에서 현재가 추출 | kt00004 |
| 6 | 일봉 차트 최신 데이터 | ka10030 |
| 7 | 분봉 차트 최신 데이터 | ka10031 |
| 8 | ka10003 (dmst_stex_tp=KRX) | ka10003 |
| 9 | ka10003 (dmst_stex_tp=NXT) | ka10003 |
| 10 | ka10003 (dmst_stex_tp=SOR) | ka10003 |

### 📋 주문 파라미터 조합 테스트

**dmst_stex_tp (시장구분):**
- `KRX`: 한국거래소
- `NXT`: NXT 시장
- `SOR`: Smart Order Routing

**trde_tp (거래유형):**
- `0`: 지정가
- `3`: 시장가
- `5`: 조건부지정가
- `6`: 최유리지정가
- `7`: 최우선지정가
- `10`: 장전시간외
- `13`: 장후시간외
- `16`: 시간외단일가
- `20`: 장전시간외우선
- `23`: 장후시간외우선
- `26`: 시간외단일가우선

**총 조합:** 3 × 11 = 33가지

## 예상 결과

### NXT 시간대 (15:30-20:00)

**예상 성공 조합:**
```
현재가 조회:
✅ 접근법 4: ka10087 시간외단일가
✅ 접근법 9: ka10003 (dmst_stex_tp=NXT)

주문:
✅ dmst_stex_tp=NXT, trde_tp=16 (시간외단일가)
✅ dmst_stex_tp=NXT, trde_tp=13 (장후시간외)
```

### 정규장 시간 (09:00-15:30)

**예상 성공 조합:**
```
현재가 조회:
✅ 접근법 1: ka10003 기본
✅ 접근법 8: ka10003 (dmst_stex_tp=KRX)

주문:
✅ dmst_stex_tp=KRX, trde_tp=0 (지정가)
✅ dmst_stex_tp=KRX, trde_tp=3 (시장가)
```

## 결과 파일

테스트 실행 후 다음 파일이 생성됩니다:

```
test_results_nxt_YYYYMMDD_HHMMSS.json
```

### 결과 파일 구조

```json
{
  "timestamp": "2025-11-04T16:30:00",
  "is_nxt_time": true,
  "is_market_time": false,
  "price_tests": [
    {
      "approach": "9_raw_api_nxt",
      "stock_code": "005930",
      "success": true,
      "price": 71500,
      "source": "raw_api_nxt"
    }
  ],
  "order_tests": [
    {
      "combination": "dmst_stex_tp=NXT, trde_tp=16",
      "success": true,
      "ord_no": "0000123456"
    }
  ],
  "summary": {
    "price_tests": {
      "total": 30,
      "success": 6,
      "success_rate": "20.0%",
      "successful_approaches": ["4_ka10087_nxt_single", "9_raw_api_nxt"]
    },
    "order_tests": {
      "total": 33,
      "success": 2,
      "success_rate": "6.1%",
      "successful_combinations": [
        "dmst_stex_tp=NXT, trde_tp=16",
        "dmst_stex_tp=NXT, trde_tp=13"
      ]
    }
  }
}
```

## 주의사항

⚠️ **주문 테스트 주의:**
- 실제 주문이 발생할 수 있습니다
- 최소 수량(1주)으로 테스트합니다
- 테스트 실행 전 확인 프롬프트가 표시됩니다
- 'yes' 입력 시에만 주문 테스트가 진행됩니다

## 테스트 후 조치

### 1. 결과 분석

```bash
# 결과 파일 확인
cat test_results_nxt_YYYYMMDD_HHMMSS.json | jq '.summary'

# 성공한 현재가 조회 방법
cat test_results_nxt_YYYYMMDD_HHMMSS.json | jq '.summary.price_tests.successful_approaches'

# 성공한 주문 조합
cat test_results_nxt_YYYYMMDD_HHMMSS.json | jq '.summary.order_tests.successful_combinations'
```

### 2. 코드 적용

성공한 조합을 찾았다면:

#### api/market.py 수정
```python
def get_stock_price(self, stock_code: str) -> Optional[Dict[str, Any]]:
    from utils.trading_date import is_nxt_hours

    # NXT 시간대 판별
    if is_nxt_hours():
        # 성공한 접근법 적용
        body = {
            "stk_cd": stock_code,
            "dmst_stex_tp": "NXT"  # 테스트 결과에서 확인
        }
    else:
        body = {"stk_cd": stock_code}

    # ...
```

#### api/order.py 수정
```python
def buy_stock(self, stock_code: str, quantity: int, price: int) -> Optional[str]:
    from utils.trading_date import is_nxt_hours

    # NXT 시간대 판별
    if is_nxt_hours():
        dmst_stex_tp = "NXT"  # 테스트 결과에서 확인
        trde_tp = "16"        # 테스트 결과에서 확인
    else:
        dmst_stex_tp = "KRX"
        trde_tp = "0"

    # ...
```

## 문제 해결

### 모든 현재가 조회가 실패하는 경우

1. 네트워크 연결 확인
2. API 키 유효성 확인
3. 장 운영 시간 확인
4. 로그 확인: `tail -f logs/autotrade.log`

### 모든 주문이 실패하는 경우

1. 계좌 잔고 확인
2. 매수가능금액 확인
3. 종목코드 유효성 확인
4. 거래정지 여부 확인

## 기대 효과

이 테스트를 통해 다음을 확인할 수 있습니다:

✅ NXT 시간대에 실시간 현재가를 가져올 수 있는 방법
✅ NXT 시간대에 주문할 수 있는 파라미터 조합
✅ 시간대별 최적의 API 호출 방법
✅ Fallback 전략의 유효성

## 추가 참고

- [키움증권 API 문서](api/kiwoom_api_specs.py)
- [거래 시간 유틸리티](utils/trading_date.py)
- [이전 NXT 패치](tests/manual_tests/patches/fix_nxt_price.py)
