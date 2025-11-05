# 웹소켓 구독 기능 가이드

**날짜**: 2025-11-05
**목적**: AutoTrade 시스템의 웹소켓 실시간 구독 기능 활용 전략

---

## 📡 웹소켓 구독 개요

### 현재 상태
- ✅ 웹소켓 연결: 성공
- ✅ 로그인: 성공
- ❌ 실시간 구독: **미활성화**

### 문제점
- REST API만 사용 중 (느림, rate limit 문제)
- 실시간 가격 업데이트 없음
- 손절/익절 타이밍 지연

---

## 🎯 지원되는 구독 유형

### 1. 현재가 구독 (KA10003)

**용도**: 실시간 주가 모니터링

**메시지 형식**:
```json
{
    "trnm": "KA10003",
    "stk_cd_list": ["005930", "000660"],
    "stex_tp": "KRX"
}
```

**응답 형식**:
```json
{
    "trnm": "KA10003",
    "stk_cd": "005930",
    "cur_prc": "100600",
    "chge": "-4300",
    "chge_rt": "-4.10",
    "acc_qty": "36647829",
    "time": "132233"
}
```

**활용 시나리오**:
- 보유 종목 실시간 모니터링
- 손절/익절 조건 체크 (0.5초마다)
- 매수 후 즉시 구독 시작

---

### 2. 호가 구독 (KA10004)

**용도**: 매수/매도 최적 가격 결정

**메시지 형식**:
```json
{
    "trnm": "KA10004",
    "stk_cd_list": ["005930"],
    "stex_tp": "KRX"
}
```

**응답 형식**:
```json
{
    "trnm": "KA10004",
    "stk_cd": "005930",
    "buy_prc_1": "100500",
    "buy_qty_1": "5000",
    "sell_prc_1": "100600",
    "sell_qty_1": "3000",
    "tot_buy_qty": "150000",
    "tot_sell_qty": "120000"
}
```

**활용 시나리오**:
- AI 검토 후 매수 직전 호가 확인
- 매수 호가 강도 실시간 계산
- 최적 진입 가격 결정

---

### 3. 체결 구독 (KA10005)

**용도**: 거래량 및 체결 강도 실시간 추적

**메시지 형식**:
```json
{
    "trnm": "KA10005",
    "stk_cd_list": ["005930"],
    "stex_tp": "KRX"
}
```

**응답 형식**:
```json
{
    "trnm": "KA10005",
    "stk_cd": "005930",
    "cheg_prc": "100600",
    "chge": "-4300",
    "cheg_qty": "100",
    "time": "132233",
    "buy_sell_gb": "1"
}
```

**활용 시나리오**:
- 거래량 급등 탐지
- 체결 강도 실시간 계산
- 대량 매도/매수 포착

---

## 🔄 구독 시나리오별 전략

### 시나리오 1: 신규 매수 진행

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 스캔: 거래량 급등 종목 발견 (삼성전자 005930)              │
│    → 아직 구독 안 함                                          │
├─────────────────────────────────────────────────────────────┤
│ 2. Deep Scan: 기관/외국인 데이터 수집                         │
│    → 아직 구독 안 함                                          │
├─────────────────────────────────────────────────────────────┤
│ 3. AI 검토: BUY 결정                                          │
│    → 호가 구독 시작 (KA10004)                                 │
│    → 5초간 호가 관찰                                           │
├─────────────────────────────────────────────────────────────┤
│ 4. 매수 주문 실행                                             │
│    → 호가 구독 해제                                           │
│    → 현재가 + 체결 구독 시작 (KA10003, KA10005)             │
├─────────────────────────────────────────────────────────────┤
│ 5. 실시간 모니터링 (보유 중)                                   │
│    → 0.5초마다 현재가 수신                                     │
│    → 손절/익절 조건 체크                                       │
│    → 트레일링 스톱 업데이트                                     │
├─────────────────────────────────────────────────────────────┤
│ 6. 매도 조건 충족                                             │
│    → 즉시 매도 주문                                           │
│    → 모든 구독 해제                                           │
└─────────────────────────────────────────────────────────────┘
```

**코드 예시**:
```python
# 3. AI 검토 후
if ai_decision == 'buy':
    # 호가 구독
    subscribe_orderbook(['005930'])
    time.sleep(5)  # 5초간 호가 관찰

    # 최적 가격 결정
    best_price = get_optimal_price('005930')

    # 4. 매수 주문
    order_result = buy('005930', quantity, best_price)

    if order_result['success']:
        # 호가 구독 해제
        unsubscribe_orderbook(['005930'])

        # 현재가 + 체결 구독
        subscribe_price(['005930'])
        subscribe_execution(['005930'])
