# AutoTrade Pro v2.0 - 차세대 자동매매 시스템

## 🎯 프로젝트 개요

AutoTrade Pro v2.0은 기존 autotrade 시스템을 대폭 업그레이드한 차세대 자동매매 시스템입니다.
두 개의 우수한 오픈소스 프로젝트의 장점을 통합하여 완성도 높고 최적화된 시스템으로 재탄생했습니다.

### 통합된 프로젝트
- **pll2050/kiwoom_trading_claude**: 안정적인 구조와 3단계 스캐닝 파이프라인
- **Jaewook-github/stock-trading-system**: 현대적인 대시보드 UI/UX 디자인

## ✨ 주요 개선 사항

### 1. YAML 기반 설정 관리 시스템
- **파일**: `config/config.yaml`, `config/config_manager.py`
- **장점**:
  - 코드 수정 없이 실시간 설정 변경 가능
  - 환경 변수 자동 치환 (${VAR_NAME})
  - 모든 설정을 한 곳에서 관리
  - 검증 및 기본값 지원

```yaml
# config/config.yaml 예시
position:
  max_open_positions: 5
  risk_per_trade_ratio: 0.20

scanning:
  fast_scan:
    enabled: true
    interval: 10
    max_candidates: 50
```

### 2. Loguru 기반 고급 로깅 시스템
- **파일**: `utils/logger_new.py`
- **기능**:
  - 자동 로그 로테이션 (매일 자정)
  - 로그 압축 (zip)
  - 컬러 출력 지원
  - 에러 전용 로그 파일 분리
  - 스택 트레이스 자동 기록

```python
from utils.logger_new import get_logger
logger = get_logger()

logger.info("정보 메시지")
logger.error("에러 발생", exc_info=True)
```

### 3. 3단계 스캐닝 파이프라인
- **파일**: `research/scanner_pipeline.py`
- **구조**:

```
Fast Scan (10초) → Deep Scan (1분) → AI Scan (5분)
  50종목            20종목            5종목
```

#### Fast Scan (10초 주기)
- 거래량, 가격, 등락률 기본 필터링
- 거래대금 기준 정렬
- **목표**: 50종목 선정

#### Deep Scan (1분 주기)
- 기관/외국인 매매 흐름 분석
- 호가 강도 분석
- **목표**: 20종목 선정

#### AI Scan (5분 주기)
- AI 분석을 통한 최종 매수 추천
- 신뢰도 기반 게이팅
- **목표**: 5종목 선정

### 4. 10가지 기준 스코어링 시스템 (440점 만점)
- **파일**: `strategy/scoring_system.py`

| 기준 | 배점 | 설명 |
|------|------|------|
| 1. 거래량 급증 | 60점 | 평균 대비 거래량 비율 |
| 2. 가격 모멘텀 | 60점 | 등락률 기반 모멘텀 |
| 3. 기관 매수세 | 60점 | 기관/외국인 순매수 |
| 4. 매수 호가 강도 | 40점 | 매수/매도 호가 비율 |
| 5. 체결 강도 | 40점 | 체결 강도 지표 |
| 6. 주요 증권사 활동 | 40점 | 상위 증권사 매수 참여 |
| 7. 프로그램 매매 | 40점 | 프로그램 순매수 |
| 8. 기술적 지표 | 40점 | RSI, MACD, 이동평균 |
| 9. 테마/뉴스 | 40점 | 테마 소속, 긍정 뉴스 |
| 10. 변동성 패턴 | 20점 | 적정 변동성 범위 |

**등급 체계**:
- S등급: 90% 이상 (396점+)
- A등급: 80-90% (352-395점)
- B등급: 70-80% (308-351점)
- C등급: 60-70% (264-307점)
- D등급: 50-60% (220-263점)
- F등급: 50% 미만 (220점 미만)

### 5. 동적 리스크 관리 모드 시스템
- **파일**: `strategy/dynamic_risk_manager.py`
- **기능**: 성과에 따라 자동으로 리스크 모드 전환

#### 4가지 리스크 모드

| 모드 | 수익률 조건 | 최대 포지션 | 거래당 리스크 | 목표 수익 | 손절 |
|------|-------------|-------------|---------------|-----------|------|
| 🔥 Aggressive | +5% 이상 | 12개 | 25% | +15% | -7% |
| ⚖️ Normal | -5% ~ +5% | 10개 | 20% | +10% | -5% |
| 🛡️ Conservative | -10% ~ -5% | 7개 | 15% | +8% | -4% |
| 🔒 Very Conservative | -10% 이하 | 5개 | 10% | +5% | -3% |

