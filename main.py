"""
main.py
자동매매 봇 메인 실행 파일
"""
import sys
import time
import signal
import logging
import threading
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 경로를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

# 설정 로드
from config import (
    validate_config,
    get_default_control_state,
    FILE_PATHS,
    MAIN_CYCLE_CONFIG,
)

# 유틸리티
from utils import setup_logger, FileHandler

# 핵심 모듈
from core import KiwoomRESTClient
from api import AccountAPI, MarketAPI, OrderAPI
from research import Research
from strategy import MomentumStrategy, PortfolioManager, RiskManager
from ai import get_analyzer

# 로거 설정
logger = logging.getLogger(__name__)


class TradingBot:
    """
    자동매매 봇 메인 클래스
    
    주요 기능:
    - 시장 모니터링
    - 종목 스크리닝
    - AI 분석
    - 자동 매매 (매수/매도)
    - 리스크 관리
    """
    
    def __init__(self):
        """봇 초기화"""
        logger.info("=" * 60)
        logger.info("자동매매 봇 초기화 시작")
        logger.info("=" * 60)
        
        # 상태
        self.is_running = False
        self.is_initialized = False
        self.pause_buy = False
        self.pause_sell = False
        
        # 제어 파일
        self.control_file = FILE_PATHS['CONTROL_FILE']
        self.state_file = FILE_PATHS['STRATEGY_STATE_FILE']
        
        # 컴포넌트
        self.client = None
        self.account_api = None
        self.market_api = None
        self.order_api = None
        self.research = None
        self.strategy = None
        self.portfolio_manager = None
        self.risk_manager = None
        self.analyzer = None
        
        # 초기화
        self._initialize_components()
        
        logger.info("자동매매 봇 초기화 완료")
    
    def _initialize_components(self):
        """컴포넌트 초기화"""
        try:
            # 1. 설정 검증
            logger.info("설정 검증 중...")
            validate_config()
            logger.info("✓ 설정 검증 완료")
            
            # 2. REST 클라이언트 초기화
            logger.info("REST API 클라이언트 초기화 중...")
            self.client = KiwoomRESTClient()
            logger.info("✓ REST API 클라이언트 초기화 완료")
            
            # 3. API 초기화
            logger.info("API 모듈 초기화 중...")
            self.account_api = AccountAPI(self.client)
            self.market_api = MarketAPI(self.client)
            self.order_api = OrderAPI(self.client)
            logger.info("✓ API 모듈 초기화 완료")
            
            # 4. Research 초기화
            logger.info("Research 모듈 초기화 중...")
            self.research = Research(self.client)
            logger.info("✓ Research 모듈 초기화 완료")
            
            # 5. 전략 초기화
            logger.info("매매 전략 초기화 중...")
            self.strategy = MomentumStrategy(self.client)
            logger.info("✓ 매매 전략 초기화 완료")
            
            # 6. 포트폴리오 관리자 초기화
            logger.info("포트폴리오 관리자 초기화 중...")
            self.portfolio_manager = PortfolioManager(self.client)
            logger.info("✓ 포트폴리오 관리자 초기화 완료")
            
            # 7. 리스크 관리자 초기화
            logger.info("리스크 관리자 초기화 중...")
            self.risk_manager = RiskManager()
            logger.info("✓ 리스크 관리자 초기화 완료")
            
            # 8. AI 분석기 초기화
            logger.info("AI 분석기 초기화 중...")
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
            
            # 9. 제어 파일 초기화
            self._initialize_control_file()
            
            # 10. 이전 상태 복원
            self._restore_state()
            
            self.is_initialized = True
            logger.info("✓ 모든 컴포넌트 초기화 완료")
            
        except Exception as e:
            logger.error(f"컴포넌트 초기화 실패: {e}", exc_info=True)
            raise
    
    def _initialize_control_file(self):
        """제어 파일 초기화"""
        if not self.control_file.exists():
            default_state = get_default_control_state()
            FileHandler.write_json(self.control_file, default_state)
            logger.info("제어 파일 생성 완료")
        else:
            logger.info("기존 제어 파일 로드")
    
    def _restore_state(self):
        """이전 상태 복원"""
        try:
            state = FileHandler.read_json(self.state_file)
            if state:
                logger.info("이전 상태 복원 중...")
                # 포지션 복원
                if 'positions' in state:
                    for stock_code, position in state['positions'].items():
                        self.strategy.add_position(
                            stock_code=stock_code,
                            quantity=position['quantity'],
                            purchase_price=position['purchase_price']
                        )
                logger.info(f"✓ {len(state.get('positions', {}))}개 포지션 복원 완료")
        except Exception as e:
            logger.warning(f"상태 복원 실패: {e}")
    
    def _save_state(self):
        """현재 상태 저장"""
        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'positions': self.strategy.get_all_positions(),
                'statistics': self.strategy.get_statistics(),
            }
            FileHandler.write_json(self.state_file, state)
        except Exception as e:
            logger.error(f"상태 저장 실패: {e}")
    
    # ==================== 메인 루프 ====================
    
    def start(self):
        """봇 시작"""
        if not self.is_initialized:
            logger.error("봇이 초기화되지 않았습니다")
            return
        
        if self.is_running:
            logger.warning("봇이 이미 실행 중입니다")
            return
        
        logger.info("=" * 60)
        logger.info("자동매매 봇 시작")
        logger.info("=" * 60)
        
        self.is_running = True
        self.strategy.start()
        
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
        logger.info("자동매매 봇 종료 중...")
        
        self.is_running = False
        self.strategy.stop()
        
        # 상태 저장
        self._save_state()
        
        # 클라이언트 종료
        if self.client:
            self.client.close()
        
        logger.info("자동매매 봇 종료 완료")
    
    def _main_loop(self):
        """메인 루프"""
        cycle_count = 0
        sleep_seconds = MAIN_CYCLE_CONFIG['SLEEP_SECONDS']
        
        while self.is_running:
            cycle_count += 1
            logger.info(f"\n{'='*60}")
            logger.info(f"메인 사이클 #{cycle_count} 시작")
            logger.info(f"{'='*60}")
            
            try:
                # 1. 제어 파일 읽기
                self._read_control_file()
                
                # 2. 실행 여부 확인
                if not self.is_running:
                    logger.info("봇 실행 중지됨")
                    break
                
                # 3. 장 운영 시간 확인
                if not self.research.is_market_open():
                    logger.info("장 운영 시간이 아닙니다. 대기 중...")
                    time.sleep(sleep_seconds)
                    continue
                
                # 4. 계좌 정보 업데이트
                self._update_account_info()
                
                # 5. 매도 검토 (보유 종목)
                if not self.pause_sell:
                    self._check_sell_signals()
                
                # 6. 매수 검토 (신규 종목)
                if not self.pause_buy:
                    self._check_buy_signals()
                
                # 7. 상태 저장
                self._save_state()
                
                # 8. 통계 출력
                self._print_statistics()
                
            except Exception as e:
                logger.error(f"메인 루프 오류: {e}", exc_info=True)
            
            # 대기
            logger.info(f"{sleep_seconds}초 대기 중...\n")
            time.sleep(sleep_seconds)
    
    def _read_control_file(self):
        """제어 파일 읽기"""
        try:
            control = FileHandler.read_json(self.control_file)
            if control:
                self.is_running = control.get('run', True)
                self.pause_buy = control.get('pause_buy', False)
                self.pause_sell = control.get('pause_sell', False)
        except Exception as e:
            logger.warning(f"제어 파일 읽기 실패: {e}")
    
    def _update_account_info(self):
        """계좌 정보 업데이트"""
        try:
            # 예수금 조회
            deposit = self.research.get_deposit()
            cash = int(deposit.get('ord_alow_amt', 0)) if deposit else 0
            
            # 보유 종목 조회
            holdings = self.research.get_holdings()
            
            # 포트폴리오 업데이트
            self.portfolio_manager.update_portfolio(holdings, cash)
            
            # 전략 포지션 업데이트
            for holding in holdings:
                stock_code = holding.get('stock_code')
                current_price = holding.get('current_price', 0)
                self.strategy.update_position(stock_code, current_price)
            
            logger.info(f"계좌 정보 업데이트: 현금 {cash:,}원, 보유 종목 {len(holdings)}개")
            
        except Exception as e:
            logger.error(f"계좌 정보 업데이트 실패: {e}")
    
    def _check_sell_signals(self):
        """매도 신호 검토"""
        logger.info("매도 신호 검토 중...")
        
        positions = self.strategy.get_all_positions()
        
        if not positions:
            logger.info("보유 종목 없음")
            return
        
        for stock_code, position in positions.items():
            try:
                # 매도 여부 판단
                should_sell = self.strategy.should_sell(stock_code, position)
                
                if should_sell:
                    self._execute_sell(stock_code, position)
                    
            except Exception as e:
                logger.error(f"{stock_code} 매도 검토 오류: {e}")
    
    def _check_buy_signals(self):
        """매수 신호 검토"""
        logger.info("매수 신호 검토 중...")

        # 포지션 추가 가능 여부 확인
        if not self.portfolio_manager.can_add_position():
            logger.info("최대 포지션 수 도달")
            return

        # 거래 가능 여부 확인
        can_trade, msg = self.risk_manager.can_trade()
        if not can_trade:
            logger.warning(f"거래 불가: {msg}")
            return

        try:
            # 종목 스크리닝
            # NOTE: 시세 API(순위 조회)가 아직 구현되지 않아 스크리닝이 작동하지 않음
            candidates = self.research.screen_stocks(
                min_volume=100000,
                min_price=1000,
                max_price=100000,
                min_rate=1.0,
                max_rate=15.0
            )

            if not candidates:
                logger.info("스크리닝 결과: 후보 종목 없음 (시세 API 미구현)")
                return

            logger.info(f"후보 종목 {len(candidates)}개 발견")

            # 상위 N개만 분석
            for candidate in candidates[:5]:
                stock_code = candidate.get('stock_code')

                # 이미 보유 중인지 확인
                if self.strategy.has_position(stock_code):
                    continue

                # 종목 분석
                analysis = self._analyze_stock(stock_code)

                if analysis and self.strategy.should_buy(stock_code, analysis):
                    self._execute_buy(stock_code, analysis)
                    break  # 1회 사이클에 1개만 매수

        except Exception as e:
            logger.warning(f"매수 신호 검토 건너뜀 (시세 API 미구현): {e}")
    
    def _analyze_stock(self, stock_code: str):
        """종목 분석"""
        try:
            # 종목 데이터 수집
            stock_data = self.research.get_stock_data_for_analysis(stock_code)
            
            if not stock_data:
                return None
            
            # AI 분석
            analysis = self.analyzer.analyze_stock(stock_data)
            
            logger.info(
                f"{stock_code} 분석 완료: "
                f"점수={analysis['score']:.2f}, "
                f"신호={analysis['signal']}, "
                f"신뢰도={analysis['confidence']}"
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"{stock_code} 분석 실패: {e}")
            return None
    
    def _execute_buy(self, stock_code: str, analysis: dict):
        """매수 실행"""
        try:
            logger.info(f"매수 실행: {stock_code}")
            
            # 현재가 조회
            price_info = self.research.get_current_price(stock_code)
            if not price_info:
                logger.error("현재가 조회 실패")
                return
            
            current_price = int(price_info.get('current_price', 0))
            
            # 가용 현금 조회
            available_cash = self.research.get_available_cash()
            
            # 매수 수량 계산
            quantity = self.strategy.calculate_position_size(
                stock_code,
                current_price,
                available_cash
            )
            
            if quantity == 0:
                logger.warning("매수 가능 수량 0")
                return
            
            # 주문 실행
            order_result = self.order_api.buy(
                stock_code=stock_code,
                quantity=quantity,
                price=current_price,
                order_type='00'  # 지정가
            )
            
            if order_result:
                order_no = order_result.get('order_no', '')
                logger.info(f"✓ 매수 주문 성공: {quantity}주 @ {current_price:,}원 (주문번호: {order_no})")
                
                # 전략에 포지션 추가
                self.strategy.add_position(
                    stock_code=stock_code,
                    quantity=quantity,
                    purchase_price=current_price,
                    order_id=order_no
                )
                
                # 거래 기록
                self.strategy.record_trade(
                    stock_code=stock_code,
                    action='buy',
                    quantity=quantity,
                    price=current_price
                )
                
        except Exception as e:
            logger.error(f"매수 실행 오류: {e}", exc_info=True)
    
    def _execute_sell(self, stock_code: str, position: dict):
        """매도 실행"""
        try:
            logger.info(f"매도 실행: {stock_code}")
            
            quantity = position.get('quantity', 0)
            current_price = int(position.get('current_price', 0))
            
            if quantity == 0:
                logger.warning("매도 수량 0")
                return
            
            # 주문 실행
            order_result = self.order_api.sell(
                stock_code=stock_code,
                quantity=quantity,
                price=current_price,
                order_type='00'  # 지정가
            )
            
            if order_result:
                order_no = order_result.get('order_no', '')
                profit_loss = position.get('profit_loss', 0)
                
                logger.info(
                    f"✓ 매도 주문 성공: {quantity}주 @ {current_price:,}원 "
                    f"(주문번호: {order_no}, 손익: {profit_loss:+,}원)"
                )
                
                # 전략에서 포지션 제거
                self.strategy.remove_position(stock_code)
                
                # 거래 기록
                self.strategy.record_trade(
                    stock_code=stock_code,
                    action='sell',
                    quantity=quantity,
                    price=current_price,
                    profit_loss=profit_loss
                )
                
                # 리스크 관리자 업데이트
                is_win = profit_loss > 0
                self.risk_manager.update_profit_loss(profit_loss, is_win)
                
        except Exception as e:
            logger.error(f"매도 실행 오류: {e}", exc_info=True)
    
    def _print_statistics(self):
        """통계 출력"""
        try:
            logger.info("\n" + "=" * 60)
            logger.info("📊 통계 정보")
            logger.info("=" * 60)
            
            # 전략 통계
            stats = self.strategy.get_statistics()
            logger.info(f"총 거래: {stats['total_trades']}회")
            logger.info(f"승률: {stats['win_rate']:.1f}%")
            logger.info(f"총 손익: {stats['total_profit_loss']:+,.0f}원")
            
            # 포트폴리오 요약
            summary = self.portfolio_manager.get_portfolio_summary()
            logger.info(f"총 자산: {summary['total_assets']:,}원")
            logger.info(f"수익률: {summary['total_profit_loss_rate']:+.2f}%")
            logger.info(f"포지션: {summary['position_count']}개")
            
            # 리스크 상태
            risk_status = self.risk_manager.get_status()
            logger.info(f"일일 손익: {risk_status['daily_profit_loss']:+,.0f}원")
            logger.info(f"연속 손실: {risk_status['consecutive_losses']}회")
            
            logger.info("=" * 60 + "\n")
            
        except Exception as e:
            logger.error(f"통계 출력 오류: {e}")


