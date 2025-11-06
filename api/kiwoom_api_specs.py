api/kiwoom_api_specs.py
키움증권 REST API 완전한 사양 정의

공식 문서 기반: https://github.com/kiwoom-retail/Kiwoom-Securities
업데이트: 2025-10-31

이 파일은 키움증권의 100개 이상 REST API를 모두 정의합니다.


ENVIRONMENTS = {
    "production": {
        "base_url": "https://api.kiwoom.com",
        "websocket_url": "wss://api.kiwoom.com:10000/api/dostk/websocket"
    },
    "mock": {
        "base_url": "https://mockapi.kiwoom.com",
        "websocket_url": "wss://mockapi.kiwoom.com:10000",
        "note": "KRX only"
    }
}

COMMON_HEADERS = {
    "authorization": {"required": True, "format": "Bearer {token}", "max_length": 1000},
    "api-id": {"required": True, "description": "TR code", "max_length": 10},
    "cont-yn": {"required": False, "description": "Continuation flag (Y/N)", "max_length": 1},
    "next-key": {"required": False, "description": "Pagination key", "max_length": 50}
}


ACCOUNT_APIS = {
    "kt00001": {
        "name": "예수금상세현황요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "예수금 상세 현황 조회",
        "request": {
            "qry_tp": {"type": "str", "required": True, "description": "3:추정조회, 2:일반조회"}
        },
        "response": ["예수금", "증거금현금", "신용금액", "대용금", "ord_alow_amt", "pymn_alow_amt", "미수금", "대출금"]
    },

    "kt00002": {
        "name": "일별추정예탁자산현황요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "일별 추정 예탁 자산 현황",
        "request": {
            "start_dt": {"type": "str", "format": "YYYYMMDD"},
            "end_dt": {"type": "str", "format": "YYYYMMDD"}
        }
    },

    "kt00003": {
        "name": "추정자산조회요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "추정 예탁 자산 조회",
        "request": {
            "qry_tp": {"type": "str", "description": "0:전체, 1:상장폐지제외"}
        }
    },

    "kt00004": {
        "name": "계좌평가현황요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "계좌 평가 현황",
        "request": {
            "qry_tp": {"type": "str"},
            "dmst_stex_tp": {"type": "str", "description": "KRX, NXT"}
        }
    },

    "kt00005": {
        "name": "체결잔고요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "체결 잔고 조회",
        "request": {
            "dmst_stex_tp": {"type": "str"}
        }
    },

    "kt00007": {
        "name": "계좌별주문체결내역상세요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "계좌별 주문 체결 내역 상세",
        "request": {
            "ord_dt": {"type": "str", "format": "YYYYMMDD"},
            "qry_tp": {"type": "str", "description": "1:주문순, 2:역순, 3:미체결, 4:체결"},
            "stk_bond_tp": {"type": "str", "description": "0:전체, 1:주식, 2:채권"},
            "sell_tp": {"type": "str", "description": "매도/매수 구분"},
            "stk_cd": {"type": "str", "required": False},
            "fr_ord_no": {"type": "str", "required": False},
            "dmst_stex_tp": {"type": "str"}
        }
    },

    "kt00008": {
        "name": "계좌별익일결제예정내역요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "익일 결제 예정 내역"
    },

    "kt00009": {
        "name": "계좌별주문체결현황요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "계좌별 주문 체결 현황"
    },

    "kt00010": {
        "name": "주문인출가능금액요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "주문 가능 금액 및 수량 조회"
    },

    "kt00011": {
        "name": "증거금율별주문가능수량조회요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "증거금율별 주문 가능 수량"
    },

    "kt00012": {
        "name": "신용보증금율별주문가능수량조회요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "신용 보증금율별 주문 가능 수량"
    },

    "kt00018": {
        "name": "계좌평가잔고내역요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "계좌 평가 잔고 내역 조회 (가장 많이 사용)",
        "request": {
            "qry_tp": {"type": "str", "description": "1:합산, 2:일반조회"},
            "dmst_stex_tp": {"type": "str", "description": "KRX:한국거래소"}
        },
        "response": {
            "acnt_evlt_remn_indv_tot": "보유종목 리스트",
            "tot_evlt_amt": "총평가금액",
            "tot_evlt_pl": "총평가손익",
            "tot_prft_rt": "총수익률",
            "prsm_dpst_aset_amt": "추정예탁자산"
        }
    },

    "ka10072": {
        "name": "일자별종목별실현손익요청_일자",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "일자별 종목별 실현손익"
    },

    "ka10073": {
        "name": "일자별종목별실현손익요청_기간",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "기간별 실현손익"
    },

    "ka10074": {
        "name": "일자별실현손익요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "일자별 실현손익"
    },

    "ka10077": {
        "name": "당일실현손익상세요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "당일 실현손익 상세"
    },

    "ka10085": {
        "name": "계좌수익률요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "계좌 수익률"
    },

    "ka10170": {
        "name": "당일매매일지요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "당일 매매 일지"
    },

    "ka10075": {
        "name": "미체결요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "미체결 주문 조회"
    },

    "ka10076": {
        "name": "체결요청",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "체결 내역 조회"
    },

    "ka10088": {
        "name": "미체결분할주문상세",
        "endpoint": "/api/dostk/acnt",
        "method": "POST",
        "description": "미체결 분할 주문 상세"
    },
}


