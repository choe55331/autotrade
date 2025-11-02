"""
research/scan_strategies.py
3가지 시장 스캔 전략 구현
"""
import time
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime

from utils.logger_new import get_logger
from utils.stock_filter import is_etf
from research.scanner_pipeline import StockCandidate

logger = get_logger()


class ScanStrategy(ABC):
    """스캔 전략 추상 클래스"""

    def __init__(self, name: str, market_api, screener, ai_analyzer=None):
        """
        Args:
            name: 전략 이름
            market_api: MarketAPI 인스턴스
            screener: Screener 인스턴스
            ai_analyzer: AI Analyzer 인스턴스 (선택적)
        """
        self.name = name
        self.market_api = market_api
        self.screener = screener
        self.ai_analyzer = ai_analyzer
        self.last_scan_time = 0
        self.scan_results = []

    @abstractmethod
    def scan(self) -> List[StockCandidate]:
        """
        시장 스캔 실행

        Returns:
            매수 후보 종목 리스트
        """
        pass

    @abstractmethod
    def get_filter_conditions(self) -> Dict[str, Any]:
        """
        필터링 조건 반환

        Returns:
            필터링 조건 딕셔너리
        """
        pass

    def get_name(self) -> str:
        """전략 이름 반환"""
        return self.name


class VolumeBasedStrategy(ScanStrategy):
    """거래량 기반 스캔 전략"""

    def __init__(self, market_api, screener, config: Dict[str, Any] = None):
        super().__init__("거래량 급등", market_api, screener)
        self.config = config or {}

    def get_filter_conditions(self) -> Dict[str, Any]:
        """거래량 기반 필터링 조건"""
        return {
            'min_price': self.config.get('min_price', 1000),
            'max_price': self.config.get('max_price', 1000000),
            'min_volume': self.config.get('min_volume', 100000),
            'min_rate': self.config.get('min_rate', 1.0),
            'max_rate': self.config.get('max_rate', 15.0),
        }

    def scan(self) -> List[StockCandidate]:
        """
        거래량 급등 종목 스캔

        Returns:
            매수 후보 종목 리스트
        """
        logger.info(f"🔍 [{self.name}] 스캔 시작")
        print(f"\n{'='*60}")
        print(f"🔍 전략 1: {self.name} 스캔")
        print(f"{'='*60}")

        try:
            start_time = time.time()

            # 거래량 순위 조회
            conditions = self.get_filter_conditions()
            candidates = self.screener.screen_combined(
                min_volume=conditions['min_volume'],
                min_price=conditions['min_price'],
                max_price=conditions['max_price'],
                min_rate=conditions['min_rate'],
                max_rate=conditions['max_rate'],
                market='ALL',
                limit=100
            )

            # StockCandidate 객체로 변환 (ETF 제외)
            stock_candidates = []
            etf_count = 0
            for stock in candidates[:40]:  # ETF 제외 고려하여 더 많이 조회
                # ETF 필터링
                if is_etf(stock['name'], stock['code']):
                    etf_count += 1
                    continue

                candidate = StockCandidate(
                    code=stock['code'],
                    name=stock['name'],
                    price=stock['current_price'],
                    volume=stock['volume'],
                    rate=stock['change_rate']
                )

                # 간단한 점수 계산
                score = 0.0
                trading_value = candidate.price * candidate.volume
                if trading_value > 1_000_000_000:
                    score += 40
                elif trading_value > 500_000_000:
                    score += 30

                if 2.0 <= candidate.rate <= 10.0:
                    score += 30

                if candidate.volume > 1_000_000:
                    score += 30

                candidate.fast_scan_score = score
                candidate.fast_scan_time = datetime.now()
                stock_candidates.append(candidate)

                if len(stock_candidates) >= 20:  # 20개 확보되면 종료
                    break

            if etf_count > 0:
                print(f"   ℹ️  ETF/지수 {etf_count}개 제외됨")

            # 점수 기준 정렬
            stock_candidates.sort(key=lambda x: x.fast_scan_score, reverse=True)

            elapsed = time.time() - start_time
            print(f"✅ [{self.name}] 스캔 완료: {len(stock_candidates)}개 후보 (소요: {elapsed:.2f}초)")
            logger.info(f"✅ [{self.name}] 스캔 완료: {len(stock_candidates)}개 후보")

            self.scan_results = stock_candidates
            self.last_scan_time = time.time()

            return stock_candidates[:5]  # 상위 5개만 반환

        except Exception as e:
            logger.error(f"❌ [{self.name}] 스캔 실패: {e}", exc_info=True)
            print(f"❌ [{self.name}] 스캔 실패: {e}")
            return []


