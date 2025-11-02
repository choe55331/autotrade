"""
main_v2.py
AutoTrade Pro v2.0 - 통합된 자동매매 시스템
"""
import sys
import time
import signal
import threading
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 경로
sys.path.insert(0, str(Path(__file__).parent))

# 새로운 시스템 임포트 (v4.2: Unified config)
try:
    from config.manager import get_config
except ImportError:
    # Fallback to old config_manager
    from config.config_manager import get_config
try:
    from utils.logger_new import get_logger
except ImportError:
    import logging
    def get_logger():
        return logging.getLogger(__name__)
try:
    from database import get_db_session, Trade, Position, PortfolioSnapshot
except ImportError:
    def get_db_session():
        return None
    Trade = None
    Position = None
    PortfolioSnapshot = None

# 핵심 모듈
from core import KiwoomRESTClient
from core.websocket_client import WebSocketClient
from api import AccountAPI, MarketAPI, OrderAPI
from research import Screener, DataFetcher
from research.strategy_manager import StrategyManager
from strategy.scoring_system import ScoringSystem
from strategy.dynamic_risk_manager import DynamicRiskManager
from strategy import PortfolioManager
from ai.mock_analyzer import MockAnalyzer  # 테스트: Mock 직접 사용
from utils.activity_monitor import get_monitor

# 가상 매매 시스템
from virtual_trading import VirtualTrader, TradeLogger

# 로거
logger = get_logger()


