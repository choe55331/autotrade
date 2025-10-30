"""
config/trading_params.py
매매 전략 파라미터
"""
from typing import Dict, Any

# 포지션 관리
POSITION_CONFIG = {
    'MAX_OPEN_POSITIONS': 5,
    'RISK_PER_TRADE_RATIO': 0.20,  # 거래당 리스크 비율 (20%)
}

# 손익 관리
PROFIT_LOSS_CONFIG = {
    'TAKE_PROFIT_RATIO': 0.10,  # 목표 수익률 (10%)
    'STOP_LOSS_RATIO': -0.05,   # 손절 비율 (-5%)
    'TRAILING_STOP_ENABLED': False,
    'TRAILING_STOP_RATIO': 0.03,  # 트레일링 스톱 비율 (3%)
}

# 종목 필터링
FILTER_CONFIG = {
    'FILTER_MIN_PRICE': 1000,      # 최소 주가
    'FILTER_MAX_PRICE': 1000000,   # 최대 주가
    'FILTER_MIN_VOLUME': 100000,   # 최소 거래량
    'FILTER_MIN_RATE': 1.0,        # 최소 등락률 (%)
    'FILTER_MAX_RATE': 15.0,       # 최대 등락률 (%)
    'FILTER_MIN_MARKET_CAP': 0,    # 최소 시가총액 (억원)
}

# AI 분석 설정
AI_CONFIG = {
    'AI_ANALYSIS_ENABLED': True,
    'AI_MIN_ANALYSIS_SCORE': 7.0,
    'AI_CONFIDENCE_THRESHOLD': 'Medium',  # Low, Medium, High
    'AI_MARKET_ANALYSIS_INTERVAL': 5,     # 분
    'AI_ADJUST_FILTERS_AUTOMATICALLY': False,
}

# 통합 매매 파라미터
TRADING_PARAMS: Dict[str, Any] = {
    **POSITION_CONFIG,
    **PROFIT_LOSS_CONFIG,
    **FILTER_CONFIG,
    **AI_CONFIG,
}

def validate_trading_params() -> tuple[bool, list[str]]:
    """
    매매 파라미터 유효성 검증
    
    Returns:
        (is_valid, errors): 유효성 여부와 오류 목록
    """
    errors = []
    
    # 포지션 관리 검증
    if not (1 <= POSITION_CONFIG['MAX_OPEN_POSITIONS'] <= 50):
        errors.append("MAX_OPEN_POSITIONS는 1~50 사이여야 합니다")
    
    if not (0 < POSITION_CONFIG['RISK_PER_TRADE_RATIO'] <= 1.0):
        errors.append("RISK_PER_TRADE_RATIO는 0~1 사이여야 합니다")
    
    # 손익 관리 검증
    if not (-1.0 <= PROFIT_LOSS_CONFIG['STOP_LOSS_RATIO'] < 0):
        errors.append("STOP_LOSS_RATIO는 -1~0 사이여야 합니다")
    
    if not (0 < PROFIT_LOSS_CONFIG['TAKE_PROFIT_RATIO'] <= 1.0):
        errors.append("TAKE_PROFIT_RATIO는 0~1 사이여야 합니다")
    
    # 필터 검증
    if FILTER_CONFIG['FILTER_MIN_PRICE'] < 0:
        errors.append("FILTER_MIN_PRICE는 0 이상이어야 합니다")
    
    if FILTER_CONFIG['FILTER_MIN_VOLUME'] < 0:
        errors.append("FILTER_MIN_VOLUME은 0 이상이어야 합니다")
    
    if not (-30.0 <= FILTER_CONFIG['FILTER_MIN_RATE'] <= 30.0):
        errors.append("FILTER_MIN_RATE는 -30~30 사이여야 합니다")
    
    if not (-30.0 <= FILTER_CONFIG['FILTER_MAX_RATE'] <= 30.0):
        errors.append("FILTER_MAX_RATE는 -30~30 사이여야 합니다")
    
    # AI 설정 검증
    if not (0.0 <= AI_CONFIG['AI_MIN_ANALYSIS_SCORE'] <= 10.0):
        errors.append("AI_MIN_ANALYSIS_SCORE는 0~10 사이여야 합니다")
    
    if AI_CONFIG['AI_CONFIDENCE_THRESHOLD'] not in ['Low', 'Medium', 'High']:
        errors.append("AI_CONFIDENCE_THRESHOLD는 'Low', 'Medium', 'High' 중 하나여야 합니다")
    
    return len(errors) == 0, errors

def get_trading_params_summary() -> str:
    """매매 파라미터 요약 문자열 반환"""
    return f"""
    === 매매 파라미터 ===
    최대 포지션: {POSITION_CONFIG['MAX_OPEN_POSITIONS']}개
    거래당 리스크: {POSITION_CONFIG['RISK_PER_TRADE_RATIO']*100:.1f}%
    목표 수익률: {PROFIT_LOSS_CONFIG['TAKE_PROFIT_RATIO']*100:.1f}%
    손절 비율: {PROFIT_LOSS_CONFIG['STOP_LOSS_RATIO']*100:.1f}%
    
    필터링:
    - 주가: {FILTER_CONFIG['FILTER_MIN_PRICE']:,}원 ~ {FILTER_CONFIG['FILTER_MAX_PRICE']:,}원
    - 거래량: {FILTER_CONFIG['FILTER_MIN_VOLUME']:,}주 이상
    - 등락률: {FILTER_CONFIG['FILTER_MIN_RATE']:.1f}% ~ {FILTER_CONFIG['FILTER_MAX_RATE']:.1f}%
    
    AI 분석: {'활성' if AI_CONFIG['AI_ANALYSIS_ENABLED'] else '비활성'}
    - 최소 점수: {AI_CONFIG['AI_MIN_ANALYSIS_SCORE']:.1f}점
    - 신뢰도: {AI_CONFIG['AI_CONFIDENCE_THRESHOLD']}
    """

__all__ = [
    'TRADING_PARAMS',
    'POSITION_CONFIG',
    'PROFIT_LOSS_CONFIG',
    'FILTER_CONFIG',
    'AI_CONFIG',
    'validate_trading_params',
    'get_trading_params_summary',
]