# account.py (v2.6 - Fixed ka00198/ka10077, Expanded Variants 500+, Clarified ka40001 251023)
# - CRITICAL FIX: Changed 'gry_tp' to 'qry_tp' for ka00198 based on error log analysis. (PDF Doc shows 'gry_tp', PDF Example shows 'qry_tp'). 
# - CRITICAL FIX: Removed invalid variant for ka10077 (empty stk_cd). (PDF requires stk_cd).
# - Expanded test variants significantly across most APIs (~500+ total) focusing on:
#   - KOSPI/KOSDAQ distinctions.
#   - Various sorting options.
#   - Different date ranges and timeframes.
#   - Common conditions (price, volume, credit).
#   - Testing alternative placeholder codes (ETF, ELW, KOSDAQ stock).
#   - Added more descriptive comments for variant groups.
# - Retained Korean API names and PDF page numbers.
# - Clarified ka40001 inverse ETF index code (used KODEX 200's code as placeholder).

import datetime
from typing import Dict, Any, Optional, List, Tuple, Callable

# Type alias for clarity
VariantFunc = Optional[Callable[[Dict[str, Any]], Optional[List[Tuple[str, Dict[str, Any]]]]]]

# Common parameters used across different API calls
today = datetime.date.today()
p_common = {
    "today_str": today.strftime("%Y%m%d"),
    "one_day_ago_str": (today - datetime.timedelta(days=1)).strftime("%Y%m%d"),
    "three_days_ago_str": (today - datetime.timedelta(days=3)).strftime("%Y%m%d"), # Added
    "week_ago_str": (today - datetime.timedelta(days=7)).strftime("%Y%m%d"),
    "two_weeks_ago_str": (today - datetime.timedelta(days=14)).strftime("%Y%m%d"), # Added
    "month_ago_str": (today - datetime.timedelta(days=30)).strftime("%Y%m%d"),
    "two_months_ago_str": (today - datetime.timedelta(days=60)).strftime("%Y%m%d"), # Added
    "six_months_ago_str": (today - datetime.timedelta(days=180)).strftime("%Y%m%d"), # Added
    "year_ago_str": (today - datetime.timedelta(days=365)).strftime("%Y%m%d"),
    "dummy_order_id": "0000000", # 실제 주문 ID 필요 (정정/취소 테스트용)
    "dummy_seq": "0",         # 실제 조건검색식 일련번호 필요 (조건검색 테스트용)
    "placeholder_elw": "57JBHH", # 만료된 ELW 예시
    "placeholder_elw_alt": "57KJ99", # 다른 ELW 예시
    "placeholder_etf": "069500", # KODEX 200
    "placeholder_etf_alt": "114800", # KODEX 인버스
    "placeholder_gold": "M04020000", # 금 1kg
    "placeholder_gold_mini": "M04020100", # 미니금 100g
    "placeholder_inds": "001", # KOSPI
    "placeholder_inds_kosdaq": "101", # KOSDAQ 종합
    "placeholder_thema": "100", # 테마코드 예시 (반도체 대표주)
    "placeholder_stk_kospi": "000660", # SK하이닉스 (코스피 예시)
    "placeholder_stk_kosdaq": "066970", # 엘앤에프 (코스닥 예시)
}

