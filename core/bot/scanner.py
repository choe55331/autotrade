"""
Stock Scanner Module
스캔 전략 실행 모듈
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class StockScanner:
    """
    종목 스캐너

    Features:
    - 3단계 스캔 파이프라인 (Fast -> Deep -> AI)
    - 10가지 스코어링 시스템
    - AI 검토 및 승인
    """

    def __init__(self, strategy_manager, scoring_system, ai_analyzer):
        """
        초기화

        Args:
            strategy_manager: 전략 매니저
            scoring_system: 스코어링 시스템
            ai_analyzer: AI 분석기
        """
        self.strategy_manager = strategy_manager
        self.scoring_system = scoring_system
        self.ai_analyzer = ai_analyzer

        self.scan_progress = {
            'current_strategy': '',
            'total_candidates': 0,
            'top_candidates': [],
            'reviewing': '',
            'rejected': [],
            'approved': []
        }

    def run_scan_pipeline(
        self,
        portfolio_manager,
        dynamic_risk_manager,
        market_status: Dict[str, Any]
    ) -> List[Any]:
        3단계 스캔 파이프라인 실행

        Args:
            portfolio_manager: 포트폴리오 관리자
            dynamic_risk_manager: 동적 리스크 관리자
            market_status: 시장 상태

        Returns:
            최종 승인된 매수 후보 리스트

        try:
            positions = portfolio_manager.get_positions()

            if not portfolio_manager.can_add_position():
                logger.info("WARNING:  최대 포지션 수 도달")
                """
                return []

            if not dynamic_risk_manager.should_open_position(len(positions)):
                logger.info("WARNING:  리스크 관리: 포지션 진입 불가")
                """
                return []

            final_candidates = self.strategy_manager.run_current_strategy()

            if not final_candidates:
                logger.info("[OK] 스캐닝 완료: 최종 후보 없음")
                return []

            candidate_scores = self._score_candidates(
                final_candidates,
                self.strategy_manager.get_current_strategy_name()
            )

            top5 = self._select_top_candidates(final_candidates, candidate_scores, 5)

            approved_candidates = self._ai_review(
                top5[:3],
                candidate_scores,
                portfolio_manager
            )

            return approved_candidates

        except Exception as e:
            logger.error(f"스캔 파이프라인 실패: {e}", exc_info=True)
            return []

    def _score_candidates(
        self,
        candidates: List[Any],
        scan_type: str
    ) -> Dict[str, Any]:

        strategy_to_scan_type = {
            '거래량 순위': 'volume_based',
            '상승률 순위': 'price_change',
            'AI 매매 분석': 'ai_driven',
        }
        scan_type_key = strategy_to_scan_type.get(scan_type, 'default')

        candidate_scores = {}

        for candidate in candidates:
            stock_data = {
                'stock_code': candidate.code,
                'stock_name': candidate.name,
                'current_price': candidate.price,
                'volume': candidate.volume,
                'change_rate': candidate.rate,
                'institutional_net_buy': candidate.institutional_net_buy,
                'foreign_net_buy': candidate.foreign_net_buy,
                'bid_ask_ratio': candidate.bid_ask_ratio,
                'institutional_trend': getattr(candidate, 'institutional_trend', None),
                'avg_volume': getattr(candidate, 'avg_volume', None),
                'volatility': getattr(candidate, 'volatility', None),
                'top_broker_buy_count': getattr(candidate, 'top_broker_buy_count', 0),
                'top_broker_net_buy': getattr(candidate, 'top_broker_net_buy', 0),
                'execution_intensity': getattr(candidate, 'execution_intensity', None),
                'program_net_buy': getattr(candidate, 'program_net_buy', None),
                'is_trending_theme': False,
                'has_positive_news': False,
            }

            scoring_result = self.scoring_system.calculate_score(
                stock_data,
                scan_type=scan_type_key
            )

            candidate_scores[candidate.code] = scoring_result
            candidate.final_score = scoring_result.total_score

        return candidate_scores

    def _select_top_candidates(
        self,
        candidates: List[Any],
        scores: Dict[str, Any],
        top_n: int
    ) -> List[Any]:

        candidates.sort(key=lambda x: x.final_score, reverse=True)

        top_candidates = candidates[:top_n]

        self.scan_progress['top_candidates'] = [
            {
                'rank': idx + 1,
                'name': c.name,
                'code': c.code,
                'score': c.final_score,
                'percentage': (c.final_score / 440) * 100
            }
            for idx, c in enumerate(top_candidates)
        ]

        logger.info(f"\n 상위 {top_n}개 후보:")
        for rank, c in enumerate(top_candidates, 1):
            score_result = scores[c.code]
            """
            logger.info(
                f"   {rank}. {c.name} - {c.final_score:.0f}점 "
                f"({(c.final_score / 440) * 100:.0f}%)"
            )

        return top_candidates

    def _ai_review(
        self,
        candidates: List[Any],
        scores: Dict[str, Any],
        portfolio_manager
    ) -> List[Any]:

        approved = []

        portfolio_info = self._get_portfolio_info(portfolio_manager)

        for idx, candidate in enumerate(candidates, 1):
            self.scan_progress['reviewing'] = f"{candidate.name} ({idx}/{len(candidates)})"

