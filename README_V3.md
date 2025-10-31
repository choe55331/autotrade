# 🍎 AutoTrade Pro v3.0 - Apple Edition

**최고 수준의 완성도와 미래지향적인 자동매매 시스템**

> 완벽한 Apple 스타일 디자인, 40+ 설정 가능한 기능, 포괄적인 기술적 분석

---

## 📱 주요 특징

### 🎨 Apple-Style 디자인
- **SF Pro Display 폰트** - Apple의 시스템 폰트 사용
- **미니멀리즘** - 깔끔하고 직관적인 인터페이스
- **다크/라이트 모드** - 원클릭 테마 전환
- **Glass-morphism** - 현대적인 블러 효과
- **부드러운 애니메이션** - 60fps 전환 효과
- **반응형 디자인** - 모바일/태블릿/데스크톱 최적화

### ⚙️ 40+ 설정 가능한 기능

모든 기능은 대시보드에서 **실시간으로 ON/OFF** 가능합니다.

#### UI & 대시보드 기능 (10가지)
1. ✅ **실시간 데이터 업데이트** - WebSocket 기반 즉시 반영
2. ✅ **반응형 웹 디자인** - 모든 디바이스 지원
3. ✅ **데이터 시각화** - Chart.js 기반 인터랙티브 차트
4. ✅ **컴포넌트 기반 UI** - 모듈화된 구조
5. ✅ **다크/라이트 모드** - 사용자 선호도 저장
6. ✅ **커스텀 레이아웃** - 드래그앤드롭 지원 (구현 예정)
7. ✅ **알림 시스템** - Toast 알림 + 중요 이벤트 통지
8. ✅ **로딩 상태 표시** - 스켈레톤 UI + 로딩 스피너
9. ✅ **일관된 디자인 시스템** - Apple HIG 준수
10. ✅ **직관적 네비게이션** - 사이드바 + 브레드크럼

#### 성능 최적화 기능 (10가지)
11. ⚡ **비동기 API 요청** - httpx/aiohttp 기반
12. ⚡ **WebSocket 최적화** - 압축 + 자동 재연결
13. ⚡ **DB 커넥션 풀링** - SQLAlchemy 풀 관리
14. ⚡ **Redis 캐싱** - 자주 조회되는 데이터 캐시
15. ⚡ **백그라운드 작업 큐** - RQ/Celery 기반 비동기 작업
16. ⚡ **AI 모델 최적화** - Gemini 2.0 Flash 사용
17. ⚡ **데이터 직렬화** - MessagePack 고속 직렬화
18. ⚡ **쿼리 최적화** - Eager loading + 쿼리 캐시
19. ⚡ **정적 파일 압축** - Gzip + 파일 최소화
20. ⚡ **성능 프로파일링** - 병목 지점 자동 감지

#### 기술적 지표 (9가지)
21. 📊 **SMA** - Simple Moving Average (5, 20, 60, 120일)
22. 📊 **EMA** - Exponential Moving Average (12, 26일)
23. 📊 **RSI** - Relative Strength Index (14일)
24. 📊 **MACD** - Moving Average Convergence Divergence
25. 📊 **Stochastic** - Stochastic Oscillator (%K, %D)
26. 📊 **Bollinger Bands** - 변동성 밴드 (20일, 2σ)
27. 📊 **ATR** - Average True Range (14일)
28. 📊 **Volume SMA** - 거래량 이동평균 (20일)
29. 📊 **OBV** - On-Balance Volume

