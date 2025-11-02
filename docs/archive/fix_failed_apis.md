# 실패한 API 수정 계획

## 1. ⚠️ 쉽게 고칠 수 있는 것들 (4개)

### kt00016 (일별계좌수익률상세현황요청)
- **문제**: `fr_dt` 필수 파라미터 누락
- **해결**: path="acnt", body={"strt_dt": "20251018", "end_dt": "20251101", "inqr_tp": "1"}

### ka10006 (주식시분요청)
- **문제**: URI 오류 - `/api/dostk/stkinfo`에서 지원 안 함
- **해결**: path="stkinfo", body={"stk_cd": "000660"}

### ka10009 (주식기관요청)
- **문제**: URI 오류
- **해결**: path="stkinfo", body={"stk_cd": "000660"}

### ka10040 (당일주요거래원요청)
- **문제**: URI 오류
- **해결**: path="stkinfo", body={"stk_cd": "000660"}

## 2. ❌ 복잡한 파라미터 필요 (9개)

### kt00010 (주문인출가능금액요청)
- path="acnt"
- body={"stk_cd": "005930", "trde_tp": "2", "uv": "480000", "ord_tp": "01"}

### ka10054 (변동성완화장치)
- path="stkinfo"
- body={"mrkt_tp": "101", "bf_mkrt_tp": "0", "motn_tp": "0", "skip_stk": "000000000", "trde_qty_tp": "1", "min_trde_qty": "1", "max_trde_qty": "999999999999", "trde_prica_tp": "0", "min_trde_prica": "0", "max_trde_prica": "9999999999", "motn_drc": "0", "stex_tp": "3", "stk_cd": "0001"}

### ka10064 (장중투자자별매매차트요청)
- path="chart"
- body={"mrkt_tp": "001", "amt_qty_tp": "1", "trde_tp": "0", "stk_cd": "005930"}

### ka10021 (호가잔량급증요청)
- path="rkinfo"
- body={"mrkt_tp": "001", "trde_tp": "1", "sort_tp": "2", "trde_qty_tp": "100", "stk_cnd": "1", "tm_tp": "30", "stex_tp": "3", "stk_cd": "005930"}

### ka90001 (테마그룹별요청)
- path="thme"
- body={"qry_tp": "0", "thema_nm": "2차전지", "date_tp": "10", "flu_pl_amt_tp": "1", "stex_tp": "1"}

### ka10102 (회원사 리스트)
- path="stkinfo"
- body={} (빈 body 정상)

### ka30003 (ELWLP보유일별추이요청)
- path="elw"
- body={"bsis_aset_cd": "201", "base_dt": "20251031", "stk_cd": ""}

### ka30004 (ELW괴리율요청)
- path="elw"
- body={"isscomp_cd": "000000000000", "bsis_aset_cd": "201", "rght_tp": "002", "lpcd": "000000000000", "trde_end_elwskip": "1"}

### ka30005 (ELW조건검색요청)
- path="elw"
- body={"isscomp_cd": "000000000000", "bsis_aset_cd": "201", "rght_tp": "2", "lpcd": "000000000000", "sort_tp": "5"}

### ka10010 (업종프로그램요청)
- path="sect"
- body={"stk_cd": "005930", "inds_cd": "0001", "upjong_cd": "001", "grp_tp": "0"}

## 해결 방법

successful_apis.json을 직접 사용하여 API를 호출하는 테스트 스크립트를 만들어야 합니다.
기존 `test_all_apis_cli.py`가 이미 이 방식을 사용하고 있을 가능성이 높습니다.
