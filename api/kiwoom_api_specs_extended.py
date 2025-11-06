api/kiwoom_api_specs_extended.py
키움증권 REST API 확장 사양 (시세, 순위, 차트, 종목정보 등)

공식 문서 기반: https://github.com/kiwoom-retail/Kiwoom-Securities


MARKET_DATA_APIS = {
    "ka10004": {
        "name": "주식호가요청",
        "endpoint": "/api/dostk/mrkcond",
        "method": "POST",
        "description": "주식 호가 조회 (10호가)",
        "request": {
            "stk_cd": {"type": "str", "required": True, "max_length": 20}
        },
        "response": ["sel_1bid~sel_10bid", "buy_1bid~buy_10bid", "tot_sel_req", "tot_buy_req"]
    },

    "ka10005": {
        "name": "주식일주월시분요청",
        "endpoint": "/api/dostk/mrkcond",
        "method": "POST",
        "description": "일봉/주봉/월봉/분봉 데이터",
        "request": {
            "stk_cd": {"type": "str", "required": True}
        },
        "response": ["date", "open_pric", "high_pric", "low_pric", "close_pric", "trde_qty", "for_poss", "orgn_netprps"]
    },

    "ka10006": {
        "name": "주식시분요청",
        "endpoint": "/api/dostk/mrkcond",
        "method": "POST",
        "description": "분봉 데이터"
    },

    "ka10007": {
        "name": "시세표성정보요청",
        "endpoint": "/api/dostk/mrkcond",
        "method": "POST",
        "description": "시장 상태 정보"
    },

    "ka10086": {
        "name": "일별주가요청",
        "endpoint": "/api/dostk/mrkcond",
        "method": "POST",
        "description": "일별 주가 데이터",
        "request": {
            "stk_cd": {"type": "str", "required": True},
            "qry_dt": {"type": "str", "format": "YYYYMMDD"},
            "indc_tp": {"type": "str", "description": "0:수량, 1:금액"}
        }
    },

    "ka10087": {
        "name": "시간외단일가요청",
        "endpoint": "/api/dostk/mrkcond",
        "method": "POST",
        "description": "시간외 단일가 호가"
    },

    "ka10063": {
        "name": "장중투자자별매매요청",
        "endpoint": "/api/dostk/mrkcond",
        "method": "POST",
        "description": "장중 투자자별 매매 동향"
    },

    "ka10066": {
        "name": "장마감후투자자별매매요청",
        "endpoint": "/api/dostk/mrkcond",
        "method": "POST",
        "description": "장 마감 후 투자자별 매매"
    },

    "ka90005": {
        "name": "프로그램매매추이요청_시간대별",
        "endpoint": "/api/dostk/mrkcond",
        "method": "POST",
        "description": "프로그램 매매 추이 (시간대별)"
    },

    "ka90006": {
        "name": "프로그램매매차익잔고추이요청",
        "endpoint": "/api/dostk/mrkcond",
        "method": "POST",
        "description": "프로그램 매매 차익 잔고"
    },

    "ka90007": {
        "name": "프로그램매매누적추이요청",
        "endpoint": "/api/dostk/mrkcond",
        "method": "POST",
        "description": "프로그램 매매 누적 추이"
    },

    "ka90008": {
        "name": "종목시간별프로그램매매추이요청",
        "endpoint": "/api/dostk/mrkcond",
        "method": "POST",
        "description": "종목별 시간별 프로그램 매매"
    },

    "ka90010": {
        "name": "프로그램매매추이요청_일자별",
        "endpoint": "/api/dostk/mrkcond",
        "method": "POST",
        "description": "프로그램 매매 추이 (일자별)"
    },

    "ka90013": {
        "name": "종목일별프로그램매매추이요청",
        "endpoint": "/api/dostk/mrkcond",
        "method": "POST",
        "description": "종목별 일별 프로그램 매매"
    },
}