"""
            logger.info(f"\n🤖 [{idx}/{len(candidates)}] {candidate.name} AI 검토 중...")

            scoring_result = scores[candidate.code]

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

            score_info = {
                'score': scoring_result.total_score,
                'max_score': 440,
                'percentage': scoring_result.percentage,
                'breakdown': {
                    '거래량 급증': scoring_result.volume_surge_score,
                    '가격 모멘텀': scoring_result.price_momentum_score,
                    '기관 매수세': scoring_result.institutional_buying_score,
                    '매수 호가 강도': scoring_result.bid_strength_score,
                }
            }

            import asyncio
            try:
                ai_analysis = asyncio.run(
                    self.ai_analyzer.analyze_stock(
                        stock_data,
                        score_info=score_info,
                        portfolio_info=portfolio_info
                    )
                )
            except:
                ai_analysis = {
                    'signal': 'hold',
                    'confidence': 0.5,
                    'reasons': ['AI 분석 실패'],
                    'risks': []
                }

            ai_signal = ai_analysis.get('signal', 'hold')

            candidate.ai_signal = ai_signal
            candidate.ai_reasons = ai_analysis.get('reasons', [])
            candidate.ai_confidence = ai_analysis.get('confidence', 0.5)

            logger.info(f"   [OK] AI 결정: {ai_signal.upper()}")

            buy_approved = (
                (ai_signal == 'buy' and scoring_result.total_score >= 250) or
                (ai_signal == 'hold' and scoring_result.total_score >= 300)
            )

            if buy_approved:
                logger.info(f"[OK] 매수 조건 충족")
                approved.append(candidate)

                self.scan_progress['approved'].append({
                    'name': candidate.name,
                    'price': candidate.price,
                    'score': scoring_result.total_score
                })
            else:
                reason_text = f"AI={ai_signal}, 점수={scoring_result.total_score:.0f}"
                logger.info(f"[ERROR] 매수 조건 미충족 ({reason_text})")

                self.scan_progress['rejected'].append({
                    'name': candidate.name,
                    'reason': reason_text,
                    'score': scoring_result.total_score
                })

        self.scan_progress['reviewing'] = ''

        return approved

    def _get_portfolio_info(self, portfolio_manager) -> str:
        """포트폴리오 정보 텍스트"""

        try:
            summary = portfolio_manager.get_portfolio_summary()

            return f"""
현재 포트폴리오:
- 보유 종목: {summary['position_count']}개
- 총 자산: {summary['total_assets']:,}원
- 수익률: {summary['total_profit_loss_rate']:+.2f}%
        """
        except:
            return "No positions"

"""
    def get_scan_progress(self) -> Dict[str, Any]:
        """스캔 진행 상황 반환"""
        return self.scan_progress
