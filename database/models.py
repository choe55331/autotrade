"""
database/models.py
SQLAlchemy 데이터베이스 모델
"""
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

try:
    from utils.logger_new import get_logger
except ImportError:
    from utils.logger import get_logger

from config.config_manager import get_config


logger = get_logger()
Base = declarative_base()


class Trade(Base):
    """거래 기록"""

    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)

    # 종목 정보
    stock_code = Column(String(10), nullable=False, index=True)
    stock_name = Column(String(50), nullable=False)

    # 거래 정보
    action = Column(String(10), nullable=False)  # 'buy' or 'sell'
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    total_amount = Column(Integer, nullable=False)

    # 수익/손실 (매도 시에만)
    profit_loss = Column(Integer, default=0)
    profit_loss_ratio = Column(Float, default=0.0)

    # 리스크 모드
    risk_mode = Column(String(20), nullable=True)

    # AI 분석 결과
    ai_score = Column(Float, nullable=True)
    ai_signal = Column(String(10), nullable=True)
    ai_confidence = Column(String(10), nullable=True)

    # 스코어링 결과
    scoring_total = Column(Float, nullable=True)
    scoring_percentage = Column(Float, nullable=True)

    # 기타
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

    # 종목 정보
    stock_code = Column(String(10), nullable=False, unique=True, index=True)
    stock_name = Column(String(50), nullable=False)

    # 포지션 정보
    quantity = Column(Integer, nullable=False)
    entry_price = Column(Integer, nullable=False)
    current_price = Column(Integer, nullable=False)

    # 목표가
    take_profit_price = Column(Integer, nullable=True)
    stop_loss_price = Column(Integer, nullable=True)

    # 수익/손실
    profit_loss = Column(Integer, default=0)
    profit_loss_ratio = Column(Float, default=0.0)

    # 진입 시 모드
    entry_risk_mode = Column(String(20), nullable=True)

    # 활성 여부
    is_active = Column(Boolean, default=True, index=True)

    def __repr__(self):
        return f"<Position(id={self.id}, {self.stock_name} {self.quantity}주 @ {self.entry_price}원)>"


class PortfolioSnapshot(Base):
    """포트폴리오 스냅샷 (일일 기록)"""

    __tablename__ = 'portfolio_snapshots'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)

    # 자본금
    total_capital = Column(Integer, nullable=False)
    cash = Column(Integer, nullable=False)
    stock_value = Column(Integer, nullable=False)

    # 수익/손실
    total_profit_loss = Column(Integer, default=0)
    total_profit_loss_ratio = Column(Float, default=0.0)

    # 포지션 정보
    open_positions = Column(Integer, default=0)

    # 리스크 모드
    risk_mode = Column(String(20), nullable=True)

    # 일일 통계
    daily_trades = Column(Integer, default=0)
    daily_profit_loss = Column(Integer, default=0)

    def __repr__(self):
        return f"<PortfolioSnapshot(timestamp={self.timestamp}, capital={self.total_capital:,}원)>"


class ScanResult(Base):
    """스캔 결과 기록"""

    __tablename__ = 'scan_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)

    # 스캔 단계
    scan_stage = Column(String(20), nullable=False, index=True)  # 'fast', 'deep', 'ai'

    # 종목 정보
    stock_code = Column(String(10), nullable=False, index=True)
    stock_name = Column(String(50), nullable=False)

    # 점수
    score = Column(Float, default=0.0)

    # AI 분석 (AI 스캔만)
    ai_score = Column(Float, nullable=True)
    ai_signal = Column(String(10), nullable=True)
    ai_confidence = Column(String(10), nullable=True)
    ai_reasons = Column(Text, nullable=True)  # JSON 문자열

    # 승인 여부
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

    # 로그 레벨
    level = Column(String(10), nullable=False, index=True)  # 'INFO', 'WARNING', 'ERROR', etc.

    # 로그 내용
    message = Column(Text, nullable=False)

    # 카테고리
    category = Column(String(50), nullable=True, index=True)  # 'trading', 'scanning', 'risk', etc.

    # 추가 데이터 (JSON)
    extra_data = Column(Text, nullable=True)

    def __repr__(self):
        return f"<SystemLog({self.level}: {self.message[:50]})>"


# 데이터베이스 엔진 및 세션
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
                # PostgreSQL 등 다른 DB 지원 (향후 확장)
                raise NotImplementedError(f"Database type '{db_type}' not implemented yet")

            # 엔진 생성
            self._engine = create_engine(
                connection_string,
                echo=db_config.get('echo', False),
                pool_size=db_config.get('pool_size', 5),
                max_overflow=db_config.get('max_overflow', 10),
            )

            # 테이블 생성
            Base.metadata.create_all(self._engine)

            # 세션 팩토리 생성
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


# 싱글톤 인스턴스
_database = Database()


def get_db_session():
    """데이터베이스 세션 가져오기"""
    return _database.get_session()


def close_database():
    """데이터베이스 종료"""
    _database.close()


__all__ = [
    'Trade',
    'Position',
    'PortfolioSnapshot',
    'ScanResult',
    'SystemLog',
    'Database',
    'get_db_session',
    'close_database',
]
