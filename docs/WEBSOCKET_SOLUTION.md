# WebSocket 연결 문제 해결 방안

## 🔍 문제 분석

테스트 결과 WebSocket 연결이 모두 실패했습니다.

### 발견된 문제점

1. **잘못된 WebSocket URL 형식**
   - 현재 코드가 사용할 수 있는 URL이 불명확

2. **구독 메시지 형식 불일치**
   - 키움 API 스펙과 다른 형식 사용

3. **인증 헤더 형식**
   - Bearer 토큰 방식이 올바른지 확인 필요

## ✅ 키움 API 문서 기준 정답

`kiwoom_docs/실시간시세.md`에 따르면:

### 1. WebSocket URL

```
운영: wss://api.kiwoom.com:10000/api/dostk/websocket
모의투자: wss://mockapi.kiwoom.com:10000/api/dostk/websocket
```

### 2. 구독 요청 형식

```json
{
  "trnm": "REG",
  "grp_no": "1",
  "refresh": "1",
  "data": [{
    "item": ["005930"],  // 종목코드 배열
    "type": ["0B"]       // 실시간 타입
  }]
}
```

### 3. 실시간 타입 (type)

| 코드 | 설명 |
|------|------|
| `00` | 주문체결 |
| `04` | 잔고 |
| `0A` | 주식기세 |
| `0B` | 주식체결 (가장 많이 사용) |
| `0C` | 주식우선호가 |
| `0D` | 주식호가잔량 |
| `0E` | 주식시간외호가 |

### 4. 응답 형식

**등록 응답:**
```json
{
  "trnm": "REG",
  "return_code": 0,
  "return_msg": ""
}
```

**실시간 데이터:**
```json
{
  "trnm": "REAL",
  "data": [{
    "type": "0B",
    "name": "주식체결",
    "item": "005930",
    "values": {
      "10": "60700",      // 현재가
      "15": "+500",       // 등락폭
      "13": "1.25"        // 등락률
    }
  }]
}
```

## 🔧 해결 방안

### 방안 1: WebSocket 비활성화 (현재 상태 유지) ✅ 권장

**장점:**
- REST API만으로도 충분히 동작
- 안정적인 운영 가능
- 재연결 부하 없음

**단점:**
- 실시간 데이터 수신 불가
- 주기적으로 REST API 호출 필요

**적용 방법:**
```python
# main.py에서 이미 적용됨
self.websocket_client = None
```

### 방안 2: WebSocket 재구현 (시간 소요)

**필요 작업:**

1. **core/websocket_client.py 수정**
   ```python
   class WebSocketClient:
       def __init__(self, rest_client):
           # URL 가져오기
           base_url = rest_client.base_url
           if 'mockapi' in base_url:
               self.ws_url = "wss://mockapi.kiwoom.com:10000/api/dostk/websocket"
           else:
               self.ws_url = "wss://api.kiwoom.com:10000/api/dostk/websocket"

           self.token = rest_client.token
           # ...

       def subscribe_execution(self, stock_code: str):
           """주식 체결 정보 구독 (키움 스펙)"""
           message = {
               "trnm": "REG",
               "grp_no": "1",
               "refresh": "1",
               "data": [{
                   "item": [stock_code],
                   "type": ["0B"]  # 주식체결
               }]
           }
           self.ws.send(json.dumps(message))
   ```

2. **메시지 파싱 로직 수정**
   ```python
   def _on_message(self, ws, message):
       data = json.loads(message)

       if data.get('trnm') == 'REG':
           # 등록 응답
           if data.get('return_code') == 0:
               logger.info("구독 성공")
           else:
               logger.error(f"구독 실패: {data.get('return_msg')}")

       elif data.get('trnm') == 'REAL':
           # 실시간 데이터
           for item in data.get('data', []):
               stock_code = item.get('item')
               values = item.get('values', {})
               price = values.get('10')  # 현재가
               # 처리...
   ```

3. **인증 헤더 확인**
   ```python
   # WebSocket 연결 시
   header = [f"authorization: Bearer {self.token}"]
   ```

### 방안 3: 하이브리드 접근 (부분 활성화)

**적용 방법:**
- 중요한 종목만 WebSocket 구독
- 나머지는 REST API 사용
- 에러 발생 시 자동으로 REST API로 폴백

```python
def setup_realtime_data(self):
    try:
        # WebSocket 시도
        if self.websocket_client:
            for stock_code in self.important_stocks:
                self.websocket_client.subscribe_execution(stock_code)
    except Exception as e:
        logger.warning(f"WebSocket 실패, REST API 사용: {e}")
        self.websocket_client = None
```

## 📊 권장 사항

### 현재 상황: **방안 1 (비활성화) 유지** ✅

**이유:**
1. ✅ REST API로 충분히 동작 중
2. ✅ NXT 시간외 거래 정답 찾음 (핵심 기능 완료)
3. ⏱️ WebSocket 재구현에 많은 시간 소요
4. ⚠️ 키움 서버가 주기적으로 연결 종료 ("Bye" 메시지)

### 향후 필요 시: **방안 2 (재구현)**

WebSocket이 꼭 필요한 경우:
1. 위의 "해결 방안 2" 참고
2. `kiwoom_docs/실시간시세.md` 스펙 준수
3. 테스트 후 단계적 적용

## 🧪 WebSocket 테스트 (재구현 후)

재구현을 완료한 후 다시 테스트:

```bash
python tests/manual_tests/test_websocket_connection.py
```

**체크리스트:**
- [ ] URL: `wss://api.kiwoom.com:10000/api/dostk/websocket`
- [ ] 구독 형식: `{"trnm": "REG", "grp_no": "1", ...}`
- [ ] 인증: `authorization: Bearer {token}`
- [ ] 응답 파싱: `trnm='REG'` (등록) vs `trnm='REAL'` (실시간)
- [ ] 재연결 로직
- [ ] 에러 핸들링

## 💡 결론

**현재 상태:**
- ✅ NXT 시간외 거래: **정답 찾음!** (dmst_stex_tp=NXT, trde_tp=0, 가격지정)
- ⚠️ WebSocket: **비활성화 상태 유지** (REST API로 충분)

**다음 단계:**
1. 현재 상태로 실제 거래 테스트
2. 안정성 확인 후 운영
3. WebSocket 필요 시 재구현 고려

**WebSocket은 선택사항이며, 현재 시스템은 REST API만으로도 정상 작동합니다!** ✅
