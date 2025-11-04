# KB증권 데이터 수신 이슈 조사

## 문제 설명

대시보드 및 스캐너에서 KB증권 매매 데이터가 일관되게 `net_qty=0` (변동없음)으로 표시됨

```
KB증권: net_qty=0주 - 변동없음
교보증권: net_qty=5,234주 - 순매수  ✓
미래에셋: net_qty=3,122주 - 순매수  ✓
NH투자: net_qty=1,523주 - 순매수  ✓
삼성증권: net_qty=2,831주 - 순매수  ✓
```

다른 증권사들은 정상적으로 데이터를 받아오는데, KB증권만 0으로 표시됩니다.

---

## API 정보

**API ID**: `ka10078` (증권사별 종목매매동향)
**위치**: `api/market.py:1585-1695` (`get_securities_firm_trading` 메서드)
**사용 위치**: `research/scanner_pipeline.py:357` (Deep Scan 단계)

### API 파라미터

```python
{
    "mmcm_cd": "040",      # 회원사코드 (KB증권)
    "stk_cd": "005930",    # 종목코드 (예: 삼성전자)
    "strt_dt": "20251101", # 시작일
    "end_dt": "20251104"   # 종료일
}
```

### 응답 예상 구조

```json
{
    "return_code": 0,
    "return_msg": "정상 처리되었습니다",
    "<data_key>": [
        {
            "dt": "20251104",
            "buy_qty": "10000",
            "sell_qty": "5000",
            "netprps_qty": "5000"  # 순매수량
        }
    ]
}
```

---

## 가능한 원인

### 1. 회원사 코드 오류 (가능성: 중)

**가설**: KB증권의 회원사 코드가 "040"이 아닐 수 있음

**근거**:
- 코드베이스 전체에서 "040"을 KB증권으로 사용 중
- `research/scanner_pipeline.py:345`
- `test_data_collection_comprehensive.py` 등

**확인 방법**:
1. 키움증권 API 문서에서 공식 회원사 코드표 확인
2. 다른 코드 시도 (예: "KB", "0040", "40" 등)
3. 키움증권 고객센터 문의

**다른 증권사 코드 (참고)**:
- 001: 한국투자증권
- 003: 미래에셋증권
- 005: 삼성증권
- 034: NH투자증권
- 039: 교보증권
- 088: 신한투자증권

### 2. API 데이터 제공 제한 (가능성: 중)

**가설**: 키움증권 API가 KB증권 데이터를 제공하지 않음

**근거**:
- KB증권만 일관되게 0 반환
- API 호출 자체는 성공 (return_code=0)
- 빈 데이터 리스트 반환 가능성

**확인 방법**:
1. Raw API 응답 확인 (디버깅 로그 활성화)
2. 키움증권 API 지원 증권사 목록 확인
3. 다른 종목으로 테스트 (삼성전자 외)

### 3. 실제 거래 부재 (가능성: 낮음)

**가설**: KB증권이 실제로 해당 종목을 거래하지 않음

**근거**:
- 모든 종목에서 일관되게 0 표시
- 다른 증권사는 활발히 거래 중

**반증**:
- KB증권은 대형 증권사로 삼성전자 등 주요 종목 거래 불가능성 낮음
- 여러 날짜, 여러 종목에서 모두 0일 가능성 낮음

### 4. API 응답 파싱 문제 (가능성: 낮음)

**가설**: KB증권 데이터만 다른 형식으로 제공됨

**근거**:
- `api/market.py:1658-1683`에서 데이터 파싱
- 다른 증권사와 동일한 로직 사용

**확인 방법**:
```python
# api/market.py:1640-1656 (디버깅 코드가 이미 존재)
if not hasattr(self, '_firm_trading_debug_shown'):
    print(f"\n[증권사 API 디버깅]")
    print(f"  response keys: {list(response.keys())}")
    print(f"  data_keys: {data_keys}")
    for key in data_keys[:3]:
        val = response.get(key)
        if isinstance(val, list):
            print(f"  {key} = list({len(val)} items)")
            if len(val) > 0:
                print(f"  first item: {val[0]}")
```

---

## 디버깅 방법

### 방법 1: Raw API 응답 확인

1. `api/market.py:1640` 디버깅 코드 강제 활성화:
   ```python
   # 항상 출력되도록 수정 (테스트용)
   if firm_code == "040":  # KB증권일 때만
       print(f"\n[KB증권 API 디버깅]")
       print(f"  전체 응답: {json.dumps(response, indent=2, ensure_ascii=False)}")
   ```