#### 매매 전략 (20가지)
30. 🎯 **동적 손절/익절** - ATR 기반 자동 조정
31. 🎯 **트레일링 스톱** - 수익 보호 자동화
32. 🎯 **거래량 필터** - 유동성 최소 기준 설정
33. 🎯 **시장 상황 분석** - 상승장/하락장/횡보장 감지
34. 🎯 **포트폴리오 리밸런싱** - 주기적 비중 조정
35. 🎯 **변동성 돌파 전략** - Larry Williams 스타일
36. 🎯 **뉴스 감성 분석** - AI 기반 뉴스 분석 (구현 예정)
37. 🎯 **AI 신뢰도 필터링** - 높은 신뢰도만 매매
38. 🎯 **VIX 필터** - 공포지수 기반 리스크 관리
39. 🎯 **섹터 로테이션** - 강세 섹터 자동 선택 (구현 예정)
40. 🎯 **수급 분석** - 기관/외국인 순매수 추적 (구현 예정)
41. 🎯 **Kelly Criterion** - 최적 포지션 사이즈 계산 (구현 예정)
42. 🎯 **멀티 타임프레임 분석** - 일봉/시간봉/분봉 동시 분석
43. 🎯 **백테스팅 강화** - 슬리피지 + 수수료 반영
44. 🎯 **파라미터 최적화** - Bayesian Optimization (구현 예정)
45. 🎯 **공매도 데이터** - 공매도 비중 추적 (구현 예정)
46. 🎯 **스캘핑 전략** - 호가창 기반 초단타 (구현 예정)
47. 🎯 **페어 트레이딩** - 통계적 차익거래 (구현 예정)
48. 🎯 **ML 예측 모델** - LSTM/XGBoost 기반 (구현 예정)
49. 🎯 **리스크 관리** - VaR, 상관계수, 섹터 집중도
50. 🎯 **포지션 관리** - 분할 진입/청산

---

## 📁 프로젝트 구조

```
autotrade/
├── 📋 config/                      # 설정 파일
│   ├── config.yaml                 # 기본 설정 (v2.0)
│   ├── features_config.yaml        # 기능 설정 (v3.0) ⭐ NEW
│   ├── config_manager.py           # 설정 관리자
│   └── settings.py                 # 시스템 설정
│
├── 📊 indicators/                  # 기술적 지표 ⭐ NEW
│   ├── __init__.py
│   ├── trend.py                    # SMA, EMA, 추세 분석
│   ├── momentum.py                 # RSI, MACD, Stochastic
│   ├── volatility.py               # Bollinger Bands, ATR
│   └── volume.py                   # Volume SMA, OBV
│
├── 🎨 dashboard/                   # 웹 대시보드
│   ├── __init__.py
│   ├── app_apple.py                # Apple-Style Dashboard ⭐ NEW
│   ├── dashboard_ultra.py          # Ultra Dashboard (v2.0)
│   └── templates/
│       └── dashboard_apple.html    # Apple UI Template ⭐ NEW
│
├── 🤖 ai/                          # AI 분석기
│   ├── gemini_analyzer.py          # Gemini AI
│   ├── claude_analyzer.py          # Claude AI
│   ├── gpt4_analyzer.py            # GPT-4
│   └── ensemble_analyzer.py        # 앙상블 분석
│
├── 📈 strategy/                    # 매매 전략
│   ├── momentum_strategy.py        # 모멘텀 전략
│   ├── scoring_system.py           # 10-기준 스코어링
│   ├── risk_manager.py             # 리스크 관리
│   └── dynamic_risk_manager.py     # 동적 리스크 관리
│
├── 🔍 research/                    # 시장 조사
│   ├── scanner_pipeline.py         # 3단계 스캐닝
│   ├── theme_analyzer.py           # 테마 분석
│   └── market_analyzer.py          # 시장 분석
│
├── 🔌 api/                         # Kiwoom API
│   ├── market.py                   # 시장 데이터
│   ├── order.py                    # 주문
│   ├── account.py                  # 계좌
│   └── realtime.py                 # 실시간 데이터
│
├── 💾 database/                    # 데이터베이스
│   ├── models.py                   # SQLAlchemy 모델
│   └── repositories.py             # 데이터 접근 계층
│
├── 📂 data/                        # 런타임 데이터
│   ├── database/
│   │   └── autotrade.db            # SQLite DB
│   ├── state/
│   │   ├── control.json            # 제어 상태
│   │   └── strategy_state.json     # 전략 상태
│   └── cache/                      # 캐시 데이터
│
├── 📝 logs/                        # 로그 파일
├── 🧪 tests/                       # 유닛 테스트
└── 📚 docs/                        # 문서

```

---

## 🚀 빠른 시작

### 1️⃣ 의존성 설치

```bash
# 기본 패키지 설치
pip install -r requirements.txt

# 선택적: Redis 설치 (캐싱 기능 사용 시)
# Windows: https://github.com/microsoftarchive/redis/releases
# Mac: brew install redis
# Linux: sudo apt-get install redis-server
```

### 2️⃣ 설정 파일 구성

```bash
# .env 파일 생성
cp .env.example .env

# API 키 설정
# GEMINI_API_KEY=your_gemini_api_key_here
```

