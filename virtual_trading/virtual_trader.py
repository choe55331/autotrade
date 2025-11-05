"""
virtual_trading/virtual_trader.py
가상 트레이더 - 여러 전략 동시 테스트

v5.7.5: 12가지 다양한 실전 매매 전략 적용 (10개 → 12개 확장)
"""
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import logging

from .virtual_account import VirtualAccount, VirtualPosition
from .diverse_strategies import (
    create_all_diverse_strategies,
    DiverseTradingStrategy,
    get_strategy_descriptions
)


logger = logging.getLogger(__name__)


class TradingStrategy:
    """매수/매도 전략 정의"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

        # 매수 조건
        self.min_score = 150  # 최소 점수
        self.min_ai_confidence = 0.5
        self.require_ai_approval = True

        # 매도 조건
        self.take_profit_rate = 0.10  # 익절 10%
        self.stop_loss_rate = -0.05   # 손절 -5%
        self.trailing_stop = False
        self.max_holding_days = 5     # 최대 보유 기간

        # 포지션 관리
        self.max_positions = 5
        self.position_size_rate = 0.15  # 1회 매수 금액 비율 (15%)

    def should_buy(self, stock_data: Dict, ai_analysis: Dict, account: VirtualAccount) -> bool:
        """매수 조건 확인"""
        # 점수 확인 (stock_data 또는 ai_analysis에서 가져오기)
        score = stock_data.get('score', ai_analysis.get('score', 0))
        if score < self.min_score:
            return False

        # AI 승인 확인
        if self.require_ai_approval:
            ai_signal = ai_analysis.get('signal', 'hold')
            if ai_signal != 'buy':
                return False

        # 최대 포지션 확인
        if len(account.positions) >= self.max_positions:
            return False

        # 중복 매수 방지
        stock_code = stock_data.get('stock_code')
        if account.has_position(stock_code):
            return False

        return True

    def calculate_quantity(self, price: int, account: VirtualAccount) -> int:
        """매수 수량 계산"""
        # 계좌 잔고의 일정 비율로 매수
        available_cash = account.cash
        target_amount = int(available_cash * self.position_size_rate)

        quantity = target_amount // price
        return max(quantity, 1)  # 최소 1주

    def should_sell(self, position: VirtualPosition, current_price: int,
                    days_held: int) -> tuple[bool, str]:
        """
        매도 조건 확인

        Returns:
            (should_sell, reason)
        """
        position.update_price(current_price)
        pnl_rate = position.unrealized_pnl_rate

        # 익절
        if pnl_rate >= self.take_profit_rate * 100:
            return True, f"익절 {pnl_rate:.1f}%"

        # 손절
        if pnl_rate <= self.stop_loss_rate * 100:
            return True, f"손절 {pnl_rate:.1f}%"

        # 보유 기간 초과
        if days_held >= self.max_holding_days:
            return True, f"보유기간 {days_held}일 초과"

        return False, ""


class VirtualTrader:
    """가상 트레이더 - 여러 전략 동시 테스트"""

    def __init__(self, initial_cash: int = 10_000_000):
        """
        초기화

        Args:
            initial_cash: 각 계좌의 초기 자금
        """
        self.initial_cash = initial_cash

        # 여러 전략의 가상 계좌
        self.accounts: Dict[str, VirtualAccount] = {}
        self.strategies: Dict[str, TradingStrategy] = {}

        # 기본 전략들 생성
        self._create_default_strategies()

        logger.info(f"💰 가상 트레이더 초기화 완료 (계좌당 {initial_cash:,}원)")

    def _create_default_strategies(self):
        """
        기본 전략들 생성

        v5.7.5: 12가지 다양한 실전 매매 전략 적용 (10개 → 12개 확장)
        - 모멘텀추세, 평균회귀, 돌파매매, 가치투자, 스윙매매
        - MACD크로스, 역발상, 섹터순환, 급등추격, 배당성장
        - 기관추종, 거래량RSI (v5.7.5 신규)
        """
        diverse_strategies = create_all_diverse_strategies()

        for strategy in diverse_strategies:
            self.add_diverse_strategy(strategy)

        logger.info(f"✅ 12가지 다양한 전략 생성 완료 (v5.7.5)")

        # 전략별 설명 로깅
        descriptions = get_strategy_descriptions()
        for name, desc in descriptions.items():
            logger.info(f"  - {name}: {desc}")

    def add_strategy(self, strategy: TradingStrategy):
        """전략 추가 (레거시 TradingStrategy)"""
        self.strategies[strategy.name] = strategy
        self.accounts[strategy.name] = VirtualAccount(
            initial_cash=self.initial_cash,
            name=f"가상계좌-{strategy.name}"
        )
        logger.info(f"📊 전략 추가: {strategy.name}")

    def add_diverse_strategy(self, strategy: DiverseTradingStrategy):
        """v5.7: 다양한 전략 추가 (DiverseTradingStrategy)"""
        self.strategies[strategy.name] = strategy
        self.accounts[strategy.name] = VirtualAccount(
            initial_cash=self.initial_cash,
            name=f"가상계좌-{strategy.name}"
        )
        logger.info(f"📊 전략 추가: {strategy.name} - {strategy.description}")

    def process_buy_signal(self, stock_data: Dict, ai_analysis: Dict = None, market_data: Dict = None):
        """
        매수 시그널 처리 - 모든 전략에 대해

        Args:
            stock_data: 종목 데이터 (code, name, price, score 등)
            ai_analysis: AI 분석 결과 (signal, reasons 등) - 레거시 전략용
            market_data: 시장 데이터 (fear_greed_index, economic_cycle 등) - 다양한 전략용
        """
        stock_code = stock_data.get('stock_code')
        stock_name = stock_data.get('stock_name')
        price = stock_data.get('current_price', 0)

        if price == 0:
            return

        # 기본값 설정
        if ai_analysis is None:
            ai_analysis = {}
        if market_data is None:
            market_data = {}

        # 각 전략별로 매수 판단
        for strategy_name, strategy in self.strategies.items():
            account = self.accounts[strategy_name]

            # v5.7: 다양한 전략 타입 지원
            try:
                if isinstance(strategy, DiverseTradingStrategy):
                    # 새로운 다양한 전략
                    should_buy = strategy.should_buy(stock_data, market_data, account)
                else:
                    # 레거시 전략
                    should_buy = strategy.should_buy(stock_data, ai_analysis, account)

                if should_buy:
                    # 수량 계산
                    quantity = strategy.calculate_quantity(price, account)

                    if quantity > 0 and account.can_buy(price, quantity):
                        # 가상 매수 실행
                        success = account.buy(
                            stock_code=stock_code,
                            stock_name=stock_name,
                            price=price,
                            quantity=quantity,
                            strategy_name=strategy_name
                        )

                        if success:
                            logger.info(
                                f"🔵 [가상매수-{strategy_name}] {stock_name} "
                                f"{quantity}주 @ {price:,}원 "
                                f"(잔고: {account.cash:,}원)"
                            )
            except Exception as e:
                logger.error(f"전략 {strategy_name} 매수 처리 오류: {e}")

    def check_sell_conditions(self, price_data: Dict[str, int], stock_data_dict: Dict[str, Dict] = None):
        """
        매도 조건 확인 - 모든 계좌의 포지션 확인

        Args:
            price_data: {stock_code: current_price}
            stock_data_dict: {stock_code: stock_data} - v5.7: 다양한 전략용 추가 데이터
        """
        if stock_data_dict is None:
            stock_data_dict = {}

        for strategy_name, account in self.accounts.items():
            strategy = self.strategies[strategy_name]

            # 각 포지션 확인
            for stock_code, position in list(account.positions.items()):
                if stock_code not in price_data:
                    continue

                current_price = price_data[stock_code]

                # 보유 기간 계산
                days_held = (datetime.now() - position.entry_time).days

                # v5.7: 다양한 전략 타입 지원
                try:
                    if isinstance(strategy, DiverseTradingStrategy):
                        # 새로운 다양한 전략 - stock_data 필요
                        stock_data = stock_data_dict.get(stock_code, {})
                        should_sell, reason = strategy.should_sell(
                            position, current_price, stock_data, days_held
                        )
                    else:
                        # 레거시 전략
                        should_sell, reason = strategy.should_sell(
                            position, current_price, days_held
                        )

                    if should_sell:
                        # 가상 매도 실행
                        realized_pnl = account.sell(
                            stock_code=stock_code,
                            price=current_price,
                            reason=reason
                        )

                        if realized_pnl is not None:
                            pnl_sign = "+" if realized_pnl > 0 else ""
                            logger.info(
                                f"🔴 [가상매도-{strategy_name}] {position.stock_name} "
                                f"{position.quantity}주 @ {current_price:,}원 "
                                f"({reason}, {pnl_sign}{realized_pnl:,}원)"
                            )
                except Exception as e:
                    logger.error(f"전략 {strategy_name} 매도 처리 오류 ({stock_code}): {e}")

    def update_all_prices(self, price_data: Dict[str, int]):
        """모든 계좌의 포지션 가격 업데이트"""
        for account in self.accounts.values():
            account.update_positions(price_data)

    def get_all_summaries(self) -> Dict[str, Dict]:
        """모든 계좌 요약"""
        summaries = {}
        for strategy_name, account in self.accounts.items():
            summaries[strategy_name] = account.get_summary()
        return summaries

    def get_best_strategy(self) -> Optional[str]:
        """최고 성과 전략"""
        if not self.accounts:
            return None

        best_strategy = None
        best_pnl_rate = float('-inf')

        for strategy_name, account in self.accounts.items():
            pnl_rate = account.get_total_pnl_rate()
            if pnl_rate > best_pnl_rate:
                best_pnl_rate = pnl_rate
                best_strategy = strategy_name

        return best_strategy

    def print_performance(self):
        """성과 출력"""
        print("\n" + "="*80)
        print("💰 가상매매 성과 요약")
        print("="*80)

        summaries = self.get_all_summaries()

        for strategy_name, summary in summaries.items():
            pnl = summary['total_pnl']
            pnl_rate = summary['total_pnl_rate']
            win_rate = summary['win_rate']

            pnl_sign = "📈" if pnl >= 0 else "📉"
            pnl_color = "+" if pnl >= 0 else ""

            print(f"\n[{strategy_name}]")
            print(f"  자산: {summary['total_value']:,}원 (초기: {summary['initial_cash']:,}원)")
            print(f"  손익: {pnl_color}{pnl:,}원 ({pnl_color}{pnl_rate:.2f}%) {pnl_sign}")
            print(f"  거래: {summary['total_trades']}건 "
                  f"(승: {summary['winning_trades']}, 패: {summary['losing_trades']})")
            print(f"  승률: {win_rate:.1f}%")
            print(f"  포지션: {summary['position_count']}개")

            # 거래 내역 출력 (최근 10건)
            account = self.accounts[strategy_name]
            if account.trade_history:
                print(f"\n  📝 거래 내역 (최근 {min(10, len(account.trade_history))}건):")
                for i, trade in enumerate(account.trade_history[-10:], 1):
                    trade_type = trade['type']
                    timestamp = trade.get('timestamp', 'N/A')
                    # ISO 형식 파싱하여 읽기 쉽게 변환
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        time_str = dt.strftime('%m/%d %H:%M:%S')
                    except:
                        time_str = timestamp

                    stock_name = trade.get('stock_name', trade.get('stock_code', 'Unknown'))
                    price = trade.get('price', 0)
                    quantity = trade.get('quantity', 0)
                    amount = trade.get('amount', 0)

                    if trade_type == 'buy':
                        print(f"     {i}. [{time_str}] 🔵 매수 {stock_name} {quantity}주 @ {price:,}원 = {amount:,}원")
                    else:  # sell
                        pnl = trade.get('realized_pnl', 0)
                        pnl_rate = trade.get('realized_pnl_rate', 0.0)
                        reason = trade.get('reason', '')
                        pnl_sign = "✅" if pnl > 0 else "❌"
                        print(f"     {i}. [{time_str}] 🔴 매도 {stock_name} {quantity}주 @ {price:,}원 "
                              f"({pnl:+,}원, {pnl_rate:+.2f}%) {pnl_sign} [{reason}]")

        # 최고 전략
        best = self.get_best_strategy()
        if best:
            print(f"\n🏆 최고 성과: {best}")

        print("="*80 + "\n")

    def save_all_states(self, base_dir: str = "data/virtual_trading"):
        """모든 계좌 상태 저장"""
        for strategy_name, account in self.accounts.items():
            filename = f"{strategy_name}.json"
            filepath = f"{base_dir}/{filename}"
            account.save_state(filepath)

    def load_all_states(self, base_dir: str = "data/virtual_trading"):
        """모든 계좌 상태 로드"""
        for strategy_name, account in self.accounts.items():
            filename = f"{strategy_name}.json"
            filepath = f"{base_dir}/{filename}"
            account.load_state(filepath)


__all__ = ['VirtualTrader', 'TradingStrategy']