```

---

### 시나리오 2: 보유 종목 모니터링

```
보유 종목: [삼성전자, SK하이닉스, NAVER]
└─> 자동 구독: KA10003 (현재가)

실시간 수신 (0.5초마다):
├─ 삼성전자: 100,600원 (-4.10%)
├─ SK하이닉스: 195,000원 (+2.50%)
└─ NAVER: 187,500원 (+1.20%)

각 종목별 체크:
├─ 손절 조건: 현재가 < 진입가 * 0.95
├─ 익절 조건: 현재가 > 진입가 * 1.10
└─ 트레일링 스톱: 현재가 < 최고가 * 0.97

조건 충족 시:
└─> 즉시 매도 주문 → 구독 해제
```

**코드 예시**:
```python
# 보유 종목 자동 구독
def auto_subscribe_holdings():
    holdings = get_current_holdings()
    stock_codes = [h['stock_code'] for h in holdings]

    if stock_codes:
        subscribe_price(stock_codes)
        logger.info(f"보유 종목 구독 시작: {len(stock_codes)}개")

# 실시간 가격 수신 핸들러
def on_price_update(data):
    stock_code = data['stk_cd']
    current_price = int(data['cur_prc'])

    position = get_position(stock_code)
    if not position:
        return

    # 손절 체크
    if current_price < position.entry_price * 0.95:
        sell(stock_code, reason="손절 -5%")
        unsubscribe_price([stock_code])

    # 익절 체크
    elif current_price > position.entry_price * 1.10:
        sell(stock_code, reason="익절 +10%")
        unsubscribe_price([stock_code])

    # 트레일링 스톱
    elif current_price > position.max_price:
        position.max_price = current_price
    elif current_price < position.max_price * 0.97:
        sell(stock_code, reason="트레일링 스톱 -3%")
        unsubscribe_price([stock_code])
```

---

### 시나리오 3: 거래량 급등 모니터링

```
워치리스트: [상위 100개 거래량 종목]
└─> 구독: KA10005 (체결)

실시간 체결 수신:
├─ 체결 강도 계산 (매수/매도 비율)
├─ 1분간 거래량 집계
└─ 급등 탐지 (평균 대비 3배 이상)

급등 탐지 시:
├─> Deep Scan 트리거
├─> AI 검토 요청
└─> 매수 조건 충족 시 즉시 진입
```

**코드 예시**:
```python
# 워치리스트 체결 구독
def monitor_top_stocks():
    top_stocks = get_top_volume_stocks(limit=100)
    stock_codes = [s['code'] for s in top_stocks]

    subscribe_execution(stock_codes)
    logger.info(f"워치리스트 구독: {len(stock_codes)}개")

# 체결 데이터 핸들러
def on_execution(data):
    stock_code = data['stk_cd']
    quantity = int(data['cheg_qty'])

    # 1분간 거래량 집계
    add_to_volume_tracker(stock_code, quantity)

    # 거래량 급등 체크 (1분마다)
    if should_check_volume_spike():
        spikes = detect_volume_spikes()

        for stock_code, spike_ratio in spikes:
            if spike_ratio >= 3.0:  # 평균 대비 3배
                logger.info(f"거래량 급등 탐지: {stock_code} ({spike_ratio:.1f}배)")
                trigger_deep_scan(stock_code)
```

---

## 📊 구독 관리 전략

### 1. 구독 우선순위

| 우선순위 | 대상 | 구독 유형 | 예상 종목 수 |
|---------|------|----------|-------------|
| 1순위 | 보유 종목 | 현재가 (KA10003) | 1-10개 |
| 2순위 | AI 검토 중 | 호가 (KA10004) | 1-3개 |
| 3순위 | 워치리스트 | 체결 (KA10005) | 50-100개 |

### 2. 구독 제한

- **최대 동시 구독**: 150종목 (키움 API 제한)
- **보유 종목**: 무제한 (우선순위 최상)
- **워치리스트**: 100개까지
- **AI 검토**: 3개까지 (5분 TTL)

### 3. 자동 구독 해제

```python
# 시간 기반 자동 해제
- 매수 후 매도 완료: 즉시 해제
- AI 검토 중 종목: 5분 후 자동 해제
- 워치리스트: 거래량 순위 변경 시 재구독

