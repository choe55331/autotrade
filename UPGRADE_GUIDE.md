# AI Trading System - Major Upgrade Guide 🚀

## Overview

대시보드와 주문 시스템을 **세계 최고 수준의 AI 자동매매 플랫폼**으로 업그레이드했습니다.
QuantConnect, Trade Ideas, Bloomberg Terminal 등 시중 최고의 플랫폼들의 기능을 참조하여 구현했습니다.

---

## 🎯 주요 업그레이드 내용

### 1. 🧠 Multi-AI Ensemble Analyzer

**세 개의 최첨단 AI 모델을 동시에 활용**하여 의사결정의 정확도를 극대화했습니다.

#### 구성 AI 모델:
- **Gemini 2.5 Flash** (기존) - Google의 최신 AI
- **GPT-4 Turbo** (신규) - OpenAI의 최첨단 모델
- **Claude 3.5 Sonnet** (신규) - Anthropic의 고급 추론 모델

#### 앙상블 전략:
- **Majority Voting**: 다수결 투표
- **Weighted Average**: 모델 성능 기반 가중 평균
- **Unanimous**: 전체 모델 합의 시에만 거래
- **Best Performer**: 역사적 최고 성능 모델 선택

#### 사용법:
```python
from ai.ensemble_analyzer import EnsembleAnalyzer, VotingStrategy

# 앙상블 분석기 초기화 (GPT-4, Claude 활성화)
analyzer = EnsembleAnalyzer(
    voting_strategy=VotingStrategy.WEIGHTED,
    enable_gpt4=True,
    enable_claude=True
)

# 주식 분석
result = analyzer.analyze_stock(stock_data)
print(f"Signal: {result['signal']}")
print(f"Confidence: {result['confidence']}")
print(f"Model votes: {result['model_votes']}")
```

#### 필수 패키지 설치:
```bash
pip install openai anthropic
```

#### 환경 변수 설정:
```bash
export OPENAI_API_KEY="your-gpt4-api-key"
export ANTHROPIC_API_KEY="your-claude-api-key"
```

---

### 2. 🤖 Deep Learning Price Predictor

**LSTM, CNN, Transformer** 모델을 활용한 가격 예측 시스템

#### 지원 모델:
- **LSTM**: 시계열 데이터 예측에 특화
- **CNN**: 차트 패턴 인식
- **Transformer**: 복잡한 종속성 파악
- **Ensemble**: 3가지 모델 결합

#### 주요 기능:
- 5일 후 가격 예측
- 신뢰구간 제공
- 기대 수익률 계산
- 자동 매수/매도 신호 생성

#### 사용법:
```python
from ai.deep_learning_predictor import DeepLearningPredictor

predictor = DeepLearningPredictor(
    sequence_length=60,  # 60일 데이터 사용
    prediction_horizon=5  # 5일 예측
)

# 가격 예측
prediction = predictor.predict_price(
    stock_data=stock_data,
    model_type="ensemble"  # "lstm", "cnn", "transformer", or "ensemble"
)

print(f"Expected Return: {prediction['expected_return']}%")
print(f"Signal: {prediction['signal']}")
print(f"Predicted Prices: {prediction['predicted_prices']}")
```

#### 필수 패키지:
```bash
pip install tensorflow numpy pandas
# 또는 PyTorch 사용 시:
pip install torch numpy pandas
```

---

### 3. 📊 Advanced Dashboard (TradingView/Bloomberg Style)

**프로페셔널급 실시간 대시보드**

#### 주요 특징:
- **실시간 차트**: TradingView 스타일 캔들스틱 차트
- **AI 인사이트 패널**: 다중 AI 모델 분석 결과 실시간 표시
- **성과 분석**: Sharpe Ratio, Sortino Ratio, Max Drawdown
- **포트폴리오 시각화**: 히트맵, 상관관계 매트릭스
- **백테스팅 결과**: 전략 성과 시각화

