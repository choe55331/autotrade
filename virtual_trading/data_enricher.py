"""
virtual_trading/data_enricher.py
가상 매매 전략을 위한 데이터 enrichment
Missing fields를 채워서 모든 전략이 작동하도록 함
"""
import logging
from typing import Dict, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class VirtualTradingDataEnricher:
    """
    가상 매매 전략에 필요한 데이터를 enrichment하는 클래스
    """

    def __init__(self, bot_instance=None):
        """
        Args:
            bot_instance: Main bot instance (optional, for advanced data fetching)
        """
        self.bot = bot_instance
        logger.info("VirtualTradingDataEnricher 초기화 완료")

    def enrich_stock_data(self, stock_data: Dict, candidate=None) -> Dict:
        """
        stock_data에 부족한 필드들을 추가/계산

        Args:
            stock_data: 원본 stock_data
            candidate: StockCandidate 객체 (추가 데이터 소스)

        Returns:
            enriched stock_data
        """
        enriched = stock_data.copy()

        # 1. 기술적 지표 계산 (MACD, BB, etc.)
        enriched = self._enrich_technical_indicators(enriched, candidate)

        # 2. 가격 변동 데이터
        enriched = self._enrich_price_data(enriched, candidate)

        # 3. 기본적 지표 (fundamental)
        enriched = self._enrich_fundamental_data(enriched, candidate)

        # 4. 시장 데이터
        enriched = self._enrich_market_data(enriched, candidate)

        return enriched

    def _enrich_technical_indicators(self, stock_data: Dict, candidate) -> Dict:
        """기술적 지표 enrichment"""
        try:
            # MACD 분해 (macd가 dict로 오는 경우)
            macd_value = stock_data.get('macd')
            if isinstance(macd_value, dict):
                stock_data['macd'] = macd_value.get('macd', 0)
                stock_data['macd_signal'] = macd_value.get('signal', 0)
                stock_data['macd_histogram'] = macd_value.get('histogram', 0)
            elif macd_value is None:
                # MACD 값이 없으면 기본값
                stock_data['macd'] = 0
                stock_data['macd_signal'] = 0
                stock_data['macd_histogram'] = 0

            # Bollinger Bands position 계산
            bb_data = stock_data.get('bollinger_bands')
            current_price = stock_data.get('current_price', 0)

            if isinstance(bb_data, dict) and current_price > 0:
                upper = bb_data.get('upper', 0)
                lower = bb_data.get('lower', 0)
                middle = bb_data.get('middle', 0)

                if upper > lower and lower > 0:
                    # BB position: 0 (하단) ~ 1 (상단)
                    bb_position = (current_price - lower) / (upper - lower)
                    stock_data['bb_position'] = max(0, min(1, bb_position))
                else:
                    stock_data['bb_position'] = 0.5  # 중간값
            elif stock_data.get('bb_position') is None:
                stock_data['bb_position'] = 0.5

            # RSI 기본값
            if stock_data.get('rsi') is None:
                # RSI 추정 (가격 변화율 기반)
                price_change = stock_data.get('price_change_percent', 0)
                if price_change > 5:
                    stock_data['rsi'] = 70  # 강세
                elif price_change < -5:
                    stock_data['rsi'] = 30  # 약세
                else:
                    stock_data['rsi'] = 50  # 중립

            # 이동평균선 (MA20)
            if stock_data.get('ma20') is None:
                # MA20이 없으면 현재가 사용
                stock_data['ma20'] = stock_data.get('current_price', 0)

            # 변동성 (Volatility) - ATR 대용
            if stock_data.get('volatility') is None:
                # 가격 변화율의 절댓값을 변동성으로 사용
                price_change = abs(stock_data.get('price_change_percent', 0))
                stock_data['volatility'] = price_change

        except Exception as e:
            logger.warning(f"기술적 지표 enrichment 실패: {e}")

        return stock_data

    def _enrich_price_data(self, stock_data: Dict, candidate) -> Dict:
        """가격 관련 데이터 enrichment"""
        try:
            # 연속 하락일수 계산 (간소화: 가격 변화율로 추정)
            if stock_data.get('consecutive_down_days') is None:
                price_change = stock_data.get('price_change_percent', 0)
                if price_change < -3:
                    stock_data['consecutive_down_days'] = 3  # 추정값
                elif price_change < -1:
                    stock_data['consecutive_down_days'] = 2
                else:
                    stock_data['consecutive_down_days'] = 0

            # 52주 고가 (없으면 현재가의 120%로 추정)
            if stock_data.get('high_52week') is None:
                current_price = stock_data.get('current_price', 0)
                stock_data['high_52week'] = current_price * 1.20  # 추정

            # 3일 가격 변화 (없으면 당일 변화로 대체)
            if stock_data.get('price_change_3day') is None:
                stock_data['price_change_3day'] = stock_data.get('price_change_percent', 0)

        except Exception as e:
            logger.warning(f"가격 데이터 enrichment 실패: {e}")

        return stock_data

    def _enrich_fundamental_data(self, stock_data: Dict, candidate) -> Dict:
        """기본적 분석 데이터 enrichment"""
        try:
            # 시가총액 (없으면 추정)
            if stock_data.get('market_cap') is None:
                # 간단한 추정: 주가 * 가정된 발행주식수
                current_price = stock_data.get('current_price', 0)
                volume = stock_data.get('volume', 0)

                if current_price > 100000:  # 고가주
                    estimated_market_cap = 500_000_000_000  # 5천억 (중견기업)
                elif current_price > 50000:
                    estimated_market_cap = 200_000_000_000  # 2천억
                else:
                    estimated_market_cap = 100_000_000_000  # 1천억

                stock_data['market_cap'] = estimated_market_cap

            # PER, PBR 기본값
            if stock_data.get('per') is None:
                stock_data['per'] = 15.0  # 평균적인 값
            if stock_data.get('pbr') is None:
                stock_data['pbr'] = 1.5  # 평균적인 값

            # 배당 관련 (없으면 기본값)
            if stock_data.get('dividend_yield') is None:
                stock_data['dividend_yield'] = 1.0  # 1%
            if stock_data.get('dividend_growth_rate') is None:
                stock_data['dividend_growth_rate'] = 3.0  # 3%
            if stock_data.get('eps') is None:
                stock_data['eps'] = 5000  # 기본값
            if stock_data.get('dps') is None:
                stock_data['dps'] = 1000  # 기본값
            if stock_data.get('debt_ratio') is None:
                stock_data['debt_ratio'] = 80.0  # 보통 수준

        except Exception as e:
            logger.warning(f"기본적 분석 데이터 enrichment 실패: {e}")

        return stock_data

    def _enrich_market_data(self, stock_data: Dict, candidate) -> Dict:
        """시장/섹터 데이터 enrichment"""
        try:
            # 섹터 정보 (없으면 추정)
            if stock_data.get('sector') is None or stock_data.get('sector') == 'Unknown':
                # 종목명 기반 간단한 섹터 추정
                stock_name = stock_data.get('stock_name', '')

                if any(keyword in stock_name for keyword in ['전자', '반도체', '디스플레이', 'IT', '소프트']):
                    stock_data['sector'] = 'IT'
                elif any(keyword in stock_name for keyword in ['바이오', '제약', '병원', '헬스']):
                    stock_data['sector'] = '헬스케어'
                elif any(keyword in stock_name for keyword in ['은행', '증권', '보험', '금융']):
                    stock_data['sector'] = '금융'
                elif any(keyword in stock_name for keyword in ['건설', '건축']):
                    stock_data['sector'] = '산업재'
                elif any(keyword in stock_name for keyword in ['식품', '음료', '유통']):
                    stock_data['sector'] = '필수소비재'
                elif any(keyword in stock_name for keyword in ['자동차', '화학', '철강']):
                    stock_data['sector'] = '경기소비재'
                else:
                    stock_data['sector'] = 'IT'  # 기본값

            # 섹터 상대 강도 (없으면 기본값)
            if stock_data.get('sector_relative_strength') is None:
                # 가격 변화율 기반 추정
                price_change = stock_data.get('price_change_percent', 0)
                if price_change > 3:
                    stock_data['sector_relative_strength'] = 1.10  # 강세
                elif price_change > 0:
                    stock_data['sector_relative_strength'] = 1.03  # 약간 강세
                else:
                    stock_data['sector_relative_strength'] = 0.97  # 약세

        except Exception as e:
            logger.warning(f"시장 데이터 enrichment 실패: {e}")

        return stock_data

    def enrich_market_context(self, market_data: Dict) -> Dict:
        """
        market_data enrichment

        Args:
            market_data: 원본 market_data

        Returns:
            enriched market_data
        """
        enriched = market_data.copy()

        # Fear & Greed Index (없으면 중립)
        if enriched.get('fear_greed_index') is None:
            enriched['fear_greed_index'] = 50  # 중립

        # Economic Cycle (없으면 확장기)
        if enriched.get('economic_cycle') is None:
            enriched['economic_cycle'] = 'expansion'

        # Market Trend
        if enriched.get('market_trend') is None:
            enriched['market_trend'] = 'neutral'

        return enriched


def create_enricher(bot_instance=None) -> VirtualTradingDataEnricher:
    """
    Data enricher 인스턴스 생성 (싱글톤 패턴)
    """
    return VirtualTradingDataEnricher(bot_instance)
