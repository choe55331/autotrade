# 전체 코드 검토 및 개선 사항 리스트

## 📋 작업 완료 현황 (오늘)

### ✅ 완료된 작업

1. **가상매매 대시보드 수정**
   - 수익률/승률 100배 오류 수정 (total_pnl_rate, win_rate 이미 percentage)
   - 자산 표시 수정 (current_cash → total_value)
   - 포지션 상세 표시 기능 추가 (클릭 시 확장)

2. **NXT 시간대 지원 함수 추가**
   - `is_nxt_hours()`: 08:00-09:00, 15:30-20:00 판별
   - `is_any_trading_hours()`: 전체 거래 시간 확인
   - `utils/trading_date.py` 업데이트

3. **NXT 현재가 조회**
   - ✅ 작동 확인 (63.3% 성공률)
   - 기본 ka10003 API가 NXT 시간에도 정상 작동
   - 수정 불필요

4. **NXT 주문 코드 발견**
   - ✅ 정확한 trde_tp 코드 확인:
     - `61`: 장시작전시간외 (08:00-09:00)
     - `62`: 시간외단일가
     - `81`: 장마감후시간외 (15:30-20:00) ⭐
   - ✅ 핵심 발견: `ord_uv=""` (시간외종가는 가격 입력 안 함)

---

## 🔴 긴급 수정 필요 (내일 첫 테스트 전 필수)

### 1. api/order.py 수정 (최우선! ⚠️)

**파일**: `api/order.py` Line 107-116

**현재 코드 (문제)**:
```python
# ord_uv(주문단가): 시장가(3)만 빈 문자열, 나머지는 가격 지정
if trde_tp == '3':
    # 시장가만 빈 문자열
    ord_uv_value = ""
else:
    # 나머지는 모두 가격 지정
    ord_uv_value = str(price)
```

**수정 코드** (✅ 정답):
```python
# ord_uv(주문단가): 시장가(3)와 시간외종가(81)는 빈 문자열
if trde_tp == '3':
    # 시장가: 가격 지정 안 함
    ord_uv_value = ""
    logger.info(f"⚠️ 시장가 주문: 가격 지정 없음")
elif trde_tp == '81':
    # 시간외종가: 가격 지정 안 함 (종가로 자동 체결)
    ord_uv_value = ""
    logger.info(f"⚠️ 시간외종가 주문: 장 마감 종가로 자동 체결")
else:
    # 나머지는 가격 지정
    ord_uv_value = str(price)
```

**이유**: 테스트 결과 `[2000](571357:시간외종가 주문시에는 단가를 입력하지 않습니다)` 오류 발생

**영향도**: 🔴 Critical - NXT 시간 주문 불가

---

### 2. main.py 매수 로직 수정

**파일**: `main.py` Line 1223-1228

**현재 코드 (문제)**:
```python
# 주문 유형 결정 (NXT 프리/애프터마켓에서는 지정가만 가능)
order_type = '00'  # 기본: 지정가
```

**수정 코드**:
```python
# 주문 유형 결정 (시간대별)
from utils.trading_date import is_nxt_hours

if is_nxt_hours():
    # NXT 시간대
    now = datetime.now()
    if now.hour == 8:
        # 프리마켓 (08:00-09:00)
        order_type = '61'  # 장시작전시간외
        logger.info("📌 프리마켓 주문: 장시작전시간외(61)")
    else:
        # 애프터마켓 (15:30-20:00)
        order_type = '81'  # 장마감후시간외
        logger.info("📌 애프터마켓 주문: 장마감후시간외(81) - 종가로 체결")
else:
    # 정규장 (09:00-15:30)
    order_type = '0'  # 보통(지정가)
    logger.info("📌 정규장 주문: 보통 지정가(0)")
```

**이유**: NXT 시간대에 맞는 order_type 자동 선택 필요

**영향도**: 🔴 Critical - NXT 자동매매 불가

---

### 3. api/order.py 매도 로직 동일 수정

**파일**: `api/order.py` Line 200+ (매도 함수)

매도 함수도 동일한 로직 적용 필요:
- trde_tp=81일 때 ord_uv=""
- 시간대별 order_type 자동 선택

**영향도**: 🟡 High - NXT 시간 매도 불가

---

## 🟡 보완 필요 (중요도 높음)

### 4. 대시보드 API 엔드포인트 추가

