"""
Advanced Trading Systems
Multi-Agent, Risk Management, Market Regime Detection, and more


Author: AutoTrade Pro
Version: 4.2

"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Callable
import numpy as np
from datetime import datetime
from collections import deque
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor



@dataclass
class AgentDecision:
    """Agent trading decision"""
    agent_id: str
    action: str
    confidence: float
    reasoning: str
    timestamp: str


@dataclass
class ConsensusDecision:
    """Consensus from multiple agents"""
    final_action: str
    consensus_level: float
    agent_votes: Dict[str, str]
    weighted_confidence: float
    dissenting_agents: List[str]


class TradingAgent:
    """Base trading agent"""

    def __init__(self, agent_id: str, strategy: str, risk_tolerance: float):
        """
        self.agent_id = agent_id
        self.strategy = strategy
        self.risk_tolerance = risk_tolerance
        self.performance_history = []

    def make_decision(self, market_data: Dict[str, Any]) -> AgentDecision:
        """Make trading decision"""
        if self.strategy == 'momentum':
            action, confidence = self._momentum_strategy(market_data)
        elif self.strategy == 'mean_reversion':
            action, confidence = self._mean_reversion_strategy(market_data)
        elif self.strategy == 'value':
            action, confidence = self._value_strategy(market_data)
        else:
            action, confidence = 'hold', 0.5

        return AgentDecision(
            agent_id=self.agent_id,
            action=action,
            confidence=confidence,
            reasoning=f"{self.strategy} strategy signal",
            timestamp=datetime.now().isoformat()
        )

    def _momentum_strategy(self, data: Dict) -> Tuple[str, float]:
        """Momentum strategy"""
        price_change = data.get('price_change_pct', 0)
        if price_change > 2:
            return 'buy', 0.8
        elif price_change < -2:
            return 'sell', 0.8
        return 'hold', 0.5

    def _mean_reversion_strategy(self, data: Dict) -> Tuple[str, float]:
        """Mean reversion strategy"""
        z_score = data.get('z_score', 0)
        if z_score < -2:
            return 'buy', 0.7
        elif z_score > 2:
            return 'sell', 0.7
        return 'hold', 0.5

    def _value_strategy(self, data: Dict) -> Tuple[str, float]:
        """Value strategy"""
        pe_ratio = data.get('pe_ratio', 15)
        if pe_ratio < 10:
            return 'buy', 0.6
        elif pe_ratio > 25:
            return 'sell', 0.6
        return 'hold', 0.5


class MultiAgentSystem:
    """
    Multi-agent trading system

    Features:
    - Multiple independent agents
    - Consensus mechanism
    - Agent performance tracking
    - Dynamic weight adjustment
    """

    def __init__(self):
        """
        self.agents: List[TradingAgent] = []
        self.agent_weights: Dict[str, float] = {}
        self.consensus_history = []

        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize agent pool"""
        strategies = ['momentum', 'mean_reversion', 'value', 'momentum', 'mean_reversion']
        risk_levels = [0.3, 0.5, 0.7, 0.4, 0.6]

        for i, (strategy, risk) in enumerate(zip(strategies, risk_levels)):
            """
            agent = TradingAgent(
                agent_id=f"agent_{i}",
                strategy=strategy,
                risk_tolerance=risk
            )
            self.agents.append(agent)
            self.agent_weights[agent.agent_id] = 1.0 / len(strategies)

    def get_consensus(self, market_data: Dict[str, Any]) -> ConsensusDecision:
        """
        Get consensus decision from all agents

        Args:
            market_data: Current market data

        Returns:
            Consensus decision
        """
        decisions = []
        for agent in self.agents:
            decision = agent.make_decision(market_data)
            decisions.append(decision)

        action_scores = {'buy': 0.0, 'sell': 0.0, 'hold': 0.0}
        agent_votes = {}

        for decision in decisions:
            weight = self.agent_weights[decision.agent_id]
            action_scores[decision.action] += decision.confidence * weight
            agent_votes[decision.agent_id] = decision.action

        final_action = max(action_scores.items(), key=lambda x: x[1])[0]
        final_score = action_scores[final_action]
        total_score = sum(action_scores.values())

        consensus_level = final_score / total_score if total_score > 0 else 0

        dissenting = [d.agent_id for d in decisions if d.action != final_action]

        consensus = ConsensusDecision(
            final_action=final_action,
            consensus_level=consensus_level,
            agent_votes=agent_votes,
            weighted_confidence=final_score,
            dissenting_agents=dissenting
        )

        self.consensus_history.append(consensus)
        return consensus

    def update_agent_weights(self, actual_outcome: str):
        """
        Update agent weights based on performance

        Args:
            actual_outcome: 'profit' or 'loss'
        """
        if not self.consensus_history:
            return

        last_consensus = self.consensus_history[-1]

        for agent in self.agents:
            agent_vote = last_consensus.agent_votes.get(agent.agent_id)

            if (actual_outcome == 'profit' and agent_vote == 'buy') or \
               (actual_outcome == 'loss' and agent_vote == 'sell'):
                """
                self.agent_weights[agent.agent_id] *= 1.1
            else:
                self.agent_weights[agent.agent_id] *= 0.9

        total_weight = sum(self.agent_weights.values())
        for agent_id in self.agent_weights:
            self.agent_weights[agent_id] /= total_weight



