"""
AutoTrade Pro - 고급 기능 모듈
실시간 호가창, 수익 추적, 포트폴리오 최적화, 뉴스 피드, 리스크 분석,
AI 자율 모드, 가상매매, 거래 일지, 알림 시스템 등
"""
from .order_book import OrderBookService, OrderBook
from .profit_tracker import ProfitTracker, PerformanceMetrics, TradeRecord
from .portfolio_optimizer import PortfolioOptimizer, PortfolioOptimization
from .news_feed import NewsFeedService, NewsArticle, NewsSummary, SentimentAnalyzer
from .risk_analyzer import RiskAnalyzer, RiskAnalysis, StockRisk, PortfolioRisk
from .ai_mode import AIAgent, AIDecision, AIStrategy, AIPerformance, get_ai_agent
from .ai_learning import AILearningEngine, TradingPattern as AITradingPattern, MarketRegime, LearningInsight
from .paper_trading import PaperTradingEngine, VirtualAccount, VirtualPosition, StrategyConfig, get_paper_trading_engine
from .trading_journal import TradingJournal, JournalEntry, JournalInsight, get_trading_journal
from .notification import NotificationManager, Notification, NotificationPriority, get_notification_manager

__all__ = [
    # Order Book
    'OrderBookService',
    'OrderBook',
    # Profit Tracking
    'ProfitTracker',
    'PerformanceMetrics',
    'TradeRecord',
    # Portfolio Optimization
    'PortfolioOptimizer',
    'PortfolioOptimization',
    # News Feed
    'NewsFeedService',
    'NewsArticle',
    'NewsSummary',
    'SentimentAnalyzer',
    # Risk Analysis
    'RiskAnalyzer',
    'RiskAnalysis',
    'StockRisk',
    'PortfolioRisk',
    # AI Mode (v3.6)
    'AIAgent',
    'AIDecision',
    'AIStrategy',
    'AIPerformance',
    'get_ai_agent',
    # AI Learning
    'AILearningEngine',
    'AITradingPattern',
    'MarketRegime',
    'LearningInsight',
    # Paper Trading (v3.7)
    'PaperTradingEngine',
    'VirtualAccount',
    'VirtualPosition',
    'StrategyConfig',
    'get_paper_trading_engine',
    # Trading Journal (v3.7)
    'TradingJournal',
    'JournalEntry',
    'JournalInsight',
    'get_trading_journal',
    # Notifications (v3.7)
    'NotificationManager',
    'Notification',
    'NotificationPriority',
    'get_notification_manager',
]
