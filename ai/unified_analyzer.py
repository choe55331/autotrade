"""
Unified AI Analyzer v6.1
통합 AI 분석기 - Gemini 전용 (최적화)
고도화된 프롬프트 엔지니어링 적용
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from abc import ABC, abstractmethod

# AI Provider imports (Gemini only)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AIProvider(ABC):
    """AI Provider 추상 클래스"""

    @abstractmethod
    async def analyze(self, prompt: str) -> str:
        """AI 분석 실행"""
        pass


class GeminiProvider(AIProvider):
    """Gemini AI Provider - Primary and Only AI Provider"""

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


class UnifiedAnalyzer:
    """
    통합 AI 분석기 (Gemini 전용)

    Features:
    - Gemini Pro 모델 사용
    - 고도화된 프롬프트 엔지니어링
    - 컨텍스트 기반 분석
    - 자동 폴백 (Mock 분석)
    """

    def __init__(self):
        self.providers: Dict[str, AIProvider] = {}
        self.default_provider = 'gemini'
        self._initialize_providers()

    def _initialize_providers(self):
        """AI Provider 초기화 (Gemini만 사용)"""

        # Gemini (Primary and Only Provider)
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key and GEMINI_AVAILABLE:
            try:
                self.providers['gemini'] = GeminiProvider(gemini_key)
                self.default_provider = 'gemini'
                print("✓ Gemini AI initialized (Primary Provider)")
            except Exception as e:
                print(f"⚠️ Gemini initialization failed: {e}")
                print("⚠️ Falling back to Mock analyzer")
        else:
            print("⚠️ Gemini API key not found - using Mock analyzer")

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

        # 분석 요청 (고도화된 프롬프트 - v6.2)
        prompt += """

## 분석 요청 (심층 분석)

### STEP 1: 3가지 시나리오 분석

#### 1. 낙관적 시나리오 (확률: %)
- 예상 상승폭: (%, 목표가)
- 주요 긍정 요인: (3가지 이상, 구체적으로)
- 상승 지속 근거: (데이터 기반)
- 목표가 달성 기간: (예상 일수)

#### 2. 중립적 시나리오 (확률: %)
- 예상 변동폭: (±%)
- 현재 가격 유지 요인: (균형 요인 분석)
- 관망 필요 기간:

#### 3. 비관적 시나리오 (확률: %)
- 예상 하락폭: (%, 손절가)
- 주요 리스크: (3가지 이상, 구체적으로)
- 하락 트리거: (어떤 이벤트/지표가 하락을 유발하는가)
- 손절가 근거:

### STEP 2: 신뢰도 자가 평가

다음 기준으로 분석의 신뢰도를 평가하세요:

1. **데이터 충분성** (0~100점)
   - 제공된 데이터가 충분한가?
   - 추가 필요 데이터는?

2. **시장 투명성** (0~100점)
   - 해당 종목의 거래가 투명한가?
   - 작전 세력 가능성은?

3. **추세 명확성** (0~100점)
   - 가격 추세가 명확한가?
   - 혼조세/박스권인가?

4. **시기 적정성** (0~100점)
   - 지금이 진입 타이밍인가?
   - 더 기다려야 하는가?

5. **리스크-리워드 비율**
   - 기대 수익: 손실 위험 = ?:?
   - 비율이 최소 2:1 이상인가?

**종합 신뢰도 점수**: (5가지 평균) / 100

### STEP 3: 최종 판단

다음 형식으로 답변하세요 (JSON 형식 엄수):

```json
{
  "signal": "buy" | "hold" | "sell",
  "confidence": 0.0 ~ 1.0,
  "reliability_score": 0 ~ 100,
  "reliability_breakdown": {
    "data_sufficiency": 0~100,
    "market_transparency": 0~100,
    "trend_clarity": 0~100,
    "timing_appropriateness": 0~100,
    "risk_reward_ratio": "예: 3:1"
  },
  "entry_price": 구체적인 진입 가격,
  "entry_timing": "즉시" | "조정 대기" | "추가 관찰 필요",
  "exit_price": 구체적인 청산 가격,
  "stop_loss": 구체적인 손절 가격,
  "position_size": "small" | "medium" | "large",
  "reasons": ["이유 1 (구체적으로)", "이유 2 (데이터 기반)", "이유 3 (정량적)"],
  "risks": ["리스크 1 (발생 확률 포함)", "리스크 2", "리스크 3"],
  "scenarios": {
    "optimistic": {"probability": 0.0~1.0, "target": 목표가, "timeline_days": 일수},
    "neutral": {"probability": 0.0~1.0, "target": 현재가 유지, "timeline_days": 일수},
    "pessimistic": {"probability": 0.0~1.0, "target": 손절가, "timeline_days": 일수}
  },
  "data_gaps": ["부족한 데이터 1", "부족한 데이터 2"],
  "confidence_rationale": "confidence와 reliability_score가 이 값인 이유를 2~3문장으로 설명",
  "analysis_text": "종합 분석 (시나리오별 확률 근거, 리스크-리워드 평가 포함)"
}
```

**중요**:
- confidence는 AI 자신의 확신도 (모델의 자신감)
- reliability_score는 분석의 객관적 신뢰도 (데이터/시장 상황 기반)
- 두 값은 다를 수 있음 (예: confidence 0.8이어도 reliability_score 60점 가능)
- JSON 형식을 정확히 지켜주세요.
"""

        return prompt

    async def analyze_stock(
        self,
        stock_data: Dict[str, Any],
        score_info: Optional[Dict[str, Any]] = None,
        portfolio_info: Optional[str] = None,
        market_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        종목 분석 (Gemini 전용)

        Args:
            stock_data: 종목 데이터
            score_info: 스코어링 정보
            portfolio_info: 포트폴리오 정보
            market_context: 시장 컨텍스트

        Returns:
            분석 결과
        """

        if not self.providers:
            # Mock 분석 (AI 없을 때)
            return self._mock_analysis(stock_data, score_info)

        prompt = self._build_advanced_prompt(
            stock_data, score_info, portfolio_info, market_context
        )

        # Gemini 분석 실행
        return await self._single_analyze(prompt, 'gemini')

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
