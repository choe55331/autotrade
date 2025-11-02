"""
research/strategy_manager.py
스캔 전략 순환 관리자
"""
from typing import List, Dict, Any
from datetime import datetime

from utils.logger_new import get_logger
from research.scan_strategies import (
    ScanStrategy,
    VolumeBasedStrategy,
    PriceChangeStrategy,
    AIDrivenStrategy,
    StockCandidate
)

logger = get_logger()


class StrategyManager:
    """
    3가지 스캔 전략을 순환하면서 실행하는 매니저

    전략 순서:
    1. 거래량 급등
    2. 상승률 순위
    3. AI 주도 탐색
    """

    def __init__(self, market_api, screener, ai_analyzer, config: Dict[str, Any] = None):
        """
        Args:
            market_api: MarketAPI 인스턴스
            screener: Screener 인스턴스
            ai_analyzer: AI Analyzer 인스턴스
            config: 설정
        """
        self.market_api = market_api
        self.screener = screener
        self.ai_analyzer = ai_analyzer
        self.config = config or {}

        # 3가지 전략 초기화
        self.strategies: List[ScanStrategy] = [
            VolumeBasedStrategy(market_api, screener, config.get('volume_strategy', {})),
            PriceChangeStrategy(market_api, screener, config.get('price_change_strategy', {})),
            AIDrivenStrategy(market_api, screener, ai_analyzer, config.get('ai_strategy', {}))
        ]

        self.current_strategy_index = 0
        self.cycle_count = 0

        logger.info(f"✅ StrategyManager 초기화 완료 - {len(self.strategies)}개 전략 등록")
        print(f"\n{'='*60}")
        print(f"🎯 스캔 전략 매니저 초기화 완료")
        print(f"{'='*60}")
        for idx, strategy in enumerate(self.strategies, 1):
            print(f"  {idx}. {strategy.get_name()}")
        print(f"{'='*60}\n")

    def get_current_strategy(self) -> ScanStrategy:
        """현재 실행할 전략 반환"""
        return self.strategies[self.current_strategy_index]

    def next_strategy(self):
        """다음 전략으로 이동"""
        self.current_strategy_index = (self.current_strategy_index + 1) % len(self.strategies)
        if self.current_strategy_index == 0:
            self.cycle_count += 1

    def run_current_strategy(self) -> List[StockCandidate]:
        """
        현재 전략 실행

        Returns:
            매수 후보 종목 리스트
        """
        strategy = self.get_current_strategy()

        # 전략 실행
        candidates = strategy.scan()

        # 다음 전략으로 이동
        self.next_strategy()

        return candidates

    def get_strategy_summary(self) -> Dict[str, Any]:
        """전략 실행 요약"""
        return {
            'cycle_count': self.cycle_count,
            'current_strategy_index': self.current_strategy_index,
            'current_strategy_name': self.get_current_strategy().get_name(),
            'strategies': [
                {
                    'name': s.get_name(),
                    'last_scan_time': datetime.fromtimestamp(s.last_scan_time).isoformat() if s.last_scan_time else None,
                    'result_count': len(s.scan_results)
                }
                for s in self.strategies
            ]
        }
