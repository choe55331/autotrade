# 🤖 키움증권 자동매매 봇

Python 기반 키움증권 REST API 자동매매 시스템

## 📋 목차

- [특징](#특징)
- [시스템 구조](#시스템-구조)
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [설정](#설정)
- [주의사항](#주의사항)

## ✨ 특징

- **자동 매매**: 모멘텀 기반 자동 매수/매도
- **AI 분석**: Google Gemini API를 활용한 종목 분석
- **리스크 관리**: 손절/익절, 포지션 관리, 일일 손실 제한
- **웹 대시보드**: 실시간 계좌 및 포지션 모니터링
- **REST API**: 키움증권 REST API 사용 (OpenAPI X)

## 🏗️ 시스템 구조
```
trading-bot/
├── config/              # 설정 파일
├── core/                # REST API 클라이언트
├── api/                 # API 래퍼
├── research/            # 데이터 조회/분석
├── strategy/            # 매매 전략
├── ai/                  # AI 분석 모듈
├── utils/               # 유틸리티
├── dashboard/           # 웹 대시보드
├── main.py              # 메인 실행 파일
└── requirements.txt     # 의존성 패키지
```

## 📥 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/kiwoom-trading-bot.git
cd kiwoom-trading-bot
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정

`.env` 파일을 생성하고 API 키 입력:
```bash
KIWOOM_REST_APPKEY=your_app_key
KIWOOM_REST_SECRETKEY=your_secret_key
ACCOUNT_NUMBER=12345678-01
GEMINI_API_KEY=your_gemini_api_key
```

## 🚀 사용 방법

### Windows에서 실행
```bash
start_autotrade.bat
```

### 직접 실행
```bash
python main.py
```

### 대시보드 접속

브라우저에서 http://localhost:5000 접속

## ⚙️ 설정

### control.json

봇 실행 중 동적으로 설정 변경 가능:
```json
{
  "run": true,                    // 봇 실행 여부
  "pause_buy": false,             // 매수 중지
  "pause_sell": false,            // 매도 중지
  "MAX_OPEN_POSITIONS": 5,        // 최대 포지션 수
  "TAKE_PROFIT_RATIO": 0.1,       // 목표 수익률 10%
  "STOP_LOSS_RATIO": -0.05        // 손절 비율 -5%
}
```

### config/trading_params.py

전략 파라미터 조정:

- 포지션 크기
- 손익 비율
- 필터링 조건
- AI 분석 설정

## ⚠️ 주의사항

1. **모의투자 테스트 필수**: 실전 투자 전 충분한 테스트 필요
2. **API 키 보안**: `.env` 파일을 Git에 커밋하지 마세요
3. **리스크 관리**: 손실 제한을 반드시 설정하세요
4. **시장 모니터링**: 자동매매 중에도 주기적인 확인 필요
5. **법적 책임**: 모든 투자 손실은 사용자 책임입니다

## 📝 라이선스

MIT License

## 🤝 기여

이슈 및 PR 환영합니다!

## 📧 문의

이슈 탭을 이용해주세요.