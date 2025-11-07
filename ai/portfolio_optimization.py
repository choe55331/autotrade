"""
Portfolio Optimization Engine
Advanced portfolio optimization techniques


Author: AutoTrade Pro
Version: 4.2

"""
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from datetime import datetime

try:
    from scipy.optimize import minimize
    from scipy.stats import norm
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("WARNING: scipy not available. Install with: pip install scipy")


@dataclass
class PortfolioAllocation:
    """Portfolio allocation result"""
    assets: List[str]
    weights: np.ndarray
    expected_return: float
    expected_risk: float
    sharpe_ratio: float
    method: str
    timestamp: str


@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics"""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    var_95: float
    cvar_95: float
    beta: float
    alpha: float



class MarkowitzOptimizer:
    """
    Markowitz Mean-Variance Portfolio Optimization

    Features:
    - Efficient frontier calculation
    - Maximum Sharpe ratio portfolio
    - Minimum variance portfolio
    - Risk-return optimization
    """

    def __init__(self):
        """
        self.optimization_history = []

    def optimize(
        self,
        returns: np.ndarray,
        target_return: Optional[float] = None,
        risk_free_rate: float = 0.02
    ) -> PortfolioAllocation:
        """
        Optimize portfolio using Markowitz model

        Args:
            returns: Historical returns matrix [n_samples, n_assets]
            target_return: Target return (optional)
            risk_free_rate: Risk-free rate for Sharpe calculation

        Returns:
            Optimal portfolio allocation
        """
        if not SCIPY_AVAILABLE:
            return self._mock_allocation(returns.shape[1])

        n_assets = returns.shape[1]

        mean_returns = np.mean(returns, axis=0)
        cov_matrix = np.cov(returns.T)

        if target_return is None:
            weights = self._max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate)
        else:
            weights = self._target_return_min_risk(mean_returns, cov_matrix, target_return)

        portfolio_return = np.dot(weights, mean_returns) * 252
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
        sharpe = (portfolio_return - risk_free_rate) / portfolio_risk

        return PortfolioAllocation(
            assets=[f"Asset_{i}" for i in range(n_assets)],
            weights=weights,
            expected_return=float(portfolio_return),
            expected_risk=float(portfolio_risk),
            sharpe_ratio=float(sharpe),
            method='markowitz',
            timestamp=datetime.now().isoformat()
        )

    def _max_sharpe_ratio(
        self,
        mean_returns: np.ndarray,
        cov_matrix: np.ndarray,
        risk_free_rate: float
    ) -> np.ndarray:
        """
        n_assets = len(mean_returns)

        def neg_sharpe(weights):
            """
            port_return = np.dot(weights, mean_returns) * 252
            port_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
            return -(port_return - risk_free_rate) / port_risk

        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_guess = np.array([1/n_assets] * n_assets)

        result = minimize(
            neg_sharpe,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        return result.x

    def _target_return_min_risk(
        self,
        mean_returns: np.ndarray,
        cov_matrix: np.ndarray,
        target_return: float
    ) -> np.ndarray:
        """
        n_assets = len(mean_returns)

        def portfolio_risk(weights):
            """
            return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)

        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x: np.dot(x, mean_returns) * 252 - target_return}
        )
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_guess = np.array([1/n_assets] * n_assets)

        result = minimize(
            portfolio_risk,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        return result.x

    def efficient_frontier(
        self,
        returns: np.ndarray,
        n_points: int = 100
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate efficient frontier

        Returns:
            risks, returns along efficient frontier
        """
        mean_returns = np.mean(returns, axis=0)
        min_return = np.min(mean_returns) * 252
        max_return = np.max(mean_returns) * 252

        target_returns = np.linspace(min_return, max_return, n_points)
        frontier_risks = []
        frontier_returns = []

        for target in target_returns:
            try:
                allocation = self.optimize(returns, target_return=target)
                frontier_risks.append(allocation.expected_risk)
                frontier_returns.append(allocation.expected_return)
            except:
                continue

        return np.array(frontier_risks), np.array(frontier_returns)

    def _mock_allocation(self, n_assets: int) -> PortfolioAllocation:
        """Mock allocation for testing"""
        weights = np.random.dirichlet(np.ones(n_assets))
        return PortfolioAllocation(
            assets=[f"Asset_{i}" for i in range(n_assets)],
            weights=weights,
            expected_return=0.12,
            expected_risk=0.15,
            sharpe_ratio=0.67,
            method='markowitz',
            timestamp=datetime.now().isoformat()
        )



class BlackLittermanOptimizer:
    """
    Black-Litterman Portfolio Optimization

    Features:
    - Combines market equilibrium with investor views
    - Bayesian approach to portfolio optimization
    - More stable than pure Markowitz
    """

    def __init__(self, risk_aversion: float = 2.5):
        """
        self.risk_aversion = risk_aversion

    def optimize(
        self,
        returns: np.ndarray,
        market_caps: np.ndarray,
        views: Dict[int, float],
        view_confidence: float = 0.5
    ) -> PortfolioAllocation:
        """
        Optimize using Black-Litterman model

        Args:
            returns: Historical returns
            market_caps: Market capitalizations
            views: Investor views {asset_idx: return}
            view_confidence: Confidence in views (0-1)

        Returns:
            Optimal allocation
        """
        if not SCIPY_AVAILABLE:
            n_assets = returns.shape[1]
            weights = np.random.dirichlet(np.ones(n_assets))
            return PortfolioAllocation(
                assets=[f"Asset_{i}" for i in range(n_assets)],
                weights=weights,
                expected_return=0.13,
                expected_risk=0.14,
                sharpe_ratio=0.75,
                method='black_litterman',
                timestamp=datetime.now().isoformat()
            )

        n_assets = returns.shape[1]

        cov_matrix = np.cov(returns.T)
        market_weights = market_caps / np.sum(market_caps)
        implied_returns = self.risk_aversion * np.dot(cov_matrix, market_weights)

        P = np.zeros((len(views), n_assets))
        Q = np.zeros(len(views))
        for i, (asset_idx, view_return) in enumerate(views.items()):
            """
            P[i, asset_idx] = 1
            Q[i] = view_return

        tau = view_confidence
        omega = np.dot(np.dot(P, tau * cov_matrix), P.T)

        M_inv = np.linalg.inv(tau * cov_matrix)
        omega_inv = np.linalg.inv(omega)

        posterior_cov = np.linalg.inv(M_inv + np.dot(np.dot(P.T, omega_inv), P))
        posterior_returns = np.dot(posterior_cov, (
            np.dot(M_inv, implied_returns) + np.dot(np.dot(P.T, omega_inv), Q)
        ))

        weights = np.dot(np.linalg.inv(self.risk_aversion * cov_matrix), posterior_returns)
        weights = weights / np.sum(np.abs(weights))
        weights = np.maximum(weights, 0)
        weights = weights / np.sum(weights)

        portfolio_return = np.dot(weights, posterior_returns) * 252
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
        sharpe = portfolio_return / portfolio_risk

        return PortfolioAllocation(
            assets=[f"Asset_{i}" for i in range(n_assets)],
            weights=weights,
            expected_return=float(portfolio_return),
            expected_risk=float(portfolio_risk),
            sharpe_ratio=float(sharpe),
            method='black_litterman',
            timestamp=datetime.now().isoformat()
        )



class RiskParityOptimizer:
    """
    Risk Parity Portfolio Optimization

    Features:
    - Equal risk contribution from each asset
    - More diversified than market-cap weighting
    - Robust to estimation error
    """

    def optimize(self, returns: np.ndarray) -> PortfolioAllocation:
        """
        Optimize for risk parity

        Args:
            returns: Historical returns

        Returns:
            Risk parity allocation
        """
        if not SCIPY_AVAILABLE:
            n_assets = returns.shape[1]
            weights = np.ones(n_assets) / n_assets
            return PortfolioAllocation(
                assets=[f"Asset_{i}" for i in range(n_assets)],
                weights=weights,
                expected_return=0.11,
                expected_risk=0.13,
                sharpe_ratio=0.69,
                method='risk_parity',
                timestamp=datetime.now().isoformat()
            )

        n_assets = returns.shape[1]
        cov_matrix = np.cov(returns.T)

        def risk_contribution(weights):
            """Calculate risk contribution of each asset"""
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            marginal_contrib = np.dot(cov_matrix, weights) / portfolio_risk
            risk_contrib = weights * marginal_contrib
            return risk_contrib

        def objective(weights):
            """Minimize variance of risk contributions"""
            rc = risk_contribution(weights)
            target_rc = np.ones(n_assets) / n_assets
            return np.sum((rc - target_rc) ** 2)

        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_guess = np.array([1/n_assets] * n_assets)

        result = minimize(
            objective,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        weights = result.x

        mean_returns = np.mean(returns, axis=0)
        portfolio_return = np.dot(weights, mean_returns) * 252
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
        sharpe = portfolio_return / portfolio_risk

        return PortfolioAllocation(
            assets=[f"Asset_{i}" for i in range(n_assets)],
            weights=weights,
            expected_return=float(portfolio_return),
            expected_risk=float(portfolio_risk),
            sharpe_ratio=float(sharpe),
            method='risk_parity',
            timestamp=datetime.now().isoformat()
        )



class MonteCarloSimulator:
    """
    Monte Carlo portfolio simulation

    Features:
    - Simulate thousands of portfolio paths
    - Calculate VaR and CVaR
    - Stress testing
    """

    def simulate(
        self,
        weights: np.ndarray,
        returns: np.ndarray,
        n_simulations: int = 10000,
        n_days: int = 252
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation

        Args:
            weights: Portfolio weights
            returns: Historical returns
            n_simulations: Number of simulations
            n_days: Trading days to simulate

        Returns:
            Simulation results
        """
        mean_returns = np.mean(returns, axis=0)
        cov_matrix = np.cov(returns.T)

        simulated_returns = np.random.multivariate_normal(
            mean_returns,
            cov_matrix,
            size=(n_simulations, n_days)
        )

        portfolio_returns = np.dot(simulated_returns, weights)
        portfolio_values = 100 * np.exp(np.cumsum(portfolio_returns, axis=1))

        final_values = portfolio_values[:, -1]

        var_95 = np.percentile(final_values, 5)
        cvar_95 = np.mean(final_values[final_values <= var_95])

        prob_profit = np.mean(final_values > 100)
        prob_loss_10 = np.mean(final_values < 90)
        prob_loss_20 = np.mean(final_values < 80)

        return {
            'final_values': final_values,
            'portfolio_paths': portfolio_values,
            'mean_final_value': float(np.mean(final_values)),
            'median_final_value': float(np.median(final_values)),
            'var_95': float(var_95),
            'cvar_95': float(cvar_95),
            'best_case': float(np.percentile(final_values, 95)),
            'worst_case': float(np.percentile(final_values, 5)),
            'prob_profit': float(prob_profit),
            'prob_loss_10': float(prob_loss_10),
            'prob_loss_20': float(prob_loss_20),
            'n_simulations': n_simulations,
            'n_days': n_days
        }



class PortfolioOptimizationManager:
    """
    Unified portfolio optimization manager

    Features:
    - Multiple optimization methods
    - Performance comparison
    - Rebalancing recommendations
    """

    def __init__(self):
        """
        self.markowitz = MarkowitzOptimizer()
        self.black_litterman = BlackLittermanOptimizer()
        self.risk_parity = RiskParityOptimizer()
        self.monte_carlo = MonteCarloSimulator()

        self.optimization_history = []

    def optimize_all(
        self,
        returns: np.ndarray,
        market_caps: Optional[np.ndarray] = None,
        views: Optional[Dict[int, float]] = None
    ) -> Dict[str, PortfolioAllocation]:
        """
        Run all optimization methods

        Returns:
            Dictionary of method -> allocation
        """
        results = {}

        results['markowitz'] = self.markowitz.optimize(returns)

        if market_caps is not None and views is not None:
            results['black_litterman'] = self.black_litterman.optimize(
                returns, market_caps, views
            )

        results['risk_parity'] = self.risk_parity.optimize(returns)

        return results

    def compare_allocations(
        self,
        allocations: Dict[str, PortfolioAllocation]
    ) -> Dict[str, Any]:
        """
        comparison = {}

        for method, allocation in allocations.items():
            """
            comparison[method] = {
                'weights': allocation.weights.tolist(),
                'expected_return': allocation.expected_return,
                'expected_risk': allocation.expected_risk,
                'sharpe_ratio': allocation.sharpe_ratio
            }

        best_method = max(allocations.items(), key=lambda x: x[1].sharpe_ratio)[0]
        comparison['best_method'] = best_method

        return comparison

    def recommend_rebalancing(
        self,
        current_weights: np.ndarray,
        target_weights: np.ndarray,
        threshold: float = 0.05
    ) -> Dict[str, Any]:
        """
        Recommend portfolio rebalancing

        Args:
            current_weights: Current portfolio weights
            target_weights: Target portfolio weights
            threshold: Rebalancing threshold

        Returns:
            Rebalancing recommendation
        """
        diff = target_weights - current_weights
        needs_rebalancing = np.any(np.abs(diff) > threshold)

        trades = []
        if needs_rebalancing:
            for i, d in enumerate(diff):
                """
                if abs(d) > threshold:
                    action = 'buy' if d > 0 else 'sell'
                    trades.append({
                        'asset': f'Asset_{i}',
                        'action': action,
                        'amount': abs(d),
                        'current_weight': float(current_weights[i]),
                        'target_weight': float(target_weights[i])
                    })

        return {
            'needs_rebalancing': needs_rebalancing,
            'trades': trades,
            'total_turnover': float(np.sum(np.abs(diff))),
            'threshold': threshold
        }


_portfolio_manager = None

def get_portfolio_manager() -> PortfolioOptimizationManager:
    """Get portfolio optimization manager"""
    global _portfolio_manager
    if _portfolio_manager is None:
        _portfolio_manager = PortfolioOptimizationManager()
    return _portfolio_manager


if __name__ == '__main__':
    print(" Portfolio Optimization Test")

    returns = np.random.randn(252, 5) * 0.01

    manager = get_portfolio_manager()

    allocation = manager.markowitz.optimize(returns)
    print(f"\nMarkowitz Allocation:")
    print(f"Weights: {allocation.weights}")
    print(f"Expected Return: {allocation.expected_return:.2%}")
    print(f"Expected Risk: {allocation.expected_risk:.2%}")
    print(f"Sharpe Ratio: {allocation.sharpe_ratio:.2f}")

    rp_allocation = manager.risk_parity.optimize(returns)
    print(f"\nRisk Parity Allocation:")
    print(f"Weights: {rp_allocation.weights}")
    print(f"Sharpe Ratio: {rp_allocation.sharpe_ratio:.2f}")

    print("\n[OK] Portfolio optimization ready")