#### 실행 방법:
```python
from dashboard.advanced_dashboard import run_advanced_dashboard

# 고급 대시보드 시작
run_advanced_dashboard(
    bot_instance=trading_bot,
    host='0.0.0.0',
    port=5000
)
```

브라우저에서 접속: `http://localhost:5000`

#### 대시보드 구성:
1. **상단 네비게이션**: 실시간 봇 상태, 제어 버튼
2. **통계 카드**: 총 자산, 현금, 손익, 승률
3. **메인 차트**: 멀티 타임프레임 실시간 차트
4. **AI 인사이트**: 3개 AI 모델의 분석 결과
5. **성과 지표**: Sharpe, Sortino, Drawdown, Alpha, Beta
6. **보유 종목 테이블**: 실시간 손익 현황

---

### 4. 🎯 Algorithmic Order Execution

**기관투자자급 주문 실행 알고리즘**

#### 지원 알고리즘:

##### TWAP (Time-Weighted Average Price)
시간 기반 균등 분할 주문
```python
from api.algo_order_executor import AlgoOrderExecutor, OrderSide

executor = AlgoOrderExecutor(order_api, market_api)

# TWAP 실행
result = executor.execute_twap(
    stock_code='005930',
    total_quantity=1000,
    side=OrderSide.BUY,
    duration_minutes=60,  # 60분에 걸쳐 실행
    num_slices=10         # 10번으로 분할
)
```

##### VWAP (Volume-Weighted Average Price)
거래량 기반 적응형 주문
```python
result = executor.execute_vwap(
    stock_code='005930',
    total_quantity=1000,
    side=OrderSide.BUY,
    duration_minutes=60,
    target_participation=0.10  # 시장 거래량의 10%
)
```

##### Iceberg Order
대량 주문 숨김 실행
```python
result = executor.execute_iceberg(
    stock_code='005930',
    total_quantity=10000,     # 실제 수량
    display_quantity=100,     # 표시 수량
    side=OrderSide.BUY,
    limit_price=70000
)
```

##### Adaptive Algorithm
시장 상황 적응형 실행
```python
result = executor.execute_adaptive(
    stock_code='005930',
    total_quantity=1000,
    side=OrderSide.BUY,
    urgency=0.7,  # 0=patient, 1=aggressive
    duration_minutes=60
)
```

#### 실행 결과 조회:
```python
# 활성 알고리즘
active = executor.get_active_algorithms()

# 완료된 알고리즘
completed = executor.get_completed_algorithms(limit=20)

# 알고리즘 취소
executor.cancel_algorithm(algo_id)
```

---

### 5. 📈 Advanced Risk Analytics

**전문가급 리스크 관리 시스템**

#### 제공 지표:

##### Value at Risk (VaR)
손실 위험 측정
```python
from strategy.advanced_risk_analytics import AdvancedRiskAnalytics

analytics = AdvancedRiskAnalytics(confidence_level=0.95)

# Historical VaR
var_hist = analytics.calculate_var_historical(returns, confidence_level=0.95)

# Parametric VaR
var_param = analytics.calculate_var_parametric(returns)

# Monte Carlo VaR
var_mc, simulations = analytics.calculate_var_monte_carlo(
    current_value=10000000,
    mean_return=0.001,
    std_return=0.02,
    time_horizon=1,
    num_simulations=10000
)
```

##### Sharpe & Sortino Ratios
위험 조정 수익률
```python
sharpe = analytics.calculate_sharpe_ratio(returns)
sortino = analytics.calculate_sortino_ratio(returns)
```

##### Maximum Drawdown
최대 낙폭 분석
```python
dd_info = analytics.calculate_maximum_drawdown(equity_curve)
print(f"Max Drawdown: {dd_info['max_drawdown_pct']}%")
print(f"Underwater Days: {dd_info['underwater_days']}")
```

