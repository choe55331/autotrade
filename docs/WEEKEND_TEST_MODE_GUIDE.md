# 주말/장마감 후 테스트 모드 가이드

## 개요

주말(24시간)이나 장마감 이후(오전 8시 이전, 오후 8시 이후)에 **가장 최근 정상 영업일 데이터**로 모든 기능을 테스트할 수 있습니다.

키움증권 확인 사항:
- ✅ REST API로 장이 안 열렸을 때도 가장 최근일 데이터로 테스트 가능
- ✅ 주문은 실제로 발생하지 않으므로 안전하게 모든 기능 테스트 가능

## 테스트 모드 활성화 조건

테스트 모드는 다음 시간대에 자동 활성화됩니다:

| 조건 | 설명 | 사용 데이터 |
|------|------|------------|
| **주말** | 토요일, 일요일 24시간 | 금요일 데이터 |
| **평일 새벽** | 오전 8시 이전 | 전날 데이터 |
| **평일 야간** | 오후 8시 이후 | 당일 데이터 |
| **장 마감 시간** | 15:30 이후 ~ 20:00 | 당일 데이터 |

## 주요 기능

### 1. 자동 영업일 판단

`utils/trading_date.py`의 함수들이 자동으로 가장 최근 영업일을 계산합니다:

```python
from utils.trading_date import (
    get_last_trading_date,
    get_trading_date_with_fallback,
    is_market_hours,
    is_after_market_hours
)

# 가장 최근 거래일 (YYYYMMDD)
trading_date = get_last_trading_date()

# 장 운영 시간 여부
is_open = is_market_hours()  # 09:00 ~ 15:30

# 최근 5일 거래일 리스트
recent_dates = get_trading_date_with_fallback(5)
```

### 2. 테스트 모드 매니저

`features/test_mode_manager.py`가 전체 기능을 자동으로 테스트합니다:

```python
from features.test_mode_manager import TestModeManager
import asyncio

# 테스트 모드 매니저 생성
manager = TestModeManager()

# 테스트 모드 활성화 확인
if manager.check_and_activate_test_mode():
    print(f"테스트 모드 활성화됨")
    print(f"사용할 데이터 날짜: {manager.test_date}")

    # 전체 기능 테스트 실행
    results = await manager.run_comprehensive_test()
```

### 3. 테스트 항목

다음 기능들이 자동으로 테스트됩니다:

1. **계좌 조회** - 예수금, 잔고 확인
2. **시장 탐색** - KOSPI/KOSDAQ 종목 리스트 조회
3. **종목 정보** - 현재가, 시가, 고가, 저가 등
4. **차트 데이터** - 일봉, 분봉 차트 조회
5. **호가 조회** - 10단계 호가 및 잔량
6. **잔고 조회** - 보유 종목 및 수익률
7. **AI 분석** - 기술적 지표, 감성 분석
8. **매매 시뮬레이션** - 매수/매도 (실제 주문 미발생)

## 사용 방법

### 방법 1: 통합 테스트 스크립트

프로젝트 루트에서 실행:

```bash
python run_weekend_test.py
```

이 스크립트는 다음을 순차적으로 테스트합니다:
1. 거래일 유틸리티 기능
2. REST API 호출 (가장 최근 영업일 데이터)
3. WebSocket 연결 테스트
4. 전체 WebSocket 기능 테스트 (장 운영 시간에만)

### 방법 2: 개별 테스트

#### REST API 테스트

```python
import asyncio
from features import run_test_mode

# 테스트 실행
results = asyncio.run(run_test_mode())

if results:
    print(f"테스트 완료: {len(results['tests'])}개 항목")
```

#### WebSocket 테스트

```bash
python test_websocket_v2.py
```

WebSocket 구독 가능 항목 (18개 TR 타입):
- `00`: 주문체결 (계좌 기반)
- `04`: 잔고 (계좌 기반)
- `0A`: 주식시세 (현재가, 거래량)
- `0B`: 주식체결
- `0C`: 주식우선호가
- `0D`: 주식호가잔량 (10단계)
- `0E`: 주식시간외호가
- `0F`: 주식당일거래원
- `0G`: ETF NAV
- `0H`: 주식예상체결
- `0J`: 업종지수
- `0U`: 업종등락
- `0g`: 주식종목정보
- `0m`: ELW 이론가
- `0s`: 장시작시간
- `0u`: ELW 지표
- `0w`: 종목프로그램매매
- `1h`: VI발동/해제

⚠️ **주의**: 장 운영 시간이 아닐 때는 WebSocket 연결만 테스트되고, 실시간 데이터는 수신되지 않습니다.

