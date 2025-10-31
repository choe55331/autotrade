# 🚀 AutoTrade Pro v2.0 빠른 시작 가이드

## ⚡ 5분 만에 시작하기

### 1단계: 패키지 설치
```bash
pip install -r requirements.txt
```

**Windows에서 에러 발생 시**:
```bash
pip install requests pandas numpy Flask PyYAML loguru SQLAlchemy python-dotenv websocket-client google-generativeai
```

### 2단계: 환경 변수 설정
프로젝트 루트에 `.env` 파일 생성:
```env
# Kiwoom API
KIWOOM_APP_KEY=your_app_key
KIWOOM_APP_SECRET=your_app_secret
KIWOOM_ACCOUNT_NO=your_account_number

# AI API (필수)
GOOGLE_API_KEY=your_gemini_api_key
```

### 3단계: 실행
```bash
python main.py
```

### 4단계: 대시보드 확인
브라우저에서 http://localhost:5000 접속

## 📊 주요 기능 확인

### 새로운 기능이 작동하는지 확인하세요:

#### 1. 3단계 스캐닝 파이프라인
로그에서 다음 메시지를 찾으세요:
```
⚡ Fast Scan 시작...
🔬 Deep Scan 시작...
🤖 AI Scan 시작...
```

#### 2. 스코어링 시스템
종목 분석 시:
```
📊 [종목명] 스코어: 350/440 (79.5%) - B등급
```

#### 3. 동적 리스크 관리
시작 시 현재 모드 표시:
```
🛡️  리스크 모드: ⚖️ 일반 모드 - 균형 잡힌 전략
```

수익률에 따라 자동으로 모드 변경:
- 🔥 Aggressive (수익 +5% 이상)
- ⚖️ Normal (-5% ~ +5%)
- 🛡️ Conservative (-10% ~ -5%)
- 🔒 Very Conservative (-10% 이하)

#### 4. 데이터베이스 기록
`data/autotrade.db` 파일이 생성되고 모든 거래가 기록됩니다.

## 🔧 문제 해결

### "No module named..." 에러
```bash
pip install -r requirements.txt
```

### 패키지 설치 실패
Windows에서 pandas 설치 실패 시:
```bash
pip install --upgrade pip
pip install pandas>=2.2.0
```

### 데이터베이스 에러
```bash
# 데이터베이스 초기화
rm -f data/autotrade.db
python main.py
```

### 이전 버전으로 돌아가기
```bash
cp archive/main_v1.py main.py
```

## 📁 폴더 구조

```
autotrade/
├── main.py                    # ✨ 새로운 통합 시스템 (v2.0)
├── main_v2.py                 # 백업용
├── archive/                   # 이전 버전들
│   └── main_v1.py
│
├── config/
│   ├── config.yaml            # ✨ YAML 설정 (중요!)
│   ├── config_manager.py      # ✨ 설정 관리자
│   └── ...
│
├── data/                      # ✨ 정리된 데이터 폴더
│   ├── control.json
│   ├── strategy_state.json
│   └── autotrade.db           # ✨ 데이터베이스
│
├── logs/                      # 로그 파일들
│   ├── bot.log
│   └── error.log              # ✨ 에러 전용 로그
│
├── research/
│   └── scanner_pipeline.py    # ✨ 3단계 스캐닝
│
├── strategy/
│   ├── scoring_system.py      # ✨ 10가지 스코어링
│   └── dynamic_risk_manager.py # ✨ 동적 리스크 관리
│
├── database/                  # ✨ 데이터베이스 모델
│   ├── models.py
│   └── __init__.py
│
└── utils/
    └── logger_new.py          # ✨ Loguru 로거
```

## 🎯 v2.0 vs v1.0 차이점

| 기능 | v1.0 | v2.0 |
|------|------|------|
| 스캐닝 | 단일 단계 | ⭐ 3단계 파이프라인 |
| 스코어링 | 간단한 점수 | ⭐ 440점 만점 체계 |
| 리스크 관리 | 정적 | ⭐ 동적 모드 전환 |
| 설정 관리 | Python 파일 | ⭐ YAML (실시간 변경) |
| 로깅 | 기본 | ⭐ Loguru (자동 로테이션) |
| 데이터 저장 | JSON | ⭐ SQLite DB |

## 💡 사용 팁

### 1. 설정 실시간 변경
`config/config.yaml` 파일을 수정하면 자동으로 반영됩니다.

### 2. 로그 확인
```bash
tail -f logs/bot.log        # 전체 로그
tail -f logs/error.log      # 에러만
```

### 3. 데이터베이스 조회
```bash
sqlite3 data/autotrade.db
> SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10;
```

### 4. 테스트 실행
```bash
python test_integration.py  # 통합 테스트
```

## 📞 도움말

- 상세 가이드: `README_V2.md`
- Windows 설치: `INSTALL_WINDOWS.md`
- GitHub Issues: 문제 발생 시 이슈 등록

---

**모든 기능이 제대로 작동하는 완전한 v2.0 시스템입니다!** 🎉