**자동 전환 로직**:
```python
수익률 +5% 이상 → Aggressive 모드 (공격적)
수익률 -5% ~ +5% → Normal 모드 (균형)
수익률 -10% ~ -5% → Conservative 모드 (방어적)
수익률 -10% 이하 → Very Conservative 모드 (극도 보수적)
```

### 6. 데이터베이스 백엔드 (SQLite)
- **파일**: `database/models.py`
- **테이블**:
  - `trades`: 모든 거래 기록
  - `positions`: 현재 보유 포지션
  - `portfolio_snapshots`: 일일 포트폴리오 스냅샷
  - `scan_results`: 스캔 결과 기록
  - `system_logs`: 시스템 로그

**장점**:
- 영구 저장 (JSON 파일 → 데이터베이스)
- 빠른 쿼리 및 분석
- 트랜잭션 지원
- 확장 가능 (PostgreSQL 지원 준비됨)

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                   Web Dashboard (Flask)                     │
│         (카드 기반 UI, 실시간 WebSocket 업데이트)              │
└────────────────────────┬───────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────┐
│                   TradingBot (main.py)                      │
│               (메인 오케스트레이터 & 이벤트 루프)               │
├────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │       3단계 스캐닝 파이프라인                          │   │
│  │   Fast (10s) → Deep (1m) → AI (5m)                  │   │
│  │     50종목      20종목      5종목                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         10가지 기준 스코어링 (440점 만점)              │   │
│  │   거래량 + 모멘텀 + 기관매수 + 호가강도 + ...          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          동적 리스크 관리 (4단계 모드)                 │   │
│  │   Aggressive ↔ Normal ↔ Conservative ↔ Very Cons.   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              AI 분석 (다중 모델 지원)                  │   │
│  │    Gemini / Claude / GPT-4 / Ensemble               │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────┬───────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────┐
│               데이터베이스 (SQLite/PostgreSQL)               │
│     Trades | Positions | Snapshots | Scans | Logs          │
└─────────────────────────────────────────────────────────────┘
```

## 📁 디렉토리 구조

```
autotrade/
├── config/
│   ├── config.yaml                    # 통합 YAML 설정 (신규)
│   ├── config_manager.py              # 설정 관리자 (신규)
│   ├── credentials.py
│   ├── trading_params.py
│   └── settings.py
│
├── utils/
│   ├── logger_new.py                  # Loguru 로거 (신규)
│   └── logger.py                      # 기존 로거 (호환성)
│
├── research/
│   ├── scanner_pipeline.py            # 3단계 스캐닝 (신규)
│   ├── screener.py
│   ├── analyzer.py
│   └── data_fetcher.py
│
├── strategy/
│   ├── scoring_system.py              # 10가지 스코어링 (신규)
│   ├── dynamic_risk_manager.py        # 동적 리스크 관리 (신규)
│   ├── momentum_strategy.py
│   ├── portfolio_manager.py
│   └── risk_manager.py
│
├── database/
│   ├── __init__.py                    # 데이터베이스 패키지 (신규)
│   └── models.py                      # SQLAlchemy 모델 (신규)
│
├── ai/
│   ├── gemini_analyzer.py
│   ├── claude_analyzer.py
│   ├── gpt4_analyzer.py
│   └── ensemble_analyzer.py
│
├── api/
│   ├── account.py
│   ├── market.py
│   ├── order.py
│   └── realtime.py
│
├── dashboard/
│   ├── dashboard.py
│   ├── dashboard_pro.py               # 업그레이드 예정
│   └── templates/
│
├── core/
│   ├── rest_client.py
│   └── websocket_client.py
│
├── main.py                            # 메인 실행 파일
├── requirements.txt                   # 업데이트됨
├── README.md                          # 기존 README
└── README_V2.md                       # 이 파일 (신규)
```

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

**주요 신규 패키지**:
- PyYAML==6.0.1 (설정 관리)
- loguru==0.7.2 (로깅)
- SQLAlchemy==2.0.23 (데이터베이스)
- alembic==1.13.1 (DB 마이그레이션)
- ta==0.11.0 (기술적 분석)
- aiohttp==3.9.1 (비동기 HTTP)
- flask-socketio==5.3.5 (실시간 통신)

### 2. 설정 파일 구성

#### `config/config.yaml` 편집
```yaml
# 키움 API 설정
api:
  kiwoom:
    base_url: "https://openapi.koreainvestment.com:9443"

# AI 설정 (환경 변수 사용 권장)
ai:
  gemini:
    enabled: true
    # API 키는 환경 변수로 설정: GOOGLE_API_KEY