# 조건 기반 자동 해제
- 장 마감 (15:30): 모든 구독 해제
- 점심 시간 (12:00-13:00): 워치리스트만 유지
- NXT 시간 (15:30-20:00): 보유 종목만 유지
```

---

## 🛠️ 구현 가이드

### WebSocket 구독 관리자 (신규 파일)

**파일**: `utils/websocket_subscription_manager.py`

```python
"""
utils/websocket_subscription_manager.py
웹소켓 구독 관리자
"""
import time
from typing import List, Dict, Set, Callable
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class WebSocketSubscriptionManager:
    """웹소켓 구독 관리자"""

    def __init__(self, ws_client):
        self.ws_client = ws_client

        # 구독 상태 추적
        self.price_subscriptions: Set[str] = set()  # KA10003
        self.orderbook_subscriptions: Set[str] = set()  # KA10004
        self.execution_subscriptions: Set[str] = set()  # KA10005

        # 구독 만료 추적 (임시 구독용)
        self.temp_subscriptions: Dict[str, datetime] = {}

        # 콜백 함수
        self.price_callbacks: List[Callable] = []
        self.orderbook_callbacks: List[Callable] = []
        self.execution_callbacks: List[Callable] = []

        logger.info("웹소켓 구독 관리자 초기화")

    def subscribe_price(self, stock_codes: List[str], temporary: bool = False):
        """현재가 구독"""
        new_codes = [code for code in stock_codes if code not in self.price_subscriptions]

        if not new_codes:
            return

        message = {
            "trnm": "KA10003",
            "stk_cd_list": new_codes,
            "stex_tp": "KRX"
        }

        self.ws_client.send(message)
        self.price_subscriptions.update(new_codes)

        # 임시 구독 (5분 후 자동 해제)
        if temporary:
            expire_time = datetime.now() + timedelta(minutes=5)
            for code in new_codes:
                self.temp_subscriptions[f"price_{code}"] = expire_time

        logger.info(f"현재가 구독: {len(new_codes)}개 추가 (total: {len(self.price_subscriptions)}개)")

    def subscribe_orderbook(self, stock_codes: List[str]):
        """호가 구독"""
        new_codes = [code for code in stock_codes if code not in self.orderbook_subscriptions]

        if not new_codes:
            return

        message = {
            "trnm": "KA10004",
            "stk_cd_list": new_codes,
            "stex_tp": "KRX"
        }

        self.ws_client.send(message)
        self.orderbook_subscriptions.update(new_codes)

        # 호가는 기본적으로 임시 (5분)
        expire_time = datetime.now() + timedelta(minutes=5)
        for code in new_codes:
            self.temp_subscriptions[f"orderbook_{code}"] = expire_time

        logger.info(f"호가 구독: {len(new_codes)}개 추가")

    def subscribe_execution(self, stock_codes: List[str]):
        """체결 구독"""
        new_codes = [code for code in stock_codes if code not in self.execution_subscriptions]

        if not new_codes:
            return

        message = {
            "trnm": "KA10005",
            "stk_cd_list": new_codes,
            "stex_tp": "KRX"
        }

        self.ws_client.send(message)
        self.execution_subscriptions.update(new_codes)

        logger.info(f"체결 구독: {len(new_codes)}개 추가 (total: {len(self.execution_subscriptions)}개)")

    def unsubscribe_price(self, stock_codes: List[str]):
        """현재가 구독 해제"""
        codes_to_remove = [code for code in stock_codes if code in self.price_subscriptions]

        if not codes_to_remove:
            return

        # TODO: 키움 API 구독 해제 메시지 (문서 확인 필요)
        # 현재는 로컬에서만 제거
        for code in codes_to_remove:
            self.price_subscriptions.discard(code)
            self.temp_subscriptions.pop(f"price_{code}", None)

        logger.info(f"현재가 구독 해제: {len(codes_to_remove)}개")

    def unsubscribe_orderbook(self, stock_codes: List[str]):
        """호가 구독 해제"""
        codes_to_remove = [code for code in stock_codes if code in self.orderbook_subscriptions]

        if not codes_to_remove:
            return

        for code in codes_to_remove:
            self.orderbook_subscriptions.discard(code)
            self.temp_subscriptions.pop(f"orderbook_{code}", None)

        logger.info(f"호가 구독 해제: {len(codes_to_remove)}개")

    def unsubscribe_execution(self, stock_codes: List[str]):
        """체결 구독 해제"""
        codes_to_remove = [code for code in stock_codes if code in self.execution_subscriptions]

        if not codes_to_remove:
            return

        for code in codes_to_remove:
            self.execution_subscriptions.discard(code)

        logger.info(f"체결 구독 해제: {len(codes_to_remove)}개")

    def register_price_callback(self, callback: Callable):
        """현재가 콜백 등록"""
        self.price_callbacks.append(callback)

    def register_orderbook_callback(self, callback: Callable):
        """호가 콜백 등록"""
        self.orderbook_callbacks.append(callback)

    def register_execution_callback(self, callback: Callable):
        """체결 콜백 등록"""
        self.execution_callbacks.append(callback)

    def handle_message(self, message: Dict):
        """웹소켓 메시지 처리"""
        trnm = message.get('trnm')

        if trnm == 'KA10003':
            # 현재가
            for callback in self.price_callbacks:
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"현재가 콜백 오류: {e}")

        elif trnm == 'KA10004':
            # 호가
            for callback in self.orderbook_callbacks:
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"호가 콜백 오류: {e}")

        elif trnm == 'KA10005':
            # 체결
            for callback in self.execution_callbacks:
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"체결 콜백 오류: {e}")

    def cleanup_expired_subscriptions(self):
        """만료된 임시 구독 정리"""
        now = datetime.now()
        expired = [
            key for key, expire_time in self.temp_subscriptions.items()
            if now > expire_time
        ]

        for key in expired:
            sub_type, stock_code = key.split('_', 1)

            if sub_type == 'price':
                self.unsubscribe_price([stock_code])
            elif sub_type == 'orderbook':
                self.unsubscribe_orderbook([stock_code])

            del self.temp_subscriptions[key]

        if expired:
            logger.info(f"만료된 구독 정리: {len(expired)}개")

    def get_subscription_summary(self) -> Dict:
        """구독 상태 요약"""
        return {
            'price': len(self.price_subscriptions),
            'orderbook': len(self.orderbook_subscriptions),
            'execution': len(self.execution_subscriptions),
            'temp': len(self.temp_subscriptions),
            'total': len(self.price_subscriptions) + len(self.orderbook_subscriptions) + len(self.execution_subscriptions)
        }


