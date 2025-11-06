research/scanner_pipeline.py
3단계 스캐닝 파이프라인 (Fast → Deep → AI)
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from utils.logger_new import get_logger

from config.config_manager import get_config


logger = get_logger()


_deep_scan_cache = {}
CACHE_TTL_SECONDS = 300


@dataclass
class StockCandidate:
    """종목 후보 데이터 클래스"""

    code: str
    name: str
    price: int
    volume: int
    rate: float

    fast_scan_score: float = 0.0
    fast_scan_time: Optional[datetime] = None
    fast_scan_breakdown: Dict[str, float] = field(default_factory=dict)

    institutional_net_buy: int = 0
    foreign_net_buy: int = 0
    bid_ask_ratio: float = 0.0
    institutional_trend: Optional[Dict[str, Any]] = None
    avg_volume: Optional[float] = None
    volatility: Optional[float] = None
    top_broker_buy_count: int = 0
    top_broker_net_buy: int = 0
    execution_intensity: Optional[float] = None
    program_net_buy: Optional[int] = None
    deep_scan_score: float = 0.0
    deep_scan_time: Optional[datetime] = None
    deep_scan_breakdown: Dict[str, float] = field(default_factory=dict)

    ai_score: float = 0.0
    ai_signal: str = ''
    ai_confidence: str = ''
    ai_reasons: List[str] = field(default_factory=list)
    ai_risks: List[str] = field(default_factory=list)
    ai_scan_time: Optional[datetime] = None

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
        초기화

        Args:
            market_api: 시장 데이터 API
            screener: 종목 스크리너
            ai_analyzer: AI 분석기
            scoring_system: 스코어링 시스템 (선택)
        self.market_api = market_api
        self.screener = screener
        self.ai_analyzer = ai_analyzer
        self.scoring_system = scoring_system

        self.config = get_config()
        self.scan_config = self.config.scanning

        self.fast_scan_interval = self.scan_config.get('fast_scan', {}).get('interval', 10)
        self.deep_scan_interval = self.scan_config.get('deep_scan', {}).get('interval', 60)
        self.ai_scan_interval = self.scan_config.get('ai_scan', {}).get('interval', 300)

        self.fast_max_candidates = self.scan_config.get('fast_scan', {}).get('max_candidates', 50)
        self.deep_max_candidates = self.scan_config.get('deep_scan', {}).get('max_candidates', 20)
        self.ai_max_candidates = self.scan_config.get('ai_scan', {}).get('max_candidates', 5)

        self.last_fast_scan = 0
        self.last_deep_scan = 0
        self.last_ai_scan = 0

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
        print("⚡ Fast Scan 시작...")
        logger.info("⚡ Fast Scan 시작...")
        start_time = time.time()

        try:
            fast_config = self.scan_config.get('fast_scan', {})
            filters = fast_config.get('filters', {})

            filter_params = {
                'min_price': filters.get('min_price', 1000),
                'max_price': filters.get('max_price', 1000000),
                'min_volume': filters.get('min_volume', 100000),
                'min_rate': filters.get('min_rate', 1.0),
                'max_rate': filters.get('max_rate', 15.0),
                'min_market_cap': filters.get('min_market_cap', 0),
            }
            print(f"📍 Fast Scan 필터: {filter_params}")

            print("📍 screener.screen_stocks() 호출 중...")
            candidates = self.screener.screen_stocks(**filter_params)
            print(f"📍 screener.screen_stocks() 결과: {len(candidates) if candidates else 0}개 종목")

            candidates = sorted(
                candidates,
                key=lambda x: x.get('volume', 0) * x.get('price', 0),
                reverse=True
            )

            candidates = candidates[:self.fast_max_candidates]

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

                candidate.fast_scan_score = self._calculate_fast_score(candidate)
                stock_candidates.append(candidate)

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

        trading_value = candidate.price * candidate.volume
        if trading_value > 1_000_000_000:
            score += 40
        elif trading_value > 500_000_000:
            score += 30
        elif trading_value > 100_000_000:
            score += 20

        if 2.0 <= candidate.rate <= 10.0:
            score += 30
        elif 1.0 <= candidate.rate <= 15.0:
            score += 20

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

            for candidate in candidates:
                try:
                    print(f"📍 Deep Scan: {candidate.name} ({candidate.code})")

                    print(f"   📊 투자자 매매 조회 중...")
                    investor_data = self.market_api.get_investor_data(candidate.code)

                    if investor_data:
                        inst_buy = investor_data.get('기관_순매수', 0)
                        frgn_buy = investor_data.get('외국인_순매수', 0)
                        candidate.institutional_net_buy = inst_buy
                        candidate.foreign_net_buy = frgn_buy
                        print(f"   ✓ 투자자: 기관={inst_buy:,}, 외국인={frgn_buy:,}")
                    else:
                        print(f"   ⚠️  투자자 데이터 없음")
                        candidate.institutional_net_buy = 0
                        candidate.foreign_net_buy = 0

                    print(f"   📊 호가 조회 중...")
                    bid_ask_data = self.market_api.get_bid_ask(candidate.code)

                    if bid_ask_data:
                        bid_total = bid_ask_data.get('매수_총잔량', 1)
                        ask_total = bid_ask_data.get('매도_총잔량', 1)
                        candidate.bid_ask_ratio = bid_total / ask_total if ask_total > 0 else 0
                        print(f"   ✓ 호가: 매수={bid_total:,}, 매도={ask_total:,}, 비율={candidate.bid_ask_ratio:.2f}")
                    else:
                        print(f"   ⚠️  호가 데이터 없음")
                        candidate.bid_ask_ratio = 0

                    print(f"   📊 일봉 데이터 조회 중...")
                    try:
                        daily_data = self.market_api.get_daily_price(candidate.code, days=20)
                        if daily_data and len(daily_data) > 0:
                            volumes = [row.get('volume', 0) for row in daily_data]
                            candidate.avg_volume = sum(volumes) / len(volumes) if volumes else None

                            prices = [row.get('close', 0) for row in daily_data]
                            if len(prices) > 1:
                                returns = [(prices[i] / prices[i+1] - 1) for i in range(len(prices)-1) if prices[i+1] > 0]
                                if returns:
                                    import statistics
                                    candidate.volatility = statistics.stdev(returns) if len(returns) > 1 else 0.0

                            print(f"   ✓ 일봉: avg_volume={candidate.avg_volume:,.0f if candidate.avg_volume else 0}, volatility={candidate.volatility:.4f if candidate.volatility else 0}")
                        else:
                            print(f"   ⚠️  일봉 데이터 없음")
                    except Exception as e:
                        print(f"   ⚠️  일봉 데이터 조회 실패: {e}")
                        logger.debug(f"일봉 데이터 조회 실패: {e}")

                    print(f"   📊 증권사별 매매동향 조회 중...")
                    try:
                        major_firms = [
                            ("040", "KB증권"),
                            ("039", "교보증권"),
                            ("001", "한국투자증권"),
                            ("003", "미래에셋증권"),
                            ("005", "삼성증권")
                        ]

                        broker_buy_count = 0
                        broker_net_buy_total = 0

                        for firm_code, firm_name in major_firms:
                            try:
                                firm_data = self.market_api.get_securities_firm_trading(
                                    firm_code=firm_code,
                                    stock_code=candidate.code,
                                    days=1
                                )

                                if firm_data and len(firm_data) > 0:
                                    recent = firm_data[0]
                                    net_qty = recent.get('net_qty', 0)

                                    if net_qty > 0:
                                        broker_buy_count += 1
                                        broker_net_buy_total += net_qty

                                time.sleep(0.05)
                            except Exception as e:
                                logger.debug(f"증권사 {firm_name} 데이터 조회 실패: {e}")
                                continue

                        candidate.top_broker_buy_count = broker_buy_count
                        candidate.top_broker_net_buy = broker_net_buy_total

                        if broker_buy_count > 0:
                            print(f"   ✓ 증권사: {broker_buy_count}/5개 순매수, 총 {broker_net_buy_total:,}주")
                        else:
                            print(f"   ⚠️  증권사: 순매수 없음")
                    except Exception as e:
                        print(f"   ⚠️  증권사 데이터 조회 실패: {e}")
                        logger.debug(f"증권사 데이터 조회 실패: {e}")

                    print(f"   📊 체결강도 조회 중...")
                    cache_key_exec = f"execution_{candidate.code}"
                    cached_exec = self._get_from_cache(cache_key_exec)

                    if cached_exec:
                        candidate.execution_intensity = cached_exec.get('execution_intensity')
                        print(f"   ✓ 체결강도: {candidate.execution_intensity:.1f} [캐시]" if candidate.execution_intensity else "   ⚠️  체결강도: 0 [캐시]")
                    else:
                        try:
                            execution_data = self.market_api.get_execution_intensity(
                                stock_code=candidate.code
                            )

                            if execution_data:
                                candidate.execution_intensity = execution_data.get('execution_intensity')
                                self._save_to_cache(cache_key_exec, execution_data)
                                print(f"   ✓ 체결강도: {candidate.execution_intensity:.1f}" if candidate.execution_intensity else "   ⚠️  체결강도: 0")
                            else:
                                print(f"   ⚠️  체결강도 데이터 없음")
                        except Exception as e:
                            print(f"   ⚠️  체결강도 조회 실패 (캐시도 없음): {e}")
                            logger.debug(f"체결강도 조회 실패: {e}")

                    print(f"   📊 프로그램매매 조회 중...")
                    cache_key_prog = f"program_{candidate.code}"
                    cached_prog = self._get_from_cache(cache_key_prog)

                    if cached_prog:
                        candidate.program_net_buy = cached_prog.get('program_net_buy')
                        print(f"   ✓ 프로그램순매수: {candidate.program_net_buy:,}원 [캐시]" if candidate.program_net_buy else "   ⚠️  프로그램순매수: 0원 [캐시]")
                    else:
                        try:
                            program_data = self.market_api.get_program_trading(
                                stock_code=candidate.code
                            )

                            if program_data:
                                candidate.program_net_buy = program_data.get('program_net_buy')
                                self._save_to_cache(cache_key_prog, program_data)
                                print(f"   ✓ 프로그램순매수: {candidate.program_net_buy:,}원" if candidate.program_net_buy else "   ⚠️  프로그램순매수: 0원")
                            else:
                                print(f"   ⚠️  프로그램매매 데이터 없음")
                        except Exception as e:
                            print(f"   ⚠️  프로그램매매 조회 실패 (캐시도 없음): {e}")
                            logger.debug(f"프로그램매매 조회 실패: {e}")

                    candidate.deep_scan_score = self._calculate_deep_score(candidate)
                    candidate.deep_scan_time = scan_time

                    time.sleep(0.1)

                except Exception as e:
                    print(f"   ❌ 오류: {e}")
                    logger.error(f"종목 {candidate.code} Deep Scan 실패: {e}", exc_info=True)
                    continue

            candidates = sorted(
                candidates,
                key=lambda x: x.deep_scan_score,
                reverse=True
            )

            has_investor_data = any(
                c.institutional_net_buy != 0 or c.foreign_net_buy != 0
                for c in candidates
            )

            if has_investor_data:
                min_institutional_buy = deep_config.get('min_institutional_net_buy', 10_000_000)
                before_filter = len(candidates)
                candidates = [
                    c for c in candidates
                    if c.institutional_net_buy >= min_institutional_buy or c.foreign_net_buy >= 5_000_000
                ]
                logger.info(f"📊 기관/외국인 필터링: {before_filter}개 → {len(candidates)}개")
            else:
                logger.warning("⚠️  기관/외국인 데이터 없음 (API 실패) - 필터링 스킵")

            candidates = candidates[:self.deep_max_candidates]

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
        score = candidate.fast_scan_score

        if candidate.institutional_net_buy > 50_000_000:
            score += 30
        elif candidate.institutional_net_buy > 20_000_000:
            score += 20
        elif candidate.institutional_net_buy > 10_000_000:
            score += 10

        if candidate.foreign_net_buy > 20_000_000:
            score += 20
        elif candidate.foreign_net_buy > 10_000_000:
            score += 15
        elif candidate.foreign_net_buy > 5_000_000:
            score += 10

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
        print("📍 run_ai_scan() 메서드 진입")
        logger.info("🤖 AI Scan 시작...")
        start_time = time.time()

        try:
            if candidates is None:
                candidates = self.deep_scan_results

            print(f"📍 AI Scan candidates: {len(candidates)}개")

            if not candidates:
                print("⚠️  candidates 비어있음 - 종료")
                logger.warning("AI Scan 대상 종목 없음")
                return []

            ai_config = self.scan_config.get('ai_scan', {})
            scan_time = datetime.now()
            min_score = ai_config.get('min_analysis_score', 7.0)
            min_confidence = ai_config.get('min_confidence', 'Medium')

            print(f"📍 AI 분석기 타입: {type(self.ai_analyzer).__name__}")
            print(f"📍 AI 분석 시작 - {len(candidates)}개 종목 처리 예정")

            ai_approved = []

            for idx, candidate in enumerate(candidates, 1):
                try:
                    print(f"📍 [{idx}/{len(candidates)}] AI 분석 중: {candidate.name} ({candidate.code})")
                    logger.info(f"🤖 AI 분석 중: {candidate.name} ({candidate.code})")

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

                    print(f"    📍 stock_data 준비 완료:")
                    print(f"       - stock_code: {stock_data.get('stock_code')}")
                    print(f"       - current_price: {stock_data.get('current_price')}")
                    print(f"       - change_rate: {stock_data.get('change_rate')}")
                    print(f"       - 전체 키: {list(stock_data.keys())}")
                    print(f"    📍 analyze_stock() 호출 중...")
                    analysis = self.ai_analyzer.analyze_stock(stock_data)
                    print(f"    📍 analyze_stock() 완료: {analysis}")

                    candidate.ai_score = analysis.get('score', 0)
                    candidate.ai_signal = analysis.get('signal', 'hold')
                    candidate.ai_confidence = analysis.get('confidence', 'Low')
                    candidate.ai_reasons = analysis.get('reasons', [])
                    candidate.ai_risks = analysis.get('risks', [])
                    candidate.ai_scan_time = scan_time

                    candidate.final_score = (
                        candidate.deep_scan_score * 0.7 +
                        candidate.ai_score * 10 * 0.3
                    )

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

                    time.sleep(1)

                except Exception as e:
                    print(f"    ❌ AI 분석 중 에러 발생: {e}")
                    import traceback
                    traceback.print_exc()
                    logger.error(f"종목 {candidate.code} AI 분석 실패: {e}", exc_info=True)
                    continue

            ai_approved = sorted(
                ai_approved,
                key=lambda x: x.final_score,
                reverse=True
            )

            ai_approved = ai_approved[:self.ai_max_candidates]

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
        print("🚀 스캐닝 파이프라인 실행 시작")
        logger.info("🚀 스캐닝 파이프라인 실행 시작")

        should_fast = self.should_run_fast_scan()
        print(f"📍 Fast Scan 조건: should_run={should_fast}, interval={self.fast_scan_interval}초, last_scan={self.last_fast_scan}")

        if should_fast:
            print("✅ Fast Scan 실행 중...")
            self.run_fast_scan()
            print(f"📊 Fast Scan 결과: {len(self.fast_scan_results)}개 종목")
        else:
            print(f"⏭️ Fast Scan 스킵 (간격 미충족, 캐시: {len(self.fast_scan_results)}개)")

        should_deep = self.should_run_deep_scan()
        has_fast_results = len(self.fast_scan_results) > 0
        print(f"📍 Deep Scan 조건: should_run={should_deep}, has_fast_results={has_fast_results} ({len(self.fast_scan_results)}개)")

        if should_deep and has_fast_results:
            print("✅ Deep Scan 실행 중...")
            self.run_deep_scan()
            print(f"📊 Deep Scan 결과: {len(self.deep_scan_results)}개 종목")
        else:
            if not should_deep:
                print(f"⏭️ Deep Scan 스킵 (간격 미충족, 캐시: {len(self.deep_scan_results)}개)")
            else:
                print(f"⏭️ Deep Scan 스킵 (Fast Scan 결과 없음)")

        print(f"ℹ️  AI 분석: 매수 시점에서 최종 후보에 대해서만 실행")

        summary = (
            f"✅ 스캐닝 파이프라인 완료: "
            f"Fast={len(self.fast_scan_results)}, "
            f"Deep={len(self.deep_scan_results)} (최종 후보)"
        )
        print(summary)
        logger.info(summary)

        return self.deep_scan_results

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

    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """캐시에서 데이터 조회"""
        global _deep_scan_cache

        if cache_key not in _deep_scan_cache:
            return None

        entry = _deep_scan_cache[cache_key]
        timestamp = entry['timestamp']

        if (datetime.now() - timestamp).total_seconds() > CACHE_TTL_SECONDS:
            del _deep_scan_cache[cache_key]
            return None

        return entry['data']

    def _save_to_cache(self, cache_key: str, data: Dict):
        """캐시에 데이터 저장"""
        global _deep_scan_cache

        _deep_scan_cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }


__all__ = ['ScannerPipeline', 'StockCandidate']