## 테스트 결과

테스트 결과는 자동으로 `test_results/` 폴더에 저장됩니다:

```
test_results/
├── test_mode_results_20251101_091234.json
├── websocket_test_v2_20251101_091500.txt
└── ...
```

### 결과 예시

```json
{
  "test_mode": true,
  "test_date": "20251031",
  "start_time": "2025-11-01T09:12:34",
  "tests": {
    "account_info": {
      "success": true,
      "data": { "deposit": 5000000 }
    },
    "market_search": {
      "success": true,
      "stock_count": 2500
    },
    "stock_info": {
      "success": true,
      "tested_stocks": [
        { "code": "005930", "success": true, "price": 75000 },
        { "code": "000660", "success": true, "price": 130000 }
      ]
    }
  }
}
```

## 주요 특징

### ✅ 장점

1. **실제 데이터 기반** - 가장 최근 영업일의 실제 시장 데이터 사용
2. **안전한 테스트** - 실제 주문 발생 없이 모든 기능 테스트 가능
3. **자동 영업일 계산** - 주말, 공휴일 자동 처리
4. **전체 기능 포괄** - 8가지 핵심 기능 자동 테스트
5. **상세한 로깅** - 모든 테스트 결과 JSON 파일로 저장

### ⚠️ 제한사항

1. **WebSocket 실시간 데이터** - 장 운영 시간(09:00-15:30)에만 수신
2. **주문 미발생** - 매수/매도 시뮬레이션만 가능, 실제 주문은 발생하지 않음
3. **일부 API** - 일부 API는 장 운영 시간에만 데이터 반환

## 문제 해결

### WebSocket 연결 실패

```
❌ WebSocket 연결 타임아웃 (5초 초과)
```

**해결책**:
- 인터넷 연결 확인
- credentials 설정 확인 (`_immutable/credentials/secrets.json`)
- 키움 서버 상태 확인

### API 호출 실패

```
❌ 계좌 조회 실패
```

**해결책**:
- API 키 및 시크릿 확인
- 계좌번호 확인
- API 토큰 만료 여부 확인

### 의존성 오류

```
ModuleNotFoundError: No module named 'numpy'
```

**해결책**:
```bash
pip install numpy pandas websockets requests
```

## API 참고 문서

자세한 API 사양은 다음 문서를 참조하세요:

- `_immutable/api_specs/API_USAGE_GUIDE.md` - API 사용 가이드
- `_immutable/api_specs/by_category/` - 카테고리별 API 스펙
- `kiwoom_docs/` - 키움증권 API 공식 문서

## 예제 코드

### 주말에 종목 분석하기

```python
import asyncio
from features.test_mode_manager import TestModeManager

async def weekend_analysis():
    manager = TestModeManager()

    # 테스트 모드 확인
    if not manager.check_and_activate_test_mode():
        print("정규 장 시간입니다")
        return

    print(f"테스트 날짜: {manager.test_date}")

    # 종목 정보 조회 테스트
    await manager._test_stock_info()

    # 차트 데이터 조회 테스트
    await manager._test_chart_data()

    # AI 분석 테스트
    await manager._test_ai_analysis()

# 실행
asyncio.run(weekend_analysis())
```

### 장마감 후 전략 백테스트

```python
import asyncio
from features.test_mode_manager import TestModeManager

async def after_hours_backtest():
    manager = TestModeManager()

    if not manager.check_and_activate_test_mode():
        print("장 운영 시간입니다")
        return

    print(f"백테스트 날짜: {manager.test_date}")

    # 전체 기능 테스트
    results = await manager.run_comprehensive_test()

    # 결과 분석
    if results:
        successful_tests = sum(
            1 for test in results['tests'].values()
            if test.get('success')
        )
        total_tests = len(results['tests'])
        print(f"성공: {successful_tests}/{total_tests}")

asyncio.run(after_hours_backtest())
```

## 관련 파일

| 파일 | 설명 |
|------|------|
| `utils/trading_date.py` | 거래일 계산 유틸리티 |
| `features/test_mode_manager.py` | 테스트 모드 매니저 |
| `run_weekend_test.py` | 통합 테스트 스크립트 |
| `test_websocket_v2.py` | WebSocket 테스트 (18개 TR 타입) |
| `test_verified_apis_fixed.py` | 검증된 API 테스트 |

## 지원

문제가 발생하거나 질문이 있으면:

1. `test_results/` 폴더의 로그 파일 확인
2. `docs/API_USAGE_GUIDE.md` 참조
3. 키움증권 고객센터 문의 (1544-9000)
