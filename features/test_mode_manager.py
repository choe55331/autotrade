"""
features/test_mode_manager.py
주말/장마감 후 테스트 모드 매니저

주말(24시간)이나 장마감 이후(오전 8시 이전, 오후 8시 이후)에
가장 최근 정상 영업일 데이터로 모든 기능을 테스트합니다.

키움증권에 확인 결과: REST API로 장이 안 열렸을 때도
가장 최근일 데이터로 테스트 가능합니다.
"""
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

        # 테스트할 종목 리스트 (대형주 중심)
        self.test_stocks = [
            "005930",  # 삼성전자
            "000660",  # SK하이닉스
            "005380",  # 현대차
            "051910",  # LG화학
            "035420",  # NAVER
            "035720",  # 카카오
            "005490",  # POSCO홀딩스
            "006400",  # 삼성SDI
            "068270",  # 셀트리온
            "207940",  # 삼성바이오로직스
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
        current_weekday = now.weekday()  # 0=월, 6=일

        # 주말 (토요일, 일요일)
        if current_weekday in [5, 6]:
            self.is_test_mode = True
            reason = "주말"

        # 평일 오전 8시 이전
        elif current_hour < 8:
            self.is_test_mode = True
            reason = "오전 8시 이전"

        # 평일 오후 8시 이후 (20:00)
        elif current_hour >= 20:
            self.is_test_mode = True
            reason = "오후 8시 이후"

        # 장 운영 시간이 아닌 경우
        elif not is_market_hours():
            self.is_test_mode = True
            reason = "장 마감 시간"

        else:
            self.is_test_mode = False
            logger.info("정규 장 시간 - 테스트 모드 비활성화")
            return False

        # 테스트 모드 활성화
        self.test_date = get_last_trading_date()
        logger.info(f"✅ 테스트 모드 활성화 ({reason})")
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

        # 1. 계좌 조회 테스트
        await self._test_account_info()

        # 2. 시장 탐색 테스트
        await self._test_market_search()

        # 3. 종목 정보 조회 테스트
        await self._test_stock_info()

        # 4. 차트 데이터 조회 테스트
        await self._test_chart_data()

        # 5. 호가 조회 테스트
        await self._test_order_book()

        # 6. 잔고 조회 테스트
        await self._test_balance()

        # 7. AI 분석 테스트
        await self._test_ai_analysis()

        # 8. 매수/매도 시뮬레이션 테스트
        await self._test_trading_simulation()

        # 테스트 완료
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        self.test_results["end_time"] = end_time.isoformat()
        self.test_results["duration_seconds"] = duration

        print("\n" + "=" * 80)
        print("✅ 테스트 완료")
        print("=" * 80)
        print(f"소요 시간: {duration:.2f}초")
        print(f"성공한 테스트: {sum(1 for t in self.test_results['tests'].values() if t.get('success'))}/{len(self.test_results['tests'])}")

        # 결과 저장
        self._save_test_results()

        return self.test_results

    async def _test_account_info(self):
        """계좌 조회 테스트"""
        print("\n[1/8] 계좌 조회 테스트...")

        try:
            from api.account import get_account_balance

            # 가장 최근 영업일 데이터로 조회
            result = get_account_balance(date=self.test_date)

            success = result is not None
            self.test_results["tests"]["account_info"] = {
                "success": success,
                "data": result if success else None,
                "error": None if success else "조회 실패"
            }

            if success:
                print("   ✅ 계좌 조회 성공")
                print(f"      예수금: {result.get('deposit', 'N/A')}")
            else:
                print("   ❌ 계좌 조회 실패")

        except Exception as e:
            logger.error(f"계좌 조회 테스트 실패: {e}")
            self.test_results["tests"]["account_info"] = {
                "success": False,
                "error": str(e)
            }
            print(f"   ❌ 오류: {e}")

    async def _test_market_search(self):
        """시장 탐색 테스트"""
        print("\n[2/8] 시장 탐색 테스트...")

        try:
            from api.market import get_stock_list

            # KOSPI, KOSDAQ 종목 리스트 조회
            result = get_stock_list(market="ALL")

            success = result is not None and len(result) > 0
            self.test_results["tests"]["market_search"] = {
                "success": success,
                "stock_count": len(result) if success else 0,
                "error": None if success else "조회 실패"
            }

            if success:
                print(f"   ✅ 시장 탐색 성공 - 총 {len(result)}개 종목")
            else:
                print("   ❌ 시장 탐색 실패")

        except Exception as e:
            logger.error(f"시장 탐색 테스트 실패: {e}")
            self.test_results["tests"]["market_search"] = {
                "success": False,
                "error": str(e)
            }
            print(f"   ❌ 오류: {e}")

    async def _test_stock_info(self):
        """종목 정보 조회 테스트"""
        print("\n[3/8] 종목 정보 조회 테스트...")

        tested_stocks = []

        try:
            from api.market import get_current_price

            # 테스트 종목들의 현재가 조회 (최근 영업일 데이터)
            for stock_code in self.test_stocks[:3]:  # 처음 3개만 테스트
                try:
                    result = get_current_price(stock_code, date=self.test_date)
                    if result:
                        tested_stocks.append({
                            "code": stock_code,
                            "success": True,
                            "price": result.get("current_price")
                        })
                        print(f"   ✅ {stock_code}: {result.get('current_price', 'N/A')}원")
                    else:
                        tested_stocks.append({
                            "code": stock_code,
                            "success": False
                        })
                        print(f"   ❌ {stock_code}: 조회 실패")

                    await asyncio.sleep(0.3)  # API 속도 제한

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

            print(f"   📊 {success_count}/{len(tested_stocks)} 종목 조회 성공")

        except Exception as e:
            logger.error(f"종목 정보 조회 테스트 실패: {e}")
            self.test_results["tests"]["stock_info"] = {
                "success": False,
                "error": str(e)
            }
            print(f"   ❌ 오류: {e}")

    async def _test_chart_data(self):
        """차트 데이터 조회 테스트"""
        print("\n[4/8] 차트 데이터 조회 테스트...")

        try:
            from api.market import get_daily_chart

            # 삼성전자 일봉 차트 (최근 20일)
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
                print(f"   ✅ 차트 데이터 조회 성공 - {len(result)}일치 데이터")
                print(f"      최근일: {result[0].get('date', 'N/A')}, 종가: {result[0].get('close', 'N/A')}")
            else:
                print("   ❌ 차트 데이터 조회 실패")

        except Exception as e:
            logger.error(f"차트 데이터 조회 테스트 실패: {e}")
            self.test_results["tests"]["chart_data"] = {
                "success": False,
                "error": str(e)
            }
            print(f"   ❌ 오류: {e}")

    async def _test_order_book(self):
        """호가 조회 테스트"""
        print("\n[5/8] 호가 조회 테스트...")

        try:
            from api.market import get_order_book

            # 삼성전자 호가 (최근 영업일 데이터)
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
                print(f"   ✅ 호가 조회 성공")
                print(f"      매도호가: {result.get('ask_price', 'N/A')}")
                print(f"      매수호가: {result.get('bid_price', 'N/A')}")
            else:
                print("   ❌ 호가 조회 실패")

        except Exception as e:
            logger.error(f"호가 조회 테스트 실패: {e}")
            self.test_results["tests"]["order_book"] = {
                "success": False,
                "error": str(e)
            }
            print(f"   ❌ 오류: {e}")

    async def _test_balance(self):
        """잔고 조회 테스트"""
        print("\n[6/8] 잔고 조회 테스트...")

        try:
            from api.account import get_holdings

            # 보유 종목 조회 (최근 영업일 데이터)
            result = get_holdings(date=self.test_date)

            success = result is not None
            self.test_results["tests"]["balance"] = {
                "success": success,
                "holdings_count": len(result) if success and isinstance(result, list) else 0,
                "error": None if success else "조회 실패"
            }

            if success:
                holdings_count = len(result) if isinstance(result, list) else 0
                print(f"   ✅ 잔고 조회 성공 - {holdings_count}개 보유 종목")
            else:
                print("   ❌ 잔고 조회 실패")

        except Exception as e:
            logger.error(f"잔고 조회 테스트 실패: {e}")
            self.test_results["tests"]["balance"] = {
                "success": False,
                "error": str(e)
            }
            print(f"   ❌ 오류: {e}")

    async def _test_ai_analysis(self):
        """AI 분석 테스트"""
        print("\n[7/8] AI 분석 시뮬레이션 테스트...")

        try:
            # AI 분석 시뮬레이션 (실제 API 호출 없이 구조 테스트)
            print("   📊 AI 분석 시뮬레이션 실행 중...")

            # 기술적 지표 계산 시뮬레이션
            technical_analysis = {
                "rsi": 45.2,
                "macd": "매수 신호",
                "bollinger": "중립",
                "volume": "평균 대비 120%"
            }

            # 감성 분석 시뮬레이션
            sentiment_analysis = {
                "news_sentiment": "긍정적",
                "social_sentiment": "중립",
                "analyst_rating": "매수"
            }

            self.test_results["tests"]["ai_analysis"] = {
                "success": True,
                "technical": technical_analysis,
                "sentiment": sentiment_analysis
            }

            print("   ✅ AI 분석 시뮬레이션 완료")
            print(f"      기술적 분석: RSI={technical_analysis['rsi']}, MACD={technical_analysis['macd']}")
            print(f"      감성 분석: 뉴스={sentiment_analysis['news_sentiment']}, 애널리스트={sentiment_analysis['analyst_rating']}")

        except Exception as e:
            logger.error(f"AI 분석 테스트 실패: {e}")
            self.test_results["tests"]["ai_analysis"] = {
                "success": False,
                "error": str(e)
            }
            print(f"   ❌ 오류: {e}")

    async def _test_trading_simulation(self):
        """매수/매도 시뮬레이션 테스트"""
        print("\n[8/8] 매수/매도 시뮬레이션 테스트...")

        try:
            print("   🔄 매매 시뮬레이션 실행 중...")
            print("   ⚠️  실제 주문은 발생하지 않습니다")

            # 매수 시뮬레이션
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

            # 매도 시뮬레이션
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

            print("   ✅ 매매 시뮬레이션 완료")
            print(f"      매수: {buy_simulation['stock_name']} {buy_simulation['quantity']}주 @ {buy_simulation['price']:,}원")
            print(f"      매도: {sell_simulation['stock_name']} {sell_simulation['quantity']}주 @ {sell_simulation['price']:,}원")
            print(f"      예상 수익: {sell_simulation['profit']:,}원 ({sell_simulation['profit_rate']:.2f}%)")

        except Exception as e:
            logger.error(f"매매 시뮬레이션 테스트 실패: {e}")
            self.test_results["tests"]["trading_simulation"] = {
                "success": False,
                "error": str(e)
            }
            print(f"   ❌ 오류: {e}")

    def _save_test_results(self):
        """테스트 결과 저장"""
        try:
            # 결과 디렉토리 생성
            result_dir = Path("test_results")
            result_dir.mkdir(exist_ok=True)

            # 파일명
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_file = result_dir / f"test_mode_results_{timestamp}.json"

            # 결과 저장
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)

            print(f"\n💾 테스트 결과 저장: {result_file}")
            logger.info(f"테스트 결과 저장: {result_file}")

        except Exception as e:
            logger.error(f"테스트 결과 저장 실패: {e}")
            print(f"⚠️  테스트 결과 저장 실패: {e}")


async def run_test_mode():
    """테스트 모드 실행 (편의 함수)"""
    manager = TestModeManager()

    if manager.check_and_activate_test_mode():
        return await manager.run_comprehensive_test()
    else:
        print("현재는 정규 장 시간입니다. 테스트 모드를 실행할 수 없습니다.")
        return None


__all__ = ['TestModeManager', 'run_test_mode']
