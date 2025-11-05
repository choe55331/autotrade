# WebSocket 끊김 문제 해결 가이드

## 문제 상황
- test_websocket_only.py에서는 성공
- 대시보드에서는 계속 "끊김" 표시

## 원인 분석

WebSocket 연결이 끊기는 주요 원인:
1. **인증 토큰 만료**: Bearer 토큰이 시간 지나면 만료
2. **Ping/Pong 타임아웃**: 20초 간격으로 ping 보내야 함
3. **구독 메시지 형식**: 잘못된 형식이면 서버가 연결 끊음
4. **네트워크 불안정**: 일시적 네트워크 문제

## test_websocket_only.py에서 성공한 패턴

```python
async with websockets.connect(
    ws_url,
    additional_headers={
        'authorization': f'Bearer {access_token}'
    },
    ping_interval=20,    # ✅ 중요!
    ping_timeout=10      # ✅ 중요!
) as websocket:
    # 구독 메시지 전송
    await websocket.send(json.dumps({
        "trnm": "REG",
        "grp_no": "1",
        "refresh": "1",
        "data": [{
            "item": ["005930"],  # 종목코드
            "type": ["0B"]       # 주식체결
        }]
    }))
```

## 대시보드 WebSocket 수정 필요사항

### 1. 연결 설정
```python
# ❌ 기존 (문제 있을 수 있음)
websocket = await websockets.connect(url)

# ✅ 수정
websocket = await websockets.connect(
    url,
    additional_headers={'authorization': f'Bearer {token}'},
    ping_interval=20,  # 20초마다 ping
    ping_timeout=10,   # 10초 안에 pong 없으면 종료
    close_timeout=10
)
```

### 2. 재연결 로직
```python
async def connect_with_retry(url, token, max_retries=3):
    """재연결 로직"""
    for attempt in range(max_retries):
        try:
            ws = await websockets.connect(
                url,
                additional_headers={'authorization': f'Bearer {token}'},
                ping_interval=20,
                ping_timeout=10
            )
            return ws
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 지수 백오프
            else:
                raise
```

### 3. 토큰 갱신
```python
# 30분마다 토큰 갱신
async def refresh_token_periodically():
    while True:
        await asyncio.sleep(1800)  # 30분
        new_token = rest_client.get_token()
        # WebSocket 재연결
```

## 대시보드 수정 파일

확인 필요한 파일들:
```
dashboard/
├── app_apple.py          # 메인 Flask 앱
├── websocket_handler.py  # WebSocket 핸들러 (있다면)
├── static/js/
│   └── websocket.js      # 프론트엔드 WebSocket 코드
└── templates/
    └── dashboard.html
```

## 빠른 해결 방법

### 방법 1: ping_interval/timeout 설정 (가장 중요!)
대시보드 WebSocket 연결에 다음 추가:
```python
ping_interval=20,
ping_timeout=10
```

### 방법 2: 연결 상태 모니터링
```python
async def monitor_websocket(ws):
    """WebSocket 상태 모니터링"""
    try:
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=30)
                # 메시지 처리
            except asyncio.TimeoutError:
                # 30초간 메시지 없으면 ping 전송
                await ws.ping()
    except websockets.exceptions.ConnectionClosed:
        # 재연결
        pass
```

### 방법 3: 자동 재연결
```python
while True:
    try:
        async with websockets.connect(...) as ws:
            # 구독 및 메시지 수신
            pass
    except Exception as e:
        print(f"연결 끊김, 5초 후 재연결: {e}")
        await asyncio.sleep(5)
```

## 테스트 방법

1. **test_websocket_only.py 실행**
```bash
python tests/manual_tests/test_websocket_only.py
```
→ 모든 테스트 성공 확인

2. **대시보드에서 WebSocket 로그 확인**
- 브라우저 개발자 도구 → Console
- 연결 상태 메시지 확인
- 에러 메시지 확인

3. **WebSocket 연결 시간 측정**
- 몇 초/분 후에 끊기는지 확인
- 20초마다 ping이 가는지 확인

## 추가 체크사항

- [ ] `ping_interval=20` 설정되어 있는가?
- [ ] `ping_timeout=10` 설정되어 있는가?
- [ ] Bearer 토큰이 올바른가?
- [ ] 구독 메시지 형식이 올바른가?
- [ ] 재연결 로직이 있는가?
- [ ] 토큰 갱신 로직이 있는가?

## 참고

성공한 test_websocket_only.py 코드를 참고하여 대시보드 WebSocket 코드를 수정하면 됩니다.

핵심:
- **ping_interval=20 필수!**
- **재연결 로직 필수!**
- **토큰 갱신 고려!**
