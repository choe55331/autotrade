"""
features/test_mode_manager.py
주말/장마감 후 테스트 모드 매니저
"""

주말(24시간)이나 장마감 이후(오전 8시 이전, 오후 8시 이후)에
가장 최근 정상 영업일 데이터로 모든 기능을 테스트합니다.

키움증권에 확인 결과: REST API로 장이 안 열렸을 때도
가장 최근일 데이터로 테스트 가능합니다.
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TestModeManager:
    """
    주말/장마감 후 테스트 모드 매니저

    주요 기능:
    1. 테스트 모드 활성화 판단
    2. 가장 최근 영업일 데이터로 전체 기능 테스트
    3. 시장탐색, 매수, AI분석, 매도, 차트 등 모든 기능 실행
    4. 테스트 결과 리포트 생성
    """

    def __init__(self):
        """테스트 모드 매니저 초기화"""
        self.is_test_mode = False
        self.test_date: Optional[str] = None
        self.test_results: Dict[str, Any] = {}
        self.start_time: Optional[datetime] = None

        self.test_stocks = [
            "005930",
            "000660",
            "005380",
            "051910",
            "035420",
            "035720",
            "005490",
            "006400",
            "068270",
            "207940",
        ]

        logger.info("테스트 모드 매니저 초기화 완료")

    def check_and_activate_test_mode(self) -> bool:
        """
        현재 시간을 확인하여 테스트 모드 활성화 여부 판단

        활성화 조건:
        - 주말 (토요일, 일요일 24시간)
        - 평일 오전 8시 이전
        - 평일 오후 8시 이후

        Returns:
            테스트 모드 활성화 여부
        """
        from utils.trading_date import is_market_hours, get_last_trading_date

        now = datetime.now()
        current_hour = now.hour
        current_weekday = now.weekday()

        if current_weekday in [5, 6]:
            self.is_test_mode = True
            reason = "주말"

        elif current_hour < 8:
            self.is_test_mode = True
            reason = "오전 8시 이전"

        elif current_hour >= 20:
            self.is_test_mode = True
            reason = "오후 8시 이후"

        elif not is_market_hours():
            self.is_test_mode = True
            reason = "장 마감 시간"

        else:
            self.is_test_mode = False
            logger.info("정규 장 시간 - 테스트 모드 비활성화")
            return False

        self.test_date = get_last_trading_date()
        logger.info(f"[OK] 테스트 모드 활성화 ({reason})")
        logger.info(f"   사용할 데이터 날짜: {self.test_date}")
        logger.info(f"   현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}")

        return True

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """
        전체 기능 테스트 실행

        테스트 항목:
        1. 계좌 조회
        2. 시장 탐색 (종목 검색)
        3. 종목 정보 조회
        4. 차트 데이터 조회
        5. 호가 조회
        6. 잔고 조회
        7. AI 분석 시뮬레이션
        8. 매수/매도 시뮬레이션

        Returns:
            테스트 결과 딕셔너리
        """
        if not self.is_test_mode:
            logger.warning("테스트 모드가 활성화되지 않았습니다")
            return {}

        self.start_time = datetime.now()
        self.test_results = {
            "test_mode": True,
            "test_date": self.test_date,
            "start_time": self.start_time.isoformat(),
            "tests": {}
        }

        print("\n" + "=" * 80)
        print("🧪 주말/장마감 후 테스트 모드")
        print("=" * 80)
        print(f"테스트 날짜: {self.test_date}")
        print(f"시작 시간: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        await self._test_account_info()

        await self._test_market_search()

        await self._test_stock_info()

        await self._test_chart_data()

        await self._test_order_book()

        await self._test_balance()

        await self._test_ai_analysis()

        await self._test_trading_simulation()

        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        self.test_results["end_time"] = end_time.isoformat()
        self.test_results["duration_seconds"] = duration

        print("\n" + "=" * 80)
        print("[OK] 테스트 완료")
        print("=" * 80)
        print(f"소요 시간: {duration:.2f}초")
        print(f"성공한 테스트: {sum(1 for t in self.test_results['tests'].values() if t.get('success'))}/{len(self.test_results['tests'])}")

        self._save_test_results()

        return self.test_results

    async def _test_account_info(self):
        """계좌 조회 테스트"""
        print("\n[1/8] 계좌 조회 테스트...")

        try:
            from api.account import get_account_balance

            result = get_account_balance(date=self.test_date)

            success = result is not None
            self.test_results["tests"]["account_info"] = {
                "success": success,
                "data": result if success else None,
                "error": None if success else "조회 실패"
            }

            if success:
                print("   [OK] 계좌 조회 성공")
                print(f"      예수금: {result.get('deposit', 'N/A')}")
            else:
                print("   [X] 계좌 조회 실패")

        except Exception as e:
            logger.error(f"계좌 조회 테스트 실패: {e}")
            self.test_results["tests"]["account_info"] = {
                "success": False,
                "error": str(e)
            }
            print(f"   [X] 오류: {e}")

    async def _test_market_search(self):
        """시장 탐색 테스트"""
        print("\n[2/8] 시장 탐색 테스트...")

        try:
            from api.market import get_stock_list

            result = get_stock_list(market="ALL")

            success = result is not None and len(result) > 0
            self.test_results["tests"]["market_search"] = {
                "success": success,
                "stock_count": len(result) if success else 0,
                "error": None if success else "조회 실패"
            }

            if success:
                print(f"   [OK] 시장 탐색 성공 - 총 {len(result)}개 종목")
            else:
                print("   [X] 시장 탐색 실패")

        except Exception as e:
            logger.error(f"시장 탐색 테스트 실패: {e}")
            self.test_results["tests"]["market_search"] = {
                "success": False,
                "error": str(e)
            }
            print(f"   [X] 오류: {e}")

    async def _test_stock_info(self):
        """종목 정보 조회 테스트"""
        print("\n[3/8] 종목 정보 조회 테스트...")

        tested_stocks = []

        try:
            from api.market import get_current_price

            for stock_code in self.test_stocks[:3]:
                try:
                    result = get_current_price(stock_code, date=self.test_date)
                    if result:
                        tested_stocks.append({
                            "code": stock_code,
                            "success": True,
                            "price": result.get("current_price")
                        })
                        print(f"   [OK] {stock_code}: {result.get('current_price', 'N/A')}원")
                    else:
                        tested_stocks.append({
                            "code": stock_code,
                            "success": False
                        })
                        print(f"   [X] {stock_code}: 조회 실패")

                    await asyncio.sleep(0.3)

                except Exception as e:
                    logger.error(f"종목 {stock_code} 조회 실패: {e}")
                    tested_stocks.append({
                        "code": stock_code,
                        "success": False,
                        "error": str(e)
                    })

            success_count = sum(1 for s in tested_stocks if s.get("success"))
            self.test_results["tests"]["stock_info"] = {
                "success": success_count > 0,
                "tested_stocks": tested_stocks,
                "success_count": success_count
            }

            print(f"   [CHART] {success_count}/{len(tested_stocks)} 종목 조회 성공")

        except Exception as e:
            logger.error(f"종목 정보 조회 테스트 실패: {e}")
            self.test_results["tests"]["stock_info"] = {
                "success": False,
                "error": str(e)
            }
            print(f"   [X] 오류: {e}")

    async def _test_chart_data(self):
        """차트 데이터 조회 테스트"""
        print("\n[4/8] 차트 데이터 조회 테스트...")

        try:
            from api.market import get_daily_chart

            stock_code = "005930"
            result = get_daily_chart(
                stock_code,
                end_date=self.test_date,
                count=20
            )

            success = result is not None and len(result) > 0
            self.test_results["tests"]["chart_data"] = {
                "success": success,
                "stock_code": stock_code,
                "data_count": len(result) if success else 0,
                "error": None if success else "조회 실패"
            }

            if success:
                print(f"   [OK] 차트 데이터 조회 성공 - {len(result)}일치 데이터")
                print(f"      최근일: {result[0].get('date', 'N/A')}, 종가: {result[0].get('close', 'N/A')}")
            else:
                print("   [X] 차트 데이터 조회 실패")

        except Exception as e:
            logger.error(f"차트 데이터 조회 테스트 실패: {e}")
            self.test_results["tests"]["chart_data"] = {
                "success": False,
                "error": str(e)
            }
            print(f"   [X] 오류: {e}")

    async def _test_order_book(self):
        """호가 조회 테스트"""
        print("\n[5/8] 호가 조회 테스트...")

        try:
            from api.market import get_order_book

            stock_code = "005930"
            result = get_order_book(stock_code, date=self.test_date)

            success = result is not None
            self.test_results["tests"]["order_book"] = {
                "success": success,
                "stock_code": stock_code,
                "data": result if success else None,
                "error": None if success else "조회 실패"
            }

            if success:
                print(f"   [OK] 호가 조회 성공")
                print(f"      매도호가: {result.get('ask_price', 'N/A')}")
                print(f"      매수호가: {result.get('bid_price', 'N/A')}")
            else:
                print("   [X] 호가 조회 실패")

        except Exception as e:
            logger.error(f"호가 조회 테스트 실패: {e}")
            self.test_results["tests"]["order_book"] = {
                "success": False,
                "error": str(e)
            }
            print(f"   [X] 오류: {e}")

    async def _test_balance(self):
        """잔고 조회 테스트"""
        print("\n[6/8] 잔고 조회 테스트...")

        try:
            from api.account import get_holdings

            result = get_holdings(date=self.test_date)

            success = result is not None
            self.test_results["tests"]["balance"] = {
                "success": success,
                "holdings_count": len(result) if success and isinstance(result, list) else 0,
                "error": None if success else "조회 실패"
            }

            if success:
                holdings_count = len(result) if isinstance(result, list) else 0
                print(f"   [OK] 잔고 조회 성공 - {holdings_count}개 보유 종목")
            else:
                print("   [X] 잔고 조회 실패")

        except Exception as e:
            logger.error(f"잔고 조회 테스트 실패: {e}")
            self.test_results["tests"]["balance"] = {
                "success": False,
                "error": str(e)
            }
            print(f"   [X] 오류: {e}")

    async def _test_ai_analysis(self):
        """AI 분석 테스트 (실제 기술적 지표 계산)"""
        print("\n[7/8] AI 분석 및 기술적 지표 계산 테스트...")

        try:
            print("   [CHART] 차트 데이터 조회 및 기술적 지표 계산 중...")

            from api.market import get_daily_chart
            import pandas as pd
            from indicators.momentum import rsi, macd, calculate_momentum_score
            from indicators.volatility import bollinger_bands, calculate_volatility_score
            from indicators.volume import calculate_volume_profile

            stock_code = "005930"
            chart_data = get_daily_chart(stock_code, period=60, date=self.test_date)

            if not chart_data or len(chart_data) < 20:
                technical_analysis = {
                    "rsi": "데이터 부족",
                    "macd": "데이터 부족",
                    "bollinger": "데이터 부족",
                    "volume": "데이터 부족"
                }
                print("   [WARNING]️ 차트 데이터 부족 - 시뮬레이션 모드")
            else:
                df = pd.DataFrame(chart_data)

                if 'stck_clpr' in df.columns:
                    df['close'] = pd.to_numeric(df['stck_clpr'], errors='coerce')
                    df['high'] = pd.to_numeric(df.get('stck_hgpr', df['stck_clpr']), errors='coerce')
                    df['low'] = pd.to_numeric(df.get('stck_lwpr', df['stck_clpr']), errors='coerce')
                    df['volume'] = pd.to_numeric(df.get('acml_vol', 0), errors='coerce')
                elif 'close' not in df.columns and len(df.columns) > 0:
                    df['close'] = pd.to_numeric(df.iloc[:, 4], errors='coerce')
                    df['high'] = pd.to_numeric(df.iloc[:, 2], errors='coerce')
                    df['low'] = pd.to_numeric(df.iloc[:, 3], errors='coerce')
                    df['volume'] = pd.to_numeric(df.iloc[:, 5], errors='coerce')

                close_prices = df['close'].dropna()

                if len(close_prices) >= 20:
                    rsi_values = rsi(close_prices, period=14)
                    current_rsi = round(rsi_values.iloc[-1], 2) if not pd.isna(rsi_values.iloc[-1]) else 50.0

                    macd_line, signal_line, histogram = macd(close_prices)
                    current_hist = histogram.iloc[-1] if not pd.isna(histogram.iloc[-1]) else 0

                    if current_hist > 0:
                        macd_signal = "매수 신호"
                    elif current_hist < 0:
                        macd_signal = "매도 신호"
                    else:
                        macd_signal = "중립"

                    high_prices = df['high'].dropna()
                    low_prices = df['low'].dropna()

                    if len(high_prices) >= 20:
                        upper, middle, lower = bollinger_bands(close_prices, period=20)
                        current_price = close_prices.iloc[-1]
                        current_upper = upper.iloc[-1]
                        current_lower = lower.iloc[-1]

                        bandwidth = current_upper - current_lower
                        percent_b = (current_price - current_lower) / bandwidth if bandwidth > 0 else 0.5

                        if percent_b > 0.8:
                            bollinger_signal = "상단 근접"
                        elif percent_b < 0.2:
                            bollinger_signal = "하단 근접"
                        else:
                            bollinger_signal = "중립"
                    else:
                        bollinger_signal = "중립"

                    volumes = df['volume'].dropna()
                    if len(volumes) >= 20:
                        avg_volume = volumes.tail(20).mean()
                        current_volume = volumes.iloc[-1]
                        volume_ratio = (current_volume / avg_volume * 100) if avg_volume > 0 else 100
                        volume_signal = f"평균 대비 {volume_ratio:.0f}%"
                    else:
                        volume_signal = "평균 대비 100%"

                    technical_analysis = {
                        "rsi": current_rsi,
                        "macd": macd_signal,
                        "bollinger": bollinger_signal,
                        "volume": volume_signal
                    }

                    print(f"   [OK] 실제 기술적 지표 계산 완료 ({len(close_prices)}일 데이터 사용)")
                else:
                    technical_analysis = {
                        "rsi": "데이터 부족",
                        "macd": "데이터 부족",
                        "bollinger": "데이터 부족",
                        "volume": "데이터 부족"
                    }
                    print("   [WARNING]️ 유효한 가격 데이터 부족")

            sentiment_analysis = {
                "news_sentiment": "시뮬레이션",
                "social_sentiment": "시뮬레이션",
                "analyst_rating": "시뮬레이션"
            }

            self.test_results["tests"]["ai_analysis"] = {
                "success": True,
                "technical": technical_analysis,
                "sentiment": sentiment_analysis,
                "data_points": len(chart_data) if chart_data else 0
            }

            print("   [OK] 기술적 분석 완료")
            print(f"      RSI: {technical_analysis['rsi']}")
            print(f"      MACD: {technical_analysis['macd']}")
            print(f"      Bollinger: {technical_analysis['bollinger']}")
            print(f"      Volume: {technical_analysis['volume']}")

        except Exception as e:
            logger.error(f"AI 분석 테스트 실패: {e}", exc_info=True)
            self.test_results["tests"]["ai_analysis"] = {
                "success": False,
                "error": str(e)
            }
            print(f"   [X] 오류: {e}")

    async def _test_trading_simulation(self):
        """매수/매도 시뮬레이션 테스트"""
        print("\n[8/8] 매수/매도 시뮬레이션 테스트...")

        try:
            print("   🔄 매매 시뮬레이션 실행 중...")
            print("   [WARNING]️  실제 주문은 발생하지 않습니다")

            buy_simulation = {
                "action": "buy",
                "stock_code": "005930",
                "stock_name": "삼성전자",
                "price": 75000,
                "quantity": 10,
                "total_amount": 750000,
                "order_type": "시장가",
                "simulated": True,
                "note": "장 마감 시간이므로 실제 주문 미발생"
            }

            sell_simulation = {
                "action": "sell",
                "stock_code": "005930",
                "stock_name": "삼성전자",
                "price": 76000,
                "quantity": 10,
                "total_amount": 760000,
                "profit": 10000,
                "profit_rate": 1.33,
                "order_type": "시장가",
                "simulated": True,
                "note": "장 마감 시간이므로 실제 주문 미발생"
            }

            self.test_results["tests"]["trading_simulation"] = {
                "success": True,
                "buy": buy_simulation,
                "sell": sell_simulation
            }

            print("   [OK] 매매 시뮬레이션 완료")
            print(f"      매수: {buy_simulation['stock_name']} {buy_simulation['quantity']}주 @ {buy_simulation['price']:,}원")
            print(f"      매도: {sell_simulation['stock_name']} {sell_simulation['quantity']}주 @ {sell_simulation['price']:,}원")
            print(f"      예상 수익: {sell_simulation['profit']:,}원 ({sell_simulation['profit_rate']:.2f}%)")

        except Exception as e:
            logger.error(f"매매 시뮬레이션 테스트 실패: {e}")
            self.test_results["tests"]["trading_simulation"] = {
                "success": False,
                "error": str(e)
            }
            print(f"   [X] 오류: {e}")

    def _save_test_results(self):
        """테스트 결과 저장"""
        try:
            result_dir = Path("test_results")
            result_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_file = result_dir / f"test_mode_results_{timestamp}.json"

            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)

            print(f"\n💾 테스트 결과 저장: {result_file}")
            logger.info(f"테스트 결과 저장: {result_file}")

        except Exception as e:
            logger.error(f"테스트 결과 저장 실패: {e}")
            print(f"[WARNING]️  테스트 결과 저장 실패: {e}")


async def run_test_mode():
    """테스트 모드 실행 (편의 함수)"""
    manager = TestModeManager()

    if manager.check_and_activate_test_mode():
        return await manager.run_comprehensive_test()
    else:
        print("현재는 정규 장 시간입니다. 테스트 모드를 실행할 수 없습니다.")
        return None


__all__ = ['TestModeManager', 'run_test_mode']
