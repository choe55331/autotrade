# 분봉 데이터 문제 해결 가이드

## 🔍 문제 원인

키움 REST API는 **과거 분봉 데이터를 제공하지 않습니다**.

로그 분석:
```
stk_dt_pole_chart_qry exists but is empty or None: []
```

API 호출은 성공하지만 데이터가 빈 배열로 반환됩니다.

## 📊 키움 API 데이터 제공 정책

### 제공되는 데이터:
- ✅ **일봉 (D)**: 과거 600일치 제공
- ✅ **주봉 (W)**: 과거 데이터 제공
- ✅ **월봉 (M)**: 과거 데이터 제공

### 제공되지 않는 데이터:
- ❌ **분봉 (1/3/5/10/60분)**: 과거 데이터 없음
- ⚠️ **분봉은 장중 실시간으로만 제공**

## ✅ 해결 방법

### 방법 1: WebSocket 실시간 분봉 (장중만)

장중(09:00-15:30)에 WebSocket으로 실시간 체결 데이터를 받아 분봉을 직접 생성합니다.

```python
# WebSocket으로 1분봉 생성 예시
import asyncio
from core.websocket_manager import WebSocketManager

# 1. WebSocket 연결
ws_manager = WebSocketManager(access_token, base_url)
await ws_manager.connect()

# 2. 주식체결(0B) 구독
await ws_manager.subscribe(
    stock_codes=["005930"],
    types=["0B"],  # 주식체결
    grp_no="1"
)

# 3. 1분마다 OHLCV 집계
minute_data = {}  # {timestamp: {open, high, low, close, volume}}

async def on_tick(data):
    price = int(data['values']['10'])  # 현재가
    volume = int(data['values']['15'])  # 체결량

    # 1분 단위로 집계
    minute_key = datetime.now().replace(second=0, microsecond=0)

    if minute_key not in minute_data:
        minute_data[minute_key] = {
            'open': price,
            'high': price,
            'low': price,
            'close': price,
            'volume': volume
        }
    else:
        minute_data[minute_key]['high'] = max(minute_data[minute_key]['high'], price)
        minute_data[minute_key]['low'] = min(minute_data[minute_key]['low'], price)
        minute_data[minute_key]['close'] = price
        minute_data[minute_key]['volume'] += volume

ws_manager.register_callback('0B', on_tick)
await ws_manager.receive_loop()
```

**장점**: 실시간 정확한 분봉
**단점**: 장중에만 가능, 과거 데이터 없음

---

### 방법 2: 일봉만 사용 (권장)

대시보드에서 분봉 선택을 비활성화하고 일봉만 사용합니다.

**dashboard/templates/dashboard_apple.html** 수정:
```javascript
// 분봉 버튼 비활성화
const timeframes = [
    { value: 'D', label: '일봉' },  // 일봉만 활성화
    // { value: '60', label: '60분' },  // 비활성화
    // { value: '10', label: '10분' },  // 비활성화
    // { value: '5', label: '5분' },    // 비활성화
    // { value: '1', label: '1분' }     // 비활성화
];
```

**장점**: 안정적으로 작동
**단점**: 분봉 사용 불가

---

### 방법 3: 외부 데이터 소스 사용

Yahoo Finance, Alpha Vantage 등 외부 API로 분봉 데이터를 가져옵니다.

```python
import yfinance as yf

# Yahoo Finance로 1분봉 가져오기
ticker = yf.Ticker("005930.KS")  # 삼성전자
df = ticker.history(period="1d", interval="1m")

# OHLCV 데이터
minute_data = df[['Open', 'High', 'Low', 'Close', 'Volume']].to_dict('records')
```

**장점**: 과거 분봉 데이터 제공
**단점**: 한국 주식 지원 제한적, 실시간 아님

---

## 🧪 테스트 파일 수정

`test_chart_timeframes.py`를 수정하여 **실제 데이터가 있는 API만 성공**으로 간주합니다.

```bash
# 다시 테스트 실행
python tests/manual_tests/test_chart_timeframes.py
```

이제 다음처럼 출력됩니다:
```
✅ 성공: 1개 (일봉만)
❌ 실패: 30개 (모든 분봉 - 데이터 없음)
```

---

## 💡 권장 사항

### 단기 해결 (즉시):
**일봉만 사용**하고 분봉 버튼을 UI에서 제거합니다.

### 중기 해결 (1-2주):
**WebSocket 실시간 분봉 생성 기능**을 추가합니다.
- 장중에만 작동
- 1분 단위로 체결 데이터 집계
- 메모리에 저장 (Redis 또는 SQLite)

### 장기 해결 (1개월+):
**자체 분봉 DB 구축**
- WebSocket으로 받은 체결 데이터를 DB에 저장
- 과거 분봉 데이터 축적
- 대시보드에서 과거 분봉 조회 가능

---

## ⚠️ 중요 사실

키움 API는 **증권사 HTS/MTS에서 제공하는 모든 데이터를 REST API로 제공하지 않습니다**.

특히 **분봉은 실시간 전용**이며 과거 데이터는:
1. HTS 프로그램에서만 조회 가능
2. 또는 별도 데이터 구독 서비스 필요

REST API로는 **일봉/주봉/월봉만 과거 데이터 제공**합니다.

---

## 🎯 다음 단계

1. **테스트 재실행**: 수정된 테스트 파일로 실제 데이터 유무 확인
2. **UI 수정**: 일봉만 사용하도록 대시보드 수정
3. **WebSocket 구현** (선택): 장중 실시간 분봉 기능 추가

어떤 방법을 선택하시겠습니까?
- A) 일봉만 사용 (빠른 해결)
- B) WebSocket 실시간 분봉 구현 (중기 해결)
- C) 외부 API 통합 (장기 해결)
