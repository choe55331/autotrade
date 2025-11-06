# 한국 주식 관련 파이썬 라이브러리 가이드

**작성일:** 2025-11-06
**버전:** v6.1
**목적:** 한국 주식 데이터 수집 및 자동매매를 위한 파이썬 라이브러리 종합 가이드

---

## 📊 1. 데이터 수집 라이브러리

### 1.1 FinanceDataReader

**가장 추천** - 국내/해외 금융 데이터를 쉽게 가져오는 라이브러리

```python
# 설치
pip install finance-datareader

# 사용 예시
import FinanceDataReader as fdr

# 국내 주식 (삼성전자)
df = fdr.DataReader('005930', '2024-01-01', '2024-12-31')

# KOSPI 지수
kospi = fdr.DataReader('KS11', '2024-01-01')

# 미국 주식
apple = fdr.DataReader('AAPL', '2024-01-01')
```

**장점:**
- ✅ 간단한 API
- ✅ 국내/해외 주식, 지수, 환율, 암호화폐 지원
- ✅ Yahoo Finance, Naver 금융, KRX 통합
- ✅ 수정주가 또는 비수정주가 선택 가능

**단점:**
- ⚠️ 일부 데이터는 외부 소스 의존 (네트워크 필요)

**데이터 소스:**
- 비수정주가: Yahoo Finance
- 수정주가: KRX, Naver, Yahoo Finance

**공식 문서:**
- https://financedata.github.io/
- https://github.com/FinanceData/FinanceDataReader

---

### 1.2 PyKRX

한국거래소(KRX) 데이터 스크래핑 전문 라이브러리

```python
# 설치
pip install pykrx

# 사용 예시
from pykrx import stock

# 전체 종목 리스트
tickers = stock.get_market_ticker_list("20241106")

# 주가 데이터 (수정주가 옵션)
df = stock.get_market_ohlcv("20240101", "20241231", "005930", adjusted=True)

# 시가총액, PER, PBR 등 기본 정보
fundamental = stock.get_market_fundamental("20241106", market="KOSPI")

# 외국인/기관 순매수
net_buy = stock.get_market_trading_value_by_date("20240101", "20241231", "005930")
```

**장점:**
- ✅ KRX 공식 데이터 직접 스크래핑
- ✅ 시가총액, PER, PBR, 배당수익률 등 기본 분석 데이터
- ✅ 외국인/기관 매매 데이터
- ✅ 수정주가/비수정주가 선택 가능
- ✅ 실시간 크롤링 (API 키 불필요)

**단점:**
- ⚠️ 웹 스크래핑 방식이라 KRX 사이트 변경 시 영향
- ⚠️ 대량 데이터 요청 시 속도 느림

**데이터 소스:**
- 한국거래소(KRX), Naver 금융

**공식 문서:**
- https://github.com/sharebook-kr/pykrx

---

### 1.3 marcap

시가총액 데이터 특화 라이브러리

```python
# 설치
pip install marcap

# 사용 예시
import marcap

# 특정 날짜 전체 종목 시가총액
df = marcap.get_data('2024-11-06')

# 삼성전자 시가총액 추이
samsung = marcap.get_data('2024-01-01', '2024-11-06', code='005930')
```

**장점:**
- ✅ 시가총액 데이터 전문
- ✅ 전체 종목 한 번에 조회

**단점:**
- ⚠️ 제한적인 데이터 (시가총액 중심)

---

### 📊 데이터 라이브러리 비교

| 라이브러리 | 데이터 종류 | 수정주가 | 해외 주식 | 업데이트 | 추천도 |
|-----------|------------|---------|----------|----------|--------|
| **FinanceDataReader** | 주가, 지수, 환율, 암호화폐 | O | O | 활발 | ⭐⭐⭐⭐⭐ |
| **PyKRX** | 주가, 기본분석, 거래 데이터 | O | X | 활발 | ⭐⭐⭐⭐⭐ |
| **marcap** | 시가총액 | X | X | 보통 | ⭐⭐⭐ |

**추천 조합:**
- `FinanceDataReader` (주가 데이터) + `PyKRX` (기본분석 데이터) = 최강 조합 💪

---

