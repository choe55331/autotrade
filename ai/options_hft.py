"""
Options Pricing and High-Frequency Trading
Advanced derivatives and ultra-fast trading systems

Author: AutoTrade Pro
Version: 4.2
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta
import time

try:
    from scipy.stats import norm
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


# ============================================================================
# 1. Options Pricing System
# ============================================================================

@dataclass
class OptionContract:
    """Option contract specification"""
    underlying: str
    strike_price: float
    expiry_date: str
    option_type: str  # 'call' or 'put'
    premium: float = 0.0


@dataclass
class OptionGreeks:
    """Option Greeks"""
    delta: float  # Price sensitivity
    gamma: float  # Delta sensitivity
    theta: float  # Time decay
    vega: float  # Volatility sensitivity
    rho: float  # Interest rate sensitivity


class BlackScholesModel:
    """
    Black-Scholes option pricing model

    Features:
    - Call and put pricing
    - Greeks calculation
    - Implied volatility
    """

    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate

    def price_option(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,  # in years
        volatility: float,
        option_type: str = 'call'
    ) -> float:
        """
        Calculate option price using Black-Scholes

        Args:
            spot_price: Current stock price
            strike_price: Strike price
            time_to_expiry: Time to expiry in years
            volatility: Annualized volatility
            option_type: 'call' or 'put'

        Returns:
            Option price
        """
        if not SCIPY_AVAILABLE:
            # Simple approximation
            intrinsic = max(0, spot_price - strike_price) if option_type == 'call' \
                else max(0, strike_price - spot_price)
            time_value = volatility * np.sqrt(time_to_expiry) * spot_price / 4
            return intrinsic + time_value

        d1 = (np.log(spot_price / strike_price) +
              (self.risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) / \
             (volatility * np.sqrt(time_to_expiry))

        d2 = d1 - volatility * np.sqrt(time_to_expiry)

        if option_type == 'call':
            price = (spot_price * norm.cdf(d1) -
                    strike_price * np.exp(-self.risk_free_rate * time_to_expiry) * norm.cdf(d2))
        else:  # put
            price = (strike_price * np.exp(-self.risk_free_rate * time_to_expiry) * norm.cdf(-d2) -
                    spot_price * norm.cdf(-d1))

        return float(price)

    def calculate_greeks(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        volatility: float,
        option_type: str = 'call'
    ) -> OptionGreeks:
        """
        Calculate option Greeks

        Returns:
            All Greeks
        """
        if not SCIPY_AVAILABLE:
            # Simplified Greeks
            return OptionGreeks(
                delta=0.5 if option_type == 'call' else -0.5,
                gamma=0.1,
                theta=-0.05,
                vega=0.2,
                rho=0.1
            )

        d1 = (np.log(spot_price / strike_price) +
              (self.risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) / \
             (volatility * np.sqrt(time_to_expiry))

        d2 = d1 - volatility * np.sqrt(time_to_expiry)

        # Delta
        if option_type == 'call':
            delta = norm.cdf(d1)
        else:
            delta = norm.cdf(d1) - 1

        # Gamma (same for call and put)
        gamma = norm.pdf(d1) / (spot_price * volatility * np.sqrt(time_to_expiry))

        # Theta
        if option_type == 'call':
            theta = ((-spot_price * norm.pdf(d1) * volatility / (2 * np.sqrt(time_to_expiry))) -
                    self.risk_free_rate * strike_price * np.exp(-self.risk_free_rate * time_to_expiry) * norm.cdf(d2)) / 365
        else:
            theta = ((-spot_price * norm.pdf(d1) * volatility / (2 * np.sqrt(time_to_expiry))) +
                    self.risk_free_rate * strike_price * np.exp(-self.risk_free_rate * time_to_expiry) * norm.cdf(-d2)) / 365

        # Vega (same for call and put)
        vega = spot_price * norm.pdf(d1) * np.sqrt(time_to_expiry) / 100

        # Rho
        if option_type == 'call':
            rho = strike_price * time_to_expiry * np.exp(-self.risk_free_rate * time_to_expiry) * norm.cdf(d2) / 100
        else:
            rho = -strike_price * time_to_expiry * np.exp(-self.risk_free_rate * time_to_expiry) * norm.cdf(-d2) / 100

        return OptionGreeks(
            delta=float(delta),
            gamma=float(gamma),
            theta=float(theta),
            vega=float(vega),
            rho=float(rho)
        )

    def implied_volatility(
        self,
        option_price: float,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        option_type: str = 'call'
    ) -> float:
        """
        Calculate implied volatility using Newton-Raphson

        Args:
            option_price: Observed option price
            spot_price: Current stock price
            strike_price: Strike price
            time_to_expiry: Time to expiry
            option_type: 'call' or 'put'

        Returns:
            Implied volatility
        """
        # Initial guess
        volatility = 0.3

        for _ in range(100):  # Max iterations
            price = self.price_option(spot_price, strike_price, time_to_expiry, volatility, option_type)
            diff = option_price - price

            if abs(diff) < 0.001:
                return volatility

            # Vega for Newton-Raphson
            greeks = self.calculate_greeks(spot_price, strike_price, time_to_expiry, volatility, option_type)
            vega = greeks.vega * 100  # Convert back from % terms

            if vega == 0:
                break

            volatility += diff / vega

            # Keep volatility positive and reasonable
            volatility = max(0.001, min(3.0, volatility))

        return float(volatility)


class OptionsStrategyAnalyzer:
    """
    Options strategy analysis

    Features:
    - Covered call
    - Protective put
    - Straddle/Strangle
    - Butterfly spread
    """

    def __init__(self):
        self.bs_model = BlackScholesModel()

    def covered_call(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        volatility: float,
        shares: int = 100
    ) -> Dict[str, Any]:
        """
        Analyze covered call strategy

        Returns:
            Strategy analysis
        """
        # Own stock + sell call
        call_premium = self.bs_model.price_option(
            spot_price, strike_price, time_to_expiry, volatility, 'call'
        )

        max_profit = (strike_price - spot_price + call_premium) * shares
        max_loss = (spot_price - call_premium) * shares

        return {
            'strategy': 'covered_call',
            'call_premium': call_premium,
            'max_profit': max_profit,
            'max_loss': -max_loss,
            'breakeven': spot_price - call_premium,
            'income_generated': call_premium * shares
        }

    def protective_put(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        volatility: float,
        shares: int = 100
    ) -> Dict[str, Any]:
        """
        Analyze protective put strategy

        Returns:
            Strategy analysis
        """
        # Own stock + buy put
        put_premium = self.bs_model.price_option(
            spot_price, strike_price, time_to_expiry, volatility, 'put'
        )

        max_loss = (spot_price - strike_price + put_premium) * shares
        max_profit = float('inf')  # Unlimited upside

        return {
            'strategy': 'protective_put',
            'put_premium': put_premium,
            'max_loss': -max_loss,
            'max_profit': 'unlimited',
            'insurance_cost': put_premium * shares,
            'protected_below': strike_price
        }

    def straddle(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        volatility: float
    ) -> Dict[str, Any]:
        """
        Analyze straddle strategy (buy call + put at same strike)

        Returns:
            Strategy analysis
        """
        call_premium = self.bs_model.price_option(
            spot_price, strike_price, time_to_expiry, volatility, 'call'
        )
        put_premium = self.bs_model.price_option(
            spot_price, strike_price, time_to_expiry, volatility, 'put'
        )

        total_premium = call_premium + put_premium

        return {
            'strategy': 'straddle',
            'call_premium': call_premium,
            'put_premium': put_premium,
            'total_cost': total_premium,
            'breakeven_up': strike_price + total_premium,
            'breakeven_down': strike_price - total_premium,
            'max_loss': -total_premium,
            'requires_move': total_premium
        }


# ============================================================================
# 2. High-Frequency Trading System
# ============================================================================

@dataclass
class HFTOrder:
    """High-frequency trading order"""
    order_id: int
    stock_code: str
    action: str  # 'buy' or 'sell'
    quantity: int
    price: float
    timestamp: float  # microseconds
    latency_us: float = 0.0  # Execution latency


@dataclass
class HFTSignal:
    """HFT trading signal"""
    signal_type: str  # 'arbitrage', 'momentum', 'mean_reversion'
    action: str
    urgency: str  # 'immediate', 'high', 'medium'
    expected_profit: float
    confidence: float
    timestamp: float


class HighFrequencyTrader:
    """
    High-frequency trading system

    Features:
    - Microsecond timing
    - Latency monitoring
    - Market making
    - Arbitrage detection
    """

    def __init__(self):
        self.order_queue = []
        self.execution_times = []
        self.avg_latency_us = 0.0

    def detect_arbitrage(
        self,
        bid_prices: List[float],
        ask_prices: List[float],
        exchanges: List[str]
    ) -> Optional[HFTSignal]:
        """
        Detect arbitrage opportunities across exchanges

        Args:
            bid_prices: Bid prices from different exchanges
            ask_prices: Ask prices from different exchanges
            exchanges: Exchange names

        Returns:
            Arbitrage signal if found
        """
        max_bid_idx = np.argmax(bid_prices)
        min_ask_idx = np.argmin(ask_prices)

        max_bid = bid_prices[max_bid_idx]
        min_ask = ask_prices[min_ask_idx]

        # Arbitrage exists if we can buy low and sell high
        if max_bid > min_ask:
            profit = max_bid - min_ask
            profit_pct = profit / min_ask * 100

            if profit_pct > 0.05:  # 0.05% threshold
                return HFTSignal(
                    signal_type='arbitrage',
                    action='arbitrage',
                    urgency='immediate',
                    expected_profit=profit_pct,
                    confidence=0.95,
                    timestamp=time.time()
                )

        return None

    def market_making_strategy(
        self,
        mid_price: float,
        spread: float,
        inventory: int,
        target_inventory: int = 0
    ) -> Tuple[float, float]:
        """
        Market making strategy with inventory management

        Args:
            mid_price: Mid price
            spread: Bid-ask spread
            inventory: Current inventory
            target_inventory: Target inventory

        Returns:
            (bid_price, ask_price)
        """
        half_spread = spread / 2

        # Adjust quotes based on inventory
        inventory_skew = (inventory - target_inventory) * 0.001

        bid_price = mid_price - half_spread - inventory_skew
        ask_price = mid_price + half_spread - inventory_skew

        return bid_price, ask_price

    def momentum_signal(
        self,
        price_changes: np.ndarray,
        window: int = 100
    ) -> Optional[HFTSignal]:
        """
        Ultra-short-term momentum signal

        Args:
            price_changes: Recent price changes (microsecond data)
            window: Lookback window

        Returns:
            Momentum signal if strong enough
        """
        if len(price_changes) < window:
            return None

        recent = price_changes[-window:]
        momentum = np.sum(recent) / window

        # Need strong momentum for HFT
        if momentum > 0.0001:  # 0.01% positive momentum
            return HFTSignal(
                signal_type='momentum',
                action='buy',
                urgency='high',
                expected_profit=momentum * 100,
                confidence=0.7,
                timestamp=time.time()
            )
        elif momentum < -0.0001:
            return HFTSignal(
                signal_type='momentum',
                action='sell',
                urgency='high',
                expected_profit=abs(momentum) * 100,
                confidence=0.7,
                timestamp=time.time()
            )

        return None

    def execute_order(
        self,
        order: HFTOrder,
        simulate: bool = True
    ) -> Dict[str, Any]:
        """
        Execute HFT order

        Args:
            order: Order to execute
            simulate: If True, simulate execution

        Returns:
            Execution result
        """
        start_time = time.time()

        if simulate:
            # Simulate latency (10-100 microseconds)
            latency_us = np.random.uniform(10, 100)
            time.sleep(latency_us / 1_000_000)  # Convert to seconds

            fill_price = order.price * (1 + np.random.uniform(-0.0001, 0.0001))
            status = 'filled'
        else:
            # Real execution would go here
            fill_price = order.price
            status = 'pending'
            latency_us = 0

        end_time = time.time()
        execution_time_us = (end_time - start_time) * 1_000_000

        self.execution_times.append(execution_time_us)
        self.avg_latency_us = np.mean(self.execution_times[-1000:])  # Last 1000

        return {
            'order_id': order.order_id,
            'status': status,
            'fill_price': fill_price,
            'latency_us': execution_time_us,
            'slippage': abs(fill_price - order.price) / order.price * 100
        }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get HFT performance metrics"""
        if not self.execution_times:
            return {
                'avg_latency_us': 0,
                'min_latency_us': 0,
                'max_latency_us': 0,
                'total_orders': 0
            }

        return {
            'avg_latency_us': float(self.avg_latency_us),
            'min_latency_us': float(np.min(self.execution_times)),
            'max_latency_us': float(np.max(self.execution_times)),
            'p50_latency_us': float(np.percentile(self.execution_times, 50)),
            'p95_latency_us': float(np.percentile(self.execution_times, 95)),
            'p99_latency_us': float(np.percentile(self.execution_times, 99)),
            'total_orders': len(self.execution_times)
        }