# 트레이딩 파라미터
position:
  max_open_positions: 10
  risk_per_trade_ratio: 0.20
```

#### 환경 변수 설정 (`.env` 파일)
```bash
# API 키
GOOGLE_API_KEY=your_gemini_api_key_here
ANTHROPIC_API_KEY=your_claude_api_key_here
OPENAI_API_KEY=your_gpt4_api_key_here

# 키움 API
KIWOOM_APP_KEY=your_kiwoom_app_key
KIWOOM_APP_SECRET=your_kiwoom_app_secret
KIWOOM_ACCOUNT_NO=your_account_number
```

### 3. 시스템 실행

```bash
python main.py
```

### 4. 대시보드 접속
브라우저에서 `http://localhost:5000` 접속

## 🎨 새로운 기능 사용법

### 1. YAML 설정 변경

```python
from config.config_manager import get_config, save_config

# 설정 가져오기
config = get_config()

# 설정 변경
config.set('position.max_open_positions', 12)

# 저장 (선택사항)
save_config()
```

### 2. 스캐닝 파이프라인 사용

```python
from research.scanner_pipeline import ScannerPipeline

# 초기화
pipeline = ScannerPipeline(
    market_api=market_api,
    screener=screener,
    ai_analyzer=ai_analyzer
)

# 전체 파이프라인 실행
final_candidates = pipeline.run_full_pipeline()

# 개별 실행
fast_results = pipeline.run_fast_scan()      # Fast Scan만
deep_results = pipeline.run_deep_scan()      # Deep Scan만
ai_results = pipeline.run_ai_scan()          # AI Scan만
```

### 3. 스코어링 시스템 사용

```python
from strategy.scoring_system import ScoringSystem

# 초기화
scorer = ScoringSystem(market_api=market_api)

# 점수 계산
stock_data = {
    'code': '005930',
    'name': '삼성전자',
    'price': 75000,
    'volume': 1000000,
    'rate': 3.5,
    # ... 기타 데이터
}

result = scorer.calculate_score(stock_data)

print(f"총점: {result.total_score}/440")
print(f"퍼센티지: {result.percentage:.1f}%")
print(f"등급: {scorer.get_grade(result.total_score)}")
```

### 4. 동적 리스크 관리 사용

```python
from strategy.dynamic_risk_manager import DynamicRiskManager

# 초기화 (초기 자본금 1천만원)
risk_mgr = DynamicRiskManager(initial_capital=10_000_000)

# 자본금 업데이트 (자동으로 모드 재평가)
risk_mgr.update_capital(current_capital=10_500_000)  # +5% → Aggressive 모드

# 현재 설정 확인
config = risk_mgr.get_current_mode_config()
print(f"최대 포지션: {config.max_open_positions}")
print(f"거래당 리스크: {config.risk_per_trade_ratio*100}%")

# 포지션 진입 가능 여부
can_open = risk_mgr.should_open_position(current_positions=5)

# 포지션 크기 계산
quantity = risk_mgr.calculate_position_size(
    stock_price=75000,
    available_cash=2_000_000
)

# 청산 임계값
thresholds = risk_mgr.get_exit_thresholds(entry_price=75000)
print(f"목표가: {thresholds['take_profit']:,}원")
print(f"손절가: {thresholds['stop_loss']:,}원")
```

### 5. 데이터베이스 사용

```python
from database import get_db_session, Trade, Position

# 세션 가져오기
session = get_db_session()

# 거래 기록 저장
trade = Trade(
    stock_code='005930',
    stock_name='삼성전자',
    action='buy',
    quantity=10,
    price=75000,
    total_amount=750000,
    ai_score=8.5,
    scoring_total=380
)
session.add(trade)
session.commit()

# 조회
recent_trades = session.query(Trade).\
    filter(Trade.stock_code == '005930').\
    order_by(Trade.timestamp.desc()).\
    limit(10).\
    all()

for trade in recent_trades:
    print(f"{trade.timestamp}: {trade.action} {trade.quantity}주 @ {trade.price:,}원")

session.close()
```

## 📊 성능 최적화

### 1. 비동기 처리 준비
- aiohttp 패키지 추가
- 향후 비동기 API 호출 지원

### 2. 데이터베이스 인덱싱
- 주요 조회 필드에 인덱스 설정
- 빠른 쿼리 성능

### 3. 캐싱
- 스캔 결과 캐싱
- API 호출 최소화

## 🔧 설정 파일 구조

### `config/config.yaml` 주요 섹션

