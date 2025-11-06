AutoTrade Pro - 고급 기능 모듈
실시간 호가창, 수익 추적, 포트폴리오 최적화, 뉴스 피드, 리스크 분석,
AI 자율 모드, 가상매매, 거래 일지, 알림 시스템 등

from .test_mode_manager import TestModeManager, run_test_mode

try:
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
    from .replay_simulator import ReplaySimulator, MarketSnapshot
    from .portfolio_rebalancer import PortfolioRebalancer, PortfolioTarget
except ImportError as e:
    import warnings
    warnings.warn(f"Some features modules could not be imported: {e}. Install required dependencies (numpy, pandas, etc.)")
    OrderBookService = OrderBook = None
    ProfitTracker = PerformanceMetrics = TradeRecord = None
    PortfolioOptimizer = PortfolioOptimization = None
    NewsFeedService = NewsArticle = NewsSummary = SentimentAnalyzer = None
    RiskAnalyzer = RiskAnalysis = StockRisk = PortfolioRisk = None
    AIAgent = AIDecision = AIStrategy = AIPerformance = get_ai_agent = None
    AILearningEngine = AITradingPattern = MarketRegime = LearningInsight = None
    PaperTradingEngine = VirtualAccount = VirtualPosition = StrategyConfig = get_paper_trading_engine = None
    TradingJournal = JournalEntry = JournalInsight = get_trading_journal = None
    NotificationManager = Notification = NotificationPriority = get_notification_manager = None
    ReplaySimulator = MarketSnapshot = None
    PortfolioRebalancer = PortfolioTarget = None

__all__ = [
    'TestModeManager',
    'run_test_mode',
    'OrderBookService',
    'OrderBook',
    'ProfitTracker',
    'PerformanceMetrics',
    'TradeRecord',
    'PortfolioOptimizer',
    'PortfolioOptimization',
    'NewsFeedService',
    'NewsArticle',
    'NewsSummary',
    'SentimentAnalyzer',
    'RiskAnalyzer',
    'RiskAnalysis',
    'StockRisk',
    'PortfolioRisk',
    'AIAgent',
    'AIDecision',
    'AIStrategy',
    'AIPerformance',
    'get_ai_agent',
    'AILearningEngine',
    'AITradingPattern',
    'MarketRegime',
    'LearningInsight',
    'PaperTradingEngine',
    'VirtualAccount',
    'VirtualPosition',
    'StrategyConfig',
    'get_paper_trading_engine',
    'TradingJournal',
    'JournalEntry',
    'JournalInsight',
    'get_trading_journal',
    'NotificationManager',
    'Notification',
    'NotificationPriority',
    'get_notification_manager',
    'ReplaySimulator',
    'MarketSnapshot',
    'PortfolioRebalancer',
    'PortfolioTarget',
]
