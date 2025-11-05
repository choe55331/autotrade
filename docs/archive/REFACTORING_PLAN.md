# AutoTrade 프로젝트 리팩토링 계획

## 📊 현재 상황 분석

### 프로젝트 규모
- **총 Python 파일**: 186개
- **전체 크기**: 9.2MB
- **가장 큰 파일들**:
  1. `dashboard/app_apple.py` - **3,249줄** ❌ (분할 필요)
  2. `api/market.py` - 1,899줄 ⚠️
  3. `main.py` - **1,617줄** ❌ (분할 필요)

### 주요 문제점

#### 1. 과도한 파일 크기
- ❌ `dashboard/app_apple.py` (3,249줄)
  - 50개 이상의 API 엔드포인트
  - WebSocket, SocketIO 처리
  - 다양한 기능이 한 파일에 집중
  - **분할 필요**: routes, websocket, api 등으로 분리

- ❌ `main.py` (1,617줄)
  - TradingBotV2 클래스가 너무 큼
  - 매매 로직, 스캐닝, AI 분석 등 모든 기능 포함
  - **분할 필요**: 기능별 모듈로 분리

#### 2. 불명확한 폴더 구조
```
tests/
├── manual_tests/     # 수동 테스트
├── archived/         # 아카이브된 테스트
└── *.py             # 자동화된 테스트
```
- 테스트 파일이 분산되어 있음
- manual_tests와 archived는 별도 폴더로 이동 필요

#### 3. 중복 코드
- 여러 파일에서 API 호출 패턴 반복
- 데이터 변환 로직 중복
- 로깅 코드 중복

#### 4. 성능 문제
- 대쉬보드에서 매번 KRX/NXT를 별도로 조회 (2번 API 호출)
- 캐싱 부족
- 불필요한 데이터 재계산

---

## 🎯 개선 계획

### Phase 1: 긴급 개선 (우선순위: 높음)

#### 1.1 dashboard/app_apple.py 분할
```
dashboard/
├── app.py                    # 메인 앱 (초기화, 설정)
├── routes/
│   ├── __init__.py
│   ├── account.py           # 계좌 관련 라우트
│   ├── trading.py           # 매매 관련 라우트
│   ├── ai.py                # AI 분석 라우트
│   ├── market.py            # 시장 데이터 라우트
│   ├── portfolio.py         # 포트폴리오 라우트
│   └── system.py            # 시스템 상태 라우트
├── websocket/
│   ├── __init__.py
│   ├── handlers.py          # WebSocket 핸들러
│   └── events.py            # SocketIO 이벤트
└── utils/
    ├── __init__.py
    ├── response.py          # 응답 포맷팅
    └── validation.py        # 입력 검증
```

**예상 효과**:
- 파일당 300-500줄로 관리 용이
- 기능별 명확한 분리
- 팀 협업 시 충돌 감소

#### 1.2 main.py 리팩토링
```
main.py (200줄) - 메인 진입점만
├── core/
│   ├── trading_bot.py       # TradingBot 기본 클래스
│   ├── scanner.py           # 종목 스캐닝
│   ├── executor.py          # 매매 실행
│   └── monitor.py           # 모니터링
├── strategies/
│   ├── base.py              # 전략 기본 클래스
│   ├── momentum.py          # 모멘텀 전략
│   └── ...
```

**예상 효과**:
- 기능별 독립적인 테스트 가능
- 코드 재사용성 향상
- 유지보수 용이

#### 1.3 테스트 폴더 재구성
```
tests/
├── unit/                     # 단위 테스트
│   ├── test_account.py
│   ├── test_trading.py
│   └── ...
├── integration/              # 통합 테스트
│   ├── test_api_integration.py
│   └── ...
├── manual/                   # 수동 테스트 (기존 manual_tests 이동)
│   └── ...
└── archived/                 # 아카이브 (참고용)
    └── ...
```

### Phase 2: 성능 개선 (우선순위: 중간)

#### 2.1 API 호출 최적화
```python
# 현재 (2번 API 호출)
holdings_krx = account_api.get_holdings(market_type="KRX")
holdings_nxt = account_api.get_holdings(market_type="NXT")

# 개선 (1번에 모든 시장 조회)
holdings = account_api.get_all_holdings()  # KRX+NXT 한 번에
```