## 🤖 2. 자동매매 API 라이브러리 (한국투자증권)

### 2.1 mojito2 ⭐ 가장 인기

대한민국 증권사 통합 REST API 레퍼 모듈

```python
# 설치
pip install mojito2

# 사용 예시
import mojito

# 계좌 로그인
broker = mojito.KoreaInvestment(
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    acc_no="YOUR_ACCOUNT_NO",
    mock=False  # 실전투자/모의투자
)

# 현재가 조회
price = broker.fetch_price("005930")

# 매수 주문
order = broker.create_limit_buy_order(
    symbol="005930",
    price=70000,
    quantity=10
)

# 계좌 잔고 조회
balance = broker.fetch_balance()
```

**장점:**
- ✅ 간단하고 직관적인 API
- ✅ REST API + WebSocket 지원
- ✅ 실전/모의투자 전환 쉬움
- ✅ 활발한 커뮤니티 (sharebook-kr)
- ✅ 한국어 문서 풍부

**단점:**
- ⚠️ 한국투자증권 계좌 필요

**공식 문서:**
- https://github.com/sharebook-kr/mojito
- https://pypi.org/project/mojito2/

**모히토 의미:**
> "돈 벌어서 몰디브가서 모히토 한 잔 하자" 🍹

---

### 2.2 python-kis

한국투자증권 트레이딩 API 강력한 커뮤니티 라이브러리

```python
# 설치
pip install python-kis

# 사용 예시
from pykis import PyKis

# 계정 설정
kis = PyKis(
    appkey="YOUR_APP_KEY",
    appsecret="YOUR_APP_SECRET",
    account="YOUR_ACCOUNT",
    virtual=False  # False=실전, True=모의
)

# 국내/해외 통합 인터페이스
# 국내 주식
domestic = kis.domestic_stock("005930")
price = domestic.get_price()

# 해외 주식 (미국)
overseas = kis.overseas_stock("AAPL")
price = overseas.get_price()
```

**장점:**
- ✅ 국내/해외 API 통합 인터페이스
- ✅ Python 3.11 기준 최신 문법
- ✅ 객체지향 설계
- ✅ 타입 힌트 지원

**단점:**
- ⚠️ 학습 곡선 다소 있음

**공식 문서:**
- https://github.com/Soju06/python-kis
- https://pypi.org/project/python-kis/

---

### 2.3 pykis

한국투자증권 Open Trading API 비공식 래퍼

```python
# 설치
pip install pykis

# 사용 예시 (간단함)
from pykis import Api

# API 초기화
api = Api(
    account="YOUR_ACCOUNT",
    key="YOUR_KEY",
    secret="YOUR_SECRET"
)

# 주문
api.buy("005930", qty=10, price=70000)
```

**장점:**
- ✅ 매우 간단한 API
- ✅ 빠른 시작

**단점:**
- ⚠️ 기능이 상대적으로 제한적

**공식 문서:**
- https://github.com/pjueon/pykis

---

### 🏦 한국투자증권 API 비교

| 라이브러리 | 난이도 | 기능성 | 문서 | 커뮤니티 | 추천도 |
|-----------|--------|--------|------|----------|--------|
| **mojito2** | 쉬움 | 풍부 | ⭐⭐⭐⭐⭐ | 활발 | ⭐⭐⭐⭐⭐ |
| **python-kis** | 보통 | 매우 풍부 | ⭐⭐⭐⭐ | 활발 | ⭐⭐⭐⭐ |
| **pykis** | 매우 쉬움 | 기본 | ⭐⭐⭐ | 보통 | ⭐⭐⭐ |

**추천:**
- 초보자: `mojito2` (가장 쉽고 문서 좋음)
- 고급 사용자: `python-kis` (기능 풍부)

---

## 📈 3. 백테스팅 라이브러리

### 3.1 Backtrader ⭐ 추천

가장 활발하게 유지보수되는 백테스팅 프레임워크

