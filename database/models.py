database/models.py
SQLAlchemy 데이터베이스 모델
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pathlib import Path

from utils.logger_new import get_logger

from config.config_manager import get_config


logger = get_logger()
Base = declarative_base()


class Trade(Base):
    """거래 기록"""

    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)

    stock_code = Column(String(10), nullable=False, index=True)
    stock_name = Column(String(50), nullable=False)

    action = Column(String(10), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    total_amount = Column(Integer, nullable=False)

    profit_loss = Column(Integer, default=0)
    profit_loss_ratio = Column(Float, default=0.0)

    risk_mode = Column(String(20), nullable=True)

    ai_score = Column(Float, nullable=True)
    ai_signal = Column(String(10), nullable=True)
    ai_confidence = Column(String(10), nullable=True)

    scoring_total = Column(Float, nullable=True)
    scoring_percentage = Column(Float, nullable=True)

    notes = Column(Text, nullable=True)

    __table_args__ = (
        Index('idx_stock_timestamp', 'stock_code', 'timestamp'),
    )

    def __repr__(self):
        return f"<Trade(id={self.id}, {self.action} {self.stock_name} {self.quantity}주 @ {self.price}원)>"


class Position(Base):
    """포지션 (보유 종목)"""

    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    stock_code = Column(String(10), nullable=False, unique=True, index=True)
    stock_name = Column(String(50), nullable=False)

    quantity = Column(Integer, nullable=False)
    entry_price = Column(Integer, nullable=False)
    current_price = Column(Integer, nullable=False)

    take_profit_price = Column(Integer, nullable=True)
    stop_loss_price = Column(Integer, nullable=True)

    profit_loss = Column(Integer, default=0)
    profit_loss_ratio = Column(Float, default=0.0)

    entry_risk_mode = Column(String(20), nullable=True)

    is_active = Column(Boolean, default=True, index=True)

    def __repr__(self):
        return f"<Position(id={self.id}, {self.stock_name} {self.quantity}주 @ {self.entry_price}원)>"

    def to_core_position(self):
        """
        ORM Position → Core Position 변환

        Returns:
            core.Position instance
        """
        from core import Position as CorePosition

        return CorePosition(
            stock_code=self.stock_code,
            stock_name=self.stock_name,
            quantity=self.quantity,
            purchase_price=float(self.entry_price),
            current_price=float(self.current_price),
            entry_time=self.created_at,
            stop_loss_price=float(self.stop_loss_price) if self.stop_loss_price else None,
            take_profit_price=float(self.take_profit_price) if self.take_profit_price else None,
            metadata={
                'db_id': self.id,
                'entry_risk_mode': self.entry_risk_mode,
                'is_active': self.is_active
            }
        )

    @classmethod
    def from_core_position(cls, pos, session=None):
        """
        Core Position → ORM Position 변환

        Args:
            pos: core.Position instance
            session: SQLAlchemy session (for saving)

        Returns:
            database.Position instance
        """
        db_pos = cls(
            stock_code=pos.stock_code,
            stock_name=pos.stock_name,
            quantity=pos.quantity,
            entry_price=int(pos.purchase_price),
            current_price=int(pos.current_price),
            take_profit_price=int(pos.take_profit_price) if pos.take_profit_price else None,
            stop_loss_price=int(pos.stop_loss_price) if pos.stop_loss_price else None,
            profit_loss=int(pos.profit_loss),
            profit_loss_ratio=pos.profit_loss_rate / 100.0 if pos.profit_loss_rate else 0.0,
            entry_risk_mode=pos.metadata.get('entry_risk_mode') if pos.metadata else None,
            is_active=pos.metadata.get('is_active', True) if pos.metadata else True
        )

        if session:
            session.add(db_pos)

        return db_pos


class PortfolioSnapshot(Base):
    """포트폴리오 스냅샷 (일일 기록)"""

    __tablename__ = 'portfolio_snapshots'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)

    total_capital = Column(Integer, nullable=False)
    cash = Column(Integer, nullable=False)
    stock_value = Column(Integer, nullable=False)

    total_profit_loss = Column(Integer, default=0)
    total_profit_loss_ratio = Column(Float, default=0.0)

    open_positions = Column(Integer, default=0)

    risk_mode = Column(String(20), nullable=True)

    daily_trades = Column(Integer, default=0)
    daily_profit_loss = Column(Integer, default=0)

    def __repr__(self):
        return f"<PortfolioSnapshot(timestamp={self.timestamp}, capital={self.total_capital:,}원)>"


