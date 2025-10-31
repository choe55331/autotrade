"""
Risk Analyzer with Visual Heatmap
Portfolio risk analysis with correlation matrix and visual heatmap

Features:
- Stock correlation analysis
- Sector risk analysis
- VaR (Value at Risk) calculation
- Beta calculation
- Risk heatmap data generation
- Stress testing
"""
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class StockRisk:
    """Risk metrics for a single stock"""
    code: str
    name: str
    beta: float  # Market beta
    volatility: float  # Historical volatility (%)
    var_1day: float  # 1-day VaR at 95% confidence (%)
    var_5day: float  # 5-day VaR at 95% confidence (%)
    max_drawdown: float  # Maximum drawdown (%)
    sharpe_ratio: float  # Sharpe ratio
    risk_level: str  # 'Low', 'Medium', 'High'


@dataclass
class CorrelationPair:
    """Correlation between two stocks"""
    code1: str
    name1: str
    code2: str
    name2: str
    correlation: float  # -1.0 to 1.0
    correlation_strength: str  # 'Strong', 'Moderate', 'Weak'


@dataclass
class SectorRisk:
    """Risk metrics for a sector"""
    sector: str
    position_count: int
    total_value: float
    weight: float  # % of portfolio
    avg_beta: float
    avg_volatility: float
    concentration_risk: str  # 'Low', 'Medium', 'High'


@dataclass
class PortfolioRisk:
    """Overall portfolio risk metrics"""
    total_value: float
    portfolio_beta: float
    portfolio_volatility: float
    portfolio_var_1day: float
    portfolio_var_5day: float
    max_correlation: float
    avg_correlation: float
    diversification_benefit: float  # 0-100%
    risk_score: float  # 0-100
    risk_level: str  # 'Conservative', 'Moderate', 'Aggressive'


@dataclass
class RiskAnalysis:
    """Complete risk analysis result"""
    timestamp: str
    portfolio_risk: PortfolioRisk
    stock_risks: List[StockRisk]
    sector_risks: List[SectorRisk]
    correlations: List[CorrelationPair]
    heatmap_data: Dict[str, Any]  # Data for correlation heatmap
    recommendations: List[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'timestamp': self.timestamp,
            'portfolio_risk': asdict(self.portfolio_risk),
            'stock_risks': [asdict(s) for s in self.stock_risks],
            'sector_risks': [asdict(s) for s in self.sector_risks],
            'correlations': [asdict(c) for c in self.correlations],
            'heatmap_data': self.heatmap_data,
            'recommendations': self.recommendations
        }