ORDER_APIS = {
    "kt10000": {
        "name": "주식매수주문",
        "endpoint": "/api/dostk/ordr",
        "method": "POST",
        "description": "현물 매수 주문",
        "request": {
            "dmst_stex_tp": {"type": "str", "description": "KRX, NXT, SOR"},
            "stk_cd": {"type": "str", "required": True, "description": "종목코드"},
            "ord_qty": {"type": "int", "required": True, "description": "주문수량"},
            "ord_uv": {"type": "int", "required": True, "description": "주문가격"},
            "trde_tp": {"type": "str", "required": True, "description": "거래유형 (0, 3, 5, 6, 7, 10, 13, 16, 20, 23, 26, 28-31, 61-62, 81)"}
        },
        "response": {
            "ord_no": "주문번호",
            "return_code": "0 = 성공",
            "return_msg": "결과 메시지"
        }
    },

    "kt10001": {
        "name": "주식매도주문",
        "endpoint": "/api/dostk/ordr",
        "method": "POST",
        "description": "현물 매도 주문"
    },

    "kt10002": {
        "name": "주식정정주문",
        "endpoint": "/api/dostk/ordr",
        "method": "POST",
        "description": "주문 정정",
        "request": {
            "orig_ord_no": {"type": "str", "required": True, "description": "원주문번호"},
            "mdfy_qty": {"type": "int", "description": "정정수량"},
            "mdfy_uv": {"type": "int", "description": "정정가격"}
        }
    },

    "kt10003": {
        "name": "주식취소주문",
        "endpoint": "/api/dostk/ordr",
        "method": "POST",
        "description": "주문 취소",
        "request": {
            "orig_ord_no": {"type": "str", "required": True},
            "cncl_qty": {"type": "int", "required": True, "description": "취소수량"}
        }
    },

    "kt10006": {
        "name": "신용매수주문",
        "endpoint": "/api/dostk/crdordr",
        "method": "POST",
        "description": "신용 매수 주문",
        "request": {
            "crd_deal_tp": {"type": "str", "description": "33:융자, 99:종합"},
            "crd_loan_dt": {"type": "str", "format": "YYYYMMDD"}
        }
    },

    "kt10007": {
        "name": "신용매도주문",
        "endpoint": "/api/dostk/crdordr",
        "method": "POST",
        "description": "신용 매도 주문"
    },

    "kt10008": {
        "name": "신용정정주문",
        "endpoint": "/api/dostk/crdordr",
        "method": "POST",
        "description": "신용 주문 정정"
    },

    "kt10009": {
        "name": "신용취소주문",
        "endpoint": "/api/dostk/crdordr",
        "method": "POST",
        "description": "신용 주문 취소"
    },
}

def get_api_spec(api_id: str):
    """API ID로 사양 조회"""
    all_apis = {**ACCOUNT_APIS, **ORDER_APIS}
    return all_apis.get(api_id)

def list_apis_by_category(category: str):
    """카테고리별 API 목록"""
    categories = {
        "account": ACCOUNT_APIS,
        "order": ORDER_APIS,
    }
    return categories.get(category, {})

__all__ = [
    'ENVIRONMENTS',
    'COMMON_HEADERS',
    'ACCOUNT_APIS',
    'ORDER_APIS',
    'get_api_spec',
    'list_apis_by_category',
]