**현재 상태**:
- `/api/virtual_trading/account/<strategy_name>` 존재
- 하지만 `/api/virtual_trading/trades` 미완성

**필요 작업**:
```python
# dashboard/app_apple.py
@app.route('/api/virtual_trading/trades')
def get_virtual_trading_trades():
    """가상매매 거래 기록"""
    try:
        if bot_instance and hasattr(bot_instance, 'virtual_trader'):
            virtual_trader = bot_instance.virtual_trader

            # 모든 전략의 거래 기록 수집
            all_trades = []
            for strategy_name, account in virtual_trader.accounts.items():
                for trade in account.trade_history[-20:]:  # 최근 20건
                    trade_data = trade.copy()
                    trade_data['strategy'] = strategy_name
                    all_trades.append(trade_data)

            # 시간순 정렬
            all_trades.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

            return jsonify({
                'success': True,
                'trades': all_trades[:20]  # 최근 20건만
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
```

**영향도**: 🟡 Medium - 대시보드 거래 기록 표시 안 됨

---

### 5. NXT 시간대 가격 검증

**현재**: current_price를 그대로 사용

**개선**:
```python
# main.py _execute_buy()에 추가
if is_nxt_hours() and order_type == '81':
    # 시간외종가 주문은 가격이 무시됨
    logger.info(f"📍 시간외종가 주문: 지정 가격 {current_price:,}원은 무시되고 종가로 체결됩니다")
    # price는 로그 기록용으로만 사용됨
```

**영향도**: 🟢 Low - 사용자 혼란 방지용

---

### 6. 주문 실패 시 상세 로깅

**현재**: 기본 오류 메시지만 출력

**개선**:
```python
# api/order.py
if result and result.get('return_code') != 0:
    error_code = result.get('return_code')
    error_msg = result.get('return_msg', '알 수 없는 오류')

    logger.error(f"❌ 매수 주문 실패")
    logger.error(f"   오류 코드: {error_code}")
    logger.error(f"   오류 메시지: {error_msg}")
    logger.error(f"   요청 파라미터:")
    logger.error(f"     - dmst_stex_tp: {dmst_stex_tp}")
    logger.error(f"     - stk_cd: {stock_code}")
    logger.error(f"     - ord_qty: {quantity}")
    logger.error(f"     - ord_uv: {ord_uv_value}")
    logger.error(f"     - trde_tp: {trde_tp}")

    # 오류별 해결 방법 제시
    if error_code == 20:
        if '571357' in error_msg:
            logger.error(f"   💡 해결: trde_tp=81은 ord_uv=\"\" 필요")
        elif '505217' in error_msg:
            logger.error(f"   💡 해결: 장 종료 - NXT trde_tp 사용 필요")
        elif '407022' in error_msg:
            logger.error(f"   💡 해결: 주문 종류 불가 - dmst_stex_tp/trde_tp 조합 확인")
```

**영향도**: 🟢 Low - 디버깅 편의성

---

## 🟢 개선 권장 (선택사항)

### 7. 설정 파일에 NXT 설정 추가

**파일**: `config/config.example.yaml`

```yaml
trading:
  # 기존 설정...

  # NXT 시간외 거래 설정
  nxt:
    enabled: true  # NXT 거래 활성화
    pre_market:
      enabled: true  # 프리마켓 (08:00-09:00)
      order_type: '61'  # 장시작전시간외
    after_market:
      enabled: true  # 애프터마켓 (15:30-20:00)
      order_type: '81'  # 장마감후시간외 (종가)
```

**영향도**: 🟢 Low - 설정 유연성

---

### 8. 테스트 파일 정리

**현재**:
- `test_nxt_comprehensive.py` (0/33 실패)
- `test_nxt_orders_correct.py` (0/6 실패 - 가격 문제)
- `test_nxt_orders_final.py` (미테스트 - 정답 예상)

**권장**:
```
tests/nxt/
├── test_nxt_price.py          # 현재가 조회 테스트
├── test_nxt_orders.py         # 주문 테스트 (최종버전)
└── test_results/              # 결과 저장
    └── YYYYMMDD_HHMMSS.json
```

**영향도**: 🟢 Low - 코드 정리

---

### 9. 가상매매 Win Rate 계산 수정

**파일**: `virtual_trading/virtual_account.py` Line 103-107

**현재**:
```python
def get_win_rate(self) -> float:
    """승률 (%)"""
    if self.total_trades == 0:
        return 0.0
    return (self.winning_trades / self.total_trades) * 100
```

