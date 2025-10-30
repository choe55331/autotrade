"""
ai 패키지
AI 분석 모듈
"""
from .base_analyzer import BaseAnalyzer
from .gemini_analyzer import GeminiAnalyzer
from .mock_analyzer import MockAnalyzer

def get_analyzer(analyzer_type: str = 'gemini', **kwargs):
    """
    분석기 팩토리 함수
    
    Args:
        analyzer_type: 'gemini' | 'mock'
        **kwargs: 분석기 초기화 파라미터
    
    Returns:
        분석기 인스턴스
    """
    if analyzer_type.lower() == 'gemini':
        return GeminiAnalyzer(**kwargs)
    elif analyzer_type.lower() == 'mock':
        return MockAnalyzer(**kwargs)
    else:
        raise ValueError(f"Unknown analyzer type: {analyzer_type}")

__all__ = [
    'BaseAnalyzer',
    'GeminiAnalyzer',
    'MockAnalyzer',
    'get_analyzer',
]