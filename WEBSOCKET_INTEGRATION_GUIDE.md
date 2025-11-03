# WebSocket 통합 가이드

## 🎯 성공한 WebSocket 패턴

테스트 결과 **Case 0-1이 성공**했습니다:

```python
# 로그인 패턴
login_request = {
    "trnm": "LOGIN",
    "token": access_token
}

# 구독 패턴
subscribe_request = {
    "trnm": "REG",
    "grp_no": "1",
    "refresh": "1",
    "data": [{
        "item": ["005930"],  # 종목코드 리스트
        "type": ["0B", "0D"]  # 타입 리스트 (0B=체결, 0D=호가)
    }]
}
```

## 📦 WebSocketManager 사용법

### 1. 기본 사용

```python
from core.websocket_manager import WebSocketManager
from core.rest_client import KiwoomRESTClient

# REST 클라이언트 초기화
rest_client = KiwoomRESTClient()

# WebSocketManager 초기화
ws_manager = WebSocketManager(
    access_token=rest_client.token,
    base_url=rest_client.base_url
)

# 연결
await ws_manager.connect()

# 구독
await ws_manager.subscribe(
    stock_codes=["005930", "000660"],  # 삼성전자, SK하이닉스
    types=["0B", "0D"],  # 체결 + 호가
    grp_no="1"
)
```

### 2. 콜백 등록

```python
# 체결 데이터 콜백
async def on_price_data(data):
    stock_code = data.get('item', '')
    values = data.get('values', {})
    price = values.get('10', '0')  # 현재가
    print(f"📈 {stock_code}: {price}원")

# 호가 데이터 콜백
async def on_orderbook_data(data):
    stock_code = data.get('item', '')
    values = data.get('values', {})
    sell_price = values.get('27', '0')  # 매도호가
    buy_price = values.get('28', '0')   # 매수호가
    print(f"📊 {stock_code}: 매도 {sell_price}원 / 매수 {buy_price}원")

# 콜백 등록
ws_manager.register_callback('0B', on_price_data)      # 주식체결
ws_manager.register_callback('0D', on_orderbook_data)  # 주식호가잔량

# 실시간 데이터 수신
await ws_manager.receive_loop()
```

### 3. main.py 통합 예제

```python
import asyncio
from core.websocket_manager import WebSocketManager
from core.rest_client import KiwoomRESTClient

async def run_with_websocket():
    """WebSocket과 함께 실행"""

    # REST 클라이언트
    rest_client = KiwoomRESTClient()

    # WebSocket 매니저
    ws_manager = WebSocketManager(
        access_token=rest_client.token,
        base_url=rest_client.base_url
    )

    # 연결
    success = await ws_manager.connect()
    if not success:
        print("❌ WebSocket 연결 실패")
        return

    # 실시간 시세 콜백
    latest_prices = {}  # 종목별 최신 가격 저장

    async def on_real_price(data):
        """실시간 체결 데이터"""
        stock_code = data.get('item', '')
        values = data.get('values', {})
        price = int(values.get('10', '0'))
        latest_prices[stock_code] = price

    ws_manager.register_callback('0B', on_real_price)

    # 매수 종목 구독
    bought_stocks = []  # 매수한 종목 리스트

    # ... 기존 main.py 로직 ...

    # 매수 후 구독 추가
    if buy_result:
        bought_stocks.append(stock_code)
        await ws_manager.subscribe(
            stock_codes=[stock_code],
            types=["0B", "0D"],  # 체결 + 호가
            grp_no="1"
        )

    # 백그라운드 태스크로 WebSocket 수신
    receive_task = asyncio.create_task(ws_manager.receive_loop())

    try:
        # 메인 로직 실행
        while True:
            # ... 기존 main.py 로직 ...

            # 실시간 가격 확인
            for stock_code in bought_stocks:
                current_price = latest_prices.get(stock_code)
                if current_price:
                    print(f"{stock_code} 현재가: {current_price:,}원")

            await asyncio.sleep(1)

    finally:
        # 종료
        receive_task.cancel()
        await ws_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(run_with_websocket())
```

## 🔧 실시간 항목 코드

| 코드 | 이름 | 설명 |
|------|------|------|
| 00 | 주문체결 | 계좌의 주문/체결 |
| 04 | 잔고 | 계좌 잔고 |
| 0A | 주식기세 | 종목 기세 |
| 0B | 주식체결 | 종목 체결 (현재가) |
| 0C | 주식우선호가 | 종목 우선호가 |
| 0D | 주식호가잔량 | 종목 호가 |
| 0E | 주식시간외호가 | 시간외 호가 |