@dataclass
class RiskMetrics:
    """Risk assessment metrics"""
    var_95: float
    cvar_95: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    beta: float
    volatility: float
    risk_score: float


class AdvancedRiskManager:
    """
    Advanced risk management system

    Features:
    - VaR and CVaR calculation
    - Stress testing
    - Position sizing
    - Correlation analysis
    """

    def __init__(self, initial_capital: float = 10000000):
        """
        self.initial_capital = initial_capital
        self.max_position_size = 0.2
        self.max_portfolio_risk = 0.15
        self.max_correlation = 0.7

    def calculate_var(
        self,
        returns: np.ndarray,
        confidence: float = 0.95,
        method: str = 'historical'
    ) -> float:
        """
        Calculate Value at Risk

        Args:
            returns: Historical returns
            confidence: Confidence level (0.95 = 95%)
            method: 'historical' or 'parametric'

        Returns:
            VaR value
        """
        if method == 'historical':
            return float(np.percentile(returns, (1 - confidence) * 100))
        elif method == 'parametric':
            from scipy.stats import norm
            mean = np.mean(returns)
            std = np.std(returns)
            return float(mean - norm.ppf(confidence) * std)
        return 0.0

    def calculate_cvar(
        self,
        returns: np.ndarray,
        confidence: float = 0.95
    ) -> float:
        """
        Calculate Conditional Value at Risk (Expected Shortfall)

        Args:
            returns: Historical returns
            confidence: Confidence level

        Returns:
            CVaR value
        """
        var = self.calculate_var(returns, confidence)
        tail_losses = returns[returns <= var]
        return float(np.mean(tail_losses)) if len(tail_losses) > 0 else var

    def stress_test(
        self,
        portfolio_weights: np.ndarray,
        returns: np.ndarray,
        scenarios: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Stress test portfolio under various scenarios

        Args:
            portfolio_weights: Current portfolio weights
            returns: Historical returns
            scenarios: List of stress scenarios

        Returns:
            Stress test results
        """
        results = {}

        for i, scenario in enumerate(scenarios):
            """
            scenario_name = scenario.get('name', f'Scenario_{i}')
            shock = scenario.get('shock', -0.2)

            shocked_returns = returns * (1 + shock)
            portfolio_return = np.dot(shocked_returns, portfolio_weights)

            results[scenario_name] = {
                'shock': shock,
                'portfolio_return': float(np.mean(portfolio_return)),
                'worst_case': float(np.min(portfolio_return)),
                'best_case': float(np.max(portfolio_return))
            }

        return results

    def calculate_position_size(
        self,
        stock_volatility: float,
        portfolio_volatility: float,
        correlation: float,
        current_capital: float
    ) -> float:
        """
        Calculate optimal position size using Kelly Criterion variant

        Args:
            stock_volatility: Stock volatility
            portfolio_volatility: Portfolio volatility
            correlation: Correlation with portfolio
            current_capital: Current capital

        Returns:
            Optimal position size in currency
        """
        max_position = current_capital * self.max_position_size

        vol_adjustment = max(0.5, 1.0 - stock_volatility / 0.3)

        corr_adjustment = max(0.5, 1.0 - abs(correlation) / self.max_correlation)

        optimal_size = max_position * vol_adjustment * corr_adjustment

        return float(optimal_size)

    def assess_portfolio_risk(
        self,
        positions: Dict[str, Dict[str, float]],
        returns_matrix: np.ndarray
    ) -> RiskMetrics:
        """
        Comprehensive portfolio risk assessment

        Args:
            positions: Current positions
            returns_matrix: Historical returns for all assets

        Returns:
            Complete risk metrics
        """
        weights = np.array([pos['weight'] for pos in positions.values()])
        portfolio_returns = np.dot(returns_matrix, weights)

        var_95 = self.calculate_var(portfolio_returns, 0.95)
        cvar_95 = self.calculate_cvar(portfolio_returns, 0.95)

        mean_return = np.mean(portfolio_returns)
        volatility = np.std(portfolio_returns) * np.sqrt(252)

        risk_free = 0.02
        sharpe = (mean_return * 252 - risk_free) / volatility if volatility > 0 else 0

        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_std = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else volatility
        sortino = (mean_return * 252 - risk_free) / downside_std if downside_std > 0 else 0

        cumulative = np.cumprod(1 + portfolio_returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = float(np.min(drawdown))

        risk_score = min(100, abs(var_95) * 100 + abs(cvar_95) * 50 + abs(max_drawdown) * 100)

        return RiskMetrics(
            var_95=float(var_95),
            cvar_95=float(cvar_95),
            max_drawdown=float(max_drawdown),
            sharpe_ratio=float(sharpe),
            sortino_ratio=float(sortino),
            beta=0.95,
            volatility=float(volatility),
            risk_score=float(risk_score)
        )



@dataclass
class MarketRegime:
    """Market regime classification"""
    regime_type: str
    confidence: float
    volatility_level: str
    trend_strength: float
    detected_at: str
    indicators: Dict[str, float]


class MarketRegimeDetector:
    """
    Market regime detection using multiple indicators

    Features:
    - Trend detection
    - Volatility clustering
    - Regime classification
    - State transitions
    """

    def __init__(self):
        """
        self.regime_history = []
        self.transition_matrix = np.array([
            [0.7, 0.2, 0.1],
            [0.3, 0.6, 0.1],
            [0.3, 0.3, 0.4],
        ])

    def detect_regime(self, price_data: np.ndarray) -> MarketRegime:
        """
        Detect current market regime

        Args:
            price_data: Historical price data

        Returns:
            Market regime classification
        """
        if len(price_data) < 50:
            return MarketRegime(
                regime_type='unknown',
                confidence=0.5,
                volatility_level='medium',
                trend_strength=0.0,
                detected_at=datetime.now().isoformat(),
                indicators={}
            )

        returns = np.diff(price_data) / price_data[:-1]

        x = np.arange(len(price_data))
        coeffs = np.polyfit(x, price_data, 1)
        trend_strength = coeffs[0] / np.mean(price_data) * 100

        volatility = np.std(returns) * np.sqrt(252) * 100

        ma_short = np.mean(price_data[-20:])
        ma_long = np.mean(price_data[-50:])
        ma_ratio = ma_short / ma_long

        if trend_strength > 0.1 and ma_ratio > 1.02:
            regime_type = 'bull'
            confidence = min(0.9, trend_strength * 5)
        elif trend_strength < -0.1 and ma_ratio < 0.98:
            regime_type = 'bear'
            confidence = min(0.9, abs(trend_strength) * 5)
        elif volatility > 30:
            regime_type = 'volatile'
            confidence = min(0.8, volatility / 50)
        else:
            regime_type = 'sideways'
            confidence = 0.6

        if volatility < 15:
            vol_level = 'low'
        elif volatility < 25:
            vol_level = 'medium'
        else:
            vol_level = 'high'

        regime = MarketRegime(
            regime_type=regime_type,
            confidence=float(confidence),
            volatility_level=vol_level,
            trend_strength=float(trend_strength),
            detected_at=datetime.now().isoformat(),
            indicators={
                'volatility': float(volatility),
                'ma_ratio': float(ma_ratio),
                'trend_coeff': float(coeffs[0])
            }
        )

        self.regime_history.append(regime)
        return regime

    def predict_regime_transition(self, current_regime: str) -> Dict[str, float]:
        """
        Predict probability of regime transitions

        Args:
            current_regime: Current regime type

        Returns:
            Transition probabilities
        """
        regime_map = {'bull': 0, 'bear': 1, 'sideways': 2}
        idx = regime_map.get(current_regime, 2)

        probabilities = self.transition_matrix[idx]

        return {
            'bull': float(probabilities[0]),
            'bear': float(probabilities[1]),
            'sideways': float(probabilities[2])
        }



