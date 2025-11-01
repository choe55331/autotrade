# 프로젝트 구조

## 📁 최적화된 폴더 구조

```
autotrade/
├── _immutable/                    # 🔒 검증된 불변 설정
│   ├── api_specs/                # API 사양 (93.5% 성공률)
│   │   ├── successful_apis.json  # 346개 검증된 API
│   │   ├── apis_by_category.json # 카테고리별 분류
│   │   └── API_USAGE_GUIDE.md    # 사용 가이드
│   ├── credentials/              # 인증 정보 (gitignore됨)
│   │   ├── secrets.json          # API 키, 계좌번호
│   │   └── secrets.example.json  # 예시 파일
│   └── README.md                 # 불변 설정 가이드
│
├── config/                        # ⚙️ 설정 관리
│   ├── __init__.py               # 설정 통합
│   ├── api_loader.py             # API 로더 (NEW!)
│   ├── credentials.py            # 자격증명 (secrets.json 우선)
│   ├── settings.py               # 일반 설정
│   ├── trading_params.py         # 매매 파라미터
│   ├── config_manager.py         # 설정 관리자
│   └── demo_stocks.py            # 데모 주식 목록
│
├── core/                          # 🔧 핵심 기능
│   ├── rest_client.py            # REST API 클라이언트 (검증 API 지원)
│   ├── websocket_client.py       # WebSocket 클라이언트
│   ├── exceptions.py             # 예외 정의
│   └── __init__.py
│
├── api/                           # 📡 API 관련
│   ├── account.py                # 계좌 API 정의
│   ├── kiwoom_api_specs.py       # API 사양
│   └── kiwoom_api_specs_extended.py
│
├── dashboard/                     # 📊 대시보드
│   ├── app_apple.py              # 메인 대시보드
│   ├── templates/                # HTML 템플릿
│   └── __init__.py
│
├── research/                      # 🔬 리서치 모듈
│   ├── scanner_pipeline.py       # 스캐너 파이프라인
│   ├── theme_analyzer.py         # 테마 분석기
│   ├── screener.py               # 스크리너
│   ├── data_fetcher.py           # 데이터 수집
│   ├── analyzer.py               # 분석기
│   └── __init__.py
│
├── strategy/                      # 📈 전략 모듈
│   ├── base_strategy.py          # 기본 전략
│   ├── momentum_strategy.py      # 모멘텀 전략
│   ├── portfolio_manager.py      # 포트폴리오 관리
│   ├── risk_manager.py           # 리스크 관리
│   ├── dynamic_risk_manager.py   # 동적 리스크 관리
│   ├── advanced_risk_analytics.py # 고급 리스크 분석
│   ├── scoring_system.py         # 스코어링 시스템
│   └── __init__.py
│
├── ai/                            # 🤖 AI 모듈
│   ├── gemini_client.py          # Gemini AI 클라이언트
│   ├── market_analyzer.py        # 시장 분석
│   ├── prompt_templates.py       # 프롬프트 템플릿
│   └── __init__.py
│
├── utils/                         # 🛠️ 유틸리티
│   ├── logger.py                 # 로거
│   ├── decorators.py             # 데코레이터
│   ├── helpers.py                # 헬퍼 함수
│   └── __init__.py
│
├── features/                      # 🎯 피처 엔지니어링
│   └── technical_indicators.py
│
├── indicators/                    # 📉 기술적 지표
│   └── momentum.py
│
├── tests/                         # 🧪 테스트 (NEW!)
│   ├── api_tests/                # API 테스트
│   │   ├── test_verified_and_corrected_apis_fixed.py  # ⭐ 최신 (346/370 성공)
│   │   ├── test_all_394_calls.py
│   │   └── ...
│   ├── analysis/                 # 분석 스크립트
│   │   ├── analyze_test_results.py
│   │   ├── create_corrected_api_calls.py
│   │   └── ...
│   ├── integration/              # 통합 테스트
│   ├── archived/                 # 보관 (구버전)
│   └── README.md
│
├── docs/                          # 📚 문서 (NEW!)
│   ├── API_OPTIMIZATION_README.md
│   ├── API_TESTER_GUIDE.md
│   ├── API_TEST_STATUS.md
│   ├── FINAL_TEST_GUIDE.md
│   ├── INSTALL_WINDOWS.md
│   ├── QUICK_START.md
│   ├── CHANGELOG_V4.*.md
│   └── ...
│
├── test_results/                  # 📊 테스트 결과 (NEW!)
│   ├── *.json                    # 테스트 결과 JSON
│   ├── *.txt                     # 테스트 결과 TXT
│   └── deprecated/               # 구버전 파일
│
├── kiwoom_docs/                   # 📖 키움 API 문서
│   └── *.md
│
├── database/                      # 💾 데이터베이스
├── logs/                          # 📝 로그
├── notification/                  # 📢 알림
│
├── main.py                        # 🚀 메인 실행 파일
├── README.md                      # 프로젝트 README
├── PROJECT_STRUCTURE.md           # 이 파일
├── requirements.txt               # 의존성
└── .gitignore                    # Git 무시 파일

```