def get_api_definition(api_id: str) -> VariantFunc:
    """
    Returns a lambda function to generate path and parameter variants for a given API ID.
    Uses common parameters (p) passed from the debugger UI.
    Includes comments with API name, PDF page reference, and requirements.
    v2.6: Fixed ka00198/ka10077 errors, expanded variants 500+, clarified ka40001.
    """
    definitions: Dict[str, VariantFunc] = {
        # === OAuth Authentication ===
        "au10001": lambda p: [], # 접근토큰 발급 (p7)
        "au10002": lambda p: [], # 접근토큰폐기 (p9)

        # === Account Information (국내주식 > 계좌) ===
        "kt00001": lambda p: [ # 예수금상세현황요청 (p376)
            ("acnt", {"qry_tp": "3"}), # 추정조회
            ("acnt", {"qry_tp": "2"})  # 일반조회
        ],
        "kt00018": lambda p: [ # 계좌평가잔고내역요청 (p419)
            ("acnt", {"qry_tp": "2", "dmst_stex_tp": "KRX"}), # 개별 KRX
            ("acnt", {"qry_tp": "1", "dmst_stex_tp": "KRX"}), # 합산 KRX
            ("acnt", {"qry_tp": "2", "dmst_stex_tp": "NXT"}), # 개별 NXT (Test)
            ("acnt", {"qry_tp": "1", "dmst_stex_tp": "NXT"})  # 합산 NXT (Test)
        ],
        "kt00002": lambda p: [ # 일별추정예탁자산현황요청 (p381)
            # ▼▼▼ [다각화 시도] 당일(실패) 대신 전일(데이터 존재 가능성) 조회 ▼▼▼
            ("acnt", {"start_dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "end_dt": p.get('one_day_ago_str', p_common['one_day_ago_str'])}), # 전일
            ("acnt", {"start_dt": p.get('week_ago_str', p_common['week_ago_str']), "end_dt": p.get('today_str', p_common['today_str'])}), # 기존 (1주 - 성공)
            ("acnt", {"start_dt": p.get('month_ago_str', p_common['month_ago_str']), "end_dt": p.get('today_str', p_common['today_str'])}) # 기존 (1달 - 성공)
        ],
        "kt00003": lambda p: [ # 추정자산조회요청 (p383)
            ("acnt", {"qry_tp": "0"}), # 전체
            ("acnt", {"qry_tp": "1"})  # 상장폐지 제외
        ],
        "ka10075": lambda p: [ # 미체결요청 (p186)
            ("acnt", {"all_stk_tp": "0", "trde_tp": "0", "stk_cd": "", "stex_tp": "0"}), # 기존 (오늘)
            ("acnt", {"all_stk_tp": "1", "trde_tp": "0", "stk_cd": p['stk_cd'], "stex_tp": "0"}), # 기존 (오늘, 종목)
            # ▼▼▼ [다각화 시도] 어제 날짜로 조회 (어제 체결내역 존재함) ▼▼▼
            ("acnt", {"all_stk_tp": "0", "trde_tp": "0", "stk_cd": "", "stex_tp": "0", "ord_dt": p.get('one_day_ago_str', p_common['one_day_ago_str'])})
        ],
        "ka10077": lambda p: [ # 당일실현손익상세요청 (p192) - Removed invalid variant with empty stk_cd
            ("acnt", {"stk_cd": p['stk_cd']}), # 특정 종목 (필수값)
        ],
        "ka10076": lambda p: [ # 체결요청 (p189)
            ("acnt", {"qry_tp": "0", "sell_tp":"0", "stex_tp":"0", "stk_cd": ""}), # 기존 (오늘 전체)
            ("acnt", {"qry_tp": "1", "sell_tp":"0", "stex_tp":"1", "stk_cd": p['stk_cd']}), # 기존 (오늘, KRX 종목)
            # ▼▼▼ [다각화 시도] 어제 날짜(거래내역 존재)로 조회 ▼▼▼
            ("acnt", {"qry_tp": "0", "sell_tp":"0", "stex_tp":"0", "stk_cd": "", "ord_dt": p.get('one_day_ago_str', p_common['one_day_ago_str'])}), # 어제 전체
            ("acnt", {"qry_tp": "1", "sell_tp":"1", "stex_tp":"0", "stk_cd": "005930", "ord_dt": p.get('one_day_ago_str', p_common['one_day_ago_str'])}), # 어제 삼성전자 매도
            ("acnt", {"qry_tp": "1", "sell_tp":"2", "stex_tp":"0", "stk_cd": "005930", "ord_dt": p.get('one_day_ago_str', p_common['one_day_ago_str'])})  # 어제 삼성전자 매수
        ],
        "ka10074": lambda p: [ # 일자별실현손익요청 (p184)
            ("acnt", {"strt_dt": p.get('today_str', p_common['today_str']), "end_dt": p.get('today_str', p_common['today_str'])}), # 당일
            ("acnt", {"strt_dt": p.get('week_ago_str', p_common['week_ago_str']), "end_dt": p.get('today_str', p_common['today_str'])}), # 최근 1주
            ("acnt", {"strt_dt": p.get('month_ago_str', p_common['month_ago_str']), "end_dt": p.get('today_str', p_common['today_str'])}) # 최근 1달
        ],
        "ka10073": lambda p: [ # 일자별종목별실현손익요청_기간 (p181)
            # ▼▼▼ [다각화 시도] 조회 종목을 실제 거래내역이 있는 '005930', '071050'으로 고정 ▼▼▼
            ("acnt", {"stk_cd": "005930", "strt_dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "end_dt": p.get('one_day_ago_str', p_common['one_day_ago_str'])}), # 어제 (삼성전자)
            ("acnt", {"stk_cd": "071050", "strt_dt": p.get('week_ago_str', p_common['week_ago_str']), "end_dt": p.get('one_day_ago_str', p_common['one_day_ago_str'])}), # 최근 1주 (한국금융지주)
            ("acnt", {"stk_cd": p['stk_cd'], "strt_dt": p.get('week_ago_str', p_common['week_ago_str']), "end_dt": p.get('today_str', p_common['today_str'])}) # 기존 1주 (SK하이닉스)
        ],
        "ka10072": lambda p: [ # 일자별종목별실현손익요청_일자 (p179)
            # ▼▼▼ [다각화 시도] 조회 종목을 실제 거래내역이 있는 '005930', '071050'으로 고정 ▼▼▼
            ("acnt", {"stk_cd": "005930", "strt_dt": p.get('one_day_ago_str', p_common['one_day_ago_str'])}), # 어제 (삼성전자)
            ("acnt", {"stk_cd": "071050", "strt_dt": p.get('one_day_ago_str', p_common['one_day_ago_str'])}), # 어제 (한국금융지주)
            ("acnt", {"stk_cd": p['stk_cd'], "strt_dt": p.get('today_str', p_common['today_str'])}) # 기존 (오늘)
        ],
        "kt00004": lambda p: [ # 계좌평가현황요청 (p384)
            ("acnt", {"qry_tp": "0", "dmst_stex_tp": "KRX"}), # KRX 전체
            ("acnt", {"qry_tp": "1", "dmst_stex_tp": "KRX"}), # KRX 상폐제외
            ("acnt", {"qry_tp": "0", "dmst_stex_tp": "NXT"})  # NXT 전체 (Test)
        ],
        "kt00005": lambda p: [ # 체결잔고요청 (p387)
            ("acnt", {"dmst_stex_tp": "KRX"}), # KRX
            ("acnt", {"dmst_stex_tp": "NXT"})  # NXT
        ],
        "kt00007": lambda p: [ # 계좌별주문체결내역상세요청 (p390)
            ("acnt", {"ord_dt": p.get('today_str', p_common['today_str']), "qry_tp": "1", "stk_bond_tp": "0", "sell_tp": "0", "dmst_stex_tp": "%"}), # 기존 (오늘 순서)
            ("acnt", {"ord_dt": p.get('today_str', p_common['today_str']), "qry_tp": "3", "stk_bond_tp": "1", "sell_tp": "0", "dmst_stex_tp": "%"}), # 기존 (오늘 미체결)
            ("acnt", {"ord_dt": p.get('today_str', p_common['today_str']), "qry_tp": "4", "stk_bond_tp": "1", "sell_tp": "0", "dmst_stex_tp": "%"}), # 기존 (오늘 체결)
            ("acnt", {"ord_dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "qry_tp": "4", "stk_bond_tp": "1", "sell_tp": "0", "dmst_stex_tp": "%"}), # 어제 체결 (성공했었음)
            ("acnt", {"ord_dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "qry_tp": "1", "stk_bond_tp": "1", "sell_tp": "2", "dmst_stex_tp": "%"})  # 어제 매수만 (성공했었음)
        ],
        "kt00008": lambda p: [("acnt", {"strt_dcd_seq": ""})], # 계좌별익일결제예정내역요청 (p393)
        "kt00009": lambda p: [ # 계좌별주문체결현황요청 (p395)
            ("acnt", {"ord_dt": p.get('today_str', p_common['today_str']), "stk_bond_tp": "0", "mrkt_tp": "0", "sell_tp": "0", "qry_tp": "0", "dmst_stex_tp": "KRX"}), # 당일 KRX 전체
            ("acnt", {"ord_dt": p.get('today_str', p_common['today_str']), "stk_bond_tp": "1", "mrkt_tp": "1", "sell_tp": "0", "qry_tp": "1", "dmst_stex_tp": "KRX"}), # 당일 KRX 주식 체결만
            ("acnt", {"ord_dt": p.get('today_str', p_common['today_str']), "stk_bond_tp": "1", "mrkt_tp": "2", "sell_tp": "0", "qry_tp": "0", "dmst_stex_tp": "%"})  # 당일 코스닥 주식 전체
        ],
        "kt00010": lambda p: [ # 주문인출가능금액요청 (p398) - uv 파라미터 유효값(로그 기반)으로 수정
            # Variant 1: 매수 시 (시장가 - 성공)
            ("acnt", {"stk_cd": p.get('stk_cd', p_common['placeholder_stk_kospi']), "trde_tp": "2", "uv": "0"}),
            # Variant 2: 매수 시 (현실적 지정가 - SK하이닉스 - 성공)
            ("acnt", {"stk_cd": p.get('stk_cd', p_common['placeholder_stk_kospi']), "trde_tp": "2", "uv": "480000"}), 
            # ▼▼▼ [다각화 시도] 매도 시도를 잔고 보유 종목(J2251901F)으로 변경 ▼▼▼
            ("acnt", {"stk_cd": "J2251901F", "trde_tp": "1", "trde_qty": "1", "uv": "1"}) # (종목, 수량, 가격 변경)
        ],
        "kt00011": lambda p: [ # 증거금율별주문가능수량조회요청 (p401) - uv 파라미터 유효값(로그 기반)으로 수정
            # Variant 1: 코스피 종목 (시장가)
            ("acnt", {"stk_cd": p.get('stk_cd', p_common['placeholder_stk_kospi']), "uv": "0"}),
            # Variant 2: 코스닥 종목 (현실적 지정가 - 엘앤에프)
            ("acnt", {"stk_cd": p_common['placeholder_stk_kosdaq'], "uv": "110000"})
        ],
        "kt00012": lambda p: [ # 신용보증금율별주문가능수량조회요청 (p404, !!신용 계좌 필요!!)
            ("acnt", {"stk_cd": p['stk_cd'], "uv": p.get('ord_uv', "10000")}), # 코스피 지정가 10000원
            ("acnt", {"stk_cd": p_common['placeholder_stk_kosdaq'], "uv": "1000"}) # 코스닥 지정가 1000원
        ],
        "kt00013": lambda p: [("acnt", {})], # 증거금세부내역조회요청 (p407)
        "kt00015": lambda p: [ # 위탁종합거래내역요청 (p410)
            ("acnt", {"strt_dt": p.get('today_str', p_common['today_str']), "end_dt": p.get('today_str', p_common['today_str']), "tp": "0", "gds_tp": "0", "dmst_stex_tp": "%"}), # 당일 전체
            ("acnt", {"strt_dt": p.get('week_ago_str', p_common['week_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "tp": "3", "gds_tp": "1", "dmst_stex_tp": "%"}), # 1주 국내주식 매매만
            ("acnt", {"strt_dt": p.get('month_ago_str', p_common['month_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "tp": "6", "gds_tp": "0", "dmst_stex_tp": "%"}), # 1달 입금만
            ("acnt", {"strt_dt": p.get('month_ago_str', p_common['month_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "tp": "7", "gds_tp": "0", "dmst_stex_tp": "%"})  # 1달 출금만
        ],
        "kt00016": lambda p: [ # 일별계좌수익률상세현황요청 (p414)
            ("acnt", {"fr_dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "to_dt": p.get('one_day_ago_str', p_common['one_day_ago_str'])}), # 전일
            ("acnt", {"fr_dt": p.get('week_ago_str', p_common['week_ago_str']), "to_dt": p.get('today_str', p_common['today_str'])}), # 1주
            ("acnt", {"fr_dt": p.get('month_ago_str', p_common['month_ago_str']), "to_dt": p.get('today_str', p_common['today_str'])}) # 1달
        ],
        "kt00017": lambda p: [("acnt", {})], # 계좌별당일현황요청 (p417)
        "ka01690": lambda p: [ # 일별잔고수익률 (p12, 운영전용 가능성)
            ("acnt", {"qry_dt": p.get('one_day_ago_str', p_common['one_day_ago_str'])}), # 전일 데이터로 조회
            ("acnt", {"qry_dt": p.get('three_days_ago_str', p_common['three_days_ago_str'])}) # 3일 전 데이터로 조회
        ],
        "ka10085": lambda p: [ # 계좌수익률요청 (p208)
            ("acnt", {"stex_tp": "0"}), # 통합
            ("acnt", {"stex_tp": "1"}), # KRX
            ("acnt", {"stex_tp": "2"})  # NXT
        ],
        "ka10088": lambda p: [ # 미체결 분할주문 상세 (p218)
             # ▼▼▼ [다각화 시도] 로그에 존재하는 어제 주문번호로 조회 ▼▼▼
             # (kt00007 로그에서 0000050 확인 [cite: 4581])
            ("acnt", {"ord_no": "0000050"}) 
        ],
        "ka10170": lambda p: [ # 당일매매일지요청 (p240)
            ("acnt", {"base_dt": p.get('today_str', p_common['today_str']), "ottks_tp": "1", "ch_crd_tp": "0"}), # 당일 매수->매도
            ("acnt", {"base_dt": p.get('today_str', p_common['today_str']), "ottks_tp": "2", "ch_crd_tp": "0"}), # 당일 매도 전체
            ("acnt", {"base_dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "ottks_tp": "1", "ch_crd_tp": "0"})  # 전일 매수->매도
        ],

        # === Stock Info (국내주식 > 종목정보) ===
        "ka00198": lambda p: [ # 실시간종목조회순위 (p10) - FIX: Changed gry_tp to qry_tp (PDF Doc shows 'gry_tp', PDF Example shows 'qry_tp')
            ("stkinfo", {"qry_tp": "4"}), # 당일 누적
            ("stkinfo", {"qry_tp": "3"}), # 1시간
            ("stkinfo", {"qry_tp": "2"}), # 10분
            ("stkinfo", {"qry_tp": "1"}), # 1분
            ("stkinfo", {"qry_tp": "5"})  # 30초
        ],
        "ka10001": lambda p: [ # 주식기본정보요청 (p14)
            ("stkinfo", {"stk_cd": p.get('stk_cd', p_common['placeholder_stk_kospi'])}), # 기본 종목(코스피)
            ("stkinfo", {"stk_cd": p_common['placeholder_stk_kosdaq']}), # 코스닥 종목
            ("stkinfo", {"stk_cd": p.get('etf_cd', p_common['placeholder_etf'])}), # ETF 종목
            # ▼▼▼ [다각화 시도] 유효한 신주인수권 코드로 변경 ▼▼▼
            ("stkinfo", {"stk_cd": "J0669721F"}) # 엘앤에프 7WR (로그에서 성공 확인)
        ],
        "ka10002": lambda p: [ # 주식거래원요청 (p17)
             ("stkinfo", {"stk_cd": p['stk_cd']}), # 코스피
             ("stkinfo", {"stk_cd": p_common['placeholder_stk_kosdaq']}) # 코스닥
        ],
        "ka10003": lambda p: [ # 체결정보요청 (p20)
            ("stkinfo", {"stk_cd": p['stk_cd']}), # 코스피
            ("stkinfo", {"stk_cd": p_common['placeholder_stk_kosdaq']}) # 코스닥
        ],
        "ka10013": lambda p: [ # 신용매매동향요청 (p47)
            ("stkinfo", {"stk_cd": p['stk_cd'], "dt": p.get('today_str', p_common['today_str']), "qry_tp": "1"}), # 융자 당일
            ("stkinfo", {"stk_cd": p['stk_cd'], "dt": p.get('today_str', p_common['today_str']), "qry_tp": "2"}), # 대주 당일
            ("stkinfo", {"stk_cd": p['stk_cd'], "dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "qry_tp": "1"}) # 융자 전일
        ],
        "ka10015": lambda p: [ # 일별거래상세요청 (p53)
            ("stkinfo", {"stk_cd": p['stk_cd'], "strt_dt": p.get('today_str', p_common['today_str'])}), # 당일
            ("stkinfo", {"stk_cd": p['stk_cd'], "strt_dt": p.get('one_day_ago_str', p_common['one_day_ago_str'])}), # 전일
            ("stkinfo", {"stk_cd": p_common['placeholder_stk_kosdaq'], "strt_dt": p.get('today_str', p_common['today_str'])}) # 코스닥 당일
        ],
        "ka10016": lambda p: [ # 신고저가요청 (p57)
            ("stkinfo", {"mrkt_tp": "001", "ntl_tp": "1", "high_low_close_tp": "2", "stk_cnd":"0", "trde_qty_tp":"00000", "crd_cnd":"0", "updown_incls":"0", "dt":"5", "stex_tp":"1"}), # 코스피 신고가(종가) 5일
            ("stkinfo", {"mrkt_tp": "101", "ntl_tp": "2", "high_low_close_tp": "1", "stk_cnd":"0", "trde_qty_tp":"00100", "crd_cnd":"0", "updown_incls":"0", "dt":"20", "stex_tp":"1"}), # 코스닥 신저가(고저) 20일 10만주 이상
            ("stkinfo", {"mrkt_tp": "000", "ntl_tp": "1", "high_low_close_tp": "1", "stk_cnd":"1", "trde_qty_tp":"00000", "crd_cnd":"0", "updown_incls":"1", "dt":"60", "stex_tp":"3"}) # 전체 신고가(고저) 60일 관리제외 상하한포함
        ],
        "ka10017": lambda p: [ # 상하한가요청 (p60)
            ("stkinfo", {"mrkt_tp": "000", "updown_tp": "1", "sort_tp": "1", "stk_cnd":"0", "trde_qty_tp":"00000", "crd_cnd":"0", "trde_gold_tp":"0", "stex_tp":"1"}), # 기존 (상한가 - 성공)
            # ▼▼▼ [다각화 시도] 하한가(4) 대신 상승(2) 조회 (데이터 확보) ▼▼▼
            ("stkinfo", {"mrkt_tp": "001", "updown_tp": "2", "sort_tp": "3", "stk_cnd":"1", "trde_qty_tp":"00000", "crd_cnd":"0", "trde_gold_tp":"0", "stex_tp":"1"}), # 코스피 상승 (등락률순, 관리제외)
            ("stkinfo", {"mrkt_tp": "101", "updown_tp": "2", "sort_tp": "1", "stk_cnd":"0", "trde_qty_tp":"00100", "crd_cnd":"0", "trde_gold_tp":"8", "stex_tp":"1"})  # 기존 (코스닥 상승 - 성공)
        ],
        "ka10018": lambda p: [ # 고저가근접요청 (p63)
            ("stkinfo", {"high_low_tp":"1", "alacc_rt":"05", "mrkt_tp":"000", "trde_qty_tp":"00000", "stk_cnd":"0", "crd_cnd":"0", "stex_tp":"1"}), # 고가 근접 0.5% (거래량 0000 -> 00000 수정)
            ("stkinfo", {"high_low_tp":"2", "alacc_rt":"10", "mrkt_tp":"001", "trde_qty_tp":"00000", "stk_cnd":"0", "crd_cnd":"0", "stex_tp":"1"}), # 코스피 저가 근접 1.0% (거래량 0000 -> 00000 수정)
            ("stkinfo", {"high_low_tp":"1", "alacc_rt":"20", "mrkt_tp":"101", "trde_qty_tp":"00010", "stk_cnd":"1", "crd_cnd":"0", "stex_tp":"1"})  # 코스닥 고가 근접 2.0% (만주, 관리제외) (거래량 0010 -> 00010 수정)
        ],
        "ka10019": lambda p: [ # 가격급등락요청 (p66)
            ("stkinfo", {"mrkt_tp":"000", "flu_tp":"1", "tm_tp":"1", "tm":"5", "trde_qty_tp":"00000", "stk_cnd":"0", "crd_cnd":"0", "pric_cnd":"0", "updown_incls":"1", "stex_tp":"1"}), # 5분 급등
            ("stkinfo", {"mrkt_tp":"001", "flu_tp":"2", "tm_tp":"1", "tm":"10", "trde_qty_tp":"00000", "stk_cnd":"0", "crd_cnd":"0", "pric_cnd":"0", "updown_incls":"1", "stex_tp":"1"}), # 코스피 10분 급락
            ("stkinfo", {"mrkt_tp":"101", "flu_tp":"1", "tm_tp":"2", "tm":"1", "trde_qty_tp":"00100", "stk_cnd":"1", "crd_cnd":"0", "pric_cnd":"8", "updown_incls":"1", "stex_tp":"1"})  # 코스닥 전일대비 급등 (10만주, 관리제외, 1천원이상)
        ],
        "ka10024": lambda p: [ # 거래량갱신요청 (p79)
            ("stkinfo", {"mrkt_tp": "001", "cycle_tp": "5", "trde_qty_tp": "50", "stex_tp": "3"}), # 코스피 5일 5만주
            ("stkinfo", {"mrkt_tp": "101", "cycle_tp": "20", "trde_qty_tp": "100", "stex_tp": "3"}), # 코스닥 20일 10만주
            ("stkinfo", {"mrkt_tp": "000", "cycle_tp": "60", "trde_qty_tp": "500", "stex_tp": "3"})  # 전체 60일 50만주
        ],
        "ka10025": lambda p: [ # 매물대집중요청 (p81)
            ("stkinfo", {"mrkt_tp": "000", "prps_cnctr_rt": "50", "cur_prc_entry": "0", "prpscnt": "10", "cycle_tp": "50", "stex_tp": "3"}), # 50일 기준, 50% 집중
            ("stkinfo", {"mrkt_tp": "001", "prps_cnctr_rt": "70", "cur_prc_entry": "1", "prpscnt": "5", "cycle_tp": "100", "stex_tp": "3"}), # 코스피 100일 기준, 70% 집중, 현재가 포함, 5개 매물대
        ],
        # Removed confusing comment about code replacement here, as the code below is correct.
        "ka10026": lambda p: [ # 고저PER요청 (p84)
            ("stkinfo", {"pertp": "1", "stex_tp": "3"}), # 저PBR
            ("stkinfo", {"pertp": "2", "stex_tp": "3"}), # 고PBR
            ("stkinfo", {"pertp": "3", "stex_tp": "3"}), # 저PER
            ("stkinfo", {"pertp": "4", "stex_tp": "3"}), # 고PER
            ("stkinfo", {"pertp": "5", "stex_tp": "3"}), # 저ROE
            ("stkinfo", {"pertp": "6", "stex_tp": "3"})  # 고ROE
        ],
        "ka10028": lambda p: [ # 시가대비등락률요청 (p89)
            ("stkinfo", {"sort_tp": "1", "trde_qty_cnd": "0000", "mrkt_tp": "000", "updown_incls": "1", "stk_cnd": "0", "crd_cnd": "0", "trde_prica_cnd": "0", "flu_cnd": "1", "stex_tp": "3"}), # 시가 대비 상승
            ("stkinfo", {"sort_tp": "1", "trde_qty_cnd": "0000", "mrkt_tp": "001", "updown_incls": "1", "stk_cnd": "0", "crd_cnd": "0", "trde_prica_cnd": "0", "flu_cnd": "2", "stex_tp": "3"}), # 코스피 시가 대비 하락
            ("stkinfo", {"sort_tp": "2", "trde_qty_cnd": "0100", "mrkt_tp": "101", "updown_incls": "1", "stk_cnd": "1", "crd_cnd": "0", "trde_prica_cnd": "10", "flu_cnd": "1", "stex_tp": "3"})  # 코스닥 고가 대비 상승 (10만주, 관리제외, 1억이상)
        ],
        "ka10043": lambda p: [ # 거래원매물대분석요청 (p125)
            ("stkinfo", {"stk_cd": p['stk_cd'], "strt_dt": p.get('week_ago_str', p_common['week_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "qry_dt_tp":"1", "pot_tp":"0", "dt":"5", "sort_base":"1", "mmcm_cd":"050", "stex_tp":"1"}), # 키움증권 5일 종가순
            ("stkinfo", {"stk_cd": p['stk_cd'], "strt_dt": p.get('month_ago_str', p_common['month_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "qry_dt_tp":"1", "pot_tp":"0", "dt":"20", "sort_base":"2", "mmcm_cd":"003", "stex_tp":"1"}) # 한국투자 20일 날짜순
        ],
        "ka10052": lambda p: [ # 거래원순간거래량요청 (p144)
            ("stkinfo", {"mmcm_cd": "888", "mrkt_tp": "0", "qty_tp": "0", "pric_tp": "0", "stex_tp": "3"}), # 전체 외국계
            ("stkinfo", {"mmcm_cd": "036", "mrkt_tp": "1", "qty_tp": "10", "pric_tp": "8", "stex_tp": "3"}), # 모건스탠리 코스피 1만주 이상, 1천원이상
            ("stkinfo", {"mmcm_cd": "050", "mrkt_tp": "2", "qty_tp": "50", "pric_tp": "0", "stex_tp": "3"})  # 키움증권 코스닥 5만주 이상
        ],
        "ka10054": lambda p: [ # 변동성완화장치(VI)발동종목요청 (p148)
             ("stkinfo", {"mrkt_tp": "000", "bf_mkrt_tp": "0", "motn_tp": "0", "skip_stk": "000000000", "trde_qty_tp": "0", "min_trde_qty":"0", "max_trde_qty":"999999999999", "trde_prica_tp": "0", "min_trde_prica": "0", "max_trde_prica":"9999999999", "motn_drc": "0", "stex_tp": "3"}), # 전체 (성공)
             ("stkinfo", {"mrkt_tp": "001", "bf_mkrt_tp": "1", "motn_tp": "1", "skip_stk": "111111111", "trde_qty_tp": "0", "min_trde_qty":"0", "max_trde_qty":"999999999999", "trde_prica_tp": "0", "min_trde_prica": "0", "max_trde_prica":"9999999999", "motn_drc": "1", "stex_tp": "3"}), # 코스피 정적 상승 (성공)
             # ▼▼▼ [다각화 시도] 조건을 '거래량 1주 이상'으로 변경 ▼▼▼
             ("stkinfo", {"mrkt_tp": "101", "bf_mkrt_tp": "0", "motn_tp": "0", "skip_stk": "000000000", "trde_qty_tp": "1", "min_trde_qty":"1", "max_trde_qty":"999999999999", "trde_prica_tp": "0", "min_trde_prica": "0", "max_trde_prica":"9999999999", "motn_drc": "0", "stex_tp": "3"})  # 코스닥 *전체시간* *전체VI* (거래량 1주 이상)
        ],
        "ka10055": lambda p: [ # 당일전일체결량요청 (p151)
            ("stkinfo", {"stk_cd": p['stk_cd'], "tdy_pred": "1"}), # 당일
            ("stkinfo", {"stk_cd": p['stk_cd'], "tdy_pred": "2"}), # 전일
            ("stkinfo", {"stk_cd": p_common['placeholder_stk_kosdaq'], "tdy_pred": "1"}) # 코스닥 당일
        ],
        "ka10058": lambda p: [ # 투자자별일별매매종목요청 (p153)
            ("stkinfo", {"strt_dt": p.get('today_str', p_common['today_str']), "end_dt": p.get('today_str', p_common['today_str']), "trde_tp": "2", "mrkt_tp": "001", "invsr_tp": "9000", "stex_tp": "1"}), # 당일 코스피 외인 순매수
            ("stkinfo", {"strt_dt": p.get('today_str', p_common['today_str']), "end_dt": p.get('today_str', p_common['today_str']), "trde_tp": "1", "mrkt_tp": "101", "invsr_tp": "9999", "stex_tp": "1"}), # 당일 코스닥 기관계 순매도
            ("stkinfo", {"strt_dt": p.get('week_ago_str', p_common['week_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "trde_tp": "2", "mrkt_tp": "001", "invsr_tp": "6000", "stex_tp": "1"})  # 1주 코스피 연기금 순매수
        ],
        "ka10059": lambda p: [ # 종목별투자자기관별요청 (p155)
            ("stkinfo", {"stk_cd": p['stk_cd'], "dt": p.get('today_str', p_common['today_str']), "amt_qty_tp": "1", "trde_tp":"0", "unit_tp": "1000"}), # 당일 금액 천원
            ("stkinfo", {"stk_cd": p['stk_cd'], "dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "amt_qty_tp": "2", "trde_tp":"0", "unit_tp": "1"}), # 전일 수량 단주
            ("stkinfo", {"stk_cd": p['stk_cd'], "dt": p.get('today_str', p_common['today_str']), "amt_qty_tp": "1", "trde_tp":"1", "unit_tp": "1000"}), # 당일 금액 매수만
            ("stkinfo", {"stk_cd": p['stk_cd'], "dt": p.get('today_str', p_common['today_str']), "amt_qty_tp": "1", "trde_tp":"2", "unit_tp": "1000"})  # 당일 금액 매도만
        ],
        "ka10061": lambda p: [ # 종목별투자자기관별합계요청 (p161)
            ("stkinfo", {"stk_cd": p['stk_cd'], "strt_dt": p.get('today_str', p_common['today_str']), "end_dt": p.get('today_str', p_common['today_str']), "amt_qty_tp": "1", "trde_tp": "0", "unit_tp": "1000"}), # 당일 금액
            ("stkinfo", {"stk_cd": p['stk_cd'], "strt_dt": p.get('week_ago_str', p_common['week_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "amt_qty_tp": "1", "trde_tp": "0", "unit_tp": "1000"}), # 1주 금액
            ("stkinfo", {"stk_cd": p['stk_cd'], "strt_dt": p.get('month_ago_str', p_common['month_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "amt_qty_tp": "2", "trde_tp": "0", "unit_tp": "1"})   # 1달 수량
        ],
        "ka10084": lambda p: [ # 당일전일체결요청 (p206)
            ("stkinfo", {"stk_cd": p['stk_cd'], "tdy_pred": "1", "tic_min": "0"}), # 당일 틱
            ("stkinfo", {"stk_cd": p['stk_cd'], "tdy_pred": "1", "tic_min": "1", "tm": "0900"}), # 당일 분 (9시)
            ("stkinfo", {"stk_cd": p['stk_cd'], "tdy_pred": "2", "tic_min": "0"}), # 전일 틱
            ("stkinfo", {"stk_cd": p['stk_cd'], "tdy_pred": "2", "tic_min": "1", "tm": "1530"})  # 전일 분 (15시30분)
        ],
        "ka10095": lambda p: [ # 관심종목정보요청 (p222)
            ("stkinfo", {"stk_cd": p['stk_cd']}), # 단일 종목 (코스피)
            ("stkinfo", {"stk_cd": p_common['placeholder_stk_kosdaq']}), # 단일 종목 (코스닥)
            ("stkinfo", {"stk_cd": f"{p['stk_cd']}|{p_common['placeholder_stk_kospi']}|{p_common['placeholder_stk_kosdaq']}"}) # 여러 종목 (| 구분)
        ],
        "ka10099": lambda p: [ # 종목정보 리스트 (p228)
            ("stkinfo", {"mrkt_tp": "0"}), # 코스피
            ("stkinfo", {"mrkt_tp": "10"}), # 코스닥
            ("stkinfo", {"mrkt_tp": "8"})   # ETF
        ],
        "ka10100": lambda p: [ # 종목정보 조회 (p231)
            ("stkinfo", {"stk_cd": p['stk_cd']}), # 코스피
            ("stkinfo", {"stk_cd": p_common['placeholder_stk_kosdaq']}) # 코스닥
        ],
        "ka10101": lambda p: [ # 업종코드 리스트 (p233)
            ("stkinfo", {"mrkt_tp": "0"}), # 코스피
            ("stkinfo", {"mrkt_tp": "1"}), # 코스닥
            ("stkinfo", {"mrkt_tp": "2"})  # KOSPI200
        ],
        "ka10102": lambda p: [("stkinfo", {})], # 회원사 리스트 (p235)
        "ka90003": lambda p: [ # 프로그램순매수상위50요청 (p350)
            ("stkinfo", {"trde_upper_tp": "2", "amt_qty_tp": "1", "mrkt_tp": "P00101", "stex_tp": "1"}), # 코스피 순매수 금액
            ("stkinfo", {"trde_upper_tp": "1", "amt_qty_tp": "2", "mrkt_tp": "P10102", "stex_tp": "1"}), # 코스닥 순매도 수량
            ("stkinfo", {"trde_upper_tp": "1", "amt_qty_tp": "1", "mrkt_tp": "P00101", "stex_tp": "1"}), # 코스피 순매도 금액
            ("stkinfo", {"trde_upper_tp": "2", "amt_qty_tp": "2", "mrkt_tp": "P10102", "stex_tp": "1"})  # 코스닥 순매수 수량
        ],
        "ka90004": lambda p: [ # 종목별프로그램매매현황요청 (p352)
            ("stkinfo", {"dt": p.get('today_str', p_common['today_str']), "mrkt_tp": "P00101", "stex_tp": "1"}), # 코스피 당일
            ("stkinfo", {"dt": p.get('today_str', p_common['today_str']), "mrkt_tp": "P10102", "stex_tp": "1"}), # 코스닥 당일
            ("stkinfo", {"dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "mrkt_tp": "P00101", "stex_tp": "1"})  # 코스피 전일
        ],
        "kt20016": lambda p: [ # 신용융자 가능종목요청 (p438)
            ("stkinfo", {"crd_stk_grde_tp": "A", "mrkt_deal_tp": "%", "stk_cd": ""}), # A군 전체
            ("stkinfo", {"crd_stk_grde_tp": "B", "mrkt_deal_tp": "1", "stk_cd": ""}), # B군 코스피
            ("stkinfo", {"crd_stk_grde_tp": "C", "mrkt_deal_tp": "0", "stk_cd": ""}), # C군 코스닥
            ("stkinfo", {"crd_stk_grde_tp": "%", "mrkt_deal_tp": "%", "stk_cd": p['stk_cd']}) # 특정 종목 (전체 등급)
        ],
        "kt20017": lambda p: [ # 신용융자 가능문의 (p440)
            ("stkinfo", {"stk_cd": p['stk_cd']}), # 코스피
            ("stkinfo", {"stk_cd": p_common['placeholder_stk_kosdaq']}) # 코스닥
        ],

        # === Market Condition (국내주식 > 시세) ===
        "ka10004": lambda p: [ # 주식호가요청 (p23)
            ("mrkcond", {"stk_cd": p['stk_cd']}), # 코스피
            ("mrkcond", {"stk_cd": p_common['placeholder_stk_kosdaq']}) # 코스닥
        ],
        "ka10005": lambda p: [ # 주식일주월시분요청 (p27)
            ("mrkcond", {"stk_cd": p['stk_cd']}), # 코스피
            ("mrkcond", {"stk_cd": p_common['placeholder_stk_kosdaq']}) # 코스닥
        ],
        "ka10006": lambda p: [ # 주식시분요청 (p30)
            ("mrkcond", {"stk_cd": p['stk_cd']}), # 코스피
            ("mrkcond", {"stk_cd": p_common['placeholder_stk_kosdaq']}) # 코스닥
        ],
        "ka10007": lambda p: [ # 시세표성정보요청 (p32)
            ("mrkcond", {"stk_cd": p['stk_cd']}), # 코스피
            ("mrkcond", {"stk_cd": p_common['placeholder_stk_kosdaq']}) # 코스닥
        ],
        "ka10011": lambda p: [ # 신주인수권전체시세요청 (p45)
            ("mrkcond", {"newstk_recvrht_tp": "00"}), # 전체
            ("mrkcond", {"newstk_recvrht_tp": "05"}), # 신주인수권증권
            ("mrkcond", {"newstk_recvrht_tp": "07"})  # 신주인수권증서
        ],
        "ka10044": lambda p: [ # 일별기관매매종목요청 (p128)
            ("mrkcond", {"strt_dt": p.get('today_str', p_common['today_str']), "end_dt": p.get('today_str', p_common['today_str']), "trde_tp": "2", "mrkt_tp": "001", "stex_tp": "3"}), # 당일 코스피 순매수
            ("mrkcond", {"strt_dt": p.get('week_ago_str', p_common['week_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "trde_tp": "1", "mrkt_tp": "101", "stex_tp": "3"}), # 1주 코스닥 순매도
            ("mrkcond", {"strt_dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "end_dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "trde_tp": "2", "mrkt_tp": "101", "stex_tp": "3"}) # 전일 코스닥 순매수
        ],
        "ka10045": lambda p: [ # 종목별기관매매추이요청 (p130)
            ("mrkcond", {"stk_cd": p['stk_cd'], "strt_dt": p.get('week_ago_str', p_common['week_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "orgn_prsm_unp_tp": "1", "for_prsm_unp_tp": "1"}), # 1주 매수단가
            ("mrkcond", {"stk_cd": p['stk_cd'], "strt_dt": p.get('month_ago_str', p_common['month_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "orgn_prsm_unp_tp": "2", "for_prsm_unp_tp": "2"}) # 1달 매도단가
        ],
        "ka10046": lambda p: [ # 체결강도추이시간별요청 (p132)
            ("mrkcond", {"stk_cd": p['stk_cd']}), # 코스피
            ("mrkcond", {"stk_cd": p_common['placeholder_stk_kosdaq']}) # 코스닥
        ],
        "ka10047": lambda p: [ # 체결강도추이일별요청 (p134)
            ("mrkcond", {"stk_cd": p['stk_cd']}), # 코스피
            ("mrkcond", {"stk_cd": p_common['placeholder_stk_kosdaq']}) # 코스닥
        ],
        "ka10063": lambda p: [ # 장중투자자별매매요청 (p165)
            ("mrkcond", {"mrkt_tp": "001", "amt_qty_tp": "1", "invsr": "6", "frgn_all": "0", "smtm_netprps_tp": "0", "stex_tp": "3"}), # 코스피 외국인 금액
            ("mrkcond", {"mrkt_tp": "101", "amt_qty_tp": "1", "invsr": "7", "frgn_all": "0", "smtm_netprps_tp": "0", "stex_tp": "3"}), # 코스닥 기관계 금액
            ("mrkcond", {"mrkt_tp": "001", "amt_qty_tp": "1", "invsr": "1", "frgn_all": "0", "smtm_netprps_tp": "0", "stex_tp": "3"}), # 코스피 투신 금액
            ("mrkcond", {"mrkt_tp": "001", "amt_qty_tp": "1", "invsr": "3", "frgn_all": "1", "smtm_netprps_tp": "1", "stex_tp": "3"})  # 코스피 연기금 금액 (외국계전체, 동시순매수 체크)
        ],
        "ka10066": lambda p: [ # 장마감후투자자별매매요청 (p172)
            ("mrkcond", {"mrkt_tp": "001", "amt_qty_tp": "1", "trde_tp": "0", "stex_tp": "3"}), # 코스피 금액 순매수
            ("mrkcond", {"mrkt_tp": "101", "amt_qty_tp": "2", "trde_tp": "0", "stex_tp": "3"}), # 코스닥 수량 순매수
            ("mrkcond", {"mrkt_tp": "000", "amt_qty_tp": "1", "trde_tp": "1", "stex_tp": "3"}), # 전체 금액 매수
            ("mrkcond", {"mrkt_tp": "000", "amt_qty_tp": "1", "trde_tp": "2", "stex_tp": "3"})  # 전체 금액 매도
        ],
        "ka10078": lambda p: [ # 증권사별종목매매동향요청 (p194)
            ("mrkcond", {"mmcm_cd": "050", "stk_cd": p['stk_cd'], "strt_dt": p.get('today_str', p_common['today_str']), "end_dt": p.get('today_str', p_common['today_str'])}), # 키움 당일
            ("mrkcond", {"mmcm_cd": "003", "stk_cd": p['stk_cd'], "strt_dt": p.get('week_ago_str', p_common['week_ago_str']), "end_dt": p.get('today_str', p_common['today_str'])}), # 한국투자 1주
            ("mrkcond", {"mmcm_cd": "005", "stk_cd": p_common['placeholder_stk_kosdaq'], "strt_dt": p.get('month_ago_str', p_common['month_ago_str']), "end_dt": p.get('today_str', p_common['today_str'])}) # 미래에셋 코스닥 1달
        ],
        "ka10086": lambda p: [ # 일별주가요청 (p211)
            ("mrkcond", {"stk_cd": p['stk_cd'], "qry_dt": p.get('today_str', p_common['today_str']), "indc_tp": "0"}), # 수량 당일
            ("mrkcond", {"stk_cd": p['stk_cd'], "qry_dt": p.get('today_str', p_common['today_str']), "indc_tp": "1"}), # 금액 당일
            ("mrkcond", {"stk_cd": p['stk_cd'], "qry_dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "indc_tp": "0"})  # 수량 전일
        ],
        "ka10087": lambda p: [ # 시간외단일가요청 (p214)
            ("mrkcond", {"stk_cd": p['stk_cd']}), # 코스피
            ("mrkcond", {"stk_cd": p_common['placeholder_stk_kosdaq']}) # 코스닥
        ],
        "ka50010": lambda p: [ # 금현물체결추이 (p318)
            ("mrkcond", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold'])}), # 금 1kg
            ("mrkcond", {"stk_cd": p_common['placeholder_gold_mini']}) # 미니금 100g
        ],
        "ka50012": lambda p: [ # 금현물일별추이 (p320)
            ("mrkcond", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "base_dt": p.get('today_str', p_common['today_str'])}), # 금 1kg 당일
            ("mrkcond", {"stk_cd": p_common['placeholder_gold_mini'], "base_dt": p.get('one_day_ago_str', p_common['one_day_ago_str'])}) # 미니금 100g 전일
        ],
        "ka50087": lambda p: [ # 금현물예상체결 (p332)
            ("mrkcond", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold'])}), # 금 1kg
            ("mrkcond", {"stk_cd": p_common['placeholder_gold_mini']}) # 미니금 100g
        ],
        "ka50100": lambda p: [ # 금현물 시세정보 (p338)
            ("mrkcond", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold'])}), # 금 1kg
            ("mrkcond", {"stk_cd": p_common['placeholder_gold_mini']}) # 미니금 100g
        ],
        "ka50101": lambda p: [ # 금현물 호가 (p340)
            ("mrkcond", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "tic_scope": "1"}), # 금 1kg (PDF Request Table 에는 tic_scope 없음, 확인 필요)
            ("mrkcond", {"stk_cd": p_common['placeholder_gold_mini'], "tic_scope": "1"}) # 미니금 100g (PDF Request Table 에는 tic_scope 없음, 확인 필요)
        ],
        "ka90005": lambda p: [ # 프로그램매매추이요청 시간대별 (p355)
            ("mrkcond", {"date": p.get('today_str', p_common['today_str']), "amt_qty_tp": "1", "mrkt_tp": "P00101", "min_tic_tp": "1", "stex_tp": "1"}), # 코스피 금액 분
            ("mrkcond", {"date": p.get('today_str', p_common['today_str']), "amt_qty_tp": "2", "mrkt_tp": "P10102", "min_tic_tp": "1", "stex_tp": "1"}), # 코스닥 수량 분
            ("mrkcond", {"date": p.get('today_str', p_common['today_str']), "amt_qty_tp": "1", "mrkt_tp": "P00101", "min_tic_tp": "0", "stex_tp": "1"})  # 코스피 금액 틱
        ],
        "ka90006": lambda p: [ # 프로그램매매차익잔고추이요청 (p358)
            ("mrkcond", {"date": p.get('today_str', p_common['today_str']), "stex_tp": "1"}), # KRX
            ("mrkcond", {"date": p.get('one_day_ago_str', p_common['one_day_ago_str']), "stex_tp": "1"}) # KRX 전일
        ],
        "ka90007": lambda p: [ # 프로그램매매누적추이요청 (p360)
            ("mrkcond", {"date": p.get('today_str', p_common['today_str']), "amt_qty_tp": "1", "mrkt_tp": "0", "stex_tp": "3"}), # 코스피 금액
            ("mrkcond", {"date": p.get('today_str', p_common['today_str']), "amt_qty_tp": "1", "mrkt_tp": "1", "stex_tp": "3"}), # 코스닥 금액
            ("mrkcond", {"date": p.get('one_day_ago_str', p_common['one_day_ago_str']), "amt_qty_tp": "2", "mrkt_tp": "0", "stex_tp": "3"})  # 코스피 수량 (전일)
        ],
        "ka90008": lambda p: [ # 종목시간별프로그램매매추이요청 (p362)
            ("mrkcond", {"amt_qty_tp": "1", "stk_cd": p['stk_cd'], "date": p.get('today_str', p_common['today_str'])}), # 금액 당일
            ("mrkcond", {"amt_qty_tp": "2", "stk_cd": p['stk_cd'], "date": p.get('today_str', p_common['today_str'])}), # 수량 당일
            ("mrkcond", {"amt_qty_tp": "1", "stk_cd": p['stk_cd'], "date": p.get('one_day_ago_str', p_common['one_day_ago_str'])}) # 금액 전일
        ],
        "ka90010": lambda p: [ # 프로그램매매추이요청 일자별 (p368)
            ("mrkcond", {"date": p.get('today_str', p_common['today_str']), "amt_qty_tp": "1", "mrkt_tp": "P00101", "min_tic_tp": "0", "stex_tp": "1"}), # 코스피 금액
            ("mrkcond", {"date": p.get('today_str', p_common['today_str']), "amt_qty_tp": "1", "mrkt_tp": "P10102", "min_tic_tp": "0", "stex_tp": "1"}), # 코스닥 금액
            ("mrkcond", {"date": p.get('week_ago_str', p_common['week_ago_str']), "amt_qty_tp": "2", "mrkt_tp": "P00101", "min_tic_tp": "0", "stex_tp": "1"})  # 코스피 수량 (1주 전 데이터로 요청)
        ],
        "ka90013": lambda p: [ # 종목일별프로그램매매추이요청 (p373)
            ("mrkcond", {"stk_cd": p['stk_cd'], "date": p.get('today_str', p_common['today_str']), "amt_qty_tp": "1"}), # 금액 당일
            ("mrkcond", {"stk_cd": p['stk_cd'], "date": p.get('today_str', p_common['today_str']), "amt_qty_tp": "2"}), # 수량 당일
            ("mrkcond", {"stk_cd": p_common['placeholder_stk_kosdaq'], "date": p.get('one_day_ago_str', p_common['one_day_ago_str']), "amt_qty_tp": "1"}) # 코스닥 종목 금액 (전일)
        ],

        # === Chart Data (국내주식 > 차트) ===
        # Chart variants focus on different timeframes. Removed 'upd_stkpc_tp' based on
        "ka10079": lambda p: [ # 주식틱차트조회요청 (p196) - upd_stkpc_tp '1' 또는 '0' 추가
            ("chart", {"stk_cd": p['stk_cd'], "tic_scope": "1", "upd_stkpc_tp": "1"}),  # 1틱 (수정주가)
            ("chart", {"stk_cd": p['stk_cd'], "tic_scope": "5", "upd_stkpc_tp": "0"}),  # 5틱 (원본주가)
            ("chart", {"stk_cd": p['stk_cd'], "tic_scope": "10", "upd_stkpc_tp": "1"}), # 10틱 (수정주가)
            ("chart", {"stk_cd": p_common['placeholder_stk_kosdaq'], "tic_scope": "30", "upd_stkpc_tp": "1"})  # 30틱 (코스닥, 수정주가)
        ],
        "ka10080": lambda p: [ # 주식분봉차트조회요청 (p198) - upd_stkpc_tp '1' 또는 '0' 추가
            ("chart", {"stk_cd": p['stk_cd'], "tic_scope": "1", "upd_stkpc_tp": "1"}),  # 1분 (수정주가)
            ("chart", {"stk_cd": p['stk_cd'], "tic_scope": "5", "upd_stkpc_tp": "0"}),  # 5분 (원본주가)
            ("chart", {"stk_cd": p['stk_cd'], "tic_scope": "15", "upd_stkpc_tp": "1"}), # 15분 (수정주가)
            ("chart", {"stk_cd": p_common['placeholder_stk_kosdaq'], "tic_scope": "30", "upd_stkpc_tp": "1"}), # 30분 (코스닥, 수정주가)
            ("chart", {"stk_cd": p['stk_cd'], "tic_scope": "60", "upd_stkpc_tp": "0"})  # 60분 (원본주가)
        ],
        "ka10081": lambda p: [ # 주식일봉차트조회요청 (p200) - upd_stkpc_tp '1' 또는 '0' 추가
            ("chart", {"stk_cd": p['stk_cd'], "base_dt": p.get('today_str', p_common['today_str']), "upd_stkpc_tp": "1"}), # 오늘 기준 (수정주가)
            ("chart", {"stk_cd": p_common['placeholder_stk_kosdaq'], "base_dt": p.get('today_str', p_common['today_str']), "upd_stkpc_tp": "0"}), # 오늘 기준 (코스닥, 원본주가)
            ("chart", {"stk_cd": p['stk_cd'], "base_dt": p.get('month_ago_str', p_common['month_ago_str']), "upd_stkpc_tp": "1"}) # 한달 전 기준 (수정주가)
        ],
        "ka10082": lambda p: [ # 주식주봉차트조회요청 (p202) - upd_stkpc_tp '1' 또는 '0' 추가
            ("chart", {"stk_cd": p['stk_cd'], "base_dt": p.get('today_str', p_common['today_str']), "upd_stkpc_tp": "1"}), # 오늘 기준 (수정주가)
            ("chart", {"stk_cd": p_common['placeholder_stk_kosdaq'], "base_dt": p.get('two_weeks_ago_str', p_common['two_weeks_ago_str']), "upd_stkpc_tp": "0"}), # 2주 전 기준 (코스닥, 원본주가)
            ("chart", {"stk_cd": p['stk_cd'], "base_dt": p.get('six_months_ago_str', p_common['six_months_ago_str']), "upd_stkpc_tp": "1"}) # 6개월 전 기준 (수정주가)
        ],
        "ka10083": lambda p: [ # 주식월봉차트조회요청 (p204) - upd_stkpc_tp '1' 또는 '0' 추가
             ("chart", {"stk_cd": p['stk_cd'], "base_dt": p.get('today_str', p_common['today_str']), "upd_stkpc_tp": "1"}), # 오늘 기준 (수정주가)
             ("chart", {"stk_cd": p_common['placeholder_stk_kosdaq'], "base_dt": p.get('today_str', p_common['today_str']), "upd_stkpc_tp": "0"}), # 오늘 기준 (코스닥, 원본주가)
             ("chart", {"stk_cd": p['stk_cd'], "base_dt": p.get('year_ago_str', p_common['year_ago_str']), "upd_stkpc_tp": "1"}) # 1년 전 기준 (수정주가)
        ],
        "ka10094": lambda p: [ # 주식년봉차트조회요청 (p220) - upd_stkpc_tp '1' 또는 '0' 추가
             ("chart", {"stk_cd": p['stk_cd'], "base_dt": p.get('today_str', p_common['today_str']), "upd_stkpc_tp": "1"}), # 올해 기준 (수정주가)
             ("chart", {"stk_cd": p_common['placeholder_stk_kosdaq'], "base_dt": p.get('today_str', p_common['today_str']), "upd_stkpc_tp": "0"}), # 올해 기준 (코스닥, 원본주가)
             ("chart", {"stk_cd": p['stk_cd'], "base_dt": p.get('year_ago_str', p_common['year_ago_str']), "upd_stkpc_tp": "1"}) # 1년 전 기준 (수정주가)
        ],
        "ka10060": lambda p: [ # 종목별투자자기관별차트요청 (p158)
            ("chart", {"dt": p.get('today_str', p_common['today_str']), "stk_cd": p['stk_cd'], "amt_qty_tp": "1", "trde_tp": "0", "unit_tp": "1000"}), # 금액 순매수
            ("chart", {"dt": p.get('today_str', p_common['today_str']), "stk_cd": p['stk_cd'], "amt_qty_tp": "2", "trde_tp": "0", "unit_tp": "1000"}), # 수량 순매수
            ("chart", {"dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "stk_cd": p['stk_cd'], "amt_qty_tp": "1", "trde_tp": "1", "unit_tp": "1"}) # 전일 금액 매수 (단주)
        ],
        "ka10064": lambda p: [ # 장중투자자별매매차트요청 (p168)
            ("chart", {"mrkt_tp": "001", "amt_qty_tp": "1", "trde_tp": "0", "stk_cd": p['stk_cd']}), # 코스피 금액 순매수 (성공)
            # ▼▼▼ [다각화 시도] 코스닥 종목을 거래량이 많은 '에코프로'로 변경 ▼▼▼
            ("chart", {"mrkt_tp": "101", "amt_qty_tp": "2", "trde_tp": "0", "stk_cd": "086520"}), # 코스닥 수량 순매수 (에코프로)
            ("chart", {"mrkt_tp": "001", "amt_qty_tp": "1", "trde_tp": "2", "stk_cd": p['stk_cd']})  # 코스피 금액 매도 (성공)
        ],
        "ka20004": lambda p: [ # 업종틱차트조회요청 (p260)
            ("chart", {"inds_cd": p.get('inds_cd', p_common['placeholder_inds']), "tic_scope": "1"}), # 코스피 1틱
            ("chart", {"inds_cd": p_common['placeholder_inds_kosdaq'], "tic_scope": "5"}), # 코스닥 5틱
            ("chart", {"inds_cd": "201", "tic_scope": "10"}) # KOSPI200 10틱
        ],
        "ka20005": lambda p: [ # 업종분봉조회요청 (p262)
            ("chart", {"inds_cd": p.get('inds_cd', p_common['placeholder_inds']), "tic_scope": "5"}), # 코스피 5분
            ("chart", {"inds_cd": p_common['placeholder_inds_kosdaq'], "tic_scope": "30"}), # 코스닥 30분
            ("chart", {"inds_cd": "201", "tic_scope": "60"}) # KOSPI200 60분
        ],
        "ka20006": lambda p: [ # 업종일봉조회요청 (p264)
            ("chart", {"inds_cd": p.get('inds_cd', p_common['placeholder_inds']), "base_dt": p.get('today_str', p_common['today_str'])}), # 코스피
            ("chart", {"inds_cd": "101", "base_dt": p.get('today_str', p_common['today_str'])}) # 코스닥
        ],
        "ka20007": lambda p: [ # 업종주봉조회요청 (p266)
            ("chart", {"inds_cd": p.get('inds_cd', p_common['placeholder_inds']), "base_dt": p.get('today_str', p_common['today_str'])}), # 코스피
            ("chart", {"inds_cd": "101", "base_dt": p.get('today_str', p_common['today_str'])}) # 코스닥
        ],
        "ka20008": lambda p: [ # 업종월봉조회요청 (p268)
            ("chart", {"inds_cd": p.get('inds_cd', p_common['placeholder_inds']), "base_dt": p.get('today_str', p_common['today_str'])}), # 코스피
            ("chart", {"inds_cd": "101", "base_dt": p.get('today_str', p_common['today_str'])}) # 코스닥
        ],
        "ka20019": lambda p: [ # 업종년봉조회요청 (p273)
            ("chart", {"inds_cd": p.get('inds_cd', p_common['placeholder_inds']), "base_dt": p.get('today_str', p_common['today_str'])}), # 코스피
            ("chart", {"inds_cd": "101", "base_dt": p.get('today_str', p_common['today_str'])}) # 코스닥
        ],
        "ka50079": lambda p: [ # 금현물틱차트조회요청 (p322)
            ("chart", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "tic_scope": "1", "upd_stkpc_tp": "1"}), # 1틱
            ("chart", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "tic_scope": "5", "upd_stkpc_tp": "1"}) # 5틱
        ],
        "ka50080": lambda p: [ # 금현물분봉차트조회요청 (p324)
            ("chart", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "tic_scope": "1", "upd_stkpc_tp": "1"}), # 1분
            ("chart", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "tic_scope": "5", "upd_stkpc_tp": "1"}) # 5분
        ],
        "ka50081": lambda p: [("chart", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "base_dt": p.get('today_str', p_common['today_str']), "upd_stkpc_tp": "1"})], # 금현물일봉차트조회요청 (p326)
        "ka50082": lambda p: [("chart", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "base_dt": p.get('today_str', p_common['today_str']), "upd_stkpc_tp": "1"})], # 금현물주봉차트조회요청 (p328)
        "ka50083": lambda p: [("chart", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "base_dt": p.get('today_str', p_common['today_str']), "upd_stkpc_tp": "1"})], # 금현물월봉차트조회요청 (p330)
        "ka50091": lambda p: [ # 금현물당일틱차트조회요청 (p334)
            ("chart", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "tic_scope": "1"}), # 1틱
            ("chart", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "tic_scope": "5"})  # 5틱
        ],
        "ka50092": lambda p: [ # 금현물당일분봉차트조회요청 (p336)
            ("chart", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "tic_scope": "1"}), # 1분
            ("chart", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "tic_scope": "5"})  # 5분
        ],

        # === Ranking Info (국내주식 > 순위정보) ===
        # Expanded variants for ranking APIs
        "ka10020": lambda p: [ # 호가잔량상위요청 (p69)
            ("rkinfo", {"mrkt_tp":"001", "sort_tp":"1", "trde_qty_tp":"00000", "stk_cnd":"0", "crd_cnd":"0", "stex_tp":"1"}), # 코스피 순매수잔량 (거래량 0000 -> 00000 수정)
            ("rkinfo", {"mrkt_tp":"101", "sort_tp":"3", "trde_qty_tp":"00000", "stk_cnd":"0", "crd_cnd":"0", "stex_tp":"1"}), # 코스닥 매수비율 (거래량 0000 -> 00000 수정)
            ("rkinfo", {"mrkt_tp":"001", "sort_tp":"2", "trde_qty_tp":"00010", "stk_cnd":"1", "crd_cnd":"0", "stex_tp":"1"}), # 코스피 순매도잔량 (만주, 관리제외) (거래량 0010 -> 00010 수정)
            ("rkinfo", {"mrkt_tp":"101", "sort_tp":"4", "trde_qty_tp":"00050", "stk_cnd":"0", "crd_cnd":"9", "stex_tp":"1"})  # 코스닥 매도비율 (5만주, 신용전체) (거래량 0050 -> 00050 수정)
        ],
        "ka10021": lambda p: [ # 호가잔량급증요청 (p72)
            ("rkinfo", {"mrkt_tp": "001", "trde_tp":"1", "sort_tp":"1", "trde_qty_tp":"10", "stk_cnd":"0", "tm_tp": "5", "stex_tp":"3"}), # 코스피 매수 급증량 5분 (성공)
            # ▼▼▼ [다각화 시도] 코스닥 + 매도 + 급증률 + 1분 ▼▼▼
            ("rkinfo", {"mrkt_tp": "101", "trde_tp":"2", "sort_tp":"2", "trde_qty_tp":"1", "stk_cnd":"0", "tm_tp": "1", "stex_tp":"3"}), # 코스닥 매도 급증률 1분
            ("rkinfo", {"mrkt_tp": "001", "trde_tp":"1", "sort_tp":"2", "trde_qty_tp":"100", "stk_cnd":"1", "tm_tp": "30", "stex_tp":"3"}), # 코스피 매수 급증률 30분 (성공)
            ("rkinfo", {"mrkt_tp": "101", "trde_tp":"2", "sort_tp":"1", "trde_qty_tp":"1", "stk_cnd":"0", "tm_tp": "1", "stex_tp":"3"})  # 코스닥 매도 급증량 1분 (성공)
        ],
        "ka10022": lambda p: [ # 잔량율급증요청 (p74)
            ("rkinfo", {"mrkt_tp":"001", "rt_tp":"1", "tm_tp":"5", "trde_qty_tp":"10", "stk_cnd":"0", "stex_tp":"3"}), # 코스피 매수/매도비율 5분
            ("rkinfo", {"mrkt_tp":"101", "rt_tp":"2", "tm_tp":"10", "trde_qty_tp":"50", "stk_cnd":"0", "stex_tp":"3"}), # 코스닥 매도/매수비율 10분
            ("rkinfo", {"mrkt_tp":"001", "rt_tp":"1", "tm_tp":"30", "trde_qty_tp":"100", "stk_cnd":"1", "stex_tp":"3"}), # 코스피 매수/매도비율 30분 (10만주, 관리제외)
            ("rkinfo", {"mrkt_tp":"101", "rt_tp":"2", "tm_tp":"1", "trde_qty_tp":"5", "stk_cnd":"0", "stex_tp":"3"})  # 코스닥 매도/매수비율 1분 (5천주)
        ],
        "ka10023": lambda p: [ # 거래량급증요청 (p76)
            ("rkinfo", {"mrkt_tp": "000", "trde_qty_tp": "100", "sort_tp": "2", "tm_tp":"1", "tm":"5", "stk_cnd":"0", "pric_tp":"0", "stex_tp":"3"}), # 전체 5분 급증률 (10만주)
            ("rkinfo", {"mrkt_tp": "001", "trde_qty_tp": "50", "sort_tp": "1", "tm_tp":"2", "stk_cnd":"0", "pric_tp":"0", "stex_tp":"3"}), # 코스피 전일대비 급증량 (5만주)
            ("rkinfo", {"mrkt_tp": "101", "trde_qty_tp": "500", "sort_tp": "3", "tm_tp":"1", "tm":"30", "stk_cnd":"1", "pric_tp":"8", "stex_tp":"3"}), # 코스닥 30분 급감량 (50만주, 관리제외, 1천원이상)
            ("rkinfo", {"mrkt_tp": "000", "trde_qty_tp": "1000", "sort_tp": "4", "tm_tp":"2", "stk_cnd":"0", "pric_tp":"0", "stex_tp":"3"}) # 전체 전일대비 급감률 (백만주)
        ],
        "ka10027": lambda p: [ # 전일대비등락률상위요청 (p86)
            ("rkinfo", {"mrkt_tp": "001", "sort_tp": "1", "trde_qty_cnd": "0100", "stk_cnd":"1", "crd_cnd":"0", "updown_incls":"1", "pric_cnd": "0", "trde_prica_cnd":"0", "stex_tp":"3"}), # 코스피 상승률 (관리제외, 10만주)
            ("rkinfo", {"mrkt_tp": "101", "sort_tp": "3", "trde_qty_cnd": "0000", "stk_cnd":"0", "crd_cnd":"0", "updown_incls":"1", "pric_cnd": "8", "trde_prica_cnd":"0", "stex_tp":"3"}), # 코스닥 하락률 (1천원이상)
            ("rkinfo", {"mrkt_tp": "000", "sort_tp": "2", "trde_qty_cnd": "0500", "stk_cnd":"0", "crd_cnd":"0", "updown_incls":"1", "pric_cnd": "0", "trde_prica_cnd":"10", "stex_tp":"3"}), # 전체 상승폭 (50만주, 1억이상)
            ("rkinfo", {"mrkt_tp": "000", "sort_tp": "4", "trde_qty_cnd": "0000", "stk_cnd":"11", "crd_cnd":"0", "updown_incls":"0", "pric_cnd": "0", "trde_prica_cnd":"0", "stex_tp":"3"})  # 전체 하락폭 (정리매매제외, 상하한제외)
        ],
        "ka10029": lambda p: [ # 예상체결등락률상위요청 (p92)
            ("rkinfo", {"mrkt_tp": "000", "sort_tp": "1", "trde_qty_cnd": "0", "stk_cnd": "0", "crd_cnd": "0", "pric_cnd": "0", "stex_tp": "3"}), # 전체 상승률 (성공)
            ("rkinfo", {"mrkt_tp": "001", "sort_tp": "4", "trde_qty_cnd": "10", "stk_cnd": "0", "crd_cnd": "0", "pric_cnd": "0", "stex_tp": "3"}), # 코스피 하락률 (성공)
            ("rkinfo", {"mrkt_tp": "101", "sort_tp": "6", "trde_qty_cnd": "50", "stk_cnd": "1", "crd_cnd": "0", "pric_cnd": "0", "stex_tp": "3"}), # 코스닥 체결량 (성공)
            # ▼▼▼ [다각화 시도] 상한가(7) -> 상승폭(2) (데이터 존재 확률) ▼▼▼
            ("rkinfo", {"mrkt_tp": "000", "sort_tp": "2", "trde_qty_cnd": "0", "stk_cnd": "0", "crd_cnd": "0", "pric_cnd": "0", "stex_tp": "3"})  # 전체 상승폭
        ],
        "ka10030": lambda p: [ # 당일거래량상위요청 (p95)
            ("rkinfo", {"mrkt_tp": "000", "sort_tp": "1", "mang_stk_incls": "0", "crd_tp": "0", "trde_qty_tp": "0", "pric_tp": "0", "trde_prica_tp": "0", "mrkt_open_tp": "1", "stex_tp":"3"}), # 전체 거래량 (장중)
            ("rkinfo", {"mrkt_tp": "001", "sort_tp": "3", "mang_stk_incls": "0", "crd_tp": "0", "trde_qty_tp": "0", "pric_tp": "0", "trde_prica_tp": "0", "mrkt_open_tp": "0", "stex_tp":"3"}), # 코스피 거래대금 (전체시간)
            ("rkinfo", {"mrkt_tp": "101", "sort_tp": "2", "mang_stk_incls": "1", "crd_tp": "9", "trde_qty_tp": "1000", "pric_tp": "8", "trde_prica_tp": "100", "mrkt_open_tp": "1", "stex_tp":"3"}) # 코스닥 회전율 (관리포함, 신용전체, 백만주, 천원이상, 10억이상, 장중)
        ],
        "ka10031": lambda p: [ # 전일거래량상위요청 (p98)
            ("rkinfo", {"mrkt_tp": "001", "qry_tp": "1", "rank_strt": "1", "rank_end": "50", "stex_tp":"3"}), # 코스피 거래량 Top 50
            ("rkinfo", {"mrkt_tp": "101", "qry_tp": "2", "rank_strt": "1", "rank_end": "100", "stex_tp":"3"}), # 코스닥 거래대금 Top 100
            ("rkinfo", {"mrkt_tp": "000", "qry_tp": "1", "rank_strt": "51", "rank_end": "100", "stex_tp":"3"}) # 전체 거래량 51-100위
        ],
        "ka10032": lambda p: [ # 거래대금상위요청 (p101)
            ("rkinfo", {"mrkt_tp": "001", "mang_stk_incls":"0", "stex_tp":"3"}), # 코스피 관리제외
            ("rkinfo", {"mrkt_tp": "101", "mang_stk_incls":"1", "stex_tp":"3"}), # 코스닥 관리포함
            ("rkinfo", {"mrkt_tp": "000", "mang_stk_incls":"0", "stex_tp":"3"})  # 전체 관리제외
        ],
        "ka10033": lambda p: [ # 신용비율상위요청 (p103)
            ("rkinfo", {"mrkt_tp": "001", "trde_qty_tp": "100", "stk_cnd":"0", "updown_incls":"1", "crd_cnd":"0", "stex_tp":"3"}), # 코스피 10만주 이상
            ("rkinfo", {"mrkt_tp": "101", "trde_qty_tp": "0", "stk_cnd":"1", "updown_incls":"1", "crd_cnd":"0", "stex_tp":"3"}), # 코스닥 관리제외
            ("rkinfo", {"mrkt_tp": "000", "trde_qty_tp": "500", "stk_cnd":"5", "updown_incls":"0", "crd_cnd":"1", "stex_tp":"3"}) # 전체 50만주 (증100제외, 상하한제외, A군) (crd_cnd 'A'->'1')
        ],
        "ka10034": lambda p: [ # 외인기간별매매상위요청 (p106)
            ("rkinfo", {"mrkt_tp": "001", "trde_tp": "2", "dt": "5", "stex_tp": "1"}), # 코스피 5일 순매수
            ("rkinfo", {"mrkt_tp": "101", "trde_tp": "1", "dt": "10", "stex_tp": "1"}), # 코스닥 10일 순매도
            ("rkinfo", {"mrkt_tp": "000", "trde_tp": "3", "dt": "20", "stex_tp": "1"}), # 전체 20일 순매매
            ("rkinfo", {"mrkt_tp": "001", "trde_tp": "2", "dt": "0", "stex_tp": "1"})  # 코스피 당일 순매수
        ],
        "ka10035": lambda p: [ # 외인연속순매매상위요청 (p108)
            ("rkinfo", {"mrkt_tp": "001", "trde_tp": "2", "base_dt_tp": "0", "stex_tp": "1"}), # 코스피 연속순매수 당일
            ("rkinfo", {"mrkt_tp": "101", "trde_tp": "1", "base_dt_tp": "1", "stex_tp": "1"}), # 코스닥 연속순매도 전일
            ("rkinfo", {"mrkt_tp": "000", "trde_tp": "2", "base_dt_tp": "1", "stex_tp": "1"})  # 전체 연속순매수 전일
        ],
        "ka10036": lambda p: [ # 외인한도소진율증가상위 (p111)
            ("rkinfo", {"mrkt_tp": "001", "dt": "5", "stex_tp": "1"}), # 코스피 5일
            ("rkinfo", {"mrkt_tp": "101", "dt": "20", "stex_tp": "1"}), # 코스닥 20일
            ("rkinfo", {"mrkt_tp": "000", "dt": "60", "stex_tp": "1"})  # 전체 60일
        ],
        "ka10037": lambda p: [ # 외국계창구매매상위요청 (p113)
            ("rkinfo", {"mrkt_tp": "000", "dt": "0", "trde_tp": "1", "sort_tp": "1", "stex_tp": "1"}), # 당일 순매수 금액
            ("rkinfo", {"mrkt_tp": "001", "dt": "5", "trde_tp": "2", "sort_tp": "2", "stex_tp": "1"}), # 코스피 5일 순매도 수량
            ("rkinfo", {"mrkt_tp": "101", "dt": "10", "trde_tp": "3", "sort_tp": "1", "stex_tp": "1"}), # 코스닥 10일 매수 금액
            ("rkinfo", {"mrkt_tp": "000", "dt": "20", "trde_tp": "4", "sort_tp": "2", "stex_tp": "1"}) # 전체 20일 매도 수량
        ],
        "ka10038": lambda p: [ # 종목별증권사순위요청 (p116)
            ("rkinfo", {"stk_cd": p['stk_cd'], "strt_dt": p.get('today_str', p_common['today_str']), "end_dt": p.get('today_str', p_common['today_str']), "qry_tp": "1", "dt":"1"}), # 당일 순매도
            ("rkinfo", {"stk_cd": p['stk_cd'], "strt_dt": p.get('today_str', p_common['today_str']), "end_dt": p.get('today_str', p_common['today_str']), "qry_tp": "2", "dt":"1"}), # 당일 순매수
            ("rkinfo", {"stk_cd": p['stk_cd'], "strt_dt": p.get('week_ago_str', p_common['week_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "qry_tp": "2", "dt":"5"})  # 5일 순매수
        ],
        "ka10039": lambda p: [ # 증권사별매매상위요청 (p118)
            ("rkinfo", {"mmcm_cd": "050", "trde_qty_tp": "0", "trde_tp": "1", "dt": "1", "stex_tp": "3"}), # 키움 순매수 1일
            ("rkinfo", {"mmcm_cd": "003", "trde_qty_tp": "10", "trde_tp": "2", "dt": "5", "stex_tp": "3"}), # 한국투자 순매도 5일 (만주 이상)
            ("rkinfo", {"mmcm_cd": "005", "trde_qty_tp": "0", "trde_tp": "1", "dt": "10", "stex_tp": "3"})  # 미래에셋 순매수 10일
        ],
        "ka10040": lambda p: [ # 당일주요거래원요청 (p120)
            ("rkinfo", {"stk_cd": p['stk_cd']}), # 코스피
            ("rkinfo", {"stk_cd": p_common['placeholder_stk_kosdaq']}) # 코스닥
        ],
        "ka10042": lambda p: [ # 순매수거래원순위요청 (p123)
            ("rkinfo", {"stk_cd": p['stk_cd'], "qry_dt_tp":"0", "pot_tp":"0", "sort_base":"1", "dt":"5"}), # 5일 종가순
            ("rkinfo", {"stk_cd": p['stk_cd'], "qry_dt_tp":"0", "pot_tp":"0", "sort_base":"2", "dt":"10"}), # 10일 날짜순
            ("rkinfo", {"stk_cd": p['stk_cd'], "qry_dt_tp":"1", "strt_dt": p.get('month_ago_str', p_common['month_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "pot_tp":"0", "sort_base":"1"}) # 지정기간(1달) 종가순
        ],
        "ka10053": lambda p: [ # 당일상위이탈원요청 (p146)
            ("rkinfo", {"stk_cd": p['stk_cd']}), # 코스피
            ("rkinfo", {"stk_cd": p_common['placeholder_stk_kosdaq']}) # 코스닥
        ],
        "ka10062": lambda p: [ # 동일순매매순위요청 (p163)
            ("rkinfo", {"strt_dt": p.get('today_str', p_common['today_str']), "end_dt": p.get('today_str', p_common['today_str']), "mrkt_tp": "001", "trde_tp": "1", "sort_cnd": "1", "unit_tp": "1", "stex_tp": "3"}), # 당일 코스피 순매수 수량
            ("rkinfo", {"strt_dt": p.get('week_ago_str', p_common['week_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "mrkt_tp": "101", "trde_tp": "2", "sort_cnd": "2", "unit_tp": "1", "stex_tp": "3"}), # 1주 코스닥 순매도 금액
            ("rkinfo", {"strt_dt": p.get('month_ago_str', p_common['month_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "mrkt_tp": "000", "trde_tp": "1", "sort_cnd": "1", "unit_tp": "1000", "stex_tp": "3"}) # 1달 전체 순매수 수량 (천주)
        ],
        "ka10065": lambda p: [ # 장중투자자별매매상위요청 (p170)
            ("rkinfo", {"trde_tp": "1", "mrkt_tp": "001", "orgn_tp": "9000"}), # 코스피 외국인 순매수
            ("rkinfo", {"trde_tp": "2", "mrkt_tp": "101", "orgn_tp": "9999"}), # 코스닥 기관계 순매도
            ("rkinfo", {"trde_tp": "1", "mrkt_tp": "000", "orgn_tp": "6000"})   # 전체 연기금 순매수
        ],
        "ka10098": lambda p: [ # 시간외단일가등락율순위요청 (p226)
            ("rkinfo", {"mrkt_tp": "000", "sort_base": "1", "stk_cnd": "0", "trde_qty_cnd": "0", "crd_cnd": "0", "trde_prica": "0"}), # 기존 (상승률)
            # ▼▼▼ [다각화 시도] 거래량/거래대금 조건 추가 ▼▼▼
            ("rkinfo", {"mrkt_tp": "001", "sort_base": "3", "stk_cnd": "1", "trde_qty_cnd": "100", "crd_cnd": "0", "trde_prica": "10"}), # 코스피 하락률 (관리제외, 천주이상, 1천만원이상)
            ("rkinfo", {"mrkt_tp": "101", "sort_base": "5", "stk_cnd": "0", "trde_qty_cnd": "500", "crd_cnd": "0", "trde_prica": "50"})  # 코스닥 보합 (5천주이상, 5천만원이상)
        ],
        "ka90009": lambda p: [ # 외국인기관매매상위요청 (p365)
            ("rkinfo", {"mrkt_tp": "001", "amt_qty_tp": "1", "qry_dt_tp": "1", "date": p.get('today_str', p_common['today_str']), "stex_tp": "1"}), # 코스피 금액 당일
            ("rkinfo", {"mrkt_tp": "101", "amt_qty_tp": "2", "qry_dt_tp": "1", "date": p.get('one_day_ago_str', p_common['one_day_ago_str']), "stex_tp": "1"}), # 코스닥 수량 전일
            ("rkinfo", {"mrkt_tp": "000", "amt_qty_tp": "1", "qry_dt_tp": "0", "stex_tp": "1"}) # 전체 금액 (날짜 미포함 - 최근 거래일 자동 조회될 것으로 예상)
        ],

        # === Foreigner/Institution (국내주식 > 기관/외국인) ===
        # !! Requires 'frgnistt' path mapping in kiwoom.py !!
        "ka10008": lambda p: [("frgnistt", {"stk_cd": p['stk_cd']})], # 주식외국인종목별매매동향 (p38)
        "ka10009": lambda p: [("frgnistt", {"stk_cd": p['stk_cd']})], # 주식기관요청 (p41)
        "ka10131": lambda p: [ # 기관외국인연속매매현황요청 (p237)
            ("frgnistt", {"dt": "5", "mrkt_tp": "001", "netslmt_tp": "2", "stk_inds_tp": "0", "amt_qty_tp": "0", "stex_tp": "1"}), # 코스피 5일 금액
            ("frgnistt", {"dt": "10", "mrkt_tp": "101", "netslmt_tp": "2", "stk_inds_tp": "0", "amt_qty_tp": "1", "stex_tp": "1"}), # 코스닥 10일 수량
            ("frgnistt", {"dt": "0", "strt_dt": p.get('week_ago_str', p_common['week_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "mrkt_tp": "001", "netslmt_tp": "2", "stk_inds_tp": "0", "amt_qty_tp": "0", "stex_tp": "1"}) # 코스피 1주 기간지정 금액
        ],
        "ka52301": lambda p: [("frgnistt", {})], # 금현물투자자현황 (p342)

        # === Sector/Industry (국내주식 > 업종) ===
        # !! Requires 'sect' path mapping in kiwoom.py !!
        "ka10010": lambda p: [ # 업종프로그램요청 (p43)
            ("sect", {"stk_cd": p.get('inds_cd', p_common['placeholder_inds'])}), # 코스피 종합
            ("sect", {"stk_cd": "201"}), # KOSPI200
            # ▼▼▼ [다각화 시도] 코스닥 업종 추가 ▼▼▼
            ("sect", {"stk_cd": p_common['placeholder_inds_kosdaq']}) # 코스닥 종합
        ],
        "ka10051": lambda p: [ # 업종별투자자순매수요청 (p141)
            ("sect", {"mrkt_tp": "0", "amt_qty_tp": "0", "base_dt": p.get('today_str', p_common['today_str']), "stex_tp": "3"}), # 코스피 금액 당일
            ("sect", {"mrkt_tp": "1", "amt_qty_tp": "1", "base_dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "stex_tp": "3"}), # 코스닥 수량 전일
            ("sect", {"mrkt_tp": "0", "amt_qty_tp": "1", "base_dt": p.get('today_str', p_common['today_str']), "stex_tp": "3"})  # 코스피 수량 당일
        ],
        "ka20001": lambda p: [ # 업종현재가요청 (p252)
            ("sect", {"mrkt_tp": "0", "inds_cd": p.get('inds_cd', p_common['placeholder_inds'])}), # 코스피 종합
            ("sect", {"mrkt_tp": "1", "inds_cd": p_common['placeholder_inds_kosdaq']}), # 코스닥 종합
            ("sect", {"mrkt_tp": "2", "inds_cd": "201"}) # KOSPI200
        ],
        "ka20002": lambda p: [ # 업종별주가요청 (p255)
            ("sect", {"mrkt_tp": "0", "inds_cd": p.get('inds_cd', p_common['placeholder_inds']), "stex_tp": "1"}), # 코스피 종합
            ("sect", {"mrkt_tp": "1", "inds_cd": p_common['placeholder_inds_kosdaq'], "stex_tp": "1"}), # 코스닥 종합
            ("sect", {"mrkt_tp": "2", "inds_cd": "201", "stex_tp": "1"}) # KOSPI200
        ],
        "ka20003": lambda p: [ # 전업종지수요청 (p258)
            ("sect", {"inds_cd": "001"}), # 코스피
            ("sect", {"inds_cd": "101"})  # 코스닥
        ],
        "ka20009": lambda p: [ # 업종현재가일별요청 (p270)
            ("sect", {"mrkt_tp": "0", "inds_cd": p.get('inds_cd', p_common['placeholder_inds'])}), # 코스피 종합
            ("sect", {"mrkt_tp": "1", "inds_cd": p_common['placeholder_inds_kosdaq']}), # 코스닥 종합
            ("sect", {"mrkt_tp": "2", "inds_cd": "201"}) # KOSPI200
        ],

        # === Theme (국내주식 > 테마) ===
        # !! Requires 'thme' path mapping in kiwoom.py !!
        "ka90001": lambda p: [ # 테마그룹별요청 (p345)
            ("thme", {"qry_tp": "0", "date_tp": "10", "flu_pl_amt_tp": "1", "stex_tp": "1"}), # 전체 10일 수익률 (성공)
            ("thme", {"qry_tp": "0", "date_tp": "5", "flu_pl_amt_tp": "3", "stex_tp": "1"}),  # 전체 5일 등락률 (성공)
            # ▼▼▼ [다각화 시도] '반도체' -> '2차전지' (데이터 존재 확률) ▼▼▼
            ("thme", {"qry_tp": "1", "thema_nm": "2차전지", "date_tp": "10", "flu_pl_amt_tp": "1", "stex_tp": "1"}), # '2차전지' 테마 검색
            ("thme", {"qry_tp": "2", "stk_cd": p['stk_cd'], "date_tp": "10", "flu_pl_amt_tp": "1", "stex_tp": "1"}) # 특정 종목 포함 (성공)
        ],
        "ka90002": lambda p: [ # 테마구성종목요청 (p347)
            ("thme", {"date_tp": "2", "thema_grp_cd": p.get('thema_cd', p_common['placeholder_thema']), "stex_tp": "1"}), # 반도체 대표주
            ("thme", {"date_tp": "10", "thema_grp_cd": "452", "stex_tp": "1"}) # SNS (10일 기준)
        ],

        # === Short Selling (국내주식 > 공매도) ===
        # !! Requires 'shsa' path mapping in kiwoom.py !!
        "ka10014": lambda p: [ # 공매도추이요청 (p50)
            ("shsa", {"stk_cd": p['stk_cd'], "tm_tp": "1", "strt_dt": p.get('month_ago_str', p_common['month_ago_str']), "end_dt": p.get('today_str', p_common['today_str'])}), # 1달
            ("shsa", {"stk_cd": p['stk_cd'], "tm_tp": "1", "strt_dt": p.get('year_ago_str', p_common['year_ago_str']), "end_dt": p.get('today_str', p_common['today_str'])}), # 1년
            ("shsa", {"stk_cd": p_common['placeholder_stk_kosdaq'], "tm_tp": "1", "strt_dt": p.get('two_weeks_ago_str', p_common['two_weeks_ago_str']), "end_dt": p.get('today_str', p_common['today_str'])}) # 코스닥 2주
        ],

        # === ELW (국내주식 > ELW) ===
        # !! Requires 'elw' path mapping in kiwoom.py !!
        "ka10048": lambda p: [ # ELW일별민감도지표요청 (p136)
             # ▼▼▼ [수정] TypeError 방지. 유효한 ELW 코드가 없어 테스트를 안전하게 건너뜀. ▼▼▼
        ],
        "ka10050": lambda p: [ # ELW민감도지표요청 (p139)
             # ▼▼▼ [수정] TypeError 방지. 유효한 ELW 코드가 없어 테스트를 안전하게 건너뜀. ▼▼▼
        ],
        "ka30001": lambda p: [ # ELW가격급등락요청 (p277)
            ("elw", {"flu_tp": "1", "tm_tp": "1", "tm": "5", "trde_qty_tp": "0", "isscomp_cd": "000000000000", "bsis_aset_cd": "000000000000", "rght_tp": "000", "lpcd": "000000000000", "trde_end_elwskip": "0"}), # 5분 급등
            ("elw", {"flu_tp": "2", "tm_tp": "2", "tm": "1", "trde_qty_tp": "10", "isscomp_cd": "000000000003", "bsis_aset_cd": "201", "rght_tp": "002", "lpcd": "000000000000", "trde_end_elwskip": "1"}) # 1일 급락 (만주, 한투, KOSPI200, 풋, 종료제외)
        ],
        "ka30002": lambda p: [ # 거래원별ELW순매매상위요청 (p279)
            ("elw", {"isscomp_cd": "003", "trde_qty_tp": "0", "trde_tp": "1", "dt": "5", "trde_end_elwskip": "0"}), # 한국투자 순매수 5일
            ("elw", {"isscomp_cd": "005", "trde_qty_tp": "50", "trde_tp": "2", "dt": "10", "trde_end_elwskip": "1"}), # 미래에셋 순매도 10일 (5만주, 종료제외)
            ("elw", {"isscomp_cd": "017", "trde_qty_tp": "0", "trde_tp": "1", "dt": "60", "trde_end_elwskip": "0"})  # KB증권 순매수 60일
        ],
        "ka30003": lambda p: [ # ELWLP보유일별추이요청 (p281)
             ("elw", {"bsis_aset_cd": "J0669721F", "base_dt": p.get('today_str', p_common['today_str'])}), # 기존 (성공)
             # ▼▼▼ [다각화 시도] 기초자산 종목 코드로 조회 ▼▼▼
             ("elw", {"bsis_aset_cd": p.get('stk_cd', p_common['placeholder_stk_kospi']), "base_dt": p.get('one_day_ago_str', p_common['one_day_ago_str'])}), # 어제 (SK하이닉스)
             ("elw", {"bsis_aset_cd": p_common['placeholder_stk_kosdaq'], "base_dt": p.get('one_day_ago_str', p_common['one_day_ago_str'])}) # 어제 (엘앤에프)
        ],
        "ka30004": lambda p: [ # ELW괴리율요청 (p283)
            ("elw", {"isscomp_cd": "000000000000", "bsis_aset_cd": "201", "rght_tp": "001", "lpcd": "000000000000", "trde_end_elwskip": "0"}), # KOSPI200 콜 (성공)
            # ▼▼▼ [다각화 시도] 기초자산 코드를 '종목코드' 및 '업종코드'로 변경 ▼▼▼
            ("elw", {"isscomp_cd": "000000000000", "bsis_aset_cd": p_common['placeholder_stk_kosdaq'], "rght_tp": "002", "lpcd": "000000000000", "trde_end_elwskip": "1"}), # 엘앤에프 풋
            ("elw", {"isscomp_cd": "000000000000", "bsis_aset_cd": p.get('stk_cd', p_common['placeholder_stk_kospi']), "rght_tp": "001", "lpcd": "000000000000", "trde_end_elwskip": "0"}), # SK하이닉스 콜
            ("elw", {"isscomp_cd": "000000000003", "bsis_aset_cd": "101", "rght_tp": "000", "lpcd": "000000000000", "trde_end_elwskip": "0"})  # 한국투자 KOSDAQ
        ],
        "ka30005": lambda p: [ # ELW조건검색요청 (p286)
            ("elw", {"isscomp_cd": "000000000000", "bsis_aset_cd": "201", "rght_tp": "1", "lpcd": "000000000000", "sort_tp": "0"}), # KOSPI200 콜 (성공)
            # ▼▼▼ [다각화 시도] 기초자산 코드를 '종목코드'로 변경 및 정렬 추가 ▼▼▼
            ("elw", {"isscomp_cd": "000000000000", "bsis_aset_cd": p_common['placeholder_stk_kosdaq'], "rght_tp": "2", "lpcd": "000000000000", "sort_tp": "5"}),  # 엘앤에프 풋 (거래량순)
            ("elw", {"isscomp_cd": "000000000000", "bsis_aset_cd": p.get('stk_cd', p_common['placeholder_stk_kospi']), "rght_tp": "1", "lpcd": "000000000000", "sort_tp": "6"})   # SK하이닉스 콜 (거래대금순)
        ],
        "ka30009": lambda p: [ # ELW등락율순위요청 (p289)
            ("elw", {"sort_tp": "1", "rght_tp": "001", "trde_end_skip": "0"}), # 콜 상승률
            ("elw", {"sort_tp": "3", "rght_tp": "002", "trde_end_skip": "1"}), # 풋 하락률 (종료제외)
            ("elw", {"sort_tp": "5", "rght_tp": "000", "trde_end_skip": "0"})  # 전체 거래량 (Sort TP 5 추가 가정)
        ],
        "ka30010": lambda p: [ # ELW잔량순위요청 (p291)
            ("elw", {"sort_tp": "1", "rght_tp": "001", "trde_end_skip": "0"}), # 콜 순매수잔량
            ("elw", {"sort_tp": "2", "rght_tp": "002", "trde_end_skip": "1"})  # 풋 순매도잔량 (종료제외)
        ],
        "ka30011": lambda p: [ # ELW근접율요청 (p293)
             # ▼▼▼ [수정] TypeError 방지. 유효한 ELW 코드가 없어 테스트를 안전하게 건너뜀. ▼▼▼
        ],
        "ka30012": lambda p: [ # ELW종목상세정보요청 (p295) - 유효한 코드로 변경
            ("elw", {"stk_cd": "J0669721F"}),
            ("elw", {"stk_cd": "J0036221D"})
        ],

        # === ETF (국내주식 > ETF) ===
        # !! Requires 'etf' path mapping in kiwoom.py !!
        "ka40001": lambda p: [ # ETF수익율요청 (p299)
            ("etf", {"stk_cd": p.get('etf_cd', p_common['placeholder_etf']), "etfobjt_idex_cd": "207", "dt": "1"}), # 1달 (KODEX 200)
            ("etf", {"stk_cd": p.get('etf_cd', p_common['placeholder_etf']), "etfobjt_idex_cd": "207", "dt": "3"}), # 1년 (KODEX 200)
            ("etf", {"stk_cd": p_common['placeholder_etf_alt'], "etfobjt_idex_cd": "207", "dt": "0"}) # 인버스 1주 (대상지수코드 '207' 사용 - 정확하지 않을 수 있음)
        ],
        "ka40002": lambda p: [ # ETF종목정보요청 (p301)
            ("etf", {"stk_cd": p.get('etf_cd', p_common['placeholder_etf'])}), # KODEX 200
            ("etf", {"stk_cd": p_common['placeholder_etf_alt']}) # KODEX 인버스
        ],
        "ka40003": lambda p: [ # ETF일별추이요청 (p303)
            ("etf", {"stk_cd": p.get('etf_cd', p_common['placeholder_etf'])}), # KODEX 200
            ("etf", {"stk_cd": p_common['placeholder_etf_alt']}) # KODEX 인버스
        ],
        "ka40004": lambda p: [ # ETF전체시세요청 (p305)
            ("etf", {"txon_type": "0", "navpre": "0", "mngmcomp": "3020", "txon_yn": "0", "trace_idex": "0", "stex_tp": "1"}), # 삼성 KODEX
            ("etf", {"txon_type": "0", "navpre": "0", "mngmcomp": "3191", "txon_yn": "0", "trace_idex": "0", "stex_tp": "1"}), # 미래에셋 TIGER
            ("etf", {"txon_type": "2", "navpre": "1", "mngmcomp": "0000", "txon_yn": "1", "trace_idex": "0", "stex_tp": "1"})  # 보유기간과세, NAV>전일종가, 과세
        ],
        "ka40006": lambda p: [ # ETF시간대별추이요청 (p308)
            ("etf", {"stk_cd": p.get('etf_cd', p_common['placeholder_etf'])}), # KODEX 200
            ("etf", {"stk_cd": p_common['placeholder_etf_alt']}) # KODEX 인버스
        ],
        "ka40007": lambda p: [ # ETF시간대별체결요청 (p310)
            ("etf", {"stk_cd": p.get('etf_cd', p_common['placeholder_etf'])}), # KODEX 200
            ("etf", {"stk_cd": p_common['placeholder_etf_alt']}) # KODEX 인버스
        ],
        "ka40008": lambda p: [ # ETF일자별체결요청 (p312)
            ("etf", {"stk_cd": p.get('etf_cd', p_common['placeholder_etf'])}), # KODEX 200
            ("etf", {"stk_cd": p_common['placeholder_etf_alt']}) # KODEX 인버스
        ],
        "ka40009": lambda p: [ # ETF NAV 요청 (p314)
            ("etf", {"stk_cd": p.get('etf_cd', p_common['placeholder_etf'])}), # KODEX 200
            ("etf", {"stk_cd": p_common['placeholder_etf_alt']}) # KODEX 인버스
        ],
        "ka40010": lambda p: [ # ETF 시간대별 추이(외국인/기관) 요청 (p316)
            ("etf", {"stk_cd": p.get('etf_cd', p_common['placeholder_etf'])}), # KODEX 200
            ("etf", {"stk_cd": p_common['placeholder_etf_alt']}) # KODEX 인버스
        ],

        # === Gold Spot (국내주식 > 금현물) ===
        # 주문 API (kt50000-kt50003) 는 Order 탭으로 이동
        "kt50020": lambda p: [("acnt", {})], # 금현물 잔고확인 (p449, 금현물 계좌 필요)
        "kt50021": lambda p: [("acnt", {})], # 금현물 예수금 (p452, 금현물 계좌 필요)
        "kt50030": lambda p: [ # 금현물 주문체결전체조회 (p454)
            ("acnt", {"ord_dt": p.get('today_str', p_common['today_str']), "qry_tp": "1", "mrkt_deal_tp": "1", "stk_bond_tp": "0", "slby_tp": "0", "stk_cd": "", "fr_ord_no": "", "dmst_stex_tp": "KRX"}), # 기존 (오늘)
            # ▼▼▼ [다각화 시도] 어제 날짜로 조회 ▼▼▼
            ("acnt", {"ord_dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "qry_tp": "2", "mrkt_deal_tp": "1", "stk_bond_tp": "0", "slby_tp": "2", "stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "fr_ord_no": "", "dmst_stex_tp": "KRX"}) # 어제 특정종목 매수 역순
        ],
        "kt50031": lambda p: [ # 금현물 주문체결조회 (p457)
            ("acnt", {"ord_dt": p.get('today_str', p_common['today_str']), "qry_tp": "1", "stk_bond_tp": "0", "sell_tp": "0", "stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "fr_ord_no": "", "dmst_stex_tp": "%"}), # 기존 (오늘)
            # ▼▼▼ [다각화 시도] 어제 날짜로 조회 ▼▼▼
            ("acnt", {"ord_dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "qry_tp": "1", "stk_bond_tp": "0", "sell_tp": "0", "stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "fr_ord_no": "", "dmst_stex_tp": "%"}) # 어제
        ],
        "kt50032": lambda p: [ # 금현물 거래내역조회 (p460)
            ("acnt", {"strt_dt": p.get('week_ago_str', p_common['week_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "tp": "0", "stk_cd": ""}), # 1주 전체
            ("acnt", {"strt_dt": p.get('today_str', p_common['today_str']), "end_dt": p.get('today_str', p_common['today_str']), "tp": "4", "stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold'])}) # 당일 특정종목 매수만
        ],
        "kt50075": lambda p: [ # 금현물 미체결조회 (p463)
            ("acnt", {"ord_dt": p.get('today_str', p_common['today_str']), "mrkt_deal_tp": "1", "stk_bond_tp": "0", "sell_tp": "0", "stk_cd": ""}), # 기존 (오늘)
            # ▼▼▼ [다각화 시도] 어제 날짜로 조회 ▼▼▼
            ("acnt", {"ord_dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "mrkt_deal_tp": "1", "stk_bond_tp": "0", "sell_tp": "2", "stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold'])}) # 어제 특정종목 매수만
        ],
        # === Stock Lending (국내주식 > 대차거래) ===
        # !! Requires 'slb' path mapping in kiwoom.py !!
        "ka10068": lambda p: [ # 대차거래추이요청(시장) (p175)
            ("slb", {"strt_dt": p.get('month_ago_str', p_common['month_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "all_tp": "1"}), # 1달
            ("slb", {"strt_dt": p.get('year_ago_str', p_common['year_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "all_tp": "1"}) # 1년
        ],
        "ka10069": lambda p: [ # 대차거래상위10종목요청 (p177)
            ("slb", {"strt_dt": p.get('today_str', p_common['today_str']), "end_dt": p.get('today_str', p_common['today_str']), "mrkt_tp": "001"}), # 코스피 당일
            ("slb", {"strt_dt": p.get('week_ago_str', p_common['week_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "mrkt_tp": "101"}) # 코스닥 1주
        ],
        "ka20068": lambda p: [ # 대차거래추이요청(종목별) (p275)
            ("slb", {"strt_dt": p.get('month_ago_str', p_common['month_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "all_tp": "0", "stk_cd": p['stk_cd']}), # 1달
            ("slb", {"strt_dt": p.get('year_ago_str', p_common['year_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "all_tp": "0", "stk_cd": p['stk_cd']}), # 1년
            ("slb", {"strt_dt": p.get('week_ago_str', p_common['week_ago_str']), "end_dt": p.get('today_str', p_common['today_str']), "all_tp": "0", "stk_cd": p_common['placeholder_stk_kosdaq']}) # 코스닥 1주
        ],
        "ka90012": lambda p: [ # 대차거래내역요청 (p371)
            # ▼▼▼ [다각화 시도] 당일(실패) -> 전일(성공)로 변경 ▼▼▼
            ("slb", {"dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "mrkt_tp": "001"}), # 코스피 *전일*
            ("slb", {"dt": p.get('one_day_ago_str', p_common['one_day_ago_str']), "mrkt_tp": "101"}) # 코스닥 전일 (성공)
        ],

        # === Condition Search (국내주식 > 조건검색) ===
        # !! Requires 'websocket' path mapping and WebSocket connection !! (Skipped by default)
        "ka10171": lambda p: [], # 조건검색 목록조회 (p242) - WebSocket Only
        "ka10172": lambda p: [], # 조건검색 요청 일반 (p244) - WebSocket Only
        "ka10173": lambda p: [], # 조건검색 요청 실시간 (p247) - WebSocket Only
        "ka10174": lambda p: [], # 조건검색 실시간 해제 (p250) - WebSocket Only

        # === Realtime Data Registration/Removal (Placeholders, not for polling) ===
        # These are WebSocket subscription IDs and are skipped.
        "00": lambda p: [], # 주문체결 (p466)
        "04": lambda p: [], # 잔고 (p470)
        "0A": lambda p: [], # 주식기세 (p473)
        "0B": lambda p: [], # 주식체결 (p476)
        "0C": lambda p: [], # 주식우선호가 (p480)
        "0D": lambda p: [], # 주식호가잔량 (p482)
        "0E": lambda p: [], # 주식시간외호가 (p491)
        "0F": lambda p: [], # 주식당일거래원 (p493)
        "0G": lambda p: [], # ETF NAV (p497)
        "0H": lambda p: [], # 주식예상체결 (p500)
        "OI": lambda p: [], # 국제금환산가격 ('ΟΙ' in PDF) (p502)
        "OJ": lambda p: [], # 업종지수 (p504)
        "OU": lambda p: [], # 업종등락 (p507)
        "0g": lambda p: [], # 주식종목정보 (p510)
        "Om": lambda p: [], # ELW 이론가 (p513)
        "Os": lambda p: [], # 장시작시간 (p516)
        "Ou": lambda p: [], # ELW 지표 (p518)
        "Ow": lambda p: [], # 종목프로그램매매 (p520)
        "1h": lambda p: [], # VI발동/해제 (p523)

        # === Order Placement (These are skipped by default in run_all_tests) ===
        # !! Requires 'ordr' path mapping in kiwoom.py !!
        "kt10000": lambda p: [("ordr", {"dmst_stex_tp": p.get("dmst_stex_tp", "KRX"), "stk_cd": p['stk_cd'], "ord_qty": p['ord_qty'], "ord_uv": p.get('ord_uv', ""), "trde_tp": p.get('trde_tp', "00"), "cond_uv": p.get('cond_uv', "")})], # 주식 매수주문 (p422)
        "kt10001": lambda p: [("ordr", {"dmst_stex_tp": p.get("dmst_stex_tp", "KRX"), "stk_cd": p['stk_cd'], "ord_qty": p['ord_qty'], "ord_uv": p.get('ord_uv', ""), "trde_tp": p.get('trde_tp', "00"), "cond_uv": p.get('cond_uv', "")})], # 주식 매도주문 (p424)
        "kt10002": lambda p: [("ordr", {"dmst_stex_tp": p.get("dmst_stex_tp", "KRX"), "orig_ord_no": p.get('orig_ord_no', p_common['dummy_order_id']), "stk_cd": p['stk_cd'], "mdfy_qty": p.get('mdfy_qty', p['ord_qty']), "mdfy_uv": p.get('mdfy_uv', p.get('ord_uv', "")), "mdfy_cond_uv": p.get('mdfy_cond_uv', "")})], # 주식 정정주문 (p426)
        "kt10003": lambda p: [("ordr", {"dmst_stex_tp": p.get("dmst_stex_tp", "KRX"), "orig_ord_no": p.get('orig_ord_no', p_common['dummy_order_id']), "stk_cd": p['stk_cd'], "cncl_qty": p.get("cncl_qty", "0")})], # 주식 취소주문 (p428)
        # !! Requires 'crdordr' path mapping in kiwoom.py !!
        "kt10006": lambda p: [("crdordr", {"dmst_stex_tp": p.get("dmst_stex_tp", "KRX"), "stk_cd": p['stk_cd'], "ord_qty": p['ord_qty'], "ord_uv": p.get('ord_uv', ""), "trde_tp": p.get('trde_tp', "00"), "cond_uv": p.get('cond_uv', "")})], # 신용 매수주문 (p430)
        "kt10007": lambda p: [("crdordr", {"dmst_stex_tp": p.get("dmst_stex_tp", "KRX"), "stk_cd": p['stk_cd'], "ord_qty": p['ord_qty'], "ord_uv": p.get('ord_uv', ""), "trde_tp": p.get('trde_tp', "00"), "crd_deal_tp": p.get("crd_deal_tp", "99"), "crd_loan_dt": p.get("crd_loan_dt", ""), "cond_uv": p.get('cond_uv', "")})], # 신용 매도주문 (p432)
        "kt10008": lambda p: [("crdordr", {"dmst_stex_tp": p.get("dmst_stex_tp", "KRX"), "orig_ord_no": p.get('orig_ord_no', p_common['dummy_order_id']), "stk_cd": p['stk_cd'], "mdfy_qty": p.get('mdfy_qty', p['ord_qty']), "mdfy_uv": p.get('mdfy_uv', p.get('ord_uv', "")), "mdfy_cond_uv": p.get('mdfy_cond_uv', "")})], # 신용 정정주문 (p434)
        "kt10009": lambda p: [("crdordr", {"dmst_stex_tp": p.get("dmst_stex_tp", "KRX"), "orig_ord_no": p.get('orig_ord_no', p_common['dummy_order_id']), "stk_cd": p['stk_cd'], "cncl_qty": p.get("cncl_qty", "0")})], # 신용 취소주문 (p436)
        # !! Requires 'ordr' path mapping in kiwoom.py !!
        "kt50000": lambda p: [("ordr", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "ord_qty": p['ord_qty'], "ord_uv": p.get('ord_uv', ""), "trde_tp": "00"})], # 금현물 매수주문 (p441)
        "kt50001": lambda p: [("ordr", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "ord_qty": p['ord_qty'], "ord_uv": p.get('ord_uv', ""), "trde_tp": "00"})], # 금현물 매도주문 (p443)
        "kt50002": lambda p: [("ordr", {"stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "orig_ord_no": p.get('orig_ord_no', p_common['dummy_order_id']), "mdfy_qty": p.get('mdfy_qty', p['ord_qty']), "mdfy_uv": p.get('mdfy_uv', p.get('ord_uv', ""))})], # 금현물 정정주문 (p445)
        "kt50003": lambda p: [("ordr", {"orig_ord_no": p.get('orig_ord_no', p_common['dummy_order_id']), "stk_cd": p.get('gold_stk_cd', p_common['placeholder_gold']), "cncl_qty": p.get("cncl_qty", "0")})], # 금현물 취소주문 (p447)
    }

    # Fallback for missing definitions - return None to indicate failure
    return definitions.get(api_id, lambda p: None)

# Example usage (for testing this file directly):
# if __name__ == "__main__":
#     params = {
#         "stk_cd": "005930", "ord_qty": "1", "ord_uv": "70000",
#         "etf_cd": "069500", "elw_cd": "57JBHH", "gold_stk_cd": "M04020000",
#         "cond_seq": "0", "orig_ord_no": "0000000", "inds_cd": "001", "thema_cd": "100",
#     }
#
#     # Add common date parameters dynamically
#     today = datetime.date.today()
#     params["today_str"] = today.strftime("%Y%m%d")
#     params["one_day_ago_str"] = (today - datetime.timedelta(days=1)).strftime("%Y%m%d")
#     params["three_days_ago_str"] = (today - datetime.timedelta(days=3)).strftime("%Y%m%d")
#     params["week_ago_str"] = (today - datetime.timedelta(days=7)).strftime("%Y%m%d")
#     params["two_weeks_ago_str"] = (today - datetime.timedelta(days=14)).strftime("%Y%m%d")
#     params["month_ago_str"] = (today - datetime.timedelta(days=30)).strftime("%Y%m%d")
#     params["two_months_ago_str"] = (today - datetime.timedelta(days=60)).strftime("%Y%m%d")
#     params["six_months_ago_str"] = (today - datetime.timedelta(days=180)).strftime("%Y%m%d")
#     params["year_ago_str"] = (today - datetime.timedelta(days=365)).strftime("%Y%m%d")
#
#     total_variants = 0
#     count_apis_with_variants = 0
#     all_defined_ids = {} # Use dict to store functions
#     # Dynamically get definitions to avoid circular dependency if run standalone
#     temp_defs = get_api_definition('').__globals__['definitions']
#     for api_id_key in temp_defs:
#           all_defined_ids[api_id_key] = get_api_definition(api_id_key)
#
#     print(f"--- Generating Variants for {len(all_defined_ids)} API Definitions ---")
#     for api_id, api_func in all_defined_ids.items():
#         if api_func:
#             try:
#                 # Ensure essential params exist for variant generation
#                 required_for_most = ["stk_cd", "ord_qty", "ord_uv", "etf_cd", "elw_cd", "gold_stk_cd", "cond_seq", "orig_ord_no", "inds_cd", "thema_cd"]
#                 test_params = params.copy()
#                 for req_key in required_for_most:
#                       if req_key not in test_params: test_params[req_key] = p_common.get(req_key,"") # Use defaults if available
#
#                 variants = api_func(test_params)
#
#                 if variants is None:
#                      # print(f"[{api_id}] Definition returned None.") # Skip logging None returns
#                      pass
#                 elif isinstance(variants, list):
#                     num_variants = len(variants)
#                     if num_variants > 0:
#                         total_variants += num_variants
#                         count_apis_with_variants += 1
#                         print(f"[{api_id}] Generated {num_variants} variants.")
#                     # else: # Empty list [] is valid for placeholders/skipped APIs
#                         # print(f"[{api_id}] Generated 0 variants (Placeholder/Skipped).")
#                 else:
#                     print(f"[{api_id}] Definition did not return a list or None.")
#
#             except KeyError as e:
#                 print(f"[{api_id}] Missing parameter for variant generation: {e}")
#             except Exception as e:
#                 print(f"[{api_id}] Error generating variants: {e.__class__.__name__}: {e}")
#         # else: # Fallback already handled
#              # print(f"[{api_id}] Definition function could not be retrieved.")
#
#     print(f"\n--- Summary ---")
#     print(f"Total API IDs defined: {len(all_defined_ids)}")
#     print(f"API IDs with generated variants: {count_apis_with_variants}")
#     print(f"Total test variants generated: {total_variants}")