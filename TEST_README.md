# 대시보드 이슈 원클릭 테스트

## 🚀 빠른 시작 (3초)

### 방법 1: Python 스크립트

```bash
python test_dashboard.py
```

### 방법 2: Bash 스크립트

```bash
./test.sh
```

### 방법 3: 전체 경로

```bash
cd /home/user/autotrade
python3 test_dashboard.py
```

## 📊 테스트 항목

### ✅ 자동으로 테스트되는 것들

1. **계좌 잔고 계산**
   - ❌ 기존: `ord_alow_amt` (인출가능액) 사용
   - ✅ 수정: `dps_amt - pchs_amt` (실제 사용가능액)
   - 여러 접근법 비교 및 결과 표시

2. **NXT 시장가격 조회**
   - 현재 시간 체크 (정규시장 / NXT 시간)
   - 삼성전자, SK하이닉스 현재가 조회
   - 여러 소스 Fallback 테스트

3. **AI 스캐닝 연동**
   - scanner_pipeline 결과 확인
   - Fast/Deep/AI Scan 카운트
   - (main.py 실행 중일 때만 작동)

## 📋 출력 예시

```
🚀 대시보드 이슈 원클릭 테스트
================================================================================

🔧 API 초기화 중...
✅ API 초기화 완료

================================================================================
📊 테스트 1: 계좌 잔고 계산
================================================================================
📍 예수금 조회 중...
📍 보유종목 조회 중...
📍 계좌 잔고 계산 중...

✅ [접근법 1] 예수금 - 구매원가 (추천)
   예수금: 10,000,000원
   구매원가: 3,000,000원
   💰 실제 사용가능액: 7,000,000원
   총 자산: 13,500,000원
   보유주식: 3,500,000원
   손익: +500,000원 (+16.67%)

✅ [접근법 2] 수동 계산
   💰 실제 사용가능액: 7,000,000원

⚠️  [기존 방식] 인출가능액 사용
   인출가능액: 6,500,000원
   차이: +500,000원

================================================================================
💰 테스트 2: NXT 시장가격 조회
================================================================================
📍 현재 시간 정보:
   정규시장 시간: 예
   NXT 거래시간: 아니오

📍 삼성전자 (005930) 가격 조회 중...
✅ 가격 조회 성공
   💰 현재가: 73,500원
   출처: market_api
   시도한 소스: market_api

📍 SK하이닉스 (000660) 가격 조회 중...
✅ 가격 조회 성공
   💰 현재가: 142,000원
   출처: market_api
   시도한 소스: market_api

✅ 2/2개 종목 가격 조회 성공

================================================================================
🤖 테스트 3: AI 스캐닝 종목 연동
================================================================================
⚠️  이 테스트는 main.py가 실행 중일 때만 작동합니다.

봇 실행 후 다음 명령으로 테스트하세요:
  python -c "from tests.manual_tests.run_dashboard_tests import quick_test; import main; quick_test(main.bot)"

================================================================================
📊 테스트 결과 요약
================================================================================

  ✅ 성공: account_balance
  ✅ 성공: nxt_price
  ❌ 실패: ai_scanning

총 2/3개 테스트 성공

⚠️  일부 테스트 실패

해결 방법:
  - API 키 확인: config/config.yaml
  - 네트워크 연결 확인
  - 상세 로그 확인
```

## 🔧 문제 해결

### API 초기화 실패

```
❌ API 초기화 실패
```

**해결:**
1. `config/config.yaml` 파일 확인
2. API 키 설정 확인
3. 계좌번호 확인

### 예수금 조회 실패

```
❌ 예수금 조회 실패
```

**해결:**
1. 키움증권 API 서버 상태 확인
2. 네트워크 연결 확인
3. API 권한 확인

### NXT 가격 조회 실패

```
❌ 가격 조회 실패
시도한 소스: market_api, holdings, previous_close
```

**해결:**
1. 장 시간 확인 (09:00-15:30 또는 16:00-18:00)
2. 종목코드 확인
3. API 응답 확인

### AI 스캐닝 테스트 스킵

```
⚠️  main 모듈이 로드되지 않았습니다.
```

**해결:**
1. `main.py` 실행 후 테스트
2. 또는 봇 실행 중에 별도 터미널에서:
   ```python
   python -c "from tests.manual_tests.run_dashboard_tests import quick_test; import main; quick_test(main.bot)"
   ```

## 📁 관련 파일

- `test_dashboard.py` - 원클릭 테스트 스크립트
- `test.sh` - Bash 래퍼 스크립트
- `tests/manual_tests/test_dashboard_issues.py` - 통합 테스트
- `tests/manual_tests/patches/` - 수정 패치 파일들
- `tests/manual_tests/README_DASHBOARD_FIXES.md` - 상세 가이드

## 🎯 다음 단계

### 1. 테스트 성공 후

수정 사항을 대시보드에 적용:

```bash
# 상세 가이드 확인
cat tests/manual_tests/README_DASHBOARD_FIXES.md

# 또는
less tests/manual_tests/README_DASHBOARD_FIXES.md
```

### 2. 대시보드 코드 수정

`dashboard/app_apple.py` 파일 수정:

#### 계좌 잔고 (라인 233)
```python
# 기존
cash = int(deposit.get('ord_alow_amt', 0))

# 수정
deposit_amount = int(deposit.get('dps_amt', 0))
total_purchase_cost = sum(int(h.get('pchs_amt', 0)) for h in holdings)
cash = deposit_amount - total_purchase_cost
```

#### NXT 가격 조회
```python
from tests.manual_tests.patches.fix_nxt_price import MarketAPIExtended

market_api_ext = MarketAPIExtended(bot.market_api, bot.account_api)
price_info = market_api_ext.get_current_price_with_source(stock_code)
current_price = price_info['price']
```

#### AI 스캐닝 (라인 186)
```python
from tests.manual_tests.patches.fix_ai_scanning import get_scanning_info

scanning_info = get_scanning_info(bot_instance, method='combined')
```

### 3. 검증

대시보드 접속하여 수정 사항 확인:
- 계좌 현금 정확한지 확인
- NXT 시간에 현재가 조회되는지 확인
- AI 스캐닝 종목 수가 표시되는지 확인

## 💡 팁

### 빠른 테스트 (main.py 실행 중)

Python 콘솔에서:

```python
from tests.manual_tests.run_dashboard_tests import quick_test
quick_test(bot)
```

### 개별 테스트

```python
# 계좌 잔고만
from tests.manual_tests.patches.fix_account_balance import AccountBalanceFix
deposit = bot.account_api.get_deposit()
holdings = bot.account_api.get_holdings()
result = AccountBalanceFix.approach_1_deposit_minus_purchase(deposit, holdings)
print(f"사용가능액: {result['cash']:,}원")

# NXT 가격만
from tests.manual_tests.patches.fix_nxt_price import MarketAPIExtended
market_api_ext = MarketAPIExtended(bot.market_api, bot.account_api)
price_info = market_api_ext.get_current_price_with_source('005930')
print(f"삼성전자: {price_info['price']:,}원")

# AI 스캐닝만
from tests.manual_tests.patches.fix_ai_scanning import get_scanning_info
info = get_scanning_info(bot, method='combined')
print(f"스캐닝: {info['fast_scan']['count']}개")
```

## 📞 문의

문제가 계속되면:
1. 로그 확인: `logs/` 디렉토리
2. 이슈 등록: GitHub Issues
3. 상세 가이드: `tests/manual_tests/README_DASHBOARD_FIXES.md`