__all__ = ['WebSocketSubscriptionManager']
```

---

## 📈 기대 효과

### 1. 성능 개선
- REST API 호출 90% 감소
- 실시간 가격 업데이트 (0.5초 지연 → 즉시)
- Rate limit 문제 해결

### 2. 수익률 개선
- 손절/익절 타이밍 개선 (+15% 예상)
- 진입 가격 최적화 (+5% 예상)
- 거래량 급등 탐지 속도 향상

### 3. 시스템 안정성
- API 부하 감소
- 에러율 감소
- 확장성 향상

---

## 🚀 다음 단계

### Phase 1: 기본 구독 (이번 주)
- [ ] WebSocketSubscriptionManager 구현
- [ ] 보유 종목 자동 구독
- [ ] 현재가 콜백 연동

### Phase 2: 손익 관리 (다음 주)
- [ ] 실시간 손절/익절 체크
- [ ] 트레일링 스톱 구현
- [ ] 분할 익절 로직

### Phase 3: 고급 기능 (2주 후)
- [ ] 거래량 급등 탐지
- [ ] 호가 강도 실시간 계산
- [ ] AI 실시간 재평가

---

## 📝 참고 사항

### 키움 웹소켓 제한사항
- 최대 동시 구독: 150종목
- 메시지 크기: 8KB 이하
- 재연결 간격: 최소 5초

### 장 시간별 전략
- **08:00-09:00 (프리마켓)**: NXT 종목만 구독
- **09:00-15:30 (정규장)**: 전체 기능 활성화
- **15:30-20:00 (애프터마켓)**: 보유 종목만 구독
- **20:00-08:00 (장외)**: 모든 구독 해제
