"""
대시보드 이슈 테스트 파일
3가지 문제를 다양한 접근법으로 테스트
"""

1. 계좌 잔고 계산 (인출가능액 -> 실제 사용가능액)
2. NXT 시장가격 조회
3. AI 스캐닝 종목 연동

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from typing import Dict, Any, List, Optional
from datetime import datetime
import traceback



class AccountBalanceCalculator:
    """계좌 잔고 계산 - 여러 접근법 테스트"""

    @staticmethod
    def approach_1_deposit_minus_holdings(deposit: Dict, holdings: List[Dict]) -> Dict[str, Any]:
        """
        접근법 1: 예수금 - (보유주식 구매가 * 수량)

        가장 정확한 방법:
        - 예수금(dps_amt)에서 시작
        - 보유주식의 구매원가(pchs_amt)를 차감
        """
        try:
            deposit_amount = int(deposit.get('dps_amt', 0))

            total_purchase_amount = sum(int(h.get('pchs_amt', 0)) for h in holdings)

            available_cash = deposit_amount - total_purchase_amount

            stock_value = sum(int(h.get('eval_amt', 0)) for h in holdings)

            total_assets = deposit_amount + stock_value

            return {
                'method': 'approach_1_deposit_minus_holdings',
                'deposit_amount': deposit_amount,
                'total_purchase_amount': total_purchase_amount,
                'available_cash': available_cash,
                'stock_value': stock_value,
                'total_assets': total_assets,
                'success': True,
                'error': None
            }
        except Exception as e:
            return {
                'method': 'approach_1_deposit_minus_holdings',
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    @staticmethod
    def approach_2_orderable_amount_direct(deposit: Dict, holdings: List[Dict]) -> Dict[str, Any]:
        """
        접근법 2: 주문가능금액(ord_alow_amt) 직접 사용

        키움증권 API가 제공하는 주문가능금액을 그대로 사용
        - 장점: 간단하고 API가 계산해줌
        - 단점: 실제 예수금이 아닐 수 있음
        """
        try:
            orderable_amount = int(deposit.get('ord_alow_amt', 0))

            stock_value = sum(int(h.get('eval_amt', 0)) for h in holdings)

            total_assets = orderable_amount + stock_value

            return {
                'method': 'approach_2_orderable_amount_direct',
                'orderable_amount': orderable_amount,
                'available_cash': orderable_amount,
                'stock_value': stock_value,
                'total_assets': total_assets,
                'success': True,
                'error': None
            }
        except Exception as e:
            return {
                'method': 'approach_2_orderable_amount_direct',
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    @staticmethod
    def approach_3_evaluation_based(account_eval: Dict, holdings: List[Dict]) -> Dict[str, Any]:
        """
        접근법 3: 계좌평가현황(kt00004) 기반

        계좌평가현황 API의 데이터 직접 사용
        - eval_amt: 평가금액
        - pchs_amt: 매입금액
        """
        try:
            deposit_amount = int(account_eval.get('dps_amt', 0))
            total_eval = int(account_eval.get('tot_eval_amt', 0))
            total_purchase = int(account_eval.get('tot_pchs_amt', 0))

            available_cash = deposit_amount - total_purchase

            stock_value = sum(int(h.get('eval_amt', 0)) for h in holdings)

            return {
                'method': 'approach_3_evaluation_based',
                'deposit_amount': deposit_amount,
                'total_eval': total_eval,
                'total_purchase': total_purchase,
                'available_cash': available_cash,
                'stock_value': stock_value,
                'total_assets': total_eval,
                'success': True,
                'error': None
            }
        except Exception as e:
            return {
                'method': 'approach_3_evaluation_based',
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    @staticmethod
    def approach_4_manual_calculation(deposit: Dict, holdings: List[Dict]) -> Dict[str, Any]:
        """
        접근법 4: 수동 계산 (모든 필드 고려)

        가능한 모든 필드를 확인하고 계산
        """
        try:
            result = {
                'method': 'approach_4_manual_calculation',
                'deposit_fields': {},
                'holdings_summary': [],
                'calculations': {}
            }

            deposit_fields = {
                'dps_amt': int(deposit.get('dps_amt', 0)),
                'ord_alow_amt': int(deposit.get('ord_alow_amt', 0)),
                'wthdr_alow_amt': int(deposit.get('wthdr_alow_amt', 0)),
                'tot_aset_amt': int(deposit.get('tot_aset_amt', 0)),
            }
            result['deposit_fields'] = deposit_fields

            for h in holdings:
                holding_info = {
                    'code': h.get('pdno', h.get('stk_cd', '')),
                    'name': h.get('prdt_name', h.get('stk_nm', '')),
                    'quantity': int(h.get('hldg_qty', h.get('rmnd_qty', 0))),
                    'avg_price': int(h.get('pchs_avg_pric', h.get('avg_prc', 0))),
                    'current_price': int(h.get('prpr', h.get('cur_prc', 0))),
                    'eval_amt': int(h.get('eval_amt', 0)),
                    'pchs_amt': int(h.get('pchs_amt', 0))
                }
                result['holdings_summary'].append(holding_info)

            total_pchs = sum(h.get('eval_amt', 0) for h in result['holdings_summary'])
            total_eval = sum(h.get('pchs_amt', 0) for h in result['holdings_summary'])

            result['calculations'] = {
                'method_1_dps_minus_pchs': deposit_fields['dps_amt'] - total_eval,
                'method_2_ord_alow': deposit_fields['ord_alow_amt'],
                'method_3_wthdr_alow': deposit_fields['wthdr_alow_amt'],
                'total_stock_value': total_pchs,
                'total_purchase_cost': total_eval,
            }

            result['success'] = True
            result['error'] = None
            return result

        except Exception as e:
            return {
                'method': 'approach_4_manual_calculation',
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }



class NXTPriceChecker:
    """NXT 시장가격 조회 - 여러 접근법 테스트"""

    def __init__(self, market_api=None):
        self.market_api = market_api

    def approach_1_direct_stock_price(self, stock_code: str) -> Dict[str, Any]:
        """
        접근법 1: get_stock_price() 직접 호출

        ka10003 (종목체결정보) 사용
        - 장 시간, NXT 시간 모두 조회 가능해야 함
        """
        try:
            if not self.market_api:
                return {'method': 'approach_1', 'success': False, 'error': 'market_api not available'}

            result = self.market_api.get_stock_price(stock_code)

            return {
                'method': 'approach_1_direct_stock_price',
                'stock_code': stock_code,
                'result': result,
                'current_price': result.get('current_price', 0) if result else 0,
                'success': result is not None,
                'error': None if result else 'get_stock_price returned None'
            }
        except Exception as e:
            return {
                'method': 'approach_1_direct_stock_price',
                'stock_code': stock_code,
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def approach_2_nxt_specific_api(self, stock_code: str) -> Dict[str, Any]:
        """
        접근법 2: NXT 전용 API 사용

        시간외 거래 전용 API가 있다면 사용
        """
        try:
            if not self.market_api:
                return {'method': 'approach_2', 'success': False, 'error': 'market_api not available'}


            if hasattr(self.market_api, 'client'):
                result = self.market_api.client.request(
                    api_id="ka10003",
                    body={"stk_cd": stock_code},
                    path="stkinfo"
                )

                return {
                    'method': 'approach_2_nxt_specific_api',
                    'stock_code': stock_code,
                    'result': result,
                    'success': result is not None and result.get('return_code') == 0,
                    'error': result.get('return_msg') if result else 'API call failed'
                }

            return {
                'method': 'approach_2_nxt_specific_api',
                'success': False,
                'error': 'client not available'
            }

        except Exception as e:
            return {
                'method': 'approach_2_nxt_specific_api',
                'stock_code': stock_code,
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def approach_3_holdings_current_price(self, stock_code: str, account_api=None) -> Dict[str, Any]:
        """
        접근법 3: 보유종목에서 현재가 추출

        계좌평가현황의 prpr (현재가) 필드 사용
        - NXT 시간에도 업데이트될 가능성 있음
        """
        try:
            if not account_api:
                return {'method': 'approach_3', 'success': False, 'error': 'account_api not available'}

            holdings = account_api.get_holdings(market_type="KRX")

            for h in holdings:
                if h.get('pdno') == stock_code or h.get('stk_cd') == stock_code:
                    current_price = int(h.get('prpr', h.get('cur_prc', 0)))

                    return {
                        'method': 'approach_3_holdings_current_price',
                        'stock_code': stock_code,
                        'current_price': current_price,
                        'holding_data': h,
                        'success': True,
                        'error': None
                    }

            return {
                'method': 'approach_3_holdings_current_price',
                'stock_code': stock_code,
                'success': False,
                'error': 'Stock not in holdings'
            }

        except Exception as e:
            return {
                'method': 'approach_3_holdings_current_price',
                'stock_code': stock_code,
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def approach_4_time_aware_price(self, stock_code: str) -> Dict[str, Any]:
        """
        접근법 4: 시간대별 가격 조회 전략

        현재 시간을 확인하고 적절한 API 사용
        - "09":"00"-15:30: 정규시장 현재가
        - 16:"00"-18:"00": NXT 시장가
        - 기타: 전일 종가
        """
        try:
            from datetime import datetime, time

            now = datetime.now()
            current_time = now.time()

            market_open = time(9, 0)
            market_close = time(15, 30)
            nxt_start = time(16, 0)
            nxt_end = time(18, 0)

            is_regular_market = market_open <= current_time <= market_close
            is_nxt_market = nxt_start <= current_time <= nxt_end

            price_source = 'unknown'
            current_price = 0

            if is_regular_market:
                price_source = 'regular_market'
                if self.market_api:
                    result = self.market_api.get_stock_price(stock_code)
                    if result:
                        current_price = result.get('current_price', 0)

            elif is_nxt_market:
                price_source = 'nxt_market'
                if self.market_api:
                    result = self.market_api.get_stock_price(stock_code)
                    if result:
                        current_price = result.get('current_price', 0)
            else:
                price_source = 'after_hours'
                if self.market_api and hasattr(self.market_api, 'get_daily_price'):
                    daily_data = self.market_api.get_daily_price(stock_code, days=1)
                    if daily_data and len(daily_data) > 0:
                        current_price = daily_data[0].get('close', 0)

            return {
                'method': 'approach_4_time_aware_price',
                'stock_code': stock_code,
                'current_time': now.strftime('%H:%M:%S'),
                'is_regular_market': is_regular_market,
                'is_nxt_market': is_nxt_market,
                'price_source': price_source,
                'current_price': current_price,
                'success': current_price > 0,
                'error': None if current_price > 0 else 'Could not get price'
            }

        except Exception as e:
            return {
                'method': 'approach_4_time_aware_price',
                'stock_code': stock_code,
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }



class AIScanningIntegrator:
    """AI 스캐닝 종목 연동 - 여러 접근법 테스트"""

    def __init__(self, bot_instance=None):
        self.bot_instance = bot_instance

    def approach_1_scanner_pipeline_direct(self) -> Dict[str, Any]:
        """
        접근법 1: scanner_pipeline에서 직접 가져오기

        ScannerPipeline 객체의 결과 직접 접근
        """
        try:
            if not self.bot_instance:
                return {'method': 'approach_1', 'success': False, 'error': 'bot_instance not available'}

            if not hasattr(self.bot_instance, 'scanner_pipeline'):
                return {'method': 'approach_1', 'success': False, 'error': 'scanner_pipeline not found'}

            pipeline = self.bot_instance.scanner_pipeline

            fast_count = len(pipeline.fast_scan_results) if hasattr(pipeline, 'fast_scan_results') else 0
            deep_count = len(pipeline.deep_scan_results) if hasattr(pipeline, 'deep_scan_results') else 0
            ai_count = len(pipeline.ai_scan_results) if hasattr(pipeline, 'ai_scan_results') else 0

            fast_stocks = [
                {
                    'code': s.code,
                    'name': s.name,
                    'price': s.price,
                    'fast_score': s.fast_scan_score
                }
                for s in pipeline.fast_scan_results[:5]
            ] if hasattr(pipeline, 'fast_scan_results') else []

            deep_stocks = [
                {
                    'code': s.code,
                    'name': s.name,
                    'price': s.price,
                    'deep_score': s.deep_scan_score
                }
                for s in pipeline.deep_scan_results[:5]
            ] if hasattr(pipeline, 'deep_scan_results') else []

            ai_stocks = [
                {
                    'code': s.code,
                    'name': s.name,
                    'price': s.price,
                    'ai_score': s.ai_score,
                    'ai_signal': s.ai_signal
                }
                for s in pipeline.ai_scan_results[:5]
            ] if hasattr(pipeline, 'ai_scan_results') else []

            return {
                'method': 'approach_1_scanner_pipeline_direct',
                'fast_scan_count': fast_count,
                'deep_scan_count': deep_count,
                'ai_scan_count': ai_count,
                'fast_scan_stocks': fast_stocks,
                'deep_scan_stocks': deep_stocks,
                'ai_scan_stocks': ai_stocks,
                'success': True,
                'error': None
            }

        except Exception as e:
            return {
                'method': 'approach_1_scanner_pipeline_direct',
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def approach_2_scan_progress_attribute(self) -> Dict[str, Any]:
        """
        접근법 2: bot_instance.scan_progress 속성 사용

        현재 대시보드에서 사용 중인 방법
        """
        try:
            if not self.bot_instance:
                return {'method': 'approach_2', 'success': False, 'error': 'bot_instance not available'}

            if not hasattr(self.bot_instance, 'scan_progress'):
                return {'method': 'approach_2', 'success': False, 'error': 'scan_progress not found'}

            scan_progress = self.bot_instance.scan_progress

            total_candidates = len(scan_progress.get('top_candidates', []))
            ai_reviewed = len(scan_progress.get('approved', [])) + len(scan_progress.get('rejected', []))
            pending = len(scan_progress.get('approved', []))

            return {
                'method': 'approach_2_scan_progress_attribute',
                'total_candidates': total_candidates,
                'ai_reviewed': ai_reviewed,
                'pending': pending,
                'top_candidates': scan_progress.get('top_candidates', [])[:5],
                'approved': scan_progress.get('approved', [])[:5],
                'rejected': scan_progress.get('rejected', [])[:5],
                'success': True,
                'error': None
            }

        except Exception as e:
            return {
                'method': 'approach_2_scan_progress_attribute',
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def approach_3_combined_sources(self) -> Dict[str, Any]:
        """
        접근법 3: scanner_pipeline + scan_progress 결합

        두 소스를 모두 확인하고 최신 데이터 사용
        """
        try:
            if not self.bot_instance:
                return {'method': 'approach_3', 'success': False, 'error': 'bot_instance not available'}

            result = {
                'method': 'approach_3_combined_sources',
                'sources': {}
            }

            if hasattr(self.bot_instance, 'scanner_pipeline'):
                pipeline = self.bot_instance.scanner_pipeline
                result['sources']['scanner_pipeline'] = {
                    'fast_count': len(pipeline.fast_scan_results) if hasattr(pipeline, 'fast_scan_results') else 0,
                    'deep_count': len(pipeline.deep_scan_results) if hasattr(pipeline, 'deep_scan_results') else 0,
                    'ai_count': len(pipeline.ai_scan_results) if hasattr(pipeline, 'ai_scan_results') else 0,
                    'available': True
                }
            else:
                result['sources']['scanner_pipeline'] = {'available': False}

            if hasattr(self.bot_instance, 'scan_progress'):
                scan_progress = self.bot_instance.scan_progress
                result['sources']['scan_progress'] = {
                    'top_candidates': len(scan_progress.get('top_candidates', [])),
                    'approved': len(scan_progress.get('approved', [])),
                    'rejected': len(scan_progress.get('rejected', [])),
                    'available': True
                }
            else:
                result['sources']['scan_progress'] = {'available': False}

            if result['sources']['scanner_pipeline'].get('available'):
                pipeline_data = result['sources']['scanner_pipeline']
                result['final_counts'] = {
                    'scanning_stocks': pipeline_data['fast_count'],
                    'ai_analyzed': pipeline_data['deep_count'],
                    'buy_pending': pipeline_data['ai_count']
                }
            elif result['sources']['scan_progress'].get('available'):
                progress_data = result['sources']['scan_progress']
                result['final_counts'] = {
                    'scanning_stocks': progress_data['top_candidates'],
                    'ai_analyzed': progress_data['approved'] + progress_data['rejected'],
                    'buy_pending': progress_data['approved']
                }
            else:
                result['final_counts'] = {
                    'scanning_stocks': 0,
                    'ai_analyzed': 0,
                    'buy_pending': 0
                }

            result['success'] = True
            result['error'] = None
            return result

        except Exception as e:
            return {
                'method': 'approach_3_combined_sources',
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def approach_4_realtime_scan_trigger(self) -> Dict[str, Any]:
        """
        접근법 4: 실시간 스캔 트리거

        스캔 파이프라인을 강제 실행하고 결과 가져오기
        """
        try:
            if not self.bot_instance:
                return {'method': 'approach_4', 'success': False, 'error': 'bot_instance not available'}

            if not hasattr(self.bot_instance, 'scanner_pipeline'):
                return {'method': 'approach_4', 'success': False, 'error': 'scanner_pipeline not found'}

            pipeline = self.bot_instance.scanner_pipeline

            print("[SEARCH] 강제 Fast Scan 실행...")
            fast_results = pipeline.run_fast_scan()

            print("[SEARCH] 강제 Deep Scan 실행...")
            deep_results = pipeline.run_deep_scan(fast_results[:20])


            return {
                'method': 'approach_4_realtime_scan_trigger',
                'fast_scan_count': len(fast_results),
                'deep_scan_count': len(deep_results),
                'fast_scan_stocks': [
                    {
                        'code': s.code,
                        'name': s.name,
                        'price': s.price,
                        'fast_score': s.fast_scan_score
                    }
                    for s in fast_results[:5]
                ],
                'deep_scan_stocks': [
                    {
                        'code': s.code,
                        'name': s.name,
                        'price': s.price,
                        'deep_score': s.deep_scan_score
                    }
                    for s in deep_results[:5]
                ],
                'success': True,
                'error': None
            }

        except Exception as e:
            return {
                'method': 'approach_4_realtime_scan_trigger',
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }



def run_all_tests(bot_instance=None, market_api=None, account_api=None):
    """모든 테스트 실행"""

    print("=" * 80)
    print("대시보드 이슈 테스트 시작")
    print("=" * 80)
    print()

    results = {
        'account_balance': [],
        'nxt_price': [],
        'ai_scanning': []
    }

    print("\n" + "=" * 80)
    print("테스트 1: 계좌 잔고 계산 (4가지 접근법)")
    print("=" * 80)

    if account_api:
        try:
            deposit = account_api.get_deposit()
            holdings = account_api.get_holdings()
            account_eval = account_api.get_account_evaluation()

            if deposit and holdings is not None:
                calc = AccountBalanceCalculator()

                print("\n[접근법 1] 예수금 - 보유주식 구매원가")
                print("-" * 80)
                result1 = calc.approach_1_deposit_minus_holdings(deposit, holdings)
                results['account_balance'].append(result1)
                print_result(result1)

                print("\n[접근법 2] 주문가능금액 직접 사용")
                print("-" * 80)
                result2 = calc.approach_2_orderable_amount_direct(deposit, holdings)
                results['account_balance'].append(result2)
                print_result(result2)

                if account_eval:
                    print("\n[접근법 3] 계좌평가현황 기반")
                    print("-" * 80)
                    result3 = calc.approach_3_evaluation_based(account_eval, holdings)
                    results['account_balance'].append(result3)
                    print_result(result3)

                print("\n[접근법 4] 수동 계산 (모든 필드)")
                print("-" * 80)
                result4 = calc.approach_4_manual_calculation(deposit, holdings)
                results['account_balance'].append(result4)
                print_result(result4)

            else:
                print("[WARNING]️  deposit 또는 holdings 조회 실패")

        except Exception as e:
            print(f"[X] 계좌 잔고 테스트 실패: {e}")
            traceback.print_exc()
    else:
        print("[WARNING]️  account_api not available")

    print("\n" + "=" * 80)
    print("테스트 2: NXT 시장가격 조회 (4가지 접근법)")
    print("=" * 80)

    test_stocks = ['005930', '000660']

    if market_api or account_api:
        checker = NXTPriceChecker(market_api)

        for stock_code in test_stocks:
            print(f"\n종목: {stock_code}")
            print("-" * 80)

            print("\n[접근법 1] get_stock_price() 직접 호출")
            result1 = checker.approach_1_direct_stock_price(stock_code)
            results['nxt_price'].append(result1)
            print_result(result1)

            print("\n[접근법 2] NXT 전용 API")
            result2 = checker.approach_2_nxt_specific_api(stock_code)
            results['nxt_price'].append(result2)
            print_result(result2)

            print("\n[접근법 3] 보유종목에서 현재가 추출")
            result3 = checker.approach_3_holdings_current_price(stock_code, account_api)
            results['nxt_price'].append(result3)
            print_result(result3)

            print("\n[접근법 4] 시간대별 가격 조회 전략")
            result4 = checker.approach_4_time_aware_price(stock_code)
            results['nxt_price'].append(result4)
            print_result(result4)
    else:
        print("[WARNING]️  market_api and account_api not available")

    print("\n" + "=" * 80)
    print("테스트 3: AI 스캐닝 종목 연동 (4가지 접근법)")
    print("=" * 80)

    if bot_instance:
        integrator = AIScanningIntegrator(bot_instance)

        print("\n[접근법 1] scanner_pipeline 직접 접근")
        print("-" * 80)
        result1 = integrator.approach_1_scanner_pipeline_direct()
        results['ai_scanning'].append(result1)
        print_result(result1)

        print("\n[접근법 2] scan_progress 속성 사용")
        print("-" * 80)
        result2 = integrator.approach_2_scan_progress_attribute()
        results['ai_scanning'].append(result2)
        print_result(result2)

        print("\n[접근법 3] scanner_pipeline + scan_progress 결합")
        print("-" * 80)
        result3 = integrator.approach_3_combined_sources()
        results['ai_scanning'].append(result3)
        print_result(result3)


    else:
        print("[WARNING]️  bot_instance not available")

    print("\n" + "=" * 80)
    print("테스트 결과 요약")
    print("=" * 80)

    print("\n[계좌 잔고 계산]")
    for r in results['account_balance']:
        status = "[OK] 성공" if r.get('success') else "[X] 실패"
        print(f"  {status}: {r.get('method')}")

    print("\n[NXT 시장가격 조회]")
    for r in results['nxt_price']:
        status = "[OK] 성공" if r.get('success') else "[X] 실패"
        print(f"  {status}: {r.get('method')}")

    print("\n[AI 스캐닝 연동]")
    for r in results['ai_scanning']:
        status = "[OK] 성공" if r.get('success') else "[X] 실패"
        print(f"  {status}: {r.get('method')}")

    print("\n" + "=" * 80)
    print("테스트 완료")
    print("=" * 80)

    return results


def print_result(result: Dict[str, Any]):
    """결과 출력"""
    import json

    if result.get('success'):
        print("[OK] 성공")
        display_result = {k: v for k, v in result.items() if k not in ['traceback', 'error']}
        print(json.dumps(display_result, indent=2, ensure_ascii=False))
    else:
        print("[X] 실패")
        print(f"Error: {result.get('error')}")
        if result.get('traceback'):
            print(f"\nTraceback:\n{result.get('traceback')}")



if __name__ == "__main__":
    print("대시보드 이슈 테스트")
    print()
    print("이 스크립트는 다음 3가지 문제를 다양한 방법으로 테스트합니다:")
    print("1. 계좌 잔고 계산 (인출가능액 -> 실제 사용가능액)")
    print("2. NXT 시장가격 조회")
    print("3. AI 스캐닝 종목 연동")
    print()
    print("사용법:")
    print("  from tests.manual_tests.test_dashboard_issues import run_all_tests")
    print("  results = run_all_tests(bot_instance, market_api, account_api)")
    print()
    print("또는:")
    print("
    print("  from tests.manual_tests.test_dashboard_issues import run_all_tests")
    print("  run_all_tests(bot, bot.market_api, bot.account_api)")
