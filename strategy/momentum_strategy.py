"""
strategy/momentum_strategy.py
모멘텀 전략 구현
"""
import logging
from typing import Dict, Any, Optional
from .base_strategy import BaseStrategy

from utils.position_calculator import calculate_position_size_by_ratio

logger = logging.getLogger(__name__)


class MomentumStrategy(BaseStrategy):
    """
    모멘텀 전략
    
    전략 로직:
    1. 상승률이 높고 거래량이 많은 종목 매수
    2. 목표 수익률 도달 시 매도
    3. 손절 비율 도달 시 손절
    """
    
    def __init__(self, client, config: Dict[str, Any] = None):
        """
        모멘텀 전략 초기화
        
        Args:
            client: KiwoomRESTClient 인스턴스
            config: 전략 설정
                {
                    'min_change_rate': 3.0,      # 최소 등락률
                    'min_volume': 100000,        # 최소 거래량
                    'take_profit_rate': 0.10,    # 목표 수익률 10%
                    'stop_loss_rate': -0.05,     # 손절 비율 -5%
                    'max_positions': 5,          # 최대 포지션
                    'position_size_rate': 0.20,  # 포지션 크기 비율 20%
                }
        """
        default_config = {
            'min_change_rate': 3.0,
            'min_volume': 100000,
            'take_profit_rate': 0.10,
            'stop_loss_rate': -0.05,
            'max_positions': 5,
            'position_size_rate': 0.20,
        }
        
        if config:
            default_config.update(config)
        
        super().__init__("MomentumStrategy", client, default_config)
        logger.info("모멘텀 전략 초기화 완료")
    
    def analyze(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        종목 분석
        
        Args:
            stock_data: 종목 데이터
        
        Returns:
            분석 결과
        """
        stock_code = stock_data.get('stock_code', '')
        stock_name = stock_data.get('stock_name', '')
        change_rate = float(stock_data.get('change_rate', 0))
        volume = int(stock_data.get('volume', 0))
        current_price = int(stock_data.get('current_price', 0))
        
        min_change_rate = self.get_config('min_change_rate', 3.0)
        min_volume = self.get_config('min_volume', 100000)
        
        score = 0.0
        reasons = []
        
        if change_rate >= min_change_rate:
            rate_score = min(change_rate / 2, 5.0)
            score += rate_score
            reasons.append(f"상승률 {change_rate:.2f}%")
        
        if volume >= min_volume:
            volume_score = min(volume / min_volume, 3.0)
            score += volume_score
            reasons.append(f"거래량 {volume:,}주")
        
        technical = stock_data.get('technical', {})
        if technical:
            ma5 = technical.get('ma5', 0)
            ma20 = technical.get('ma20', 0)
            
            if current_price > ma5 > ma20:
                score += 2.0
                reasons.append("이동평균선 정배열")
            elif current_price > ma5:
                score += 1.0
                reasons.append("5일선 상향")
        
        if score >= 7.0:
            signal = 'buy'
            confidence = 'High'
        elif score >= 5.0:
            signal = 'buy'
            confidence = 'Medium'
        elif score >= 3.0:
            signal = 'hold'
            confidence = 'Low'
        else:
            signal = 'hold'
            confidence = 'Low'
        
        reason = f"{stock_name}: " + ", ".join(reasons) if reasons else "조건 미달"
        
        analysis = {
            'signal': signal,
            'score': round(score, 2),
            'reason': reason,
            'confidence': confidence,
            'change_rate': change_rate,
            'volume': volume,
        }
        
        logger.info(f"분석 완료: {stock_code} - {signal.upper()} (점수: {score:.2f}, 신뢰도: {confidence})")
        return analysis
    
    def should_buy(self, stock_code: str, analysis: Dict[str, Any]) -> bool:
        """
        매수 여부 판단
        
        Args:
            stock_code: 종목코드
            analysis: 분석 결과
        
        Returns:
            매수 여부
        """
        if self.has_position(stock_code):
            logger.debug(f"{stock_code} 이미 보유 중")
            return False
        
        max_positions = self.get_config('max_positions', 5)
        if self.get_position_count() >= max_positions:
            logger.debug(f"최대 포지션 {max_positions}개 도달")
            return False
        
        signal = analysis.get('signal', 'hold')
        score = analysis.get('score', 0)
        
        if signal == 'buy' and score >= 5.0:
            logger.info(f"{stock_code} 매수 조건 충족 (점수: {score:.2f})")
            return True
        
        return False
    
    def should_sell(self, stock_code: str, position: Dict[str, Any]) -> bool:
        """
        매도 여부 판단
        
        Args:
            stock_code: 종목코드
            position: 포지션 정보
        
        Returns:
            매도 여부
        """
        profit_loss_rate = position.get('profit_loss_rate', 0)
        
        take_profit_rate = self.get_config('take_profit_rate', 0.10) * 100
        stop_loss_rate = self.get_config('stop_loss_rate', -0.05) * 100
        
        if profit_loss_rate >= take_profit_rate:
            logger.info(f"{stock_code} 익절 조건 충족 ({profit_loss_rate:+.2f}%)")
            return True
        
        if profit_loss_rate <= stop_loss_rate:
            logger.info(f"{stock_code} 손절 조건 충족 ({profit_loss_rate:+.2f}%)")
            return True
        
        return False
    
    def calculate_position_size(
        self,
        stock_code: str,
        current_price: int,
        available_cash: int
    ) -> int:
        포지션 크기 계산 (공통 유틸리티 사용)

        Args:
            stock_code: 종목코드
            current_price: 현재가
            available_cash: 가용 현금

        Returns:
            매수 수량
        if current_price == 0:
            return 0

        position_size_rate = self.get_config('position_size_rate', 0.20)

        quantity = calculate_position_size_by_ratio(
            capital=available_cash,
            price=current_price,
            ratio=position_size_rate,
            commission_rate=0.00015,
            min_quantity=1
        )

        invest_amount = int(available_cash * position_size_rate)
        logger.info(
            f"{stock_code} 포지션 크기 계산: "
            f"{quantity}주 (투자금액: {invest_amount:,}원)"
        )

        return quantity
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        전략 정보 조회
        
        Returns:
            전략 정보
        """
        return {
            'name': self.name,
            'description': '상승 모멘텀이 강한 종목을 매수하는 전략',
            'type': 'momentum',
            'config': self.get_all_config(),
            'statistics': self.get_statistics(),
            'positions': len(self.positions),
        }


__all__ = ['MomentumStrategy']