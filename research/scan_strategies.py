"""
research/scan_strategies.py
3가지 시장 스캔 전략 구현
"""

"""
v5.7.5: Deep Scan 공통화 적용
"""
import time
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime

from utils.logger_new import get_logger
from utils.stock_filter import is_etf
from research.scanner_pipeline import StockCandidate
from research.deep_scan_utils import enrich_candidates_with_deep_scan

logger = get_logger()


_deep_scan_cache = {}
CACHE_TTL_SECONDS = 300


def _get_from_cache(cache_key: str) -> Optional[Dict]:
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


def _save_to_cache(cache_key: str, data: Dict):
    """캐시에 데이터 저장"""
    global _deep_scan_cache

    _deep_scan_cache[cache_key] = {
        'data': data,
        'timestamp': datetime.now()
    }


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
        """
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
        print(f"\n🔍 {self.name} 스캔")

        try:
            start_time = time.time()
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

            stock_candidates = []
            etf_count = 0
            for stock in candidates[:40]:
                if is_etf(stock['name'], stock['code']):
                    """
                    etf_count += 1
                    continue

                candidate = StockCandidate(
                    code=stock['code'],
                    name=stock['name'],
                    price=stock['current_price'],
                    volume=stock['volume'],
                    rate=stock['change_rate']
                )

                breakdown = {}
                score = 0.0

                trading_value = candidate.price * candidate.volume
                if trading_value > 1_000_000_000:
                    breakdown['거래대금'] = 40
                    score += 40
                elif trading_value > 500_000_000:
                    breakdown['거래대금'] = 30
                    score += 30
                else:
                    breakdown['거래대금'] = 0

                if 2.0 <= candidate.rate <= 10.0:
                    breakdown['상승률'] = 30
                    score += 30
                else:
                    breakdown['상승률'] = 0

                if candidate.volume > 1_000_000:
                    breakdown['거래량'] = 30
                    score += 30
                else:
                    breakdown['거래량'] = 0

                candidate.fast_scan_score = score
                candidate.fast_scan_breakdown = breakdown
                candidate.fast_scan_time = datetime.now()
                stock_candidates.append(candidate)

                if len(stock_candidates) >= 20:
                    break

            stock_candidates.sort(key=lambda x: x.fast_scan_score, reverse=True)

            print(f"[OK] 후보 {len(stock_candidates)}개 선정 (ETF {etf_count}개 제외)")

            print(f"\n🔬 Deep Scan 실행 중 (상위 {min(len(stock_candidates), 20)}개)...")
            top_candidates = stock_candidates[:20]

            for idx, candidate in enumerate(top_candidates, 1):
                """
                try:
                    print(f"   [{idx}/{len(top_candidates)}] {candidate.name} ({candidate.code})")

                    investor_data = self.market_api.get_investor_data(candidate.code)
                    if investor_data:
                        candidate.institutional_net_buy = investor_data.get('기관_순매수', 0)
                        candidate.foreign_net_buy = investor_data.get('외국인_순매수', 0)
                        print(f"      일별 - 기관={candidate.institutional_net_buy:,}, 외국인={candidate.foreign_net_buy:,}")
                    else:
                        candidate.institutional_net_buy = 0
                        candidate.foreign_net_buy = 0

                    bid_ask_data = self.market_api.get_bid_ask(candidate.code)
                    if bid_ask_data:
                        bid_total = bid_ask_data.get('매수_총잔량', 1)
                        ask_total = bid_ask_data.get('매도_총잔량', 1)
                        candidate.bid_ask_ratio = bid_total / ask_total if ask_total > 0 else 0
                        print(f"      호가비율={candidate.bid_ask_ratio:.2f}")
                    else:
                        candidate.bid_ask_ratio = 0

                    trend_data = self.market_api.get_institutional_trading_trend(
                        candidate.code,
                        days=5,
                        price_type='buy'
                    )
                    if trend_data:
                        candidate.institutional_trend = trend_data
                        print(f"      기관추이: 5일 데이터 수집")
                    else:
                        print(f"      기관추이: 데이터 없음")

                    daily_data = self.market_api.get_daily_chart(candidate.code, period=20)
                    if daily_data and len(daily_data) > 1:
                        volumes = [d.get('volume', 0) for d in daily_data if d.get('volume')]
                        if volumes:
                            candidate.avg_volume = sum(volumes) / len(volumes)
                            print(f"      일봉: 평균거래량={candidate.avg_volume:,.0f}")

                        rates = []
                        for d in daily_data:
                            close = d.get('close', 0)
                            open_price = d.get('open', 0)
                            if open_price and open_price > 0:
                                rate = (close - open_price) / open_price
                                rates.append(rate)

                        if len(rates) > 1:
                            import statistics
                            candidate.volatility = statistics.stdev(rates)
                            print(f"      일봉: 변동성={candidate.volatility*100:.2f}%")
                    else:
                        print(f"      일봉: 데이터 없음")

                    major_firms = [
                        ('001', '한국투자'),
                        ('003', '미래에셋'),
                        ('030', 'NH투자'),
                        ('005', '삼성'),
                        ('038', 'KB증권'),
                    ]

                    buy_count = 0
                    total_net_buy = 0

                    for firm_code, firm_name in major_firms:
                        try:
                            firm_data = self.market_api.get_securities_firm_trading(
                                firm_code=firm_code,
                                stock_code=candidate.code,
                                days=5
                            )

                            if firm_data and len(firm_data) > 0:
                                latest = firm_data[0]
                                net_qty = latest.get('net_qty', 0)

                                print(f"         └ {firm_name}: net_qty={net_qty:,}주", end="")

                                if net_qty > 0:
                                    buy_count += 1
                                    total_net_buy += net_qty
                                    print(f" [OK] 순매수")
                                elif net_qty < 0:
                                    print(f" WARNING: 순매도")
                                else:
                                    print(f" - 변동없음")
                            else:
                                print(f"         └ {firm_name}: 데이터 없음")

                            time.sleep(0.05)

                        except Exception as e:
                            print(f"         └ {firm_name}: 오류 - {e}")
                            continue

                    candidate.top_broker_buy_count = buy_count
                    candidate.top_broker_net_buy = total_net_buy

                    if buy_count > 0:
                        print(f"      증권사: 순매수증권사={buy_count}개, 순매수총량={total_net_buy:,}주")
                    else:
                        print(f"      증권사: 순매수 없음")

                    cache_key_exec = f"execution_{candidate.code}"
                    cached_exec = _get_from_cache(cache_key_exec)

                    if cached_exec:
                        candidate.execution_intensity = cached_exec.get('execution_intensity')
                        if candidate.execution_intensity:
                            print(f"      체결강도={candidate.execution_intensity:.1f} [캐시]")
                        else:
                            print(f"      체결강도: 값 없음 [캐시]")
                    else:
                        execution_data = self.market_api.get_execution_intensity(candidate.code)
                        if execution_data:
                            candidate.execution_intensity = execution_data.get('execution_intensity')
                            _save_to_cache(cache_key_exec, execution_data)
                            if candidate.execution_intensity:
                                print(f"      체결강도={candidate.execution_intensity:.1f}")
                            else:
                                print(f"      체결강도: 값 없음")
                        else:
                            print(f"      체결강도: 데이터 없음")

                    cache_key_prog = f"program_{candidate.code}"
                    cached_prog = _get_from_cache(cache_key_prog)

                    if cached_prog:
                        candidate.program_net_buy = cached_prog.get('program_net_buy')
                        if candidate.program_net_buy:
                            print(f"      프로그램순매수={candidate.program_net_buy:,} [캐시]")
                        else:
                            print(f"      프로그램매매: 값 없음 [캐시]")
                    else:
                        program_data = self.market_api.get_program_trading(candidate.code)
                        if program_data:
                            candidate.program_net_buy = program_data.get('program_net_buy')
                            _save_to_cache(cache_key_prog, program_data)
                            if candidate.program_net_buy:
                                print(f"      프로그램순매수={candidate.program_net_buy:,}")
                            else:
                                print(f"      프로그램매매: 값 없음")
                        else:
                            print(f"      프로그램매매: 데이터 없음")

                    time.sleep(0.1)

                except Exception as e:
                    print(f"      [ERROR] Deep Scan 오류: {e}")
                    logger.error(f"종목 {candidate.code} Deep Scan 실패: {e}", exc_info=True)
                    candidate.institutional_net_buy = 0
                    candidate.foreign_net_buy = 0
                    candidate.bid_ask_ratio = 0
                    candidate.avg_volume = None
                    candidate.volatility = None
                    candidate.top_broker_buy_count = 0
                    candidate.top_broker_net_buy = 0
                    candidate.execution_intensity = None
                    candidate.program_net_buy = None

            self.scan_results = top_candidates
            self.last_scan_time = time.time()

            return top_candidates

        except Exception as e:
            logger.error(f"[ERROR] [{self.name}] 스캔 실패: {e}", exc_info=True)
            print(f"[ERROR] [{self.name}] 스캔 실패: {e}")
            return []


class PriceChangeStrategy(ScanStrategy):
    """상승률 기반 스캔 전략"""

    def __init__(self, market_api, screener, config: Dict[str, Any] = None):
        """
        super().__init__("상승률 순위", market_api, screener)
        self.config = config or {}

    def get_filter_conditions(self) -> Dict[str, Any]:
        """상승률 기반 필터링 조건"""
        return {
            'min_price': self.config.get('min_price', 1000),
            'max_price': self.config.get('max_price', 500000),
            'min_volume': self.config.get('min_volume', 50000),
            'min_rate': self.config.get('min_rate', 3.0),
            'max_rate': self.config.get('max_rate', 29.9),
        }

    def scan(self) -> List[StockCandidate]:
        """
        상승률 상위 종목 스캔

        Returns:
            매수 후보 종목 리스트
        """
        logger.info(f" [{self.name}] 스캔 시작")
        print(f"\n{'='*60}")
        print(f" 전략 2: {self.name} 스캔")
        print(f"{'='*60}")

        try:
            start_time = time.time()

            rank_list = self.market_api.get_price_change_rank(
                market='ALL',
                sort='rise',
                limit=100
            )

            if not rank_list:
                print(f"WARNING:  [{self.name}] 데이터 없음 (주말/비거래시간)")
                return []

            conditions = self.get_filter_conditions()

            stock_candidates = []
            etf_count = 0
            for stock in rank_list:
                if is_etf(stock['name'], stock['code']):
                    """
                    etf_count += 1
                    continue

                if not (conditions['min_price'] <= stock['price'] <= conditions['max_price']):
                    """
                    continue
                if stock['volume'] < conditions['min_volume']:
                    continue
                if not (conditions['min_rate'] <= stock['change_rate'] <= conditions['max_rate']):
                    """
                    continue

                candidate = StockCandidate(
                    code=stock['code'],
                    name=stock['name'],
                    price=stock['price'],
                    volume=stock['volume'],
                    rate=stock['change_rate']
                )

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

            stock_candidates.sort(key=lambda x: x.fast_scan_score, reverse=True)

            elapsed = time.time() - start_time
            print(f"[OK] [{self.name}] 스캔 완료: {len(stock_candidates)}개 후보 (소요: {elapsed:.2f}초)")
            logger.info(f"[OK] [{self.name}] 스캔 완료: {len(stock_candidates)}개 후보")

            if stock_candidates:
                enrich_candidates_with_deep_scan(
                    stock_candidates,
                    self.market_api,
                    max_candidates=20,
                    verbose=True
                )

            self.scan_results = stock_candidates
            self.last_scan_time = time.time()

            return stock_candidates[:5]

        except Exception as e:
            logger.error(f"[ERROR] [{self.name}] 스캔 실패: {e}", exc_info=True)
            print(f"[ERROR] [{self.name}] 스캔 실패: {e}")
            return []


class AIDrivenStrategy(ScanStrategy):
    """AI 주도 스캔 전략"""

    def __init__(self, market_api, screener, ai_analyzer, config: Dict[str, Any] = None):
        """
        super().__init__("AI 주도 탐색", market_api, screener, ai_analyzer)
        self.config = config or {}

    def get_filter_conditions(self) -> Dict[str, Any]:
        """
        AI에게 필터링 조건 질의

        Returns:
            AI가 제안한 필터링 조건
        """
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

            print(f"    🤖 AI에게 스캔 전략 질의 중...")
            print(f"    ℹ️  현재는 기본 전략 사용 (향후 AI 자기강화 학습 적용)")

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

            stock_candidates = []
            etf_count = 0
            for stock in candidates[:40]:
                if is_etf(stock['name'], stock['code']):
                    """
                    etf_count += 1
                    continue

                candidate = StockCandidate(
                    code=stock['code'],
                    name=stock['name'],
                    price=stock['current_price'],
                    volume=stock['volume'],
                    rate=stock['change_rate']
                )

                score = 50.0
                candidate.fast_scan_score = score
                candidate.fast_scan_time = datetime.now()
                stock_candidates.append(candidate)

                if len(stock_candidates) >= 20:
                    break

            if etf_count > 0:
                print(f"   ℹ️  ETF/지수 {etf_count}개 제외됨")

            elapsed = time.time() - start_time
            print(f"[OK] [{self.name}] 스캔 완료: {len(stock_candidates)}개 후보 (소요: {elapsed:.2f}초)")
            logger.info(f"[OK] [{self.name}] 스캔 완료: {len(stock_candidates)}개 후보")

            if stock_candidates:
                enrich_candidates_with_deep_scan(
                    stock_candidates,
                    self.market_api,
                    max_candidates=20,
                    verbose=True
                )

            self.scan_results = stock_candidates
            self.last_scan_time = time.time()

            return stock_candidates[:5]

        except Exception as e:
            logger.error(f"[ERROR] [{self.name}] 스캔 실패: {e}", exc_info=True)
            print(f"[ERROR] [{self.name}] 스캔 실패: {e}")
            return []
