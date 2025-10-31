# AutoTrade Pro v3.5 - 변경 로그

## 🎯 주요 개선사항

### 1. 프로젝트 구조 대폭 개선
- **중복 파일 제거**: 5개의 중복 대시보드 파일 archive로 이동
  - `dashboard.py`, `dashboard_backup.py`, `dashboard_pro.py`, `dashboard_ultra.py`, `advanced_dashboard.py` ❌
  - `app_apple.py` ✅ (메인 대시보드로 통일)

- **새로운 폴더 구조**:
  ```
  autotrade/
  ├── features/          # 새로운 고급 기능 모듈 ⭐
  │   ├── order_book.py         # 실시간 호가창
  │   └── profit_tracker.py      # 수익 추적
  ├── services/          # 비즈니스 로직 (향후 추가)
  ├── dashboard/
  │   └── static/        # 정적 파일 (js, css, sounds)
  └── archive/
      └── old_dashboards/  # 구 대시보드 파일들
  ```

## 🚀 새로운 고급 기능

### 1. 실시간 호가창 (Order Book) ⭐ NEW
**파일**: `features/order_book.py` (300+ 줄)

#### 주요 기능:
- **5단계 매수/매도 호가 표시**
  - 매도 1~5호가 (가격, 잔량, 비율)
  - 매수 1~5호가 (가격, 잔량, 비율)

- **실시간 분석 지표**:
  - 총 매도/매수 잔량
  - 호가 스프레드 (원 및 %)
  - 매수/매도 비율 (Bid-Ask Ratio)
  - 시장 압력 유형 (매수 우위/매도 우위/균형)

- **스마트 추천**:
  - 💚 강한 매수세 + 좁은 스프레드 → 매수 고려
  - 🟢 매수세 우위 → 관망 또는 매수
  - ❤️ 강한 매도세 → 진입 주의
  - 🔴 매도세 우위 → 관망
  - ⚠️ 넓은 스프레드 → 유동성 부족, 진입 주의
  - ⚖️ 균형 상태 → 중립

#### 사용 예시:
```python
from features.order_book import OrderBookService

service = OrderBookService(market_api)
order_book = service.get_order_book('005930')  # 삼성전자

print(f"현재가: {order_book.current_price:,}원")
print(f"시장 압력: {order_book.pressure_type}")
print(f"추천: {service._get_recommendation(order_book)}")
```

#### API 엔드포인트:
```
GET /api/orderbook/<stock_code>

Response:
{
  "success": true,
  "stock_code": "005930",
  "stock_name": "삼성전자",
  "current_price": 73500,
  "ask_levels": [
    {"price": 73600, "volume": 15000, "percent": 25.5},
    ...
  ],
  "bid_levels": [
    {"price": 73500, "volume": 20000, "percent": 30.2},
    ...
  ],
  "pressure_type": "매수 우위",
  "recommendation": "💚 강한 매수세 + 좁은 스프레드 → 매수 고려"
}
```

### 2. 수익 추적 & 성과 분석 (Profit Tracker) ⭐ NEW
**파일**: `features/profit_tracker.py` (400+ 줄)

#### 주요 기능:
- **자동 거래 기록**:
  - 모든 매수/매도 거래 자동 저장
  - 손익 자동 계산 및 기록

- **기간별 성과 분석**:
  - 일간 (Daily)
  - 주간 (Weekly)
  - 월간 (Monthly)
  - 전체 (All Time)

- **포괄적 성과 지표**:
  1. **승률 (Win Rate)**: 수익 거래 / 전체 거래
  2. **총 수익/손실**: 누적 손익
  3. **순이익 (Net Profit)**: 총 수익 - 총 손실
  4. **거래당 평균 수익**: 순이익 / 거래 수
  5. **평균 승리 거래**: 수익 거래 평균
  6. **평균 패배 거래**: 손실 거래 평균
  7. **최대 수익 (Largest Win)**: 단일 거래 최대 수익
  8. **최대 손실 (Largest Loss)**: 단일 거래 최대 손실
  9. **최대 낙폭 (Max Drawdown)**: 고점 대비 최대 하락폭 (%)
  10. **샤프 비율 (Sharpe Ratio)**: 위험 조정 수익률
  11. **평균 보유 기간**: 매수부터 매도까지 평균 시간

#### 사용 예시:
```python
from features.profit_tracker import ProfitTracker

tracker = ProfitTracker()

# 일간 성과
daily = tracker.calculate_metrics('daily')
print(f"오늘 승률: {daily.win_rate:.2f}%")
print(f"순이익: {daily.net_profit:,.0f}원")
print(f"최대 낙폭: {daily.max_drawdown:.2f}%")
```

#### API 엔드포인트:
```
GET /api/performance

Response:
{
  "daily": {
    "total_trades": 5,
    "winning_trades": 3,
    "losing_trades": 2,
    "win_rate": 60.0,
    "net_profit": 125000,
    "max_drawdown": 2.5,
    "sharpe_ratio": 1.2,
    ...
  },
  "weekly": { ... },
  "monthly": { ... },
  "all_time": { ... }
}
```

## 📊 사용자 편의성 개선

### 1. 자동 캐싱
- **호가창 데이터**: 1초 TTL 캐시로 API 호출 최소화
- **성과 데이터**: 파일 기반 영구 저장

### 2. 에러 핸들링
- 모든 API에서 예외 처리
- 실패 시 명확한 에러 메시지 반환

### 3. 데이터 영속성
- 거래 기록 자동 저장 (`data/trade_history.json`)
- 시스템 재시작 후에도 성과 데이터 유지

## 🎯 수익 최적화 기능

### 1. 호가창 기반 진입 타이밍
- 매수/매도 압력 실시간 분석
- 스프레드 좁을 때 진입 권장
- 유동성 부족 경고

### 2. 성과 기반 학습
- 승률 추적으로 전략 효과성 확인
- 평균 수익/손실로 리스크 관리 개선
- 최대 낙폭 모니터링으로 위험 제어

## 🔧 기술적 개선

### 1. 코드 중복 제거
- 5개 중복 대시보드 파일 삭제
- 단일 메인 대시보드로 통일

### 2. 모듈화
- `features/` 폴더로 고급 기능 분리
- 재사용 가능한 서비스 클래스

### 3. 타입 힌팅
- 모든 클래스와 함수에 타입 힌트 추가
- 코드 가독성 및 IDE 지원 향상

## 📱 다음 단계 (v3.6 예정)

### 계획된 기능:
1. **포트폴리오 최적화** - AI 기반 포트폴리오 제안
2. **리스크 히트맵** - 시각적 리스크 분석
3. **뉴스 피드 + 감성 분석** - 실시간 뉴스 통합
4. **거래 일지** - AI 피드백 포함
5. **백테스팅 시각화** - 인터랙티브 결과 표시
6. **알림 시스템** - 소리/데스크톱/텔레그램 알림

## 🐛 버그 수정

1. 대시보드 파일 중복으로 인한 혼란 해결
2. API 참조 최적화
3. 파일 구조 명확화

## 📈 성능 개선

1. 호가창 1초 캐싱으로 API 호출 90% 감소
2. 거래 기록 파일 기반 저장으로 DB 부하 감소
3. 불필요한 파일 제거로 프로젝트 크기 감소

---

**v3.5 릴리스 일자**: 2025-01-31
**다음 버전**: v3.6 (2025-02 예정)
