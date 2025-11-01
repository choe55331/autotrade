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
from research.scanner_pipeline import ScannerPipeline
from strategy.scoring_system import ScoringSystem
from strategy.dynamic_risk_manager import DynamicRiskManager
from strategy import PortfolioManager
from ai import get_analyzer
from utils.activity_monitor import get_monitor

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
        self.scanner_pipeline = None
        self.scoring_system = None
        self.dynamic_risk_manager = None

        # 기존 시스템
        self.portfolio_manager = None
        self.analyzer = None

        # 활동 모니터
        self.monitor = get_monitor()

        # 데이터베이스 세션
        self.db_session = None

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
                # 설정에서 WebSocket URL과 토큰 가져오기
                from config import get_config
                config = get_config()

                # WebSocket 설정이 있으면 연결
                ws_url = getattr(config, 'websocket_url', None)
                if ws_url and self.client.token:
                    self.websocket_client = WebSocketClient(
                        url=ws_url,
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

            # 4. AI 분석기
            logger.info("🤖 AI 분석기 초기화 중...")
            try:
                self.analyzer = get_analyzer('gemini')
                if self.analyzer.initialize():
                    logger.info("✓ Gemini AI 분석기 초기화 완료")
                else:
                    logger.warning("Gemini AI 초기화 실패, Mock 분석기로 전환")
                    self.analyzer = get_analyzer('mock')
                    self.analyzer.initialize()
            except Exception as e:
                logger.warning(f"AI 분석기 초기화 실패: {e}, Mock 분석기 사용")
                self.analyzer = get_analyzer('mock')
                self.analyzer.initialize()

            # 5. 3단계 스캐닝 파이프라인 (신규)
            logger.info("🔍 3단계 스캐닝 파이프라인 초기화 중...")
            screener = Screener(self.client)
            self.scanner_pipeline = ScannerPipeline(
                market_api=self.market_api,
                screener=screener,
                ai_analyzer=self.analyzer
            )
            logger.info("✓ 3단계 스캐닝 파이프라인 초기화 완료")

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

            # 9. 제어 파일
            self._initialize_control_file()

            # 10. 이전 상태 복원
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

    def start(self):
        """봇 시작"""
        if not self.is_initialized:
            logger.error("봇이 초기화되지 않았습니다")
            return

        logger.info("="*60)
        logger.info("🚀 AutoTrade Pro v2.0 실행 시작")
        logger.info("="*60)

        self.is_running = True

        try:
            self._main_loop()
        except KeyboardInterrupt:
            logger.info("사용자에 의한 중단")
        except Exception as e:
            logger.error(f"메인 루프 오류: {e}", exc_info=True)
        finally:
            self.stop()

    def stop(self):
        """봇 정지"""
        logger.info("AutoTrade Pro v2.0 종료 중...")
        self.is_running = False

        if self.db_session:
            self.db_session.close()

        if self.client:
            self.client.close()

        logger.info("✅ AutoTrade Pro v2.0 종료 완료")

    def _main_loop(self):
        """메인 루프"""
        cycle_count = 0
        # Backward compatibility: handle both Pydantic (object) and old config (dict)
        if hasattr(self.config.main_cycle, 'sleep_seconds'):
            sleep_seconds = self.config.main_cycle.sleep_seconds
        else:
            sleep_seconds = self.config.main_cycle.get('sleep_seconds', 60)

        while self.is_running:
            cycle_count += 1
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 메인 사이클 #{cycle_count}")
            logger.info(f"{'='*60}")

            try:
                # 1. 제어 파일 확인
                self._read_control_file()

                if not self.is_running:
                    break

                # 2. 거래 시간 확인
                if not self._check_trading_hours():
                    time.sleep(sleep_seconds)
                    continue

                # 3. 계좌 정보 업데이트
                self._update_account_info()

                # 4. 매도 검토
                if not self.pause_sell:
                    self._check_sell_signals()

                # 5. 매수 검토 (3단계 스캐닝)
                if not self.pause_buy:
                    self._run_scanning_pipeline()

                # 6. 포트폴리오 스냅샷 저장
                self._save_portfolio_snapshot()

                # 7. 통계 출력
                self._print_statistics()

            except Exception as e:
                logger.error(f"메인 루프 오류: {e}", exc_info=True)

            logger.info(f"⏳ {sleep_seconds}초 대기...\n")
            time.sleep(sleep_seconds)

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

        if not market_status['is_trading_hours']:
            logger.info(f"⏸️  장 운영 시간 아님: {market_status['market_status']}")
            return False

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
        logger.info("🔍 3단계 스캐닝 파이프라인 시작")

        try:
            # 포지션 추가 가능 여부
            if not self.portfolio_manager.can_add_position():
                logger.info("⚠️  최대 포지션 수 도달")
                return

            # 동적 리스크 관리 확인
            current_positions = len(self.portfolio_manager.get_positions())
            if not self.dynamic_risk_manager.should_open_position(current_positions):
                logger.info("⚠️  리스크 관리: 포지션 진입 불가")
                return

            # 전체 파이프라인 실행
            final_candidates = self.scanner_pipeline.run_full_pipeline()

            if not final_candidates:
                logger.info("✅ 스캐닝 완료: 최종 후보 없음")
                return

            # 최종 후보 매수 처리
            for candidate in final_candidates[:3]:  # 최대 3개
                # 스코어링 시스템으로 추가 검증
                stock_data = candidate.to_dict()
                scoring_result = self.scoring_system.calculate_score(stock_data)

                logger.info(
                    f"📊 {candidate.name} 스코어: {scoring_result.total_score:.1f}/440 "
                    f"({scoring_result.percentage:.1f}%) - {self.scoring_system.get_grade(scoring_result.total_score)}등급"
                )

                # 최종 승인 조건
                if (candidate.ai_signal == 'buy' and
                    scoring_result.total_score >= 300 and  # 300점 이상
                    self.dynamic_risk_manager.should_approve_ai_signal(candidate.ai_score, candidate.ai_confidence)):

                    self._execute_buy(candidate, scoring_result)
                    break  # 1회 사이클에 1개만

        except Exception as e:
            logger.error(f"스캐닝 파이프라인 실패: {e}", exc_info=True)

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
                logger.info(f"🧪 테스트 모드: 종가 기준 매수 시뮬레이션")

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
                logger.info(f"🧪 테스트 모드: 종가 기준 매도 시뮬레이션")

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
        logger.error(f"🔌 WebSocket 오류: {error}")
        self.monitor.log_activity(
            'system',
            f'⚠️ WebSocket 오류: {error}',
            level='error'
        )

    def _on_ws_close(self, close_status_code, close_msg):
        """WebSocket 연결 종료 콜백"""
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
