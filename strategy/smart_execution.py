"""
Smart Order Execution Algorithms - v5.13
TWAP, VWAP, Iceberg, POV, Implementation Shortfall
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import logging
import time

logger = logging.getLogger(__name__)


class ExecutionAlgorithm(Enum):
    """실행 알고리즘 타입"""
    TWAP = "twap"  # Time-Weighted Average Price
    VWAP = "vwap"  # Volume-Weighted Average Price
    ICEBERG = "iceberg"  # Iceberg Order
    POV = "pov"  # Percentage of Volume
    IMPLEMENTATION_SHORTFALL = "implementation_shortfall"
    ADAPTIVE = "adaptive"  # Adaptive algorithm


@dataclass
class OrderSlice:
    """주문 슬라이스"""
    slice_id: str
    stock_code: str
    quantity: int
    target_price: Optional[float]
    scheduled_time: datetime
    urgency: float  # 0-1 (1 = most urgent)
    metadata: Dict[str, Any]


@dataclass
class ExecutionResult:
    """실행 결과"""
    order_id: str
    stock_code: str
    total_quantity: int
    executed_quantity: int
    slices_executed: int
    slices_total: int
    average_price: float
    total_cost: float
    slippage: float  # vs target price
    slippage_bps: float  # basis points
    execution_time_seconds: float
    algorithm_used: ExecutionAlgorithm
    success: bool
    error_message: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class MarketData:
    """시장 데이터"""
    stock_code: str
    timestamp: datetime
    price: float
    volume: int
    bid_price: float
    ask_price: float
    bid_volume: int
    ask_volume: int


class SmartOrderExecutor:
    """
    스마트 주문 실행 시스템

    Algorithms:
    - TWAP: Time-Weighted Average Price
    - VWAP: Volume-Weighted Average Price
    - Iceberg: Hidden volume orders
    - POV: Percentage of Volume
    - Implementation Shortfall: Minimize cost vs benchmark
    """

    def __init__(self):
        """Initialize executor"""
        self.active_orders: Dict[str, List[OrderSlice]] = {}
        self.execution_history: List[ExecutionResult] = []

        logger.info("Smart Order Executor initialized")

    def execute_order(self,
                     order_id: str,
                     stock_code: str,
                     stock_name: str,
                     quantity: int,
                     side: str,  # 'buy' or 'sell'
                     algorithm: ExecutionAlgorithm,
                     duration_minutes: int,
                     current_price: float,
                     market_data: Optional[List[MarketData]] = None,
                     params: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """
        주문 실행

        Args:
            order_id: 주문 ID
            stock_code: 종목 코드
            stock_name: 종목명
            quantity: 수량
            side: 매수/매도
            algorithm: 실행 알고리즘
            duration_minutes: 실행 기간 (분)
            current_price: 현재가
            market_data: 시장 데이터 (VWAP용)
            params: 알고리즘 파라미터

        Returns:
            ExecutionResult
        """
        logger.info(f"Executing order: {order_id}, {stock_name}, "
                   f"{quantity} shares, {algorithm.value}, {duration_minutes}min")

        start_time = datetime.now()

        if params is None:
            params = {}

        # Generate order slices
        if algorithm == ExecutionAlgorithm.TWAP:
            slices = self._generate_twap_slices(
                order_id, stock_code, quantity, duration_minutes, current_price
            )
        elif algorithm == ExecutionAlgorithm.VWAP:
            slices = self._generate_vwap_slices(
                order_id, stock_code, quantity, duration_minutes,
                current_price, market_data
            )
        elif algorithm == ExecutionAlgorithm.ICEBERG:
            slices = self._generate_iceberg_slices(
                order_id, stock_code, quantity, current_price,
                params.get('visible_quantity', quantity // 10)
            )
        elif algorithm == ExecutionAlgorithm.POV:
            slices = self._generate_pov_slices(
                order_id, stock_code, quantity, duration_minutes,
                current_price, params.get('participation_rate', 0.1)
            )
        elif algorithm == ExecutionAlgorithm.IMPLEMENTATION_SHORTFALL:
            slices = self._generate_is_slices(
                order_id, stock_code, quantity, duration_minutes,
                current_price, params.get('urgency', 0.5)
            )
        else:  # ADAPTIVE
            slices = self._generate_adaptive_slices(
                order_id, stock_code, quantity, duration_minutes,
                current_price, market_data
            )

        if not slices:
            return ExecutionResult(
                order_id=order_id,
                stock_code=stock_code,
                total_quantity=quantity,
                executed_quantity=0,
                slices_executed=0,
                slices_total=0,
                average_price=current_price,
                total_cost=0.0,
                slippage=0.0,
                slippage_bps=0.0,
                execution_time_seconds=0.0,
                algorithm_used=algorithm,
                success=False,
                error_message="Failed to generate order slices",
                metadata={}
            )

        # Store active order
        self.active_orders[order_id] = slices

        # Simulate execution
        result = self._simulate_execution(
            order_id, stock_code, quantity, slices,
            current_price, side, algorithm
        )

        # Store in history
        self.execution_history.append(result)

        execution_time = (datetime.now() - start_time).total_seconds()
        result.execution_time_seconds = execution_time

        logger.info(f"Order executed: {order_id}, "
                   f"{result.executed_quantity}/{result.total_quantity} shares, "
                   f"avg_price={result.average_price:,.0f}, "
                   f"slippage={result.slippage_bps:.1f}bps")

        return result

    def cancel_order(self, order_id: str) -> bool:
        """주문 취소"""
        if order_id in self.active_orders:
            del self.active_orders[order_id]
            logger.info(f"Order cancelled: {order_id}")
            return True
        return False

    def get_execution_stats(self) -> Dict[str, Any]:
        """실행 통계"""
        if not self.execution_history:
            return {
                'total_orders': 0,
                'successful_orders': 0,
                'avg_slippage_bps': 0.0,
                'total_volume': 0
            }

        successful = [r for r in self.execution_history if r.success]

        return {
            'total_orders': len(self.execution_history),
            'successful_orders': len(successful),
            'success_rate': len(successful) / len(self.execution_history) if self.execution_history else 0,
            'avg_slippage_bps': np.mean([r.slippage_bps for r in successful]) if successful else 0.0,
            'total_volume': sum(r.executed_quantity for r in self.execution_history),
            'total_cost': sum(r.total_cost for r in self.execution_history)
        }

    # ===== ALGORITHM IMPLEMENTATIONS =====

    def _generate_twap_slices(self, order_id: str, stock_code: str,
                              quantity: int, duration_minutes: int,
                              current_price: float) -> List[OrderSlice]:
        """
        TWAP (Time-Weighted Average Price)
        균등하게 시간에 분산하여 주문
        """
        num_slices = min(duration_minutes, 20)  # Max 20 slices
        slice_quantity = quantity // num_slices
        remainder = quantity % num_slices

        slices = []
        now = datetime.now()

        for i in range(num_slices):
            qty = slice_quantity + (1 if i < remainder else 0)

            slice_time = now + timedelta(minutes=i * (duration_minutes / num_slices))

            slice = OrderSlice(
                slice_id=f"{order_id}_twap_{i}",
                stock_code=stock_code,
                quantity=qty,
                target_price=None,  # Market order
                scheduled_time=slice_time,
                urgency=0.5,  # Neutral urgency
                metadata={'algorithm': 'twap', 'slice_index': i}
            )
            slices.append(slice)

        logger.info(f"Generated {len(slices)} TWAP slices")
        return slices

    def _generate_vwap_slices(self, order_id: str, stock_code: str,
                             quantity: int, duration_minutes: int,
                              current_price: float,
                              market_data: Optional[List[MarketData]]) -> List[OrderSlice]:
        """
        VWAP (Volume-Weighted Average Price)
        거래량 패턴에 따라 주문 분산
        """
        num_slices = min(duration_minutes, 20)

        # If no market data, fall back to TWAP
        if not market_data or len(market_data) < 10:
            logger.warning("Insufficient market data for VWAP, using TWAP")
            return self._generate_twap_slices(
                order_id, stock_code, quantity, duration_minutes, current_price
            )

        # Calculate volume profile
        volumes = [md.volume for md in market_data[-num_slices:]]
        total_volume = sum(volumes)

        if total_volume == 0:
            return self._generate_twap_slices(
                order_id, stock_code, quantity, duration_minutes, current_price
            )

        # Distribute quantity based on volume
        slices = []
        now = datetime.now()
        allocated = 0

        for i in range(num_slices):
            vol_weight = volumes[i] / total_volume if i < len(volumes) else 1.0 / num_slices
            slice_quantity = int(quantity * vol_weight)

            if i == num_slices - 1:
                slice_quantity = quantity - allocated  # Last slice gets remainder

            allocated += slice_quantity

            slice_time = now + timedelta(minutes=i * (duration_minutes / num_slices))

            slice = OrderSlice(
                slice_id=f"{order_id}_vwap_{i}",
                stock_code=stock_code,
                quantity=slice_quantity,
                target_price=None,
                scheduled_time=slice_time,
                urgency=0.5,
                metadata={'algorithm': 'vwap', 'volume_weight': vol_weight}
            )
            slices.append(slice)

        logger.info(f"Generated {len(slices)} VWAP slices")
        return slices

    def _generate_iceberg_slices(self, order_id: str, stock_code: str,
                                quantity: int, current_price: float,
                                visible_quantity: int) -> List[OrderSlice]:
        """
        Iceberg Order
        큰 주문을 작은 조각으로 나누어 일부만 노출
        """
        num_slices = max(1, quantity // visible_quantity)
        slices = []
        now = datetime.now()

        remaining = quantity
        for i in range(num_slices):
            slice_qty = min(visible_quantity, remaining)
            remaining -= slice_qty

            # Space out slices slightly
            slice_time = now + timedelta(seconds=i * 5)

            slice = OrderSlice(
                slice_id=f"{order_id}_iceberg_{i}",
                stock_code=stock_code,
                quantity=slice_qty,
                target_price=None,
                scheduled_time=slice_time,
                urgency=0.7,  # Higher urgency
                metadata={
                    'algorithm': 'iceberg',
                    'visible': True,
                    'hidden_remaining': remaining
                }
            )
            slices.append(slice)

        logger.info(f"Generated {len(slices)} Iceberg slices (visible={visible_quantity})")
        return slices

    def _generate_pov_slices(self, order_id: str, stock_code: str,
                            quantity: int, duration_minutes: int,
                            current_price: float,
                            participation_rate: float) -> List[OrderSlice]:
        """
        POV (Percentage of Volume)
        시장 거래량의 일정 비율로 주문
        """
        num_slices = min(duration_minutes, 20)

        # Assume average market volume
        assumed_market_volume_per_minute = 100000  # Mock value
        market_volume_per_slice = assumed_market_volume_per_minute * (duration_minutes / num_slices)

        slices = []
        now = datetime.now()
        allocated = 0

        for i in range(num_slices):
            # Calculate slice size based on participation rate
            slice_qty = int(market_volume_per_slice * participation_rate)
            slice_qty = min(slice_qty, quantity - allocated)

            if i == num_slices - 1:
                slice_qty = quantity - allocated  # Last slice

            allocated += slice_qty

            if slice_qty <= 0:
                break

            slice_time = now + timedelta(minutes=i * (duration_minutes / num_slices))

            slice = OrderSlice(
                slice_id=f"{order_id}_pov_{i}",
                stock_code=stock_code,
                quantity=slice_qty,
                target_price=None,
                scheduled_time=slice_time,
                urgency=0.6,
                metadata={
                    'algorithm': 'pov',
                    'participation_rate': participation_rate
                }
            )
            slices.append(slice)

        logger.info(f"Generated {len(slices)} POV slices (participation={participation_rate:.1%})")
        return slices

    def _generate_is_slices(self, order_id: str, stock_code: str,
                           quantity: int, duration_minutes: int,
                           current_price: float, urgency: float) -> List[OrderSlice]:
        """
        Implementation Shortfall
        시장 충격을 최소화하면서 빠르게 실행
        """
        # Higher urgency = fewer, larger slices
        # Lower urgency = more, smaller slices

        if urgency > 0.8:
            num_slices = 5  # Very urgent
        elif urgency > 0.6:
            num_slices = 10
        elif urgency > 0.4:
            num_slices = 15
        else:
            num_slices = 20  # Patient

        # Front-load for urgent orders
        slices = []
        now = datetime.now()
        allocated = 0

        for i in range(num_slices):
            # Weight factor: front-load if urgent
            if urgency > 0.5:
                weight = 1.5 - (i / num_slices)  # Decreasing
            else:
                weight = 0.5 + (i / num_slices)  # Increasing (patient)

            slice_qty = int((quantity / num_slices) * weight)
            slice_qty = min(slice_qty, quantity - allocated)

            if i == num_slices - 1:
                slice_qty = quantity - allocated

            allocated += slice_qty

            if slice_qty <= 0:
                break

            slice_time = now + timedelta(minutes=i * (duration_minutes / num_slices))

            slice = OrderSlice(
                slice_id=f"{order_id}_is_{i}",
                stock_code=stock_code,
                quantity=slice_qty,
                target_price=None,
                scheduled_time=slice_time,
                urgency=urgency,
                metadata={'algorithm': 'implementation_shortfall'}
            )
            slices.append(slice)

        logger.info(f"Generated {len(slices)} IS slices (urgency={urgency:.2f})")
        return slices

    def _generate_adaptive_slices(self, order_id: str, stock_code: str,
                                 quantity: int, duration_minutes: int,
                                 current_price: float,
                                 market_data: Optional[List[MarketData]]) -> List[OrderSlice]:
        """
        Adaptive Algorithm
        시장 상황에 따라 동적으로 조정
        """
        # Analyze market conditions
        if market_data and len(market_data) >= 10:
            recent_data = market_data[-10:]

            # Check volatility
            prices = [md.price for md in recent_data]
            volatility = np.std(prices) / np.mean(prices)

            # Check volume
            volumes = [md.volume for md in recent_data]
            avg_volume = np.mean(volumes)
            recent_volume = volumes[-1] if volumes else 0
            volume_spike = recent_volume / avg_volume if avg_volume > 0 else 1.0

            # Choose strategy based on conditions
            if volatility > 0.02:  # High volatility
                logger.info("High volatility detected, using TWAP")
                return self._generate_twap_slices(
                    order_id, stock_code, quantity, duration_minutes, current_price
                )
            elif volume_spike > 1.5:  # Volume spike
                logger.info("Volume spike detected, using POV")
                return self._generate_pov_slices(
                    order_id, stock_code, quantity, duration_minutes,
                    current_price, 0.15
                )
            else:  # Normal conditions
                logger.info("Normal conditions, using VWAP")
                return self._generate_vwap_slices(
                    order_id, stock_code, quantity, duration_minutes,
                    current_price, market_data
                )
        else:
            # No market data, use TWAP
            return self._generate_twap_slices(
                order_id, stock_code, quantity, duration_minutes, current_price
            )

    def _simulate_execution(self, order_id: str, stock_code: str,
                          total_quantity: int, slices: List[OrderSlice],
                          benchmark_price: float, side: str,
                          algorithm: ExecutionAlgorithm) -> ExecutionResult:
        """
        주문 실행 시뮬레이션

        In production, this would interface with actual trading API
        """
        executed_quantity = 0
        total_cost = 0.0
        executed_slices = 0

        for slice_obj in slices:
            # Simulate price impact and market movements
            price_impact = self._calculate_price_impact(
                slice_obj.quantity, total_quantity, side
            )

            # Random market movement
            market_movement = np.random.normal(0, benchmark_price * 0.001)

            # Execution price
            execution_price = benchmark_price + price_impact + market_movement

            # Execute slice
            slice_cost = execution_price * slice_obj.quantity
            total_cost += slice_cost
            executed_quantity += slice_obj.quantity
            executed_slices += 1

        # Calculate metrics
        avg_price = total_cost / executed_quantity if executed_quantity > 0 else benchmark_price
        slippage = avg_price - benchmark_price
        slippage_bps = (slippage / benchmark_price) * 10000 if benchmark_price > 0 else 0

        result = ExecutionResult(
            order_id=order_id,
            stock_code=stock_code,
            total_quantity=total_quantity,
            executed_quantity=executed_quantity,
            slices_executed=executed_slices,
            slices_total=len(slices),
            average_price=avg_price,
            total_cost=total_cost,
            slippage=slippage,
            slippage_bps=slippage_bps,
            execution_time_seconds=0.0,  # Will be set by caller
            algorithm_used=algorithm,
            success=True,
            error_message=None,
            metadata={
                'num_slices': len(slices),
                'side': side
            }
        )

        return result

    def _calculate_price_impact(self, slice_quantity: int,
                               total_quantity: int, side: str) -> float:
        """
        가격 충격 계산

        Simplified model: impact proportional to sqrt(quantity)
        """
        # Square root model
        impact_factor = np.sqrt(slice_quantity / 10000)  # Normalize

        # Market impact coefficient (adjust based on liquidity)
        market_impact_coeff = 0.001  # 0.1%

        # Direction
        direction = 1 if side == 'buy' else -1

        impact = direction * impact_factor * market_impact_coeff * 70000  # Assume price around 70k

        return impact


# Global singleton
_smart_executor: Optional[SmartOrderExecutor] = None


def get_smart_executor() -> SmartOrderExecutor:
    """스마트 실행기 싱글톤"""
    global _smart_executor
    if _smart_executor is None:
        _smart_executor = SmartOrderExecutor()
    return _smart_executor
