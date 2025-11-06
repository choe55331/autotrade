"""
Comprehensive Risk Analysis System - v5.12
VaR, CVaR, Stress Testing, Portfolio Risk Metrics
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class RiskMetrics:
    """리스크 메트릭"""
    stock_code: str
    stock_name: str

    # Volatility Metrics
    historical_volatility: float  # Annualized
    parkinson_volatility: float  # High-Low based
    garman_klass_volatility: float  # OHLC based

    # Value at Risk
    var_95: float  # 95% VaR (daily)
    var_99: float  # 99% VaR (daily)
    cvar_95: float  # Conditional VaR (Expected Shortfall)
    cvar_99: float  # 99% CVaR

    # Drawdown Metrics
    current_drawdown: float
    max_drawdown: float
    max_drawdown_duration_days: int
    recovery_period_days: int

    # Beta and Correlation
    beta: float  # vs market index
    correlation_with_market: float
    systematic_risk: float  # Beta * market volatility
    idiosyncratic_risk: float  # Total risk - systematic risk

    # Tail Risk
    skewness: float  # Return distribution skewness
    kurtosis: float  # Return distribution kurtosis (excess)
    tail_ratio: float  # Ratio of positive to negative tail

    # Liquidity Risk
    avg_daily_volume: float
    volume_volatility: float
    bid_ask_spread_proxy: float  # High-Low range as proxy

    # Position Risk
    position_size_risk: float  # % of portfolio
    leverage_risk: float
    concentration_risk: float

    # Risk-Adjusted Returns
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float  # Return / Max Drawdown
    omega_ratio: float

    # Stress Test Results
    stress_test_scenarios: Dict[str, float]

    # Overall Risk Score
    risk_score: float  # 0-100 (higher = riskier)
    risk_grade: str  # "LOW", "MEDIUM", "HIGH", "EXTREME"

    calculated_at: str


@dataclass
class PortfolioRiskMetrics:
    """포트폴리오 리스크 메트릭"""
    portfolio_value: float

    # Portfolio VaR
    portfolio_var_95: float
    portfolio_var_99: float
    portfolio_cvar_95: float
    diversification_ratio: float  # Portfolio risk / sum of individual risks

    # Correlation Matrix
    correlation_matrix: Dict[str, Dict[str, float]]

    # Concentration Risk
    herfindahl_index: float  # Sum of squared weights
    effective_stocks: float  # 1 / Herfindahl
    max_position_weight: float
    top_5_concentration: float  # Weight of top 5 positions

    # Factor Exposures
    market_beta: float
    sector_exposure: Dict[str, float]

    # Portfolio Drawdown
    current_drawdown: float
    max_drawdown: float

    # Risk-Adjusted Returns
    sharpe_ratio: float
    sortino_ratio: float

    # Stress Test Results
    stress_test_results: Dict[str, float]

    # Overall Assessment
    risk_score: float
    risk_capacity_utilization: float  # % of max acceptable risk
    recommendations: List[str]

    calculated_at: str


class RiskAnalyzer:
    """
    포괄적인 리스크 분석 시스템
    """

    def __init__(self, risk_free_rate: float = 0.03):
        """
        Args:
            risk_free_rate: 무위험 수익률 (연간)
        """
        self.risk_free_rate = risk_free_rate
        logger.info(f"Risk Analyzer initialized: risk_free_rate={risk_free_rate:.2%}")

    def analyze_stock_risk(self, stock_code: str, stock_name: str,
                          price_history: List[Dict[str, Any]],
                          market_index_history: Optional[List[Dict[str, Any]]] = None,
                          position_size: float = 0.0,
                          portfolio_value: float = 0.0) -> RiskMetrics:
        """
        종목 리스크 분석

        Args:
            stock_code: 종목 코드
            stock_name: 종목명
            price_history: 가격 데이터 (OHLCV)
            market_index_history: 시장 지수 데이터
            position_size: 포지션 크기 (금액)
            portfolio_value: 포트폴리오 총 가치

        Returns:
            RiskMetrics
        """
        logger.info(f"Analyzing risk for {stock_name} ({stock_code})")

        if len(price_history) < 20:
            logger.warning(f"Insufficient data for risk analysis: {len(price_history)}")
            return self._empty_risk_metrics(stock_code, stock_name)

        # Extract data
        closes = np.array([p['close'] for p in price_history])
        opens = np.array([p.get('open', p['close']) for p in price_history])
        highs = np.array([p.get('high', p['close']) for p in price_history])
        lows = np.array([p.get('low', p['close']) for p in price_history])
        volumes = np.array([p.get('volume', 0) for p in price_history])

        # Calculate returns
        returns = np.diff(closes) / closes[:-1]

        # === VOLATILITY METRICS ===
        historical_vol = self._historical_volatility(returns)
        parkinson_vol = self._parkinson_volatility(highs, lows)
        gk_vol = self._garman_klass_volatility(opens, highs, lows, closes)

        # === VALUE AT RISK ===
        var_95 = self._value_at_risk(returns, confidence=0.95)
        var_99 = self._value_at_risk(returns, confidence=0.99)
        cvar_95 = self._conditional_var(returns, confidence=0.95)
        cvar_99 = self._conditional_var(returns, confidence=0.99)

        # === DRAWDOWN METRICS ===
        dd_metrics = self._calculate_drawdown_metrics(closes)

        # === BETA AND CORRELATION ===
        if market_index_history and len(market_index_history) >= len(price_history):
            market_closes = np.array([m['close'] for m in market_index_history[:len(price_history)]])
            market_returns = np.diff(market_closes) / market_closes[:-1]

            beta = self._calculate_beta(returns, market_returns)
            correlation = np.corrcoef(returns, market_returns)[0, 1]

            market_vol = np.std(market_returns) * np.sqrt(252)
            systematic_risk = abs(beta) * market_vol
            idiosyncratic_risk = max(0, historical_vol - systematic_risk)
        else:
            beta = 1.0
            correlation = 0.0
            systematic_risk = historical_vol * 0.7
            idiosyncratic_risk = historical_vol * 0.3

        # === TAIL RISK ===
        skewness = self._calculate_skewness(returns)
        kurtosis = self._calculate_kurtosis(returns)
        tail_ratio = self._calculate_tail_ratio(returns)

        # === LIQUIDITY RISK ===
        avg_volume = np.mean(volumes)
        volume_vol = np.std(volumes) / (avg_volume + 1)
        bid_ask_proxy = np.mean((highs - lows) / closes)

        # === POSITION RISK ===
        position_size_risk = position_size / portfolio_value if portfolio_value > 0 else 0
        leverage_risk = 0.0  # Placeholder
        concentration_risk = position_size_risk  # Simplified

        # === RISK-ADJUSTED RETURNS ===
        avg_return = np.mean(returns) * 252  # Annualized
        sharpe = self._sharpe_ratio(returns, self.risk_free_rate)
        sortino = self._sortino_ratio(returns, self.risk_free_rate)
        calmar = avg_return / (dd_metrics['max_drawdown'] + 0.01)
        omega = self._omega_ratio(returns, self.risk_free_rate)

        # === STRESS TESTS ===
        stress_scenarios = self._run_stress_tests(closes[-1], historical_vol)

        # === OVERALL RISK SCORE ===
        risk_score = self._calculate_risk_score({
            'volatility': historical_vol,
            'max_drawdown': dd_metrics['max_drawdown'],
            'var_95': abs(var_95),
            'cvar_95': abs(cvar_95),
            'kurtosis': kurtosis,
            'concentration': concentration_risk
        })

        if risk_score < 30:
            risk_grade = "LOW"
        elif risk_score < 60:
            risk_grade = "MEDIUM"
        elif risk_score < 80:
            risk_grade = "HIGH"
        else:
            risk_grade = "EXTREME"

        metrics = RiskMetrics(
            stock_code=stock_code,
            stock_name=stock_name,
            historical_volatility=historical_vol,
            parkinson_volatility=parkinson_vol,
            garman_klass_volatility=gk_vol,
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            cvar_99=cvar_99,
            current_drawdown=dd_metrics['current_drawdown'],
            max_drawdown=dd_metrics['max_drawdown'],
            max_drawdown_duration_days=dd_metrics['max_dd_duration'],
            recovery_period_days=dd_metrics['recovery_period'],
            beta=beta,
            correlation_with_market=correlation,
            systematic_risk=systematic_risk,
            idiosyncratic_risk=idiosyncratic_risk,
            skewness=skewness,
            kurtosis=kurtosis,
            tail_ratio=tail_ratio,
            avg_daily_volume=avg_volume,
            volume_volatility=volume_vol,
            bid_ask_spread_proxy=bid_ask_proxy,
            position_size_risk=position_size_risk,
            leverage_risk=leverage_risk,
            concentration_risk=concentration_risk,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            calmar_ratio=calmar,
            omega_ratio=omega,
            stress_test_scenarios=stress_scenarios,
            risk_score=risk_score,
            risk_grade=risk_grade,
            calculated_at=datetime.now().isoformat()
        )

        logger.info(f"Risk analysis complete: {stock_name} - "
                   f"Risk Score: {risk_score:.1f} ({risk_grade}), "
                   f"Sharpe: {sharpe:.2f}, Max DD: {dd_metrics['max_drawdown']:.1%}")

        return metrics

    def analyze_portfolio_risk(self, positions: List[Dict[str, Any]],
                               portfolio_value: float,
                               price_histories: Dict[str, List[Dict[str, Any]]],
                               correlation_matrix: Optional[Dict[str, Dict[str, float]]] = None) -> PortfolioRiskMetrics:
        """
        포트폴리오 리스크 분석

        Args:
            positions: 포지션 목록 [{'stock_code': '', 'value': float, ...}]
            portfolio_value: 포트폴리오 총 가치
            price_histories: 종목별 가격 데이터
            correlation_matrix: 상관관계 매트릭스 (optional)

        Returns:
            PortfolioRiskMetrics
        """
        logger.info(f"Analyzing portfolio risk: {len(positions)} positions, "
                   f"value={portfolio_value:,.0f}")

        if not positions:
            return self._empty_portfolio_metrics(portfolio_value)

        # Calculate weights
        weights = {p['stock_code']: p['value'] / portfolio_value for p in positions}

        # Calculate individual returns and volatilities
        stock_returns = {}
        stock_vols = {}

        for stock_code, history in price_histories.items():
            if len(history) < 20:
                continue

            closes = np.array([h['close'] for h in history])
            returns = np.diff(closes) / closes[:-1]

            stock_returns[stock_code] = returns
            stock_vols[stock_code] = np.std(returns) * np.sqrt(252)

        # Build correlation matrix if not provided
        if correlation_matrix is None:
            correlation_matrix = self._build_correlation_matrix(stock_returns)

        # === PORTFOLIO VAR ===
        portfolio_var_95, portfolio_var_99 = self._calculate_portfolio_var(
            weights, stock_vols, stock_returns, correlation_matrix
        )
        portfolio_cvar_95 = self._calculate_portfolio_cvar(
            weights, stock_returns, confidence=0.95
        )

        # === DIVERSIFICATION RATIO ===
        diversification_ratio = self._calculate_diversification_ratio(
            weights, stock_vols, correlation_matrix
        )

        # === CONCENTRATION RISK ===
        herfindahl = sum(w**2 for w in weights.values())
        effective_stocks = 1 / herfindahl if herfindahl > 0 else 0
        max_weight = max(weights.values()) if weights else 0

        sorted_weights = sorted(weights.values(), reverse=True)
        top_5_concentration = sum(sorted_weights[:5]) if len(sorted_weights) >= 5 else sum(sorted_weights)

        # === FACTOR EXPOSURES ===
        market_beta = np.mean([1.0] * len(positions))  # Placeholder
        sector_exposure = {}  # Placeholder

        # === PORTFOLIO DRAWDOWN ===
        # Calculate portfolio equity curve
        portfolio_returns = self._calculate_portfolio_returns(weights, stock_returns)

        if len(portfolio_returns) > 0:
            portfolio_equity = np.cumprod(1 + portfolio_returns) * portfolio_value
            dd_metrics = self._calculate_drawdown_metrics(portfolio_equity)
            current_dd = dd_metrics['current_drawdown']
            max_dd = dd_metrics['max_drawdown']
        else:
            current_dd = 0.0
            max_dd = 0.0

        # === RISK-ADJUSTED RETURNS ===
        if len(portfolio_returns) > 0:
            sharpe = self._sharpe_ratio(portfolio_returns, self.risk_free_rate)
            sortino = self._sortino_ratio(portfolio_returns, self.risk_free_rate)
        else:
            sharpe = 0.0
            sortino = 0.0

        # === STRESS TESTS ===
        stress_results = self._run_portfolio_stress_tests(
            weights, stock_vols, portfolio_value
        )

        # === OVERALL RISK ASSESSMENT ===
        risk_score = self._calculate_portfolio_risk_score({
            'concentration': herfindahl,
            'max_drawdown': max_dd,
            'var_95': abs(portfolio_var_95 / portfolio_value),
            'diversification': 1 - diversification_ratio
        })

        risk_capacity = 100.0  # Max acceptable risk
        risk_utilization = (risk_score / risk_capacity) * 100

        # === RECOMMENDATIONS ===
        recommendations = self._generate_risk_recommendations({
            'concentration': herfindahl,
            'max_weight': max_weight,
            'diversification_ratio': diversification_ratio,
            'risk_score': risk_score,
            'max_drawdown': max_dd
        })

        metrics = PortfolioRiskMetrics(
            portfolio_value=portfolio_value,
            portfolio_var_95=portfolio_var_95,
            portfolio_var_99=portfolio_var_99,
            portfolio_cvar_95=portfolio_cvar_95,
            diversification_ratio=diversification_ratio,
            correlation_matrix=correlation_matrix,
            herfindahl_index=herfindahl,
            effective_stocks=effective_stocks,
            max_position_weight=max_weight,
            top_5_concentration=top_5_concentration,
            market_beta=market_beta,
            sector_exposure=sector_exposure,
            current_drawdown=current_dd,
            max_drawdown=max_dd,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            stress_test_results=stress_results,
            risk_score=risk_score,
            risk_capacity_utilization=risk_utilization,
            recommendations=recommendations,
            calculated_at=datetime.now().isoformat()
        )

        logger.info(f"Portfolio risk analysis complete: Risk Score={risk_score:.1f}, "
                   f"Sharpe={sharpe:.2f}, Diversification={diversification_ratio:.2f}")

        return metrics

    # ===== VOLATILITY CALCULATIONS =====

    def _historical_volatility(self, returns: np.ndarray) -> float:
        """Historical volatility (annualized)"""
        return np.std(returns) * np.sqrt(252)

    def _parkinson_volatility(self, highs: np.ndarray, lows: np.ndarray) -> float:
        """Parkinson volatility (high-low based)"""
        hl_ratios = np.log(highs / lows)
        return np.sqrt(np.mean(hl_ratios**2) / (4 * np.log(2))) * np.sqrt(252)

    def _garman_klass_volatility(self, opens: np.ndarray, highs: np.ndarray,
                                 lows: np.ndarray, closes: np.ndarray) -> float:
        """Garman-Klass volatility (OHLC based)"""
        hl = np.log(highs / lows)
        co = np.log(closes / opens)
        gk = 0.5 * hl**2 - (2*np.log(2) - 1) * co**2
        return np.sqrt(np.mean(gk)) * np.sqrt(252)

    # ===== VAR CALCULATIONS =====

    def _value_at_risk(self, returns: np.ndarray, confidence: float = 0.95) -> float:
        """Value at Risk (historical method)"""
        return np.percentile(returns, (1 - confidence) * 100)

    def _conditional_var(self, returns: np.ndarray, confidence: float = 0.95) -> float:
        """Conditional VaR (Expected Shortfall)"""
        var = self._value_at_risk(returns, confidence)
        return np.mean(returns[returns <= var])

    def _calculate_portfolio_var(self, weights: Dict[str, float],
                                 volatilities: Dict[str, float],
                                 returns: Dict[str, np.ndarray],
                                 correlation_matrix: Dict[str, Dict[str, float]]) -> Tuple[float, float]:
        """Portfolio VaR calculation"""
        # Simplified calculation
        # In production: use covariance matrix properly

        portfolio_vol = 0.0
        for stock1, w1 in weights.items():
            for stock2, w2 in weights.items():
                if stock1 in volatilities and stock2 in volatilities:
                    corr = correlation_matrix.get(stock1, {}).get(stock2, 0.0)
                    portfolio_vol += w1 * w2 * volatilities[stock1] * volatilities[stock2] * corr

        portfolio_vol = np.sqrt(max(0, portfolio_vol))

        # Convert to daily
        daily_vol = portfolio_vol / np.sqrt(252)

        # VaR at 95% and 99%
        var_95 = -1.65 * daily_vol  # Z-score for 95%
        var_99 = -2.33 * daily_vol  # Z-score for 99%

        return var_95, var_99

    def _calculate_portfolio_cvar(self, weights: Dict[str, float],
                                  returns: Dict[str, np.ndarray],
                                  confidence: float = 0.95) -> float:
        """Portfolio CVaR"""
        # Calculate portfolio returns
        portfolio_returns = self._calculate_portfolio_returns(weights, returns)

        if len(portfolio_returns) == 0:
            return 0.0

        return self._conditional_var(portfolio_returns, confidence)

    # ===== DRAWDOWN CALCULATIONS =====

    def _calculate_drawdown_metrics(self, equity_curve: np.ndarray) -> Dict[str, Any]:
        """Drawdown metrics"""
        running_max = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - running_max) / running_max

        current_dd = drawdown[-1]
        max_dd = np.min(drawdown)

        # Max drawdown duration
        in_drawdown = drawdown < 0
        dd_periods = []
        current_period = 0

        for is_dd in in_drawdown:
            if is_dd:
                current_period += 1
            else:
                if current_period > 0:
                    dd_periods.append(current_period)
                current_period = 0

        max_dd_duration = max(dd_periods) if dd_periods else 0

        # Recovery period (from last peak to current)
        last_peak_idx = np.argmax(running_max == equity_curve[-1])
        recovery_period = len(equity_curve) - last_peak_idx - 1

        return {
            'current_drawdown': current_dd,
            'max_drawdown': max_dd,
            'max_dd_duration': max_dd_duration,
            'recovery_period': recovery_period
        }

    # ===== BETA AND CORRELATION =====

    def _calculate_beta(self, stock_returns: np.ndarray,
                       market_returns: np.ndarray) -> float:
        """Calculate beta"""
        if len(stock_returns) != len(market_returns):
            min_len = min(len(stock_returns), len(market_returns))
            stock_returns = stock_returns[:min_len]
            market_returns = market_returns[:min_len]

        covariance = np.cov(stock_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)

        return covariance / (market_variance + 1e-10)

    def _build_correlation_matrix(self, returns: Dict[str, np.ndarray]) -> Dict[str, Dict[str, float]]:
        """Build correlation matrix"""
        corr_matrix = {}

        for stock1, ret1 in returns.items():
            corr_matrix[stock1] = {}
            for stock2, ret2 in returns.items():
                if stock1 == stock2:
                    corr_matrix[stock1][stock2] = 1.0
                else:
                    min_len = min(len(ret1), len(ret2))
                    if min_len > 1:
                        corr = np.corrcoef(ret1[:min_len], ret2[:min_len])[0, 1]
                        corr_matrix[stock1][stock2] = corr
                    else:
                        corr_matrix[stock1][stock2] = 0.0

        return corr_matrix

    # ===== TAIL RISK =====

    def _calculate_skewness(self, returns: np.ndarray) -> float:
        """Return distribution skewness"""
        mean = np.mean(returns)
        std = np.std(returns)
        if std == 0:
            return 0.0
        return np.mean(((returns - mean) / std) ** 3)

    def _calculate_kurtosis(self, returns: np.ndarray) -> float:
        """Return distribution kurtosis (excess)"""
        mean = np.mean(returns)
        std = np.std(returns)
        if std == 0:
            return 0.0
        return np.mean(((returns - mean) / std) ** 4) - 3

    def _calculate_tail_ratio(self, returns: np.ndarray) -> float:
        """Tail ratio (positive to negative tail)"""
        positive_tail = np.percentile(returns, 95)
        negative_tail = abs(np.percentile(returns, 5))
        return positive_tail / (negative_tail + 1e-10)

    # ===== RISK-ADJUSTED RETURNS =====

    def _sharpe_ratio(self, returns: np.ndarray, risk_free_rate: float) -> float:
        """Sharpe ratio"""
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        return np.mean(excess_returns) / (np.std(returns) + 1e-10) * np.sqrt(252)

    def _sortino_ratio(self, returns: np.ndarray, risk_free_rate: float) -> float:
        """Sortino ratio (downside deviation)"""
        excess_returns = returns - (risk_free_rate / 252)
        downside_returns = returns[returns < 0]

        if len(downside_returns) == 0:
            return 0.0

        downside_std = np.std(downside_returns)
        return np.mean(excess_returns) / (downside_std + 1e-10) * np.sqrt(252)

    def _omega_ratio(self, returns: np.ndarray, risk_free_rate: float,
                    threshold: float = 0.0) -> float:
        """Omega ratio"""
        excess = returns - threshold
        gains = np.sum(excess[excess > 0])
        losses = -np.sum(excess[excess < 0])
        return gains / (losses + 1e-10)

    # ===== STRESS TESTS =====

    def _run_stress_tests(self, current_price: float, volatility: float) -> Dict[str, float]:
        """Run stress test scenarios"""
        scenarios = {
            'market_crash_10%': -0.10,
            'market_crash_20%': -0.20,
            'market_crash_30%': -0.30,
            'flash_crash': -0.15,
            '2x_volatility': -(2 * volatility),
            '3x_volatility': -(3 * volatility),
            'black_swan': -0.40
        }

        return {name: current_price * (1 + change) for name, change in scenarios.items()}

    def _run_portfolio_stress_tests(self, weights: Dict[str, float],
                                    volatilities: Dict[str, float],
                                    portfolio_value: float) -> Dict[str, float]:
        """Run portfolio stress tests"""
        scenarios = {}

        # Market crash scenarios
        for crash_pct in [0.10, 0.20, 0.30]:
            loss = portfolio_value * crash_pct
            scenarios[f'market_crash_{int(crash_pct*100)}%'] = -loss

        # Volatility spike
        avg_vol = np.mean(list(volatilities.values())) if volatilities else 0.3
        scenarios['volatility_spike_2x'] = -portfolio_value * (avg_vol * 2) / np.sqrt(252)
        scenarios['volatility_spike_3x'] = -portfolio_value * (avg_vol * 3) / np.sqrt(252)

        # Concentration risk (largest position fails)
        max_weight = max(weights.values()) if weights else 0
        scenarios['largest_position_fails'] = -portfolio_value * max_weight

        return scenarios

    # ===== DIVERSIFICATION =====

    def _calculate_diversification_ratio(self, weights: Dict[str, float],
                                        volatilities: Dict[str, float],
                                        correlation_matrix: Dict[str, Dict[str, float]]) -> float:
        """Diversification ratio"""
        # Weighted average of individual volatilities
        weighted_vol = sum(w * volatilities.get(stock, 0) for stock, w in weights.items())

        # Portfolio volatility
        portfolio_vol_sq = 0.0
        for stock1, w1 in weights.items():
            for stock2, w2 in weights.items():
                if stock1 in volatilities and stock2 in volatilities:
                    corr = correlation_matrix.get(stock1, {}).get(stock2, 0.0)
                    portfolio_vol_sq += w1 * w2 * volatilities[stock1] * volatilities[stock2] * corr

        portfolio_vol = np.sqrt(max(0, portfolio_vol_sq))

        return portfolio_vol / (weighted_vol + 1e-10)

    def _calculate_portfolio_returns(self, weights: Dict[str, float],
                                    stock_returns: Dict[str, np.ndarray]) -> np.ndarray:
        """Calculate portfolio returns time series"""
        # Find minimum length
        min_len = min(len(ret) for ret in stock_returns.values()) if stock_returns else 0

        if min_len == 0:
            return np.array([])

        portfolio_returns = np.zeros(min_len)

        for stock, weight in weights.items():
            if stock in stock_returns:
                portfolio_returns += weight * stock_returns[stock][:min_len]

        return portfolio_returns

    # ===== RISK SCORING =====

    def _calculate_risk_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall risk score (0-100)"""
        score = 0.0

        # Volatility (0-30 points)
        vol = metrics.get('volatility', 0.3)
        score += min(30, vol * 100)

        # Max drawdown (0-25 points)
        dd = abs(metrics.get('max_drawdown', 0.0))
        score += min(25, dd * 100)

        # VaR (0-20 points)
        var = abs(metrics.get('var_95', 0.0))
        score += min(20, var * 200)

        # CVaR (0-15 points)
        cvar = abs(metrics.get('cvar_95', 0.0))
        score += min(15, cvar * 150)

        # Tail risk - kurtosis (0-10 points)
        kurt = abs(metrics.get('kurtosis', 0.0))
        score += min(10, kurt * 2)

        return min(100, score)

    def _calculate_portfolio_risk_score(self, metrics: Dict[str, float]) -> float:
        """Calculate portfolio risk score"""
        score = 0.0

        # Concentration (0-30 points)
        herfindahl = metrics.get('concentration', 0.0)
        score += min(30, herfindahl * 150)

        # Max drawdown (0-30 points)
        dd = abs(metrics.get('max_drawdown', 0.0))
        score += min(30, dd * 100)

        # VaR (0-25 points)
        var = abs(metrics.get('var_95', 0.0))
        score += min(25, var * 250)

        # Lack of diversification (0-15 points)
        div_penalty = metrics.get('diversification', 0.0)
        score += min(15, div_penalty * 100)

        return min(100, score)

    def _generate_risk_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        """Generate risk recommendations"""
        recommendations = []

        # Concentration
        if metrics.get('max_weight', 0) > 0.3:
            recommendations.append("⚠️ 포지션 집중도 높음 - 분산 투자 권장")

        herfindahl = metrics.get('concentration', 0.0)
        if herfindahl > 0.25:
            recommendations.append("⚠️ 포트폴리오 집중도 높음 - 종목 수 확대 필요")

        # Diversification
        if metrics.get('diversification_ratio', 1.0) < 0.7:
            recommendations.append("✅ 우수한 분산 효과")
        elif metrics.get('diversification_ratio', 1.0) > 0.9:
            recommendations.append("⚠️ 분산 효과 미흡 - 상관관계 낮은 종목 추가")

        # Risk level
        risk_score = metrics.get('risk_score', 0)
        if risk_score > 70:
            recommendations.append("🚨 높은 리스크 - 포지션 축소 검토")
        elif risk_score < 30:
            recommendations.append("✅ 낮은 리스크 - 안정적 포트폴리오")

        # Drawdown
        max_dd = abs(metrics.get('max_drawdown', 0.0))
        if max_dd > 0.20:
            recommendations.append("⚠️ 큰 낙폭 경험 - 손절 전략 강화 필요")

        if not recommendations:
            recommendations.append("✅ 적정 리스크 수준")

        return recommendations

    # ===== EMPTY METRICS =====

    def _empty_risk_metrics(self, stock_code: str, stock_name: str) -> RiskMetrics:
        """Empty risk metrics"""
        return RiskMetrics(
            stock_code=stock_code,
            stock_name=stock_name,
            historical_volatility=0.0,
            parkinson_volatility=0.0,
            garman_klass_volatility=0.0,
            var_95=0.0,
            var_99=0.0,
            cvar_95=0.0,
            cvar_99=0.0,
            current_drawdown=0.0,
            max_drawdown=0.0,
            max_drawdown_duration_days=0,
            recovery_period_days=0,
            beta=1.0,
            correlation_with_market=0.0,
            systematic_risk=0.0,
            idiosyncratic_risk=0.0,
            skewness=0.0,
            kurtosis=0.0,
            tail_ratio=1.0,
            avg_daily_volume=0.0,
            volume_volatility=0.0,
            bid_ask_spread_proxy=0.0,
            position_size_risk=0.0,
            leverage_risk=0.0,
            concentration_risk=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            calmar_ratio=0.0,
            omega_ratio=0.0,
            stress_test_scenarios={},
            risk_score=0.0,
            risk_grade="UNKNOWN",
            calculated_at=datetime.now().isoformat()
        )

    def _empty_portfolio_metrics(self, portfolio_value: float) -> PortfolioRiskMetrics:
        """Empty portfolio metrics"""
        return PortfolioRiskMetrics(
            portfolio_value=portfolio_value,
            portfolio_var_95=0.0,
            portfolio_var_99=0.0,
            portfolio_cvar_95=0.0,
            diversification_ratio=1.0,
            correlation_matrix={},
            herfindahl_index=0.0,
            effective_stocks=0.0,
            max_position_weight=0.0,
            top_5_concentration=0.0,
            market_beta=1.0,
            sector_exposure={},
            current_drawdown=0.0,
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            stress_test_results={},
            risk_score=0.0,
            risk_capacity_utilization=0.0,
            recommendations=["No data available"],
            calculated_at=datetime.now().isoformat()
        )


# Global singleton
_risk_analyzer: Optional[RiskAnalyzer] = None


def get_risk_analyzer() -> RiskAnalyzer:
    """Get risk analyzer singleton"""
    global _risk_analyzer
    if _risk_analyzer is None:
        _risk_analyzer = RiskAnalyzer(risk_free_rate=0.03)
    return _risk_analyzer
