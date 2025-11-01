"""
AutoTrade Pro v4.0 - 변동성 돌파 전략
래리 윌리엄스 변동성 돌파 전략 구현

전략 개요:
- 전일 변동폭(고가-저가)의 K배만큼 시가에서 상승하면 매수
- 당일 종가까지 보유 후 청산
- 거래량 필터 적용 가능
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, time

logger = logging.getLogger(__name__)


class VolatilityBreakoutStrategy:
    """변동성 돌파 전략"""

    def __init__(self, settings: Dict[str, Any] = None):
        """
        초기화

        Args:
            settings: 전략 설정
                {
                    'k_value': 0.5,                # 변동폭 승수 (0.3 ~ 0.7)
                    'entry_time': '09:05',         # 진입 시각
                    'exit_time': '15:15',          # 청산 시각
                    'use_volume_filter': True,     # 거래량 필터 사용
                    'min_volume_ratio': 1.2,       # 최소 거래량 비율 (평균 대비)
                    'stop_loss_pct': 0.03          # 손절 비율 (3%)
                }
        """
        self.settings = settings or {}
        self.k_value = self.settings.get('k_value', 0.5)
        self.entry_time = self._parse_time(self.settings.get('entry_time', '09:05'))
        self.exit_time = self._parse_time(self.settings.get('exit_time', '15:15'))
        self.use_volume_filter = self.settings.get('use_volume_filter', True)
        self.min_volume_ratio = self.settings.get('min_volume_ratio', 1.2)
        self.stop_loss_pct = self.settings.get('stop_loss_pct', 0.03)

        # 상태 관리
        self.positions: Dict[str, Dict] = {}  # 보유 포지션
        self.daily_range: Dict[str, float] = {}  # 전일 변동폭

        logger.info(
            f"변동성 돌파 전략 초기화: K={self.k_value}, "
            f"진입={self.entry_time}, 청산={self.exit_time}"
        )

    def _parse_time(self, time_str: str) -> time:
        """시간 문자열 파싱"""
        hour, minute = map(int, time_str.split(':'))
        return time(hour, minute)

    def update_daily_range(
        self,
        stock_code: str,
        yesterday_high: float,
        yesterday_low: float,
        yesterday_close: float
    ):
        """
        전일 데이터 업데이트

        Args:
            stock_code: 종목 코드
            yesterday_high: 전일 고가
            yesterday_low: 전일 저가
            yesterday_close: 전일 종가
        """
        range_value = yesterday_high - yesterday_low
        self.daily_range[stock_code] = {
            'range': range_value,
            'close': yesterday_close,
            'high': yesterday_high,
            'low': yesterday_low
        }

        logger.debug(
            f"[{stock_code}] 전일 데이터: "
            f"변동폭={range_value:,}, 종가={yesterday_close:,}"
        )

    def check_entry_signal(
        self,
        stock_code: str,
        current_time: time,
        today_open: float,
        current_price: float,
        current_volume: float,
        avg_volume: float
    ) -> tuple[bool, Optional[str]]:
        """
        매수 신호 체크

        Args:
            stock_code: 종목 코드
            current_time: 현재 시각
            today_open: 당일 시가
            current_price: 현재가
            current_volume: 현재 거래량
            avg_volume: 평균 거래량

        Returns:
            (should_buy, reason)
        """
        # 시간 체크
        if current_time < self.entry_time:
            return False, "아직 진입 시간 아님"

        # 이미 보유 중인지 체크
        if stock_code in self.positions:
            return False, "이미 보유 중"

        # 전일 데이터 확인
        if stock_code not in self.daily_range:
            return False, "전일 데이터 없음"

        daily_data = self.daily_range[stock_code]
        range_value = daily_data['range']

        # 목표가 계산
        target_price = today_open + (range_value * self.k_value)

        # 돌파 여부 체크
        if current_price < target_price:
            return False, f"목표가 미달 (현재={current_price:,}, 목표={target_price:,})"

        # 거래량 필터
        if self.use_volume_filter:
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            if volume_ratio < self.min_volume_ratio:
                return False, (
                    f"거래량 부족 (현재 비율={volume_ratio:.2f}, "
                    f"최소={self.min_volume_ratio:.2f})"
                )

        logger.info(
            f"[{stock_code}] 변동성 돌파 매수 신호! "
            f"현재가={current_price:,} > 목표가={target_price:,}"
        )
        return True, "변동성 돌파"

    def enter_position(
        self,
        stock_code: str,
        entry_price: float,
        quantity: int
    ):
        """포지션 진입"""
        stop_loss_price = entry_price * (1 - self.stop_loss_pct)

        self.positions[stock_code] = {
            'entry_price': entry_price,
            'quantity': quantity,
            'entry_time': datetime.now(),
            'stop_loss_price': stop_loss_price
        }

        logger.info(
            f"[{stock_code}] 포지션 진입: "
            f"가격={entry_price:,}, 수량={quantity}, 손절={stop_loss_price:,}"
        )

    def check_exit_signal(
        self,
        stock_code: str,
        current_time: time,
        current_price: float
    ) -> tuple[bool, Optional[str]]:
        """
        매도 신호 체크

        Args:
            stock_code: 종목 코드
            current_time: 현재 시각
            current_price: 현재가

        Returns:
            (should_sell, reason)
        """
        if stock_code not in self.positions:
            return False, None

        position = self.positions[stock_code]

        # 손절 체크
        if current_price <= position['stop_loss_price']:
            logger.warning(
                f"[{stock_code}] 손절 신호! "
                f"현재가={current_price:,} <= 손절가={position['stop_loss_price']:,}"
            )
            return True, "STOP_LOSS"

        # 청산 시간 체크
        if current_time >= self.exit_time:
            logger.info(f"[{stock_code}] 청산 시간 도래")
            return True, "EXIT_TIME"

        return False, None

    def exit_position(self, stock_code: str, exit_price: float):
        """포지션 청산"""
        if stock_code not in self.positions:
            logger.warning(f"[{stock_code}] 보유 포지션 없음")
            return

        position = self.positions[stock_code]
        profit_loss = (exit_price - position['entry_price']) * position['quantity']
        profit_loss_pct = (exit_price - position['entry_price']) / position['entry_price'] * 100

        logger.info(
            f"[{stock_code}] 포지션 청산: "
            f"진입={position['entry_price']:,}, 청산={exit_price:,}, "
            f"손익={profit_loss:,.0f}원 ({profit_loss_pct:+.2f}%)"
        )

        del self.positions[stock_code]

    def get_position(self, stock_code: str) -> Optional[Dict]:
        """포지션 정보 조회"""
        return self.positions.get(stock_code)

    def get_all_positions(self) -> Dict[str, Dict]:
        """모든 포지션 조회"""
        return self.positions.copy()

    def calculate_position_size(
        self,
        total_capital: float,
        current_price: float,
        max_position_ratio: float = 0.10
    ) -> int:
        """
        포지션 크기 계산

        Args:
            total_capital: 총 자본금
            current_price: 현재가
            max_position_ratio: 최대 포지션 비율 (10%)

        Returns:
            매수 수량
        """
        max_amount = total_capital * max_position_ratio
        quantity = int(max_amount / current_price)
        return max(1, quantity)


# 테스트
if __name__ == "__main__":
    strategy = VolatilityBreakoutStrategy()

    # 전일 데이터 설정
    strategy.update_daily_range(
        "005930",
        yesterday_high=72000,
        yesterday_low=70000,
        yesterday_close=71000
    )

    # 매수 신호 체크
    should_buy, reason = strategy.check_entry_signal(
        "005930",
        current_time=time(9, 10),
        today_open=71000,
        current_price=72000,  # 시가 + 변동폭*0.5 = 71000 + 1000 = 72000
        current_volume=1000000,
        avg_volume=800000
    )

    print(f"매수 신호: {should_buy}, 사유: {reason}")