##### Monte Carlo Simulation
포트폴리오 시뮬레이션
```python
mc_results = analytics.run_monte_carlo_simulation(
    initial_value=10000000,
    mean_return=0.001,
    std_return=0.02,
    time_horizon=252,      # 1년
    num_simulations=10000
)

print(f"Probability of Profit: {mc_results['probability_profit']:.1%}")
print(f"95% Confidence Interval: {mc_results['percentile_5']:,.0f} ~ {mc_results['percentile_95']:,.0f}")
```

##### Comprehensive Risk Report
전체 리스크 지표
```python
metrics = analytics.calculate_risk_metrics(
    returns=daily_returns,
    equity_curve=equity_curve,
    benchmark_returns=kospi_returns
)

print(f"Sharpe: {metrics['sharpe_ratio']}")
print(f"Sortino: {metrics['sortino_ratio']}")
print(f"Max DD: {metrics['max_drawdown_pct']}%")
print(f"Alpha: {metrics['alpha']}")
print(f"Beta: {metrics['beta']}")
```

---

### 6. 🔬 Professional Backtesting Engine

**제도권급 백테스팅 시스템**

#### 주요 기능:
- 역사적 데이터 시뮬레이션
- 현실적인 실행 (슬리피지, 수수료)
- 포지션 관리
- 상세한 성과 분석
- 거래별 추적

#### 사용법:
```python
from backtesting import BacktestEngine, BacktestConfig

# 백테스트 설정
config = BacktestConfig(
    initial_capital=10000000,  # 초기 자본
    commission_rate=0.0015,    # 수수료 0.15%
    slippage_rate=0.001,       # 슬리피지 0.1%
    position_size=0.20,        # 포지션당 20%
    max_positions=5,           # 최대 5개 포지션
    stop_loss=-0.05,           # 손절 -5%
    take_profit=0.10           # 익절 +10%
)

# 백테스트 엔진 생성
engine = BacktestEngine(config)

# 백테스트 실행
results = engine.run_backtest(
    strategy=your_strategy,
    historical_data=historical_data,
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2024, 12, 31)
)

# 결과 출력
print(engine.generate_report(results))
```

#### 결과 분석:
```python
print(f"Total Return: {results.total_return_pct:.2f}%")
print(f"Sharpe Ratio: {results.sharpe_ratio:.2f}")
print(f"Win Rate: {results.win_rate:.1f}%")
print(f"Max Drawdown: {results.max_drawdown_pct:.2f}%")
print(f"Profit Factor: {results.profit_factor:.2f}")

# 거래 내역
for trade in results.trades:
    print(f"{trade.entry_date} - {trade.stock_code}: {trade.profit_loss_pct:+.2f}%")

# 시각화 (equity curve)
import matplotlib.pyplot as plt
plt.plot(results.equity_curve)
plt.title('Equity Curve')
plt.show()
```

---

## 📦 필수 패키지 설치

### Core AI & ML
```bash
pip install openai anthropic tensorflow numpy pandas scipy
```

### Data & Visualization
```bash
pip install pandas numpy matplotlib seaborn
```

### Web Dashboard
```bash
pip install flask chart.js
```

---

## 🚀 빠른 시작 가이드

### 1. 환경 설정
```bash
# API 키 설정
export GEMINI_API_KEY="your-gemini-key"
export OPENAI_API_KEY="your-gpt4-key"
export ANTHROPIC_API_KEY="your-claude-key"
export KIWOOM_API_KEY="your-kiwoom-key"
export KIWOOM_API_SECRET="your-kiwoom-secret"

# 패키지 설치
pip install -r requirements.txt
```

### 2. 고급 대시보드 실행
```bash
python run_advanced_dashboard.py
```

### 3. 백테스팅 실행
```bash
python run_backtest.py
```

---

## 🎨 주요 개선사항 요약

### AI 분석
- ✅ **3개 AI 모델 앙상블** (Gemini + GPT-4 + Claude)
- ✅ **딥러닝 가격 예측** (LSTM, CNN, Transformer)
- ✅ **모델 성능 추적** 및 적응형 선택

