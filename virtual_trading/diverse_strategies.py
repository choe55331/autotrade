virtual_trading/diverse_strategies.py
12가지 다양한 실전 매매 전략 구현 (v5.7.5: 10개 → 12개 확장)

User Requirement:
"시중에 나온 다양한 매매 전략법을 완전 다른걸로 12개 해서 유리한 조합 테스트"
Not simple score variations - fundamentally different trading approaches.

v5.7.5 추가 전략:
11. 기관추종 (Institutional Following): 기관/외국인 순매수 추종
12. 거래량RSI (Volume & RSI Combined): 거래량 급증 + RSI 조합
from typing import Dict, Optional
from datetime import datetime
from .virtual_account import VirtualAccount, VirtualPosition


class DiverseTradingStrategy:
    """다양한 실전 매매 전략의 베이스 클래스"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

        self.max_positions = 5
        self.position_size_rate = 0.15
        self.min_price = 1000

    def should_buy(self, stock_data: Dict, market_data: Dict, account: VirtualAccount) -> bool:
        """매수 조건 확인 (전략별로 오버라이드)"""
        raise NotImplementedError

    def should_sell(self, position: VirtualPosition, current_price: int,
                    stock_data: Dict, days_held: int) -> tuple[bool, str]:
        raise NotImplementedError

    def calculate_quantity(self, price: int, account: VirtualAccount) -> int:
        """매수 수량 계산"""
        available_cash = account.cash
        target_amount = int(available_cash * self.position_size_rate)
        quantity = target_amount // price
        return max(quantity, 1)


class MomentumStrategy(DiverseTradingStrategy):
    """
    강한 상승 추세를 따라가는 전략
    - 거래량 급증 + 주가 상승 종목에 진입
    - 추세 약화시 빠르게 청산
    """

    def __init__(self):
        super().__init__("모멘텀추세", "강한 상승세 포착 후 추세 추종")
        self.max_positions = 6
        self.position_size_rate = 0.18
        self.min_volume_ratio = 2.0
        self.min_price_change = 3.0

    def should_buy(self, stock_data: Dict, market_data: Dict, account: VirtualAccount) -> bool:
        if len(account.positions) >= self.max_positions:
            return False

        volume_ratio = stock_data.get('volume_ratio', 1.0)
        if volume_ratio < self.min_volume_ratio:
            return False

        price_change = stock_data.get('price_change_percent', 0)
        if price_change < self.min_price_change:
            return False

        rsi = stock_data.get('rsi', 50)
        if rsi > 70:
            return False

        return True

    def should_sell(self, position: VirtualPosition, current_price: int,
                    stock_data: Dict, days_held: int) -> tuple[bool, str]:
        position.update_price(current_price)
        pnl_rate = position.unrealized_pnl_rate

        if pnl_rate >= 12.0:
            return True, f"모멘텀 익절 {pnl_rate:.1f}%"

        if pnl_rate <= -6.0:
            return True, f"모멘텀 손절 {pnl_rate:.1f}%"

        volume_ratio = stock_data.get('volume_ratio', 1.0)
        if volume_ratio < 0.7 and pnl_rate < 3.0:
            return True, "거래량 감소로 청산"

        if days_held >= 7:
            return True, f"보유 {days_held}일 경과"

        return False, ""


class MeanReversionStrategy(DiverseTradingStrategy):
    """
    과매도 구간에서 반등 포착 전략
    - RSI 30 이하 과매도 구간 진입
    - 단기 반등 노리고 빠른 익절
    """

    def __init__(self):
        super().__init__("평균회귀", "과매도 구간 반등 노림")
        self.max_positions = 4
        self.position_size_rate = 0.20
        self.max_rsi = 35
        self.min_days_down = 3

    def should_buy(self, stock_data: Dict, market_data: Dict, account: VirtualAccount) -> bool:
        if len(account.positions) >= self.max_positions:
            return False

        rsi = stock_data.get('rsi', 50)
        if rsi > self.max_rsi:
            return False

        consecutive_down = stock_data.get('consecutive_down_days', 0)
        if consecutive_down < self.min_days_down:
            return False

        price_change = stock_data.get('price_change_percent', 0)
        if price_change < -10.0:
            return False

        return True

    def should_sell(self, position: VirtualPosition, current_price: int,
                    stock_data: Dict, days_held: int) -> tuple[bool, str]:
        position.update_price(current_price)
        pnl_rate = position.unrealized_pnl_rate

        if pnl_rate >= 5.0:
            return True, f"평균회귀 익절 {pnl_rate:.1f}%"

        if pnl_rate <= -4.0:
            return True, f"평균회귀 손절 {pnl_rate:.1f}%"

        rsi = stock_data.get('rsi', 50)
        if rsi >= 60 and pnl_rate > 2.0:
            return True, "RSI 회복으로 익절"

        if days_held >= 5:
            return True, f"보유 {days_held}일 경과"

        return False, ""


class BreakoutStrategy(DiverseTradingStrategy):
    """
    저항선 돌파 시 진입 전략
    - 52주 신고가 돌파
    - 박스권 상단 돌파
    """

    def __init__(self):
        super().__init__("돌파매매", "저항선 돌파 포착")
        self.max_positions = 5
        self.position_size_rate = 0.16
        self.breakout_threshold = 0.98

    def should_buy(self, stock_data: Dict, market_data: Dict, account: VirtualAccount) -> bool:
        if len(account.positions) >= self.max_positions:
            return False

        current_price = stock_data.get('current_price', 0)
        high_52w = stock_data.get('high_52week')

        if high_52w is not None:
            if current_price < high_52w * self.breakout_threshold:
                return False
        else:
            price_change = stock_data.get('price_change_percent', 0)
            if price_change < 5.0:
                return False

        volume_ratio = stock_data.get('volume_ratio', 1.0)
        if volume_ratio < 1.5:
            return False

        price_change = stock_data.get('price_change_percent', 0)
        if price_change < 1.0:
            return False

        return True

    def should_sell(self, position: VirtualPosition, current_price: int,
                    stock_data: Dict, days_held: int) -> tuple[bool, str]:
        position.update_price(current_price)
        pnl_rate = position.unrealized_pnl_rate

        if pnl_rate >= 15.0:
            return True, f"돌파 익절 {pnl_rate:.1f}%"

        highest_rate = position.highest_price / position.average_price * 100 - 100
        if highest_rate > 8.0:
            current_rate = current_price / position.average_price * 100 - 100
            if current_rate < highest_rate - 7.0:
                return True, f"트레일링 스탑 (최고 {highest_rate:.1f}% → 현재 {current_rate:.1f}%)"

        if pnl_rate <= -5.0:
            return True, f"돌파 실패 손절 {pnl_rate:.1f}%"

        if days_held >= 10:
            return True, f"보유 {days_held}일 경과"

        return False, ""


class ValueInvestingStrategy(DiverseTradingStrategy):
    """
    저평가 우량주 장기 보유 전략
    - PER, PBR 낮은 종목
    - 배당 수익률 높은 종목
    """

    def __init__(self):
        super().__init__("가치투자", "저평가 우량주 장기 보유")
        self.max_positions = 3
        self.position_size_rate = 0.25
        self.max_per = 12.0
        self.max_pbr = 1.2
        self.min_dividend = 2.0

    def should_buy(self, stock_data: Dict, market_data: Dict, account: VirtualAccount) -> bool:
        if len(account.positions) >= self.max_positions:
            return False

        per = stock_data.get('per')
        if per is not None and per > 0:
            if per > self.max_per:
                return False

        pbr = stock_data.get('pbr')
        if pbr is not None and pbr > 0:
            if pbr > self.max_pbr:
                return False

        dividend_yield = stock_data.get('dividend_yield')
        if dividend_yield is not None:
            if dividend_yield < self.min_dividend:
                return False

        if per is None and pbr is None and dividend_yield is None:
            price_change = stock_data.get('price_change_percent', 0)
            if not (2.0 <= price_change <= 5.0):
                return False
            volume_ratio = stock_data.get('volume_ratio', 1.0)
            if volume_ratio < 1.0:
                return False
        else:
            price_change = stock_data.get('price_change_percent', 0)
            if abs(price_change) > 5.0:
                return False

        return True

    def should_sell(self, position: VirtualPosition, current_price: int,
                    stock_data: Dict, days_held: int) -> tuple[bool, str]:
        position.update_price(current_price)
        pnl_rate = position.unrealized_pnl_rate

        if pnl_rate >= 20.0:
            return True, f"가치투자 익절 {pnl_rate:.1f}%"

        if pnl_rate <= -8.0:
            return True, f"가치투자 손절 {pnl_rate:.1f}%"

        per = stock_data.get('per', 0)
        if per > 20.0 and pnl_rate > 10.0:
            return True, "밸류에이션 악화로 익절"

        if days_held >= 30:
            return True, f"보유 {days_held}일 경과"

        return False, ""


class SwingTradingStrategy(DiverseTradingStrategy):
    """
    단기 변동성을 이용한 스윙 전략
    - 볼린저밴드 하단 매수, 상단 매도
    - 3-7일 단기 보유
    """

    def __init__(self):
        super().__init__("스윙매매", "단기 변동성 활용")
        self.max_positions = 7
        self.position_size_rate = 0.12
        self.bb_lower_threshold = 0.95

    def should_buy(self, stock_data: Dict, market_data: Dict, account: VirtualAccount) -> bool:
        if len(account.positions) >= self.max_positions:
            return False

        bb_position = stock_data.get('bb_position', 0.5)
        if bb_position > 0.3:
            return False

        volatility = stock_data.get('volatility', 0)
        if volatility < 2.0:
            return False

        rsi = stock_data.get('rsi', 50)
        if rsi > 40:
            return False

        return True

    def should_sell(self, position: VirtualPosition, current_price: int,
                    stock_data: Dict, days_held: int) -> tuple[bool, str]:
        position.update_price(current_price)
        pnl_rate = position.unrealized_pnl_rate

        if pnl_rate >= 8.0:
            return True, f"스윙 익절 {pnl_rate:.1f}%"

        if pnl_rate <= -4.0:
            return True, f"스윙 손절 {pnl_rate:.1f}%"

        bb_position = stock_data.get('bb_position', 0.5)
        if bb_position > 0.7 and pnl_rate > 3.0:
            return True, "볼린저 상단 도달 익절"

        if days_held >= 7:
            return True, f"보유 {days_held}일 경과"

        return False, ""


class MACDStrategy(DiverseTradingStrategy):
    """
    MACD 지표 기반 전략
    - MACD 골든크로스 매수
    - MACD 데드크로스 매도
    """

    def __init__(self):
        super().__init__("MACD크로스", "MACD 시그널 추종")
        self.max_positions = 5
        self.position_size_rate = 0.17

    def should_buy(self, stock_data: Dict, market_data: Dict, account: VirtualAccount) -> bool:
        if len(account.positions) >= self.max_positions:
            return False

        macd = stock_data.get('macd', 0)
        macd_signal = stock_data.get('macd_signal', 0)
        if macd <= macd_signal:
            return False

        macd_hist = stock_data.get('macd_histogram', 0)
        if macd_hist <= 0:
            return False

        price = stock_data.get('current_price', 0)
        ma20 = stock_data.get('ma20', price)
        if price < ma20:
            return False

        return True

    def should_sell(self, position: VirtualPosition, current_price: int,
                    stock_data: Dict, days_held: int) -> tuple[bool, str]:
        position.update_price(current_price)
        pnl_rate = position.unrealized_pnl_rate

        macd = stock_data.get('macd', 0)
        macd_signal = stock_data.get('macd_signal', 0)
        if macd < macd_signal and pnl_rate > -3.0:
            return True, f"MACD 데드크로스 {pnl_rate:.1f}%"

        if pnl_rate >= 10.0:
            return True, f"MACD 익절 {pnl_rate:.1f}%"

        if pnl_rate <= -5.0:
            return True, f"MACD 손절 {pnl_rate:.1f}%"

        if days_held >= 15:
            return True, f"보유 {days_held}일 경과"

        return False, ""


class ContrarianStrategy(DiverseTradingStrategy):
    """
    시장 공포/탐욕 지수를 역으로 활용
    - 공포 극대화 시점에 매수
    - 탐욕 극대화 시점에 매도
    """

    def __init__(self):
        super().__init__("역발상", "시장 감정의 반대편 베팅")
        self.max_positions = 4
        self.position_size_rate = 0.22
        self.fear_threshold = 30
        self.greed_threshold = 70

    def should_buy(self, stock_data: Dict, market_data: Dict, account: VirtualAccount) -> bool:
        if len(account.positions) >= self.max_positions:
            return False

        fear_greed_index = market_data.get('fear_greed_index', 50)
        if fear_greed_index > self.fear_threshold:
            return False

        price_change_3d = stock_data.get('price_change_3day', 0)
        if price_change_3d > -5.0:
            return False

        volume_ratio = stock_data.get('volume_ratio', 1.0)
        if volume_ratio < 1.3:
            return False

        market_cap = stock_data.get('market_cap', 0)
        if market_cap < 100_000_000_000:
            return False

        return True

    def should_sell(self, position: VirtualPosition, current_price: int,
                    stock_data: Dict, days_held: int) -> tuple[bool, str]:
        position.update_price(current_price)
        pnl_rate = position.unrealized_pnl_rate

        market_data = stock_data.get('market_data', {})
        fear_greed_index = market_data.get('fear_greed_index', 50)
        if fear_greed_index > self.greed_threshold and pnl_rate > 5.0:
            return True, f"탐욕 극대화 익절 {pnl_rate:.1f}%"

        if pnl_rate >= 18.0:
            return True, f"역발상 익절 {pnl_rate:.1f}%"

        if pnl_rate <= -7.0:
            return True, f"역발상 손절 {pnl_rate:.1f}%"

        if days_held >= 20:
            return True, f"보유 {days_held}일 경과"

        return False, ""


class SectorRotationStrategy(DiverseTradingStrategy):
    """
    경기 사이클에 따른 섹터 순환 전략
    - 경기 확장기: IT, 경기소비재
    - 경기 둔화기: 필수소비재, 유틸리티
    """

    def __init__(self):
        super().__init__("섹터순환", "경기 사이클별 섹터 선택")
        self.max_positions = 6
        self.position_size_rate = 0.15

        self.cycle_sectors = {
            'expansion': ['IT', '경기소비재', '산업재'],
            'peak': ['에너지', '금융'],
            'contraction': ['필수소비재', '헬스케어', '유틸리티'],
            'trough': ['경기소비재', 'IT']
        }

    def should_buy(self, stock_data: Dict, market_data: Dict, account: VirtualAccount) -> bool:
        if len(account.positions) >= self.max_positions:
            return False

        cycle_phase = market_data.get('economic_cycle', 'expansion')
        preferred_sectors = self.cycle_sectors.get(cycle_phase, [])

        sector = stock_data.get('sector', '')
        if sector not in preferred_sectors:
            return False

        sector_strength = stock_data.get('sector_relative_strength', 1.0)
        if sector_strength < 1.05:
            return False

        price_change = stock_data.get('price_change_percent', 0)
        if price_change < 2.0:
            return False

        return True

    def should_sell(self, position: VirtualPosition, current_price: int,
                    stock_data: Dict, days_held: int) -> tuple[bool, str]:
        position.update_price(current_price)
        pnl_rate = position.unrealized_pnl_rate

        sector_strength = stock_data.get('sector_relative_strength', 1.0)
        if sector_strength < 0.95 and pnl_rate > 0:
            return True, f"섹터 약화 익절 {pnl_rate:.1f}%"

        if pnl_rate >= 12.0:
            return True, f"섹터 익절 {pnl_rate:.1f}%"

        if pnl_rate <= -5.0:
            return True, f"섹터 손절 {pnl_rate:.1f}%"

        if days_held >= 14:
            return True, f"보유 {days_held}일 경과"

        return False, ""


class HotStockStrategy(DiverseTradingStrategy):
    """
    단기 급등주 추격 전략
    - 당일 급등 종목 진입
    - 빠른 익절/손절
    """

    def __init__(self):
        super().__init__("급등추격", "당일 급등주 단타")
        self.max_positions = 8
        self.position_size_rate = 0.10
        self.min_price_surge = 5.0
        self.max_price_surge = 20.0

    def should_buy(self, stock_data: Dict, market_data: Dict, account: VirtualAccount) -> bool:
        if len(account.positions) >= self.max_positions:
            return False

        price_change = stock_data.get('price_change_percent', 0)
        if not (self.min_price_surge <= price_change <= self.max_price_surge):
            return False

        volume_ratio = stock_data.get('volume_ratio', 1.0)
        if volume_ratio < 3.0:
            return False

        market_cap = stock_data.get('market_cap', 0)
        if market_cap < 50_000_000_000:
            return False

        current_price = stock_data.get('current_price', 0)
        high_52w = stock_data.get('high_52week', current_price * 2)
        if current_price < high_52w * 0.90:
            return False

        return True

    def should_sell(self, position: VirtualPosition, current_price: int,
                    stock_data: Dict, days_held: int) -> tuple[bool, str]:
        position.update_price(current_price)
        pnl_rate = position.unrealized_pnl_rate

        if pnl_rate >= 6.0:
            return True, f"급등 익절 {pnl_rate:.1f}%"

        if pnl_rate <= -3.0:
            return True, f"급등 손절 {pnl_rate:.1f}%"

        if days_held >= 1:
            return True, f"당일 마감 {pnl_rate:.1f}%"

        return False, ""


class DividendGrowthStrategy(DiverseTradingStrategy):
    """
    배당 성장주 장기 보유 전략
    - 배당 성장률 높은 종목
    - 안정적인 현금 흐름
    """

    def __init__(self):
        super().__init__("배당성장", "배당 증가 우량주 장기 보유")
        self.max_positions = 4
        self.position_size_rate = 0.23
        self.min_dividend_yield = 2.5
        self.min_dividend_growth = 5.0

    def should_buy(self, stock_data: Dict, market_data: Dict, account: VirtualAccount) -> bool:
        if len(account.positions) >= self.max_positions:
            return False

        dividend_yield = stock_data.get('dividend_yield', 0)
        if dividend_yield < self.min_dividend_yield:
            return False

        dividend_growth = stock_data.get('dividend_growth_rate', 0)
        if dividend_growth < self.min_dividend_growth:
            return False

        eps = stock_data.get('eps', 0)
        dps = stock_data.get('dps', 0)
        if dps == 0 or eps / dps < 1.5:
            return False

        debt_ratio = stock_data.get('debt_ratio', 999)
        if debt_ratio > 100:
            return False

        return True

    def should_sell(self, position: VirtualPosition, current_price: int,
                    stock_data: Dict, days_held: int) -> tuple[bool, str]:
        position.update_price(current_price)
        pnl_rate = position.unrealized_pnl_rate

        dividend_growth = stock_data.get('dividend_growth_rate', 0)
        if dividend_growth < 0 and pnl_rate > -5.0:
            return True, f"배당 감소로 청산 {pnl_rate:.1f}%"

        if pnl_rate >= 25.0:
            return True, f"배당 성장주 익절 {pnl_rate:.1f}%"

        if pnl_rate <= -10.0:
            return True, f"배당 성장주 손절 {pnl_rate:.1f}%"

        if days_held >= 60:
            return True, f"보유 {days_held}일 경과"

        return False, ""


class InstitutionalFollowingStrategy(DiverseTradingStrategy):
    """
    기관/외국인 순매수 추종 전략 (Smart Money Following)
    - 기관과 외국인의 순매수가 강한 종목에 진입
    - 스마트머니를 따라가는 전략
    """

    def __init__(self):
        super().__init__("기관추종", "기관/외국인 순매수 추종")
        self.max_positions = 5
        self.position_size_rate = 0.17
        self.min_institutional_buy = 10_000_000
        self.min_foreign_buy = 5_000_000

    def should_buy(self, stock_data: Dict, market_data: Dict, account: VirtualAccount) -> bool:
        if len(account.positions) >= self.max_positions:
            return False

        institutional_net_buy = stock_data.get('institutional_net_buy', 0)
        if institutional_net_buy < self.min_institutional_buy:
            return False

        foreign_net_buy = stock_data.get('foreign_net_buy', 0)

        if foreign_net_buy >= self.min_foreign_buy:
            pass

        broker_buy_count = stock_data.get('top_broker_buy_count', 0)
        if broker_buy_count >= 2:
            pass

        price_change = stock_data.get('change_rate', 0)
        if price_change < 1.0:
            return False

        return True

    def should_sell(self, position: VirtualPosition, current_price: int,
                    stock_data: Dict, days_held: int) -> tuple[bool, str]:
        position.update_price(current_price)
        pnl_rate = position.unrealized_pnl_rate

        if pnl_rate >= 8.0:
            return True, f"기관추종 익절 {pnl_rate:.1f}%"

        if pnl_rate <= -4.0:
            return True, f"기관추종 손절 {pnl_rate:.1f}%"

        institutional_net_buy = stock_data.get('institutional_net_buy', 0)
        foreign_net_buy = stock_data.get('foreign_net_buy', 0)

        if institutional_net_buy < -5_000_000 or foreign_net_buy < -5_000_000:
            return True, f"기관/외국인 순매도로 청산 {pnl_rate:.1f}%"

        if days_held >= 10:
            return True, f"보유 {days_held}일 경과"

        return False, ""


class VolumeRSIStrategy(DiverseTradingStrategy):
    """
    거래량 급증 + RSI 과매도/적정 조합 전략
    - 거래량이 급증하면서 RSI가 과매도 또는 적정 구간에 있을 때 진입
    - 단기 반등을 노리는 전략
    """

    def __init__(self):
        super().__init__("거래량RSI", "거래량 급증 + RSI 조합")
        self.max_positions = 6
        self.position_size_rate = 0.16
        self.min_volume_ratio = 2.5
        self.rsi_lower_bound = 25
        self.rsi_upper_bound = 60

    def should_buy(self, stock_data: Dict, market_data: Dict, account: VirtualAccount) -> bool:
        if len(account.positions) >= self.max_positions:
            return False

        volume = stock_data.get('volume', 0)
        avg_volume = stock_data.get('avg_volume')

        if avg_volume and avg_volume > 0:
            volume_ratio = volume / avg_volume
            if volume_ratio < self.min_volume_ratio:
                return False
        else:
            if volume < 1_000_000:
                return False

        rsi = stock_data.get('rsi')
        if rsi is not None:
            if not (self.rsi_lower_bound <= rsi <= self.rsi_upper_bound):
                return False
        else:
            price_change = stock_data.get('change_rate', 0)
            if price_change > 10.0:
                return False

        execution_intensity = stock_data.get('execution_intensity')
        if execution_intensity and execution_intensity < 80:
            return False

        price_change = stock_data.get('change_rate', 0)
        if price_change < 0.5:
            return False

        return True

    def should_sell(self, position: VirtualPosition, current_price: int,
                    stock_data: Dict, days_held: int) -> tuple[bool, str]:
        position.update_price(current_price)
        pnl_rate = position.unrealized_pnl_rate

        if pnl_rate >= 7.0:
            return True, f"거래량RSI 익절 {pnl_rate:.1f}%"

        if pnl_rate <= -3.5:
            return True, f"거래량RSI 손절 {pnl_rate:.1f}%"

        rsi = stock_data.get('rsi')
        if rsi and rsi > 75 and pnl_rate > 3.0:
            return True, f"RSI 과열 청산 {pnl_rate:.1f}%"

        volume = stock_data.get('volume', 0)
        avg_volume = stock_data.get('avg_volume')
        if avg_volume and avg_volume > 0:
            volume_ratio = volume / avg_volume
            if volume_ratio < 0.8 and pnl_rate < 2.0:
                return True, f"거래량 급감 청산 {pnl_rate:.1f}%"

        if days_held >= 5:
            return True, f"보유 {days_held}일 경과"

        return False, ""


def create_all_diverse_strategies() -> list:
    """v5.7.5: 12가지 다양한 전략 생성 (10개 → 12개 확장)"""
    return [
        MomentumStrategy(),
        MeanReversionStrategy(),
        BreakoutStrategy(),
        ValueInvestingStrategy(),
        SwingTradingStrategy(),
        MACDStrategy(),
        ContrarianStrategy(),
        SectorRotationStrategy(),
        HotStockStrategy(),
        DividendGrowthStrategy(),
        InstitutionalFollowingStrategy(),
        VolumeRSIStrategy()
    ]


def get_strategy_descriptions() -> Dict[str, str]:
    """전략별 상세 설명 (v5.7.5: 12개)"""
    return {
        "모멘텀추세": "강한 상승 추세를 따라가는 전략. 거래량 급증 + 주가 상승 시 진입.",
        "평균회귀": "과매도 구간 반등 포착. RSI 30 이하에서 진입.",
        "돌파매매": "52주 신고가 돌파 시 진입. 큰 수익 추구.",
        "가치투자": "저평가 우량주 장기 보유. PER/PBR 낮고 배당 높은 종목.",
        "스윙매매": "단기 변동성 활용. 볼린저밴드 하단 매수, 상단 매도.",
        "MACD크로스": "MACD 지표 기반. 골든크로스 매수, 데드크로스 매도.",
        "역발상": "시장 감정의 반대편 베팅. 공포 시 매수, 탐욕 시 매도.",
        "섹터순환": "경기 사이클에 따른 섹터 선택. 경기 확장기엔 IT, 둔화기엔 필수소비재.",
        "급등추격": "당일 급등주 단타. 빠른 익절/손절.",
        "배당성장": "배당 성장주 장기 보유. 안정적 현금 흐름.",
        "기관추종": "기관/외국인 순매수 추종. 스마트머니 따라가기.",
        "거래량RSI": "거래량 급증 + RSI 과매도/적정 조합. 단기 반등 포착."
    }