### 3️⃣ 시스템 실행

```bash
# 메인 프로그램 실행
python main.py

# 대시보드만 실행 (테스트용)
python dashboard/app_apple.py
```

### 4️⃣ 대시보드 접속

브라우저에서 **http://localhost:5000** 접속

---

## 🎨 대시보드 사용법

### 메인 화면

#### 1. 헤더
- **로고** - AutoTrade Pro v3.0
- **Trading 토글** - 매매 시작/중지
- **설정 버튼** - 40+ 기능 설정 패널
- **테마 토글** - 다크/라이트 모드 전환

#### 2. 통계 카드 (4개)
- **Total Assets** - 총 자산 + 수익률
- **Cash** - 보유 현금
- **Profit/Loss** - 실현/미실현 손익
- **Positions** - 보유 종목 수

#### 3. 포트폴리오 차트
- **실시간 그래프** - Chart.js 기반 라인 차트
- **24시간 데이터** - 포트폴리오 가치 변화 추적
- **인터랙티브** - 호버 시 상세 정보 표시

#### 4. 3단계 스캐닝 파이프라인
- **⚡ Fast Scan** - 10초마다 50종목 스캔
- **🔬 Deep Scan** - 1분마다 20종목 심층 분석
- **🤖 AI Scan** - 5분마다 5종목 AI 분석

#### 5. Top Candidates
- **AI 선정 종목** - 최고 점수 종목 표시
- **신뢰도** - AI 신뢰도 점수
- **매수 신호** - BUY/HOLD/SELL 표시

#### 6. Recent Activity
- **실시간 활동 로그** - 매매/스캔/시스템 이벤트
- **WebSocket 기반** - 즉시 업데이트
- **아이콘 분류** - 시각적 구분

#### 7. Current Positions
- **보유 종목 테이블** - 실시간 손익 표시
- **평균 단가** - 매수 평균 가격
- **수익률** - 퍼센트 및 금액

### 설정 패널

설정 버튼(<i class="fas fa-sliders-h"></i>)을 클릭하면 모달 창이 열립니다.

#### UI & Dashboard Features
```
✓ 실시간 데이터 업데이트
✓ 반응형 웹 디자인
✓ 데이터 시각화
✓ 다크/라이트 모드
... (10개 기능)
```

#### Performance Optimization
```
✓ 비동기 API 요청
✓ WebSocket 최적화
✓ Redis 캐싱
✓ 백그라운드 작업 큐
... (10개 기능)
```

#### Technical Indicators
```
✓ SMA (5, 20, 60, 120일)
✓ RSI (14일)
✓ MACD
✓ Bollinger Bands
... (9개 지표)
```

#### Trading Strategies
```
✓ 동적 손절/익절
✓ 트레일링 스톱
✓ 거래량 필터
✓ 시장 상황 분석
... (20개 전략)
```

각 기능 옆의 **토글 스위치**로 ON/OFF 가능합니다.
변경 사항은 즉시 `config/features_config.yaml`에 저장됩니다.

---

## 📊 기술적 지표 사용법

### 코드 예제

```python
from indicators import rsi, macd, bollinger_bands, atr
from indicators import calculate_momentum_score, calculate_volatility_score
import pandas as pd

# 데이터 준비 (예: 종가 데이터)
prices = pd.Series([100, 102, 101, 105, 107, 106, 108, 110, 109, 112])
high = pd.Series([101, 103, 102, 106, 108, 107, 109, 111, 110, 113])
low = pd.Series([99, 101, 100, 104, 106, 105, 107, 109, 108, 111])
volume = pd.Series([1000, 1200, 900, 1500, 1800, 1100, 1400, 1600, 1300, 1700])

# RSI 계산
rsi_values = rsi(prices, period=14)
print(f"Current RSI: {rsi_values.iloc[-1]:.2f}")

# MACD 계산
macd_line, signal_line, histogram = macd(prices)
print(f"MACD: {macd_line.iloc[-1]:.2f}")
print(f"Signal: {signal_line.iloc[-1]:.2f}")
print(f"Histogram: {histogram.iloc[-1]:.2f}")

# Bollinger Bands 계산
upper, middle, lower = bollinger_bands(prices, period=20, std_dev=2)
print(f"Upper Band: {upper.iloc[-1]:.2f}")
print(f"Middle Band: {middle.iloc[-1]:.2f}")
print(f"Lower Band: {lower.iloc[-1]:.2f}")

# ATR 계산 (변동성)
atr_values = atr(high, low, prices, period=14)
print(f"Current ATR: {atr_values.iloc[-1]:.2f}")

# 종합 모멘텀 점수
momentum = calculate_momentum_score(prices, high, low)
print(f"Momentum Signal: {momentum['signal']}")  # BUY/SELL/NEUTRAL
print(f"Momentum Score: {momentum['score']:.2f}")  # 0-100
print(f"Strength: {momentum['strength']}")  # weak/moderate/strong

# 종합 변동성 점수
volatility = calculate_volatility_score(prices, high, low)
print(f"Volatility Level: {volatility['level']}")  # low/normal/high/very_high
print(f"Volatility Score: {volatility['score']:.2f}")
```

