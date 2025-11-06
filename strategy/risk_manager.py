strategy/risk_manager.py
리스크 관리
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RiskManager:
    """
    리스크 관리 클래스
    
    주요 기능:
    - 손실 제한
    - 포지션 크기 제한
    - 일일 손실 한도
    - 연속 손실 감지
    - 리스크 모니터링
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        RiskManager 초기화
        
        Args:
            config: 리스크 관리 설정
                {
                    'max_position_size': 0.30,        # 최대 포지션 크기 30%
                    'max_daily_loss': 0.03,           # 일일 최대 손실 3%
                    'max_total_loss': 0.10,           # 총 최대 손실 10%
                    'stop_loss_rate': 0.05,           # 손절 비율 5%
                    'max_consecutive_losses': 3,      # 최대 연속 손실 횟수
                    'position_limit': 5,              # 최대 포지션 수
                    'emergency_stop_loss': 0.15,      # 긴급 손절 15%
                }
        """
        self.config = config or {}
        
        self.max_position_size = self.config.get('max_position_size', 0.30)
        self.max_daily_loss = self.config.get('max_daily_loss', 0.03)
        self.max_total_loss = self.config.get('max_total_loss', 0.10)
        self.stop_loss_rate = self.config.get('stop_loss_rate', 0.05)
        self.max_consecutive_losses = self.config.get('max_consecutive_losses', 3)
        self.position_limit = self.config.get('position_limit', 5)
        self.emergency_stop_loss = self.config.get('emergency_stop_loss', 0.15)
        
        self.daily_profit_loss = 0.0
        self.total_profit_loss = 0.0
        self.consecutive_losses = 0
        self.trading_enabled = True
        self.emergency_stop = False
        
        self.trade_history = []
        self.daily_reset_time = None
        
        logger.info("RiskManager 초기화 완료")
    
    
    def validate_position_size(
        self,
        position_value: float,
        total_assets: float
    ) -> tuple[bool, str]:
        포지션 크기 검증
        
        Args:
            position_value: 포지션 가치
            total_assets: 총 자산
        
        Returns:
            (검증 통과 여부, 메시지)
        if total_assets == 0:
            return False, "총 자산이 0입니다"
        
        position_ratio = position_value / total_assets
        
        if position_ratio > self.max_position_size:
            return False, f"포지션 크기 초과 ({position_ratio*100:.1f}% > {self.max_position_size*100:.1f}%)"
        
        return True, "포지션 크기 적정"
    
    def calculate_max_position_value(self, total_assets: float) -> float:
        """
        최대 포지션 가치 계산
        
        Args:
            total_assets: 총 자산
        
        Returns:
            최대 포지션 가치
        """
        return total_assets * self.max_position_size
    
    
    def check_stop_loss(
        self,
        purchase_price: float,
        current_price: float
    ) -> tuple[bool, str]:
        손절 여부 확인
        
        Args:
            purchase_price: 매수가
            current_price: 현재가
        
        Returns:
            (손절 여부, 메시지)
        if purchase_price == 0:
            return False, "매수가 정보 없음"
        
        loss_rate = (current_price - purchase_price) / purchase_price
        
        if loss_rate <= -self.emergency_stop_loss:
            return True, f"긴급 손절 발동 ({loss_rate*100:.2f}% 손실)"
        
        if loss_rate <= -self.stop_loss_rate:
            return True, f"손절 조건 충족 ({loss_rate*100:.2f}% 손실)"
        
        return False, "손절 조건 미충족"
    
    def check_daily_loss_limit(self) -> tuple[bool, str]:
        """
        일일 손실 한도 확인
        
        Returns:
            (거래 가능 여부, 메시지)
        """
        self._check_daily_reset()
        
        if abs(self.daily_profit_loss) >= self.max_daily_loss:
            return False, f"일일 손실 한도 도달 ({self.daily_profit_loss*100:.2f}%)"
        
        return True, "일일 손실 한도 내"
    
    def check_total_loss_limit(self, initial_capital: float) -> tuple[bool, str]:
        """
        총 손실 한도 확인
        
        Args:
            initial_capital: 초기 자본
        
        Returns:
            (거래 가능 여부, 메시지)
        """
        if initial_capital == 0:
            return True, "초기 자본 정보 없음"
        
        total_loss_rate = self.total_profit_loss / initial_capital
        
        if total_loss_rate <= -self.max_total_loss:
            self.emergency_stop = True
            return False, f"총 손실 한도 초과 ({total_loss_rate*100:.2f}%) - 긴급 정지"
        
        return True, "총 손실 한도 내"
    
    def update_profit_loss(
        self,
        profit_loss: float,
        is_win: bool
    ):
        손익 업데이트
        
        Args:
            profit_loss: 손익 금액
            is_win: 수익 여부
        self.daily_profit_loss += profit_loss
        
        self.total_profit_loss += profit_loss
        
        if is_win:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            
            if self.consecutive_losses >= self.max_consecutive_losses:
                logger.warning(f"연속 손실 {self.consecutive_losses}회 발생 - 거래 일시 정지 권고")
        
        logger.info(
            f"손익 업데이트: {profit_loss:+,.0f}원 "
            f"(일일: {self.daily_profit_loss:+,.0f}원, 총: {self.total_profit_loss:+,.0f}원)"
        )
    
    def _check_daily_reset(self):
        """일일 리셋 확인"""
        now = datetime.now()
        
        if self.daily_reset_time is None:
            self.daily_reset_time = now
            return
        
        if now.date() > self.daily_reset_time.date():
            logger.info(f"일일 손익 리셋 (이전: {self.daily_profit_loss:+,.0f}원)")
            self.daily_profit_loss = 0.0
            self.daily_reset_time = now
    
    
    def can_open_position(self, current_positions: int) -> tuple[bool, str]:
        """
        포지션 추가 가능 여부
        
        Args:
            current_positions: 현재 포지션 수
        
        Returns:
            (추가 가능 여부, 메시지)
        """
        if current_positions >= self.position_limit:
            return False, f"최대 포지션 수 도달 ({current_positions}/{self.position_limit})"
        
        return True, f"포지션 추가 가능 ({current_positions}/{self.position_limit})"
    
    
    def can_trade(self, reason: str = "") -> tuple[bool, str]:
        """
        거래 가능 여부 확인
        
        Args:
            reason: 확인 사유
        
        Returns:
            (거래 가능 여부, 메시지)
        """
        if self.emergency_stop:
            return False, "긴급 정지 상태"
        
        if not self.trading_enabled:
            return False, "거래 비활성화됨"
        
        can_trade_daily, msg_daily = self.check_daily_loss_limit()
        if not can_trade_daily:
            return False, msg_daily
        
        if self.consecutive_losses >= self.max_consecutive_losses:
            return False, f"연속 손실 {self.consecutive_losses}회 도달"
        
        return True, "거래 가능"
    
    def enable_trading(self):
        """거래 활성화"""
        self.trading_enabled = True
        logger.info("거래 활성화")
    
    def disable_trading(self, reason: str = ""):
        """거래 비활성화"""
        self.trading_enabled = False
        logger.warning(f"거래 비활성화: {reason}")
    
    def reset_emergency_stop(self):
        """긴급 정지 해제 (신중하게 사용)"""
        self.emergency_stop = False
        logger.warning("긴급 정지 해제됨")
    
    
    def assess_risk_level(
        self,
        portfolio_value: float,
        total_assets: float,
        position_count: int
    ) -> Dict[str, Any]:
        리스크 수준 평가
        
        Args:
            portfolio_value: 포트폴리오 가치
            total_assets: 총 자산
            position_count: 포지션 수
        
        Returns:
            리스크 평가 결과
        risk_score = 0
        risk_factors = []
        
        if total_assets > 0:
            concentration = portfolio_value / total_assets
            if concentration > 0.8:
                risk_score += 3
                risk_factors.append("높은 주식 집중도")
            elif concentration > 0.6:
                risk_score += 2
                risk_factors.append("중간 주식 집중도")
            elif concentration > 0.4:
                risk_score += 1
        
        if abs(self.daily_profit_loss) > self.max_daily_loss * 0.8:
            risk_score += 3
            risk_factors.append("높은 일일 손실")
        elif abs(self.daily_profit_loss) > self.max_daily_loss * 0.5:
            risk_score += 2
            risk_factors.append("중간 일일 손실")
        
        if self.consecutive_losses >= 2:
            risk_score += 2
            risk_factors.append(f"연속 손실 {self.consecutive_losses}회")
        elif self.consecutive_losses >= 1:
            risk_score += 1
        
        if position_count >= self.position_limit:
            risk_score += 2
            risk_factors.append("최대 포지션 수 도달")
        elif position_count >= self.position_limit * 0.8:
            risk_score += 1
            risk_factors.append("높은 포지션 수")
        
        if risk_score >= 7:
            risk_level = "Critical"
            recommendation = "즉시 포지션 축소 및 손실 제한 필요"
        elif risk_score >= 5:
            risk_level = "High"
            recommendation = "포지션 축소 및 신규 매수 자제"
        elif risk_score >= 3:
            risk_level = "Medium"
            recommendation = "주의 깊은 모니터링 필요"
        else:
            risk_level = "Low"
            recommendation = "정상 운영 가능"
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'recommendation': recommendation,
            'can_trade': risk_score < 7,
            'daily_profit_loss': self.daily_profit_loss,
            'total_profit_loss': self.total_profit_loss,
            'consecutive_losses': self.consecutive_losses,
        }
    
    
    def record_trade(
        self,
        stock_code: str,
        action: str,
        quantity: int,
        price: float,
        profit_loss: float = 0.0
    ):
        거래 기록
        
        Args:
            stock_code: 종목코드
            action: 'buy' | 'sell'
            quantity: 수량
            price: 가격
            profit_loss: 손익 (매도 시)
        trade = {
            'timestamp': datetime.now(),
            'stock_code': stock_code,
            'action': action,
            'quantity': quantity,
            'price': price,
            'profit_loss': profit_loss,
        }
        
        self.trade_history.append(trade)
        
        if len(self.trade_history) > 100:
            self.trade_history = self.trade_history[-100:]
    
    def get_recent_trades(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        최근 거래 조회
        
        Args:
            count: 조회 개수
        
        Returns:
            거래 이력
        """
        return self.trade_history[-count:] if self.trade_history else []
    
    
    def get_status(self) -> Dict[str, Any]:
        """
        리스크 관리 상태
        
        Returns:
            상태 정보
        """
        return {
            'trading_enabled': self.trading_enabled,
            'emergency_stop': self.emergency_stop,
            'daily_profit_loss': self.daily_profit_loss,
            'total_profit_loss': self.total_profit_loss,
            'consecutive_losses': self.consecutive_losses,
            'max_daily_loss': self.max_daily_loss,
            'max_total_loss': self.max_total_loss,
            'stop_loss_rate': self.stop_loss_rate,
            'position_limit': self.position_limit,
        }
    
    def reset(self):
        """리스크 관리 상태 리셋"""
        self.daily_profit_loss = 0.0
        self.total_profit_loss = 0.0
        self.consecutive_losses = 0
        self.trading_enabled = True
        self.emergency_stop = False
        self.daily_reset_time = None
        
        logger.info("RiskManager 상태 리셋 완료")


__all__ = ['RiskManager']