class ScanResult(Base):
    """스캔 결과 기록"""

    __tablename__ = 'scan_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)

    scan_stage = Column(String(20), nullable=False, index=True)

    stock_code = Column(String(10), nullable=False, index=True)
    stock_name = Column(String(50), nullable=False)

    score = Column(Float, default=0.0)

    ai_score = Column(Float, nullable=True)
    ai_signal = Column(String(10), nullable=True)
    ai_confidence = Column(String(10), nullable=True)
    ai_reasons = Column(Text, nullable=True)

    approved = Column(Boolean, default=False, index=True)

    __table_args__ = (
        Index('idx_scan_stage_timestamp', 'scan_stage', 'timestamp'),
    )

    def __repr__(self):
        return f"<ScanResult({self.scan_stage} scan: {self.stock_name}, score={self.score:.1f})>"


class SystemLog(Base):
    """시스템 로그"""

    __tablename__ = 'system_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)

    level = Column(String(10), nullable=False, index=True)

    message = Column(Text, nullable=False)

    category = Column(String(50), nullable=True, index=True)

    extra_data = Column(Text, nullable=True)

    def __repr__(self):
        return f"<SystemLog({self.level}: {self.message[:50]})>"


class Database:
    """데이터베이스 관리자"""

    _instance: Optional['Database'] = None
    _engine = None
    _Session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """초기화"""
        if self._engine is None:
            self._initialize_database()

    def _initialize_database(self):
        """데이터베이스 초기화"""
        try:
            config = get_config()
            db_config = config.database

            db_type = db_config.get('type', 'sqlite')

            if db_type == 'sqlite':
                db_path = db_config.get('path', 'data/autotrade.db')
                db_file = Path(db_path)
                db_file.parent.mkdir(parents=True, exist_ok=True)

                connection_string = f"sqlite:///{db_path}"
            else:
                raise NotImplementedError(f"Database type '{db_type}' not implemented yet")

            self._engine = create_engine(
                connection_string,
                echo=db_config.get('echo', False),
                pool_size=db_config.get('pool_size', 5),
                max_overflow=db_config.get('max_overflow', 10),
            )

            Base.metadata.create_all(self._engine)

            self._Session = sessionmaker(bind=self._engine)

            logger.info(f"💾 데이터베이스 초기화 완료: {connection_string}")

        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}", exc_info=True)
            raise

    def get_session(self):
        """세션 가져오기"""
        if self._Session is None:
            self._initialize_database()
        return self._Session()

    def close(self):
        """데이터베이스 종료"""
        if self._engine:
            self._engine.dispose()
            logger.info("💾 데이터베이스 종료")


_database = Database()


def get_db_session():
    """데이터베이스 세션 가져오기"""
    return _database.get_session()


def close_database():
    """데이터베이스 종료"""
    _database.close()


class BacktestResult(Base):
    """백테스팅 결과"""

    __tablename__ = 'backtest_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)

    backtest_id = Column(String(50), unique=True, nullable=False, index=True)
    strategy_name = Column(String(50), nullable=False)
    start_date = Column(String(10), nullable=False)
    end_date = Column(String(10), nullable=False)

    initial_capital = Column(Float, nullable=False)
    final_capital = Column(Float, nullable=False)

    total_return = Column(Float, nullable=False)
    total_return_pct = Column(Float, nullable=False)

    sharpe_ratio = Column(Float, nullable=True)
    sortino_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    max_drawdown_pct = Column(Float, nullable=True)
    calmar_ratio = Column(Float, nullable=True)

    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)

    avg_win = Column(Float, nullable=True)
    avg_loss = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)

    report_html_path = Column(String(200), nullable=True)
    report_pdf_path = Column(String(200), nullable=True)

    parameters = Column(Text, nullable=True)

    def __repr__(self):
        return f"<BacktestResult({self.strategy_name}: {self.total_return_pct:.2f}%)>"


