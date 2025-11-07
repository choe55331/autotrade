"""
strategy/base_strategy.py
전략 기본 클래스
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """
    매매 전략 기본 추상 클래스
    
    모든 전략은 이 클래스를 상속받아 구현해야 함
    """
    
    def __init__(
        self,
        name: str,
        client,
        config: Dict[str, Any] = None
    ):
        """
        전략 초기화
        
        Args:
            name: 전략 이름
            client: KiwoomRESTClient 인스턴스
            config: 전략 설정
            """
        self.name = name
        self.client = client
        self.config = config or {}
        
        self.is_active = False
        self.positions = {}
        self.orders = {}
        
        self.stats = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit_loss': 0.0,
            'start_time': None,
            'last_trade_time': None,
        }
        
        logger.info(f"{self.name} 전략 초기화 완료")
    
    @abstractmethod
    def analyze(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        종목 분석 (추상 메서드)
        
        Args:
            stock_data: 종목 데이터
        
        Returns:
            분석 결과
            {
                'signal': 'buy' | 'sell' | 'hold',
                'score': 0.0~10.0,
                'reason': '매수/매도 이유',
                'confidence': 'Low' | 'Medium' | 'High'
            }
        """
        pass
    
    @abstractmethod
    def should_buy(self, stock_code: str, analysis: Dict[str, Any]) -> bool:
        """
        매수 여부 판단 (추상 메서드)
        
        Args:
            stock_code: 종목코드
            analysis: 분석 결과
        
        Returns:
            매수 여부
        """
        pass
    
    @abstractmethod
    def should_sell(self, stock_code: str, position: Dict[str, Any]) -> bool:
        """
        매도 여부 판단 (추상 메서드)
        
        Args:
            stock_code: 종목코드
            position: 포지션 정보
        
        Returns:
            매도 여부
        """
        pass
    
    @abstractmethod
    def calculate_position_size(
        self,
        stock_code: str,
        current_price: int,
        available_cash: int
    ) -> int:
        """
        포지션 크기 계산 (추상 메서드)
        
        Args:
            stock_code: 종목코드
            current_price: 현재가
            available_cash: 가용 현금
        
        Returns:
            매수 수량
        pass
    
    
    """
    def start(self):
        """전략 시작"""
        self.is_active = True
        self.stats['start_time'] = datetime.now()
        logger.info(f"{self.name} 전략 시작")
    
    def stop(self):
        """전략 중지"""
        self.is_active = False
        logger.info(f"{self.name} 전략 중지")
    
    def add_position(
        self,
        stock_code: str,
        quantity: int,
        purchase_price: float,
        order_id: str = None
    ):
        """
        포지션 추가
        
        Args:
            stock_code: 종목코드
            quantity: 수량
            purchase_price: 매수가
            order_id: 주문번호
            """
        self.positions[stock_code] = {
            'stock_code': stock_code,
            'quantity': quantity,
            'purchase_price': purchase_price,
            'purchase_time': datetime.now(),
            'order_id': order_id,
            'current_price': purchase_price,
            'profit_loss': 0.0,
            'profit_loss_rate': 0.0,
        }
        
        logger.info(f"포지션 추가: {stock_code} {quantity}주 @ {purchase_price:,.0f}원")
    
    def remove_position(self, stock_code: str):
        """
        포지션 제거
        
        Args:
            stock_code: 종목코드
        """
        if stock_code in self.positions:
            position = self.positions.pop(stock_code)
            logger.info(f"포지션 제거: {stock_code}")
            return position
        return None
    
    def update_position(
        self,
        stock_code: str,
        current_price: float
    ):
        """
        포지션 업데이트
        
        Args:
            stock_code: 종목코드
            current_price: 현재가
            """
        if stock_code not in self.positions:
            return
        
        position = self.positions[stock_code]
        position['current_price'] = current_price
        
        purchase_price = position['purchase_price']
        quantity = position['quantity']
        
        position['profit_loss'] = (current_price - purchase_price) * quantity
        if purchase_price > 0:
            position['profit_loss_rate'] = ((current_price - purchase_price) / purchase_price) * 100
    
    def get_position(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        포지션 조회
        
        Args:
            stock_code: 종목코드
        
        Returns:
            포지션 정보
        """
        return self.positions.get(stock_code)
    
    def get_all_positions(self) -> Dict[str, Dict[str, Any]]:
        """모든 포지션 조회"""
        return self.positions.copy()
    
    def has_position(self, stock_code: str) -> bool:
        """
        포지션 보유 여부
        
        Args:
            stock_code: 종목코드
        
        Returns:
            보유 여부
        """
        return stock_code in self.positions
    
    def get_position_count(self) -> int:
        """포지션 개수"""
        return len(self.positions)
    
    
    def record_trade(
        self,
        stock_code: str,
        action: str,
        quantity: int,
        price: float,
        profit_loss: float = 0.0
    ):
        """
        거래 기록
        
        Args:
            stock_code: 종목코드
            action: 'buy' | 'sell'
            quantity: 수량
            price: 가격
            profit_loss: 손익 (매도 시)
            """
        self.stats['total_trades'] += 1
        self.stats['last_trade_time'] = datetime.now()
        
        if action == 'sell':
            self.stats['total_profit_loss'] += profit_loss
            
            if profit_loss > 0:
                self.stats['winning_trades'] += 1
            elif profit_loss < 0:
                self.stats['losing_trades'] += 1
        
        logger.info(
            f"거래 기록: {action.upper()} {stock_code} "
            f"{quantity}주 @ {price:,.0f}원 "
            f"(손익: {profit_loss:+,.0f}원)"
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        전략 통계 조회
        
        Returns:
            통계 정보
        """
        total_trades = self.stats['total_trades']
        winning_trades = self.stats['winning_trades']
        losing_trades = self.stats['losing_trades']
        
        if total_trades > 0:
            win_rate = (winning_trades / total_trades) * 100
        else:
            win_rate = 0.0
        
        if self.stats['start_time']:
            running_time = datetime.now() - self.stats['start_time']
            running_hours = running_time.total_seconds() / 3600
        else:
            running_hours = 0.0
        
        return {
            'strategy_name': self.name,
            'is_active': self.is_active,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': round(win_rate, 2),
            'total_profit_loss': self.stats['total_profit_loss'],
            'position_count': len(self.positions),
            'running_hours': round(running_hours, 2),
            'start_time': self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S') if self.stats['start_time'] else None,
            'last_trade_time': self.stats['last_trade_time'].strftime('%Y-%m-%d %H:%M:%S') if self.stats['last_trade_time'] else None,
        }
    
    def reset_statistics(self):
        """통계 초기화"""
        self.stats = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit_loss': 0.0,
            'start_time': datetime.now(),
            'last_trade_time': None,
        }
        logger.info(f"{self.name} 통계 초기화")
    
    
    def get_config(self, key: str, default=None):
        """
        설정 값 조회
        
        Args:
            key: 설정 키
            default: 기본값
        
        Returns:
            설정 값
        """
        return self.config.get(key, default)
    
    def update_config(self, key: str, value: Any):
        """
        설정 값 업데이트
        
        Args:
            key: 설정 키
            value: 설정 값
        """
        self.config[key] = value
        logger.info(f"{self.name} 설정 업데이트: {key} = {value}")
    
    def get_all_config(self) -> Dict[str, Any]:
        """전체 설정 조회"""
        return self.config.copy()
    
    
    def get_state(self) -> Dict[str, Any]:
        """
        전략 상태 정보
        
        Returns:
            상태 정보
        """
        return {
            'name': self.name,
            'is_active': self.is_active,
            'positions': self.get_all_positions(),
            'statistics': self.get_statistics(),
            'config': self.get_all_config(),
        }
    
    def __repr__(self):
        """
        """
        return f"<{self.__class__.__name__}(name='{self.name}', active={self.is_active}, positions={len(self.positions)})>"


__all__ = ['BaseStrategy']