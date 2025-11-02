"""
research/scanner_pipeline.py
3단계 스캐닝 파이프라인 (Fast → Deep → AI)
"""
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from utils.logger_new import get_logger

from config.config_manager import get_config


logger = get_logger()


@dataclass
class StockCandidate:
    """종목 후보 데이터 클래스"""

    code: str
    name: str
    price: int
    volume: int
    rate: float  # 등락률 (%)

    # Fast Scan 데이터
    fast_scan_score: float = 0.0
    fast_scan_time: Optional[datetime] = None

    # Deep Scan 데이터
    institutional_net_buy: int = 0
    foreign_net_buy: int = 0
    bid_ask_ratio: float = 0.0
    deep_scan_score: float = 0.0
    deep_scan_time: Optional[datetime] = None

    # AI Scan 데이터
    ai_score: float = 0.0
    ai_signal: str = ''
    ai_confidence: str = ''
    ai_reasons: List[str] = field(default_factory=list)
    ai_risks: List[str] = field(default_factory=list)
    ai_scan_time: Optional[datetime] = None

    # 최종 점수
    final_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'code': self.code,
            'name': self.name,
            'price': self.price,
            'volume': self.volume,
            'rate': self.rate,
            'fast_scan_score': self.fast_scan_score,
            'institutional_net_buy': self.institutional_net_buy,
            'foreign_net_buy': self.foreign_net_buy,
            'deep_scan_score': self.deep_scan_score,
            'ai_score': self.ai_score,
            'ai_signal': self.ai_signal,
            'ai_confidence': self.ai_confidence,
            'ai_reasons': self.ai_reasons,
            'ai_risks': self.ai_risks,
            'final_score': self.final_score,
        }


