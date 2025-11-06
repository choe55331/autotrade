"""
Advanced Portfolio Optimizer v7.0
Comprehensive portfolio optimization combining quantitative and AI methods

Features:
- Modern Portfolio Theory (MPT) & Efficient Frontier
- Maximum Sharpe Ratio, Minimum Volatility, Risk Parity
- Kelly Criterion position sizing
- AI-based sector diversification analysis
- Risk concentration detection
- Intelligent rebalancing recommendations
- Dashboard integration
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import numpy as np
import logging

logger = logging.getLogger(__name__)


class OptimizationObjective(Enum):
    """Optimization objectives"""
    MAX_SHARPE = "max_sharpe"
    MIN_VOLATILITY = "min_volatility"
    MAX_RETURN = "max_return"
    RISK_PARITY = "risk_parity"
    BALANCED = "balanced"


@dataclass
class PortfolioPosition:
    """Single position in portfolio"""
    code: str
    name: str
    quantity: int
    avg_price: float
    current_price: float
    value: float
    weight: float
    sector: str
    profit_loss: float
    profit_loss_percent: float


@dataclass
class SectorAllocation:
    """Sector allocation information"""
    sector: str
    value: float
    weight: float
    position_count: int
    avg_return: float


@dataclass
class PortfolioMetrics:
    """Portfolio-wide metrics"""
    total_value: float
    position_count: int
    sector_count: int
    diversification_score: float
    concentration_risk: str
    largest_position_weight: float
    top3_concentration: float
    avg_correlation: float
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float


@dataclass
class OptimizationSuggestion:
    """Optimization suggestion"""
    type: str
    priority: str
    title: str
    description: str
    action: str
    impact: str


@dataclass
class OptimizationResult:
    """Complete optimization result"""
    timestamp: str
    objective: str
    metrics: PortfolioMetrics
    positions: List[PortfolioPosition]
    sector_allocation: List[SectorAllocation]
    optimal_weights: Dict[str, float]
    suggestions: List[OptimizationSuggestion]
    risk_level: str
    rebalancing_needed: bool

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON"""
        return {
            'timestamp': self.timestamp,
            'objective': self.objective,
            'metrics': asdict(self.metrics),
            'positions': [asdict(p) for p in self.positions],
            'sector_allocation': [asdict(s) for s in self.sector_allocation],
            'optimal_weights': self.optimal_weights,
            'suggestions': [asdict(s) for s in self.suggestions],
            'risk_level': self.risk_level,
            'rebalancing_needed': self.rebalancing_needed
        }


@dataclass
class EfficientFrontierPoint:
    """Point on efficient frontier"""
    expected_return: float
    volatility: float
    sharpe_ratio: float
    weights: Dict[str, float]


