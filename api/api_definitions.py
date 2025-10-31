"""
api/api_definitions.py
키움증권 REST API 중앙 정의 파일

참고:
- https://github.com/kiwoom-retail/Kiwoom-Securities
- https://openapi.kiwoom.com
- 모든 API ID는 kt로 시작하는 공식 ID 사용
"""

# ==================== 계좌 관련 API (kt00001 ~ kt00018) ====================

ACCOUNT_APIS = {
    # 예수금 및 잔고 조회
    "예수금상세현황": {
        "api_id": "kt00001",
        "name": "예수금상세현황요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "예수금 상세 현황 조회",
        "request": {
            "qry_tp": "2"  # 1:합산, 2:일반조회
        },
        "response": {
            "ord_alow_amt": "주문가능금액",
            "pymn_alow_amt": "출금가능금액",
            "tot_aval_amt": "총예수금",
            "d2_aval_amt": "D+2예수금"
        }
    },

    "계좌평가잔고": {
        "api_id": "kt00018",
        "name": "계좌평가잔고내역요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "계좌 평가 잔고 내역 조회",
        "request": {
            "qry_tp": "1",  # 1:합산, 2:일반조회
            "dmst_stex_tp": "KRX"  # KRX:한국거래소
        },
        "response": {
            "acnt_evlt_remn_indv_tot": "보유종목 리스트",
            "tot_evlt_amt": "총평가금액",
            "tot_evlt_pl": "총평가손익",
            "tot_prft_rt": "총수익률",
            "prsm_dpst_aset_amt": "추정예탁자산"
        }
    },

    "일별추정예탁자산": {
        "api_id": "kt00002",
        "name": "일별추정예탁자산현황요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "일별 추정 예탁 자산 현황"
    },

    "추정자산조회": {
        "api_id": "kt00003",
        "name": "추정자산조회요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "추정 자산 조회"
    },

    "계좌평가현황": {
        "api_id": "kt00004",
        "name": "계좌평가현황요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "계좌 평가 현황"
    },

    "체결잔고": {
        "api_id": "kt00005",
        "name": "체결잔고요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "체결 잔고 조회"
    },

    "주문체결내역": {
        "api_id": "kt00007",
        "name": "계좌별주문체결내역상세요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "계좌별 주문 체결 내역 상세"
    },

    "익일결제예정": {
        "api_id": "kt00008",
        "name": "계좌별익일결제예정내역요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "익일 결제 예정 내역"
    },
}

# ==================== 시세 조회 API ====================

MARKET_APIS = {
    "현재가조회": {
        "api_id": "kt10001",  # 추정 (공식 문서 확인 필요)
        "name": "주식현재가조회",
        "endpoint": "/api/dostk/quote",
        "method": "POST",
        "description": "주식 현재가 조회",
        "request": {
            "stk_cd": "종목코드"
        },
        "response": {
            "cur_prc": "현재가",
            "chng_rt": "등락률",
            "acc_vol": "누적거래량"
        }
    },

    "호가조회": {
        "api_id": "kt10002",  # 추정
        "name": "주식호가조회",
        "endpoint": "/api/dostk/quote",
        "method": "POST",
        "description": "주식 호가 조회"
    },

    "체결가조회": {
        "api_id": "kt10003",  # 추정
        "name": "주식체결가조회",
        "endpoint": "/api/dostk/quote",
        "method": "POST",
        "description": "주식 체결가 조회"
    },
}

# ==================== 주문 관련 API ====================

ORDER_APIS = {
    "현금매수": {
        "api_id": "kt20001",  # 추정
        "name": "현금매수주문",
        "endpoint": "/api/dostk/order",
        "method": "POST",
        "description": "현금 매수 주문",
        "request": {
            "ord_dv": "01",  # 01:시장가, 02:지정가
            "stk_cd": "종목코드",
            "ord_qty": "주문수량",
            "ord_prc": "주문가격",
            "ord_tp": "2"  # 1:매도, 2:매수
        },
        "response": {
            "ord_no": "주문번호",
            "ord_tm": "주문시간"
        }
    },

    "현금매도": {
        "api_id": "kt20002",  # 추정
        "name": "현금매도주문",
        "endpoint": "/api/dostk/order",
        "method": "POST",
        "description": "현금 매도 주문",
        "request": {
            "ord_dv": "01",  # 01:시장가, 02:지정가
            "stk_cd": "종목코드",
            "ord_qty": "주문수량",
            "ord_prc": "주문가격",
            "ord_tp": "1"  # 1:매도, 2:매수
        }
    },

    "주문취소": {
        "api_id": "kt20003",  # 추정
        "name": "주문취소",
        "endpoint": "/api/dostk/order",
        "method": "POST",
        "description": "주문 취소"
    },

    "주문정정": {
        "api_id": "kt20004",  # 추정
        "name": "주문정정",
        "endpoint": "/api/dostk/order",
        "method": "POST",
        "description": "주문 정정"
    },
}

# ==================== 조건검색 관련 API ====================

CONDITION_APIS = {
    "조건검색목록": {
        "api_id": "kt30001",  # 추정
        "name": "조건검색목록조회",
        "endpoint": "/api/dostk/condition",
        "method": "POST",
        "description": "저장된 조건검색 목록 조회"
    },

    "조건검색실행": {
        "api_id": "kt30002",  # 추정
        "name": "조건검색실행",
        "endpoint": "/api/dostk/condition",
        "method": "POST",
        "description": "조건검색 실행"
    },
}

# ==================== API 통합 딕셔너리 ====================

ALL_APIS = {
    **ACCOUNT_APIS,
    **MARKET_APIS,
    **ORDER_APIS,
    **CONDITION_APIS,
}


def get_api_spec(api_name: str):
    """
    API 명세 조회

    Args:
        api_name: API 이름 (예: "예수금상세현황", "계좌평가잔고")

    Returns:
        API 명세 딕셔너리
    """
    return ALL_APIS.get(api_name)


def get_api_by_id(api_id: str):
    """
    API ID로 명세 조회

    Args:
        api_id: API ID (예: "kt00001", "kt00018")

    Returns:
        API 명세 딕셔너리
    """
    for name, spec in ALL_APIS.items():
        if spec.get("api_id") == api_id:
            return spec
    return None


def list_account_apis():
    """계좌 관련 API 목록"""
    return ACCOUNT_APIS


def list_market_apis():
    """시세 관련 API 목록"""
    return MARKET_APIS


def list_order_apis():
    """주문 관련 API 목록"""
    return ORDER_APIS


def list_all_apis():
    """전체 API 목록"""
    return ALL_APIS


__all__ = [
    'ACCOUNT_APIS',
    'MARKET_APIS',
    'ORDER_APIS',
    'CONDITION_APIS',
    'ALL_APIS',
    'get_api_spec',
    'get_api_by_id',
    'list_account_apis',
    'list_market_apis',
    'list_order_apis',
    'list_all_apis',
]