## 🎯 주요 개선 사항 (2025-11-01)

### 1. 불변 설정 폴더 (`_immutable/`)
- ✅ 검증된 346개 API 저장 (93.5% 성공률)
- ✅ API 키와 계좌번호 중앙 집중 관리
- ✅ 카테고리별 API 분류
- ✅ .gitignore로 보안 강화

### 2. API 로더 시스템
- ✅ `config/api_loader.py` - 검증된 API 자동 로드
- ✅ `core/rest_client.py` - `call_verified_api()` 메서드 추가
- ✅ 카테고리별 조회 (account, market, ranking, search 등)
- ✅ API 검색 및 탐색 기능

### 3. 테스트 파일 정리
- ✅ 25개 테스트 파일 → `tests/` 폴더로 이동
- ✅ API 테스트, 분석, 통합, 보관으로 분류
- ✅ 루트 디렉토리 깔끔하게 정리

### 4. 문서 정리
- ✅ 14개 마크다운 파일 → `docs/` 폴더로 이동
- ✅ API 사용 가이드 추가
- ✅ 프로젝트 구조 문서 생성

### 5. 테스트 결과 아카이브
- ✅ JSON/TXT 결과 → `test_results/` 폴더로 이동
- ✅ 구버전 파일 → `deprecated/` 서브폴더
- ✅ 히스토리 보존

## 📊 파일 통계

### 정리 전 (루트)
- Python 파일: 27개
- JSON 파일: 15개
- Markdown 파일: 14개
- **총: 56개 파일**

### 정리 후 (루트)
- Python 파일: 1개 (main.py)
- Markdown 파일: 2개 (README.md, PROJECT_STRUCTURE.md)
- **총: 3개 파일** ✨

### 개선율
- **94.6% 파일 감소** (56개 → 3개)
- 폴더 구조 체계화
- 검색 및 유지보수 용이성 향상

## 🔧 사용 방법

### 1. 검증된 API 사용

```python
from core.rest_client import KiwoomRESTClient

# 자동으로 _immutable/credentials/secrets.json 로드
client = KiwoomRESTClient()

# 검증된 API 호출 (93.5% 성공률)
result = client.call_verified_api('kt00005')

# 카테고리별 API 조회
account_apis = client.get_available_apis(category='account')
```

### 2. 설정 관리

```python
from config import (
    get_credentials,
    get_api_loader,
    TRADING_PARAMS,
)

# 자격증명 (secrets.json 우선)
creds = get_credentials()
print(creds.KIWOOM_REST_APPKEY)

# 검증된 API 로드
loader = get_api_loader()
all_apis = loader.get_all_apis()

# 매매 파라미터
max_positions = TRADING_PARAMS['MAX_OPEN_POSITIONS']
```

### 3. 테스트 실행

```bash
# 최신 검증된 테스트 (346/370 성공)
python tests/api_tests/test_verified_and_corrected_apis_fixed.py

# 테스트 결과 분석
python tests/analysis/analyze_test_results.py
```

## 🔐 보안

### gitignore 설정
```gitignore
# Immutable credentials (NEVER commit!)
_immutable/credentials/secrets.json
_immutable/credentials/*.key
_immutable/credentials/*.pem
_immutable/credentials/*.env
```

### credentials 우선순위
1. `_immutable/credentials/secrets.json` (최우선)
2. 환경변수 (`.env`)
3. 기본값 (하드코딩)

## 📝 다음 단계

### Dashboard 업데이트
- [ ] `dashboard/app_apple.py` → 새 API 로더 사용
- [ ] 검증된 API만 사용하도록 수정
- [ ] 에러 처리 개선

### Research 업데이트
- [ ] `research/data_fetcher.py` → 검증된 API 사용
- [ ] `research/scanner_pipeline.py` → API 로더 통합

### Strategy 업데이트
- [ ] `strategy/portfolio_manager.py` → 검증된 계좌 API 사용
- [ ] 리스크 관리 → 실시간 시세 API 통합

## 🎉 성과

✅ **346개 검증된 API** (93.5% 성공률)
✅ **94.6% 파일 정리** (56개 → 3개)
✅ **중앙 집중식 설정** 관리
✅ **검증된 파라미터** 사용
✅ **보안 강화** (credentials 분리)
✅ **유지보수성** 향상
✅ **문서화** 완료

---

**마지막 업데이트**: 2025-11-01
**버전**: 5.0.0 (대규모 개편)