class RiskAnalyzer:
    """Portfolio risk analysis and correlation calculator"""

    def __init__(self, market_api=None):
        """
        Initialize risk analyzer

        Args:
            market_api: Market API instance for fetching historical data
        """
        self.market_api = market_api
        self.cache_file = Path('data/risk_cache.json')
        self.cache_ttl = 3600  # 1 hour
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

    def _generate_mock_returns(self, seed: int = None) -> np.ndarray:
        """
        Generate mock daily returns for testing

        Args:
            seed: Random seed for reproducibility

        Returns:
            Array of daily returns (30 days)
        """
        if seed is not None:
            np.random.seed(seed)

        # Generate 30 days of returns with some autocorrelation
        returns = np.random.normal(0.001, 0.02, 30)  # Mean 0.1%, StdDev 2%
        return returns

    def _calculate_beta(self, returns: np.ndarray, market_returns: np.ndarray) -> float:
        """
        Calculate stock beta vs market

        Args:
            returns: Stock returns
            market_returns: Market returns

        Returns:
            Beta value
        """
        try:
            covariance = np.cov(returns, market_returns)[0, 1]
            market_variance = np.var(market_returns)

            if market_variance == 0:
                return 1.0

            beta = covariance / market_variance
            return round(beta, 2)

        except Exception as e:
            logger.error(f"Error calculating beta: {e}")
            return 1.0

    def _calculate_volatility(self, returns: np.ndarray, annualize: bool = True) -> float:
        """
        Calculate historical volatility

        Args:
            returns: Daily returns
            annualize: Whether to annualize (multiply by sqrt(252))

        Returns:
            Volatility as percentage
        """
        vol = np.std(returns)
        if annualize:
            vol *= np.sqrt(252)  # Trading days per year
        return round(vol * 100, 2)

    def _calculate_var(self, returns: np.ndarray, confidence: float = 0.95, days: int = 1) -> float:
        """
        Calculate Value at Risk

        Args:
            returns: Daily returns
            confidence: Confidence level (e.g., 0.95 for 95%)
            days: Number of days

        Returns:
            VaR as percentage (positive number)
        """
        var = np.percentile(returns, (1 - confidence) * 100)
        if days > 1:
            var *= np.sqrt(days)
        return round(abs(var) * 100, 2)

    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """
        Calculate maximum drawdown

        Args:
            returns: Daily returns

        Returns:
            Max drawdown as percentage (positive number)
        """
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_dd = abs(np.min(drawdown))
        return round(max_dd * 100, 2)

    def _calculate_sharpe_ratio(self, returns: np.ndarray, risk_free_rate: float = 0.03) -> float:
        """
        Calculate Sharpe ratio

        Args:
            returns: Daily returns
            risk_free_rate: Annual risk-free rate

        Returns:
            Sharpe ratio
        """
        daily_rf = risk_free_rate / 252
        excess_returns = returns - daily_rf
        avg_excess = np.mean(excess_returns)
        std_excess = np.std(excess_returns)

        if std_excess == 0:
            return 0.0

        sharpe = (avg_excess / std_excess) * np.sqrt(252)
        return round(sharpe, 2)

    def _determine_risk_level(self, volatility: float, var: float, beta: float) -> str:
        """Determine risk level based on metrics"""
        risk_score = 0

        # Volatility component
        if volatility > 40:
            risk_score += 3
        elif volatility > 25:
            risk_score += 2
        else:
            risk_score += 1

        # VaR component
        if var > 5:
            risk_score += 3
        elif var > 3:
            risk_score += 2
        else:
            risk_score += 1

        # Beta component
        if abs(beta) > 1.5:
            risk_score += 2
        elif abs(beta) > 1.0:
            risk_score += 1

        if risk_score >= 7:
            return 'High'
        elif risk_score >= 4:
            return 'Medium'
        else:
            return 'Low'

    def _calculate_correlation(self, returns1: np.ndarray, returns2: np.ndarray) -> float:
        """Calculate correlation between two return series"""
        try:
            corr = np.corrcoef(returns1, returns2)[0, 1]
            return round(corr, 3)
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return 0.0

    def _classify_correlation(self, corr: float) -> str:
        """Classify correlation strength"""
        abs_corr = abs(corr)
        if abs_corr > 0.7:
            return 'Strong'
        elif abs_corr > 0.4:
            return 'Moderate'
        else:
            return 'Weak'

    def analyze_stock_risk(
        self,
        stock_code: str,
        stock_name: str,
        returns: Optional[np.ndarray] = None
    ) -> StockRisk:
        """
        Analyze risk for a single stock

        Args:
            stock_code: Stock code
            stock_name: Stock name
            returns: Optional daily returns array

        Returns:
            StockRisk object
        """
        # Use mock data if no returns provided
        if returns is None:
            seed = int(stock_code) % 1000 if stock_code.isdigit() else 42
            returns = self._generate_mock_returns(seed)

        # Generate mock market returns
        market_returns = self._generate_mock_returns(seed=1)

        # Calculate metrics
        beta = self._calculate_beta(returns, market_returns)
        volatility = self._calculate_volatility(returns)
        var_1day = self._calculate_var(returns, days=1)
        var_5day = self._calculate_var(returns, days=5)
        max_drawdown = self._calculate_max_drawdown(returns)
        sharpe_ratio = self._calculate_sharpe_ratio(returns)
        risk_level = self._determine_risk_level(volatility, var_1day, beta)

        return StockRisk(
            code=stock_code,
            name=stock_name,
            beta=beta,
            volatility=volatility,
            var_1day=var_1day,
            var_5day=var_5day,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            risk_level=risk_level
        )

    def calculate_correlation_matrix(
        self,
        positions: List[Dict[str, Any]]
    ) -> Tuple[pd.DataFrame, List[CorrelationPair]]:
        """
        Calculate correlation matrix for portfolio positions

        Args:
            positions: List of position dictionaries with code and name

        Returns:
            (DataFrame with correlation matrix, List of CorrelationPair objects)
        """
        if len(positions) < 2:
            return pd.DataFrame(), []

        # Generate mock returns for each stock
        returns_data = {}
        for pos in positions:
            code = pos['code']
            seed = int(code) % 1000 if code.isdigit() else hash(code) % 1000
            returns_data[code] = self._generate_mock_returns(seed)

        # Create DataFrame
        df = pd.DataFrame(returns_data)

        # Calculate correlation matrix
        corr_matrix = df.corr()

        # Extract correlation pairs
        pairs = []
        codes = list(returns_data.keys())
        for i in range(len(codes)):
            for j in range(i + 1, len(codes)):
                code1, code2 = codes[i], codes[j]
                corr = corr_matrix.loc[code1, code2]

                # Find names
                name1 = next((p['name'] for p in positions if p['code'] == code1), code1)
                name2 = next((p['name'] for p in positions if p['code'] == code2), code2)

                pairs.append(CorrelationPair(
                    code1=code1,
                    name1=name1,
                    code2=code2,
                    name2=name2,
                    correlation=round(corr, 3),
                    correlation_strength=self._classify_correlation(corr)
                ))

        # Sort by absolute correlation descending
        pairs.sort(key=lambda x: abs(x.correlation), reverse=True)

        return corr_matrix, pairs

    def analyze_portfolio_risk(
        self,
        positions: List[Dict[str, Any]]
    ) -> Optional[RiskAnalysis]:
        """
        Complete portfolio risk analysis

        Args:
            positions: List of position dicts with:
                - code, name, value, weight, sector

        Returns:
            RiskAnalysis object with complete analysis
        """
        try:
            if not positions:
                logger.warning("No positions to analyze")
                return None

            total_value = sum(p['value'] for p in positions)

            # 1. Analyze individual stock risks
            stock_risks = []
            stock_returns = {}

            for pos in positions:
                code = pos['code']
                seed = int(code) % 1000 if code.isdigit() else hash(code) % 1000
                returns = self._generate_mock_returns(seed)
                stock_returns[code] = returns

                risk = self.analyze_stock_risk(code, pos['name'], returns)
                stock_risks.append(risk)

            # 2. Calculate correlations
            corr_matrix, correlations = self.calculate_correlation_matrix(positions)

            # 3. Calculate portfolio-level metrics
            weights = np.array([p['weight'] / 100.0 for p in positions])

            # Portfolio beta (weighted average)
            betas = np.array([r.beta for r in stock_risks])
            portfolio_beta = round(np.dot(weights, betas), 2)

            # Portfolio volatility (considering correlations)
            volatilities = np.array([r.volatility / 100.0 for r in stock_risks])
            if len(corr_matrix) > 0:
                portfolio_variance = np.dot(weights, np.dot(corr_matrix.values, weights * volatilities**2))
                portfolio_vol = round(np.sqrt(portfolio_variance) * 100, 2)
            else:
                portfolio_vol = round(np.dot(weights, volatilities) * 100, 2)

            # Portfolio VaR (simplified weighted average)
            vars_1day = np.array([r.var_1day for r in stock_risks])
            portfolio_var_1day = round(np.dot(weights, vars_1day), 2)

            vars_5day = np.array([r.var_5day for r in stock_risks])
            portfolio_var_5day = round(np.dot(weights, vars_5day), 2)

            # Correlation metrics
            if correlations:
                max_corr = max(abs(c.correlation) for c in correlations)
                avg_corr = sum(c.correlation for c in correlations) / len(correlations)
            else:
                max_corr = 0.0
                avg_corr = 0.0

            # Diversification benefit (lower correlation = higher benefit)
            diversification_benefit = round(max(0, (1 - avg_corr) * 100), 1)

            # Overall risk score
            risk_score = (portfolio_beta * 20) + (portfolio_vol * 1.5) + (max_corr * 30)
            risk_score = min(100, max(0, risk_score))

            if risk_score > 70:
                risk_level = 'Aggressive'
            elif risk_score > 40:
                risk_level = 'Moderate'
            else:
                risk_level = 'Conservative'

            portfolio_risk = PortfolioRisk(
                total_value=total_value,
                portfolio_beta=portfolio_beta,
                portfolio_volatility=portfolio_vol,
                portfolio_var_1day=portfolio_var_1day,
                portfolio_var_5day=portfolio_var_5day,
                max_correlation=round(max_corr, 3),
                avg_correlation=round(avg_corr, 3),
                diversification_benefit=diversification_benefit,
                risk_score=round(risk_score, 1),
                risk_level=risk_level
            )

            # 4. Analyze sector risks
            sector_data: Dict[str, Dict] = {}
            for pos in positions:
                sector = pos.get('sector', '기타')
                if sector not in sector_data:
                    sector_data[sector] = {
                        'count': 0,
                        'value': 0,
                        'betas': [],
                        'volatilities': []
                    }

                sector_data[sector]['count'] += 1
                sector_data[sector]['value'] += pos['value']

                # Find stock risk
                risk = next((r for r in stock_risks if r.code == pos['code']), None)
                if risk:
                    sector_data[sector]['betas'].append(risk.beta)
                    sector_data[sector]['volatilities'].append(risk.volatility)

            sector_risks = []
            for sector, data in sector_data.items():
                weight = (data['value'] / total_value * 100) if total_value > 0 else 0

                avg_beta = np.mean(data['betas']) if data['betas'] else 1.0
                avg_vol = np.mean(data['volatilities']) if data['volatilities'] else 0.0

                # Concentration risk
                if weight > 50:
                    conc_risk = 'High'
                elif weight > 30:
                    conc_risk = 'Medium'
                else:
                    conc_risk = 'Low'

                sector_risks.append(SectorRisk(
                    sector=sector,
                    position_count=data['count'],
                    total_value=data['value'],
                    weight=round(weight, 1),
                    avg_beta=round(avg_beta, 2),
                    avg_volatility=round(avg_vol, 2),
                    concentration_risk=conc_risk
                ))

            sector_risks.sort(key=lambda x: x.weight, reverse=True)

            # 5. Generate heatmap data
            heatmap_data = self._generate_heatmap_data(positions, corr_matrix)

            # 6. Generate recommendations
            recommendations = self._generate_risk_recommendations(
                portfolio_risk, stock_risks, sector_risks, correlations
            )

            return RiskAnalysis(
                timestamp=datetime.now().isoformat(),
                portfolio_risk=portfolio_risk,
                stock_risks=stock_risks,
                sector_risks=sector_risks,
                correlations=correlations[:10],  # Top 10 correlations
                heatmap_data=heatmap_data,
                recommendations=recommendations
            )

        except Exception as e:
            logger.error(f"Error analyzing portfolio risk: {e}")
            return None

    def _generate_heatmap_data(
        self,
        positions: List[Dict],
        corr_matrix: pd.DataFrame
    ) -> Dict[str, Any]:
        """Generate data for correlation heatmap visualization"""
        if len(corr_matrix) == 0:
            return {'labels': [], 'data': []}

        labels = [pos['name'] for pos in positions]
        data = corr_matrix.values.tolist()

        return {
            'labels': labels,
            'data': data,
            'min': -1.0,
            'max': 1.0
        }

    def _generate_risk_recommendations(
        self,
        portfolio_risk: PortfolioRisk,
        stock_risks: List[StockRisk],
        sector_risks: List[SectorRisk],
        correlations: List[CorrelationPair]
    ) -> List[str]:
        """Generate risk-based recommendations"""
        recommendations = []

        # 1. High portfolio risk
        if portfolio_risk.risk_score > 70:
            recommendations.append(
                f"⚠️ 포트폴리오 리스크가 높습니다 (점수: {portfolio_risk.risk_score:.0f}/100). "
                "변동성이 큰 종목의 비중을 줄이는 것을 고려하세요."
            )

        # 2. High correlation
        if portfolio_risk.max_correlation > 0.8:
            recommendations.append(
                f"📊 일부 종목 간 상관관계가 매우 높습니다 ({portfolio_risk.max_correlation:.2f}). "
                "분산 효과가 제한적일 수 있습니다."
            )

        # 3. High beta
        if portfolio_risk.portfolio_beta > 1.3:
            recommendations.append(
                f"📈 포트폴리오 베타가 높습니다 ({portfolio_risk.portfolio_beta:.2f}). "
                "시장 변동에 민감하게 반응할 수 있습니다."
            )

        # 4. High VaR
        if portfolio_risk.portfolio_var_1day > 4:
            recommendations.append(
                f"💰 1일 VaR이 {portfolio_risk.portfolio_var_1day:.1f}%입니다. "
                "단기 손실 위험이 있으니 주의하세요."
            )

        # 5. Individual stock risks
        high_risk_stocks = [s for s in stock_risks if s.risk_level == 'High']
        if high_risk_stocks:
            stock_names = ', '.join([s.name for s in high_risk_stocks[:3]])
            recommendations.append(
                f"⚡ 고위험 종목: {stock_names}. 변동성이 크니 주의가 필요합니다."
            )

        # 6. Sector concentration
        high_conc_sectors = [s for s in sector_risks if s.concentration_risk == 'High']
        if high_conc_sectors:
            sector_names = ', '.join([s.sector for s in high_conc_sectors])
            recommendations.append(
                f"🏢 섹터 집중 위험: {sector_names}. 다른 섹터로 분산을 고려하세요."
            )

        # 7. Good diversification
        if portfolio_risk.diversification_benefit > 60:
            recommendations.append(
                f"✅ 우수한 분산 투자 ({portfolio_risk.diversification_benefit:.0f}% 분산 효과). "
                "현재 구성을 유지하세요."
            )

        return recommendations

    def get_risk_analysis_for_dashboard(
        self,
        positions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get risk analysis formatted for dashboard

        Returns:
            Dictionary ready for JSON API response
        """
        try:
            analysis = self.analyze_portfolio_risk(positions)

            if not analysis:
                return {
                    'success': False,
                    'message': 'No positions to analyze'
                }

            return {
                'success': True,
                'data': analysis.to_dict()
            }

        except Exception as e:
            logger.error(f"Error getting dashboard risk analysis: {e}")
            return {
                'success': False,
                'message': str(e)
            }


# Example usage
if __name__ == '__main__':
    # Test with sample positions
    sample_positions = [
        {'code': '005930', 'name': '삼성전자', 'value': 7350000, 'weight': 32.0, 'sector': '반도체'},
        {'code': '000660', 'name': 'SK하이닉스', 'value': 6500000, 'weight': 28.3, 'sector': '반도체'},
        {'code': '035720', 'name': '카카오', 'value': 9100000, 'weight': 39.7, 'sector': '인터넷/게임'},
    ]

    analyzer = RiskAnalyzer()
    analysis = analyzer.analyze_portfolio_risk(sample_positions)

    if analysis:
        print("\n포트폴리오 리스크 분석")
        print("=" * 60)
        print(f"리스크 점수: {analysis.portfolio_risk.risk_score:.1f}/100")
        print(f"리스크 수준: {analysis.portfolio_risk.risk_level}")
        print(f"포트폴리오 베타: {analysis.portfolio_risk.portfolio_beta}")
        print(f"포트폴리오 변동성: {analysis.portfolio_risk.portfolio_volatility}%")
        print(f"1일 VaR (95%): {analysis.portfolio_risk.portfolio_var_1day}%")
        print(f"분산 효과: {analysis.portfolio_risk.diversification_benefit:.0f}%")
        print(f"\n리스크 권장사항: {len(analysis.recommendations)}개")
        for rec in analysis.recommendations:
            print(f"  - {rec}")
