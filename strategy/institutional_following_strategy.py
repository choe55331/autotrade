"""
AutoTrade Pro v4.0 - 수급 추종 전략
외국인/기관의 대량 매수를 포착하여 추종 매매

주요 기능:
- 외국인/기관 순매수 감지
- 연속 매수일 추적
- 수급 강도 계산
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class InstitutionalData:
    """수급 데이터"""
    date: datetime
    stock_code: str
    foreign_net_buy: float  # 외국인 순매수 (원)
    institutional_net_buy: float  # 기관 순매수 (원)
    total_net_buy: float  # 합계


class InstitutionalFollowingStrategy:
    """수급 추종 전략"""

    def __init__(self, settings: Dict[str, Any] = None):
        """
        초기화

        Args:
            settings:
                {
                    'min_net_buy_volume': 1000000000,  # 최소 순매수 (10억)
                    'consecutive_days': 3,             # 연속 매수일
                    'lookback_days': 10                # 분석 기간
                }
        """
        self.settings = settings or {}
        self.min_net_buy_volume = self.settings.get('min_net_buy_volume', 1000000000)
        self.consecutive_days = self.settings.get('consecutive_days', 3)
        self.lookback_days = self.settings.get('lookback_days', 10)

        # 수급 데이터 저장
        self.data_history: Dict[str, deque] = {}

        logger.info(f"수급 추종 전략 초기화: 최소매수={self.min_net_buy_volume/1e8:.0f}억")

    def add_institutional_data(self, data: InstitutionalData):
        """수급 데이터 추가"""
        if data.stock_code not in self.data_history:
            self.data_history[data.stock_code] = deque(maxlen=self.lookback_days)

        self.data_history[data.stock_code].append(data)

    def check_buy_signal(self, stock_code: str) -> tuple[bool, Optional[str]]:
        """
        매수 신호 확인

        Args:
            stock_code: 종목 코드

        Returns:
            (should_buy, reason)
        """
        if stock_code not in self.data_history:
            return False, "수급 데이터 없음"

        history = list(self.data_history[stock_code])

        if len(history) < self.consecutive_days:
            return False, f"데이터 부족 ({len(history)}일)"

        # 최근 N일 연속 순매수 확인
        recent_data = history[-self.consecutive_days:]

        consecutive_buy_days = 0
        total_net_buy = 0

        for data in recent_data:
            if data.total_net_buy > 0:
                consecutive_buy_days += 1
                total_net_buy += data.total_net_buy
            else:
                consecutive_buy_days = 0  # 연속성 끊김

        if consecutive_buy_days >= self.consecutive_days:
            if total_net_buy >= self.min_net_buy_volume:
                logger.info(
                    f"[{stock_code}] 수급 추종 매수 신호: "
                    f"{consecutive_buy_days}일 연속 순매수 {total_net_buy/1e8:.0f}억"
                )
                return True, f"{consecutive_buy_days}일 연속 순매수 ({total_net_buy/1e8:.0f}억)"

        return False, "수급 약함"

    def calculate_buying_strength(self, stock_code: str) -> float:
        """
        수급 강도 계산 (0.0 ~ 1.0)

        Args:
            stock_code: 종목 코드

        Returns:
            수급 강도
        """
        if stock_code not in self.data_history:
            return 0.0

        history = list(self.data_history[stock_code])
        if not history:
            return 0.0

        # 최근 N일 순매수 합계
        recent_net_buy = sum(data.total_net_buy for data in history[-5:])

        # 정규화 (10억 = 1.0)
        strength = min(abs(recent_net_buy) / 1000000000, 1.0)

        return strength if recent_net_buy > 0 else 0.0

    def get_top_stocks_by_institutional_buying(
        self,
        n: int = 10
    ) -> List[tuple[str, float]]:
        """
        수급이 강한 상위 종목 조회

        Args:
            n: 상위 N개

        Returns:
            [(stock_code, strength), ...]
        """
        stocks_with_strength = []

        for stock_code in self.data_history.keys():
            strength = self.calculate_buying_strength(stock_code)
            if strength > 0:
                stocks_with_strength.append((stock_code, strength))

        stocks_with_strength.sort(key=lambda x: x[1], reverse=True)

        return stocks_with_strength[:n]


# 테스트
if __name__ == "__main__":
    strategy = InstitutionalFollowingStrategy()

    # 샘플 데이터 추가
    base_date = datetime.now() - timedelta(days=10)

    for i in range(10):
        date = base_date + timedelta(days=i)

        # 삼성전자 - 연속 순매수
        data = InstitutionalData(
            date=date,
            stock_code="005930",
            foreign_net_buy=500000000,  # 5억
            institutional_net_buy=700000000,  # 7억
            total_net_buy=1200000000  # 12억
        )
        strategy.add_institutional_data(data)

    # 매수 신호 확인
    should_buy, reason = strategy.check_buy_signal("005930")
    print(f"매수 신호: {should_buy} ({reason})")

    # 상위 종목
    top_stocks = strategy.get_top_stocks_by_institutional_buying(5)
    print("\n수급 강한 상위 종목:")
    for code, strength in top_stocks:
        print(f"  {code}: {strength:.2f}")
