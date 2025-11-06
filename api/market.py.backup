"""
api/market.py
시세 및 시장 정보 API (market_condition, rank_info, sector, theme 등 통합)
"""
import logging
from typing import Dict, Any, Optional, List
from utils.trading_date import get_last_trading_date

logger = logging.getLogger(__name__)


class MarketAPI:
    """
    시세 및 시장 정보 API

    통합된 기능:
    - 시세 조회
    - 호가 조회
    - 시장 상황
    - 순위 정보
    - 업종 정보
    - 테마 정보

    ⚠️ 중요: API 응답 파싱 패턴
    ----------------------------------
    키움증권 REST API는 응답 구조가 API마다 다릅니다!

    ⚠️ DOSK API ID는 키움증권 내부 API ID입니다
    - DOSK_XXXX는 한국투자증권이 아님!
    - 실제 요청은 키움증권 API 서버로 전송됨 (/api/dostk/...)

    1. 일반적인 패턴: response['output']
       예: DOSK_XXXX 시리즈 (키움증권 내부 API ID)

    2. 랭킹 API 패턴: 특정 키 사용
       - ka10031 (거래량순위): response['pred_trde_qty_upper']
       - ka10027 (등락률순위): response['pred_pre_flu_rt_upper']

    3. 데이터 정규화 필요
       API 응답 키 → 표준 키 변환:
       - stk_cd → code (종목코드, _AL 접미사 제거)
       - stk_nm → name (종목명)
       - cur_prc → price (현재가)
       - trde_qty / now_trde_qty → volume (거래량)
       - flu_rt → change_rate (등락률)

    새 API 추가 시:
    1. successful_apis.json에서 실제 응답 구조 확인
    2. 디버그 출력으로 실제 응답 키 확인
    3. 올바른 키로 데이터 추출
    4. 필요시 데이터 정규화
    """
    
    def __init__(self, client):
        """
        MarketAPI 초기화
        
        Args:
            client: KiwoomRESTClient 인스턴스
        """
        self.client = client
        logger.info("MarketAPI 초기화 완료")
    
    def get_stock_price(self, stock_code: str, use_fallback: bool = True) -> Optional[Dict[str, Any]]:
        """
        종목 체결정보 조회 (키움증권 API ka10003)
        NXT 시간대 및 fallback 지원

        Args:
            stock_code: 종목코드
            use_fallback: 실패 시 대체 소스 사용 여부 (기본값: True)

        Returns:
            체결정보 (현재가 포함)
        """
        from utils.trading_date import is_nxt_hours, is_any_trading_hours

        # NXT 시간대에는 종목코드에 _NX 접미사 추가
        nxt_stock_code = stock_code
        if is_nxt_hours():
            # NXT 종목코드 형식: 039490_NX
            if not stock_code.endswith("_NX"):
                nxt_stock_code = f"{stock_code}_NX"
            logger.info(f"NXT 시간대 - 종목코드 변환: {stock_code} → {nxt_stock_code}")

        body = {
            "stk_cd": nxt_stock_code
        }

        response = self.client.request(
            api_id="ka10003",
            body=body,
            path="stkinfo"
        )

        if response and response.get('return_code') == 0:
            # ka10003 응답: cntr_infr 리스트
            cntr_infr = response.get('cntr_infr', [])

            if cntr_infr and len(cntr_infr) > 0:
                # 최신 체결 정보 (첫 번째 항목)
                latest = cntr_infr[0]

                # 현재가 파싱 (+/- 부호 제거)
                cur_prc_str = latest.get('cur_prc', '0')
                current_price = abs(int(cur_prc_str.replace('+', '').replace('-', '')))

                # 정규화된 응답
                price_info = {
                    'current_price': current_price,
                    'cur_prc': current_price,  # 원본 필드명도 유지
                    'change': latest.get('pred_pre', '0'),
                    'change_rate': latest.get('pre_rt', '0'),
                    'volume': latest.get('cntr_trde_qty', '0'),
                    'acc_volume': latest.get('acc_trde_qty', '0'),
                    'acc_trading_value': latest.get('acc_trde_prica', '0'),
                    'time': latest.get('tm', ''),
                    'stex_tp': latest.get('stex_tp', ''),
                    'source': 'nxt_market' if is_nxt_hours() else 'regular_market',
                }

                logger.info(f"{stock_code} 현재가: {current_price:,}원 (출처: {price_info['source']})")
                return price_info
            else:
                logger.warning(f"현재가 조회 실패: 체결정보 없음")
        else:
            logger.warning(f"현재가 조회 API 실패: {response.get('return_msg') if response else 'No response'}")

        # Fallback 1: 호가 정보에서 현재가 추출 시도 (NXT 코드)
        if use_fallback:
            logger.info(f"{stock_code} 호가 정보로 현재가 조회 시도...")
            orderbook = self.get_orderbook(stock_code)
            if orderbook and orderbook.get('현재가', 0) > 0:
                current_price = int(orderbook.get('현재가', 0))
                logger.info(f"{stock_code} 현재가: {current_price:,}원 (출처: orderbook)")
                return {
                    'current_price': current_price,
                    'cur_prc': current_price,
                    'source': 'orderbook',
                    'time': '',
                }

            # Fallback 2: NXT 시간대에 _NX 호가도 실패하면 기본 코드로 재시도
            if is_nxt_hours() and nxt_stock_code != stock_code:
                logger.info(f"{stock_code} NXT 호가 실패 - 기본 코드로 재시도...")
                # get_orderbook 내부에서 _NX를 추가하므로, 강제로 기본 코드 사용
                body_fallback = {"stk_cd": stock_code}
                response_fallback = self.client.request(
                    api_id="ka10004",
                    body=body_fallback,
                    path="mrkcond"
                )
                if response_fallback and response_fallback.get('return_code') == 0:
                    sel_fpr_bid = response_fallback.get('sel_fpr_bid', '0').replace('+', '').replace('-', '')
                    buy_fpr_bid = response_fallback.get('buy_fpr_bid', '0').replace('+', '').replace('-', '')

                    sell_price = abs(int(sel_fpr_bid)) if sel_fpr_bid and sel_fpr_bid != '0' else 0
                    buy_price = abs(int(buy_fpr_bid)) if buy_fpr_bid and buy_fpr_bid != '0' else 0

                    if sell_price > 0 or buy_price > 0:
                        # 중간가 계산
                        if sell_price > 0 and buy_price > 0:
                            current_price = (sell_price + buy_price) // 2
                        elif sell_price > 0:
                            current_price = sell_price
                        else:
                            current_price = buy_price

                        logger.info(f"{stock_code} 현재가: {current_price:,}원 (출처: orderbook_basic_fallback)")
                        return {
                            'current_price': current_price,
                            'cur_prc': current_price,
                            'source': 'orderbook_basic_fallback',
                            'time': '',
                        }

        logger.error(f"{stock_code} 현재가 조회 완전 실패 (모든 소스)")
        return None
    
    def get_orderbook(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        호가 조회 (키움증권 API ka10004)

        Args:
            stock_code: 종목코드

        Returns:
            호가 정보
            {
                'sell_price': 매도1호가,
                'buy_price': 매수1호가,
                'mid_price': 중간가,
                '매도_총잔량': 총매도잔량,
                '매수_총잔량': 총매수잔량,
                ...
            }
        """
        from utils.trading_date import is_nxt_hours

        # NXT 시간대에는 종목코드에 _NX 접미사 추가
        nxt_stock_code = stock_code
        if is_nxt_hours():
            if not stock_code.endswith("_NX"):
                nxt_stock_code = f"{stock_code}_NX"

        body = {
            "stk_cd": nxt_stock_code
        }

        response = self.client.request(
            api_id="ka10004",
            body=body,
            path="mrkcond"
        )

        if response and response.get('return_code') == 0:
            # ka10004 응답은 output 키 없이 바로 데이터가 옴
            orderbook = response

            # 매도1호가 / 매수1호가 파싱
            sel_fpr_bid = orderbook.get('sel_fpr_bid', '0').replace('+', '').replace('-', '')
            buy_fpr_bid = orderbook.get('buy_fpr_bid', '0').replace('+', '').replace('-', '')

            sell_price = abs(int(sel_fpr_bid)) if sel_fpr_bid and sel_fpr_bid != '0' else 0
            buy_price = abs(int(buy_fpr_bid)) if buy_fpr_bid and buy_fpr_bid != '0' else 0

            # 총잔량 파싱
            tot_sel_req = orderbook.get('tot_sel_req', '0').replace('+', '').replace('-', '')
            tot_buy_req = orderbook.get('tot_buy_req', '0').replace('+', '').replace('-', '')

            total_sell_qty = abs(int(tot_sel_req)) if tot_sel_req and tot_sel_req != '0' else 0
            total_buy_qty = abs(int(tot_buy_req)) if tot_buy_req and tot_buy_req != '0' else 0

            # 정규화된 응답
            orderbook['sell_price'] = sell_price  # 매도1호가
            orderbook['buy_price'] = buy_price    # 매수1호가

            # scanner_pipeline.py 호환 필드명 추가
            orderbook['매도_총잔량'] = total_sell_qty
            orderbook['매수_총잔량'] = total_buy_qty

            # 중간가 계산
            if sell_price > 0 and buy_price > 0:
                orderbook['mid_price'] = (sell_price + buy_price) // 2
            elif sell_price > 0:
                orderbook['mid_price'] = sell_price
            elif buy_price > 0:
                orderbook['mid_price'] = buy_price
            else:
                orderbook['mid_price'] = 0

            logger.info(
                f"{stock_code} 호가 조회 완료: "
                f"매도1={sell_price:,}, 매수1={buy_price:,}, "
                f"총잔량(매도={total_sell_qty:,}, 매수={total_buy_qty:,})"
            )
            return orderbook
        else:
            logger.error(f"호가 조회 실패: {response.get('return_msg') if response else 'No response'}")
            return None
    
    def get_market_index(self, market_code: str = '001') -> Optional[Dict[str, Any]]:
        """
        시장 지수 조회
        
        Args:
            market_code: 시장코드 ('001': 코스피, '101': 코스닥)
        
        Returns:
            지수 정보
        """
        body = {
            "market_code": market_code
        }
        
        response = self.client.request(
            api_id="DOSK_0004",
            body=body,
            path="inquire/index"
        )
        
        if response and response.get('return_code') == 0:
            index_info = response.get('output', {})
            market_name = "코스피" if market_code == '001' else "코스닥"
            logger.info(f"{market_name} 지수: {index_info.get('index', 0):.2f}")
            return index_info
        else:
            logger.error(f"지수 조회 실패: {response.get('return_msg')}")
            return None
    
    def get_volume_rank(
        self,
        market: str = 'ALL',
        limit: int = 20,
        date: str = None
    ) -> List[Dict[str, Any]]:
        """
        전일 거래량 순위 조회 (ka10031)

        Args:
            market: 시장구분 ('0': 전체, '1': KOSPI, '2': KOSDAQ)
            limit: 조회 건수 (최대 200)
            date: 조회일 (현재 미사용, 자동으로 전일 데이터 조회)

        Returns:
            거래량 순위 리스트

        Note:
            이 API는 실시간 전일 데이터만 제공합니다.
            주말/공휴일/장마감 후에는 데이터가 제공되지 않을 수 있습니다.
        """
        try:
            # 시장 코드 변환 (successful_apis.json 검증된 값)
            market_map = {'ALL': '000', 'KOSPI': '001', 'KOSDAQ': '101'}
            mrkt_tp = market_map.get(market.upper(), '001')

            # 순위 범위 설정 (1위부터 limit까지)
            body = {
                "mrkt_tp": mrkt_tp,        # 시장구분 (000:전체, 001:KOSPI, 101:KOSDAQ)
                "qry_tp": "1",              # 조회구분 (1:거래량, 2:거래대금) - 검증됨
                "stex_tp": "3",             # 증권거래소 (3:전체) - 검증됨
                "rank_strt": "1",           # 시작순위
                "rank_end": str(limit)      # 종료순위
            }

            print(f"📍 거래량 순위 조회 시작 (market={market}, limit={limit})")
            logger.info(f"거래량 순위 조회 시작 (market={market}, limit={limit})")

            response = self.client.request(
                api_id="ka10031",
                body=body,
                path="rkinfo"
            )

            print(f"📍 API 응답 received: return_code={response.get('return_code') if response else None}")

            if response and response.get('return_code') == 0:
                # ka10031 API는 'pred_trde_qty_upper' 키에 데이터 반환
                rank_list = response.get('pred_trde_qty_upper', [])
                print(f"📍 rank_list 크기: {len(rank_list) if rank_list else 0}개")

                if not rank_list:
                    msg = "⚠️ API 호출 성공했으나 데이터가 비어있습니다 (장마감 후/주말/공휴일일 수 있음)"
                    print(msg)
                    logger.warning(msg)
                    print(f"📍 전체 응답 키: {list(response.keys())}")
                    return []

                # 데이터 정규화: API 응답 키 -> 표준 키
                normalized_list = []
                debug_printed = False

                for item in rank_list:
                    # 현재가 파싱 (부호 포함 가능)
                    cur_prc_str = item.get('cur_prc', '0')
                    current_price = abs(int(cur_prc_str.replace('+', '').replace('-', '')))

                    # 등락폭 파싱 (부호 포함 가능)
                    pred_pre_str = item.get('pred_pre', '0')
                    change = int(pred_pre_str.replace('+', '').replace('-', ''))

                    # 등락 부호 확인 (2: 상승, 3: 보합, 5: 하락)
                    pred_pre_sig = item.get('pred_pre_sig', '3')
                    is_positive = pred_pre_sig == '2' or pred_pre_str.startswith('+')

                    # 전일 종가 계산
                    if is_positive:
                        prev_price = current_price - change
                    else:
                        prev_price = current_price + change

                    # 등락률 계산: (등락폭 / 전일종가) * 100
                    if prev_price > 0:
                        change_rate = abs(change / prev_price * 100)
                    else:
                        change_rate = 0.0

                    # API 응답에 등락률 필드가 있으면 사용
                    if 'flu_rt' in item:
                        change_rate = abs(float(item.get('flu_rt', '0').replace('+', '').replace('-', '')))

                    normalized_list.append({
                        'code': item.get('stk_cd', '').replace('_AL', ''),  # _AL 접미사 제거
                        'name': item.get('stk_nm', ''),
                        'price': current_price,
                        'current_price': current_price,  # Screener 호환
                        'volume': int(item.get('trde_qty', '0')),
                        'change': change,
                        'change_rate': change_rate,  # Screener 호환
                        'rate': change_rate,  # StockCandidate 호환
                        'change_sign': item.get('pred_pre_sig', ''),
                    })

                logger.info(f"✅ 거래량 순위 {len(normalized_list)}개 조회 완료")
                return normalized_list
            else:
                error_msg = response.get('return_msg', 'Unknown error') if response else 'No response'
                logger.error(f"❌ 거래량 순위 조회 실패: {error_msg}")
                logger.error(f"Response code: {response.get('return_code') if response else 'N/A'}")
                logger.debug(f"Full response: {response}")
                return []

        except Exception as e:
            logger.error(f"❌ 거래량 순위 조회 중 예외 발생: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_price_change_rank(
        self,
        market: str = 'ALL',
        sort: str = 'rise',
        limit: int = 20,
        date: str = None
    ) -> List[Dict[str, Any]]:
        """
        전일대비 등락률 상위 조회 (ka10027)

        Args:
            market: 시장구분 ('ALL', 'KOSPI', 'KOSDAQ')
            sort: 정렬 ('rise': 상승률, 'fall': 하락률)
            limit: 조회 건수 (최대 200, 실제로는 40개씩 반환)
            date: 조회일 (현재 미사용)

        Returns:
            등락률 순위 리스트

        Note:
            이 API는 실시간 전일 데이터만 제공합니다.
            주말/공휴일/장마감 후에는 데이터가 제공되지 않을 수 있습니다.
        """
        try:
            # 시장 코드 변환 (successful_apis.json 검증된 값)
            market_map = {'ALL': '000', 'KOSPI': '001', 'KOSDAQ': '101'}
            mrkt_tp = market_map.get(market.upper(), '001')

            # 정렬 타입 변환 (검증된 값: 1=상승률, 2=하락률로 추정)
            sort_map = {'rise': '1', 'fall': '2'}
            sort_tp = sort_map.get(sort.lower(), '1')

            sort_name = "상승률" if sort == 'rise' else "하락률"
            logger.info(f"{sort_name} 순위 조회 시작 (market={market}, limit={limit})")

            body = {
                "mrkt_tp": mrkt_tp,          # 시장구분 (000:전체, 001:KOSPI, 101:KOSDAQ)
                "sort_tp": sort_tp,           # 정렬구분 (1:상승률, 2:하락률)
                "trde_qty_cnd": "0100",       # 거래량 조건 (검증된 값)
                "stk_cnd": "1",               # 종목 조건 (검증된 값)
                "crd_cnd": "0",               # 신용 조건 (0: 전체)
                "updown_incls": "1",          # 상한하한 포함 (0: 제외, 1: 포함)
                "pric_cnd": "0",              # 가격 조건 (0: 전체)
                "trde_prica_cnd": "0",        # 거래대금 조건 (0: 전체)
                "stex_tp": "3"                # 증권거래소 (3: 전체)
            }

            response = self.client.request(
                api_id="ka10027",
                body=body,
                path="rkinfo"
            )

            if response and response.get('return_code') == 0:
                # ka10027 API는 'pred_pre_flu_rt_upper' 키에 데이터 반환
                rank_list = response.get('pred_pre_flu_rt_upper', [])

                if not rank_list:
                    logger.warning("⚠️ API 호출 성공했으나 데이터가 비어있습니다 (장마감 후/주말/공휴일일 수 있음)")
                    return []

                # 데이터 정규화: API 응답 키 -> 표준 키
                normalized_list = []
                for item in rank_list[:limit]:
                    normalized_list.append({
                        'code': item.get('stk_cd', '').replace('_AL', ''),  # _AL 접미사 제거
                        'name': item.get('stk_nm', ''),
                        'price': int(item.get('cur_prc', '0').replace('+', '').replace('-', '')),
                        'change_rate': float(item.get('flu_rt', '0').replace('+', '').replace('-', '')),
                        'volume': int(item.get('now_trde_qty', '0')),
                        'change': int(item.get('pred_pre', '0').replace('+', '').replace('-', '')),
                        'change_sign': item.get('pred_pre_sig', ''),
                    })

                logger.info(f"✅ {sort_name} 순위 {len(normalized_list)}개 조회 완료")
                return normalized_list
            else:
                error_msg = response.get('return_msg', 'Unknown error') if response else 'No response'
                logger.error(f"❌ 등락률 순위 조회 실패: {error_msg}")
                logger.error(f"Response code: {response.get('return_code') if response else 'N/A'}")
                logger.debug(f"Full response: {response}")
                return []

        except Exception as e:
            logger.error(f"❌ 등락률 순위 조회 중 예외 발생: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_trading_value_rank(
        self,
        market: str = 'ALL',
        limit: int = 20,
        include_managed: bool = False
    ) -> List[Dict[str, Any]]:
        """
        거래대금 상위 조회 (ka10032)

        Args:
            market: 시장구분 ('ALL', 'KOSPI', 'KOSDAQ')
            limit: 조회 건수 (최대 200)
            include_managed: 관리종목 포함 여부

        Returns:
            거래대금 순위 리스트

        Note:
            이 API는 실시간 전일 데이터만 제공합니다.
            주말/공휴일/장마감 후에는 데이터가 제공되지 않을 수 있습니다.
        """
        try:
            # 시장 코드 변환 (successful_apis.json 검증된 값)
            market_map = {'ALL': '000', 'KOSPI': '001', 'KOSDAQ': '101'}
            mrkt_tp = market_map.get(market.upper(), '001')

            logger.info(f"거래대금 순위 조회 시작 (market={market}, limit={limit})")

            body = {
                "mrkt_tp": mrkt_tp,               # 시장구분
                "mang_stk_incls": "1" if include_managed else "0",  # 관리종목 포함
                "stex_tp": "3"                    # 증권거래소 (3: 전체)
            }

            response = self.client.request(
                api_id="ka10032",
                body=body,
                path="rkinfo"
            )

            if response and response.get('return_code') == 0:
                # 응답 키 찾기 (자동 탐색)
                data_keys = [k for k in response.keys() if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]

                # 첫 번째 리스트 키 사용
                rank_list = []
                for key in data_keys:
                    val = response.get(key)
                    if isinstance(val, list) and len(val) > 0:
                        rank_list = val
                        break

                if not rank_list:
                    logger.warning("⚠️ API 호출 성공했으나 데이터가 비어있습니다 (장마감 후/주말/공휴일일 수 있음)")
                    return []

                # 데이터 정규화
                normalized_list = []
                for item in rank_list[:limit]:
                    normalized_list.append({
                        'code': item.get('stk_cd', '').replace('_AL', ''),
                        'name': item.get('stk_nm', ''),
                        'price': int(item.get('cur_pric', '0').replace('+', '').replace('-', '')),
                        'trading_value': int(item.get('trde_prica', '0')),  # 거래대금
                        'volume': int(item.get('trde_qty', '0')),
                        'change': int(item.get('pred_pre', '0').replace('+', '').replace('-', '')),
                        'change_sign': item.get('pred_pre_sig', ''),
                    })

                logger.info(f"✅ 거래대금 순위 {len(normalized_list)}개 조회 완료")
                return normalized_list
            else:
                error_msg = response.get('return_msg', 'Unknown error') if response else 'No response'
                logger.error(f"❌ 거래대금 순위 조회 실패: {error_msg}")
                logger.error(f"Response code: {response.get('return_code') if response else 'N/A'}")
                logger.debug(f"Full response: {response}")
                return []

        except Exception as e:
            logger.error(f"❌ 거래대금 순위 조회 중 예외 발생: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_volume_surge_rank(
        self,
        market: str = 'ALL',
        limit: int = 20,
        time_interval: int = 5
    ) -> List[Dict[str, Any]]:
        """
        거래량 급증 종목 조회 (ka10023)

        Args:
            market: 시장구분 ('ALL', 'KOSPI', 'KOSDAQ')
            limit: 조회 건수
            time_interval: 시간 간격 (분)

        Returns:
            거래량 급증 순위 리스트
        """
        market_map = {'ALL': '000', 'KOSPI': '001', 'KOSDAQ': '101'}
        mrkt_tp = market_map.get(market.upper(), '000')

        body = {
            "mrkt_tp": mrkt_tp,
            "trde_qty_tp": "100",  # 거래량 조건
            "sort_tp": "2",        # 정렬 타입
            "tm_tp": "1",          # 시간 타입 (1:분, 2:시간)
            "tm": str(time_interval),  # 시간 간격
            "stk_cnd": "0",
            "pric_tp": "0",
            "stex_tp": "3"
        }

        response = self.client.request(
            api_id="ka10023",
            body=body,
            path="rkinfo"
        )

        if response and response.get('return_code') == 0:
            # 응답 키 찾기
            data_keys = [k for k in response.keys() if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]

            rank_list = []
            for key in data_keys:
                val = response.get(key)
                if isinstance(val, list) and len(val) > 0:
                    rank_list = val
                    break

            # 데이터 정규화
            normalized_list = []
            for item in rank_list[:limit]:
                normalized_list.append({
                    'code': item.get('stk_cd', '').replace('_AL', ''),
                    'name': item.get('stk_nm', ''),
                    'price': int(item.get('cur_prc', '0').replace('+', '').replace('-', '')),
                    'volume': int(item.get('trde_qty', '0')),
                    'volume_increase_rate': float(item.get('qty_incrs_rt', '0')),  # 거래량 증가율
                    'change_rate': float(item.get('flu_rt', '0').replace('+', '').replace('-', '')),
                })

            logger.info(f"거래량 급증 {len(normalized_list)}개 조회 완료")
            return normalized_list
        else:
            logger.error(f"거래량 급증 조회 실패: {response.get('return_msg')}")
            return []

    def get_intraday_change_rank(
        self,
        market: str = 'ALL',
        sort: str = 'rise',
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        시가대비 등락률 순위 조회 (ka10028)

        Args:
            market: 시장구분 ('ALL', 'KOSPI', 'KOSDAQ')
            sort: 정렬 ('rise': 상승률, 'fall': 하락률)
            limit: 조회 건수

        Returns:
            시가대비 등락률 순위 리스트
        """
        market_map = {'ALL': '000', 'KOSPI': '001', 'KOSDAQ': '101'}
        mrkt_tp = market_map.get(market.upper(), '000')

        # 정렬 타입 (1:상승률, 2:하락률)
        sort_map = {'rise': '1', 'fall': '2'}
        sort_tp = sort_map.get(sort.lower(), '1')

        body = {
            "sort_tp": sort_tp,
            "trde_qty_cnd": "0000",
            "mrkt_tp": mrkt_tp,
            "updown_incls": "1",
            "stk_cnd": "0",
            "crd_cnd": "0",
            "trde_prica_cnd": "0",
            "flu_cnd": "1",
            "stex_tp": "3"
        }

        response = self.client.request(
            api_id="ka10028",
            body=body,
            path="stkinfo"
        )

        if response and response.get('return_code') == 0:
            # 응답 키 찾기
            data_keys = [k for k in response.keys() if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]

            rank_list = []
            for key in data_keys:
                val = response.get(key)
                if isinstance(val, list) and len(val) > 0:
                    rank_list = val
                    break

            # 데이터 정규화
            normalized_list = []
            for item in rank_list[:limit]:
                normalized_list.append({
                    'code': item.get('stk_cd', '').replace('_AL', ''),
                    'name': item.get('stk_nm', ''),
                    'price': int(item.get('cur_prc', '0').replace('+', '').replace('-', '')),
                    'open_price': int(item.get('open_prc', '0')),  # 시가
                    'intraday_change_rate': float(item.get('flu_rt', '0').replace('+', '').replace('-', '')),
                    'volume': int(item.get('trde_qty', '0')),
                })

            sort_name = "상승률" if sort == 'rise' else "하락률"
            logger.info(f"시가대비 {sort_name} {len(normalized_list)}개 조회 완료")
            return normalized_list
        else:
            logger.error(f"시가대비 등락률 조회 실패: {response.get('return_msg')}")
            return []

    def get_foreign_period_trading_rank(
        self,
        market: str = 'KOSPI',
        trade_type: str = 'buy',
        period_days: int = 5,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        외국인 기간별 매매 상위 (ka10034)

        Args:
            market: 시장구분 ('KOSPI', 'KOSDAQ')
            trade_type: 매매구분 ('buy': 순매수, 'sell': 순매도)
            period_days: 기간 (1, 3, 5, 10, 20일)
            limit: 조회 건수

        Returns:
            외국인 기간별 매매 순위
        """
        market_map = {'KOSPI': '001', 'KOSDAQ': '101'}
        mrkt_tp = market_map.get(market.upper(), '001')

        trade_map = {'buy': '2', 'sell': '1'}
        trde_tp = trade_map.get(trade_type.lower(), '2')

        body = {
            "mrkt_tp": mrkt_tp,
            "trde_tp": trde_tp,
            "dt": str(period_days),
            "stex_tp": "1"
        }

        response = self.client.request(api_id="ka10034", body=body, path="rkinfo")

        if response and response.get('return_code') == 0:
            data_keys = [k for k in response.keys() if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]
            rank_list = []
            for key in data_keys:
                val = response.get(key)
                if isinstance(val, list) and len(val) > 0:
                    rank_list = val
                    break

            normalized_list = []
            for item in rank_list[:limit]:
                normalized_list.append({
                    'code': item.get('stk_cd', '').replace('_AL', ''),
                    'name': item.get('stk_nm', ''),
                    'price': int(item.get('cur_prc', '0').replace('+', '').replace('-', '')),
                    'foreign_net_buy': int(item.get('frg_nt_qty', '0')),  # 외국인 순매수량
                    'change_rate': float(item.get('flu_rt', '0').replace('+', '').replace('-', '')),
                })

            logger.info(f"외국인 {period_days}일 매매 {len(normalized_list)}개 조회")
            return normalized_list
        else:
            logger.error(f"외국인 기간별 매매 조회 실패: {response.get('return_msg')}")
            return []

    def get_foreign_continuous_trading_rank(
        self,
        market: str = 'KOSPI',
        trade_type: str = 'buy',
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        외국인 연속 순매매 상위 (ka10035)

        Args:
            market: 시장구분 ('KOSPI', 'KOSDAQ')
            trade_type: 매매구분 ('buy': 순매수, 'sell': 순매도)
            limit: 조회 건수

        Returns:
            외국인 연속 순매매 순위
        """
        market_map = {'KOSPI': '001', 'KOSDAQ': '101'}
        mrkt_tp = market_map.get(market.upper(), '001')

        trade_map = {'buy': '2', 'sell': '1'}
        trde_tp = trade_map.get(trade_type.lower(), '2')

        body = {
            "mrkt_tp": mrkt_tp,
            "trde_tp": trde_tp,
            "base_dt_tp": "0",
            "stex_tp": "1"
        }

        response = self.client.request(api_id="ka10035", body=body, path="rkinfo")

        if response and response.get('return_code') == 0:
            data_keys = [k for k in response.keys() if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]
            rank_list = []
            for key in data_keys:
                val = response.get(key)
                if isinstance(val, list) and len(val) > 0:
                    rank_list = val
                    break

            normalized_list = []
            for item in rank_list[:limit]:
                normalized_list.append({
                    'code': item.get('stk_cd', '').replace('_AL', ''),
                    'name': item.get('stk_nm', ''),
                    'price': int(item.get('cur_prc', '0').replace('+', '').replace('-', '')),
                    'continuous_days': int(item.get('cont_dt', '0')),  # 연속일수
                    'total_net_buy': int(item.get('tot_nt_qty', '0')),  # 총 순매수량
                })

            logger.info(f"외국인 연속매매 {len(normalized_list)}개 조회")
            return normalized_list
        else:
            logger.error(f"외국인 연속 순매매 조회 실패: {response.get('return_msg')}")
            return []

    def get_foreign_institution_trading_rank(
        self,
        market: str = 'KOSPI',
        amount_or_qty: str = 'amount',
        date: str = None,
        limit: int = 20,
        investor_type: str = 'foreign_buy'
    ) -> List[Dict[str, Any]]:
        """
        외국인/기관 매매 상위 (ka90009)

        ⚠️ 주의: 이 API는 현재가를 제공하지 않습니다!
        각 항목은 4개의 카테고리로 구성됩니다:
        - for_netprps_: 외국인 순매수 상위
        - for_netslmt_: 외국인 순매도 상위
        - orgn_netprps_: 기관 순매수 상위
        - orgn_netslmt_: 기관 순매도 상위

        Args:
            market: 시장구분 ('KOSPI', 'KOSDAQ')
            amount_or_qty: 조회구분 ('amount': 금액, 'qty': 수량)
            date: 조회일 (YYYYMMDD, None이면 오늘)
            limit: 조회 건수
            investor_type: 투자자 유형 ('foreign_buy': 외국인 순매수, 'foreign_sell': 외국인 순매도,
                                      'institution_buy': 기관 순매수, 'institution_sell': 기관 순매도)

        Returns:
            외국인/기관 매매 순위 (현재가 없음)
        """
        from utils.trading_date import get_last_trading_date

        market_map = {'KOSPI': '001', 'KOSDAQ': '101'}
        mrkt_tp = market_map.get(market.upper(), '001')

        amt_qty_map = {'amount': '1', 'qty': '2'}
        amt_qty_tp = amt_qty_map.get(amount_or_qty.lower(), '1')

        if date is None:
            date = get_last_trading_date()  # 이미 'YYYYMMDD' 형식 문자열 반환

        body = {
            "mrkt_tp": mrkt_tp,
            "amt_qty_tp": amt_qty_tp,
            "qry_dt_tp": "1",
            "date": date,
            "stex_tp": "1"
        }

        response = self.client.request(api_id="ka90009", body=body, path="rkinfo")

        if response and response.get('return_code') == 0:
            # ka90009 API는 'frgnr_orgn_trde_upper' 키에 데이터 반환
            rank_list = response.get('frgnr_orgn_trde_upper', [])

            # 투자자 유형에 따른 필드명 매핑
            field_map = {
                'foreign_buy': ('for_netprps_stk_cd', 'for_netprps_stk_nm', 'for_netprps_amt', 'for_netprps_qty'),
                'foreign_sell': ('for_netslmt_stk_cd', 'for_netslmt_stk_nm', 'for_netslmt_amt', 'for_netslmt_qty'),
                'institution_buy': ('orgn_netprps_stk_cd', 'orgn_netprps_stk_nm', 'orgn_netprps_amt', 'orgn_netprps_qty'),
                'institution_sell': ('orgn_netslmt_stk_cd', 'orgn_netslmt_stk_nm', 'orgn_netslmt_amt', 'orgn_netslmt_qty'),
            }

            code_field, name_field, amt_field, qty_field = field_map.get(investor_type, field_map['foreign_buy'])

            normalized_list = []
            for item in rank_list[:limit]:
                normalized_list.append({
                    'code': item.get(code_field, '').replace('_AL', ''),
                    'name': item.get(name_field, ''),
                    'net_amount': int(item.get(amt_field, '0').replace('+', '').replace('-', '')),  # 순매수/매도 금액 (백만원)
                    'net_qty': int(item.get(qty_field, '0').replace('+', '').replace('-', '')),  # 순매수/매도 수량 (천주)
                })

            type_name = {
                'foreign_buy': '외국인 순매수',
                'foreign_sell': '외국인 순매도',
                'institution_buy': '기관 순매수',
                'institution_sell': '기관 순매도'
            }.get(investor_type, investor_type)

            logger.info(f"{type_name} {len(normalized_list)}개 조회")
            return normalized_list
        else:
            logger.error(f"외국인/기관 매매 조회 실패: {response.get('return_msg')}")
            return []

    def get_credit_ratio_rank(
        self,
        market: str = 'KOSPI',
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        신용비율 상위 (ka10033)

        Args:
            market: 시장구분 ('KOSPI', 'KOSDAQ')
            limit: 조회 건수

        Returns:
            신용비율 상위 순위
        """
        market_map = {'KOSPI': '001', 'KOSDAQ': '101'}
        mrkt_tp = market_map.get(market.upper(), '001')

        body = {
            "mrkt_tp": mrkt_tp,
            "trde_qty_tp": "100",
            "stk_cnd": "0",
            "updown_incls": "1",
            "crd_cnd": "0",
            "stex_tp": "3"
        }

        response = self.client.request(api_id="ka10033", body=body, path="rkinfo")

        if response and response.get('return_code') == 0:
            data_keys = [k for k in response.keys() if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]
            rank_list = []
            for key in data_keys:
                val = response.get(key)
                if isinstance(val, list) and len(val) > 0:
                    rank_list = val
                    break

            normalized_list = []
            for item in rank_list[:limit]:
                normalized_list.append({
                    'code': item.get('stk_cd', '').replace('_AL', ''),
                    'name': item.get('stk_nm', ''),
                    'price': int(item.get('cur_prc', '0').replace('+', '').replace('-', '')),
                    'credit_ratio': float(item.get('crd_rt', '0')),  # 신용비율
                    'credit_balance': int(item.get('crd_rmn_qty', '0')),  # 신용잔고
                })

            logger.info(f"신용비율 {len(normalized_list)}개 조회")
            return normalized_list
        else:
            logger.error(f"신용비율 조회 실패: {response.get('return_msg')}")
            return []

    def get_investor_intraday_trading_rank(
        self,
        market: str = 'KOSPI',
        investor_type: str = 'foreign',
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        장중 투자자별 매매 상위 (ka10065)

        ⚠️ 주의: 이 API는 현재가를 제공하지 않습니다!
        매도수량, 매수수량, 순매수량만 제공됩니다.

        Args:
            market: 시장구분 ('KOSPI', 'KOSDAQ')
            investor_type: 투자자구분 ('foreign': 외국인, 'institution': 기관, 'individual': 개인)
            limit: 조회 건수

        Returns:
            투자자별 매매 순위 (현재가 없음)
        """
        market_map = {'KOSPI': '001', 'KOSDAQ': '101'}
        mrkt_tp = market_map.get(market.upper(), '001')

        # 투자자 타입: 9000=외국인, 1000=개인, 8000=기관
        investor_map = {
            'foreign': '9000',
            'institution': '8000',
            'individual': '1000'
        }
        orgn_tp = investor_map.get(investor_type.lower(), '9000')

        body = {
            "trde_tp": "1",  # 1: 순매수
            "mrkt_tp": mrkt_tp,
            "orgn_tp": orgn_tp
        }

        response = self.client.request(api_id="ka10065", body=body, path="rkinfo")

        if response and response.get('return_code') == 0:
            # ka10065 API는 'opmr_invsr_trde_upper' 키에 데이터 반환
            rank_list = response.get('opmr_invsr_trde_upper', [])

            normalized_list = []
            for item in rank_list[:limit]:
                # 값에서 +,- 기호 제거하고 숫자로 변환
                sel_qty = int(item.get('sel_qty', '0').replace('+', '').replace('-', ''))
                buy_qty = int(item.get('buy_qty', '0').replace('+', '').replace('-', ''))
                netslmt = int(item.get('netslmt', '0').replace('+', '').replace('-', ''))

                normalized_list.append({
                    'code': item.get('stk_cd', '').replace('_AL', ''),
                    'name': item.get('stk_nm', ''),
                    'sell_qty': sel_qty,      # 매도수량
                    'buy_qty': buy_qty,       # 매수수량
                    'net_buy_qty': netslmt,   # 순매수량 (매수-매도)
                })

            investor_name = {'foreign': '외국인', 'institution': '기관', 'individual': '개인'}.get(investor_type.lower(), investor_type)
            logger.info(f"{investor_name} 장중매매 {len(normalized_list)}개 조회")
            return normalized_list
        else:
            logger.error(f"투자자별 매매 조회 실패: {response.get('return_msg')}")
            return []

    def get_sector_list(self) -> List[Dict[str, Any]]:
        """
        업종 목록 조회
        
        Returns:
            업종 목록
        """
        response = self.client.request(
            api_id="DOSK_0020",
            body={},
            path="inquire/sector/list"
        )
        
        if response and response.get('return_code') == 0:
            sectors = response.get('output', [])
            logger.info(f"업종 {len(sectors)}개 조회 완료")
            return sectors
        else:
            logger.error(f"업종 목록 조회 실패: {response.get('return_msg')}")
            return []
    
    def get_sector_info(self, sector_code: str) -> Optional[Dict[str, Any]]:
        """
        업종 정보 조회
        
        Args:
            sector_code: 업종코드
        
        Returns:
            업종 정보
        """
        body = {
            "sector_code": sector_code
        }
        
        response = self.client.request(
            api_id="DOSK_0021",
            body=body,
            path="inquire/sector/info"
        )
        
        if response and response.get('return_code') == 0:
            sector_info = response.get('output', {})
            logger.info(f"업종 정보 조회 완료: {sector_info.get('sector_name', '')}")
            return sector_info
        else:
            logger.error(f"업종 정보 조회 실패: {response.get('return_msg')}")
            return None
    
    def get_theme_list(self) -> List[Dict[str, Any]]:
        """
        테마 목록 조회
        
        Returns:
            테마 목록
        """
        response = self.client.request(
            api_id="DOSK_0030",
            body={},
            path="inquire/theme/list"
        )
        
        if response and response.get('return_code') == 0:
            themes = response.get('output', [])
            logger.info(f"테마 {len(themes)}개 조회 완료")
            return themes
        else:
            logger.error(f"테마 목록 조회 실패: {response.get('return_msg')}")
            return []
    
    def get_theme_stocks(self, theme_code: str) -> List[Dict[str, Any]]:
        """
        테마 종목 조회
        
        Args:
            theme_code: 테마코드
        
        Returns:
            테마 종목 리스트
        """
        body = {
            "theme_code": theme_code
        }
        
        response = self.client.request(
            api_id="DOSK_0031",
            body=body,
            path="inquire/theme/stocks"
        )
        
        if response and response.get('return_code') == 0:
            stocks = response.get('output', [])
            logger.info(f"테마 종목 {len(stocks)}개 조회 완료")
            return stocks
        else:
            logger.error(f"테마 종목 조회 실패: {response.get('return_msg')}")
            return []
    
    def get_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        종목 상세 정보 조회
        
        Args:
            stock_code: 종목코드
        
        Returns:
            종목 상세 정보
        """
        body = {
            "stock_code": stock_code
        }
        
        response = self.client.request(
            api_id="DOSK_0005",
            body=body,
            path="inquire/stock/info"
        )
        
        if response and response.get('return_code') == 0:
            stock_info = response.get('output', {})
            logger.info(f"{stock_code} 상세 정보 조회 완료")
            return stock_info
        else:
            logger.error(f"종목 정보 조회 실패: {response.get('return_msg')}")
            return None
    
    def search_stock(self, keyword: str) -> List[Dict[str, Any]]:
        """
        종목 검색
        
        Args:
            keyword: 검색어
        
        Returns:
            검색 결과 리스트
        """
        body = {
            "keyword": keyword
        }
        
        response = self.client.request(
            api_id="DOSK_0006",
            body=body,
            path="inquire/stock/search"
        )
        
        if response and response.get('return_code') == 0:
            results = response.get('output', [])
            logger.info(f"'{keyword}' 검색 결과 {len(results)}개")
            return results
        else:
            logger.error(f"종목 검색 실패: {response.get('return_msg')}")
            return []
    
    def get_investor_trading(
        self,
        stock_code: str,
        date: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        투자자별 매매 동향 조회 (키움증권 API ka10059)

        Args:
            stock_code: 종목코드
            date: 조회일 (YYYYMMDD, None이면 최근 거래일 자동 계산)

        Returns:
            투자자별 매매 동향
            {
                '기관_순매수': 10000,
                '외국인_순매수': 5000,
                '개인_순매수': -15000,
                ...
            }
        """
        # 날짜 자동 계산
        if not date:
            date = get_last_trading_date()

        body = {
            "stk_cd": stock_code,
            "dt": date,
            "amt_qty_tp": "1",  # 1:금액, 2:수량
            "trde_tp": "0",     # 0:순매수, 1:매수, 2:매도
            "unit_tp": "1000"   # 1000:천주, 1:단주
        }

        response = self.client.request(
            api_id="ka10059",
            body=body,
            path="stkinfo"
        )

        if response and response.get('return_code') == 0:
            # ka10059 응답 구조: stk_invsr_orgn 리스트
            stk_invsr_orgn = response.get('stk_invsr_orgn', [])

            if not stk_invsr_orgn:
                logger.warning(f"{stock_code} 투자자별 매매 데이터 없음")
                return None

            # 가장 최근 데이터 (첫 번째 항목)
            latest = stk_invsr_orgn[0]

            # 필드 파싱 (천 단위로 제공되므로 1000 곱함)
            def parse_value(val: str) -> int:
                """문자열 값을 정수로 변환 (+/- 기호 제거, 천 단위 → 원 단위)"""
                if not val:
                    return 0
                val_str = val.replace('+', '').replace('-', '').strip()
                try:
                    # 천 단위로 제공되므로 1000을 곱함
                    return int(float(val_str)) * 1000
                except (ValueError, AttributeError):
                    return 0

            # 부호 확인 (+ 또는 -)
            def get_sign(val: str) -> int:
                """값의 부호 반환 (1 또는 -1)"""
                if not val:
                    return 1
                return -1 if val.startswith('-') else 1

            # 기관, 외국인, 개인 순매수 추출
            orgn_val = latest.get('orgn', '0')
            frgnr_val = latest.get('frgnr_invsr', '0')
            ind_val = latest.get('ind_invsr', '0')

            institutional_net = parse_value(orgn_val) * get_sign(orgn_val)
            foreign_net = parse_value(frgnr_val) * get_sign(frgnr_val)
            individual_net = parse_value(ind_val) * get_sign(ind_val)

            investor_info = {
                '기관_순매수': institutional_net,
                '외국인_순매수': foreign_net,
                '개인_순매수': individual_net,
                '날짜': latest.get('dt', date),
                '현재가': parse_value(latest.get('cur_prc', '0')),
                '등락율': latest.get('flu_rt', '0'),
            }

            logger.info(
                f"{stock_code} 투자자별 매매 조회 완료: "
                f"기관={institutional_net:,}, 외국인={foreign_net:,}, 개인={individual_net:,}"
            )
            return investor_info
        else:
            logger.error(f"투자자별 매매 동향 조회 실패: {response.get('return_msg') if response else 'No response'}")
            return None

    def get_investor_data(
        self,
        stock_code: str,
        date: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        투자자 매매 데이터 조회 (get_investor_trading의 별칭)

        Args:
            stock_code: 종목코드
            date: 조회일 (YYYYMMDD, None이면 최근 거래일 자동 계산)

        Returns:
            투자자별 매매 동향
            {
                '기관_순매수': 10000,
                '외국인_순매수': 5000,
                ...
            }
        """
        return self.get_investor_trading(stock_code, date)

    def get_bid_ask(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        호가 데이터 조회 (get_orderbook의 별칭)

        Args:
            stock_code: 종목코드

        Returns:
            호가 정보
            {
                '매수_총잔량': 10000,
                '매도_총잔량': 8000,
                ...
            }
        """
        return self.get_orderbook(stock_code)

    def get_daily_chart(
        self,
        stock_code: str,
        period: int = 20,
        date: str = None
    ) -> List[Dict[str, Any]]:
        """
        일봉 차트 데이터 조회 (ka10081 사용)

        Args:
            stock_code: 종목코드
            period: 조회 기간 (일수) - 참고용, API는 기준일부터 과거 데이터 반환
            date: 기준일 (YYYYMMDD, None이면 최근 거래일)

        Returns:
            일봉 데이터 리스트
            [
                {
                    'date': '20231201',
                    'open': 70000,
                    'high': 71000,
                    'low': 69500,
                    'close': 70500,
                    'volume': 1000000
                },
                ...
            ]
        """
        # 날짜 자동 계산
        if not date:
            date = get_last_trading_date()

        body = {
            "stk_cd": stock_code,
            "base_dt": date,
            "upd_stkpc_tp": "1"  # 수정주가 반영
        }

        response = self.client.request(
            api_id="ka10081",
            body=body,
            path="chart"
        )

        if response and response.get('return_code') == 0:
            # ka10081은 'stk_dt_pole_chart_qry' 키에 데이터 반환
            daily_data = response.get('stk_dt_pole_chart_qry', [])

            # 데이터 표준화
            standardized_data = []
            for item in daily_data:
                try:
                    standardized_data.append({
                        'date': item.get('dt', ''),
                        'open': int(item.get('open_pric', 0)),
                        'high': int(item.get('high_pric', 0)),
                        'low': int(item.get('low_pric', 0)),
                        'close': int(item.get('cur_prc', 0)),
                        'volume': int(item.get('trde_qty', 0))
                    })
                except (ValueError, TypeError):
                    continue

            logger.info(f"{stock_code} 일봉 차트 {len(standardized_data)}개 조회 완료")
            return standardized_data[:period] if period else standardized_data  # period만큼만 반환
        else:
            logger.error(f"일봉 차트 조회 실패: {response.get('return_msg')}")
            return []

    def get_intraday_investor_trading_market(
        self,
        market: str = 'KOSPI',
        investor_type: str = 'institution',
        amount_or_qty: str = 'amount',
        exchange: str = 'KRX'
    ) -> List[Dict[str, Any]]:
        """
        장중 투자자별 매매 상위 (ka10063) - 시장 전체

        이 API는 특정 종목이 아닌 시장 전체의 투자자별 매매 동향을 조회합니다.

        Args:
            market: 시장구분 ('KOSPI', 'KOSDAQ')
            investor_type: 투자자구분 ('institution': 기관계, 'foreign': 외국인)
            amount_or_qty: 조회구분 ('amount': 금액, 'qty': 수량)
            exchange: 거래소구분 ('KRX', 'NXT', 'ALL')

        Returns:
            장중 투자자별 매매 순위 리스트
        """
        try:
            market_map = {'KOSPI': '001', 'KOSDAQ': '101'}
            mrkt_tp = market_map.get(market.upper(), '001')

            amt_qty_map = {'amount': '1', 'qty': '2'}
            amt_qty_tp = amt_qty_map.get(amount_or_qty.lower(), '1')

            investor_map = {'institution': '7', 'foreign': '6'}
            invsr = investor_map.get(investor_type.lower(), '7')

            # 외국인일 경우 외국계전체 체크
            frgn_all = '1' if investor_type.lower() == 'foreign' else '0'

            exchange_map = {'KRX': '1', 'NXT': '2', 'ALL': '3'}
            stex_tp = exchange_map.get(exchange.upper(), '1')

            body = {
                "mrkt_tp": mrkt_tp,           # 시장구분
                "amt_qty_tp": amt_qty_tp,     # 금액수량구분
                "invsr": invsr,               # 투자자별
                "frgn_all": frgn_all,         # 외국계전체
                "smtm_netprps_tp": "0",       # 동시순매수구분
                "stex_tp": stex_tp            # 거래소구분
            }

            response = self.client.request(
                api_id="ka10063",
                body=body,
                path="mrkcond"
            )

            if response and response.get('return_code') == 0:
                # 응답 키 자동 탐색
                data_keys = [k for k in response.keys() if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]

                rank_list = []
                for key in data_keys:
                    val = response.get(key)
                    if isinstance(val, list) and len(val) > 0:
                        rank_list = val
                        break

                if not rank_list:
                    logger.warning("장중 투자자별 매매 데이터 없음 (장외시간일 수 있음)")
                    return []

                # 데이터 정규화
                normalized_list = []
                for item in rank_list:
                    normalized_list.append({
                        'code': item.get('stk_cd', '').replace('_AL', ''),
                        'name': item.get('stk_nm', ''),
                        'price': int(item.get('cur_prc', '0').replace('+', '').replace('-', '')),
                        'net_buy_amount': int(item.get('netprps_amt', '0').replace('+', '').replace('-', '')),
                        'net_buy_qty': int(item.get('netprps_qty', '0').replace('+', '').replace('-', '')),
                        'change_rate': float(item.get('flu_rt', '0').replace('+', '').replace('-', '')),
                    })

                investor_name = {'institution': '기관', 'foreign': '외국인'}.get(investor_type.lower(), investor_type)
                logger.info(f"장중 {investor_name} 매매 {len(normalized_list)}개 조회")
                return normalized_list
            else:
                logger.error(f"장중 투자자별 매매 조회 실패: {response.get('return_msg')}")
                return []

        except Exception as e:
            logger.error(f"장중 투자자별 매매 조회 중 예외 발생: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_postmarket_investor_trading_market(
        self,
        market: str = 'KOSPI',
        amount_or_qty: str = 'amount',
        trade_type: str = 'net_buy',
        exchange: str = 'KRX'
    ) -> List[Dict[str, Any]]:
        """
        장마감후 투자자별 매매 상위 (ka10066) - 시장 전체

        이 API는 특정 종목이 아닌 시장 전체의 장마감후 투자자별 매매 동향을 조회합니다.

        Args:
            market: 시장구분 ('KOSPI', 'KOSDAQ')
            amount_or_qty: 조회구분 ('amount': 금액, 'qty': 수량)
            trade_type: 매매구분 ('net_buy': 순매수, 'buy': 매수, 'sell': 매도)
            exchange: 거래소구분 ('KRX', 'NXT', 'ALL')

        Returns:
            장마감후 투자자별 매매 순위 리스트
        """
        try:
            market_map = {'KOSPI': '001', 'KOSDAQ': '101'}
            mrkt_tp = market_map.get(market.upper(), '001')

            amt_qty_map = {'amount': '1', 'qty': '2'}
            amt_qty_tp = amt_qty_map.get(amount_or_qty.lower(), '1')

            trade_map = {'net_buy': '0', 'buy': '1', 'sell': '2'}
            trde_tp = trade_map.get(trade_type.lower(), '0')

            exchange_map = {'KRX': '1', 'NXT': '2', 'ALL': '3'}
            stex_tp = exchange_map.get(exchange.upper(), '1')

            body = {
                "mrkt_tp": mrkt_tp,       # 시장구분
                "amt_qty_tp": amt_qty_tp, # 금액수량구분
                "trde_tp": trde_tp,       # 매매구분
                "stex_tp": stex_tp        # 거래소구분
            }

            response = self.client.request(
                api_id="ka10066",
                body=body,
                path="mrkcond"
            )

            if response and response.get('return_code') == 0:
                # 응답 키 자동 탐색
                data_keys = [k for k in response.keys() if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]

                rank_list = []
                for key in data_keys:
                    val = response.get(key)
                    if isinstance(val, list) and len(val) > 0:
                        rank_list = val
                        break

                if not rank_list:
                    logger.warning("장마감후 투자자별 매매 데이터 없음 (장외시간일 수 있음)")
                    return []

                # 데이터 정규화
                normalized_list = []
                for item in rank_list:
                    normalized_list.append({
                        'code': item.get('stk_cd', '').replace('_AL', ''),
                        'name': item.get('stk_nm', ''),
                        'individual_net': int(item.get('ind_invsr', '0').replace('+', '').replace('-', '')),
                        'foreign_net': int(item.get('frgnr_invsr', '0').replace('+', '').replace('-', '')),
                        'institution_net': int(item.get('orgn', '0').replace('+', '').replace('-', '')),
                        'financial_net': int(item.get('fnac_orgn', '0').replace('+', '').replace('-', '')),
                        'insurance_net': int(item.get('isrc', '0').replace('+', '').replace('-', '')),
                    })

                trade_name = {'net_buy': '순매수', 'buy': '매수', 'sell': '매도'}.get(trade_type.lower(), trade_type)
                logger.info(f"장마감후 {trade_name} {len(normalized_list)}개 조회")
                return normalized_list
            else:
                logger.error(f"장마감후 투자자별 매매 조회 실패: {response.get('return_msg')}")
                return []

        except Exception as e:
            logger.error(f"장마감후 투자자별 매매 조회 중 예외 발생: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_institutional_trading_trend(
        self,
        stock_code: str,
        days: int = 5,
        price_type: str = 'buy'
    ) -> Optional[Dict[str, Any]]:
        """
        종목별 기관매매추이 (ka10045)

        특정 종목에 대한 기관 및 외국인의 매매 추세와 추정 단가를 조회합니다.

        Args:
            stock_code: 종목코드
            days: 조회 일수 (1, 5, 10, 20 등)
            price_type: 단가구분 ('buy': 매수단가, 'sell': 매도단가)

        Returns:
            기관매매추이 데이터
            {
                'institution_trend': [...],  # 기관 매매 추이
                'foreign_trend': [...],      # 외국인 매매 추이
                'estimated_prices': {...}    # 추정 단가 정보
            }
        """
        try:
            from datetime import datetime, timedelta

            # 날짜 범위 계산
            end_date = datetime.strptime(get_last_trading_date(), "%Y%m%d")
            start_date = end_date - timedelta(days=days)
            start_dt_str = start_date.strftime("%Y%m%d")
            end_dt_str = end_date.strftime("%Y%m%d")

            price_type_map = {'buy': '1', 'sell': '2'}
            prsm_unp_tp = price_type_map.get(price_type.lower(), '1')

            body = {
                "stk_cd": stock_code,
                "strt_dt": start_dt_str,      # 시작일자
                "end_dt": end_dt_str,         # 종료일자
                "orgn_prsm_unp_tp": prsm_unp_tp,  # 기관추정단가구분
                "for_prsm_unp_tp": prsm_unp_tp    # 외인추정단가구분
            }

            response = self.client.request(
                api_id="ka10045",
                body=body,
                path="mrkcond"
            )

            if response and response.get('return_code') == 0:
                # 응답 키 자동 탐색
                data_keys = [k for k in response.keys() if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]

                trend_data = {}
                for key in data_keys:
                    val = response.get(key)
                    if isinstance(val, list) and len(val) > 0:
                        trend_data[key] = val

                if not trend_data:
                    logger.warning(f"{stock_code} 기관매매추이 데이터 없음")
                    return None

                logger.info(f"{stock_code} 기관매매추이 조회 완료 ({days}일)")
                return trend_data
            else:
                logger.error(f"기관매매추이 조회 실패: {response.get('return_msg')}")
                return None

        except Exception as e:
            logger.error(f"기관매매추이 조회 중 예외 발생: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_securities_firm_trading(
        self,
        firm_code: str,
        stock_code: str,
        days: int = 3
    ) -> Optional[List[Dict[str, Any]]]:
        """
        증권사별 종목매매동향 (ka10078)

        특정 증권사의 특정 종목에 대한 매매 동향을 조회합니다.

        Args:
            firm_code: 회원사코드 (예: '040'=KB증권, '039'=교보증권, '001'=한국투자증권)
            stock_code: 종목코드
            days: 조회 일수 (기본 3일)

        Returns:
            증권사별 매매동향 리스트
            [
                {
                    'date': '20231201',
                    'buy_qty': 10000,
                    'sell_qty': 5000,
                    'net_qty': 5000,
                    ...
                },
                ...
            ]
        """
        try:
            from datetime import datetime, timedelta

            # 날짜 범위 계산
            end_date = datetime.strptime(get_last_trading_date(), "%Y%m%d")
            start_date = end_date - timedelta(days=days)
            start_dt_str = start_date.strftime("%Y%m%d")
            end_dt_str = end_date.strftime("%Y%m%d")

            body = {
                "mmcm_cd": firm_code,      # 회원사코드
                "stk_cd": stock_code,      # 종목코드
                "strt_dt": start_dt_str,   # 시작일자
                "end_dt": end_dt_str       # 종료일자
            }

            response = self.client.request(
                api_id="ka10078",
                body=body,
                path="mrkcond"
            )

            if response and response.get('return_code') == 0:
                # 응답 키 자동 탐색
                data_keys = [k for k in response.keys() if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]

                # 디버깅: raw response 출력 (첫 번째 호출만, WARNING 레벨로 강제 출력)
                if not hasattr(self, '_firm_trading_debug_shown'):
                    print(f"\n[증권사 API 디버깅]")
                    print(f"  response keys: {list(response.keys())}")
                    print(f"  data_keys: {data_keys}")
                    for key in data_keys[:3]:  # 처음 3개
                        val = response.get(key)
                        if isinstance(val, list):
                            print(f"  {key} = list({len(val)} items)")
                            if len(val) > 0:
                                print(f"  first item: {val[0]}")
                            else:
                                print(f"  ⚠️ 빈 리스트!")
                        else:
                            print(f"  {key} = {type(val).__name__}")
                    print()
                    self._firm_trading_debug_shown = True

                trading_list = []
                for key in data_keys:
                    val = response.get(key)
                    if isinstance(val, list) and len(val) > 0:
                        trading_list = val
                        break

                if not trading_list:
                    logger.warning(f"증권사({firm_code}) {stock_code} 매매동향 데이터 없음 (빈 응답)")
                    return None

                # 데이터 정규화
                normalized_list = []
                for item in trading_list:
                    # netprps_qty는 음수일 수 있음 (순매도)
                    netprps_qty_str = item.get('netprps_qty', '0').replace('+', '').strip()
                    net_qty = int(netprps_qty_str) if netprps_qty_str and netprps_qty_str != '' else 0

                    normalized_list.append({
                        'date': item.get('dt', ''),
                        'buy_qty': int(item.get('buy_qty', '0').replace('+', '').replace('-', '').strip() or '0'),
                        'sell_qty': int(item.get('sell_qty', '0').replace('+', '').replace('-', '').strip() or '0'),
                        'net_qty': net_qty,  # 음수 보존 (순매도는 음수)
                        'buy_amount': 0,  # API에서 제공하지 않음
                        'sell_amount': 0,  # API에서 제공하지 않음
                    })

                logger.info(f"증권사({firm_code}) {stock_code} 매매동향 {len(normalized_list)}건 조회")
                return normalized_list
            else:
                logger.error(f"증권사별 매매동향 조회 실패: {response.get('return_msg')}")
                return None

        except Exception as e:
            logger.error(f"증권사별 매매동향 조회 중 예외 발생: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_execution_intensity(
        self,
        stock_code: str,
        days: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        체결강도 조회 (ka10047)

        Args:
            stock_code: 종목코드
            days: 조회 일수 (기본 1일, 최근 데이터만 사용)

        Returns:
            체결강도 데이터
            {
                'execution_intensity': 120.5,  # 체결강도
                'date': '20231201',
                'current_price': 50000,
                ...
            }
        """
        try:
            response = self.client.request(
                api_id="ka10047",
                body={"stk_cd": stock_code},
                path="mrkcond"
            )

            if response and response.get('return_code') == 0:
                # 응답 키 자동 탐색
                data_keys = [k for k in response.keys() if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]

                if data_keys:
                    first_key = data_keys[0]
                    data_list = response.get(first_key, [])

                    if isinstance(data_list, list) and len(data_list) > 0:
                        # 최근 데이터 (첫 번째)
                        recent = data_list[0]

                        # 체결강도 추출
                        execution_intensity = recent.get('cntr_str', '0')
                        try:
                            execution_intensity_value = float(execution_intensity.replace(',', '').replace('+', '').replace('-', ''))
                        except (ValueError, AttributeError):
                            execution_intensity_value = 0.0

                        result = {
                            'execution_intensity': execution_intensity_value,
                            'date': recent.get('dt', ''),
                            'current_price': recent.get('cur_prc', 0),
                            'change_rate': recent.get('flu_rt', 0),
                            'volume': recent.get('trde_qty', 0),
                        }

                        logger.info(f"{stock_code} 체결강도: {execution_intensity_value}")
                        return result

                logger.warning(f"체결강도 데이터 없음: {stock_code}")
                return None
            else:
                logger.error(f"체결강도 조회 실패: {response.get('return_msg')}")
                return None

        except Exception as e:
            logger.error(f"체결강도 조회 중 예외 발생: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_program_trading(
        self,
        stock_code: str,
        days: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        프로그램매매 추이 조회 (ka90013)

        Args:
            stock_code: 종목코드
            days: 조회 일수 (기본 1일, 최근 데이터만 사용)

        Returns:
            프로그램매매 데이터
            {
                'program_net_buy': 5000000,  # 프로그램순매수금액 (원)
                'program_buy': 10000000,     # 프로그램매수금액
                'program_sell': 5000000,     # 프로그램매도금액
                'date': '20231201',
                ...
            }
        """
        try:
            response = self.client.request(
                api_id="ka90013",
                body={
                    "stk_cd": stock_code,
                    "amt_qty_tp": "1",  # 1:금액
                    "date": ""  # 빈 값이면 최근일
                },
                path="mrkcond"
            )

            if response and response.get('return_code') == 0:
                # 응답 키 자동 탐색
                data_keys = [k for k in response.keys() if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]

                if data_keys:
                    first_key = data_keys[0]
                    data_list = response.get(first_key, [])

                    if isinstance(data_list, list) and len(data_list) > 0:
                        # 최근 데이터 (첫 번째)
                        recent = data_list[0]

                        # 프로그램순매수금액 추출
                        program_net_buy = recent.get('prm_netprps_amt', '0')

                        # [DEBUG] API 응답값 확인
                        logger.debug(f"[프로그램매매 API] {stock_code}: prm_netprps_amt = '{program_net_buy}' (raw)")

                        try:
                            # '+', '-' 부호와 쉼표 제거 후 숫자로 변환
                            program_net_buy_value = int(program_net_buy.replace(',', '').replace('+', '').replace('-', ''))
                            # 부호 처리 (원래 문자열에 '-'가 있으면 음수)
                            if str(program_net_buy).startswith('-'):
                                program_net_buy_value = -program_net_buy_value

                            # ⚠️ API가 "천원" 단위로 반환하므로 1000배
                            program_net_buy_value = program_net_buy_value * 1000
                            logger.debug(f"[프로그램매매 API] {stock_code}: 천원 단위 적용 → {program_net_buy_value:,}원")
                        except (ValueError, AttributeError):
                            program_net_buy_value = 0

                        result = {
                            'program_net_buy': program_net_buy_value,
                            'program_buy': recent.get('prm_buy_amt', 0),
                            'program_sell': recent.get('prm_sell_amt', 0),
                            'date': recent.get('dt', ''),
                            'current_price': recent.get('cur_prc', 0),
                        }

                        logger.info(f"{stock_code} 프로그램순매수: {program_net_buy_value:,}원")
                        return result

                logger.warning(f"프로그램매매 데이터 없음: {stock_code}")
                return None
            else:
                logger.error(f"프로그램매매 조회 실패: {response.get('return_msg')}")
                return None

        except Exception as e:
            logger.error(f"프로그램매매 조회 중 예외 발생: {e}")
            import traceback
            traceback.print_exc()
            return None


# Standalone function for backward compatibility
def get_daily_chart(stock_code: str, period: int = 20, date: str = None) -> List[Dict[str, Any]]:
    """
    일봉 차트 데이터 조회 (standalone function)

    Args:
        stock_code: 종목코드
        period: 조회 기간 (일수)
        date: 기준일 (YYYYMMDD, None이면 최근 거래일)

    Returns:
        일봉 데이터 리스트
    """
    from core.rest_client import KiwoomRESTClient

    # Get client instance
    client = KiwoomRESTClient.get_instance()

    # Create MarketAPI instance
    market_api = MarketAPI(client)

    # Call method
    return market_api.get_daily_chart(stock_code, period, date)


__all__ = ['MarketAPI', 'get_daily_chart']