"""
Trade Executor Module
매매 실행 모듈
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TradeExecutor:
    """
    거래 실행자

    Features:
    - 매수/매도 실행
    - NXT 시장 규칙 적용
    - 데이터베이스 기록
    - 알림 발송
    """

    def __init__(
        self,
        order_api,
        account_api,
        market_api,
        dynamic_risk_manager,
        db_session,
        alert_manager,
        monitor
    ):
        self.order_api = order_api
        self.account_api = account_api
        self.market_api = market_api
        self.dynamic_risk_manager = dynamic_risk_manager
        self.db_session = db_session
        self.alert_manager = alert_manager
        self.monitor = monitor

        self.market_status = {}

    def set_market_status(self, market_status: Dict[str, Any]):
        """시장 상태 설정"""
        self.market_status = market_status

    def execute_buy(
        self,
        candidate,
        scoring_result
    ) -> bool:
        """
        매수 실행

        Args:
            candidate: 매수 후보
            scoring_result: 스코어링 결과

        Returns:
            성공 여부
        """
        try:
            if self.market_status.get('can_cancel_only'):
                logger.warning(f"⚠️  {self.market_status['market_type']}: 신규 매수 주문 불가")
                return False

            stock_code = candidate.code
            stock_name = candidate.name
            current_price = candidate.price

            deposit = self.account_api.get_deposit()
            available_cash = int(str(deposit.get('100stk_ord_alow_amt', '0')).replace(',', '')) if deposit else 0

            quantity = self.dynamic_risk_manager.calculate_position_size(
                stock_price=current_price,
                available_cash=available_cash
            )

            if quantity == 0:
                logger.warning("매수 가능 수량 0")
                return False

            total_amount = current_price * quantity

            logger.info(
                f"💳 {stock_name} 매수 실행: {quantity}주 @ {current_price:,}원 "
                f"(총 {total_amount:,}원)"
            )

            order_type = self._determine_order_type()

            order_result = self.order_api.buy(
                stock_code=stock_code,
                quantity=quantity,
                price=current_price,
                order_type=order_type
            )

            if order_result:
                order_no = order_result.get('order_no', '')

                self._record_trade(
                    stock_code=stock_code,
                    stock_name=stock_name,
                    action='buy',
                    quantity=quantity,
                    price=current_price,
                    total_amount=total_amount,
                    ai_score=getattr(candidate, 'ai_confidence', 0.5),
                    ai_signal=getattr(candidate, 'ai_signal', 'unknown'),
                    scoring_total=scoring_result.total_score,
                    scoring_percentage=scoring_result.percentage
                )

                logger.info(f"✅ {stock_name} 매수 성공 (주문번호: {order_no})")

                self.alert_manager.alert_position_opened(
                    stock_code=stock_code,
                    stock_name=stock_name,
                    buy_price=current_price,
                    quantity=quantity
                )

                self.monitor.log_activity(
                    'buy',
                    f'✅ {stock_name} 매수: {quantity}주 @ {current_price:,}원',
                    level='success'
                )

                return True
            else:
                logger.error("매수 주문 실패")
                return False

        except Exception as e:
            logger.error(f"매수 실행 실패: {e}", exc_info=True)
            return False

    def execute_sell(
        self,
        stock_code: str,
        stock_name: str,
        quantity: int,
        price: int,
        profit_loss: int,
        profit_loss_rate: float,
        reason: str
    ) -> bool:
        """
        매도 실행

        Returns:
            성공 여부
        """
        try:
            if self.market_status.get('can_cancel_only'):
                logger.warning(f"⚠️  {self.market_status['market_type']}: 신규 매도 주문 불가")
                return False

            logger.info(
                f"💸 {stock_name} 매도 실행: {quantity}주 @ {price:,}원 "
                f"(손익: {profit_loss:+,}원, {profit_loss_rate:+.2f}%)"
            )

            order_type = self._determine_order_type()

            order_result = self.order_api.sell(
                stock_code=stock_code,
                quantity=quantity,
                price=price,
                order_type=order_type
            )

            if order_result:
                order_no = order_result.get('order_no', '')

                self._record_trade(
                    stock_code=stock_code,
                    stock_name=stock_name,
                    action='sell',
                    quantity=quantity,
                    price=price,
                    total_amount=price * quantity,
                    profit_loss=profit_loss,
                    profit_loss_ratio=profit_loss_rate / 100,
                    notes=reason
                )

                log_level = 'success' if profit_loss >= 0 else 'warning'
                logger.info(f"✅ {stock_name} 매도 성공 (주문번호: {order_no})")

                self.alert_manager.alert_position_closed(
                    stock_code=stock_code,
                    stock_name=stock_name,
                    sell_price=price,
                    profit_loss_rate=profit_loss_rate,
                    profit_loss_amount=profit_loss,
                    reason=reason
                )

                self.monitor.log_activity(
                    'sell',
                    f'✅ {stock_name} 매도: {quantity}주 @ {price:,}원 (손익: {profit_loss:+,}원)',
                    level=log_level
                )

                return True
            else:
                logger.error("매도 주문 실패")
                return False

        except Exception as e:
            logger.error(f"매도 실행 실패: {e}", exc_info=True)
            return False

    def _determine_order_type(self) -> str:
        """주문 유형 결정 (시간대별)"""

        from utils.trading_date import is_nxt_hours
        from datetime import datetime

        if is_nxt_hours():
            now = datetime.now()
            if now.hour == 8:
                return '61'
            else:
                return '81'
        else:
            return '0'

    def _record_trade(self, **kwargs):
        """거래 기록"""

        try:
            from database import Trade

            trade = Trade(
                risk_mode=self.dynamic_risk_manager.current_mode.value,
                **kwargs
            )

            self.db_session.add(trade)
            self.db_session.commit()

        except Exception as e:
            logger.error(f"거래 기록 실패: {e}")