#### 2.2 캐싱 도입
```python
from functools import lru_cache
from datetime import datetime, timedelta

@cache_with_ttl(seconds=5)
def get_account_summary():
    """5초간 캐시된 계좌 요약 반환"""
    pass
```

#### 2.3 비동기 처리
```python
# 병렬로 여러 API 호출
async def get_dashboard_data():
    deposit, holdings, candidates = await asyncio.gather(
        get_deposit_async(),
        get_holdings_async(),
        get_candidates_async()
    )
```

### Phase 3: UI/UX 개선 (우선순위: 중간)

#### 3.1 차트 성능 개선
- Lazy loading으로 초기 로딩 속도 향상
- 차트 데이터 캐싱
- WebSocket으로 실시간 업데이트 (polling 대신)

#### 3.2 대쉬보드 응답성 개선
- API 호출 최소화
- 로딩 스피너 추가
- 오류 메시지 사용자 친화적으로 개선

#### 3.3 모바일 최적화
- 반응형 디자인 개선
- 터치 인터페이스 최적화

### Phase 4: 코드 품질 개선 (우선순위: 낮음)

#### 4.1 타입 힌트 추가
```python
def get_account_balance() -> Dict[str, Union[int, float]]:
    """계좌 잔액 조회"""
    pass
```

#### 4.2 Docstring 표준화
- Google 스타일 또는 NumPy 스타일로 통일
- 모든 public 함수에 docstring 추가

#### 4.3 린팅 및 포맷팅
- `black` (코드 포맷터)
- `flake8` (린터)
- `mypy` (타입 체커)

---

## 🚀 실행 계획

### 단계별 실행 (권장)

#### Week 1: Phase 1.1 - dashboard 분할
- [ ] routes 폴더 생성
- [ ] account.py 분리 (계좌 API)
- [ ] trading.py 분리 (매매 API)
- [ ] ai.py 분리 (AI API)
- [ ] 기존 app_apple.py 제거

#### Week 2: Phase 1.2 - main.py 리팩토링
- [ ] TradingBot 클래스 분할
- [ ] Scanner 모듈 분리
- [ ] Executor 모듈 분리
- [ ] 테스트 작성 및 검증

#### Week 3: Phase 2 - 성능 개선
- [ ] API 호출 최적화
- [ ] 캐싱 도입
- [ ] 성능 측정 및 비교

#### Week 4: Phase 3 - UI/UX 개선
- [ ] 차트 최적화
- [ ] 대쉬보드 응답성 개선
- [ ] 사용자 피드백 반영

---

## 📝 즉시 적용 가능한 개선 사항

### 1. 불필요한 파일 제거
```bash
# 아카이브된 테스트 파일 정리
mv tests/archived/* archive_backup/
rm -rf tests/archived

# 중복 파일 확인 및 제거
# (예: 비슷한 이름의 파일들)
```

### 2. 간단한 성능 개선
```python
# dashboard/app_apple.py에서
# 중복 API 호출 제거, 결과 재사용
```

### 3. 로깅 개선
```python
# 일관된 로깅 포맷 사용
import logging
logger = logging.getLogger(__name__)
logger.info(f"[{module_name}] {message}")
```

---

## 🎯 다음 단계

1. **이 계획 검토 및 피드백**
2. **우선순위 확인** (어떤 Phase부터 진행할지)
3. **단계적 실행** (한 번에 하나씩)
4. **테스트 및 검증** (각 단계마다)
5. **문서화** (변경 사항 기록)

---

## ⚠️ 주의사항

1. **백업 필수**: 리팩토링 전 코드 백업
2. **테스트 작성**: 변경 전/후 동작 검증
3. **점진적 변경**: 한 번에 모든 것을 바꾸지 말 것
4. **기능 유지**: 기존 기능이 깨지지 않도록 주의
5. **문서화**: 변경 사항을 README나 CHANGELOG에 기록

---

## 📊 예상 효과

### 파일 크기 감소
- `app_apple.py`: 3,249줄 → 200줄 (93% 감소)
- `main.py`: 1,617줄 → 200줄 (88% 감소)

### 성능 향상
- API 호출: 50% 감소 (캐싱 + 최적화)
- 대쉬보드 로딩: 30% 빠름
- 메모리 사용량: 20% 감소

### 유지보수성 향상
- 파일당 평균 줄 수: 300-500줄
- 기능별 명확한 분리
- 테스트 작성 용이

---

*작성일: 2025-11-05*
*작성자: Claude AI Assistant*
