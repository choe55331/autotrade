# 🤖 AI 자기학습/강화학습 아키텍처 제안서

## 📌 현재 시스템 vs 목표 시스템

### 현재 (Rule-based + AI 판단)
```
시장 스캔 → 룰 기반 점수 계산 → AI 최종 판단 → 매수/매도
```
- **한계**: 고정된 룰, 수동 파라미터 조정, 피드백 없음

### 목표 (AI 자기학습/강화학습)
```
환경(시장) ↔ 에이전트(AI) → 행동(매매) → 보상(수익) → 학습 → 정책 개선
```
- **목표**: 자동 파라미터 최적화, 전략 진화, 승률 향상

---

## 🏗️ 제안 아키텍처

### 1. 환경 (Environment)
시장 상태를 나타내는 관찰 공간

```python
class TradingEnvironment:
    """강화학습을 위한 거래 환경"""

    def __init__(self):
        # 상태 공간 (State Space)
        self.state = {
            # 시장 데이터
            'market_condition': {},  # 코스피/코스닥 상태
            'sector_trends': {},     # 업종별 동향
            'volatility_index': 0,   # 변동성 지수

            # 포트폴리오 상태
            'cash_ratio': 0,         # 현금 비율
            'position_count': 0,     # 보유 종목 수
            'total_pnl': 0,          # 누적 손익
            'win_rate': 0,           # 승률

            # 후보 종목 상태
            'candidate_scores': [],  # 후보 종목 점수들
            'candidate_features': [],# 후보 종목 특징들
        }

    def step(self, action):
        """행동 실행 및 다음 상태 반환"""
        # 행동 실행 (매수/매도/대기)
        next_state, reward, done, info = self._execute_action(action)
        return next_state, reward, done, info

    def reset(self):
        """환경 초기화"""
        return self.state
```

### 2. 에이전트 (Agent)
DQN, PPO, A3C 등의 강화학습 알고리즘

```python
class TradingAgent:
    """강화학습 에이전트"""

    def __init__(self, state_dim, action_dim):
        # 신경망 구조
        self.policy_network = PolicyNetwork(state_dim, action_dim)
        self.value_network = ValueNetwork(state_dim)

        # 경험 저장소
        self.replay_buffer = ReplayBuffer(capacity=100000)

        # 학습 하이퍼파라미터
        self.learning_rate = 0.001
        self.gamma = 0.99  # 할인율
        self.epsilon = 1.0  # 탐색률

    def select_action(self, state):
        """정책에 따라 행동 선택"""
        # epsilon-greedy 전략
        if np.random.random() < self.epsilon:
            return self._explore()  # 탐색
        else:
            return self._exploit(state)  # 활용

    def learn(self, batch):
        """배치 학습"""
        # TD 오차 계산
        td_error = self._calculate_td_error(batch)

        # 정책 업데이트
        self._update_policy(td_error)

        # 가치 함수 업데이트
        self._update_value_function(td_error)
```

### 3. 행동 공간 (Action Space)

```python
class ActionSpace:
    """가능한 행동들"""

    ACTIONS = {
        # 매수 관련
        'BUY_AGGRESSIVE': 0,     # 공격적 매수 (높은 비율)
        'BUY_MODERATE': 1,       # 보통 매수
        'BUY_CONSERVATIVE': 2,   # 보수적 매수 (낮은 비율)

        # 파라미터 조정
        'INCREASE_THRESHOLD': 3,  # 진입 기준 상향
        'DECREASE_THRESHOLD': 4,  # 진입 기준 하향
        'ADJUST_POSITION_SIZE': 5,# 포지션 크기 조정

        # 전략 변경
        'SWITCH_STRATEGY': 6,     # 스캔 전략 전환
        'ENABLE_RISK_MODE': 7,    # 리스크 모드 전환

        # 대기
        'HOLD': 8,                # 현 상태 유지
    }
```

### 4. 보상 함수 (Reward Function)

```python
def calculate_reward(state, action, next_state):
    """보상 계산"""
    reward = 0

    # 1. 수익 기반 보상 (주요)
    pnl_change = next_state['total_pnl'] - state['total_pnl']
    reward += pnl_change * 10  # 수익은 높게 가중

    # 2. 승률 기반 보상
    if next_state['win_rate'] > state['win_rate']:
        reward += 50
    elif next_state['win_rate'] < state['win_rate']:
        reward -= 30

    # 3. 리스크 관리 보상
    if next_state['max_drawdown'] < state['max_drawdown']:
        reward += 20  # 낙폭 감소 보상

    # 4. 샤프 비율 개선 보상
    if next_state['sharpe_ratio'] > state['sharpe_ratio']:
        reward += 30

    # 5. 페널티
    if next_state['consecutive_losses'] > 3:
        reward -= 100  # 연속 손실 페널티

    return reward
```