class AdvancedPortfolioOptimizer:
    """
    Advanced portfolio optimization system

    Combines:
    - Quantitative optimization (MPT, Sharpe, Efficient Frontier)
    - AI-based analysis (sector diversification, risk concentration)
    - Intelligent rebalancing recommendations
    """

    SECTOR_MAP = {
        '005930': '반도체', '000660': '반도체',
        '035420': '인터넷/게임', '035720': '인터넷/게임',
        '051910': '화학', '006400': '자동차',
        '207940': '바이오', '068270': '음식료',
        '028260': '음식료', '105560': '금융',
    }

    def __init__(self, market_api=None, risk_free_rate: float = 0.03):
        """
        Initialize advanced portfolio optimizer

        Args:
            market_api: Market API instance
            risk_free_rate: Risk-free rate (annual)
        """
        self.market_api = market_api
        self.risk_free_rate = risk_free_rate
        self.cache_file = Path('data/portfolio_optimization_cache.json')
        self.cache_ttl = 300

        self._ensure_data_dir()
        logger.info(f"Advanced Portfolio Optimizer v7.0 initialized (rf={risk_free_rate:.2%})")

    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

    def _get_sector(self, stock_code: str) -> str:
        """Get sector for stock code"""
        if stock_code in self.SECTOR_MAP:
            return self.SECTOR_MAP[stock_code]

        code_int = int(stock_code)
        if code_int < 100000:
            return '제조업'
        elif code_int < 200000:
            return '서비스업'
        elif code_int < 300000:
            return '기술/IT'
        else:
            return '기타'

    def optimize_portfolio(
        self,
        positions_data: List[Dict],
        price_histories: Optional[Dict[str, List[Dict]]] = None,
        objective: OptimizationObjective = OptimizationObjective.BALANCED,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Optional[OptimizationResult]:
        """
        Comprehensive portfolio optimization

        Args:
            positions_data: Current positions
            price_histories: Historical price data for quantitative analysis
            objective: Optimization objective
            constraints: Optimization constraints

        Returns:
            OptimizationResult with complete analysis
        """
        try:
            if not positions_data:
                logger.warning("No positions to optimize")
                return None

            logger.info(f"Optimizing portfolio: {len(positions_data)} positions, objective={objective.value}")

            total_value = sum(p['value'] for p in positions_data)

            positions = self._create_positions(positions_data, total_value)
            sector_allocation = self._analyze_sectors(positions)
            metrics = self._calculate_metrics(positions, sector_allocation)

            optimal_weights = {}
            if price_histories and len(price_histories) >= 2:
                optimal_weights = self._optimize_weights(
                    price_histories, objective, constraints
                )

                if optimal_weights:
                    metrics = self._update_metrics_with_optimization(
                        metrics, optimal_weights, price_histories
                    )

            suggestions = self._generate_suggestions(
                positions, metrics, sector_allocation, optimal_weights
            )

            risk_level = self._determine_risk_level(metrics)
            rebalancing_needed = self._check_rebalancing_needed(
                positions, optimal_weights
            )

            return OptimizationResult(
                timestamp=datetime.now().isoformat(),
                objective=objective.value,
                metrics=metrics,
                positions=positions,
                sector_allocation=sector_allocation,
                optimal_weights=optimal_weights,
                suggestions=suggestions,
                risk_level=risk_level,
                rebalancing_needed=rebalancing_needed
            )

        except Exception as e:
            logger.error(f"Portfolio optimization failed: {e}")
            return None

    def _create_positions(
        self,
        positions_data: List[Dict],
        total_value: float
    ) -> List[PortfolioPosition]:
        """Create portfolio position objects"""
        positions = []

        for p in positions_data:
            quantity = p['quantity']
            avg_price = p['avg_price']
            current_price = p['current_price']
            value = p['value']

            profit_loss = value - (avg_price * quantity)
            profit_loss_percent = ((current_price - avg_price) / avg_price * 100) if avg_price > 0 else 0
            weight = (value / total_value * 100) if total_value > 0 else 0

            positions.append(PortfolioPosition(
                code=p['code'],
                name=p['name'],
                quantity=quantity,
                avg_price=avg_price,
                current_price=current_price,
                value=value,
                weight=weight,
                sector=self._get_sector(p['code']),
                profit_loss=profit_loss,
                profit_loss_percent=profit_loss_percent
            ))

        positions.sort(key=lambda x: x.weight, reverse=True)
        return positions

    def _analyze_sectors(
        self,
        positions: List[PortfolioPosition]
    ) -> List[SectorAllocation]:
        """Analyze sector allocation"""
        if not positions:
            return []

        sector_data: Dict[str, Dict] = {}

        for pos in positions:
            if pos.sector not in sector_data:
                sector_data[pos.sector] = {
                    'value': 0,
                    'count': 0,
                    'returns': []
                }

            sector_data[pos.sector]['value'] += pos.value
            sector_data[pos.sector]['count'] += 1
            sector_data[pos.sector]['returns'].append(pos.profit_loss_percent)

        total_value = sum(pos.value for pos in positions)

        allocations = []
        for sector, data in sector_data.items():
            weight = (data['value'] / total_value * 100) if total_value > 0 else 0
            avg_return = np.mean(data['returns']) if data['returns'] else 0

            allocations.append(SectorAllocation(
                sector=sector,
                value=data['value'],
                weight=weight,
                position_count=data['count'],
                avg_return=avg_return
            ))

        allocations.sort(key=lambda x: x.weight, reverse=True)
        return allocations

    def _calculate_metrics(
        self,
        positions: List[PortfolioPosition],
        sector_allocation: List[SectorAllocation]
    ) -> PortfolioMetrics:
        """Calculate portfolio metrics"""
        total_value = sum(p.value for p in positions)
        diversification_score = self._calculate_diversification_score(positions)
        concentration_risk, largest_weight, top3_weight = self._calculate_concentration_risk(positions)

        return PortfolioMetrics(
            total_value=total_value,
            position_count=len(positions),
            sector_count=len(set(p.sector for p in positions)),
            diversification_score=diversification_score,
            concentration_risk=concentration_risk,
            largest_position_weight=largest_weight,
            top3_concentration=top3_weight,
            avg_correlation=0.0,
            expected_return=0.0,
            expected_volatility=0.0,
            sharpe_ratio=0.0
        )

    def _update_metrics_with_optimization(
        self,
        metrics: PortfolioMetrics,
        optimal_weights: Dict[str, float],
        price_histories: Dict[str, List[Dict]]
    ) -> PortfolioMetrics:
        """Update metrics with optimization results"""
        returns_matrix = self._calculate_returns_matrix(price_histories)
        if returns_matrix is None:
            return metrics

        cov_matrix = self._calculate_covariance_matrix(returns_matrix)
        expected_returns = self._calculate_expected_returns(returns_matrix)
        stock_codes = list(price_histories.keys())

        weights_array = np.array([optimal_weights.get(code, 0) for code in stock_codes])
        portfolio_return = np.dot(weights_array, expected_returns)
        portfolio_variance = np.dot(weights_array, np.dot(cov_matrix, weights_array))
        portfolio_volatility = np.sqrt(portfolio_variance)
        sharpe = (portfolio_return - self.risk_free_rate) / (portfolio_volatility + 1e-10)

        metrics.expected_return = portfolio_return
        metrics.expected_volatility = portfolio_volatility
        metrics.sharpe_ratio = sharpe

        return metrics

    def _calculate_diversification_score(
        self,
        positions: List[PortfolioPosition]
    ) -> float:
        """
        Calculate diversification score (0-100)

        Higher score = better diversified
        """
        if not positions:
            return 0.0

        position_score = min(40, len(positions) * 4)

        sectors = set(p.sector for p in positions)
        sector_score = min(30, len(sectors) * 6)

        weights = [p.weight for p in positions]
        ideal_weight = 100.0 / len(positions)
        weight_variance = np.var([abs(w - ideal_weight) for w in weights])
        weight_score = max(0, 30 - weight_variance)

        total_score = position_score + sector_score + weight_score
        return min(100.0, total_score)

    def _calculate_concentration_risk(
        self,
        positions: List[PortfolioPosition]
    ) -> Tuple[str, float, float]:
        """
        Calculate concentration risk

        Returns:
            (risk_level, largest_position_weight, top3_weight)
        """
        if not positions:
            return 'Low', 0.0, 0.0

        weights = sorted([p.weight for p in positions], reverse=True)
        largest_weight = weights[0]
        top3_weight = sum(weights[:3]) if len(weights) >= 3 else sum(weights)

        if largest_weight > 40 or top3_weight > 70:
            risk = 'High'
        elif largest_weight > 25 or top3_weight > 50:
            risk = 'Medium'
        else:
            risk = 'Low'

        return risk, largest_weight, top3_weight

    def _optimize_weights(
        self,
        price_histories: Dict[str, List[Dict]],
        objective: OptimizationObjective,
        constraints: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Optimize portfolio weights using quantitative methods"""
        returns_matrix = self._calculate_returns_matrix(price_histories)
        if returns_matrix is None or len(returns_matrix) == 0:
            return {}

        cov_matrix = self._calculate_covariance_matrix(returns_matrix)
        expected_returns = self._calculate_expected_returns(returns_matrix)
        stock_codes = list(price_histories.keys())

        if constraints is None:
            constraints = {}

        max_weight = constraints.get('max_weight', 0.3)
        min_weight = constraints.get('min_weight', 0.05)
        allow_short = constraints.get('allow_short', False)

        if objective == OptimizationObjective.MAX_SHARPE:
            weights = self._maximize_sharpe_ratio(
                expected_returns, cov_matrix, stock_codes,
                max_weight, min_weight, allow_short
            )
        elif objective == OptimizationObjective.MIN_VOLATILITY:
            weights = self._minimize_volatility(
                cov_matrix, stock_codes, max_weight, min_weight, allow_short
            )
        elif objective == OptimizationObjective.RISK_PARITY:
            weights = self._risk_parity(cov_matrix, stock_codes)
        else:
            weights = self._balanced_weights(
                expected_returns, cov_matrix, stock_codes,
                max_weight, min_weight, allow_short
            )

        return weights

    def _maximize_sharpe_ratio(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        stock_codes: List[str],
        max_weight: float,
        min_weight: float,
        allow_short: bool
    ) -> Dict[str, float]:
        """Maximize Sharpe ratio"""
        num_stocks = len(stock_codes)
        weights = np.ones(num_stocks) / num_stocks

        if not allow_short:
            weights = np.clip(weights, min_weight, max_weight)
            weights = weights / np.sum(weights)

        learning_rate = 0.01
        num_iterations = 1000
        best_sharpe = -np.inf
        best_weights = weights.copy()

        for _ in range(num_iterations):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            sharpe = (portfolio_return - self.risk_free_rate) / (portfolio_volatility + 1e-10)

            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_weights = weights.copy()

            for i in range(num_stocks):
                test_weights = weights.copy()
                test_weights[i] += 0.001
                test_weights = test_weights / np.sum(test_weights)

                test_return = np.dot(test_weights, expected_returns)
                test_variance = np.dot(test_weights, np.dot(cov_matrix, test_weights))
                test_volatility = np.sqrt(test_variance)
                test_sharpe = (test_return - self.risk_free_rate) / (test_volatility + 1e-10)

                gradient = (test_sharpe - sharpe) / 0.001
                weights[i] += learning_rate * gradient

            if not allow_short:
                weights = np.clip(weights, min_weight, max_weight)

            weights = weights / np.sum(weights)

        return {stock_codes[i]: float(best_weights[i]) for i in range(num_stocks)}

    def _minimize_volatility(
        self,
        cov_matrix: np.ndarray,
        stock_codes: List[str],
        max_weight: float,
        min_weight: float,
        allow_short: bool
    ) -> Dict[str, float]:
        """Minimize portfolio volatility"""
        num_stocks = len(stock_codes)
        variances = np.diag(cov_matrix)
        inv_vol = 1 / np.sqrt(variances + 1e-10)
        weights = inv_vol / np.sum(inv_vol)

        if not allow_short:
            weights = np.clip(weights, min_weight, max_weight)
            weights = weights / np.sum(weights)

        return {stock_codes[i]: float(weights[i]) for i in range(num_stocks)}

    def _risk_parity(
        self,
        cov_matrix: np.ndarray,
        stock_codes: List[str]
    ) -> Dict[str, float]:
        """Risk parity weighting"""
        num_stocks = len(stock_codes)
        weights = np.ones(num_stocks) / num_stocks

        for _ in range(100):
            portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            marginal_risk = np.dot(cov_matrix, weights) / (portfolio_vol + 1e-10)
            risk_contribution = weights * marginal_risk
            target_risk = portfolio_vol / num_stocks
            adjustment = target_risk / (risk_contribution + 1e-10)
            weights = weights * adjustment
            weights = weights / np.sum(weights)

        return {stock_codes[i]: float(weights[i]) for i in range(num_stocks)}

    def _balanced_weights(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        stock_codes: List[str],
        max_weight: float,
        min_weight: float,
        allow_short: bool
    ) -> Dict[str, float]:
        """Balanced weighting combining return and risk"""
        sharpe_weights = self._maximize_sharpe_ratio(
            expected_returns, cov_matrix, stock_codes,
            max_weight, min_weight, allow_short
        )

        vol_weights = self._minimize_volatility(
            cov_matrix, stock_codes, max_weight, min_weight, allow_short
        )

        balanced = {}
        for code in stock_codes:
            balanced[code] = 0.6 * sharpe_weights.get(code, 0) + 0.4 * vol_weights.get(code, 0)

        total = sum(balanced.values())
        balanced = {k: v/total for k, v in balanced.items()}

        return balanced

    def _calculate_returns_matrix(
        self,
        price_histories: Dict[str, List[Dict]]
    ) -> Optional[np.ndarray]:
        """Calculate returns matrix from price histories"""
        returns_dict = {}

        for stock_code, history in price_histories.items():
            if len(history) < 20:
                logger.warning(f"Insufficient data for {stock_code}: {len(history)}")
                continue

            closes = np.array([h['close'] for h in history])
            returns = np.diff(closes) / closes[:-1]
            returns_dict[stock_code] = returns

        if not returns_dict:
            return None

        min_length = min(len(ret) for ret in returns_dict.values())
        stock_codes = list(returns_dict.keys())
        returns_matrix = np.array([
            returns_dict[code][:min_length] for code in stock_codes
        ])

        return returns_matrix.T

    def _calculate_covariance_matrix(
        self,
        returns_matrix: np.ndarray
    ) -> np.ndarray:
        """Calculate annualized covariance matrix"""
        cov_matrix = np.cov(returns_matrix.T)
        return cov_matrix * 252

    def _calculate_expected_returns(
        self,
        returns_matrix: np.ndarray
    ) -> np.ndarray:
        """Calculate annualized expected returns"""
        mean_returns = np.mean(returns_matrix, axis=0)
        return mean_returns * 252

    def _generate_suggestions(
        self,
        positions: List[PortfolioPosition],
        metrics: PortfolioMetrics,
        sector_allocation: List[SectorAllocation],
        optimal_weights: Dict[str, float]
    ) -> List[OptimizationSuggestion]:
        """Generate optimization suggestions"""
        suggestions = []

        if metrics.concentration_risk == 'High':
            if metrics.largest_position_weight > 40:
                suggestions.append(OptimizationSuggestion(
                    type='reduce',
                    priority='high',
                    title='⚠️ Concentration Risk: Largest position too big',
                    description=f'Largest position accounts for {metrics.largest_position_weight:.1f}% of portfolio',
                    action='Reduce largest position to below 25%',
                    impact='Risk reduction, improved stability'
                ))

        if sector_allocation:
            top_sector = sector_allocation[0]
            if top_sector.weight > 50:
                suggestions.append(OptimizationSuggestion(
                    type='diversify',
                    priority='high',
                    title=f'🏢 Sector Concentration: {top_sector.sector} overweight',
                    description=f'{top_sector.sector} sector is {top_sector.weight:.1f}% of portfolio',
                    action='Add positions from other sectors',
                    impact='Sector risk reduction, stability improvement'
                ))

        if metrics.diversification_score < 40:
            suggestions.append(OptimizationSuggestion(
                type='add',
                priority='high',
                title='📈 Insufficient Diversification',
                description=f'Diversification score: {metrics.diversification_score:.0f}/100 (Low)',
                action='Add 3-5 positions to improve diversification',
                impact='Risk reduction, return stability'
            ))

        if metrics.sharpe_ratio > 0 and optimal_weights:
            suggestions.append(OptimizationSuggestion(
                type='rebalance',
                priority='medium',
                title='⚖️ Rebalancing Opportunity',
                description=f'Optimal weights calculated (Sharpe: {metrics.sharpe_ratio:.2f})',
                action='Rebalance to optimal weights for better risk-adjusted returns',
                impact='Improved Sharpe ratio, optimized risk/return'
            ))

        if metrics.diversification_score >= 70 and metrics.concentration_risk == 'Low':
            suggestions.append(OptimizationSuggestion(
                type='maintain',
                priority='low',
                title='✅ Excellent Portfolio Construction',
                description=f'Diversification: {metrics.diversification_score:.0f}/100, Low concentration risk',
                action='Maintain current portfolio structure',
                impact='Stable risk-adjusted returns'
            ))

        return suggestions

    def _determine_risk_level(
        self,
        metrics: PortfolioMetrics
    ) -> str:
        """Determine overall portfolio risk level"""
        risk_score = 0

        if metrics.concentration_risk == 'High':
            risk_score += 3
        elif metrics.concentration_risk == 'Medium':
            risk_score += 2
        else:
            risk_score += 1

        if metrics.diversification_score < 40:
            risk_score += 3
        elif metrics.diversification_score < 60:
            risk_score += 2
        else:
            risk_score += 1

        if metrics.position_count < 3:
            risk_score += 2
        elif metrics.position_count < 5:
            risk_score += 1

        if risk_score >= 7:
            return 'Aggressive'
        elif risk_score >= 5:
            return 'Moderate'
        else:
            return 'Conservative'

    def _check_rebalancing_needed(
        self,
        positions: List[PortfolioPosition],
        optimal_weights: Dict[str, float],
        threshold: float = 0.05
    ) -> bool:
        """Check if rebalancing is needed"""
        if not optimal_weights:
            return False

        for pos in positions:
            current_weight = pos.weight / 100
            optimal_weight = optimal_weights.get(pos.code, 0)
            if abs(current_weight - optimal_weight) > threshold:
                return True

        return False

    def get_rebalancing_orders(
        self,
        positions: List[PortfolioPosition],
        optimal_weights: Dict[str, float],
        portfolio_value: float,
        min_trade_amount: float = 100000,
        threshold: float = 0.05
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate rebalancing orders

        Returns:
            Dict[stock_code, {'action': 'buy'/'sell', 'amount': float, 'weight_diff': float}]
        """
        orders = {}

        for pos in positions:
            current_weight = pos.weight / 100
            optimal_weight = optimal_weights.get(pos.code, 0)
            weight_diff = optimal_weight - current_weight

            if abs(weight_diff) < threshold:
                continue

            trade_amount = abs(weight_diff) * portfolio_value

            if trade_amount < min_trade_amount:
                continue

            action = 'buy' if weight_diff > 0 else 'sell'

            orders[pos.code] = {
                'action': action,
                'amount': trade_amount,
                'weight_diff': weight_diff,
                'current_weight': current_weight,
                'optimal_weight': optimal_weight
            }

        return orders


_advanced_portfolio_optimizer_instance = None


def get_advanced_portfolio_optimizer(
    market_api=None,
    risk_free_rate: float = 0.03
) -> AdvancedPortfolioOptimizer:
    """
    Get or create singleton instance

    Args:
        market_api: Market API instance
        risk_free_rate: Risk-free rate

    Returns:
        AdvancedPortfolioOptimizer singleton
    """
    global _advanced_portfolio_optimizer_instance

    if _advanced_portfolio_optimizer_instance is None:
        _advanced_portfolio_optimizer_instance = AdvancedPortfolioOptimizer(
            market_api=market_api,
            risk_free_rate=risk_free_rate
        )

    return _advanced_portfolio_optimizer_instance


__all__ = [
    'AdvancedPortfolioOptimizer',
    'OptimizationObjective',
    'OptimizationResult',
    'PortfolioPosition',
    'SectorAllocation',
    'PortfolioMetrics',
    'OptimizationSuggestion',
    'EfficientFrontierPoint',
    'get_advanced_portfolio_optimizer'
]