```python
# 설치
pip install backtrader

# 사용 예시
import backtrader as bt

class MyStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(period=20)

    def next(self):
        if self.data.close[0] > self.sma[0]:
            self.buy()
        elif self.data.close[0] < self.sma[0]:
            self.sell()

# 백테스팅 실행
cerebro = bt.Cerebro()
cerebro.addstrategy(MyStrategy)
cerebro.adddata(data)  # FinanceDataReader 데이터 사용 가능
cerebro.run()
cerebro.plot()
```

**장점:**
- ✅ 활발한 유지보수 및 커뮤니티
- ✅ 우수한 시각화
- ✅ 다양한 내장 지표
- ✅ 슬리피지, 수수료 반영
- ✅ 학습 자료 풍부

**단점:**
- ⚠️ 초기 학습 곡선

**공식 문서:**
- https://www.backtrader.com/

---

### 3.2 Zipline

Quantopian 기반 백테스팅 (유지보수 중단)

```python
# 설치
pip install zipline-reloaded  # 커뮤니티 버전

# 사용 예시
from zipline.api import order, record, symbol

def initialize(context):
    context.asset = symbol('AAPL')

def handle_data(context, data):
    order(context.asset, 10)
    record(AAPL=data.current(context.asset, 'price'))
```

**장점:**
- ✅ Quantopian 기반 (많은 예제 존재)

**단점:**
- ❌ 공식 개발 중단 (2020년 Quantopian 폐쇄)
- ❌ 최신 Python 지원 부족
- ❌ 한국 주식 데이터 직접 연동 어려움

**추천:**
- 2025년 기준 **Backtrader 사용 권장**

---

### 3.3 QuantLib

양적 금융 라이브러리 (옵션 가격, 리스크 관리)

```python
# 설치
pip install QuantLib

# 사용 예시 (블랙-숄즈 옵션 가격)
import QuantLib as ql

# 옵션 파라미터
option = ql.EuropeanOption(...)
bs_process = ql.BlackScholesProcess(...)
option.setPricingEngine(ql.AnalyticEuropeanEngine(bs_process))

price = option.NPV()
```

**장점:**
- ✅ 금융 공학 전문 (옵션, 채권, 파생상품)
- ✅ 학술적/전문적 용도

**단점:**
- ⚠️ 일반 주식 백테스팅에는 과도함
- ⚠️ 높은 학습 곡선

**공식 문서:**
- https://www.quantlib.org/

---

### 📊 백테스팅 라이브러리 비교

| 라이브러리 | 유지보수 | 시각화 | 한국주식 | 난이도 | 추천도 |
|-----------|---------|--------|---------|--------|--------|
| **Backtrader** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 보통 | ⭐⭐⭐⭐⭐ |
| **Zipline** | ❌ (중단) | ⭐⭐⭐ | ⭐⭐ | 높음 | ⭐⭐ |
| **QuantLib** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | 매우 높음 | ⭐⭐⭐ (전문가용) |

---

## 🎯 4. 추천 조합 (2025년 기준)

### 🏆 초보자 추천

```python
# 데이터 수집
pip install finance-datareader pykrx

# 자동매매
pip install mojito2

# 백테스팅
pip install backtrader
```

**이유:**
- FinanceDataReader: 가장 쉬운 데이터 수집
- PyKRX: 기본분석 데이터 보완
- mojito2: 가장 쉬운 자동매매
- Backtrader: 활발한 커뮤니티와 좋은 문서

---

### 💪 고급 사용자 추천

```python
# 데이터 수집
pip install finance-datareader pykrx pandas-ta

# 자동매매
pip install python-kis

# 백테스팅
pip install backtrader vectorbt

# 기술적 지표
pip install ta-lib pandas-ta
```

**추가 라이브러리:**
- `pandas-ta`: 150개+ 기술적 지표
- `vectorbt`: 고속 벡터화 백테스팅
- `ta-lib`: C 기반 고속 기술적 지표

---

## 📚 5. 기타 유용한 라이브러리

### 5.1 기술적 지표

```python
# pandas-ta (추천)
pip install pandas-ta

import pandas_ta as ta

df.ta.rsi()
df.ta.macd()
df.ta.bbands()
df.ta.sma(length=20)

# ta (Technical Analysis Library)
pip install ta

from ta.momentum import RSIIndicator
rsi = RSIIndicator(close=df['Close'])
df['rsi'] = rsi.rsi()
```