# ==================== 시그널 핸들러 ====================

def signal_handler(signum, frame):
    """시그널 핸들러 (Ctrl+C)"""
    logger.info("\n프로그램 종료 신호 수신")
    sys.exit(0)


# ==================== 메인 함수 ====================

def main():
    """메인 함수"""
    # 로거 설정 (가장 먼저 실행)
    setup_logger(
        name='trading_bot',
        log_file=Path('logs/bot.log'),
        level='INFO',
        console=True
    )

    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("\n" + "="*60)
    print("프로그램 시작".center(60))
    print("="*60 + "\n")
    logger.info("프로그램 시작")

    try:
        # 봇 생성
        print("1. 트레이딩 봇 초기화 중...")
        logger.info("트레이딩 봇 생성 시작")
        bot = TradingBot()
        print("✓ 트레이딩 봇 초기화 완료\n")

        # 대시보드 시작 (별도 스레드)
        print("2. 웹 대시보드 시작 중...")
        try:
            from dashboard import run_dashboard

            # Flask 워커 스레드로 실행
            dashboard_thread = threading.Thread(
                target=run_dashboard,
                args=(bot,),
                kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False},
                daemon=True,
                name='DashboardThread'
            )
            dashboard_thread.start()

            # 대시보드가 시작될 때까지 잠깐 대기
            time.sleep(1)

            print("✓ 웹 대시보드 시작 완료")
            print(f"  → http://127.0.0.1:5000")
            print(f"  → http://localhost:5000\n")
            logger.info("대시보드 시작: http://localhost:5000")

        except Exception as e:
            print(f"⚠ 대시보드 시작 실패: {e}\n")
            logger.warning(f"대시보드 시작 실패: {e}")

        # 봇 시작
        print("3. 자동매매 봇 시작 중...")
        print("="*60 + "\n")
        bot.start()

    except KeyboardInterrupt:
        print("\n\n사용자에 의한 중단")
        logger.info("사용자에 의한 중단")
        return 0

    except Exception as e:
        print(f"\n❌ 프로그램 오류: {e}")
        logger.error(f"프로그램 오류: {e}", exc_info=True)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())