RANKING_APIS = {
    "ka10020": {
        "name": "호가잔량상위요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "호가 잔량 상위 종목"
    },

    "ka10023": {
        "name": "거래량급증요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "거래량 급증 종목"
    },

    "ka10030": {
        "name": "당일거래량상위요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "당일 거래량 상위 (가장 많이 사용)"
    },

    "ka10031": {
        "name": "전일거래량상위요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "전일 거래량 상위"
    },

    "ka10032": {
        "name": "거래대금상위요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "거래대금 상위 종목"
    },

    "ka10027": {
        "name": "전일대비등락률상위요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "전일 대비 등락률 상위"
    },

    "ka10029": {
        "name": "예상체결등락률상위요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "예상 체결 등락률 상위"
    },

    "ka10034": {
        "name": "외인기간별매매상위요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "외국인 기간별 매매 상위"
    },

    "ka10035": {
        "name": "외인연속순매매상위요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "외국인 연속 순매매 상위"
    },

    "ka10036": {
        "name": "외인한도소진율증가상위",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "외국인 한도 소진율 증가 상위"
    },

    "ka90009": {
        "name": "외국인기관매매상위요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "외국인+기관 매매 상위"
    },

    "ka10021": {
        "name": "호가잔량급증요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "호가 잔량 급증"
    },

    "ka10022": {
        "name": "잔량율급증요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "잔량율 급증"
    },

    "ka10033": {
        "name": "신용비율상위요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "신용 비율 상위"
    },

    "ka10037": {
        "name": "외국계창구매매상위요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "외국계 창구 매매 상위"
    },

    "ka10038": {
        "name": "종목별증권사순위요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "종목별 증권사 순위"
    },

    "ka10039": {
        "name": "증권사별매매상위요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "증권사별 매매 상위"
    },

    "ka10040": {
        "name": "당일주요거래원요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "당일 주요 거래원"
    },

    "ka10042": {
        "name": "순매수거래원순위요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "순매수 거래원 순위"
    },

    "ka10053": {
        "name": "당일상위이탈원요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "당일 상위 이탈원"
    },

    "ka10062": {
        "name": "동일순매매순위요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "동일 순매매 순위"
    },

    "ka10065": {
        "name": "장중투자자별매매상위요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "장중 투자자별 매매 상위"
    },

    "ka10098": {
        "name": "시간외단일가등락율순위요청",
        "endpoint": "/api/dostk/rkinfo",
        "method": "POST",
        "description": "시간외 단일가 등락율 순위"
    },
}


STOCK_INFO_APIS = {
    "ka10001": {
        "name": "주식기본정보요청",
        "endpoint": "/api/dostk/stkinfo",
        "method": "POST",
        "description": "주식 기본 정보 (가장 많이 사용)"
    },

    "ka10002": {
        "name": "주식거래원요청",
        "endpoint": "/api/dostk/stkinfo",
        "method": "POST",
        "description": "주식 거래원 정보"
    },

    "ka10003": {
        "name": "체결정보요청",
        "endpoint": "/api/dostk/stkinfo",
        "method": "POST",
        "description": "체결 정보"
    },

    "ka10013": {
        "name": "신용매매동향요청",
        "endpoint": "/api/dostk/stkinfo",
        "method": "POST",
        "description": "신용 매매 동향"
    },

    "ka10015": {
        "name": "일별거래상세요청",
        "endpoint": "/api/dostk/stkinfo",
        "method": "POST",
        "description": "일별 거래 상세"
    },

    "ka10016": {
        "name": "신고저가요청",
        "endpoint": "/api/dostk/stkinfo",
        "method": "POST",
        "description": "신고저가 정보"
    },

    "ka10017": {
        "name": "상하한가요청",
        "endpoint": "/api/dostk/stkinfo",
        "method": "POST",
        "description": "상하한가 정보"
    },

    "ka10018": {
        "name": "고저가근접요청",
        "endpoint": "/api/dostk/stkinfo",
        "method": "POST",
        "description": "고저가 근접 종목"
    },

    "ka10019": {
        "name": "가격급등락요청",
        "endpoint": "/api/dostk/stkinfo",
        "method": "POST",
        "description": "가격 급등락 종목"
    },

    "ka10024": {
        "name": "거래량갱신요청",
        "endpoint": "/api/dostk/stkinfo",
        "method": "POST",
        "description": "거래량 갱신 종목"
    },

    "ka10025": {
        "name": "매물대집중요청",
        "endpoint": "/api/dostk/stkinfo",
        "method": "POST",
        "description": "매물대 집중 분석"
    },

    "ka10026": {
        "name": "고저PER요청",
        "endpoint": "/api/dostk/stkinfo",
        "method": "POST",
        "description": "고저 PER 정보"
    },

    "ka10028": {
        "name": "시가대비등락률요청",
        "endpoint": "/api/dostk/stkinfo",
        "method": "POST",
        "description": "시가 대비 등락률"
    },

    "ka10043": {
        "name": "거래원매물대분석요청",
        "endpoint": "/api/dostk/stkinfo",
        "method": "POST",
        "description": "거래원 매물대 분석"
    },

    "ka10052": {
        "name": "거래원순간거래량요청",
        "endpoint": "/api/dostk/stkinfo",
        "method": "POST",
        "description": "거래원 순간 거래량"
    },

    "ka10054": {
        "name": "변동성완화장치발동종목요청",
        "endpoint": "/api/dostk/stkinfo",
        "method": "POST",
        "description": "VI(변동성완화장치) 발동 종목"
    },
}


SECTOR_APIS = {
    "ka10010": {
        "name": "업종프로그램요청",
        "endpoint": "/api/dostk/sect",
        "method": "POST",
        "description": "업종 프로그램 매매 정보"
    },

    "ka10051": {
        "name": "업종별투자자순매수요청",
        "endpoint": "/api/dostk/sect",
        "method": "POST",
        "description": "업종별 투자자 순매수"
    },

    "ka20001": {
        "name": "업종현재가요청",
        "endpoint": "/api/dostk/sect",
        "method": "POST",
        "description": "업종 현재가"
    },

    "ka20002": {
        "name": "업종별주가요청",
        "endpoint": "/api/dostk/sect",
        "method": "POST",
        "description": "업종별 주가"
    },

    "ka20003": {
        "name": "전업종지수요청",
        "endpoint": "/api/dostk/sect",
        "method": "POST",
        "description": "전 업종 지수"
    },

    "ka20009": {
        "name": "업종현재가일별요청",
        "endpoint": "/api/dostk/sect",
        "method": "POST",
        "description": "업종 현재가 일별 데이터"
    },
}


