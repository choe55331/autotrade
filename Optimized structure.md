# 키움증권 REST API 자동매매 시스템 - 최적화된 구조

## 📁 최적화된 파일 구조

```
autotrade5/
│
├── config/                     # 설정 파일 통합
│   ├── __init__.py
│   ├── settings.py            # 기본 설정
│   ├── credentials.py         # API 키 등 민감 정보
│   └── trading_params.py      # 매매 파라미터
│
├── core/                       # 핵심 API 클라이언트
│   ├── __init__.py
│   ├── rest_client.py         # REST API 클라이언트 (기존 kiwoom.py)
│   ├── websocket_client.py    # WebSocket 클라이언트 통합
│   └── exceptions.py          # 커스텀 예외 정의
│
├── api/                        # API 엔드포인트 래퍼 (account 폴더 통합)
│   ├── __init__.py
│   ├── account.py             # 계좌 관련 API
│   ├── market.py              # 시세/시장 관련 API
│   ├── order.py               # 주문 관련 API
│   └── realtime.py            # 실시간 데이터 API
│
├── research/                   # 데이터 조회/분석 (기존 유지)
│   ├── __init__.py
│   ├── data_fetcher.py        # 데이터 수집
│   ├── analyzer.py            # 데이터 분석
│   └── screener.py            # 종목 스크리닝
│
├── strategy/                   # 매매 전략 (개선)
│   ├── __init__.py
│   ├── base_strategy.py       # 전략 기본 클래스
│   ├── momentum_strategy.py   # 모멘텀 전략 예시
│   ├── portfolio_manager.py   # 포트폴리오 관리
│   └── risk_manager.py        # 리스크 관리
│
├── ai/                         # AI 분석 모듈 (신규)
│   ├── __init__.py
│   ├── base_analyzer.py       # 분석기 인터페이스
│   ├── gemini_analyzer.py     # Gemini 분석기
│   └── mock_analyzer.py       # Mock 분석기
│
├── notification/               # 알림 모듈 (신규)
│   ├── __init__.py
│   ├── base_notifier.py       # 알림 인터페이스
│   ├── telegram_notifier.py   # Telegram 알림
│   └── mock_notifier.py       # Mock 알림
│
├── utils/                      # 유틸리티 (신규)
│   ├── __init__.py
│   ├── logger.py              # 로깅 설정
│   ├── file_handler.py        # 파일 입출력
│   ├── validators.py          # 데이터 검증
│   └── decorators.py          # 공통 데코레이터
│
├── dashboard/                  # 대시보드 (기존 유지)
│   ├── __init__.py
│   └── dashboard.py
│
├── main.py                     # 메인 실행 파일 (개선)
├── start_autotrade.bat         # 시작 스크립트
├── requirements.txt            # 의존성 관리
├── .env                        # 환경변수 (민감정보)
├── bot.log                     # 로그 파일
├── control.json                # 봇 제어 파일
└── strategy_state.json         # 전략 상태 저장 파일
```

## 🔧 개선 사항 요약

### 1. **config 폴더 분리**
- 설정을 용도별로 분리하여 관리 용이성 향상
- 민감정보(.env)와 일반 설정 분리

### 2. **core 폴더 신규 생성**
- REST/WebSocket 클라이언트를 core로 통합
- 예외 처리를 중앙화

### 3. **api 폴더 통합**
- 14개로 나뉘어진 account 폴더를 4개 파일로 통합
- 관련 기능끼리 그룹화

### 4. **ai/notification 폴더 분리**
- Mock 클래스를 별도 모듈로 분리
- 의존성 주입 패턴 적용

### 5. **utils 폴더 신규**
- 공통 유틸리티 함수 중앙화
- 재사용성 향상