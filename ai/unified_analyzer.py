"""
Unified AI Analyzer v6.0
통합 AI 분석기 - Gemini, Claude, GPT-4 지원
고도화된 프롬프트 엔지니어링 적용
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from abc import ABC, abstractmethod

# AI Provider imports
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from anthropic import Anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

try:
    from openai import OpenAI
    GPT4_AVAILABLE = True
except ImportError:
    GPT4_AVAILABLE = False


class AIProvider(ABC):
    """AI Provider 추상 클래스"""

    @abstractmethod
    async def analyze(self, prompt: str) -> str:
        """AI 분석 실행"""
        pass


class GeminiProvider(AIProvider):
    """Gemini AI Provider"""

    def __init__(self, api_key: str):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not installed")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    async def analyze(self, prompt: str) -> str:
        response = await asyncio.to_thread(
            self.model.generate_content, prompt
        )
        return response.text


class ClaudeProvider(AIProvider):
    """Claude AI Provider"""

    def __init__(self, api_key: str):
        if not CLAUDE_AVAILABLE:
            raise ImportError("anthropic not installed")

        self.client = Anthropic(api_key=api_key)

    async def analyze(self, prompt: str) -> str:
        response = await asyncio.to_thread(
            self.client.messages.create,
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text


class GPT4Provider(AIProvider):
    """GPT-4 AI Provider"""

    def __init__(self, api_key: str):
        if not GPT4_AVAILABLE:
            raise ImportError("openai not installed")

        self.client = OpenAI(api_key=api_key)

    async def analyze(self, prompt: str) -> str:
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content


class UnifiedAnalyzer:
    """
    통합 AI 분석기

    Features:
    - 3개 AI 모델 지원 (Gemini, Claude, GPT-4)
    - 앙상블 분석 (다중 모델 투표)
    - 고도화된 프롬프트 엔지니어링
    - 컨텍스트 기반 분석 (RAG 준비)
    """

    def __init__(self):
        self.providers: Dict[str, AIProvider] = {}
        self.default_provider = None
        self._initialize_providers()

    def _initialize_providers(self):
        """AI Provider 초기화"""

        # Gemini
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key and GEMINI_AVAILABLE:
            try:
                self.providers['gemini'] = GeminiProvider(gemini_key)
                if not self.default_provider:
                    self.default_provider = 'gemini'
                print("✓ Gemini AI initialized")
            except Exception as e:
                print(f"⚠️ Gemini initialization failed: {e}")

        # Claude
        claude_key = os.getenv('ANTHROPIC_API_KEY')
        if claude_key and CLAUDE_AVAILABLE:
            try:
                self.providers['claude'] = ClaudeProvider(claude_key)
                if not self.default_provider:
                    self.default_provider = 'claude'
                print("✓ Claude AI initialized")
            except Exception as e:
                print(f"⚠️ Claude initialization failed: {e}")

        # GPT-4
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and GPT4_AVAILABLE:
            try:
                self.providers['gpt4'] = GPT4Provider(openai_key)
                if not self.default_provider:
                    self.default_provider = 'gpt4'
                print("✓ GPT-4 initialized")
            except Exception as e:
                print(f"⚠️ GPT-4 initialization failed: {e}")

        if not self.providers:
            print("⚠️ No AI providers available - using Mock")

    def _build_advanced_prompt(
        self,
        stock_data: Dict[str, Any],
        score_info: Optional[Dict[str, Any]] = None,
        portfolio_info: Optional[str] = None,
        market_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """고도화된 프롬프트 생성"""

        stock_code = stock_data.get('stock_code', 'N/A')
        stock_name = stock_data.get('stock_name', 'N/A')
        current_price = stock_data.get('current_price', 0)
        change_rate = stock_data.get('change_rate', 0)
        volume = stock_data.get('volume', 0)

        prompt = f"""
당신은 20년 경력의 퀀트 트레이더입니다. 다음 종목을 종합적으로 분석하여 매수 여부를 결정하세요.

## 종목 정보
- 종목명: {stock_name} ({stock_code})
- 현재가: {current_price:,}원
- 변동률: {change_rate:+.2f}%
- 거래량: {volume:,}주