class PriceChangeStrategy(ScanStrategy):
    """상승률 기반 스캔 전략"""

    def __init__(self, market_api, screener, config: Dict[str, Any] = None):
        super().__init__("상승률 순위", market_api, screener)
        self.config = config or {}

    def get_filter_conditions(self) -> Dict[str, Any]:
        """상승률 기반 필터링 조건"""
        return {
            'min_price': self.config.get('min_price', 1000),
            'max_price': self.config.get('max_price', 500000),
            'min_volume': self.config.get('min_volume', 50000),
            'min_rate': self.config.get('min_rate', 3.0),
            'max_rate': self.config.get('max_rate', 29.9),  # 상한가 제외
        }

    def scan(self) -> List[StockCandidate]:
        """
        상승률 상위 종목 스캔

        Returns:
            매수 후보 종목 리스트
        """
        logger.info(f"📈 [{self.name}] 스캔 시작")
        print(f"\n{'='*60}")
        print(f"📈 전략 2: {self.name} 스캔")
        print(f"{'='*60}")

        try:
            start_time = time.time()

            # 상승률 순위 조회
            rank_list = self.market_api.get_price_change_rank(
                market='ALL',
                sort='rise',
                limit=100
            )

            if not rank_list:
                print(f"⚠️  [{self.name}] 데이터 없음 (주말/비거래시간)")
                return []

            # 필터링 조건
            conditions = self.get_filter_conditions()

            # 필터링 및 StockCandidate 변환 (ETF 제외)
            stock_candidates = []
            etf_count = 0
            for stock in rank_list:
                # ETF 필터링
                if is_etf(stock['name'], stock['code']):
                    etf_count += 1
                    continue

                # 조건 체크
                if not (conditions['min_price'] <= stock['price'] <= conditions['max_price']):
                    continue
                if stock['volume'] < conditions['min_volume']:
                    continue
                if not (conditions['min_rate'] <= stock['change_rate'] <= conditions['max_rate']):
                    continue

                candidate = StockCandidate(
                    code=stock['code'],
                    name=stock['name'],
                    price=stock['price'],
                    volume=stock['volume'],
                    rate=stock['change_rate']
                )

                # 상승률 기반 점수
                score = 0.0
                if candidate.rate >= 10.0:
                    score += 50
                elif candidate.rate >= 5.0:
                    score += 35
                elif candidate.rate >= 3.0:
                    score += 20

                if candidate.volume > 500_000:
                    score += 30

                if 5000 <= candidate.price <= 100000:
                    score += 20

                candidate.fast_scan_score = score
                candidate.fast_scan_time = datetime.now()
                stock_candidates.append(candidate)

            if etf_count > 0:
                print(f"   ℹ️  ETF/지수 {etf_count}개 제외됨")

            # 점수 기준 정렬
            stock_candidates.sort(key=lambda x: x.fast_scan_score, reverse=True)

            elapsed = time.time() - start_time
            print(f"✅ [{self.name}] 스캔 완료: {len(stock_candidates)}개 후보 (소요: {elapsed:.2f}초)")
            logger.info(f"✅ [{self.name}] 스캔 완료: {len(stock_candidates)}개 후보")

            self.scan_results = stock_candidates
            self.last_scan_time = time.time()

            return stock_candidates[:5]  # 상위 5개만 반환

        except Exception as e:
            logger.error(f"❌ [{self.name}] 스캔 실패: {e}", exc_info=True)
            print(f"❌ [{self.name}] 스캔 실패: {e}")
            return []


class AIDrivenStrategy(ScanStrategy):
    """AI 주도 스캔 전략"""

    def __init__(self, market_api, screener, ai_analyzer, config: Dict[str, Any] = None):
        super().__init__("AI 주도 탐색", market_api, screener, ai_analyzer)
        self.config = config or {}

    def get_filter_conditions(self) -> Dict[str, Any]:
        """
        AI에게 필터링 조건 질의

        Returns:
            AI가 제안한 필터링 조건
        """
        # TODO: AI에게 시장 상황 분석 후 최적 조건 질의
        # 현재는 기본값 반환
        return {
            'min_price': 5000,
            'max_price': 200000,
            'min_volume': 200000,
            'min_rate': 2.0,
            'max_rate': 20.0,
        }

    def scan(self) -> List[StockCandidate]:
        """
        AI 주도 시장 스캔

        Returns:
            매수 후보 종목 리스트
        """
        logger.info(f"🤖 [{self.name}] 스캔 시작")
        print(f"\n{'='*60}")
        print(f"🤖 전략 3: {self.name} 스캔")
        print(f"{'='*60}")

        try:
            start_time = time.time()

            # TODO: AI에게 스캔 전략 질의
            print(f"    🤖 AI에게 스캔 전략 질의 중...")
            print(f"    ℹ️  현재는 기본 전략 사용 (향후 AI 자기강화 학습 적용)")

            # 현재는 거래량 + 상승률 혼합 전략
            conditions = self.get_filter_conditions()

            candidates = self.screener.screen_combined(
                min_volume=conditions['min_volume'],
                min_price=conditions['min_price'],
                max_price=conditions['max_price'],
                min_rate=conditions['min_rate'],
                max_rate=conditions['max_rate'],
                market='ALL',
                limit=100
            )

            # StockCandidate 변환 (ETF 제외)
            stock_candidates = []
            etf_count = 0
            for stock in candidates[:40]:  # ETF 제외 고려
                # ETF 필터링
                if is_etf(stock['name'], stock['code']):
                    etf_count += 1
                    continue

                candidate = StockCandidate(
                    code=stock['code'],
                    name=stock['name'],
                    price=stock['current_price'],
                    volume=stock['volume'],
                    rate=stock['change_rate']
                )

                # AI 추천 점수 (향후 강화학습 적용)
                score = 50.0  # 기본 점수
                candidate.fast_scan_score = score
                candidate.fast_scan_time = datetime.now()
                stock_candidates.append(candidate)

                if len(stock_candidates) >= 20:
                    break

            if etf_count > 0:
                print(f"   ℹ️  ETF/지수 {etf_count}개 제외됨")

            elapsed = time.time() - start_time
            print(f"✅ [{self.name}] 스캔 완료: {len(stock_candidates)}개 후보 (소요: {elapsed:.2f}초)")
            logger.info(f"✅ [{self.name}] 스캔 완료: {len(stock_candidates)}개 후보")

            self.scan_results = stock_candidates
            self.last_scan_time = time.time()

            return stock_candidates[:5]  # 상위 5개만 반환

        except Exception as e:
            logger.error(f"❌ [{self.name}] 스캔 실패: {e}", exc_info=True)
            print(f"❌ [{self.name}] 스캔 실패: {e}")
            return []
