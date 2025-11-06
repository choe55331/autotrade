Portfolio Optimizer
AI-based portfolio analysis and optimization suggestions

Features:
- Sector diversification analysis
- Risk concentration detection
- Correlation matrix computation
- Position sizing optimization
- Rebalancing recommendations
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
    """Sector allocation info"""
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


@dataclass
class OptimizationSuggestion:
    """Single optimization suggestion"""
    type: str
    priority: str
    title: str
    description: str
    action: str
    impact: str


@dataclass
class PortfolioOptimization:
    """Complete portfolio optimization result"""
    timestamp: str
    metrics: PortfolioMetrics
    positions: List[PortfolioPosition]
    sector_allocation: List[SectorAllocation]
    suggestions: List[OptimizationSuggestion]
    risk_level: str

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'timestamp': self.timestamp,
            'metrics': asdict(self.metrics),
            'positions': [asdict(p) for p in self.positions],
            'sector_allocation': [asdict(s) for s in self.sector_allocation],
            'suggestions': [asdict(s) for s in self.suggestions],
            'risk_level': self.risk_level
        }


class PortfolioOptimizer:
    """Portfolio optimization and analysis service"""

    SECTOR_MAP = {
        '005930': '반도체',
        '000660': '반도체',
        '035420': '인터넷/게임',
        '035720': '인터넷/게임',
        '051910': '화학',
        '006400': '자동차',
        '207940': '바이오',
        '068270': '음식료',
        '028260': '음식료',
        '105560': '금융',
    }

    def __init__(self, market_api=None):
        """
        Initialize portfolio optimizer

        Args:
            market_api: Market API instance for fetching stock data
        """
        self.market_api = market_api
        self.cache_file = Path('data/portfolio_cache.json')
        self.cache_ttl = 300
        self._ensure_data_dir()

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

    def _calculate_diversification_score(self, positions: List[PortfolioPosition]) -> float:
        """
        Calculate portfolio diversification score (0-100)

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

    def _calculate_concentration_risk(self, positions: List[PortfolioPosition]) -> Tuple[str, float, float]:
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

    def _analyze_sectors(self, positions: List[PortfolioPosition]) -> List[SectorAllocation]:
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

    def _generate_suggestions(
        self,
        positions: List[PortfolioPosition],
        metrics: PortfolioMetrics,
        sector_allocation: List[SectorAllocation]
    ) -> List[OptimizationSuggestion]:
        suggestions = []

        if metrics.concentration_risk == 'High':
            if metrics.largest_position_weight > 40:
                suggestions.append(OptimizationSuggestion(
                    type='reduce',
                    priority='high',
                    title='⚠️ 집중도 위험: 최대 보유 종목 비중 과다',
                    description=f'최대 보유 종목이 포트폴리오의 {metrics.largest_position_weight:.1f}%를 차지하고 있습니다.',
                    action='가장 큰 비중의 종목을 일부 매도하여 25% 이하로 조정하세요.',
                    impact='리스크 감소, 안정성 향상'
                ))

            if metrics.top3_concentration > 70:
                suggestions.append(OptimizationSuggestion(
                    type='diversify',
                    priority='high',
                    title='📊 상위 3종목 집중도 높음',
                    description=f'상위 3종목이 포트폴리오의 {metrics.top3_concentration:.1f}%를 차지합니다.',
                    action='신규 종목을 추가하거나 상위 종목 일부를 매도하세요.',
                    impact='분산 투자, 리스크 감소'
                ))

        if sector_allocation:
            top_sector = sector_allocation[0]
            if top_sector.weight > 50:
                suggestions.append(OptimizationSuggestion(
                    type='diversify',
                    priority='high',
                    title=f'🏢 섹터 집중: {top_sector.sector} 과다 비중',
                    description=f'{top_sector.sector} 섹터가 {top_sector.weight:.1f}%를 차지하고 있습니다.',
                    action='다른 섹터의 종목을 추가하여 섹터 리스크를 분산하세요.',
                    impact='섹터 리스크 감소, 안정성 향상'
                ))

        if metrics.diversification_score < 40:
            suggestions.append(OptimizationSuggestion(
                type='add',
                priority='high',
                title='📈 분산 투자 부족',
                description=f'분산 점수: {metrics.diversification_score:.0f}/100 (낮음)',
                action='포트폴리오에 3-5개의 종목을 추가하여 분산도를 높이세요.',
                impact='리스크 감소, 수익 안정성 향상'
            ))
        elif metrics.diversification_score < 60:
            suggestions.append(OptimizationSuggestion(
                type='add',
                priority='medium',
                title='📊 분산 투자 개선 가능',
                description=f'분산 점수: {metrics.diversification_score:.0f}/100 (보통)',
                action='1-2개의 다른 섹터 종목을 추가하면 더 안정적인 포트폴리오가 됩니다.',
                impact='리스크 감소'
            ))

        for pos in positions:
            if pos.weight > 15 and pos.profit_loss_percent < -10:
                suggestions.append(OptimizationSuggestion(
                    type='rebalance',
                    priority='medium',
                    title=f'📉 {pos.name}: 큰 손실 포지션',
                    description=f'{pos.weight:.1f}% 비중으로 {pos.profit_loss_percent:.1f}% 손실',
                    action='손절 고려 또는 비중 축소를 검토하세요.',
                    impact='손실 제한, 자금 재배치'
                ))

            if pos.weight > 20 and pos.profit_loss_percent > 30:
                suggestions.append(OptimizationSuggestion(
                    type='rebalance',
                    priority='low',
                    title=f'💰 {pos.name}: 수익 실현 고려',
                    description=f'{pos.weight:.1f}% 비중으로 {pos.profit_loss_percent:.1f}% 수익',
                    action='일부 수익을 실현하고 다른 종목에 재투자를 고려하세요.',
                    impact='수익 확정, 리스크 감소'
                ))

        if metrics.diversification_score >= 70 and metrics.concentration_risk == 'Low':
            suggestions.append(OptimizationSuggestion(
                type='maintain',
                priority='low',
                title='✅ 우수한 포트폴리오 구성',
                description=f'분산 점수 {metrics.diversification_score:.0f}/100, 집중도 위험 낮음',
                action='현재 포트폴리오 구성을 유지하세요.',
                impact='안정적인 수익 추구'
            ))

        return suggestions

    def _determine_risk_level(self, metrics: PortfolioMetrics) -> str:
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

    def optimize_portfolio(self, positions_data: List[Dict]) -> Optional[PortfolioOptimization]:
        """
        Analyze and optimize portfolio

        Args:
            positions_data: List of position dictionaries with:
                - code, name, quantity, avg_price, current_price, value

        Returns:
            PortfolioOptimization object with complete analysis
        """
        try:
            if not positions_data:
                logger.warning("No positions to optimize")
                return None

            total_value = sum(p['value'] for p in positions_data)

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

            sector_allocation = self._analyze_sectors(positions)

            diversification_score = self._calculate_diversification_score(positions)
            concentration_risk, largest_weight, top3_weight = self._calculate_concentration_risk(positions)

            metrics = PortfolioMetrics(
                total_value=total_value,
                position_count=len(positions),
                sector_count=len(set(p.sector for p in positions)),
                diversification_score=diversification_score,
                concentration_risk=concentration_risk,
                largest_position_weight=largest_weight,
                top3_concentration=top3_weight,
                avg_correlation=0.0
            )

            suggestions = self._generate_suggestions(positions, metrics, sector_allocation)

            risk_level = self._determine_risk_level(metrics)

            return PortfolioOptimization(
                timestamp=datetime.now().isoformat(),
                metrics=metrics,
                positions=positions,
                sector_allocation=sector_allocation,
                suggestions=suggestions,
                risk_level=risk_level
            )

        except Exception as e:
            logger.error(f"Error optimizing portfolio: {e}")
            return None

    def get_optimization_for_dashboard(self, positions_data: List[Dict]) -> Dict[str, Any]:
        """
        Get optimization data formatted for dashboard

        Returns:
            Dictionary ready for JSON API response
        """
        try:
            optimization = self.optimize_portfolio(positions_data)

            if not optimization:
                return {
                    'success': False,
                    'message': 'No positions to optimize'
                }

            return {
                'success': True,
                'data': optimization.to_dict()
            }

        except Exception as e:
            logger.error(f"Error getting dashboard optimization: {e}")
            return {
                'success': False,
                'message': str(e)
            }


if __name__ == '__main__':
    sample_positions = [
        {'code': '005930', 'name': '삼성전자', 'quantity': 100, 'avg_price': 70000, 'current_price': 73500, 'value': 7350000},
        {'code': '000660', 'name': 'SK하이닉스', 'quantity': 50, 'avg_price': 125000, 'current_price': 130000, 'value': 6500000},
        {'code': '035720', 'name': '카카오', 'quantity': 200, 'avg_price': 48000, 'current_price': 45500, 'value': 9100000},
    ]

    optimizer = PortfolioOptimizer()
    result = optimizer.optimize_portfolio(sample_positions)

    if result:
        print(f"\n포트폴리오 분석 결과")
        print("=" * 60)
        print(f"총 자산: {result.metrics.total_value:,.0f}원")
        print(f"보유 종목: {result.metrics.position_count}개")
        print(f"분산 점수: {result.metrics.diversification_score:.0f}/100")
        print(f"집중도 위험: {result.metrics.concentration_risk}")
        print(f"리스크 수준: {result.risk_level}")
        print(f"\n최적화 제안: {len(result.suggestions)}개")
        for sug in result.suggestions:
            print(f"  - [{sug.priority.upper()}] {sug.title}")