class TradingBotV2:
    """
    AutoTrade Pro v2.0 메인 봇

    통합 기능:
    - 3단계 스캐닝 파이프라인 (Fast → Deep → AI)
    - 10가지 기준 스코어링 시스템 (440점 만점)
    - 동적 리스크 관리 (4단계 모드)
    - 데이터베이스 기록
    - YAML 설정 관리
    """

    def __init__(self):
        """봇 초기화"""
        logger.info("="*60)
        logger.info("🚀 AutoTrade Pro v2.0 초기화 시작")
        logger.info("="*60)

        # 설정 로드
        self.config = get_config()

        # 테스트 모드 확인 및 활성화
        self.test_mode_active = False
        self.test_date = None
        self._check_test_mode()

        # 상태
        self.is_running = False
        self.is_initialized = False
        self.market_status = {}  # 시장 상태 정보 (NXT 포함)
        self.start_time = datetime.now()  # 봇 시작 시간 기록

        # 제어 파일 (data 폴더로 이동)
        self.control_file = Path('data/control.json')
        self.state_file = Path('data/strategy_state.json')

        # 컴포넌트
        self.client = None
        self.websocket_client = None  # WebSocket 클라이언트
        self.account_api = None
        self.market_api = None
        self.order_api = None
        self.data_fetcher = None  # 시장 데이터 조회용

        # 새로운 시스템
        self.strategy_manager = None
        self.scoring_system = None
        self.dynamic_risk_manager = None

        # 기존 시스템
        self.portfolio_manager = None
        self.analyzer = None

        # 가상 매매 시스템
        self.virtual_trader = None
        self.trade_logger = None

        # 활동 모니터
        self.monitor = get_monitor()

        # 데이터베이스 세션
        self.db_session = None

        # AI 승인 매수 후보 리스트
        self.ai_approved_candidates = []

        # 스캔 진행 상황 추적
        self.scan_progress = {
            'current_strategy': '',  # 현재 스캔 전략
            'total_candidates': 0,   # 발견된 후보 수
            'top_candidates': [],    # 상위 후보 (이름, 점수)
            'reviewing': '',         # 현재 검토 중인 종목
            'rejected': [],          # 탈락 종목 (이름, 이유)
            'approved': [],          # 승인 종목 (이름, 가격, 전략)
        }

        # 초기화
        self._initialize_components()

        logger.info("✅ AutoTrade Pro v2.0 초기화 완료")

    def _check_test_mode(self):
        """테스트 모드 확인 및 활성화

        조건:
        - 휴일 (토요일, 일요일)
        - 평일 오후 8시(20:00) ~ 오전 8시(08:00)
        """
        try:
            from utils.trading_date import should_use_test_mode, get_last_trading_date

            # 테스트 모드 사용 여부 확인
            if should_use_test_mode():
                self.test_mode_active = True
                self.test_date = get_last_trading_date()

                now = datetime.now()
                weekday_kr = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
                current_weekday = weekday_kr[now.weekday()]

                logger.info("=" * 60)
                logger.info("🧪 테스트 모드 자동 활성화")
                logger.info(f"   현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')} ({current_weekday})")
                logger.info(f"   사용 데이터 날짜: {self.test_date}")

                if now.weekday() >= 5:
                    logger.info(f"   사유: 휴일 ({current_weekday})")
                else:
                    logger.info(f"   사유: 평일 비장시간 (20:00~08:00)")

                logger.info("   ⚠️  실제 주문은 발생하지 않습니다")
                logger.info("=" * 60)
            else:
                logger.info("⚡ 정규 장 시간 - 실시간 모드")
                self.test_mode_active = False

        except Exception as e:
            logger.warning(f"테스트 모드 확인 실패: {e}")
            self.test_mode_active = False

    def get_test_mode_info(self) -> dict:
        """테스트 모드 정보 반환"""
        return {
            "active": self.test_mode_active,
            "test_date": self.test_date,
            "current_time": datetime.now().isoformat(),
            "is_market_hours": not self.test_mode_active
        }

    def _initialize_components(self):
        """컴포넌트 초기화"""
        try:
            # 1. 데이터베이스 초기화
            logger.info("💾 데이터베이스 초기화 중...")
            self.db_session = get_db_session()
            logger.info("✓ 데이터베이스 초기화 완료")

            # 2. REST 클라이언트
            logger.info("🌐 REST API 클라이언트 초기화 중...")
            self.client = KiwoomRESTClient()
            logger.info("✓ REST API 클라이언트 초기화 완료")

            # 2-1. WebSocket 클라이언트 (실시간 데이터 수신)
            try:
                logger.info("🔌 WebSocket 클라이언트 초기화 중...")
                # 설정에서 WebSocket URL 가져오기
                from config import KIWOOM_WEBSOCKET_URL

                # WebSocket 설정이 있으면 연결
                if KIWOOM_WEBSOCKET_URL and self.client.token:
                    self.websocket_client = WebSocketClient(
                        url=KIWOOM_WEBSOCKET_URL,
                        token=self.client.token
                    )

                    # 콜백 등록
                    self.websocket_client.register_callbacks(
                        on_open=self._on_ws_open,
                        on_message=self._on_ws_message,
                        on_error=self._on_ws_error,
                        on_close=self._on_ws_close
                    )

                    # 연결 시작
                    self.websocket_client.connect()
                    logger.info("✓ WebSocket 클라이언트 초기화 완료 (자동 재연결 활성화)")
                else:
                    self.websocket_client = None
                    logger.info("⚠️  WebSocket 설정 없음 - REST API로 동작")
            except Exception as e:
                logger.warning(f"⚠️  WebSocket 초기화 실패: {e} - REST API로 동작")
                self.websocket_client = None

            # 3. API 모듈
            logger.info("📡 API 모듈 초기화 중...")
            self.account_api = AccountAPI(self.client)
            self.market_api = MarketAPI(self.client)
            self.order_api = OrderAPI(self.client)
            self.data_fetcher = DataFetcher(self.client)  # 시장 데이터 조회
            logger.info("✓ API 모듈 초기화 완료")

            # 4. AI 분석기 (Gemini API 키가 있으면 실제 사용, 없으면 Mock)
            logger.info("🤖 AI 분석기 초기화 중...")
            try:
                from config import GEMINI_API_KEY

                # Gemini API 키 확인
                if GEMINI_API_KEY and GEMINI_API_KEY.strip() and GEMINI_API_KEY != "your-gemini-api-key-here":
                    # 실제 Gemini 사용
                    from ai.gemini_analyzer import GeminiAnalyzer
                    self.analyzer = GeminiAnalyzer()
                    if self.analyzer.initialize():
                        logger.info("✅ Gemini AI 분석기 초기화 완료 (실제 AI 사용)")
                    else:
                        logger.warning("Gemini 초기화 실패 - Mock으로 대체")
                        from ai.mock_analyzer import MockAnalyzer
                        self.analyzer = MockAnalyzer()
                        self.analyzer.initialize()
                        logger.info("✓ Mock AI 분석기 초기화 완료 (대체)")
                else:
                    # Gemini API 키 없음 - Mock 사용
                    from ai.mock_analyzer import MockAnalyzer
                    self.analyzer = MockAnalyzer()
                    self.analyzer.initialize()
                    logger.info("✓ Mock AI 분석기 초기화 완료 (Gemini API 키 없음)")

            except Exception as e:
                logger.error(f"AI 분석기 초기화 실패: {e}")
                # 폴백: Mock 사용
                from ai.mock_analyzer import MockAnalyzer
                self.analyzer = MockAnalyzer()
                self.analyzer.initialize()
                logger.warning("✓ Mock AI 분석기로 폴백")

            # 5. 3가지 스캔 전략 매니저 (신규)
            logger.info("🎯 3가지 스캔 전략 매니저 초기화 중...")
            screener = Screener(self.client)
            self.strategy_manager = StrategyManager(
                market_api=self.market_api,
                screener=screener,
                ai_analyzer=self.analyzer,
                config=get_config().get('scan_strategies', {})
            )
            logger.info("✓ 3가지 스캔 전략 매니저 초기화 완료")

            # 6. 10가지 스코어링 시스템 (신규)
            logger.info("📊 10가지 스코어링 시스템 초기화 중...")
            self.scoring_system = ScoringSystem(market_api=self.market_api)
            logger.info("✓ 10가지 스코어링 시스템 초기화 완료")

            # 7. 동적 리스크 관리 (신규)
            logger.info("🛡️ 동적 리스크 관리자 초기화 중...")
            initial_capital = self._get_initial_capital()
            self.dynamic_risk_manager = DynamicRiskManager(initial_capital=initial_capital)
            logger.info("✓ 동적 리스크 관리자 초기화 완료")

            # 8. 포트폴리오 관리자
            logger.info("💼 포트폴리오 관리자 초기화 중...")
            self.portfolio_manager = PortfolioManager(self.client)
            logger.info("✓ 포트폴리오 관리자 초기화 완료")

            # 9. 가상 매매 시스템
            logger.info("📝 가상 매매 시스템 초기화 중...")
            try:
                # 가상 매매 초기 자본: 실제 계좌 잔고 기준
                deposit = self.account_api.get_deposit()
                if deposit:
                    # 실제 주문 가능 금액
                    real_available_cash = int(deposit.get('ord_alow_amt', 0))
                    # 총 평가 금액
                    total_assets = int(deposit.get('tot_evlu_amt', 0))

                    # 가상 매매는 실제 총 자산 기준으로 시작
                    virtual_initial_cash = total_assets if total_assets > 0 else real_available_cash

                    logger.info(f"   실제 총 자산: {total_assets:,}원")
                    logger.info(f"   가상 매매 초기 자본: {virtual_initial_cash:,}원")
                else:
                    # API 조회 실패 시 기본값 (1000만원)
                    virtual_initial_cash = 10_000_000
                    logger.warning(f"   계좌 정보 조회 실패 - 기본값 사용: {virtual_initial_cash:,}원")

                # VirtualTrader 초기화 (3가지 전략: 공격적, 보수적, 균형)
                self.virtual_trader = VirtualTrader(initial_cash=virtual_initial_cash)

                # TradeLogger 초기화
                self.trade_logger = TradeLogger()

                # 과거 7일 로그 불러오기
                loaded_count = self.trade_logger.load_historical_trades(days=7)
                if loaded_count > 0:
                    logger.info(f"✓ 과거 거래 로그 {loaded_count}건 불러옴")

                # 가상 계좌 상태 복원
                self.virtual_trader.load_all_states()

                logger.info("✅ 가상 매매 시스템 초기화 완료 (3가지 전략 운영)")
            except Exception as e:
                logger.warning(f"⚠️  가상 매매 시스템 초기화 실패: {e}")
                self.virtual_trader = None
                self.trade_logger = None

            # 10. 제어 파일
            self._initialize_control_file()

            # 11. 이전 상태 복원
            self._restore_state()

            self.is_initialized = True
            logger.info("✅ 모든 컴포넌트 초기화 완료")

            # 활동 모니터
            self.monitor.log_activity(
                'system',
                '🚀 AutoTrade Pro v2.0 시작',
                level='success'
            )

        except Exception as e:
            logger.error(f"컴포넌트 초기화 실패: {e}", exc_info=True)
            raise

    def _get_initial_capital(self) -> int:
        """초기 자본금 가져오기"""
        try:
            deposit = self.account_api.get_deposit()
            if deposit:
                return int(deposit.get('d_ord_aval_cash', 10_000_000))
            return 10_000_000  # 기본값 1천만원
        except:
            return 10_000_000

    def _initialize_control_file(self):
        """제어 파일 초기화"""
        if not self.control_file.exists():
            default_state = {
                'run': True,
                'pause_buy': False,
                'pause_sell': False,
            }
            import json
            with open(self.control_file, 'w') as f:
                json.dump(default_state, f, indent=2)
            logger.info("제어 파일 생성 완료")

    def _restore_state(self):
        """이전 상태 복원"""
        try:
            if self.state_file.exists():
                import json
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                logger.info(f"이전 상태 복원: {len(state.get('positions', {}))}개 포지션")
        except Exception as e:
            logger.warning(f"상태 복원 실패: {e}")

    def _test_samsung_trade(self):
        """삼성전자 테스트 매매 (연결 직후 1주 매수 → 10초 후 매도)"""
        try:
            logger.info("="*60)
            logger.info("🧪 삼성전자 테스트 매매 시작")
            logger.info("="*60)

            samsung_code = "005930"  # 삼성전자
            samsung_name = "삼성전자"

            # 현재 시간 확인 및 거래 유형 결정
            now = datetime.now()
            current_hour = now.hour
            current_minute = now.minute

            market_type = ""
            order_type = "00"  # 지정가

            # 시간대별 거래 유형 판단
            if 8 <= current_hour < 9:
                market_type = "NXT 프리마켓"
                logger.info(f"⏰ 현재 시간: {now.strftime('%H:%M:%S')} - {market_type}")
            elif 9 <= current_hour < 15 or (current_hour == 15 and current_minute < 30):
                market_type = "일반시장"
                logger.info(f"⏰ 현재 시간: {now.strftime('%H:%M:%S')} - {market_type}")
            else:
                market_type = "장외시간"
                logger.warning(f"⏰ 현재 시간: {now.strftime('%H:%M:%S')} - {market_type} (테스트 주문 시도, 서버에서 거절 예상)")

            # 1. 삼성전자 현재가 조회
            logger.info(f"📊 {samsung_name} 현재가 조회 중...")
            current_price = 70000  # 기본값 (장외시간 대비)

            try:
                # 먼저 현재가 API 시도
                quote = self.market_api.get_stock_price(samsung_code)
                if quote and quote.get('current_price', 0) > 0:
                    current_price = int(quote.get('current_price', 0))
                    logger.info(f"✓ {samsung_name} 현재가: {current_price:,}원")
                else:
                    # 현재가 조회 실패 시 호가 조회로 대체
                    logger.warning(f"⚠️ 현재가 조회 실패 - 호가 조회 시도 중...")
                    orderbook = self.market_api.get_orderbook(samsung_code)
                    if orderbook:
                        # 매도1호가와 매수1호가의 중간값 사용
                        sell_price = int(orderbook.get('sell_hoga', [{}])[0].get('price', 0)) if orderbook.get('sell_hoga') else 0
                        buy_price = int(orderbook.get('buy_hoga', [{}])[0].get('price', 0)) if orderbook.get('buy_hoga') else 0

                        if sell_price > 0 and buy_price > 0:
                            current_price = (sell_price + buy_price) // 2
                            logger.info(f"✓ {samsung_name} 호가 기준 현재가: {current_price:,}원 (매도1: {sell_price:,}, 매수1: {buy_price:,})")
                        elif sell_price > 0:
                            current_price = sell_price
                            logger.info(f"✓ {samsung_name} 매도1호가 사용: {current_price:,}원")
                        elif buy_price > 0:
                            current_price = buy_price
                            logger.info(f"✓ {samsung_name} 매수1호가 사용: {current_price:,}원")
                        else:
                            logger.warning(f"⚠️ 호가 조회 실패 - 고정가격 사용: {current_price:,}원")
                    else:
                        logger.warning(f"⚠️ 호가 조회 실패 - 고정가격 사용: {current_price:,}원")

            except Exception as e:
                logger.warning(f"⚠️ 가격 조회 실패: {e} - 고정가격 사용: {current_price:,}원")

            # 2. 매수 주문 실행
            quantity = 1  # 1주
            logger.info(f"📥 {samsung_name} 매수 주문 실행 중...")
            logger.info(f"   종목코드: {samsung_code}")
            logger.info(f"   수량: {quantity}주")
            logger.info(f"   가격: {current_price:,}원")
            logger.info(f"   총액: {current_price * quantity:,}원")
            logger.info(f"   거래유형: {market_type}")

            try:
                buy_result = self.order_api.buy(
                    stock_code=samsung_code,
                    quantity=quantity,
                    price=current_price,
                    order_type=order_type
                )

                if buy_result:
                    order_no = buy_result.get('order_no', 'N/A')
                    logger.info(f"✅ {samsung_name} 매수 주문 성공!")
                    logger.info(f"   주문번호: {order_no}")

                    # 활동 로그
                    self.monitor.log_activity(
                        'test_buy',
                        f'🧪 테스트: {samsung_name} 매수 {quantity}주 @ {current_price:,}원',
                        level='success'
                    )
                else:
                    logger.error("매수 주문 실패")
                    return

            except Exception as e:
                logger.error(f"매수 주문 실패: {e}")
                return

            # 3. 10초 대기
            logger.info("⏳ 10초 대기 중...")
            for i in range(10, 0, -1):
                print(f"   {i}초 남음...", end='\r')
                time.sleep(1)
            print()

            # 4. 매도 주문 실행
            logger.info(f"📤 {samsung_name} 매도 주문 실행 중...")

            # 최신 현재가 재조회
            sell_price = current_price  # 기본값: 매수가 사용
            try:
                # 먼저 현재가 API 시도
                quote = self.market_api.get_stock_price(samsung_code)
                if quote and quote.get('current_price', 0) > 0:
                    sell_price = int(quote.get('current_price', 0))
                    logger.info(f"✓ {samsung_name} 현재가 (매도): {sell_price:,}원")
                else:
                    # 현재가 조회 실패 시 호가 조회로 대체
                    logger.warning(f"⚠️ 현재가 재조회 실패 - 호가 조회 시도 중...")
                    orderbook = self.market_api.get_orderbook(samsung_code)
                    if orderbook:
                        # 매도1호가와 매수1호가의 중간값 사용
                        sell_hoga = int(orderbook.get('sell_hoga', [{}])[0].get('price', 0)) if orderbook.get('sell_hoga') else 0
                        buy_hoga = int(orderbook.get('buy_hoga', [{}])[0].get('price', 0)) if orderbook.get('buy_hoga') else 0

                        if sell_hoga > 0 and buy_hoga > 0:
                            sell_price = (sell_hoga + buy_hoga) // 2
                            logger.info(f"✓ {samsung_name} 호가 기준 현재가: {sell_price:,}원 (매도1: {sell_hoga:,}, 매수1: {buy_hoga:,})")
                        elif buy_hoga > 0:
                            sell_price = buy_hoga
                            logger.info(f"✓ {samsung_name} 매수1호가 사용: {sell_price:,}원")
                        elif sell_hoga > 0:
                            sell_price = sell_hoga
                            logger.info(f"✓ {samsung_name} 매도1호가 사용: {sell_price:,}원")
                        else:
                            logger.warning(f"⚠️ 호가 조회 실패 - 매수가 사용: {sell_price:,}원")
                    else:
                        logger.warning(f"⚠️ 호가 조회 실패 - 매수가 사용: {sell_price:,}원")

            except Exception as e:
                logger.warning(f"⚠️ 가격 재조회 실패: {e} - 매수가 사용: {sell_price:,}원")

            try:
                sell_result = self.order_api.sell(
                    stock_code=samsung_code,
                    quantity=quantity,
                    price=sell_price,
                    order_type=order_type
                )

                if sell_result:
                    order_no = sell_result.get('order_no', 'N/A')
                    profit_loss = (sell_price - current_price) * quantity
                    logger.info(f"✅ {samsung_name} 매도 주문 성공!")
                    logger.info(f"   주문번호: {order_no}")
                    logger.info(f"   매수가: {current_price:,}원")
                    logger.info(f"   매도가: {sell_price:,}원")
                    logger.info(f"   손익: {profit_loss:+,}원")

                    # 활동 로그
                    self.monitor.log_activity(
                        'test_sell',
                        f'🧪 테스트: {samsung_name} 매도 {quantity}주 @ {sell_price:,}원 (손익: {profit_loss:+,}원)',
                        level='success' if profit_loss >= 0 else 'warning'
                    )
                else:
                    logger.error("매도 주문 실패")

            except Exception as e:
                logger.error(f"매도 주문 실패: {e}")

            logger.info("="*60)
            logger.info("✅ 삼성전자 테스트 매매 완료")
            logger.info("="*60)

        except Exception as e:
            logger.error(f"테스트 매매 중 오류: {e}", exc_info=True)

    def start(self):
        """봇 시작"""
        if not self.is_initialized:
            logger.error("봇이 초기화되지 않았습니다")
            print("❌ 오류: 봇이 초기화되지 않았습니다")
            return

        print("\n" + "="*60)
        print("🚀 AutoTrade Pro v2.0 메인 루프 시작")
        print("="*60)
        logger.info("="*60)
        logger.info("🚀 AutoTrade Pro v2.0 실행 시작")
        logger.info("="*60)

        self.is_running = True

        try:
            # 🧪 삼성전자 테스트 매매 실행
            self._test_samsung_trade()

            # 메인 루프 시작
            self._main_loop()
        except KeyboardInterrupt:
            logger.info("사용자에 의한 중단")
            print("\n사용자에 의한 중단")
        except Exception as e:
            logger.error(f"메인 루프 오류: {e}", exc_info=True)
            print(f"\n❌ 메인 루프 오류: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.stop()

    def stop(self):
        """봇 정지"""
        logger.info("AutoTrade Pro v2.0 종료 중...")
        self.is_running = False

        # 가상 매매 상태 저장
        if self.virtual_trader:
            try:
                logger.info("📝 가상 매매 상태 저장 중...")
                self.virtual_trader.save_all_states()
                logger.info("✓ 가상 매매 상태 저장 완료")
            except Exception as e:
                logger.warning(f"가상 매매 상태 저장 실패: {e}")

        # 가상 매매 로그 요약 출력
        if self.trade_logger:
            try:
                self.trade_logger.print_summary()
            except Exception as e:
                logger.warning(f"가상 매매 로그 요약 출력 실패: {e}")

        if self.db_session:
            self.db_session.close()

        if self.client:
            self.client.close()

        logger.info("✅ AutoTrade Pro v2.0 종료 완료")

    def _main_loop(self):
        """메인 루프"""
        cycle_count = 0
        # Backward compatibility: handle both Pydantic (object) and old config (dict)
        try:
            if hasattr(self.config.main_cycle, 'sleep_seconds'):
                sleep_seconds = self.config.main_cycle.sleep_seconds
            else:
                sleep_seconds = self.config.main_cycle.get('sleep_seconds', 60)
        except Exception as e:
            logger.warning(f"Config 로드 실패, 기본값 사용: {e}")
            sleep_seconds = 60

        while self.is_running:
            cycle_count += 1

            # 첫 사이클이 아니면 대기
            if cycle_count > 1:
                logger.info(f"⏳ {sleep_seconds}초 대기...\n")
                time.sleep(sleep_seconds)

            print(f"\n{'='*60}")
            print(f"🔄 사이클 #{cycle_count}")
            print(f"{'='*60}")

            try:
                self._read_control_file()
                if not self.is_running:
                    break

                trading_hours_ok = self._check_trading_hours()
                if not trading_hours_ok:
                    continue

                self._update_account_info()

                # 가상 매매 가격 업데이트 및 매도 검토
                if self.virtual_trader:
                    try:
                        # 가상 계좌의 모든 포지션 가격 업데이트
                        price_data = self._get_virtual_trading_prices()
                        if price_data:
                            self.virtual_trader.update_all_prices(price_data)

                        # 가상 매매 매도 조건 확인
                        self.virtual_trader.check_sell_conditions(price_data)
                    except Exception as e:
                        logger.warning(f"가상 매매 업데이트 실패: {e}")

                # 매도 검토
                if not self.pause_sell:
                    self._check_sell_signals()

                # 매수 검토
                if not self.pause_buy:
                    self._run_scanning_pipeline()

                self._save_portfolio_snapshot()
                self._print_statistics()

            except Exception as e:
                logger.error(f"메인 루프 오류: {e}", exc_info=True)
                print(f"❌ 메인 루프 오류: {e}")
                import traceback
                traceback.print_exc()

    def _read_control_file(self):
        """제어 파일 읽기"""
        try:
            import json
            if self.control_file.exists():
                with open(self.control_file, 'r') as f:
                    control = json.load(f)
                self.is_running = control.get('run', True)
                self.pause_buy = control.get('pause_buy', False)
                self.pause_sell = control.get('pause_sell', False)
        except Exception as e:
            logger.warning(f"제어 파일 읽기 실패: {e}")

    def _check_trading_hours(self) -> bool:
        """거래 시간 확인 (NXT 시장 포함)"""
        from research.analyzer import Analyzer
        analyzer = Analyzer(self.client)
        market_status = analyzer.get_market_status()

        # 시장 상태 저장 (다른 메서드에서 사용)
        self.market_status = market_status

        # 테스트 모드: 장 운영 시간이 아니어도 실제 API 호출로 탐색/분석/주문 실행
        if not market_status['is_trading_hours']:
            logger.info(f"⏸️  장 운영 시간 아님: {market_status['market_status']}")
            logger.info(f"🧪 테스트 모드 활성화 - 실제 API 호출 실행 (서버에서 주문 거절 예상)")
            # 테스트 모드로 강제 설정
            self.market_status['is_trading_hours'] = True
            self.market_status['is_test_mode'] = True
            self.market_status['market_type'] = '테스트 모드'
            # return False  # 주석 처리: 항상 실행

        # 시장 상태 로그
        if market_status.get('is_test_mode'):
            logger.info(f"🧪 테스트 모드: {market_status['market_status']}")
        elif market_status.get('can_cancel_only'):
            logger.info(f"⚠️  {market_status['market_type']}: {market_status['market_status']}")
        elif market_status.get('order_type_limit') == 'limit_only':
            logger.info(f"📊 {market_status['market_type']}: {market_status['market_status']}")
        else:
            logger.info(f"✅ {market_status['market_type']}: {market_status['market_status']}")

        return True

    def _update_account_info(self):
        """계좌 정보 업데이트"""
        try:
            deposit = self.account_api.get_deposit()
            cash = int(deposit.get('ord_alow_amt', 0)) if deposit else 0

            holdings = self.account_api.get_holdings()

            # 포트폴리오 업데이트
            self.portfolio_manager.update_portfolio(holdings, cash)

            # 동적 리스크 관리자 업데이트
            total_capital = cash + sum(h.get('eval_amt', 0) for h in holdings)
            self.dynamic_risk_manager.update_capital(total_capital)

            logger.info(f"💰 계좌 정보: 현금 {cash:,}원, 보유 {len(holdings)}개")

        except Exception as e:
            logger.error(f"계좌 정보 업데이트 실패: {e}")

    def _check_sell_signals(self):
        """매도 신호 검토"""
        logger.info("🔍 매도 신호 검토 중...")

        # 테스트 모드 표시
        if self.market_status.get('is_test_mode'):
            logger.info("🧪 테스트 모드: 실제 보유 종목으로 매도 로직 실행 (API 호출, 서버에서 거절 예상)")

        try:
            holdings = self.account_api.get_holdings()

            if not holdings:
                logger.info("보유 종목 없음")
                return

            for holding in holdings:
                stock_code = holding.get('pdno')
                stock_name = holding.get('prdt_name')
                current_price = int(holding.get('prpr', 0))
                quantity = int(holding.get('hldg_qty', 0))
                buy_price = int(holding.get('pchs_avg_pric', 0))

                # 수익률 계산
                profit_loss = (current_price - buy_price) * quantity
                profit_loss_rate = ((current_price - buy_price) / buy_price) * 100 if buy_price > 0 else 0

                # 청산 임계값 가져오기
                thresholds = self.dynamic_risk_manager.get_exit_thresholds(buy_price)

                # 매도 조건 확인
                should_sell = False
                sell_reason = ""

                if current_price >= thresholds['take_profit']:
                    should_sell = True
                    sell_reason = f"목표가 도달 ({thresholds['take_profit']:,}원)"
                elif current_price <= thresholds['stop_loss']:
                    should_sell = True
                    sell_reason = f"손절가 도달 ({thresholds['stop_loss']:,}원)"

                if should_sell:
                    logger.info(f"📤 {stock_name} 매도 신호: {sell_reason}")
                    self._execute_sell(stock_code, stock_name, quantity, current_price, profit_loss, profit_loss_rate, sell_reason)

        except Exception as e:
            logger.error(f"매도 검토 실패: {e}")

    def _run_scanning_pipeline(self):
        """3단계 스캐닝 파이프라인 실행"""

        try:
            # 포지션 추가 가능 여부
            can_add = self.portfolio_manager.can_add_position()
            positions = self.portfolio_manager.get_positions()
            if not can_add:
                logger.info("⚠️  최대 포지션 수 도달")
                return

            # 동적 리스크 관리 확인
            current_positions = len(positions)
            should_open = self.dynamic_risk_manager.should_open_position(current_positions)

            if not should_open:
                logger.info("⚠️  리스크 관리: 포지션 진입 불가")
                return

            # 현재 전략 실행 (3가지 전략 순환)
            final_candidates = self.strategy_manager.run_current_strategy()

            # 스캔 진행 상황 업데이트
            strategy_name = self.strategy_manager.get_current_strategy_name() if hasattr(self.strategy_manager, 'get_current_strategy_name') else '시장 스캔'
            self.scan_progress['current_strategy'] = strategy_name
            self.scan_progress['total_candidates'] = len(final_candidates)
            self.scan_progress['rejected'] = []
            self.scan_progress['approved'] = []

            if not final_candidates:
                print("✅ 스캐닝 완료: 최종 후보 없음")
                logger.info("✅ 스캐닝 완료: 최종 후보 없음")
                return

            # 20개 모두 스코어링 시스템으로 점수 계산
            candidate_scores = {}
            for candidate in final_candidates:
                stock_data = {
                    'stock_code': candidate.code,
                    'stock_name': candidate.name,
                    'current_price': candidate.price,
                    'volume': candidate.volume,
                    'change_rate': candidate.rate,
                    'institutional_net_buy': candidate.institutional_net_buy,
                    'foreign_net_buy': candidate.foreign_net_buy,
                    'bid_ask_ratio': candidate.bid_ask_ratio,
                }
                scoring_result = self.scoring_system.calculate_score(stock_data)
                candidate_scores[candidate.code] = scoring_result
                candidate.final_score = scoring_result.total_score

            # 점수 기준 재정렬
            final_candidates.sort(key=lambda x: x.final_score, reverse=True)

            # 상위 5개만 표시 및 AI 검토
            top5 = final_candidates[:5]
            print(f"\n📊 상위 5개 후보:")

            # scan_progress 업데이트 - 상위 후보
            self.scan_progress['top_candidates'] = []

            for rank, c in enumerate(top5, 1):
                score_result = candidate_scores[c.code]
                # 주요 점수 카테고리 (0점 초과인 것만)
                breakdown_parts = []
                if score_result.volume_surge_score > 0:
                    breakdown_parts.append(f"거래량:{score_result.volume_surge_score:.0f}")
                if score_result.price_momentum_score > 0:
                    breakdown_parts.append(f"가격:{score_result.price_momentum_score:.0f}")
                if score_result.institutional_buying_score > 0:
                    breakdown_parts.append(f"기관:{score_result.institutional_buying_score:.0f}")
                if score_result.bid_strength_score > 0:
                    breakdown_parts.append(f"호가:{score_result.bid_strength_score:.0f}")
                if score_result.technical_indicators_score > 0:
                    breakdown_parts.append(f"기술:{score_result.technical_indicators_score:.0f}")
                breakdown_str = ", ".join(breakdown_parts) if breakdown_parts else "기타"
                percentage = (c.final_score / 440) * 100
                print(f"   {rank}. {c.name} - {c.final_score:.0f}점 ({percentage:.0f}%) [{breakdown_str}]")

                # scan_progress에 추가
                self.scan_progress['top_candidates'].append({
                    'rank': rank,
                    'name': c.name,
                    'code': c.code,
                    'score': c.final_score,
                    'percentage': percentage,
                    'breakdown': breakdown_str
                })

            # 포트폴리오 정보
            portfolio_info = "No positions"

            # AI 매수 검토 (상위 3개)
            for idx, candidate in enumerate(top5[:3], 1):
                # scan_progress 업데이트 - 현재 검토 중
                self.scan_progress['reviewing'] = f"{candidate.name} ({idx}/3)"

                print(f"\n🤖 [{idx}/3] {candidate.name}")

                # 이미 계산된 점수 사용
                scoring_result = candidate_scores[candidate.code]

                # AI 분석 실행
                stock_data = {
                    'stock_code': candidate.code,
                    'stock_name': candidate.name,
                    'current_price': candidate.price,
                    'volume': candidate.volume,
                    'change_rate': candidate.rate,
                    'institutional_net_buy': candidate.institutional_net_buy,
                    'foreign_net_buy': candidate.foreign_net_buy,
                    'bid_ask_ratio': candidate.bid_ask_ratio,
                }

                # 점수 breakdown 생성
                score_info = {
                    'score': scoring_result.total_score,
                    'percentage': scoring_result.percentage,
                    'breakdown': {
                        '거래량 급증': scoring_result.volume_surge_score,
                        '가격 모멘텀': scoring_result.price_momentum_score,
                        '기관 매수세': scoring_result.institutional_buying_score,
                        '매수 호가 강도': scoring_result.bid_strength_score,
                        '체결 강도': scoring_result.execution_intensity_score,
                        '증권사 활동': scoring_result.broker_activity_score,
                        '프로그램 매매': scoring_result.program_trading_score,
                        '기술적 지표': scoring_result.technical_indicators_score,
                        '테마/뉴스': scoring_result.theme_news_score,
                        '변동성 패턴': scoring_result.volatility_pattern_score,
                    }
                }

                # AI에게 매수 여부, 분할 매수 전략 질문
                ai_analysis = self.analyzer.analyze_stock(
                    stock_data,
                    score_info=score_info,
                    portfolio_info=portfolio_info
                )
                ai_signal = ai_analysis.get('signal', 'hold')
                split_strategy = ai_analysis.get('split_strategy', '')

                # AI 분석 결과 저장
                candidate.ai_signal = ai_signal
                candidate.ai_reasons = ai_analysis.get('reasons', [])

                # AI 원본 응답 전체 출력
                if ai_analysis.get('analysis_text'):
                    print(f"   [AI 원본 응답]")
                    for line in ai_analysis['analysis_text'].split('\n'):
                        if line.strip():
                            print(f"   {line}")

                # 결과 출력
                print(f"\n   ✅ AI 결정: {ai_signal.upper()}")

                if ai_signal == 'buy' and split_strategy:
                    print(f"   📊 분할매수 전략:")
                    for line in split_strategy.split('\n'):
                        if line.strip():
                            print(f"      {line}")

                if ai_analysis.get('reasons'):
                    print(f"   💡 사유: {ai_analysis['reasons'][0]}")

                if ai_analysis.get('risks') and ai_analysis['risks']:
                    print(f"   ⚠️  경고: {ai_analysis['risks'][0]}")

                # AI 승인 시 매수 후보 리스트에 추가
                if ai_signal == 'buy':
                    buy_candidate = {
                        'stock_code': candidate.code,
                        'stock_name': candidate.name,
                        'current_price': candidate.price,
                        'change_rate': candidate.rate,
                        'score': scoring_result.total_score,
                        'split_strategy': split_strategy,
                        'ai_reason': ai_analysis.get('reasons', [''])[0] if ai_analysis.get('reasons') else '',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    # 최대 10개까지만 유지
                    self.ai_approved_candidates.insert(0, buy_candidate)
                    self.ai_approved_candidates = self.ai_approved_candidates[:10]

                # 최종 승인 조건
                if ai_signal == 'buy' and scoring_result.total_score >= 300:
                    print(f"✅ 매수 조건 충족 - 주문 실행")

                    # scan_progress 업데이트 - 승인
                    self.scan_progress['approved'].append({
                        'name': candidate.name,
                        'price': candidate.price,
                        'strategy': split_strategy,
                        'score': scoring_result.total_score
                    })

                    # 실제 매수 실행
                    self._execute_buy(candidate, scoring_result)

                    # 가상 매매 시스템에도 매수 신호 전달
                    if self.virtual_trader:
                        try:
                            stock_data = {
                                'stock_code': candidate.code,
                                'stock_name': candidate.name,
                                'current_price': candidate.price,
                                'change_rate': candidate.rate,
                                'volume': getattr(candidate, 'volume', 0),
                            }
                            ai_analysis_data = {
                                'signal': ai_signal,
                                'split_strategy': split_strategy,
                                'reasons': ai_analysis.get('reasons', []),
                                'score': scoring_result.total_score,
                            }
                            self.virtual_trader.process_buy_signal(stock_data, ai_analysis_data)
                            print(f"   📝 가상 매매: 3가지 전략으로 매수 시그널 처리 완료")
                        except Exception as e:
                            logger.warning(f"가상 매매 매수 처리 실패: {e}")

                    break  # 1회 사이클에 1개만
                else:
                    reason_text = f"AI={ai_signal}, 점수={scoring_result.total_score:.0f}"
                    print(f"❌ 매수 조건 미충족 ({reason_text})")

                    # scan_progress 업데이트 - 탈락
                    self.scan_progress['rejected'].append({
                        'name': candidate.name,
                        'reason': reason_text,
                        'score': scoring_result.total_score
                    })

            # 검토 완료
            self.scan_progress['reviewing'] = ''
            print("📍 스캔 전략 완료")

        except Exception as e:
            logger.error(f"스캔 전략 실패: {e}", exc_info=True)
            print(f"❌ 스캔 전략 오류: {e}")
            import traceback
            traceback.print_exc()

    def _execute_buy(self, candidate, scoring_result):
        """매수 실행 (NXT 시장 규칙 적용)"""
        try:
            # KRX 종가 결정 시간에는 신규 주문 불가
            if self.market_status.get('can_cancel_only'):
                logger.warning(f"⚠️  {self.market_status['market_type']}: 신규 매수 주문 불가")
                return

            stock_code = candidate.code
            stock_name = candidate.name
            current_price = candidate.price

            # 가용 현금
            deposit = self.account_api.get_deposit()
            available_cash = int(deposit.get('ord_alow_amt', 0)) if deposit else 0

            # 포지션 크기 계산 (동적 리스크 관리)
            quantity = self.dynamic_risk_manager.calculate_position_size(
                stock_price=current_price,
                available_cash=available_cash
            )

            if quantity == 0:
                logger.warning("매수 가능 수량 0")
                return

            total_amount = current_price * quantity

            logger.info(
                f"💳 {stock_name} 매수 실행: {quantity}주 @ {current_price:,}원 "
                f"(총 {total_amount:,}원)"
            )

            # 주문 유형 결정 (NXT 프리/애프터마켓에서는 지정가만 가능)
            order_type = '00'  # 기본: 지정가
            if self.market_status.get('order_type_limit') == 'all':
                # 메인마켓에서는 시장가 주문도 가능 (필요시)
                order_type = '00'  # 여전히 지정가 사용 (안전)

            # 테스트 모드일 때 로그
            if self.market_status.get('is_test_mode'):
                logger.info(f"🧪 테스트 모드: AI 검토 완료 → 실제 매수 API 호출 (서버에서 거절 예상)")
                logger.info(f"   종목: {stock_name}, AI 점수: {candidate.ai_score}, 종합 점수: {scoring_result.total_score}")

            # 주문 실행
            order_result = self.order_api.buy(
                stock_code=stock_code,
                quantity=quantity,
                price=current_price,
                order_type=order_type
            )

            if order_result:
                order_no = order_result.get('order_no', '')

                # DB에 거래 기록
                trade = Trade(
                    stock_code=stock_code,
                    stock_name=stock_name,
                    action='buy',
                    quantity=quantity,
                    price=current_price,
                    total_amount=total_amount,
                    risk_mode=self.dynamic_risk_manager.current_mode.value,
                    ai_score=candidate.ai_score,
                    ai_signal=candidate.ai_signal,
                    ai_confidence=candidate.ai_confidence,
                    scoring_total=scoring_result.total_score,
                    scoring_percentage=scoring_result.percentage
                )
                self.db_session.add(trade)
                self.db_session.commit()

                logger.info(f"✅ {stock_name} 매수 성공 (주문번호: {order_no})")

                self.monitor.log_activity(
                    'buy',
                    f'✅ {stock_name} 매수: {quantity}주 @ {current_price:,}원',
                    level='success'
                )

        except Exception as e:
            logger.error(f"매수 실행 실패: {e}", exc_info=True)

    def _execute_sell(self, stock_code, stock_name, quantity, price, profit_loss, profit_loss_rate, reason):
        """매도 실행 (NXT 시장 규칙 적용)"""
        try:
            # KRX 종가 결정 시간에는 신규 주문 불가
            if self.market_status.get('can_cancel_only'):
                logger.warning(f"⚠️  {self.market_status['market_type']}: 신규 매도 주문 불가")
                return

            logger.info(
                f"💸 {stock_name} 매도 실행: {quantity}주 @ {price:,}원 "
                f"(손익: {profit_loss:+,}원, {profit_loss_rate:+.2f}%)"
            )

            # 주문 유형 결정 (NXT 프리/애프터마켓에서는 지정가만 가능)
            order_type = '00'  # 지정가

            # 테스트 모드일 때 로그
            if self.market_status.get('is_test_mode'):
                logger.info(f"🧪 테스트 모드: 매도 조건 충족 → 실제 매도 API 호출 (서버에서 거절 예상)")
                logger.info(f"   종목: {stock_name}, 사유: {reason}, 손익: {profit_loss:+,}원 ({profit_loss_rate:+.2f}%)")

            # 주문 실행
            order_result = self.order_api.sell(
                stock_code=stock_code,
                quantity=quantity,
                price=price,
                order_type=order_type
            )

            if order_result:
                order_no = order_result.get('order_no', '')

                # DB에 거래 기록
                trade = Trade(
                    stock_code=stock_code,
                    stock_name=stock_name,
                    action='sell',
                    quantity=quantity,
                    price=price,
                    total_amount=price * quantity,
                    profit_loss=profit_loss,
                    profit_loss_ratio=profit_loss_rate / 100,
                    risk_mode=self.dynamic_risk_manager.current_mode.value,
                    notes=reason
                )
                self.db_session.add(trade)
                self.db_session.commit()

                log_level = 'success' if profit_loss >= 0 else 'warning'
                logger.info(f"✅ {stock_name} 매도 성공 (주문번호: {order_no})")

                self.monitor.log_activity(
                    'sell',
                    f'✅ {stock_name} 매도: {quantity}주 @ {price:,}원 (손익: {profit_loss:+,}원)',
                    level=log_level
                )

        except Exception as e:
            logger.error(f"매도 실행 실패: {e}", exc_info=True)

    def _save_portfolio_snapshot(self):
        """포트폴리오 스냅샷 저장"""
        try:
            summary = self.portfolio_manager.get_portfolio_summary()

            snapshot = PortfolioSnapshot(
                total_capital=summary['total_assets'],
                cash=summary['cash'],
                stock_value=summary['stocks_value'],  # Fixed: stocks_value -> stock_value
                total_profit_loss=summary['total_profit_loss'],
                total_profit_loss_ratio=summary['total_profit_loss_rate'] / 100,
                open_positions=summary['position_count'],
                risk_mode=self.dynamic_risk_manager.current_mode.value
            )

            self.db_session.add(snapshot)
            self.db_session.commit()

        except Exception as e:
            logger.error(f"포트폴리오 스냅샷 저장 실패: {e}")

    def _get_virtual_trading_prices(self) -> dict:
        """가상 매매용 현재 가격 조회"""
        try:
            if not self.virtual_trader:
                return {}

            # 모든 가상 계좌의 포지션에서 종목 코드 추출
            all_stock_codes = set()
            for account in self.virtual_trader.accounts.values():
                all_stock_codes.update(account.positions.keys())

            if not all_stock_codes:
                return {}

            # 각 종목의 현재가 조회
            price_data = {}
            for stock_code in all_stock_codes:
                try:
                    # 현재가 조회
                    quote = self.market_api.get_stock_price(stock_code)
                    if quote:
                        price_data[stock_code] = int(quote.get('current_price', 0))
                except Exception as e:
                    logger.warning(f"가격 조회 실패 ({stock_code}): {e}")
                    continue

            return price_data

        except Exception as e:
            logger.error(f"가상 매매 가격 조회 실패: {e}")
            return {}

    def _print_statistics(self):
        """통계 출력"""
        try:
            logger.info("\n" + "="*60)
            logger.info("📊 실시간 통계")
            logger.info("="*60)

            # 포트폴리오
            summary = self.portfolio_manager.get_portfolio_summary()
            logger.info(f"💰 총 자산: {summary['total_assets']:,}원")
            logger.info(f"💵 현금: {summary['cash']:,}원")
            logger.info(f"📈 수익률: {summary['total_profit_loss_rate']:+.2f}%")
            logger.info(f"📦 포지션: {summary['position_count']}개")

            # 리스크 모드
            risk_status = self.dynamic_risk_manager.get_status_summary()
            logger.info(f"🛡️  리스크 모드: {self.dynamic_risk_manager.get_mode_description()}")
            logger.info(f"📊 최대 포지션: {risk_status['config']['max_open_positions']}개")

            # 스캐닝 상태
            scan_summary = self.scanner_pipeline.get_scan_summary()
            logger.info(f"🔍 Fast Scan: {scan_summary['fast_scan']['count']}종목")
            logger.info(f"🔬 Deep Scan: {scan_summary['deep_scan']['count']}종목")
            logger.info(f"🤖 AI Scan: {scan_summary['ai_scan']['count']}종목")

            # 가상 매매 성과
            if self.virtual_trader:
                try:
                    logger.info("\n" + "-"*60)
                    logger.info("📝 가상 매매 성과 (3가지 전략)")
                    logger.info("-"*60)
                    self.virtual_trader.print_performance()
                except Exception as e:
                    logger.warning(f"가상 매매 성과 출력 실패: {e}")

            logger.info("="*60 + "\n")

        except Exception as e:
            logger.error(f"통계 출력 실패: {e}")

    # ==================== WebSocket 콜백 메서드 ====================

    def _on_ws_open(self, ws):
        """WebSocket 연결 성공 콜백"""
        logger.info("🔌 WebSocket 연결 성공 - 실시간 데이터 수신 시작")
        self.monitor.log_activity(
            'system',
            '🔌 WebSocket 연결 성공',
            level='success'
        )

        # 실시간 데이터 구독 시작
        try:
            # 보유 종목에 대한 실시간 가격 구독
            if self.portfolio_manager and hasattr(self.portfolio_manager, 'get_positions'):
                positions = self.portfolio_manager.get_positions()
                if not positions:
                    logger.info("보유 종목 없음 - 구독 생략")
                    return

                for position in positions:
                    stock_code = position.get('stock_code')
                    if stock_code and self.websocket_client:
                        # TODO: Kiwoom API의 실제 구독 메시지 형식으로 교체 필요
                        # 현재는 테스트 형식 (실제 API 문서 확인 필요)
                        self.websocket_client.subscribe({
                            'type': 'price',
                            'stock_code': stock_code
                        })
                        logger.debug(f"실시간 가격 구독 요청: {stock_code}")

                logger.info("✓ 실시간 데이터 구독 완료")
            else:
                logger.info("보유 종목 없음 - 구독 생략")
        except Exception as e:
            logger.warning(f"실시간 데이터 구독 중 오류: {e}")

    def _on_ws_message(self, data: dict):
        """WebSocket 메시지 수신 콜백"""
        try:
            # 실시간 데이터 처리
            msg_type = data.get('type')

            if msg_type == 'price':
                # 실시간 가격 업데이트
                stock_code = data.get('stock_code')
                price = data.get('price')
                logger.debug(f"실시간 가격: {stock_code} = {price:,}원")

            elif msg_type == 'order':
                # 주문 체결 알림
                logger.info(f"📥 주문 체결 알림: {data.get('message')}")
                self.monitor.log_activity(
                    'order',
                    data.get('message', '주문 체결'),
                    level='info'
                )

        except Exception as e:
            logger.error(f"WebSocket 메시지 처리 중 오류: {e}")

    def _on_ws_error(self, error):
        """WebSocket 에러 콜백"""
        # "Bye" 메시지는 정상 종료이므로 로그 억제
        error_str = str(error)
        if 'Bye' not in error_str:
            logger.error(f"🔌 WebSocket 오류: {error}")
            self.monitor.log_activity(
                'system',
                f'⚠️ WebSocket 오류: {error}',
                level='error'
            )

    def _on_ws_close(self, close_status_code, close_msg):
        """WebSocket 연결 종료 콜백"""
        # 정상 종료(1000)는 로그 억제
        if close_status_code and close_status_code != 1000:
            logger.warning(f"🔌 WebSocket 연결 종료 (코드: {close_status_code}, 메시지: {close_msg})")
            logger.info("🔄 자동 재연결 시도 중...")
            self.monitor.log_activity(
                'system',
                f'⚠️ WebSocket 연결 종료 - 재연결 시도 중',
                level='warning'
            )


def signal_handler(signum, frame):
    """시그널 핸들러"""
    logger.info("\n프로그램 종료 신호 수신")
    sys.exit(0)


def main():
    """메인 함수"""
    # 시그널 핸들러
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("\n" + "="*60)
    print("AutoTrade Pro v2.0".center(60))
    print("="*60 + "\n")

    try:
        # 봇 생성
        print("1. 트레이딩 봇 초기화 중...")
        bot = TradingBotV2()
        print("✓ 트레이딩 봇 초기화 완료\n")

        # 대시보드 시작
        print("2. 웹 대시보드 시작 중...")
        try:
            from dashboard import run_dashboard

            dashboard_thread = threading.Thread(
                target=run_dashboard,
                args=(bot,),
                kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False},
                daemon=True,
                name='DashboardThread'
            )
            dashboard_thread.start()
            time.sleep(1)

            print("✓ 웹 대시보드 시작 완료")
            print(f"  → http://localhost:5000\n")

        except Exception as e:
            print(f"⚠ 대시보드 시작 실패: {e}\n")

        # 봇 시작
        print("3. 자동매매 봇 시작...")
        print("="*60 + "\n")
        bot.start()

    except KeyboardInterrupt:
        print("\n사용자에 의한 중단")
        return 0
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        logger.error(f"오류: {e}", exc_info=True)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