# Singleton instances
_bs_model = None
_options_analyzer = None
_hft_trader = None

def get_bs_model() -> BlackScholesModel:
    """Get Black-Scholes model"""
    global _bs_model
    if _bs_model is None:
        _bs_model = BlackScholesModel()
    return _bs_model

def get_options_analyzer() -> OptionsStrategyAnalyzer:
    """Get options strategy analyzer"""
    global _options_analyzer
    if _options_analyzer is None:
        _options_analyzer = OptionsStrategyAnalyzer()
    return _options_analyzer

def get_hft_trader() -> HighFrequencyTrader:
    """Get HFT trader"""
    global _hft_trader
    if _hft_trader is None:
        _hft_trader = HighFrequencyTrader()
    return _hft_trader


if __name__ == '__main__':
    print("⚡ Options & HFT Systems Test")

    # Test Black-Scholes
    bs = get_bs_model()
    call_price = bs.price_option(
        spot_price=100,
        strike_price=105,
        time_to_expiry=0.25,  # 3 months
        volatility=0.25,
        option_type='call'
    )
    print(f"\nCall Option Price: ${call_price:.2f}")

    greeks = bs.calculate_greeks(100, 105, 0.25, 0.25, 'call')
    print(f"Delta: {greeks.delta:.3f}")
    print(f"Gamma: {greeks.gamma:.3f}")
    print(f"Theta: {greeks.theta:.3f}")

    # Test options strategy
    analyzer = get_options_analyzer()
    straddle = analyzer.straddle(100, 100, 0.25, 0.25)
    print(f"\nStraddle Cost: ${straddle['total_cost']:.2f}")
    print(f"Breakeven Range: ${straddle['breakeven_down']:.2f} - ${straddle['breakeven_up']:.2f}")

    # Test HFT
    hft = get_hft_trader()
    order = HFTOrder(
        order_id=1,
        stock_code='005930',
        action='buy',
        quantity=100,
        price=73500,
        timestamp=time.time()
    )
    result = hft.execute_order(order)
    print(f"\nHFT Execution Latency: {result['latency_us']:.0f} μs")

    print("\n✅ Options & HFT systems ready")