2. `main.py` 실행 후 로그 확인

3. KB증권 응답과 다른 증권사 응답 비교

### 방법 2: 다양한 종목 테스트

```python
test_stocks = [
    ("005930", "삼성전자"),
    ("000660", "SK하이닉스"),
    ("005380", "현대차"),
    ("035720", "카카오"),
]

for stock_code, stock_name in test_stocks:
    kb_data = market_api.get_securities_firm_trading(
        firm_code="040",
        stock_code=stock_code,
        days=3
    )
    print(f"{stock_name}: {len(kb_data) if kb_data else 0}일 데이터")
```

### 방법 3: 회원사 코드 검증

```python
# 다양한 코드 패턴 시도
possible_codes = [
    "040",   # 현재 사용 중
    "0040",  # 0 패딩
    "40",    # 0 제거
    "KB",    # 문자열
]

for code in possible_codes:
    try:
        data = market_api.get_securities_firm_trading(
            firm_code=code,
            stock_code="005930",
            days=1
        )
        if data and len(data) > 0:
            print(f"✓ 코드 '{code}' 성공!")
    except Exception as e:
        print(f"✗ 코드 '{code}' 실패: {e}")
```

### 방법 4: API 문서 확인

1. 키움증권 개발자 센터 로그인
2. API 문서 > 순위정보 > ka10078 증권사별종목매매동향
3. 회원사코드(mmcm_cd) 필드 설명 확인
4. 예시 요청/응답 확인

---

## 해결 방안

### 단기 해결책

KB증권 데이터를 스캐너에서 제외하고 나머지 4개 증권사만 사용:

```python
# research/scanner_pipeline.py:344
major_firms = [
    # ("040", "KB증권"),  # 일시적으로 비활성화
    ("039", "교보증권"),
    ("001", "한국투자증권"),
    ("003", "미래에셋증권"),
    ("005", "삼성증권"),
    ("034", "NH투자증권"),  # 추가
]
```

### 중기 해결책

1. 키움증권 고객센터 문의하여 정확한 회원사 코드 확인
2. KB증권 데이터가 실제로 제공되지 않으면 다른 증권사로 대체
3. API 문서 업데이트 및 코드 주석 추가

### 장기 해결책

1. 회원사 코드를 동적으로 검증하는 기능 추가
2. API 응답에서 지원되는 회원사 목록 자동 조회
3. 증권사별 데이터 제공 여부를 사전에 체크하는 헬스체크 기능

---

## 관련 파일

### 핵심 파일
- `api/market.py:1585-1695` - get_securities_firm_trading() 메서드
- `research/scanner_pipeline.py:340-386` - 증권사 데이터 수집 로직

### 참고 파일
- `test_data_collection_comprehensive.py:208` - 테스트 코드 예제
- `research/scan_strategies.py:242` - 증권사 데이터 활용 예제

---

## 테스트 계획

1. **디버깅 활성화**: KB증권 raw API 응답 출력
2. **다양한 종목 테스트**: 5개 이상 대형주로 테스트
3. **회원사 코드 검증**: 다양한 코드 패턴 시도
4. **API 문서 확인**: 키움증권 공식 문서 확인
5. **고객센터 문의**: 최종 확인

---

## 현재 상태

- [x] 문제 식별: KB증권만 net_qty=0
- [x] 코드 분석: 회원사 코드 "040" 사용 중
- [ ] Raw API 응답 확인 필요
- [ ] 다양한 종목으로 테스트 필요
- [ ] 회원사 코드 검증 필요
- [ ] API 문서 확인 필요

---

## 결론

KB증권 데이터 수신 문제는 다음 중 하나일 가능성이 높습니다:

1. **회원사 코드 오류**: "040"이 아닌 다른 코드 필요
2. **API 제한**: 키움증권 API가 KB증권 데이터 미제공

**권장 조치**:
1. Raw API 응답 로그 확인 (최우선)
2. 키움증권 API 문서에서 회원사 코드표 확인
3. 필요시 KB증권 제외하고 다른 증권사 추가

**임시 조치**:
- KB증권을 major_firms 리스트에서 제거하고 NH투자증권 추가
- 5개 증권사 중 4개만으로도 충분한 시장 커버리지 확보 가능
