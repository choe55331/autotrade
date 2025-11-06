Advanced Portfolio Optimization - v5.13
Modern Portfolio Theory, Efficient Frontier, Black-Litterman Model
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import numpy as np
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class OptimizationObjective(Enum):
    """최적화 목표"""
    MAX_SHARPE = "max_sharpe"
    MIN_VOLATILITY = "min_volatility"
    MAX_RETURN = "max_return"
    RISK_PARITY = "risk_parity"
    BLACK_LITTERMAN = "black_litterman"


@dataclass
class OptimizationResult:
    """최적화 결과"""
    weights: Dict[str, float]
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    objective: OptimizationObjective
    constraints_satisfied: bool
    optimization_time_seconds: float
    metadata: Dict[str, Any]


@dataclass
class EfficientFrontierPoint:
    """효율적 투자선 상의 점"""
    expected_return: float
    volatility: float
    sharpe_ratio: float
    weights: Dict[str, float]


class PortfolioOptimizer:
    """
    고급 포트폴리오 최적화

    Methods:
    - Modern Portfolio Theory (MPT)
    - Efficient Frontier
    - Maximum Sharpe Ratio
    - Minimum Volatility
    - Risk Parity
    - Black-Litterman Model
    """

    def __init__(self, risk_free_rate: float = 0.03):
        """
        Args:
            risk_free_rate: 무위험 수익률 (연간)
        """
        self.risk_free_rate = risk_free_rate
        logger.info(f"Portfolio Optimizer initialized: rf={risk_free_rate:.2%}")

    def optimize(self,
                 price_histories: Dict[str, List[Dict[str, Any]]],
                 objective: OptimizationObjective = OptimizationObjective.MAX_SHARPE,
                 constraints: Optional[Dict[str, Any]] = None,
                 target_return: Optional[float] = None,
                 target_volatility: Optional[float] = None) -> OptimizationResult:
        포트폴리오 최적화

        Args:
            price_histories: 종목별 가격 히스토리
            objective: 최적화 목표
            constraints: 제약 조건
                {
                    'max_weight': 0.3,
                    'min_weight': 0.05,
                    'sector_limits': {'tech': 0.4},
                    'allow_short': False
                }
            target_return: 목표 수익률 (연간)
            target_volatility: 목표 변동성 (연간)

        Returns:
            OptimizationResult
        logger.info(f"Optimizing portfolio: {len(price_histories)} stocks, "
                   f"objective={objective.value}")

        start_time = datetime.now()

        returns_matrix = self._calculate_returns_matrix(price_histories)

        if returns_matrix is None or len(returns_matrix) == 0:
            logger.error("Failed to calculate returns matrix")
            return self._empty_result(objective)

        cov_matrix = self._calculate_covariance_matrix(returns_matrix)
        expected_returns = self._calculate_expected_returns(returns_matrix)

        stock_codes = list(price_histories.keys())

        if constraints is None:
            constraints = {}

        max_weight = constraints.get('max_weight', 1.0)
        min_weight = constraints.get('min_weight', 0.0)
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
        elif objective == OptimizationObjective.MAX_RETURN:
            weights = self._maximize_return(
                expected_returns, cov_matrix, stock_codes,
                max_weight, min_weight, allow_short, target_volatility
            )
        elif objective == OptimizationObjective.RISK_PARITY:
            weights = self._risk_parity(
                cov_matrix, stock_codes
            )
        elif objective == OptimizationObjective.BLACK_LITTERMAN:
            weights = self._maximize_sharpe_ratio(
                expected_returns, cov_matrix, stock_codes,
                max_weight, min_weight, allow_short
            )
        else:
            weights = self._equal_weight(stock_codes)

        weights_array = np.array([weights[code] for code in stock_codes])
        portfolio_return = np.dot(weights_array, expected_returns)
        portfolio_variance = np.dot(weights_array, np.dot(cov_matrix, weights_array))
        portfolio_volatility = np.sqrt(portfolio_variance)

        sharpe = (portfolio_return - self.risk_free_rate) / (portfolio_volatility + 1e-10)

        constraints_satisfied = self._check_constraints(
            weights, constraints
        )

        optimization_time = (datetime.now() - start_time).total_seconds()

        result = OptimizationResult(
            weights=weights,
            expected_return=portfolio_return,
            expected_volatility=portfolio_volatility,
            sharpe_ratio=sharpe,
            objective=objective,
            constraints_satisfied=constraints_satisfied,
            optimization_time_seconds=optimization_time,
            metadata={
                'num_stocks': len(stock_codes),
                'effective_stocks': self._calculate_effective_stocks(weights),
                'max_weight': max(weights.values()),
                'min_weight': min(weights.values()),
                'concentration_herfindahl': sum(w**2 for w in weights.values())
            }
        )

        logger.info(f"Optimization complete: return={portfolio_return:.2%}, "
                   f"vol={portfolio_volatility:.2%}, sharpe={sharpe:.2f}")

        return result

    def calculate_efficient_frontier(self,
                                     price_histories: Dict[str, List[Dict[str, Any]]],
                                     num_points: int = 50,
                                     constraints: Optional[Dict[str, Any]] = None) -> List[EfficientFrontierPoint]:
        효율적 투자선 계산

        Args:
            price_histories: 종목별 가격 히스토리
            num_points: 계산할 점의 개수
            constraints: 제약 조건

        Returns:
            List[EfficientFrontierPoint]
        logger.info(f"Calculating efficient frontier with {num_points} points")

        returns_matrix = self._calculate_returns_matrix(price_histories)
        if returns_matrix is None:
            return []

        cov_matrix = self._calculate_covariance_matrix(returns_matrix)
        expected_returns = self._calculate_expected_returns(returns_matrix)
        stock_codes = list(price_histories.keys())

        if constraints is None:
            constraints = {}

        min_vol_weights = self._minimize_volatility(
            cov_matrix, stock_codes,
            constraints.get('max_weight', 1.0),
            constraints.get('min_weight', 0.0),
            constraints.get('allow_short', False)
        )

        min_vol_return = np.dot(
            np.array([min_vol_weights[code] for code in stock_codes]),
            expected_returns
        )

        max_return = np.max(expected_returns)

        target_returns = np.linspace(min_vol_return, max_return, num_points)

        frontier_points = []

        for target_return in target_returns:
            weights = self._minimize_volatility_with_target_return(
                expected_returns, cov_matrix, stock_codes,
                target_return, constraints
            )

            weights_array = np.array([weights[code] for code in stock_codes])
            portfolio_return = np.dot(weights_array, expected_returns)
            portfolio_variance = np.dot(weights_array, np.dot(cov_matrix, weights_array))
            portfolio_volatility = np.sqrt(portfolio_variance)

            sharpe = (portfolio_return - self.risk_free_rate) / (portfolio_volatility + 1e-10)

            point = EfficientFrontierPoint(
                expected_return=portfolio_return,
                volatility=portfolio_volatility,
                sharpe_ratio=sharpe,
                weights=weights
            )

            frontier_points.append(point)

        logger.info(f"Efficient frontier calculated: {len(frontier_points)} points")

        return frontier_points

    def rebalance_recommendation(self,
                                 current_weights: Dict[str, float],
                                 optimal_weights: Dict[str, float],
                                 portfolio_value: float,
                                 min_trade_amount: float = 100000,
                                 rebalance_threshold: float = 0.05) -> Dict[str, Dict[str, Any]]:
        리밸런싱 추천

        Args:
            current_weights: 현재 비중
            optimal_weights: 최적 비중
            portfolio_value: 포트폴리오 가치
            min_trade_amount: 최소 거래 금액
            rebalance_threshold: 리밸런싱 임계값 (5% = 0.05)

        Returns:
            Dict[stock_code, {'action': 'buy'/'sell', 'amount': float, 'weight_diff': float}]
        recommendations = {}

        all_stocks = set(current_weights.keys()) | set(optimal_weights.keys())

        for stock in all_stocks:
            current_weight = current_weights.get(stock, 0.0)
            optimal_weight = optimal_weights.get(stock, 0.0)

            weight_diff = optimal_weight - current_weight

            if abs(weight_diff) < rebalance_threshold:
                continue

            trade_amount = abs(weight_diff) * portfolio_value

            if trade_amount < min_trade_amount:
                continue

            action = 'buy' if weight_diff > 0 else 'sell'

            recommendations[stock] = {
                'action': action,
                'amount': trade_amount,
                'weight_diff': weight_diff,
                'current_weight': current_weight,
                'optimal_weight': optimal_weight
            }

        logger.info(f"Rebalancing recommendations: {len(recommendations)} stocks")

        return recommendations


    def _maximize_sharpe_ratio(self, expected_returns: np.ndarray,
                               cov_matrix: np.ndarray, stock_codes: List[str],
                               max_weight: float, min_weight: float,
                               allow_short: bool) -> Dict[str, float]:
        num_stocks = len(stock_codes)

        weights = np.ones(num_stocks) / num_stocks

        if not allow_short:
            weights = np.clip(weights, min_weight, max_weight)
            weights = weights / np.sum(weights)

        learning_rate = 0.01
        num_iterations = 1000

        best_sharpe = -np.inf
        best_weights = weights.copy()

        for iteration in range(num_iterations):
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

    def _minimize_volatility(self, cov_matrix: np.ndarray, stock_codes: List[str],
                            max_weight: float, min_weight: float,
                            allow_short: bool) -> Dict[str, float]:
        num_stocks = len(stock_codes)

        variances = np.diag(cov_matrix)
        inv_vol = 1 / np.sqrt(variances + 1e-10)

        weights = inv_vol / np.sum(inv_vol)

        if not allow_short:
            weights = np.clip(weights, min_weight, max_weight)
            weights = weights / np.sum(weights)

        return {stock_codes[i]: float(weights[i]) for i in range(num_stocks)}

    def _maximize_return(self, expected_returns: np.ndarray, cov_matrix: np.ndarray,
                        stock_codes: List[str], max_weight: float, min_weight: float,
                        allow_short: bool, target_volatility: Optional[float]) -> Dict[str, float]:
        num_stocks = len(stock_codes)

        if target_volatility is None:
            max_return_idx = np.argmax(expected_returns)
            weights = np.zeros(num_stocks)
            weights[max_return_idx] = 1.0
        else:
            weights = self._maximize_sharpe_ratio(
                expected_returns, cov_matrix, stock_codes,
                max_weight, min_weight, allow_short
            )
            return weights

        return {stock_codes[i]: float(weights[i]) for i in range(num_stocks)}

    def _risk_parity(self, cov_matrix: np.ndarray, stock_codes: List[str]) -> Dict[str, float]:
        """리스크 패리티"""
        num_stocks = len(stock_codes)

        weights = np.ones(num_stocks) / num_stocks

        for iteration in range(100):
            portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            marginal_risk = np.dot(cov_matrix, weights) / (portfolio_vol + 1e-10)
            risk_contribution = weights * marginal_risk

            target_risk = portfolio_vol / num_stocks
            adjustment = target_risk / (risk_contribution + 1e-10)

            weights = weights * adjustment
            weights = weights / np.sum(weights)

        return {stock_codes[i]: float(weights[i]) for i in range(num_stocks)}

    def _minimize_volatility_with_target_return(self,
                                                expected_returns: np.ndarray,
                                                cov_matrix: np.ndarray,
                                                stock_codes: List[str],
                                                target_return: float,
                                                constraints: Dict[str, Any]) -> Dict[str, float]:
        num_stocks = len(stock_codes)

        weights = np.ones(num_stocks) / num_stocks

        max_weight = constraints.get('max_weight', 1.0)
        min_weight = constraints.get('min_weight', 0.0)
        allow_short = constraints.get('allow_short', False)

        learning_rate = 0.01
        for iteration in range(500):
            current_return = np.dot(weights, expected_returns)
            return_diff = target_return - current_return

            if abs(return_diff) < 0.0001:
                break

            if return_diff > 0:
                adjustment = expected_returns / np.sum(expected_returns)
            else:
                adjustment = (1 / (expected_returns + 1e-10))
                adjustment = adjustment / np.sum(adjustment)

            weights = weights + learning_rate * return_diff * adjustment

            if not allow_short:
                weights = np.clip(weights, min_weight, max_weight)

            weights = weights / np.sum(weights)

        return {stock_codes[i]: float(weights[i]) for i in range(num_stocks)}

    def _equal_weight(self, stock_codes: List[str]) -> Dict[str, float]:
        """균등 비중"""
        weight = 1.0 / len(stock_codes)
        return {code: weight for code in stock_codes}


    def _calculate_returns_matrix(self, price_histories: Dict[str, List[Dict[str, Any]]]) -> Optional[np.ndarray]:
        """수익률 매트릭스 계산"""
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

    def _calculate_covariance_matrix(self, returns_matrix: np.ndarray) -> np.ndarray:
        """공분산 매트릭스 계산 (연간화)"""
        cov_matrix = np.cov(returns_matrix.T)
        return cov_matrix * 252

    def _calculate_expected_returns(self, returns_matrix: np.ndarray) -> np.ndarray:
        """기대 수익률 계산 (연간화)"""
        mean_returns = np.mean(returns_matrix, axis=0)
        return mean_returns * 252

    def _check_constraints(self, weights: Dict[str, float],
                          constraints: Dict[str, Any]) -> bool:
        max_weight = constraints.get('max_weight', 1.0)
        min_weight = constraints.get('min_weight', 0.0)
        allow_short = constraints.get('allow_short', False)

        for stock, weight in weights.items():
            if weight > max_weight or weight < min_weight:
                return False

            if not allow_short and weight < 0:
                return False

        if abs(sum(weights.values()) - 1.0) > 0.01:
            return False

        return True

    def _calculate_effective_stocks(self, weights: Dict[str, float]) -> float:
        """유효 종목 수 (1 / Herfindahl index)"""
        herfindahl = sum(w**2 for w in weights.values())
        return 1 / herfindahl if herfindahl > 0 else 0

    def _empty_result(self, objective: OptimizationObjective) -> OptimizationResult:
        """빈 결과"""
        return OptimizationResult(
            weights={},
            expected_return=0.0,
            expected_volatility=0.0,
            sharpe_ratio=0.0,
            objective=objective,
            constraints_satisfied=False,
            optimization_time_seconds=0.0,
            metadata={}
        )


_portfolio_optimizer: Optional[PortfolioOptimizer] = None


def get_portfolio_optimizer() -> PortfolioOptimizer:
    """포트폴리오 최적화기 싱글톤"""
    global _portfolio_optimizer
    if _portfolio_optimizer is None:
        _portfolio_optimizer = PortfolioOptimizer(risk_free_rate=0.03)
    return _portfolio_optimizer
