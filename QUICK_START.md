# 빠른 시작 가이드 ⚡

## 1. 기본 실행 (기존 방식)

```bash
# 기본 봇 + 기본 대시보드
python main.py
```

브라우저에서 접속: `http://localhost:5000`

---

## 2. 새로운 방식 (권장) 🚀

### 📊 기본 모드
```bash
python start.py
```

### 🎨 고급 대시보드만 실행
```bash
python start.py --dashboard
```
- TradingView 스타일 차트
- 실시간 AI 인사이트
- 프로페셔널 UI

### 🧠 AI Ensemble 활성화
```bash
python start.py --dashboard --ai-ensemble
```
- Gemini + GPT-4 + Claude 동시 사용
- 다중 모델 투표 시스템

**⚠️ 필수 설정:**
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 🎯 모든 고급 기능 활성화
```bash
python start.py --dashboard --ai-ensemble --algo-orders --risk-analytics
```
- 고급 대시보드
- 3-AI 앙상블
- 알고리즘 주문 (TWAP, VWAP)
- 리스크 분석 (VaR, Sharpe)

---

## 3. 실행 옵션 전체 목록

```bash
# 도움말
python start.py --help

# 기본 모드
python start.py

# 고급 대시보드 (포트 변경)
python start.py --dashboard --dashboard-port 8080

# AI Ensemble (GPT-4만)
python start.py --dashboard --enable-gpt4

# AI Ensemble (Claude만)
python start.py --dashboard --enable-claude

# AI Ensemble (모든 모델)
python start.py --dashboard --ai-ensemble

# 알고리즘 주문 활성화
python start.py --algo-orders

# 리스크 분석 활성화
python start.py --risk-analytics

# 딥러닝 예측 활성화
python start.py --dl-prediction

# DRY RUN (실제 주문 없이 테스트)
python start.py --dry-run

# 백테스팅
python start.py --backtest --backtest-start 2023-01-01 --backtest-end 2024-12-31
```

---

## 4. 추천 시작 방법

### 🔰 초보자
```bash
# 1단계: 기본 모드로 익숙해지기
python start.py

# 2단계: 고급 대시보드 체험
python start.py --dashboard
```

### 🚀 중급자
```bash
# AI Ensemble + 고급 대시보드
python start.py --dashboard --ai-ensemble
```

### 💎 전문가
```bash
# 모든 기능 활성화
python start.py --dashboard --ai-ensemble --algo-orders --risk-analytics --dl-prediction
```

---

## 5. 필수 패키지 설치

### 기본 실행 (이미 설치됨)
```bash
pip install flask requests pandas numpy
```

### AI Ensemble 사용 시
```bash
pip install openai anthropic
```

### 딥러닝 예측 사용 시
```bash
pip install tensorflow
# 또는
pip install torch
```

---

## 6. API 키 설정

### 환경변수로 설정
```bash
# Kiwoom (필수)
export KIWOOM_API_KEY="your-key"
export KIWOOM_API_SECRET="your-secret"

# Gemini (기본 사용)
export GEMINI_API_KEY="your-key"

# GPT-4 (옵션)
export OPENAI_API_KEY="sk-..."

# Claude (옵션)
export ANTHROPIC_API_KEY="sk-ant-..."
```

### .env 파일 사용
```bash
# .env 파일 생성
cat > .env << EOF
KIWOOM_API_KEY=your-key
KIWOOM_API_SECRET=your-secret
GEMINI_API_KEY=your-key
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
EOF
```

---

## 7. 대시보드 접속

### 기본 대시보드
```
http://localhost:5000
```

### 고급 대시보드
```
http://localhost:5000
```

포트 변경 시:
```bash
python start.py --dashboard --dashboard-port 8080
# http://localhost:8080
```

---

## 8. 문제 해결

### Q: "ModuleNotFoundError: No module named 'openai'"
```bash
A: pip install openai anthropic
```

### Q: AI Ensemble이 동작하지 않음
```bash
A: 환경변수 확인
   echo $OPENAI_API_KEY
   echo $ANTHROPIC_API_KEY
```

### Q: 대시보드가 로드되지 않음
```bash
A: 포트 충돌 확인
   lsof -i :5000
   # 다른 포트 사용
   python start.py --dashboard --dashboard-port 8080
```

### Q: TensorFlow 설치 오류
```bash
A: Python 버전 확인 (3.8+ 필요)
   python --version

   pip install --upgrade pip
   pip install tensorflow
```

---

## 9. 실전 사용 예시

### 시나리오 1: 보수적 트레이딩
```bash
# AI 3개 모두 동의할 때만 거래
python start.py --dashboard --ai-ensemble
# (대시보드에서 voting_strategy를 'unanimous'로 설정)
```

### 시나리오 2: 공격적 트레이딩
```bash
# 가중 평균 + 알고리즘 주문
python start.py --dashboard --ai-ensemble --algo-orders
```

### 시나리오 3: 리스크 중심
```bash
# 리스크 분석 + 보수적 포지션
python start.py --dashboard --risk-analytics
```

### 시나리오 4: 백테스팅
```bash
# 전략 검증
python start.py --backtest --backtest-start 2023-01-01 --backtest-end 2023-12-31
```

---

## 10. 다음 단계

1. **UPGRADE_GUIDE.md** - 상세한 기능 설명
2. **예제 코드** - 각 기능별 사용 예시
3. **설정 커스터마이징** - 나만의 전략 설정

---

## 💡 팁

- **처음 사용**: `python start.py --dashboard` 로 시작
- **AI 활용**: GPT-4 > Claude > Gemini 순으로 정확도 높음
- **리스크 관리**: `--risk-analytics` 옵션 항상 권장
- **백테스팅**: 실전 전에 반드시 백테스팅으로 검증

---

## 📞 지원

문제가 있으시면 `UPGRADE_GUIDE.md`의 "문제 해결" 섹션을 참조하세요.

**Happy Trading! 🚀💰**