class ScannerPipeline:
    """3단계 스캐닝 파이프라인"""

    def __init__(
        self,
        market_api,
        screener,
        ai_analyzer,
        scoring_system=None
    ):
        """
        초기화

        Args:
            market_api: 시장 데이터 API
            screener: 종목 스크리너
            ai_analyzer: AI 분석기
            scoring_system: 스코어링 시스템 (선택)
        """
        self.market_api = market_api
        self.screener = screener
        self.ai_analyzer = ai_analyzer
        self.scoring_system = scoring_system

        # 설정 로드
        self.config = get_config()
        self.scan_config = self.config.scanning

        # 스캔 간격
        self.fast_scan_interval = self.scan_config.get('fast_scan', {}).get('interval', 10)
        self.deep_scan_interval = self.scan_config.get('deep_scan', {}).get('interval', 60)
        self.ai_scan_interval = self.scan_config.get('ai_scan', {}).get('interval', 300)

        # 최대 후보 수
        self.fast_max_candidates = self.scan_config.get('fast_scan', {}).get('max_candidates', 50)
        self.deep_max_candidates = self.scan_config.get('deep_scan', {}).get('max_candidates', 20)
        self.ai_max_candidates = self.scan_config.get('ai_scan', {}).get('max_candidates', 5)

        # 스캔 상태
        self.last_fast_scan = 0
        self.last_deep_scan = 0
        self.last_ai_scan = 0

        # 후보 캐시
        self.fast_scan_results: List[StockCandidate] = []
        self.deep_scan_results: List[StockCandidate] = []
        self.ai_scan_results: List[StockCandidate] = []

        logger.info("🔍 3단계 스캐닝 파이프라인 초기화 완료")

    def should_run_fast_scan(self) -> bool:
        """Fast Scan 실행 여부 확인"""
        return time.time() - self.last_fast_scan >= self.fast_scan_interval

    def should_run_deep_scan(self) -> bool:
        """Deep Scan 실행 여부 확인"""
        return time.time() - self.last_deep_scan >= self.deep_scan_interval

    def should_run_ai_scan(self) -> bool:
        """AI Scan 실행 여부 확인"""
        return time.time() - self.last_ai_scan >= self.ai_scan_interval

    def run_fast_scan(self) -> List[StockCandidate]:
        """
        Fast Scan (10초 주기)
        - 거래량, 가격, 등락률 기본 필터링
        - 목표: 50종목 선정

        Returns:
            선정된 종목 리스트
        """
        logger.info("⚡ Fast Scan 시작...")
        start_time = time.time()

        try:
            # 설정 로드
            fast_config = self.scan_config.get('fast_scan', {})
            filters = fast_config.get('filters', {})

            # 기본 필터로 종목 스크리닝
            candidates = self.screener.screen_stocks(
                min_price=filters.get('min_price', 1000),
                max_price=filters.get('max_price', 1000000),
                min_volume=filters.get('min_volume', 100000),
                min_rate=filters.get('min_rate', 1.0),
                max_rate=filters.get('max_rate', 15.0),
                min_market_cap=filters.get('min_market_cap', 0),
            )

            # 거래량 기준 정렬
            candidates = sorted(
                candidates,
                key=lambda x: x.get('volume', 0) * x.get('price', 0),  # 거래대금
                reverse=True
            )

            # 최대 개수 제한
            candidates = candidates[:self.fast_max_candidates]

            # StockCandidate 객체로 변환
            scan_time = datetime.now()
            stock_candidates = []

            for stock in candidates:
                candidate = StockCandidate(
                    code=stock['code'],
                    name=stock['name'],
                    price=stock['price'],
                    volume=stock['volume'],
                    rate=stock['rate'],
                    fast_scan_time=scan_time,
                )

                # Fast Scan 점수 계산 (간단한 거래대금 기준)
                candidate.fast_scan_score = self._calculate_fast_score(candidate)
                stock_candidates.append(candidate)

            # 결과 저장
            self.fast_scan_results = stock_candidates
            self.last_fast_scan = time.time()

            elapsed = time.time() - start_time
            logger.info(
                f"⚡ Fast Scan 완료: {len(stock_candidates)}종목 선정 "
                f"(소요시간: {elapsed:.2f}초)"
            )

            return stock_candidates

        except Exception as e:
            logger.error(f"Fast Scan 실패: {e}", exc_info=True)
            return []

    def _calculate_fast_score(self, candidate: StockCandidate) -> float:
        """
        Fast Scan 점수 계산

        Args:
            candidate: 종목 후보

        Returns:
            점수 (0~100)
        """
        score = 0.0

        # 거래대금 점수 (40점)
        trading_value = candidate.price * candidate.volume
        if trading_value > 1_000_000_000:  # 10억 이상
            score += 40
        elif trading_value > 500_000_000:  # 5억 이상
            score += 30
        elif trading_value > 100_000_000:  # 1억 이상
            score += 20

        # 등락률 점수 (30점)
        if 2.0 <= candidate.rate <= 10.0:
            score += 30
        elif 1.0 <= candidate.rate <= 15.0:
            score += 20

        # 거래량 점수 (30점)
        if candidate.volume > 1_000_000:
            score += 30
        elif candidate.volume > 500_000:
            score += 20
        elif candidate.volume > 100_000:
            score += 10

        return score

    def run_deep_scan(self, candidates: Optional[List[StockCandidate]] = None) -> List[StockCandidate]:
        """
        Deep Scan (1분 주기)
        - 기관/외국인 매매 흐름 분석
        - 호가 강도 분석
        - 목표: 20종목 선정

        Args:
            candidates: 분석할 종목 리스트 (None이면 Fast Scan 결과 사용)

        Returns:
            선정된 종목 리스트
        """
        logger.info("🔬 Deep Scan 시작...")
        start_time = time.time()

        try:
            if candidates is None:
                candidates = self.fast_scan_results

            if not candidates:
                logger.warning("Deep Scan 대상 종목 없음")
                return []

            deep_config = self.scan_config.get('deep_scan', {})
            scan_time = datetime.now()

            # 각 종목에 대해 심층 분석
            for candidate in candidates:
                try:
                    # 기관/외국인 매매 데이터 조회
                    investor_data = self.market_api.get_investor_data(candidate.code)

                    if investor_data:
                        candidate.institutional_net_buy = investor_data.get('기관_순매수', 0)
                        candidate.foreign_net_buy = investor_data.get('외국인_순매수', 0)

                    # 호가 데이터 조회
                    bid_ask_data = self.market_api.get_bid_ask(candidate.code)

                    if bid_ask_data:
                        bid_total = bid_ask_data.get('매수_총잔량', 1)
                        ask_total = bid_ask_data.get('매도_총잔량', 1)
                        candidate.bid_ask_ratio = bid_total / ask_total if ask_total > 0 else 0

                    # Deep Scan 점수 계산
                    candidate.deep_scan_score = self._calculate_deep_score(candidate)
                    candidate.deep_scan_time = scan_time

                    time.sleep(0.1)  # API 호출 간격

                except Exception as e:
                    logger.error(f"종목 {candidate.code} Deep Scan 실패: {e}")
                    continue

            # 점수 기준 정렬
            candidates = sorted(
                candidates,
                key=lambda x: x.deep_scan_score,
                reverse=True
            )

            # 필터링: 최소 기관 매수 조건
            min_institutional_buy = deep_config.get('min_institutional_net_buy', 10_000_000)
            candidates = [
                c for c in candidates
                if c.institutional_net_buy >= min_institutional_buy or c.foreign_net_buy >= 5_000_000
            ]

            # 최대 개수 제한
            candidates = candidates[:self.deep_max_candidates]

            # 결과 저장
            self.deep_scan_results = candidates
            self.last_deep_scan = time.time()

            elapsed = time.time() - start_time
            logger.info(
                f"🔬 Deep Scan 완료: {len(candidates)}종목 선정 "
                f"(소요시간: {elapsed:.2f}초)"
            )

            return candidates

        except Exception as e:
            logger.error(f"Deep Scan 실패: {e}", exc_info=True)
            return []

    def _calculate_deep_score(self, candidate: StockCandidate) -> float:
        """
        Deep Scan 점수 계산

        Args:
            candidate: 종목 후보

        Returns:
            점수 (0~100)
        """
        score = candidate.fast_scan_score  # Fast Scan 점수 승계

        # 기관 순매수 점수 (30점)
        if candidate.institutional_net_buy > 50_000_000:  # 5천만원 이상
            score += 30
        elif candidate.institutional_net_buy > 20_000_000:  # 2천만원 이상
            score += 20
        elif candidate.institutional_net_buy > 10_000_000:  # 1천만원 이상
            score += 10

        # 외국인 순매수 점수 (20점)
        if candidate.foreign_net_buy > 20_000_000:
            score += 20
        elif candidate.foreign_net_buy > 10_000_000:
            score += 15
        elif candidate.foreign_net_buy > 5_000_000:
            score += 10

        # 호가 강도 점수 (20점)
        if candidate.bid_ask_ratio > 1.5:
            score += 20
        elif candidate.bid_ask_ratio > 1.2:
            score += 15
        elif candidate.bid_ask_ratio > 1.0:
            score += 10

        return score

    def run_ai_scan(self, candidates: Optional[List[StockCandidate]] = None) -> List[StockCandidate]:
        """
        AI Scan (5분 주기)
        - AI 분석을 통한 최종 매수 추천
        - 목표: 5종목 선정

        Args:
            candidates: 분석할 종목 리스트 (None이면 Deep Scan 결과 사용)

        Returns:
            선정된 종목 리스트
        """
        logger.info("🤖 AI Scan 시작...")
        start_time = time.time()

        try:
            if candidates is None:
                candidates = self.deep_scan_results

            if not candidates:
                logger.warning("AI Scan 대상 종목 없음")
                return []

            ai_config = self.scan_config.get('ai_scan', {})
            scan_time = datetime.now()
            min_score = ai_config.get('min_analysis_score', 7.0)
            min_confidence = ai_config.get('min_confidence', 'Medium')

            # AI 분석 수행
            ai_approved = []

            for candidate in candidates:
                try:
                    logger.info(f"🤖 AI 분석 중: {candidate.name} ({candidate.code})")

                    # 종목 데이터 준비
                    stock_data = {
                        'code': candidate.code,
                        'name': candidate.name,
                        'price': candidate.price,
                        'volume': candidate.volume,
                        'rate': candidate.rate,
                        'institutional_net_buy': candidate.institutional_net_buy,
                        'foreign_net_buy': candidate.foreign_net_buy,
                        'bid_ask_ratio': candidate.bid_ask_ratio,
                    }

                    # AI 분석 실행
                    analysis = self.ai_analyzer.analyze_stock(stock_data)

                    # 결과 저장
                    candidate.ai_score = analysis.get('score', 0)
                    candidate.ai_signal = analysis.get('signal', 'hold')
                    candidate.ai_confidence = analysis.get('confidence', 'Low')
                    candidate.ai_reasons = analysis.get('reasons', [])
                    candidate.ai_risks = analysis.get('risks', [])
                    candidate.ai_scan_time = scan_time

                    # 최종 점수 계산 (Deep Scan 70% + AI 30%)
                    candidate.final_score = (
                        candidate.deep_scan_score * 0.7 +
                        candidate.ai_score * 10 * 0.3  # AI 점수는 0~10이므로 10을 곱함
                    )

                    # AI 승인 조건 확인
                    confidence_level = {'Low': 1, 'Medium': 2, 'High': 3}
                    min_conf_level = confidence_level.get(min_confidence, 2)
                    ai_conf_level = confidence_level.get(candidate.ai_confidence, 1)

                    if (
                        candidate.ai_signal == 'buy' and
                        candidate.ai_score >= min_score and
                        ai_conf_level >= min_conf_level
                    ):
                        ai_approved.append(candidate)
                        logger.info(
                            f"✅ AI 승인: {candidate.name} "
                            f"(점수: {candidate.ai_score:.1f}, 신뢰도: {candidate.ai_confidence})"
                        )
                    else:
                        logger.info(
                            f"❌ AI 거부: {candidate.name} "
                            f"(점수: {candidate.ai_score:.1f}, 신뢰도: {candidate.ai_confidence})"
                        )

                    time.sleep(1)  # AI API 호출 간격

                except Exception as e:
                    logger.error(f"종목 {candidate.code} AI 분석 실패: {e}")
                    continue

            # 최종 점수 기준 정렬
            ai_approved = sorted(
                ai_approved,
                key=lambda x: x.final_score,
                reverse=True
            )

            # 최대 개수 제한
            ai_approved = ai_approved[:self.ai_max_candidates]

            # 결과 저장
            self.ai_scan_results = ai_approved
            self.last_ai_scan = time.time()

            elapsed = time.time() - start_time
            logger.info(
                f"🤖 AI Scan 완료: {len(ai_approved)}종목 선정 "
                f"(소요시간: {elapsed:.2f}초)"
            )

            return ai_approved

        except Exception as e:
            logger.error(f"AI Scan 실패: {e}", exc_info=True)
            return []

    def run_full_pipeline(self) -> List[StockCandidate]:
        """
        전체 파이프라인 실행 (필요한 단계만 실행)

        Returns:
            최종 AI 승인 종목 리스트
        """
        logger.info("🚀 스캐닝 파이프라인 실행 시작")

        # Fast Scan
        if self.should_run_fast_scan():
            self.run_fast_scan()

        # Deep Scan
        if self.should_run_deep_scan() and self.fast_scan_results:
            self.run_deep_scan()

        # AI Scan
        if self.should_run_ai_scan() and self.deep_scan_results:
            self.run_ai_scan()

        logger.info(
            f"✅ 스캐닝 파이프라인 완료: "
            f"Fast={len(self.fast_scan_results)}, "
            f"Deep={len(self.deep_scan_results)}, "
            f"AI={len(self.ai_scan_results)}"
        )

        return self.ai_scan_results

    def get_scan_summary(self) -> Dict[str, Any]:
        """스캔 결과 요약"""
        return {
            'fast_scan': {
                'count': len(self.fast_scan_results),
                'last_run': datetime.fromtimestamp(self.last_fast_scan).isoformat() if self.last_fast_scan else None,
            },
            'deep_scan': {
                'count': len(self.deep_scan_results),
                'last_run': datetime.fromtimestamp(self.last_deep_scan).isoformat() if self.last_deep_scan else None,
            },
            'ai_scan': {
                'count': len(self.ai_scan_results),
                'last_run': datetime.fromtimestamp(self.last_ai_scan).isoformat() if self.last_ai_scan else None,
            },
        }


__all__ = ['ScannerPipeline', 'StockCandidate']