### 5. 가상 매매 시뮬레이터

```python
class VirtualTradingSimulator:
    """가상 예산으로 매매 시뮬레이션"""

    def __init__(self, initial_capital=10_000_000):
        self.virtual_capital = initial_capital
        self.virtual_positions = {}
        self.trade_history = []

    def execute_trade(self, action, stock_data):
        """가상 매매 실행"""
        # 실제 API 호출 없이 로컬에서 시뮬레이션
        result = self._simulate_trade(action, stock_data)

        # 거래 기록
        self.trade_history.append({
            'timestamp': datetime.now(),
            'action': action,
            'result': result,
            'pnl': result['pnl']
        })

        return result

    def get_performance_metrics(self):
        """성과 지표 계산"""
        return {
            'total_pnl': self._calculate_total_pnl(),
            'win_rate': self._calculate_win_rate(),
            'sharpe_ratio': self._calculate_sharpe(),
            'max_drawdown': self._calculate_drawdown(),
            'profit_factor': self._calculate_profit_factor(),
        }
```

---

## 🔄 학습 파이프라인

### Phase 1: 오프라인 학습 (과거 데이터)
```python
# 1. 과거 데이터로 사전 학습
historical_data = load_historical_data('2023-01-01', '2024-12-31')
agent.pretrain(historical_data, episodes=10000)

# 2. 백테스팅으로 검증
backtest_results = backtester.run(agent, historical_data)
print(f"승률: {backtest_results['win_rate']:.2%}")
print(f"샤프 비율: {backtest_results['sharpe_ratio']:.2f}")
```

### Phase 2: 온라인 학습 (실시간 가상 매매)
```python
# 3. 가상 매매로 실시간 학습
for episode in range(1000):
    state = env.reset()
    done = False

    while not done:
        # 행동 선택
        action = agent.select_action(state)

        # 가상 매매 실행
        next_state, reward, done, info = virtual_sim.execute(action)

        # 경험 저장
        agent.replay_buffer.store(state, action, reward, next_state, done)

        # 학습
        if len(agent.replay_buffer) > batch_size:
            batch = agent.replay_buffer.sample(batch_size)
            agent.learn(batch)

        state = next_state

    # 에피소드 종료 후 성과 평가
    metrics = virtual_sim.get_performance_metrics()
    logger.info(f"Episode {episode}: 승률={metrics['win_rate']:.2%}, "
                f"수익률={metrics['total_return']:.2%}")
```

### Phase 3: 실전 배포 (점진적)
```python
# 4. 성과가 좋으면 실제 거래에 일부 적용
if agent.validation_sharpe > 2.0 and agent.validation_win_rate > 0.6:
    # 실제 자본의 10%만 AI 전략에 할당
    live_trader.set_ai_allocation(0.1)
    live_trader.enable_ai_trading(agent)
```

---

## 📊 학습 가능한 요소들

### 1. 시장 탐색 조건
```python
# AI가 학습하여 최적화
exploration_params = {
    'min_volume': agent.get_optimal_param('min_volume'),
    'min_price_change': agent.get_optimal_param('min_price_change'),
    'market_cap_range': agent.get_optimal_param('market_cap_range'),
    'scan_frequency': agent.get_optimal_param('scan_frequency'),
}
```

### 2. 후보 선별 조건
```python
# AI가 가중치 학습
scoring_weights = {
    'volume_surge': agent.learned_weights['volume_surge'],
    'price_momentum': agent.learned_weights['price_momentum'],
    'institutional_buy': agent.learned_weights['institutional_buy'],
    # ... 다른 지표들
}
```

### 3. 매수 조건
```python
# AI가 임계값 학습
entry_thresholds = {
    'min_score': agent.get_optimal_param('min_score'),
    'min_ai_confidence': agent.get_optimal_param('min_ai_confidence'),
    'max_risk_level': agent.get_optimal_param('max_risk_level'),
}
```

### 4. 포지션 관리
```python
# AI가 포지션 크기 최적화
position_sizing = agent.calculate_optimal_position_size(
    signal_strength=signal_strength,
    market_volatility=volatility,
    portfolio_risk=current_risk,
)
```

### 5. 손익 관리
```python
# AI가 동적으로 조정
stop_loss = agent.get_dynamic_stop_loss(
    entry_price=entry_price,
    volatility=stock_volatility,
    position_size=position_size,
)

take_profit = agent.get_dynamic_take_profit(
    entry_price=entry_price,
    expected_return=expected_return,
    holding_period=holding_period,
)
```