**문제**: 매수만 하고 매도 안 하면 total_trades=0 → 승률 계산 안 됨

**개선**:
```python
def get_win_rate(self) -> float:
    """승률 (%)"""
    completed_trades = self.winning_trades + self.losing_trades
    if completed_trades == 0:
        return 0.0
    return (self.winning_trades / completed_trades) * 100
```

**영향도**: 🟢 Low - 승률 표시 정확도

---

### 10. 대시보드 버전 표시 개선

**현재**: v5.0 (하드코딩)

**개선**:
```python
# dashboard/app_apple.py
DASHBOARD_VERSION = "5.0"
LAST_UPDATED = "2025-11-04"

@app.route('/api/version')
def get_version():
    return jsonify({
        'version': DASHBOARD_VERSION,
        'last_updated': LAST_UPDATED,
        'features': [
            'NXT 시간대 지원',
            '가상매매 3전략',
            '포지션 상세 보기',
            '프로그램 모니터'
        ]
    })
```

**영향도**: 🟢 Low - 정보성

---

## 📊 우선순위 정리

### 🔴 긴급 (내일 오전 필수)

1. **api/order.py Line 107-116** - ord_uv="" 로직 추가
2. **main.py Line 1223-1228** - NXT order_type 자동 선택

→ **예상 작업 시간: 30분**
→ **테스트 필수!**

### 🟡 중요 (이번 주 내)

3. 매도 로직 동일 수정
4. 대시보드 거래 기록 API 완성
5. NXT 가격 검증 로그 추가
6. 주문 실패 상세 로깅

→ **예상 작업 시간: 2시간**

### 🟢 권장 (여유 있을 때)

7. 설정 파일 NXT 섹션 추가
8. 테스트 파일 정리
9. 승률 계산 수정
10. 버전 API 추가

→ **예상 작업 시간: 1시간**

---

## 🧪 내일 테스트 계획

### 오전 8:00-9:00 (프리마켓)

```bash
# 1. 코드 수정 적용 확인
git pull

# 2. 테스트 실행
python test_nxt_orders_final.py
```

**예상 성공 조합**:
- dmst_stex_tp=NXT, trde_tp=61, ord_uv=""

### 오후 15:30-20:00 (애프터마켓)

```bash
python test_nxt_orders_final.py
```

**예상 성공 조합**:
- dmst_stex_tp=NXT, trde_tp=81, ord_uv=""

### 성공 후

1. main.py 재시작
2. 실제 AI 매수 시그널 대기
3. 주문 성공 여부 확인
4. 체결 확인 (키움 HTS)

---

## 📝 체크리스트

### 코드 수정 체크리스트

- [ ] api/order.py - trde_tp=81일 때 ord_uv="" 처리
- [ ] main.py - NXT 시간대별 order_type 자동 선택
- [ ] api/order.py - 매도 로직 동일 수정
- [ ] 로그 레벨 확인 (DEBUG 활성화)
- [ ] 설정 파일 백업

### 테스트 체크리스트

- [ ] 프리마켓 테스트 (08:00-09:00)
- [ ] 애프터마켓 테스트 (15:30-20:00)
- [ ] 주문 체결 확인
- [ ] 로그 파일 확인
- [ ] 대시보드 표시 확인

### 배포 체크리스트

- [ ] 변경 사항 커밋
- [ ] PR 생성
- [ ] 테스트 결과 문서화
- [ ] main 브랜치 머지

---

## 🎯 최종 목표

**내일 테스트 성공 조건**:
1. ✅ NXT 프리마켓 주문 성공 (08:00-09:00)
2. ✅ NXT 애프터마켓 주문 성공 (15:30-20:00)
3. ✅ 실제 AI 매수 시그널에 자동 주문
4. ✅ 주문 체결 확인
5. ✅ 대시보드에 정상 표시

**성공 시**: NXT 시간대 완전 자동화 ✅
**실패 시**: 테스트 결과 분석 및 추가 수정

---

## 📌 참고 문서

- [키움증권 API 문서](kiwoom_docs/주문.md)
- [NXT 테스트 가이드](NXT_TEST_GUIDE.md)
- [정확한 코드](CORRECT_NXT_CODES.md)
- [다음 단계](NEXT_STEPS.md)

---

**생성 시간**: 2025-11-04 19:30
**작성자**: Claude
**상태**: 검토 완료, 수정 대기