class PerformanceOptimizer:
    """
    System performance optimization

    Features:
    - Multi-processing
    - Caching
    - Parallel execution
    - Memory optimization
    """

    def __init__(self):
        """
        self.cache = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.process_pool = ProcessPoolExecutor(max_workers=mp.cpu_count())

    def parallel_backtest(
        self,
        strategies: List[Callable],
        data: Any,
        n_jobs: int = -1
    ) -> List[Any]:
        """
        Run multiple backtests in parallel

        Args:
            strategies: List of strategy functions
            data: Historical data
            n_jobs: Number of parallel jobs (-1 = all cores)

        Returns:
            List of backtest results
        """
        if n_jobs == -1:
            n_jobs = mp.cpu_count()

        futures = []
        for strategy in strategies:
            future = self.process_pool.submit(strategy, data)
            futures.append(future)

        results = [f.result() for f in futures]
        return results

    def cached_calculation(self, key: str, calc_func: Callable, *args, **kwargs) -> Any:
        """
        Cache expensive calculations

        Args:
            key: Cache key
            calc_func: Calculation function
            *args, **kwargs: Function arguments

        Returns:
            Cached or calculated result
        """
        if key in self.cache:
            return self.cache[key]

        result = calc_func(*args, **kwargs)
        self.cache[key] = result
        return result

    def batch_process(
        self,
        items: List[Any],
        process_func: Callable,
        batch_size: int = 100
    ) -> List[Any]:
        """
        Process items in batches for memory efficiency

        Args:
            items: Items to process
            process_func: Processing function
            batch_size: Batch size

        Returns:
            Processed results
        """
        results = []
        for i in range(0, len(items), batch_size):
            """
            batch = items[i:i + batch_size]
            batch_results = [process_func(item) for item in batch]
            results.extend(batch_results)

        return results


