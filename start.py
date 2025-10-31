"""
고급 자동매매 시스템 시작 스크립트
Advanced AI Trading System Launcher
"""

import sys
import argparse
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description='AI 자동매매 시스템',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 기본 모드 (기존 봇)
  python start.py

  # 고급 대시보드 실행
  python start.py --dashboard

  # 고급 대시보드 + AI Ensemble
  python start.py --dashboard --ai-ensemble

  # 백테스팅 실행
  python start.py --backtest

  # 모든 기능 활성화
  python start.py --dashboard --ai-ensemble --algo-orders --risk-analytics
        """
    )

    # 실행 모드
    parser.add_argument(
        '--mode',
        choices=['basic', 'advanced'],
        default='basic',
        help='실행 모드 (basic: 기본, advanced: 고급)'
    )

    # 대시보드
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='고급 대시보드 실행 (TradingView 스타일)'
    )

    parser.add_argument(
        '--dashboard-port',
        type=int,
        default=5000,
        help='대시보드 포트 (기본: 5000)'
    )

    # AI 기능
    parser.add_argument(
        '--ai-ensemble',
        action='store_true',
        help='Multi-AI Ensemble 활성화 (Gemini + GPT-4 + Claude)'
    )

    parser.add_argument(
        '--enable-gpt4',
        action='store_true',
        help='GPT-4 모델 활성화'
    )

    parser.add_argument(
        '--enable-claude',
        action='store_true',
        help='Claude 모델 활성화'
    )

    parser.add_argument(
        '--dl-prediction',
        action='store_true',
        help='딥러닝 가격 예측 활성화'
    )

    # 주문 실행
    parser.add_argument(
        '--algo-orders',
        action='store_true',
        help='알고리즘 주문 실행 활성화 (TWAP, VWAP, Iceberg)'
    )

    # 리스크 분석
    parser.add_argument(
        '--risk-analytics',
        action='store_true',
        help='고급 리스크 분석 활성화 (VaR, Monte Carlo)'
    )

    # 백테스팅
    parser.add_argument(
        '--backtest',
        action='store_true',
        help='백테스팅 모드로 실행'
    )

    parser.add_argument(
        '--backtest-start',
        type=str,
        help='백테스팅 시작일 (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--backtest-end',
        type=str,
        help='백테스팅 종료일 (YYYY-MM-DD)'
    )

    # 기타
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='실제 주문 없이 시뮬레이션만 실행'
    )

    args = parser.parse_args()

    # 설정 출력
    logger.info("=" * 70)
    logger.info("🚀 AI 자동매매 시스템 시작")
    logger.info("=" * 70)
    logger.info(f"실행 모드: {args.mode.upper()}")
    logger.info(f"대시보드: {'✓' if args.dashboard else '✗'}")
    logger.info(f"AI Ensemble: {'✓' if args.ai_ensemble else '✗'}")
    logger.info(f"알고리즘 주문: {'✓' if args.algo_orders else '✗'}")
    logger.info(f"리스크 분석: {'✓' if args.risk_analytics else '✗'}")
    logger.info(f"백테스팅: {'✓' if args.backtest else '✗'}")
    logger.info("=" * 70)

    # 백테스팅 모드
    if args.backtest:
        run_backtest(args)
        return

    # 일반 모드
    if args.mode == 'advanced' or args.dashboard or args.ai_ensemble:
        run_advanced_mode(args)
    else:
        run_basic_mode(args)


def run_basic_mode(args):
    """기본 모드 실행"""
    logger.info("📊 기본 모드로 실행 중...")

    from main import TradingBot
    from dashboard.dashboard import run_dashboard
    import threading

    # 봇 생성
    bot = TradingBot()

    # 기본 대시보드 시작 (백그라운드)
    dashboard_thread = threading.Thread(
        target=run_dashboard,
        args=(bot, '0.0.0.0', 5000),
        daemon=True
    )
    dashboard_thread.start()

    logger.info(f"✓ 대시보드 시작: http://localhost:5000")

    # 봇 실행
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("사용자 중단 요청")
        bot.stop()


def run_advanced_mode(args):
    """고급 모드 실행"""
    logger.info("🚀 고급 모드로 실행 중...")

    from main import TradingBot
    import threading

    # 봇 생성
    bot = TradingBot()

    # AI Ensemble 설정
    if args.ai_ensemble or args.enable_gpt4 or args.enable_claude:
        setup_ai_ensemble(bot, args)

    # 알고리즘 주문 설정
    if args.algo_orders:
        setup_algo_orders(bot)

    # 리스크 분석 설정
    if args.risk_analytics:
        setup_risk_analytics(bot)

    # 딥러닝 예측 설정
    if args.dl_prediction:
        setup_dl_prediction(bot)

    # 고급 대시보드 시작
    if args.dashboard:
        from dashboard.advanced_dashboard import run_advanced_dashboard

        dashboard_thread = threading.Thread(
            target=run_advanced_dashboard,
            args=(bot, '0.0.0.0', args.dashboard_port),
            daemon=True
        )
        dashboard_thread.start()

        logger.info(f"✓ 고급 대시보드 시작: http://localhost:{args.dashboard_port}")

    # 봇 실행
    try:
        if not args.dry_run:
            bot.run()
        else:
            logger.info("DRY RUN 모드 - 실제 주문 없이 시뮬레이션")
            bot.run()
    except KeyboardInterrupt:
        logger.info("사용자 중단 요청")
        bot.stop()


def setup_ai_ensemble(bot, args):
    """AI Ensemble 설정"""
    logger.info("🧠 AI Ensemble 설정 중...")

    try:
        from ai.ensemble_analyzer import EnsembleAnalyzer, VotingStrategy

        # Ensemble 분석기 생성
        ensemble = EnsembleAnalyzer(
            voting_strategy=VotingStrategy.WEIGHTED,
            enable_gpt4=args.enable_gpt4 or args.ai_ensemble,
            enable_claude=args.enable_claude or args.ai_ensemble
        )

        # 봇에 통합
        bot.analyzer = ensemble

        logger.info("✓ AI Ensemble 설정 완료")
        logger.info(f"  - 활성 모델 수: {len(ensemble.analyzers)}")

    except Exception as e:
        logger.error(f"AI Ensemble 설정 실패: {e}")
        logger.warning("기본 Gemini 분석기 사용")


def setup_algo_orders(bot):
    """알고리즘 주문 설정"""
    logger.info("🎯 알고리즘 주문 설정 중...")

    try:
        from api.algo_order_executor import AlgoOrderExecutor

        # Algo Executor 생성
        bot.algo_executor = AlgoOrderExecutor(
            bot.order_api,
            bot.market_api
        )

        logger.info("✓ 알고리즘 주문 설정 완료")
        logger.info("  - TWAP, VWAP, Iceberg, Adaptive 사용 가능")

    except Exception as e:
        logger.error(f"알고리즘 주문 설정 실패: {e}")


def setup_risk_analytics(bot):
    """리스크 분석 설정"""
    logger.info("📈 리스크 분석 설정 중...")

    try:
        from strategy.advanced_risk_analytics import AdvancedRiskAnalytics

        # Risk Analytics 생성
        bot.risk_analytics = AdvancedRiskAnalytics(
            confidence_level=0.95
        )

        logger.info("✓ 리스크 분석 설정 완료")
        logger.info("  - VaR, Sharpe, Sortino, Monte Carlo 사용 가능")

    except Exception as e:
        logger.error(f"리스크 분석 설정 실패: {e}")


def setup_dl_prediction(bot):
    """딥러닝 예측 설정"""
    logger.info("🤖 딥러닝 예측 설정 중...")

    try:
        from ai.deep_learning_predictor import DeepLearningPredictor

        # DL Predictor 생성
        bot.dl_predictor = DeepLearningPredictor(
            sequence_length=60,
            prediction_horizon=5
        )

        logger.info("✓ 딥러닝 예측 설정 완료")
        logger.info("  - LSTM, CNN, Transformer 모델 사용 가능")

    except Exception as e:
        logger.error(f"딥러닝 예측 설정 실패: {e}")


def run_backtest(args):
    """백테스팅 실행"""
    logger.info("🔬 백테스팅 모드 실행 중...")

    from datetime import datetime
    from backtesting import BacktestEngine, BacktestConfig

    # 날짜 파싱
    if args.backtest_start:
        start_date = datetime.strptime(args.backtest_start, '%Y-%m-%d')
    else:
        start_date = datetime(2023, 1, 1)

    if args.backtest_end:
        end_date = datetime.strptime(args.backtest_end, '%Y-%m-%d')
    else:
        end_date = datetime.now()

    logger.info(f"백테스팅 기간: {start_date.date()} ~ {end_date.date()}")

    # 백테스트 설정
    config = BacktestConfig(
        initial_capital=10000000,
        commission_rate=0.0015,
        slippage_rate=0.001,
        position_size=0.20,
        max_positions=5
    )

    # 엔진 생성
    engine = BacktestEngine(config)

    logger.info("백테스팅 데이터 로딩 중...")
    # TODO: 실제 데이터 로딩 로직 구현 필요
    logger.warning("백테스팅 기능은 historical_data 준비 후 사용 가능합니다")
    logger.info("자세한 사항은 UPGRADE_GUIDE.md를 참조하세요")


if __name__ == '__main__':
    main()