### 주문 실행
- ✅ **TWAP, VWAP 알고리즘**
- ✅ **Iceberg 주문** (대량 주문 숨김)
- ✅ **Adaptive 실행** (시장 적응형)
- ✅ **슬리피지 최적화**

### 리스크 관리
- ✅ **VaR 계산** (Historical, Parametric, Monte Carlo)
- ✅ **Sharpe/Sortino Ratio**
- ✅ **Maximum Drawdown 추적**
- ✅ **Monte Carlo 시뮬레이션**
- ✅ **포트폴리오 리스크 분석**

### 대시보드
- ✅ **TradingView 스타일 차트**
- ✅ **실시간 AI 인사이트**
- ✅ **성과 분석 대시보드**
- ✅ **포트폴리오 시각화**
- ✅ **Bloomberg Terminal 디자인**

### 백테스팅
- ✅ **전문가급 백테스팅 엔진**
- ✅ **현실적 실행 시뮬레이션**
- ✅ **상세 성과 분석**
- ✅ **거래별 추적**

---

## 📊 벤치마크 비교

| 기능 | 업그레이드 전 | 업그레이드 후 |
|------|-------------|-------------|
| AI 모델 | 1개 (Gemini) | 3개 (Gemini + GPT-4 + Claude) |
| 가격 예측 | ❌ | ✅ LSTM/CNN/Transformer |
| 주문 알고리즘 | 기본 | TWAP/VWAP/Iceberg/Adaptive |
| 리스크 분석 | 기본 | VaR/Monte Carlo/Sharpe |
| 대시보드 | 기본 HTML | TradingView/Bloomberg 스타일 |
| 백테스팅 | ❌ | ✅ Professional Grade |
| 성과 지표 | 5개 | 15개+ |

---

## 🔧 설정 커스터마이징

### AI Ensemble 설정
```python
# ai/ensemble_config.py
ENSEMBLE_CONFIG = {
    'voting_strategy': 'weighted',
    'enable_gpt4': True,
    'enable_claude': True,
    'confidence_threshold': 0.7,
    'min_model_agreement': 2  # 최소 2개 모델 합의
}
```

### 리스크 관리 설정
```python
# strategy/risk_config.py
RISK_CONFIG = {
    'var_confidence': 0.95,
    'max_drawdown_threshold': 0.15,  # 15%
    'position_var_limit': 0.10,      # 포지션당 10%
    'portfolio_var_limit': 0.20      # 전체 20%
}
```

---

## 🆘 문제 해결

### Q: GPT-4 API 에러
```
A: OPENAI_API_KEY가 올바르게 설정되었는지 확인
   GPT-4 API 접근 권한 확인
```

### Q: TensorFlow 설치 오류
```
A: Python 3.8+ 버전 사용 확인
   pip install --upgrade tensorflow
```

### Q: 대시보드가 로드되지 않음
```
A: Flask 서버가 정상 실행 중인지 확인
   방화벽/포트 설정 확인
```

---

## 📚 추가 자료

- [TradingView Advanced Features](https://www.tradingview.com)
- [QuantConnect Documentation](https://www.quantconnect.com/docs)
- [Bloomberg Terminal Guide](https://www.bloomberg.com/professional/product/bloomberg-terminal/)

---

## 🎯 다음 버전 예정 기능

- [ ] 감성 분석 (뉴스, 소셜미디어)
- [ ] 차트 패턴 인식 (헤드앤숄더, 삼각형 등)
- [ ] 강화학습 기반 전략 최적화
- [ ] 멀티 전략 포트폴리오 매니저
- [ ] 실시간 알림 시스템

---

## 📄 라이선스

이 프로젝트는 개인 투자 용도로 제작되었습니다.

---

**업그레이드 완료! 🎉**

이제 세계 최고 수준의 AI 자동매매 시스템을 사용할 수 있습니다!
