# 📊 Scoring System 간소화 가이드

## ❌ 현재 문제

**10가지 항목 중 6개가 0점**
- 체결 강도: 데이터 없음
- 증권사 활동: 데이터 없음
- 프로그램 매매: 데이터 없음
- 테마/뉴스: API 없음
- 기관 매수세: 데이터는 있지만 기준 미달로 0점
- 매수 호가 강도: 데이터는 있지만 기준 미달로 0점

**결과:**
- 440점 만점이지만 실질적으로 200점만 작동
- AI가 받는 정보에 0점 항목이 너무 많아 혼란

---

## ✅ 해결 방안

### Option 1: 단순 제거 (추천)
```python
# strategy/scoring_system.py 수정

class ScoringResult:
    max_score: float = 280.0  # 440 → 280

    # 제거할 필드
    # execution_intensity_score
    # broker_activity_score
    # program_trading_score
    # theme_news_score

def calculate_score(self, stock_data):
    # 작동하는 6개만 계산
    result.volume_surge_score = self._score_volume_surge(stock_data)  # 60점
    result.price_momentum_score = self._score_price_momentum(stock_data)  # 60점
    result.institutional_buying_score = self._score_institutional_buying(stock_data)  # 60점
    result.bid_strength_score = self._score_bid_strength(stock_data)  # 40점
    result.technical_indicators_score = self._score_technical_indicators(stock_data)  # 40점
    result.volatility_pattern_score = self._score_volatility_pattern(stock_data)  # 20점

    # 총점 280점
    result.total_score = sum of 6 items
```

### Option 2: API 추가 후 활성화 (장기)
```python
# 1. 키움 API에서 추가 데이터 받아오기

# 체결 강도
def get_execution_data(stock_code):
    """매수/매도 체결량으로 체결 강도 계산"""
    response = client.request(
        api_id="DOSK_XXXX",  # 체결 데이터 API
        body={"stock_code": stock_code}
    )
    buy_volume = response['buy_volume']
    sell_volume = response['sell_volume']
    execution_intensity = (buy_volume / (buy_volume + sell_volume)) * 200
    return execution_intensity

# 증권사 활동
def get_broker_data(stock_code):
    """거래원 매매 데이터"""
    response = client.request(
        api_id="주식거래원요청",
        body={"stock_code": stock_code}
    )
    # 상위 증권사 매수 개수 카운트
    return top_broker_buy_count

# 프로그램 매매
def get_program_trading(stock_code):
    """프로그램 매매 추이"""
    response = client.request(
        api_id="종목시간별프로그램매매추이요청",
        body={"stock_code": stock_code}
    )
    return program_net_buy
```

---

## 🎯 즉시 적용 가능한 수정

### 1. AI 프롬프트에서 0점 항목 숨기기
```python
# ai/gemini_analyzer.py

# 10가지 세부 점수 → 0점이 아닌 것만 표시
score_breakdown_detailed = "\n".join([
    f"  {k}: {v:.1f}점"
    for k, v in breakdown.items()
    if v > 0  # 0점 항목 제외
])
```

### 2. main.py 출력 개선
```python
# main.py

# 상위 5개 후보 출력 시 0점 항목 제외
breakdown_parts = []
if score_result.volume_surge_score > 0:
    breakdown_parts.append(f"거래량:{score_result.volume_surge_score:.0f}")
if score_result.price_momentum_score > 0:
    breakdown_parts.append(f"가격:{score_result.price_momentum_score:.0f}")
# ... 0점이 아닌 것만 추가
```

### 3. scoring_system.py 주석 처리
```python
# 5. 체결 강도 (40점) - TODO: API 추가 필요
# result.execution_intensity_score = 0.0

# 6. 증권사 활동 (40점) - TODO: API 추가 필요
# result.broker_activity_score = 0.0

# 7. 프로그램 매매 (40점) - TODO: API 추가 필요
# result.program_trading_score = 0.0

# 9. 테마/뉴스 (40점) - API 제공 안 함
# result.theme_news_score = 0.0

# 실제 작동하는 6개만 계산
result.total_score = (
    result.volume_surge_score +          # 60점
    result.price_momentum_score +        # 60점
    result.institutional_buying_score +  # 60점
    result.bid_strength_score +          # 40점
    result.technical_indicators_score +  # 40점
    result.volatility_pattern_score      # 20점
    # 총 280점
)

result.max_score = 280.0  # 440 → 280
```

---

## 📝 수정 체크리스트

- [ ] `strategy/scoring_system.py` - ScoringResult.max_score = 280
- [ ] `strategy/scoring_system.py` - calculate_score() 메서드 수정
- [ ] `strategy/scoring_system.py` - 0점 항목 주석 처리
- [ ] `ai/gemini_analyzer.py` - 0점 항목 필터링
- [ ] `main.py` - 매수 조건 임계값 조정 (300 → 200)
- [ ] `main.py` - 출력 시 0점 항목 제외

---

## 🚀 향후 개선 방향

1. **단기** (즉시): 0점 항목 숨기기 + 만점 280점으로 조정
2. **중기** (1주): 키움 API 문서 확인 후 추가 데이터 구현
3. **장기** (1개월): REST API 외에 WebSocket으로 실시간 데이터 수신

---

## 💡 키움 API 조사 필요

다음 API들이 제공되는지 확인 필요:
- ✅ 프로그램 매매: `종목시간별프로그램매매추이요청`
- ✅ 거래원: `주식거래원요청`
- ❓ 체결 강도: 매수/매도 체결량 API 확인 필요
- ❌ 테마/뉴스: 별도 API 필요 (뉴스 제공사 연동)