class OptimizationResult(Base):
    """파라미터 최적화 결과"""

    __tablename__ = 'optimization_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)

    optimization_id = Column(String(50), unique=True, nullable=False, index=True)
    strategy_name = Column(String(50), nullable=False)
    method = Column(String(20), nullable=False)

    best_params = Column(Text, nullable=False)
    best_score = Column(Float, nullable=False)

    n_trials = Column(Integer, nullable=False)
    n_completed = Column(Integer, nullable=False)
    duration_seconds = Column(Float, nullable=False)

    trials_data = Column(Text, nullable=True)

    def __repr__(self):
        return f"<OptimizationResult({self.strategy_name}: score={self.best_score:.4f})>"


class Alert(Base):
    """알림 기록"""

    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)

    alert_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), default='info')

    title = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)

    stock_code = Column(String(10), nullable=True, index=True)
    stock_name = Column(String(50), nullable=True)

    sent_email = Column(Boolean, default=False)
    sent_sms = Column(Boolean, default=False)
    sent_telegram = Column(Boolean, default=False)
    sent_web_push = Column(Boolean, default=False)

    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime, nullable=True)

    extra_data = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Alert({self.alert_type}: {self.title})>"


class StrategyPerformance(Base):
    """전략 성과 기록"""

    __tablename__ = 'strategy_performances'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)

    strategy_name = Column(String(50), nullable=False, index=True)

    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)

    total_profit = Column(Float, default=0.0)
    total_profit_pct = Column(Float, default=0.0)
    avg_profit_per_trade = Column(Float, default=0.0)

    parameters = Column(Text, nullable=True)

    def __repr__(self):
        return f"<StrategyPerformance({self.strategy_name}: {self.win_rate:.2f}% win rate)>"


class AnomalyLog(Base):
    """시스템 이상 감지 로그"""

    __tablename__ = 'anomaly_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    detected_at = Column(DateTime, default=datetime.now, nullable=False, index=True)

    anomaly_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), default='medium')

    expected_value = Column(Float, nullable=True)
    actual_value = Column(Float, nullable=True)
    anomaly_score = Column(Float, nullable=True)

    description = Column(Text, nullable=False)

    action_taken = Column(Boolean, default=False)
    action_description = Column(Text, nullable=True)

    extra_data = Column(Text, nullable=True)

    def __repr__(self):
        return f"<AnomalyLog({self.anomaly_type}: score={self.anomaly_score:.2f})>"


class MarketRegime(Base):
    """시장 레짐 분류 기록"""

    __tablename__ = 'market_regimes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    classified_at = Column(DateTime, default=datetime.now, nullable=False, index=True)

    regime_type = Column(String(20), nullable=False)
    volatility_level = Column(String(20), nullable=False)

    confidence = Column(Float, nullable=False)

    vix_level = Column(Float, nullable=True)
    trend_strength = Column(Float, nullable=True)
    market_momentum = Column(Float, nullable=True)

    recommended_strategy = Column(String(50), nullable=True)

    indicators = Column(Text, nullable=True)

    def __repr__(self):
        return f"<MarketRegime({self.regime_type}, {self.volatility_level})>"


__all__ = [
    'Trade',
    'Position',
    'PortfolioSnapshot',
    'ScanResult',
    'SystemLog',
    'BacktestResult',
    'OptimizationResult',
    'Alert',
    'StrategyPerformance',
    'AnomalyLog',
    'MarketRegime',
    'Database',
    'get_db_session',
    'close_database',
]