### 동적 손절/익절 계산

```python
from indicators.volatility import calculate_dynamic_stop_loss, calculate_dynamic_take_profit

# 매수 진입
entry_price = 50000  # 50,000원
current_atr = 1500   # ATR 1,500원

# 동적 손절가 계산
stop_loss = calculate_dynamic_stop_loss(
    entry_price=entry_price,
    atr_value=current_atr,
    direction='long',
    atr_multiplier=2.0,  # ATR의 2배
    min_percent=3.0,     # 최소 3%
    max_percent=10.0     # 최대 10%
)
print(f"Stop Loss: {stop_loss:,.0f}원 ({((stop_loss/entry_price - 1) * 100):.2f}%)")

# 동적 익절가 계산
take_profit = calculate_dynamic_take_profit(
    entry_price=entry_price,
    atr_value=current_atr,
    direction='long',
    atr_multiplier=3.0,  # ATR의 3배
    min_percent=5.0,     # 최소 5%
    max_percent=20.0     # 최대 20%
)
print(f"Take Profit: {take_profit:,.0f}원 ({((take_profit/entry_price - 1) * 100):.2f}%)")
```

---

## ⚙️ 설정 파일 설명

### `config/features_config.yaml`

모든 기능의 ON/OFF를 제어하는 중앙 설정 파일입니다.

```yaml
# UI 기능
ui:
  realtime_updates:
    enabled: true
    update_interval: 2  # 2초마다 업데이트

  theme:
    default: "dark"  # dark, light, auto

  notifications:
    enabled: true
    types:
      toast: true
      sound: false

# 성능 최적화
performance:
  async_api:
    enabled: true
    max_concurrent: 10

  caching:
    enabled: true
    backend: "redis"  # redis, memory
    ttl:
      stock_info: 3600  # 1시간
      realtime_data: 5  # 5초

# 기술적 지표
trading:
  technical_indicators:
    enabled: true
    indicators:
      rsi:
        enabled: true
        period: 14
        overbought: 70
        oversold: 30

      macd:
        enabled: true
        fast_period: 12
        slow_period: 26
        signal_period: 9

      bollinger_bands:
        enabled: true
        period: 20
        std_dev: 2

  # 동적 손절/익절
  dynamic_stops:
    enabled: true
    method: "atr"  # atr, percentage, fixed
    stop_loss:
      atr_multiplier: 2.0
      min_percent: 3.0
      max_percent: 10.0

  # 거래량 필터
  volume_filters:
    enabled: true
    min_volume: 100000  # 최소 일 거래량
    min_value: 1000000000  # 최소 일 거래대금 (10억)
```

---

## 🔧 고급 기능

### 1. Redis 캐싱 활성화

```bash
# Redis 서버 시작
redis-server

# features_config.yaml에서 캐싱 활성화
performance:
  caching:
    enabled: true
    backend: "redis"
```

### 2. 백그라운드 작업 큐

```bash
# RQ Worker 시작
rq worker --url redis://localhost:6379/1

# features_config.yaml에서 작업 큐 활성화
performance:
  task_queue:
    enabled: true
    backend: "rq"
```

### 3. 비동기 API 사용

```python
# features_config.yaml에서 활성화
performance:
  async_api:
    enabled: true
    library: "httpx"  # httpx 또는 aiohttp
```

---

## 📈 매매 전략 커스터마이징

### 전략 1: 동적 리스크 관리