```yaml
system:          # 시스템 정보
  name: "AutoTrade Pro"
  version: "2.0.0"

logging:         # 로깅 설정
  level: "INFO"
  rotation: "00:00"

database:        # 데이터베이스 설정
  type: "sqlite"
  path: "data/autotrade.db"

api:             # API 설정
  kiwoom:
    rest_call_interval: 0.3

position:        # 포지션 관리
  max_open_positions: 5
  risk_per_trade_ratio: 0.20

profit_loss:     # 손익 관리
  take_profit_ratio: 0.10
  stop_loss_ratio: -0.05

scanning:        # 스캐닝 설정
  fast_scan:
    enabled: true
    interval: 10
    max_candidates: 50
  deep_scan:
    enabled: true
    interval: 60
    max_candidates: 20
  ai_scan:
    enabled: true
    interval: 300
    max_candidates: 5

scoring:         # 스코어링 기준
  total_max_score: 440
  criteria:
    volume_surge:
      weight: 60
    price_momentum:
      weight: 60
    # ... (10가지 기준)

risk_management: # 리스크 관리 모드
  aggressive:
    max_open_positions: 12
  normal:
    max_open_positions: 10
  conservative:
    max_open_positions: 7
  very_conservative:
    max_open_positions: 5

ai:              # AI 설정
  gemini:
    enabled: true
    model: "gemini-2.0-flash-exp"
  claude:
    enabled: false
  ensemble:
    enabled: false

dashboard:       # 대시보드 설정
  enabled: true
  port: 5000
  websocket:
    enabled: true

notification:    # 알림 설정
  telegram:
    enabled: false
```

## 🧪 테스트

### 기본 테스트
```bash
# 기존 테스트
python test_trading.py
python test_account_api.py

# TODO: 신규 테스트 추가 예정
# python test_scanner_pipeline.py
# python test_scoring_system.py
# python test_dynamic_risk.py
```

## 📈 모니터링

### 로그 확인
```bash
# 메인 로그
tail -f logs/bot.log

# 에러 로그
tail -f logs/error.log

# 특정 날짜 로그
ls -la logs/
```

### 데이터베이스 조회
```bash
# SQLite CLI
sqlite3 data/autotrade.db

# 거래 내역
SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10;

# 현재 포지션
SELECT * FROM positions WHERE is_active = 1;

# 포트폴리오 스냅샷
SELECT * FROM portfolio_snapshots ORDER BY timestamp DESC LIMIT 5;
```

## 🔐 보안

### 환경 변수 사용
- API 키는 절대 코드에 하드코딩하지 않기
- `.env` 파일 사용 (`.gitignore`에 추가됨)

### 데이터베이스 보안
- 민감한 정보는 암호화 권장
- 정기적인 백업

## 🌟 향후 개선 계획

### Phase 1 (완료)
- ✅ YAML 기반 설정 시스템
- ✅ Loguru 로깅 시스템
- ✅ 3단계 스캐닝 파이프라인
- ✅ 10가지 기준 스코어링
- ✅ 동적 리스크 관리
- ✅ 데이터베이스 백엔드

### Phase 2 (계획)
- ⏳ 현대화된 대시보드 UI (카드 기반, 반응형)
- ⏳ WebSocket 실시간 업데이트
- ⏳ 백테스팅 고도화
- ⏳ 성능 분석 대시보드

### Phase 3 (장기)
- 📋 모바일 앱 개발
- 📋 PostgreSQL 지원
- 📋 분산 처리 (다중 계좌)
- 📋 머신러닝 강화

## 🐛 문제 해결

### 일반적인 이슈

#### 1. "Module not found" 에러
```bash
pip install -r requirements.txt
```

#### 2. 데이터베이스 초기화 실패
```bash
# 데이터베이스 재생성
rm data/autotrade.db
python main.py
```

#### 3. 설정 파일 에러
```bash
# YAML 구문 검증
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
```

## 📞 지원

### 문서
- 메인 README: `README.md`
- 이 문서: `README_V2.md`

### 로그
- 모든 작업은 상세하게 로그에 기록됨
- `logs/` 디렉토리 확인

## 📄 라이선스

[기존 라이선스 참조]

## 🙏 감사의 말

이 프로젝트는 다음 오픈소스 프로젝트의 아이디어와 구조를 참고했습니다:
- **pll2050/kiwoom_trading_claude**: 3단계 스캐닝 파이프라인, 안정적인 아키텍처
- **Jaewook-github/stock-trading-system**: 대시보드 UI/UX 디자인

---

**AutoTrade Pro v2.0** - 완성도 높고 최적화된 차세대 자동매매 시스템 🚀
