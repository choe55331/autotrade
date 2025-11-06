"""
api/market/investor_data.py
투자자별 매매 및 트레이딩 데이터 조회 API
"""
import logging
from typing import Dict, Any, List, Optional
from utils.trading_date import get_last_trading_date

logger = logging.getLogger(__name__)


class InvestorDataAPI:
    """
    투자자별 매매 및 트레이딩 데이터 조회 API

    주요 기능:
    - 투자자별 매매 동향
    - 기관매매 추이
    - 증권사별 매매
    - 체결강도
    - 프로그램매매
    등
    """

    def __init__(self, client):
        """
        InvestorDataAPI 초기화

        Args:
            client: KiwoomRESTClient 인스턴스
        """
        self.client = client
        logger.debug("InvestorDataAPI 초기화 완료")

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


__all__ = ['InvestorDataAPI']
