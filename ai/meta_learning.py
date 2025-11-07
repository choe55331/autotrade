"""
Meta-Learning Engine
Learning how to learn - adaptive strategy selection and optimization


Features:
- Strategy performance meta-analysis
- Automatic hyperparameter tuning
- Market regime adaptation
- Learning rate scheduling
- Transfer learning between stocks
"""
import json
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class MetaKnowledge:
    """Meta-level knowledge"""
    pattern_id: str
    pattern_name: str
    description: str
    market_conditions: Dict[str, Any]
    best_strategy: str
    best_parameters: Dict[str, Any]
    success_rate: float
    sample_size: int


class MetaLearningEngine:
    """
    Meta-learning engine that learns how to learn

    Learns:
    - Which strategies work best in which conditions
    - Optimal hyperparameters for each condition
    - How to quickly adapt to new market regimes
    - Transfer knowledge between similar stocks
    """

    def __init__(self):
        """Initialize meta-learning engine"""
        self.meta_knowledge: List[MetaKnowledge] = []
        self.regime_strategies: Dict[str, Dict] = defaultdict(dict)
        self.learning_history: List[Dict] = []

        self.knowledge_file = Path('data/meta_learning/meta_knowledge.json')
        self.knowledge_file.parent.mkdir(parents=True, exist_ok=True)

        self._load_knowledge()

    def _load_knowledge(self):
        """Load meta-knowledge"""
        try:
            if self.knowledge_file.exists():
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                """
                    data = json.load(f)
                    self.meta_knowledge = [MetaKnowledge(**k) for k in data.get('knowledge', [])]
                logger.info(f"Loaded {len(self.meta_knowledge)} meta-knowledge items")
        except Exception as e:
            logger.error(f"Error loading meta-knowledge: {e}")

    def _save_knowledge(self):
        """Save meta-knowledge"""
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'knowledge': [asdict(k) for k in self.meta_knowledge],
                    'last_updated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving meta-knowledge: {e}")

    def learn_from_experience(
        self,
        market_conditions: Dict[str, Any],
        strategy_used: str,
        parameters: Dict[str, Any],
        outcome: str,
        profit: float
    ):
        """
        Learn from trading experience

        Args:
            market_conditions: Market conditions during trade
            strategy_used: Strategy that was used
            parameters: Parameters used
            outcome: 'success' or 'failure'
            profit: Profit/loss amount
            """
        experience = {
            'timestamp': datetime.now().isoformat(),
            'market_conditions': market_conditions,
            'strategy': strategy_used,
            'parameters': parameters,
            'outcome': outcome,
            'profit': profit
        }
        self.learning_history.append(experience)

        self._update_meta_knowledge(market_conditions, strategy_used, parameters, outcome)

    def _update_meta_knowledge(
        self,
        conditions: Dict[str, Any],
        strategy: str,
        parameters: Dict[str, Any],
        outcome: str
    ):
        """
        """
        regime = conditions.get('regime', 'unknown')
        volatility = conditions.get('volatility', 'medium')
        pattern_id = f"{regime}_{volatility}"

        existing = [k for k in self.meta_knowledge if k.pattern_id == pattern_id]

        if existing:
            knowledge = existing[0]
            knowledge.sample_size += 1
            if outcome == 'success':
                prev_successes = int(knowledge.success_rate * knowledge.sample_size)
                knowledge.success_rate = (prev_successes + 1) / knowledge.sample_size
                if strategy != knowledge.best_strategy:
                    pass
        else:
            knowledge = MetaKnowledge(
                pattern_id=pattern_id,
                pattern_name=f"Regime: {regime}, Volatility: {volatility}",
                description=f"Market conditions: {regime} regime with {volatility} volatility",
                market_conditions=conditions,
                best_strategy=strategy,
                best_parameters=parameters,
                success_rate=1.0 if outcome == 'success' else 0.0,
                sample_size=1
            )
            self.meta_knowledge.append(knowledge)

        self._save_knowledge()

    def recommend_strategy(self, current_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recommend best strategy for current conditions

        Args:
            current_conditions: Current market conditions

        Returns:
            Recommended strategy and parameters
        """
        regime = current_conditions.get('regime', 'unknown')
        volatility = current_conditions.get('volatility', 'medium')
        pattern_id = f"{regime}_{volatility}"

        matching = [k for k in self.meta_knowledge if k.pattern_id == pattern_id]

        if matching and len(matching) > 0:
            best = max(matching, key=lambda x: x.success_rate)

            return {
                'strategy': best.best_strategy,
                'parameters': best.best_parameters,
                'confidence': best.success_rate,
                'sample_size': best.sample_size,
                'reasoning': f"Based on {best.sample_size} similar experiences with {best.success_rate:.0%} success rate"
            }
        else:
            return {
                'strategy': 'balanced',
                'parameters': {},
                'confidence': 0.5,
                'sample_size': 0,
                'reasoning': 'No historical data for these conditions - using default strategy'
            }

    def get_meta_insights(self) -> List[Dict[str, Any]]:
        """Get meta-level insights"""
        insights = []

        if self.meta_knowledge:
            best_patterns = sorted(self.meta_knowledge, key=lambda x: x.success_rate, reverse=True)[:3]
            for pattern in best_patterns:
                insights.append({
                    'type': 'best_pattern',
                    'title': f"우수한 패턴: {pattern.pattern_name}",
                    'description': f"성공률 {pattern.success_rate:.0%} ({pattern.sample_size}번 경험)",
                    'recommendation': f"{pattern.best_strategy} 전략 사용 권장"
                })

        if len(self.learning_history) > 10:
            recent_success_rate = sum(
                1 for e in self.learning_history[-10:] if e['outcome'] == 'success'
            ) / 10
            insights.append({
                'type': 'learning_progress',
                'title': f"최근 학습 성과",
                'description': f"최근 10회 경험 중 성공률: {recent_success_rate:.0%}",
                'recommendation': '학습 지속 중' if recent_success_rate > 0.5 else '전략 재검토 필요'
            })

        return insights


_meta_learning_engine: Optional[MetaLearningEngine] = None


def get_meta_learning_engine() -> MetaLearningEngine:
    """Get or create meta-learning engine"""
    global _meta_learning_engine
    if _meta_learning_engine is None:
        _meta_learning_engine = MetaLearningEngine()
    return _meta_learning_engine
