Trading Journal with AI Analysis
Automatic trade recording and intelligent analysis

Features:
- Automatic trade recording
- AI-powered trade analysis
- Pattern recognition in mistakes
- Performance insights
- Improvement suggestions
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class JournalEntry:
    """Single journal entry"""
    id: str
    timestamp: str
    trade_type: str
    stock_code: str
    stock_name: str
    quantity: int
    price: float
    total_amount: float

    entry_reason: str
    strategy_used: str
    confidence_level: float
    market_condition: str

    exit_reason: Optional[str] = None
    holding_period: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_pct: Optional[float] = None

    was_successful: bool = False
    ai_analysis: Optional[str] = None
    lessons_learned: List[str] = None
    mistakes: List[str] = None
    tags: List[str] = None

    emotional_state: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class TradingPattern:
    """Recurring trading pattern"""
    pattern_id: str
    pattern_name: str
    description: str
    occurrences: int
    success_rate: float
    avg_profit: float
    examples: List[str]


@dataclass
class JournalInsight:
    """AI-generated insight from journal"""
    timestamp: str
    insight_type: str
    title: str
    description: str
    supporting_data: List[str]
    recommendation: str
    priority: str


class TradingJournal:
    """
    Intelligent trading journal with AI analysis

    Automatically records all trades and provides insights
    """

    def __init__(self, ai_learning_engine=None):
        """
        Initialize trading journal

        Args:
            ai_learning_engine: AI learning engine for advanced analysis
        """
        self.ai_engine = ai_learning_engine

        self.entries: List[JournalEntry] = []
        self.patterns: List[TradingPattern] = []
        self.insights: List[JournalInsight] = []

        self.journal_file = Path('data/trading_journal.json')
        self.patterns_file = Path('data/journal_patterns.json')
        self.insights_file = Path('data/journal_insights.json')

        self._ensure_data_files()
        self._load_journal()

    def _ensure_data_files(self):
        """Ensure data files exist"""
        for file in [self.journal_file, self.patterns_file, self.insights_file]:
            file.parent.mkdir(parents=True, exist_ok=True)
            if not file.exists():
                file.write_text('{"entries": []}')

    def _load_journal(self):
        """Load journal from file"""
        try:
            if self.journal_file.exists():
                with open(self.journal_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entries = [JournalEntry(**e) for e in data.get('entries', [])]
                logger.info(f"Loaded {len(self.entries)} journal entries")

            if self.patterns_file.exists():
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.patterns = [TradingPattern(**p) for p in data.get('patterns', [])]

            if self.insights_file.exists():
                with open(self.insights_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.insights = [JournalInsight(**i) for i in data.get('insights', [])]

        except Exception as e:
            logger.error(f"Error loading journal: {e}")

    def _save_journal(self):
        """Save journal to file"""
        try:
            with open(self.journal_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'entries': [asdict(e) for e in self.entries[-1000:]],
                    'last_updated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)

            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'patterns': [asdict(p) for p in self.patterns],
                    'last_updated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)

            with open(self.insights_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'insights': [asdict(i) for i in self.insights[-50:]],
                    'last_updated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Error saving journal: {e}")

    def record_trade(
        self,
        trade_type: str,
        stock_code: str,
        stock_name: str,
        quantity: int,
        price: float,
        strategy: str,
        reason: str,
        confidence: float = 0.5,
        market_condition: str = 'unknown',
        emotional_state: str = None,
        notes: str = None
    ) -> JournalEntry:
        Record a trade in the journal

        Args:
            trade_type: 'buy' or 'sell'
            stock_code: Stock code
            stock_name: Stock name
            quantity: Number of shares
            price: Price per share
            strategy: Strategy used
            reason: Reason for trade
            confidence: Confidence level (0-1)
            market_condition: Current market condition
            emotional_state: Trader's emotional state
            notes: Additional notes

        Returns:
            Journal entry
        entry_id = f"{trade_type}_{stock_code}_{int(datetime.now().timestamp())}"

        entry = JournalEntry(
            id=entry_id,
            timestamp=datetime.now().isoformat(),
            trade_type=trade_type,
            stock_code=stock_code,
            stock_name=stock_name,
            quantity=quantity,
            price=price,
            total_amount=price * quantity,
            entry_reason=reason,
            strategy_used=strategy,
            confidence_level=confidence,
            market_condition=market_condition,
            emotional_state=emotional_state,
            notes=notes,
            tags=self._auto_tag(trade_type, reason, confidence)
        )

        if trade_type == 'sell':
            self._complete_trade_cycle(entry, stock_code)

        self.entries.append(entry)
        self._save_journal()

        logger.info(f"Journal: Recorded {trade_type} of {stock_name}")

        if len(self.entries) % 10 == 0:
            self._analyze_patterns()

        return entry

    def _auto_tag(self, trade_type: str, reason: str, confidence: float) -> List[str]:
        """Automatically generate tags for entry"""
        tags = []

        tags.append(trade_type)

        if confidence > 0.8:
            tags.append('high_confidence')
        elif confidence < 0.5:
            tags.append('low_confidence')

        reason_lower = reason.lower()
        if 'rsi' in reason_lower:
            tags.append('rsi_signal')
        if '거래량' in reason_lower or 'volume' in reason_lower:
            tags.append('volume_signal')
        if 'ai' in reason_lower:
            tags.append('ai_decision')
        if '손절' in reason_lower or 'stop' in reason_lower:
            tags.append('stop_loss')
        if '익절' in reason_lower or 'profit' in reason_lower:
            tags.append('take_profit')

        return tags

    def _complete_trade_cycle(self, sell_entry: JournalEntry, stock_code: str):
        """Complete a trade cycle by matching sell with buy"""
        buy_entries = [e for e in self.entries
                      if e.trade_type == 'buy' and
                      e.stock_code == stock_code and
                      e.exit_reason is None]

        if not buy_entries:
            return

        buy_entry = buy_entries[-1]

        buy_time = datetime.fromisoformat(buy_entry.timestamp)
        sell_time = datetime.fromisoformat(sell_entry.timestamp)
        holding_period = (sell_time - buy_time).total_seconds() / 3600

        profit_loss = (sell_entry.price - buy_entry.price) * buy_entry.quantity
        profit_loss_pct = ((sell_entry.price - buy_entry.price) / buy_entry.price) * 100

        buy_entry.exit_reason = sell_entry.entry_reason
        buy_entry.holding_period = holding_period
        buy_entry.profit_loss = profit_loss
        buy_entry.profit_loss_pct = profit_loss_pct
        buy_entry.was_successful = profit_loss > 0

        sell_entry.holding_period = holding_period
        sell_entry.profit_loss = profit_loss
        sell_entry.profit_loss_pct = profit_loss_pct
        sell_entry.was_successful = profit_loss > 0

        self._ai_analyze_trade(buy_entry, sell_entry)

    def _ai_analyze_trade(self, buy_entry: JournalEntry, sell_entry: JournalEntry):
        """AI analyzes completed trade"""
        analysis = []
        lessons = []
        mistakes = []

        if buy_entry.was_successful:
            analysis.append("✅ 수익 거래")

            if buy_entry.profit_loss_pct > 5:
                lessons.append("강한 수익 실현 - 진입 타이밍 우수")

            if buy_entry.holding_period < 24:
                lessons.append("단기 수익 - 빠른 진입/탈출")

            if buy_entry.confidence_level > 0.7:
                lessons.append("높은 신뢰도 결정이 성공으로 이어짐")
        else:
            analysis.append("❌ 손실 거래")

            if buy_entry.profit_loss_pct < -3:
                mistakes.append("큰 손실 - 진입 타이밍 개선 필요")

            if 'stop_loss' not in buy_entry.tags:
                mistakes.append("손절 규칙 미적용 - 손실 확대")

            if buy_entry.confidence_level < 0.5:
                mistakes.append("낮은 신뢰도로 진입 - 기준 강화 필요")

        if buy_entry.market_condition == 'volatile':
            if buy_entry.was_successful:
                lessons.append("변동장에서 성공 - 변동성 활용 능력")
            else:
                mistakes.append("변동장 손실 - 안정적 시장 선호 권장")

        buy_entry.ai_analysis = " | ".join(analysis)
        buy_entry.lessons_learned = lessons
        buy_entry.mistakes = mistakes

        sell_entry.ai_analysis = buy_entry.ai_analysis
        sell_entry.lessons_learned = lessons
        sell_entry.mistakes = mistakes

        logger.info(f"AI analyzed trade: {buy_entry.stock_name} ({buy_entry.profit_loss_pct:+.1f}%)")

    def _analyze_patterns(self):
        """Analyze journal for recurring patterns"""
        if len(self.entries) < 20:
            return

        high_conf_trades = [e for e in self.entries if e.confidence_level > 0.7 and e.was_successful is not None]
        if len(high_conf_trades) >= 5:
            success_rate = sum(1 for e in high_conf_trades if e.was_successful) / len(high_conf_trades)
            avg_profit = np.mean([e.profit_loss_pct for e in high_conf_trades if e.profit_loss_pct])

            pattern = TradingPattern(
                pattern_id='high_confidence',
                pattern_name='높은 신뢰도 거래',
                description=f'신뢰도 70% 이상 거래의 승률이 {success_rate:.0%}',
                occurrences=len(high_conf_trades),
                success_rate=success_rate,
                avg_profit=avg_profit,
                examples=[e.id for e in high_conf_trades[:5]]
            )

            existing = [p for p in self.patterns if p.pattern_id == 'high_confidence']
            if existing:
                idx = self.patterns.index(existing[0])
                self.patterns[idx] = pattern
            else:
                self.patterns.append(pattern)


        self._save_journal()

    def generate_insights(self) -> List[JournalInsight]:
        """Generate AI insights from journal"""
        new_insights = []

        if len(self.entries) < 10:
            return new_insights

        completed_trades = [e for e in self.entries if e.was_successful is not None]

        if not completed_trades:
            return new_insights

        win_rate = sum(1 for e in completed_trades if e.was_successful) / len(completed_trades)

        if win_rate > 0.65:
            insight = JournalInsight(
                timestamp=datetime.now().isoformat(),
                insight_type='strength',
                title='우수한 승률',
                description=f'최근 승률 {win_rate:.0%}로 매우 우수합니다.',
                supporting_data=[f"총 {len(completed_trades)}건 거래 중 {sum(1 for e in completed_trades if e.was_successful)}건 성공"],
                recommendation='현재 전략을 유지하되, 성공 패턴을 문서화하세요.',
                priority='medium'
            )
            new_insights.append(insight)
        elif win_rate < 0.45:
            insight = JournalInsight(
                timestamp=datetime.now().isoformat(),
                insight_type='weakness',
                title='낮은 승률 경고',
                description=f'최근 승률 {win_rate:.0%}로 개선이 필요합니다.',
                supporting_data=[f"총 {len(completed_trades)}건 거래 중 {sum(1 for e in completed_trades if not e.was_successful)}건 실패"],
                recommendation='진입 기준을 더 엄격하게 조정하거나, 전략을 재검토하세요.',
                priority='high'
            )
            new_insights.append(insight)

        all_mistakes = []
        for entry in completed_trades:
            if entry.mistakes:
                all_mistakes.extend(entry.mistakes)

        if all_mistakes:
            from collections import Counter
            mistake_counts = Counter(all_mistakes)
            most_common = mistake_counts.most_common(1)[0]

            insight = JournalInsight(
                timestamp=datetime.now().isoformat(),
                insight_type='threat',
                title='반복되는 실수 감지',
                description=f'"{most_common[0]}" 실수가 {most_common[1]}회 반복되고 있습니다.',
                supporting_data=[f"{mistake}: {count}회" for mistake, count in mistake_counts.most_common(3)],
                recommendation='이 패턴을 인식하고 의식적으로 개선하세요.',
                priority='high'
            )
            new_insights.append(insight)

        strategy_performance = defaultdict(list)
        for entry in completed_trades:
            if entry.profit_loss_pct:
                strategy_performance[entry.strategy_used].append(entry.profit_loss_pct)

        if strategy_performance:
            best_strategy = max(strategy_performance.items(), key=lambda x: np.mean(x[1]))

            insight = JournalInsight(
                timestamp=datetime.now().isoformat(),
                insight_type='opportunity',
                title=f'최고 성과 전략: {best_strategy[0]}',
                description=f'{best_strategy[0]} 전략이 평균 {np.mean(best_strategy[1]):.1f}% 수익으로 가장 우수합니다.',
                supporting_data=[f"{strategy}: {np.mean(returns):.1f}% (거래 {len(returns)}건)"
                               for strategy, returns in strategy_performance.items()],
                recommendation=f'{best_strategy[0]} 전략의 비중을 늘리는 것을 고려하세요.',
                priority='medium'
            )
            new_insights.append(insight)

        self.insights.extend(new_insights)
        self._save_journal()

        return new_insights

    def get_statistics(self, period: str = 'all') -> Dict[str, Any]:
        """Get journal statistics"""
        if period == 'today':
            cutoff = datetime.now().replace(hour=0, minute=0, second=0)
            entries = [e for e in self.entries if datetime.fromisoformat(e.timestamp) >= cutoff]
        elif period == 'week':
            cutoff = datetime.now() - timedelta(days=7)
            entries = [e for e in self.entries if datetime.fromisoformat(e.timestamp) >= cutoff]
        elif period == 'month':
            cutoff = datetime.now() - timedelta(days=30)
            entries = [e for e in self.entries if datetime.fromisoformat(e.timestamp) >= cutoff]
        else:
            entries = self.entries

        completed_trades = [e for e in entries if e.was_successful is not None]

        if not completed_trades:
            return {'total_trades': 0}

        return {
            'total_trades': len(completed_trades),
            'winning_trades': sum(1 for e in completed_trades if e.was_successful),
            'losing_trades': sum(1 for e in completed_trades if not e.was_successful),
            'win_rate': sum(1 for e in completed_trades if e.was_successful) / len(completed_trades),
            'avg_profit': np.mean([e.profit_loss for e in completed_trades if e.profit_loss]),
            'avg_profit_pct': np.mean([e.profit_loss_pct for e in completed_trades if e.profit_loss_pct]),
            'best_trade': max(completed_trades, key=lambda x: x.profit_loss_pct if x.profit_loss_pct else 0),
            'worst_trade': min(completed_trades, key=lambda x: x.profit_loss_pct if x.profit_loss_pct else 0),
            'avg_holding_period': np.mean([e.holding_period for e in completed_trades if e.holding_period]),
            'total_patterns': len(self.patterns),
            'total_insights': len(self.insights)
        }

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for dashboard"""
        stats = self.get_statistics('month')
        recent_insights = self.insights[-5:] if self.insights else []

        return {
            'success': True,
            'statistics': stats,
            'recent_entries': [asdict(e) for e in self.entries[-10:]],
            'patterns': [asdict(p) for p in self.patterns],
            'recent_insights': [asdict(i) for i in recent_insights],
            'last_updated': datetime.now().isoformat()
        }


_trading_journal: Optional[TradingJournal] = None


def get_trading_journal(ai_learning_engine=None) -> TradingJournal:
    """Get or create trading journal instance"""
    global _trading_journal
    if _trading_journal is None:
        _trading_journal = TradingJournal(ai_learning_engine)
    return _trading_journal


if __name__ == '__main__':
    from collections import defaultdict

    journal = TradingJournal()

    print("\n📔 Trading Journal Test")
    print("=" * 60)

    buy = journal.record_trade(
        trade_type='buy',
        stock_code='005930',
        stock_name='삼성전자',
        quantity=100,
        price=73500,
        strategy='모멘텀',
        reason='RSI 45, 거래량 1.8배',
        confidence=0.75
    )

    sell = journal.record_trade(
        trade_type='sell',
        stock_code='005930',
        stock_name='삼성전자',
        quantity=100,
        price=75000,
        strategy='모멘텀',
        reason='익절 (+2%)',
        confidence=0.80
    )

    insights = journal.generate_insights()
    print(f"\n생성된 인사이트: {len(insights)}개")
    for insight in insights:
        print(f"  [{insight.insight_type}] {insight.title}")

    stats = journal.get_statistics()
    print(f"\n통계:")
    print(f"  총 거래: {stats.get('total_trades', 0)}건")
    print(f"  승률: {stats.get('win_rate', 0):.0%}")