## 시장 데이터
"""

        # 기관/외국인 매매 데이터
        inst_buy = stock_data.get('institutional_net_buy', 0)
        foreign_buy = stock_data.get('foreign_net_buy', 0)
        if inst_buy or foreign_buy:
            prompt += f"""
### 투자자별 매매동향
- 기관 순매수: {inst_buy:,}원
- 외국인 순매수: {foreign_buy:,}원
"""

        # 호가 데이터
        bid_ask_ratio = stock_data.get('bid_ask_ratio', 0)
        if bid_ask_ratio:
            prompt += f"""
### 호가 분석
- 매수/매도 호가 비율: {bid_ask_ratio:.2f}
"""

        # 스코어링 정보
        if score_info:
            total_score = score_info.get('score', 0)
            max_score = score_info.get('max_score', 440)
            percentage = score_info.get('percentage', 0)

            prompt += f"""
## 정량적 평가 (10가지 기준, {max_score}점 만점)
- 총점: {total_score:.0f}점 / {max_score}점 ({percentage:.1f}%)

### 점수 분포:
"""
            breakdown = score_info.get('breakdown', {})
            for criterion, score in breakdown.items():
                if score > 0:
                    prompt += f"- {criterion}: {score:.0f}점\n"

        # 포트폴리오 정보
        if portfolio_info and portfolio_info != "No positions":
            prompt += f"""
## 현재 포트폴리오
{portfolio_info}
"""

        # 시장 컨텍스트
        if market_context:
            kospi = market_context.get('kospi', 0)
            market_trend = market_context.get('trend', 'neutral')
            volatility = market_context.get('volatility', 'normal')

            prompt += f"""
## 시장 상황
- KOSPI: {kospi:,.2f}
- 시장 추세: {market_trend}
- 변동성: {volatility}
"""

        # 분석 요청
        prompt += """

## 분석 요청

다음 3가지 시나리오를 분석하세요:

### 1. 낙관적 시나리오 (확률: %)
- 예상 상승폭:
- 주요 긍정 요인:
- 목표가:

### 2. 중립적 시나리오 (확률: %)
- 예상 변동폭:
- 현재 가격 유지 요인:

### 3. 비관적 시나리오 (확률: %)
- 예상 하락폭:
- 주요 리스크:
- 손절가:

## 최종 판단

다음 형식으로 답변하세요:

```json
{
  "signal": "buy" | "hold" | "sell",
  "confidence": 0.0 ~ 1.0,
  "entry_price": 구체적인 진입 가격,
  "exit_price": 구체적인 청산 가격,
  "stop_loss": 구체적인 손절 가격,
  "position_size": "small" | "medium" | "large",
  "reasons": ["이유 1", "이유 2", "이유 3"],
  "risks": ["리스크 1", "리스크 2"],
  "scenarios": {
    "optimistic": {"probability": 0.3, "target": 75000},
    "neutral": {"probability": 0.5, "target": 70000},
    "pessimistic": {"probability": 0.2, "target": 65000}
  },
  "analysis_text": "상세 분석 텍스트"
}
```