---

## 🛠️ 구현 로드맵

### Step 1: 데이터 수집 및 전처리 (2주)
- [ ] 과거 1년치 시세 데이터 수집
- [ ] 거래 기록 정규화
- [ ] 특징 공학 (feature engineering)
- [ ] 데이터셋 분할 (train/val/test)

### Step 2: 시뮬레이터 구축 (2주)
- [ ] 가상 거래 환경 구현
- [ ] 수수료/슬리피지 모델링
- [ ] 백테스팅 엔진 구현
- [ ] 성과 지표 계산 모듈

### Step 3: RL 에이전트 구현 (3주)
- [ ] DQN/PPO 알고리즘 구현
- [ ] 신경망 아키텍처 설계
- [ ] 리플레이 버퍼 구현
- [ ] 학습 루프 구현

### Step 4: 오프라인 학습 (2주)
- [ ] 과거 데이터로 사전 학습
- [ ] 하이퍼파라미터 튜닝
- [ ] 백테스팅 검증
- [ ] 오버피팅 방지

### Step 5: 온라인 학습 시스템 (2주)
- [ ] 실시간 데이터 파이프라인
- [ ] 온라인 학습 루프 구현
- [ ] A/B 테스팅 프레임워크
- [ ] 모니터링 대시보드

### Step 6: 실전 배포 (1주)
- [ ] 리스크 관리 레이어 추가
- [ ] 점진적 배포 (10% → 30% → 50%)
- [ ] 실시간 모니터링 및 알림
- [ ] 비상 정지 메커니즘

**총 예상 기간: 12주 (약 3개월)**

---

## ⚠️ 주의사항

### 1. 데이터 품질
- 과거 데이터가 미래를 보장하지 않음
- 과적합 (overfitting) 위험
- 시장 체제 변화 (market regime change)

### 2. 계산 리소스
- GPU 필요 (학습 시간 단축)
- 대량의 메모리 (리플레이 버퍼)
- 지속적인 학습 (24/7 운영)

### 3. 리스크 관리
- AI가 학습 중 큰 손실 가능
- 반드시 가상 매매로 충분히 검증
- 실전 배포는 소액부터 시작

### 4. 규제 및 윤리
- 시장 조작으로 오인될 수 있는 패턴 학습 방지
- 불공정거래 규제 준수
- 투명성 및 설명 가능성 (XAI) 고려

---

## 📚 추천 라이브러리

```python
# 강화학습 프레임워크
- stable-baselines3  # RL 알고리즘 구현체
- ray[rllib]         # 분산 RL
- tensorflow/pytorch # 딥러닝

# 백테스팅
- backtrader        # 전략 백테스팅
- zipline           # Quantopian 백테스팅 엔진
- vectorbt          # 고성능 백테스팅

# 데이터 처리
- pandas            # 데이터 조작
- numpy             # 수치 계산
- ta-lib            # 기술적 지표
```

---

## 🎯 성공 지표 (KPI)

### 가상 매매 단계
- 승률 > 60%
- 샤프 비율 > 2.0
- 최대 낙폭 < 15%
- 수익률 > 시장 수익률 + 5%

### 실전 배포 기준
- 가상 매매 3개월 이상 안정적 수익
- 다양한 시장 환경에서 검증 완료
- 리스크 관리 메커니즘 완벽 작동
- 사람보다 일관성 있는 성과

---

## 💡 결론

현재 시스템은 **Rule-based + AI 판단** 구조로, 기본적인 자동매매는 가능하지만 **자기학습/최적화는 불가능**합니다.

**AI 강화학습 시스템**을 구축하려면:
1. ✅ **단기** (1-2주): 현재 시스템 데이터 품질 향상 (이번 작업)
2. 🔄 **중기** (3개월): 가상 매매 + 강화학습 파이프라인 구축
3. 🚀 **장기** (6개월~): 실전 배포 + 지속적 학습

**현실적 조언:**
- 먼저 현재 시스템으로 실전 경험 축적 (데이터 수집)
- 동시에 가상 매매 시뮬레이터 구축
- 충분한 데이터가 쌓이면 강화학습 시작
- 성과가 검증되면 점진적 실전 배포

**투자 대비 효과:**
- 개발 비용: 높음 (3-6개월, 전문 인력)
- 기대 효과: 중~상 (시장 상황에 따라 다름)
- 리스크: 높음 (학습 중 손실, 과적합)

지금은 **현재 시스템 최적화 + 데이터 수집**에 집중하고,
충분한 실전 데이터가 쌓이면 강화학습 도입을 권장합니다.