```yaml
trading:
  dynamic_stops:
    enabled: true
    method: "atr"
    stop_loss:
      atr_multiplier: 2.0  # 공격적: 1.5, 보수적: 2.5
      min_percent: 3.0
      max_percent: 10.0
    take_profit:
      atr_multiplier: 3.0  # 공격적: 2.0, 보수적: 4.0
```

### 전략 2: 모멘텀 + 변동성 조합

```yaml
trading:
  technical_indicators:
    indicators:
      rsi:
        enabled: true
        overbought: 70  # 더 공격적: 80, 더 보수적: 60
        oversold: 30    # 더 공격적: 20, 더 보수적: 40

      bollinger_bands:
        enabled: true
        std_dev: 2  # 더 넓은 밴드: 2.5, 더 좁은 밴드: 1.5
```

### 전략 3: 거래량 확인 필수화

```yaml
trading:
  volume_filters:
    enabled: true
    min_volume: 100000  # 더 높은 유동성: 500000
    min_value: 1000000000  # 10억 이상만
    min_liquidity_ratio: 0.1  # 평균 거래량 대비 최소 비율
```

---

## 🐛 문제 해결

### 문제 1: Dashboard가 열리지 않음

```bash
# 포트 충돌 확인
netstat -ano | findstr :5000

# 다른 포트로 실행
python dashboard/app_apple.py --port 5001
```

### 문제 2: Redis 연결 오류

```bash
# Redis 서버 상태 확인
redis-cli ping
# 응답: PONG

# features_config.yaml에서 캐싱 비활성화
performance:
  caching:
    enabled: false
```

### 문제 3: 패키지 설치 오류 (Windows)

```bash
# Visual C++ Build Tools 설치
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 또는 Anaconda 사용
conda install pandas numpy scikit-learn xgboost
```

### 문제 4: 테마가 적용되지 않음

```
1. 브라우저 캐시 삭제 (Ctrl+Shift+Delete)
2. 하드 리프레시 (Ctrl+F5)
3. 시크릿 모드에서 테스트
```

---

## 🎯 로드맵

### ✅ Phase 1: 기본 기능 (v3.0) - 완료
- [x] Apple-style 대시보드
- [x] 다크/라이트 모드
- [x] 40+ 기능 설정 시스템
- [x] 기술적 지표 9종
- [x] 동적 손절/익절
- [x] 실시간 데이터 업데이트

### 🚧 Phase 2: 고급 기능 (v3.1) - 진행 중
- [ ] 뉴스 감성 분석
- [ ] 섹터 로테이션
- [ ] 수급 분석 (기관/외국인)
- [ ] Kelly Criterion
- [ ] 파라미터 최적화 (Bayesian)

### 📅 Phase 3: ML/AI (v3.2) - 계획
- [ ] LSTM 가격 예측
- [ ] XGBoost 매매 신호
- [ ] 강화학습 (RL) 전략
- [ ] 앙상블 AI 모델

### 🔮 Phase 4: 프로 기능 (v3.3) - 계획
- [ ] 멀티 브로커 지원
- [ ] 알고리즘 주문 (TWAP, VWAP)
- [ ] 고빈도 거래 (HFT) 모드
- [ ] 클라우드 배포 (AWS/GCP)

---

## 📞 지원

### 문서
- [설치 가이드](./INSTALL_WINDOWS.md)
- [빠른 시작](./QUICK_START.md)
- [API 문서](./docs/API.md)

### 커뮤니티
- GitHub Issues: [리포트 문제](https://github.com/yourusername/autotrade/issues)
- Discord: [커뮤니티 참여](https://discord.gg/autotrade)

---

## 📄 라이센스

MIT License

---

## 🙏 감사의 말

이 프로젝트는 다음 오픈소스 프로젝트들의 도움을 받았습니다:

- [pll2050/kiwoom_trading_claude](https://github.com/pll2050/kiwoom_trading_claude) - 시스템 구조 참고
- [Jaewook-github/stock-trading-system](https://github.com/Jaewook-github/stock-trading-system-Kiwoom-rest-api-AI-coding-test) - 대시보드 디자인 영감

---

**⚠️ 면책 조항**

이 소프트웨어는 교육 및 연구 목적으로 제공됩니다. 실제 투자 시 발생하는 손실에 대해 개발자는 책임지지 않습니다. 자동매매는 높은 리스크를 동반하므로 충분한 테스트 후 사용하시기 바랍니다.

---

Made with 🍎 by AutoTrade Pro Team