_multi_agent_system = None
_risk_manager = None
_regime_detector = None
_performance_optimizer = None

def get_multi_agent_system() -> MultiAgentSystem:
    """Get multi-agent system"""
    global _multi_agent_system
    if _multi_agent_system is None:
        _multi_agent_system = MultiAgentSystem()
    return _multi_agent_system

def get_risk_manager() -> AdvancedRiskManager:
    """Get risk manager"""
    global _risk_manager
    if _risk_manager is None:
        _risk_manager = AdvancedRiskManager()
    return _risk_manager

def get_regime_detector() -> MarketRegimeDetector:
    """Get regime detector"""
    global _regime_detector
    if _regime_detector is None:
        _regime_detector = MarketRegimeDetector()
    return _regime_detector

def get_performance_optimizer() -> PerformanceOptimizer:
    """Get performance optimizer"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer


if __name__ == '__main__':
    print("🚀 Advanced Systems Test")

    mas = get_multi_agent_system()
    market_data = {'price_change_pct': 2.5, 'z_score': -1.5, 'pe_ratio': 12}
    consensus = mas.get_consensus(market_data)
    print(f"\nMulti-Agent Consensus: {consensus.final_action}")
    print(f"Consensus Level: {consensus.consensus_level:.1%}")

    rm = get_risk_manager()
    returns = np.random.randn(252) * 0.01
    var = rm.calculate_var(returns)
    print(f"\nVaR (95%): {var:.2%}")

    rd = get_regime_detector()
    prices = np.cumsum(np.random.randn(100)) + 100
    regime = rd.detect_regime(prices)
    print(f"\nMarket Regime: {regime.regime_type} ({regime.confidence:.1%})")
    print(f"Volatility: {regime.volatility_level}")

    print("\n[OK] Advanced systems ready")
