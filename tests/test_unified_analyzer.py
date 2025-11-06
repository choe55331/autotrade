"""
Unified Analyzer Tests
"""

import pytest
import asyncio
from ai.unified_analyzer import UnifiedAnalyzer


class TestUnifiedAnalyzer:
    """UnifiedAnalyzer 테스트"""

    @pytest.fixture
    def analyzer(self):
        """Analyzer 인스턴스"""
        return UnifiedAnalyzer()

    def test_initialization(self, analyzer):
        """초기화 테스트"""
        assert analyzer is not None
        assert isinstance(analyzer.providers, dict)

    @pytest.mark.asyncio
    async def test_mock_analysis(self, analyzer):
        """Mock 분석 테스트"""
        stock_data = {
            'stock_code': '005930',
            'stock_name': '삼성전자',
            'current_price': 70000,
            'volume': 1000000,
            'change_rate': 2.5
        }

        score_info = {
            'score': 280,
            'max_score': 440,
            'percentage': 63.6
        }

        result = await analyzer.analyze_stock(stock_data, score_info=score_info)

        assert result is not None
        assert 'signal' in result
        assert result['signal'] in ['buy', 'hold', 'sell']
        assert 'confidence' in result
        assert 0 <= result['confidence'] <= 1

    def test_prompt_building(self, analyzer):
        """프롬프트 생성 테스트"""
        stock_data = {
            'stock_code': '005930',
            'stock_name': '삼성전자',
            'current_price': 70000,
            'volume': 1000000,
            'change_rate': 2.5
        }

        prompt = analyzer._build_advanced_prompt(stock_data)

        assert prompt is not None
        assert '삼성전자' in prompt
        assert '70,000' in prompt
        assert 'signal' in prompt.lower()