CHART_APIS = {
    "ka10060": {
        "name": "투자자기관차트요청",
        "endpoint": "/api/dostk/chart",
        "method": "POST",
        "description": "투자자/기관 차트"
    },

    "ka10064": {
        "name": "장중투자자매매차트요청",
        "endpoint": "/api/dostk/chart",
        "method": "POST",
        "description": "장중 투자자 매매 차트"
    },

    "ka10079": {
        "name": "주식틱차트요청",
        "endpoint": "/api/dostk/chart",
        "method": "POST",
        "description": "주식 틱 차트"
    },

    "ka10080": {
        "name": "주식분차트요청",
        "endpoint": "/api/dostk/chart",
        "method": "POST",
        "description": "주식 분봉 차트 (1-60분)"
    },

    "ka10081": {
        "name": "주식일차트요청",
        "endpoint": "/api/dostk/chart",
        "method": "POST",
        "description": "주식 일봉 차트"
    },

    "ka10082": {
        "name": "주식주차트요청",
        "endpoint": "/api/dostk/chart",
        "method": "POST",
        "description": "주식 주봉 차트"
    },

    "ka10083": {
        "name": "주식월차트요청",
        "endpoint": "/api/dostk/chart",
        "method": "POST",
        "description": "주식 월봉 차트"
    },

    "ka10094": {
        "name": "주식년차트요청",
        "endpoint": "/api/dostk/chart",
        "method": "POST",
        "description": "주식 연봉 차트"
    },

    "ka20004": {
        "name": "업종틱차트요청",
        "endpoint": "/api/dostk/chart",
        "method": "POST",
        "description": "업종 틱 차트"
    },

    "ka20005": {
        "name": "업종분차트요청",
        "endpoint": "/api/dostk/chart",
        "method": "POST",
        "description": "업종 분봉 차트"
    },

    "ka20006": {
        "name": "업종일차트요청",
        "endpoint": "/api/dostk/chart",
        "method": "POST",
        "description": "업종 일봉 차트"
    },

    "ka20007": {
        "name": "업종주차트요청",
        "endpoint": "/api/dostk/chart",
        "method": "POST",
        "description": "업종 주봉 차트"
    },

    "ka20008": {
        "name": "업종월차트요청",
        "endpoint": "/api/dostk/chart",
        "method": "POST",
        "description": "업종 월봉 차트"
    },

    "ka20019": {
        "name": "업종년차트요청",
        "endpoint": "/api/dostk/chart",
        "method": "POST",
        "description": "업종 연봉 차트"
    },
}


CONDITION_SEARCH_APIS = {
    "ka10171": {
        "name": "조건검색목록조회",
        "endpoint": "wss://api.kiwoom.com:10000/api/dostk/websocket",
        "method": "WebSocket",
        "description": "저장된 조건검색 목록 조회",
        "request": {
            "trnm": "CNSRLST"
        }
    },

    "ka10172": {
        "name": "조건검색일반검색",
        "endpoint": "wss://api.kiwoom.com:10000/api/dostk/websocket",
        "method": "WebSocket",
        "description": "일반 조건검색 (1회 조회)",
        "request": {
            "trnm": "CNSRREQ",
            "seq": "조건검색 ID",
            "search_type": "0"
        }
    },

    "ka10173": {
        "name": "조건검색실시간검색",
        "endpoint": "wss://api.kiwoom.com:10000/api/dostk/websocket",
        "method": "WebSocket",
        "description": "실시간 조건검색 (변동사항 자동 수신)",
        "request": {
            "trnm": "CNSRREQ",
            "search_type": "1"
        }
    },

    "ka10174": {
        "name": "조건검색실시간해제",
        "endpoint": "wss://api.kiwoom.com:10000/api/dostk/websocket",
        "method": "WebSocket",
        "description": "실시간 조건검색 종료",
        "request": {
            "trnm": "CNSRCLR"
        }
    },
}

ALL_EXTENDED_APIS = {
    **MARKET_DATA_APIS,
    **RANKING_APIS,
    **STOCK_INFO_APIS,
    **SECTOR_APIS,
    **CHART_APIS,
    **CONDITION_SEARCH_APIS,
}

__all__ = [
    'MARKET_DATA_APIS',
    'RANKING_APIS',
    'STOCK_INFO_APIS',
    'SECTOR_APIS',
    'CHART_APIS',
    'CONDITION_SEARCH_APIS',
    'ALL_EXTENDED_APIS',
]
