# 자동매매 시스템 - 간단 실행 가이드 🚀

## 실행 방법 (딱 1가지)

```bash
python main.py
```

끝! 이게 전부입니다.

---

## 대시보드 접속

브라우저에서:
```
http://localhost:5000
```

---

## 필수 설정

### 1. API 키 설정 (.env 파일)

`config/credentials.py` 파일에 키 입력:

```python
# Kiwoom API
KIWOOM_API_KEY = "your-kiwoom-api-key"
KIWOOM_API_SECRET = "your-kiwoom-api-secret"
KIWOOM_ACCOUNT_NO = "your-account-number"

# Gemini API (AI 분석용)
GEMINI_API_KEY = "your-gemini-api-key"
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

---

## 주요 기능

### ✅ 현재 사용 가능한 기능

1. **자동 매매**
   - AI(Gemini) 분석 기반 자동 매수/매도
   - 모멘텀 전략
   - 리스크 관리

2. **대시보드**
   - 계좌 정보 실시간 조회
   - 보유 종목 현황
   - 손익 현황
   - 봇 제어 (시작/정지/매수중지/매수재개)

3. **AI 분석**
   - Gemini AI 기반 종목 분석
   - 매수/매도 신호 생성
   - 시장 분석

---

## 계좌 정보 확인

대시보드에서 자동으로 다음 정보를 표시합니다:

- 💰 총 자산
- 💵 보유 현금 (예수금)
- 📊 평가 금액 (보유 주식 가치)
- 📈 총 손익 (금액 & 수익률)
- 📋 보유 종목 상세 내역

대시보드가 10초마다 자동으로 새로고침됩니다.

---

## 문제 해결

### Q: 계좌 정보가 안 보여요
```
A: Kiwoom API 키가 올바른지 확인
   config/credentials.py 파일 확인
   Kiwoom API 호출 한도 확인 (초당 0.3초 제한)
```

### Q: AI 분석이 안 돼요
```
A: Gemini API 키 확인
   export GEMINI_API_KEY="your-key"
   또는 config/credentials.py에 설정
```

### Q: 대시보드가 안 열려요
```
A: 포트 5000이 사용 중인지 확인
   lsof -i :5000  (Linux/Mac)
   netstat -ano | findstr :5000  (Windows)
```

### Q: 실제 주문이 안 나가요
```
A: api/order.py가 DRY RUN 모드인지 확인
   실제 거래를 위해서는 order.py 수정 필요
```

---

## 로그 확인

```bash
# 로그 파일 위치
logs/trading_bot.log

# 실시간 로그 보기
tail -f logs/trading_bot.log  # Linux/Mac
Get-Content logs/trading_bot.log -Wait  # Windows PowerShell
```

---

## 제어

### 대시보드에서 제어
- ▶️ 시작: 봇 시작
- ⏹️ 정지: 봇 정지
- ⏸️ 매수 중지: 매수만 일시 중지 (매도는 계속)
- ▶️ 매수 재개: 매수 재개

### control.json 파일로 제어

`control.json` 파일을 수정하면 실시간으로 설정 변경:

```json
{
  "run": true,
  "pause_buy": false,
  "pause_sell": false,
  "max_positions": 5,
  "risk_per_trade": 0.20
}
```

---

## 고급 기능 (선택사항)

고급 기능을 사용하고 싶다면:

1. **UPGRADE_GUIDE.md** 참조
   - Multi-AI Ensemble (GPT-4, Claude 추가)
   - 딥러닝 가격 예측
   - 알고리즘 주문 실행
   - 전문가급 리스크 분석
   - 백테스팅

2. **필요한 경우에만 활성화**
   - 기본 기능만으로도 충분히 사용 가능
   - 고급 기능은 추가 API 키와 패키지 필요

---

## 디렉토리 구조

```
autotrade/
├── main.py              ← 이것만 실행하면 됩니다!
├── dashboard/
│   └── dashboard.py     ← 대시보드
├── api/                 ← Kiwoom API 연동
├── strategy/            ← 매매 전략
├── ai/                  ← AI 분석 (Gemini)
├── config/              ← 설정 파일
├── logs/                ← 로그 파일
└── control.json         ← 실시간 제어 파일
```

---

## 안전 수칙 ⚠️

1. **소액으로 시작**: 처음엔 소액으로 테스트
2. **DRY RUN 먼저**: 실제 거래 전에 시뮬레이션
3. **손절 설정**: 리스크 관리 필수
4. **모니터링**: 대시보드로 실시간 확인
5. **로그 확인**: 문제 발생 시 로그 분석

---

## 지원

- 기본 가이드: 이 파일 (README_SIMPLE.md)
- 고급 기능: UPGRADE_GUIDE.md
- 빠른 시작: QUICK_START.md

---

**그냥 실행하세요:**

```bash
python main.py
```

**끝!** 🎉