### 5.2 데이터 분석

```python
# mplfinance (차트 시각화)
pip install mplfinance

import mplfinance as mpf
mpf.plot(df, type='candle', volume=True, style='yahoo')
```

### 5.3 머신러닝

```python
# scikit-learn
pip install scikit-learn

# TensorFlow / PyTorch
pip install tensorflow
pip install torch
```

---

## 🚀 6. AutoTrade Pro에서 사용 중인 라이브러리

현재 프로젝트 (`/home/user/autotrade`)에서 사용 중:

### 데이터 수집
- 자체 구현 KIS API 클라이언트 (`api/client.py`)
- WebSocket 실시간 데이터 (`api/websocket_manager.py`)

### 기술적 분석
- pandas, numpy (기본 계산)
- 자체 구현 지표 (`features/indicators.py`)

### AI 분석
- Google Gemini (`ai/gemini_analyzer.py`)
- Anthropic Claude (`ai/claude_analyzer.py`)
- OpenAI GPT-4 (`ai/gpt4_analyzer.py`)
- Ensemble Voting (`ai/unified_analyzer.py`)

### 백테스팅
- 자체 구현 가상매매 (`virtual_trading/`)
- 12가지 다양한 전략 (`virtual_trading/diverse_strategies.py`)

---

## 💡 7. 시작하기 좋은 튜토리얼

### 한국어 리소스

1. **파이썬으로 배우는 알고리즘 트레이딩** (Wikidocs)
   - https://wikidocs.net/book/110
   - Zipline, Backtrader 예제

2. **퀀트 투자 쿡북** (Wikidocs)
   - https://wikidocs.net/book/226
   - FinanceDataReader, PyKRX 사용법

3. **파이썬으로 배우는 오픈API 트레이딩** (Wikidocs)
   - https://wikidocs.net/book/159
   - 한국투자증권 API 사용법

4. **한국투자증권 공식 개발자센터**
   - https://apiportal.koreainvestment.com/
   - 공식 API 문서

---

## ⚠️ 8. 주의사항

### 한국투자증권 API 사용 시

1. **API 키 발급 필요**
   - KIS Developers 포털에서 신청
   - 실전투자 계좌 또는 모의투자 계좌

2. **요청 제한**
   - 초당 요청 수 제한 있음
   - Rate limiting 구현 필요

3. **거래 시간**
   - 정규장: 09:00 - 15:30
   - 분봉 데이터는 정규장 시간에만 사용 가능

### 데이터 수집 시

1. **웹 스크래핑 라이브러리 (PyKRX)**
   - 과도한 요청 자제
   - 딜레이 추가 권장 (`time.sleep()`)

2. **API 키 보안**
   - `.env` 파일 사용
   - Git에 커밋하지 말 것
   - `python-dotenv` 사용 권장

```python
# 보안 모범 사례
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('KIS_API_KEY')
API_SECRET = os.getenv('KIS_API_SECRET')
```

---

## 📝 9. 결론

### 🎯 2025년 최고의 조합

**데이터 수집:**
- `FinanceDataReader` + `PyKRX`

**자동매매:**
- `mojito2` (초보자) 또는 `python-kis` (고급)

**백테스팅:**
- `Backtrader`

**기술적 지표:**
- `pandas-ta`

---

## 🔗 10. 유용한 링크

### 공식 문서
- FinanceDataReader: https://github.com/FinanceData/FinanceDataReader
- PyKRX: https://github.com/sharebook-kr/pykrx
- mojito2: https://github.com/sharebook-kr/mojito
- python-kis: https://github.com/Soju06/python-kis
- Backtrader: https://www.backtrader.com/

### 커뮤니티
- 한국투자증권 공식 GitHub: https://github.com/koreainvestment/open-trading-api
- Sharebook (주식 자동매매 커뮤니티): https://github.com/sharebook-kr

### 학습 자료
- Wikidocs 알고리즘 트레이딩: https://wikidocs.net/book/110
- Wikidocs 퀀트 투자: https://wikidocs.net/book/226

---

**마지막 업데이트:** 2025-11-06
**기여:** Issues 또는 Pull Requests 환영
**라이센스:** MIT