## 📊 실시간 필드 (values)

### 0B (주식체결)

| 필드 | 한글명 | 설명 |
|------|--------|------|
| 10 | 현재가 | |
| 11 | 전일대비구분 | 2:상승, 3:보합, 5:하락 |
| 12 | 전일대비 | |
| 13 | 등락율 | |
| 14 | 거래량 | |
| 15 | 거래대금 | |

### 0D (주식호가잔량)

| 필드 | 한글명 | 설명 |
|------|--------|------|
| 27 | (최우선)매도호가 | |
| 28 | (최우선)매수호가 | |
| 121 | 매도호가총잔량 | |
| 122 | 매수호가총잔량 | |

## 🎯 활용 사례

### 1. 실시간 손익률 계산

```python
async def on_price_update(data):
    stock_code = data.get('item', '')
    current_price = int(data.get('values', {}).get('10', '0'))

    # 매수 정보 조회
    buy_info = get_buy_info(stock_code)
    if buy_info:
        buy_price = buy_info['price']
        profit_rate = (current_price - buy_price) / buy_price * 100

        print(f"{stock_code} 손익률: {profit_rate:.2f}%")

        # 목표 수익률 달성 시 매도
        if profit_rate >= 5.0:
            await sell_stock(stock_code)
```

### 2. 호가 변화 감지

```python
async def on_orderbook_update(data):
    stock_code = data.get('item', '')
    values = data.get('values', {})

    bid_total = int(values.get('122', '0'))  # 매수 총잔량
    ask_total = int(values.get('121', '0'))  # 매도 총잔량

    if ask_total > 0:
        ratio = bid_total / ask_total

        # 매수 우세 시
        if ratio > 1.5:
            print(f"{stock_code} 매수 우세 (비율: {ratio:.2f})")
```

### 3. 급등 감지

```python
price_history = {}  # {stock_code: [prices]}

async def on_price_update(data):
    stock_code = data.get('item', '')
    current_price = int(data.get('values', {}).get('10', '0'))

    if stock_code not in price_history:
        price_history[stock_code] = []

    price_history[stock_code].append(current_price)

    # 최근 5개 가격 유지
    if len(price_history[stock_code]) > 5:
        price_history[stock_code].pop(0)

    # 5개 이상 있으면 급등 체크
    if len(price_history[stock_code]) >= 5:
        first_price = price_history[stock_code][0]
        rate = (current_price - first_price) / first_price * 100

        if rate >= 2.0:
            print(f"🚀 {stock_code} 급등 감지: {rate:.2f}%")
```

## 🔄 재연결 자동 처리

WebSocketManager는 자동으로 재연결을 시도합니다:

```python
# 연결 끊김 시 자동 재연결
# - 최대 5회 시도
# - 재연결 간격: 5초
# - 재연결 성공 시 기존 구독 자동 복원

# 설정 변경
ws_manager.reconnect_delay = 10  # 재연결 간격 10초
ws_manager.max_reconnect_attempts = 10  # 최대 10회 시도
```

## 🎉 완성된 기능

✅ **WebSocketManager 클래스**
- LOGIN 패턴 자동 적용
- 자동 재연결
- 구독 관리
- 콜백 시스템

✅ **24개 스코어링 API**
- ka10003: 주식체결정보
- ka10004: 주식호가
- ka10008: 외국인 종목별 매매
- ka10009: 기관 정보
- ka10027: 등락률 순위
- ka10031: 거래량 순위
- ka10032: 거래대금 순위
- ka10045: 종목별 기관매매추이 ⭐ (Deep Scan에 통합)
- ka10059: 투자자별 매매
- ka10063: 장중 투자자별 매매 ⭐
- ka10066: 장마감후 투자자별 매매 ⭐
- ka10078: 증권사별 종목매매 ⭐
- ka10131: 기관외국인 연속매매
- 기타 11개...

✅ **Deep Scan 강화**
- ka10045 데이터 자동 수집
- 기관/외국인 매수 추세 스코어링
- 트렌드 데이터 저장 (candidate.institutional_trend)

## 📝 테스트

WebSocketManager 단독 테스트:

```bash
cd /home/user/autotrade
python core/websocket_manager.py
```

예상 출력:
```
WebSocket 테스트 시작...
✅ WebSocket 연결 성공
✅ 로그인 성공
✅ 구독 성공
📈 체결: 005930 - 현재가 60000원
📊 호가: 005930 - 매도 60100원 / 매수 59900원
...
```

## 🚀 다음 단계

main.py에 통합하여 실시간 자동매매 완성!