JSON 형식을 정확히 지켜주세요.
"""

        return prompt

    async def analyze_stock(
        self,
        stock_data: Dict[str, Any],
        score_info: Optional[Dict[str, Any]] = None,
        portfolio_info: Optional[str] = None,
        market_context: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None,
        ensemble: bool = False
    ) -> Dict[str, Any]:
        """
        종목 분석

        Args:
            stock_data: 종목 데이터
            score_info: 스코어링 정보
            portfolio_info: 포트폴리오 정보
            market_context: 시장 컨텍스트
            provider: AI 제공자 ('gemini', 'claude', 'gpt4', None=기본값)
            ensemble: 앙상블 모드 (다중 모델 투표)

        Returns:
            분석 결과
        """

        if not self.providers:
            # Mock 분석 (AI 없을 때)
            return self._mock_analysis(stock_data, score_info)

        prompt = self._build_advanced_prompt(
            stock_data, score_info, portfolio_info, market_context
        )

        if ensemble and len(self.providers) > 1:
            # 앙상블 분석 (다중 모델)
            return await self._ensemble_analyze(prompt)
        else:
            # 단일 모델 분석
            provider_name = provider or self.default_provider
            if provider_name not in self.providers:
                provider_name = self.default_provider

            return await self._single_analyze(prompt, provider_name)

    async def _single_analyze(self, prompt: str, provider_name: str) -> Dict[str, Any]:
        """단일 모델 분석"""

        try:
            provider = self.providers[provider_name]
            response_text = await provider.analyze(prompt)

            # JSON 파싱
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                result = json.loads(json_str)
                result['provider'] = provider_name
                result['raw_response'] = response_text
                return result
            else:
                # JSON 파싱 실패
                return self._fallback_parse(response_text, provider_name)

        except Exception as e:
            print(f"❌ {provider_name} analysis failed: {e}")
            return self._mock_analysis({}, None)

    async def _ensemble_analyze(self, prompt: str) -> Dict[str, Any]:
        """앙상블 분석 (다중 모델 투표)"""

        tasks = [
            self._single_analyze(prompt, name)
            for name in self.providers.keys()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 예외 제거
        valid_results = [r for r in results if isinstance(r, dict)]

        if not valid_results:
            return self._mock_analysis({}, None)

        # 투표
        buy_votes = sum(1 for r in valid_results if r.get('signal') == 'buy')
        hold_votes = sum(1 for r in valid_results if r.get('signal') == 'hold')
        sell_votes = sum(1 for r in valid_results if r.get('signal') == 'sell')

        total_votes = len(valid_results)

        # 최종 신호
        if buy_votes >= total_votes / 2:
            final_signal = 'buy'
        elif sell_votes >= total_votes / 2:
            final_signal = 'sell'
        else:
            final_signal = 'hold'

        # 평균 신뢰도
        avg_confidence = sum(r.get('confidence', 0.5) for r in valid_results) / total_votes

        return {
            'signal': final_signal,
            'confidence': avg_confidence,
            'ensemble': True,
            'votes': {
                'buy': buy_votes,
                'hold': hold_votes,
                'sell': sell_votes
            },
            'models': [r.get('provider') for r in valid_results],
            'individual_results': valid_results,
            'analysis_text': f"앙상블 분석 ({total_votes}개 모델): {final_signal.upper()}"
        }

    def _fallback_parse(self, response_text: str, provider_name: str) -> Dict[str, Any]:
        """JSON 파싱 실패 시 폴백"""

        signal = 'hold'
        if 'buy' in response_text.lower() or '매수' in response_text:
            signal = 'buy'
        elif 'sell' in response_text.lower() or '매도' in response_text:
            signal = 'sell'

        return {
            'signal': signal,
            'confidence': 0.5,
            'reasons': ['AI 분석 결과 (텍스트)'],
            'risks': [],
            'analysis_text': response_text,
            'provider': provider_name,
            'parsing_failed': True
        }

    def _mock_analysis(self, stock_data: Dict[str, Any], score_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock 분석 (AI 없을 때)"""

        score = score_info.get('score', 0) if score_info else 0

        if score >= 280:
            signal = 'buy'
            confidence = 0.8
        elif score >= 200:
            signal = 'hold'
            confidence = 0.6
        else:
            signal = 'hold'
            confidence = 0.4

        return {
            'signal': signal,
            'confidence': confidence,
            'reasons': [f'점수 기반 판단 ({score:.0f}점)'],
            'risks': ['AI 분석 미사용'],
            'analysis_text': f'Mock 분석: {signal.upper()} (점수: {score:.0f})',
            'provider': 'mock'
        }

    def initialize(self) -> bool:
        """호환성을 위한 초기화 메서드"""
        return len(self.providers) > 0 or True  # Mock도 지원


# 싱글톤 인스턴스
_unified_analyzer_instance = None


def get_unified_analyzer() -> UnifiedAnalyzer:
    """통합 Analyzer 싱글톤 인스턴스 반환"""
    global _unified_analyzer_instance
    if _unified_analyzer_instance is None:
        _unified_analyzer_instance = UnifiedAnalyzer()
    return _unified_analyzer_instance
