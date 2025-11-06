"""
ai/gemini_analyzer.py
Google Gemini AI 분석기
"""
import logging
import time
from typing import Dict, Any, Optional
from .base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)


class GeminiAnalyzer(BaseAnalyzer):
    """
    Google Gemini AI 분석기

    Gemini API를 사용한 종목/시장 분석
    """

    # 종목 분석 프롬프트 템플릿 (v5.10 - ENHANCED)
    STOCK_ANALYSIS_PROMPT_TEMPLATE = """# 🎯 PROFESSIONAL QUANTITATIVE TRADING ANALYSIS REQUEST (v5.10)

당신은 20년 이상의 경력을 가진 퀀트 헤지펀드 매니저이자 리스크 관리 전문가입니다.
다음 한국 주식에 대한 심층 분석을 수행해주세요.

## 📊 STOCK IDENTIFICATION
**종목**: {stock_name} ({stock_code})
**현재가**: {current_price:,}원
**등락률**: {change_rate:+.2f}%
**거래량**: {volume:,}주

## 🔢 QUANTITATIVE SCORING SYSTEM (440점 만점)
**종합 점수**: {score}/440점 ({percentage:.1f}%)

### 세부 점수 분석 (10개 지표):
{score_breakdown_detailed}

**점수 해석 가이드**:
- 350점 이상 (80%+): S등급 - 매우 강력한 매수 신호
- 300-349점 (68-79%): A등급 - 강력한 매수 신호
- 250-299점 (57-68%): B등급 - 긍정적 신호
- 200-249점 (45-56%): C등급 - 중립
- 200점 미만 (45%-): D/F등급 - 부정적 신호

## 💰 INVESTOR FLOW ANALYSIS (스마트머니 추적)
**기관 순매수**: {institutional_net_buy:,}원
**외국인 순매수**: {foreign_net_buy:,}원
**매수호가 강도**: {bid_ask_ratio:.2f}

**투자자 흐름 해석**:
- 외국인+기관 동시 순매수 = 강력한 상승 신호
- 외국인 순매도 + 개인 순매수 = 경고 신호
- 매수호가강도 > 1.5 = 강한 매수세
- 매수호가강도 < 0.7 = 강한 매도세

## 📈 CURRENT PORTFOLIO CONTEXT
{portfolio_info}

---

## 🎓 REQUIRED COMPREHENSIVE ANALYSIS

### 1. TECHNICAL SCORE VALIDATION (점수 타당성 분석)
- 10가지 세부 점수를 개별적으로 평가
- 각 점수가 실제 시장 상황과 부합하는지 검증
- 과대평가되었거나 과소평가된 지표 식별
- 점수의 신뢰도 평가 (0-100%)

### 2. SMART MONEY FLOW ANALYSIS (스마트머니 흐름)
- 기관/외국인 매매 패턴 해석
- 개인 vs 기관/외국인 포지션 비교
- 누적 매수/매도 흐름 분석
- 스마트머니가 보내는 신호 해독

### 3. PRICE ACTION & MOMENTUM (가격 행동 분석)
- 단기 급등 vs 추세 전환 vs 조정 후 재상승 구분
- 현재 모멘텀의 지속 가능성 평가
- 과매수/과매도 상태 판단
- 변동성 분석 및 예상 가격 범위

### 4. RISK-REWARD ASSESSMENT (위험-보상 분석)
**주요 리스크 요인**:
- 기술적 리스크 (저항선, 지지선 이탈 가능성)
- 펀더멘털 리스크 (밸류에이션, 업종 리스크)
- 시장 리스크 (전체 시장 약세, 변동성 확대)
- 유동성 리스크
- 이벤트 리스크 (실적 발표, 규제 등)

**예상 시나리오**:
- 🐂 Bull Case (확률 ___%): [상승 시나리오]
- 📊 Base Case (확률 ___%): [기본 시나리오]
- 🐻 Bear Case (확률 ___%): [하락 시나리오]

### 5. TRADING STRATEGY (구체적 매매 전략)
**진입 전략**:
- 즉시 매수 vs 대기 vs 분할 매수
- 최적 진입 가격 및 타이밍
- 포지션 크기 권장 (포트폴리오 대비 %)

**리스크 관리**:
- 손절가 설정 (가격 및 근거)
- 익절 목표가 (1차, 2차, 3차)
- 최대 보유 기간
- 손익비 (Risk-Reward Ratio)

### 6. PROBABILITY ASSESSMENT (확률 기반 평가)
- 수익 확률: ___%
- 손실 확률: ___%
- 기대 수익률: ___% (확률 가중 평균)
- 최대 손실 예상: ___%

---

## 📋 REQUIRED OUTPUT FORMAT (JSON 형식):

```json
{
  "signal": "STRONG_BUY" | "BUY" | "WEAK_BUY" | "HOLD" | "WEAK_SELL" | "SELL" | "STRONG_SELL",
  "confidence_level": "Very High" | "High" | "Medium" | "Low" | "Very Low",
  "overall_score": <0-10 with 0.1 precision>,

  "score_validation": {
    "is_score_reliable": true | false,
    "score_confidence": <0-100 percentage>,
    "overvalued_indicators": ["indicator1", ...],
    "undervalued_indicators": ["indicator1", ...],
    "key_score_drivers": ["driver1", "driver2", "driver3"]
  },

  "investor_flow_signal": {
    "institutional_sentiment": "Strong Buy" | "Buy" | "Neutral" | "Sell" | "Strong Sell",
    "foreign_sentiment": "Strong Buy" | "Buy" | "Neutral" | "Sell" | "Strong Sell",
    "smart_money_signal": "Strong Accumulation" | "Accumulation" | "Neutral" | "Distribution" | "Strong Distribution",
    "flow_confidence": <0-100>
  },

  "price_action_analysis": {
    "pattern": "Sharp Rally" | "Trend Reversal" | "Post-Correction Rally" | "Consolidation" | "Breakdown",
    "momentum_sustainability": "Very High" | "High" | "Medium" | "Low" | "Very Low",
    "overbought_oversold": "Severely Overbought" | "Overbought" | "Neutral" | "Oversold" | "Severely Oversold",
    "expected_price_range_7d": {"low": <price>, "high": <price>}
  },

  "risk_analysis": {
    "overall_risk": "Very Low" | "Low" | "Medium" | "High" | "Very High",
    "key_risks": [
      {"type": "technical|fundamental|market|liquidity|event", "description": "...", "severity": <1-10>}
    ],
    "risk_mitigation": ["action1", "action2"]
  },

  "scenario_analysis": {
    "bull_case": {"probability": <0-100>, "description": "...", "target_price": <price>},
    "base_case": {"probability": <0-100>, "description": "...", "target_price": <price>},
    "bear_case": {"probability": <0-100>, "description": "...", "target_price": <price>}
  },

  "trading_plan": {
    "entry_strategy": "Immediate" | "Wait for Pullback" | "Wait for Breakout" | "Avoid",
    "position_size_pct": <0-100, as % of portfolio>,
    "entry_prices": [
      {"percentage": <%, e.g. 40>, "price": <price>, "condition": "Market/Limit/-2%/-4%"}
    ],
    "stop_loss": <price>,
    "take_profit_targets": [
      {"percentage_to_sell": <%, e.g. 30>, "price": <price>, "rationale": "..."}
    ],
    "max_holding_days": <number or null>,
    "risk_reward_ratio": <number>
  },

  "probability_metrics": {
    "success_probability": <0-100>,
    "loss_probability": <0-100>,
    "expected_return": <percentage, probability-weighted>,
    "max_drawdown_estimate": <percentage>
  },

  "key_insights": [
    "Most critical insight #1",
    "Most critical insight #2",
    "Most critical insight #3"
  ],

  "warnings": [
    "Critical warning #1",
    "Critical warning #2"
  ],

  "detailed_reasoning": "<3-5 paragraph comprehensive analysis covering all aspects>",

  "analyst_conviction": "Very High" | "High" | "Medium" | "Low" | "Very Low"
}
```

## ⚠️ CRITICAL ANALYSIS GUIDELINES:

1. **Be Brutally Honest**: Don't sugarcoat risks or force a bullish view
2. **Probabilistic Thinking**: Express everything in probabilities, not certainties
3. **Risk-First Mindset**: Always assess downside before upside
4. **Contrarian Awareness**: Question if the market is overreacting or underreacting
5. **Evidence-Based**: Root all conclusions in the actual data provided
6. **Actionable**: Provide specific, executable trading recommendations
7. **Intellectual Honesty**: If signals are mixed or data insufficient, say "HOLD - Insufficient Edge"

**특히 중요**: 점수가 높다고 무조건 매수 추천하지 말 것. 스마트머니 흐름과 가격 액션을 종합적으로 고려할 것."""

    def __init__(self, api_key: str = None, model_name: str = None):
        """
        Gemini 분석기 초기화

        Args:
            api_key: Gemini API 키
            model_name: 모델 이름 (기본: gemini-2.5-flash)
        """
        super().__init__("GeminiAnalyzer")

        # API 설정
        if api_key is None:
            from config import GEMINI_API_KEY, GEMINI_MODEL_NAME
            self.api_key = GEMINI_API_KEY
            self.model_name = model_name or GEMINI_MODEL_NAME or 'gemini-2.5-flash'
        else:
            self.api_key = api_key
            self.model_name = model_name or 'gemini-2.5-flash'

        self.model = None

        # v5.7.5: AI 분석 TTL 캐시 (5분)
        self._analysis_cache = {}
        self._cache_ttl = 300  # 5분 (초)

        logger.info(f"GeminiAnalyzer 초기화 (모델: {self.model_name})")
    
    def initialize(self) -> bool:
        """
        Gemini API 초기화
        
        Returns:
            초기화 성공 여부
        """
        try:
            import google.generativeai as genai
            
            # API 키 설정
            genai.configure(api_key=self.api_key)
            
            # 모델 생성
            self.model = genai.GenerativeModel(self.model_name)
            
            self.is_initialized = True
            logger.info("Gemini API 초기화 성공")
            return True
            
        except ImportError:
            logger.error("google-generativeai 패키지가 설치되지 않았습니다")
            logger.error("pip install google-generativeai 실행 필요")
            return False
        except Exception as e:
            logger.error(f"Gemini API 초기화 실패: {e}")
            return False
    
    def analyze_stock(
        self,
        stock_data: Dict[str, Any],
        analysis_type: str = 'comprehensive',
        score_info: Dict[str, Any] = None,
        portfolio_info: str = None
    ) -> Dict[str, Any]:
        """
        종목 분석

        Args:
            stock_data: 종목 데이터
            analysis_type: 분석 유형
            score_info: 점수 정보 (score, percentage, breakdown)
            portfolio_info: 현재 포트폴리오 정보

        Returns:
            분석 결과
        """
        # 초기화 확인
        if not self.is_initialized:
            if not self.initialize():
                return self._get_error_result("분석기 초기화 실패")

        # 데이터 검증
        is_valid, msg = self.validate_stock_data(stock_data)
        if not is_valid:
            return self._get_error_result(msg)

        # v5.7.5: 캐시 확인 (종목코드 + 점수 기준)
        stock_code = stock_data.get('stock_code', '')
        score = score_info.get('score', 0) if score_info else 0
        cache_key = f"{stock_code}_{int(score)}"  # 점수는 정수로 (소수점 무시)

        # 캐시에서 조회
        if cache_key in self._analysis_cache:
            cached_entry = self._analysis_cache[cache_key]
            cached_time = cached_entry['timestamp']
            cached_result = cached_entry['result']

            # TTL 체크
            if (time.time() - cached_time) < self._cache_ttl:
                logger.info(f"AI 분석 캐시 히트: {stock_code} (캐시 유효시간: {int(self._cache_ttl - (time.time() - cached_time))}초)")
                print(f"   💾 AI 분석 캐시 사용 (캐시 유효: {int(self._cache_ttl - (time.time() - cached_time))}초)")
                return cached_result
            else:
                # TTL 만료 - 캐시 삭제
                del self._analysis_cache[cache_key]
                logger.info(f"AI 분석 캐시 만료: {stock_code}")

        # 분석 시작
        start_time = time.time()

        # 재시도 로직 (최대 3회)
        max_retries = 3
        retry_delay = 2  # 초

        for attempt in range(max_retries):
            try:
                # 점수 정보 포맷팅
                if score_info:
                    score = score_info.get('score', 0)
                    percentage = score_info.get('percentage', 0)
                    breakdown = score_info.get('breakdown', {})
                    # 10가지 세부 점수 상세 표시
                    score_breakdown_detailed = "\n".join([
                        f"  {k}: {v:.1f}점" for k, v in breakdown.items() if v >= 0
                    ])
                else:
                    score = 0
                    percentage = 0
                    score_breakdown_detailed = "  점수 정보 없음"

                # 포트폴리오 정보 (없으면 기본 메시지)
                portfolio_text = portfolio_info or "보유 종목 없음"

                # 투자자 동향 데이터
                institutional_net_buy = stock_data.get('institutional_net_buy', 0)
                foreign_net_buy = stock_data.get('foreign_net_buy', 0)
                bid_ask_ratio = stock_data.get('bid_ask_ratio', 1.0)

                # 프롬프트 템플릿 사용
                prompt = self.STOCK_ANALYSIS_PROMPT_TEMPLATE.format(
                    stock_name=stock_data.get('stock_name', ''),
                    stock_code=stock_data.get('stock_code', ''),
                    current_price=stock_data.get('current_price', 0),
                    change_rate=stock_data.get('change_rate', 0.0),
                    volume=stock_data.get('volume', 0),
                    score=score,
                    percentage=percentage,
                    score_breakdown_detailed=score_breakdown_detailed,
                    institutional_net_buy=institutional_net_buy,
                    foreign_net_buy=foreign_net_buy,
                    bid_ask_ratio=bid_ask_ratio,
                    portfolio_info=portfolio_text
                )

                # Gemini API 호출 - 타임아웃 30초 설정
                # safety_settings 없이 호출 (기본값 사용)
                try:
                    response = self.model.generate_content(
                        prompt,
                        request_options={'timeout': 30}  # 30초 타임아웃
                    )
                except Exception as timeout_error:
                    # 타임아웃이나 API 에러 발생 시 재시도
                    raise ValueError(f"Gemini API timeout or error: {timeout_error}")

                # 응답 검증 (finish_reason 체크)
                if not response.candidates:
                    raise ValueError("Gemini API returned no candidates")

                candidate = response.candidates[0]
                finish_reason = candidate.finish_reason

                # finish_reason: 1=STOP(정상), 2=SAFETY(안전필터), 3=MAX_TOKENS, 4=RECITATION, 5=OTHER
                if finish_reason != 1:  # 1 = STOP (정상 완료)
                    reason_map = {2: "SAFETY", 3: "MAX_TOKENS", 4: "RECITATION", 5: "OTHER"}
                    reason_name = reason_map.get(finish_reason, f"UNKNOWN({finish_reason})")
                    raise ValueError(f"Gemini blocked: {reason_name}")

                # 응답 파싱
                result = self._parse_stock_analysis_response(response.text, stock_data)

                # v5.7.5: 캐시에 저장
                self._analysis_cache[cache_key] = {
                    'timestamp': time.time(),
                    'result': result
                }
                logger.info(f"AI 분석 결과 캐시 저장: {stock_code} (TTL: {self._cache_ttl}초)")

                # 통계 업데이트
                elapsed_time = time.time() - start_time
                self.update_statistics(True, elapsed_time)

                logger.info(
                    f"종목 분석 완료: {stock_data.get('stock_code')} "
                    f"(점수: {result['score']}, 신호: {result['signal']})"
                )

                return result

            except Exception as e:
                error_msg = str(e)

                # 재시도 로그 (모든 시도 표시)
                if attempt < max_retries - 1:
                    logger.warning(f"AI 분석 실패 (시도 {attempt+1}/{max_retries}), {retry_delay}초 후 재시도: {error_msg}")
                    print(f"   ⚠️ AI 응답 지연 또는 에러 (시도 {attempt+1}/{max_retries}), {retry_delay}초 후 재시도...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 지수 백오프
                else:
                    # 모든 시도 실패 - 최종 에러
                    logger.error(f"AI 분석 최종 실패 ({max_retries}회 시도): {error_msg}")
                    print(f"   ❌ AI 분석 최종 실패: {error_msg}")
                    self.update_statistics(False)
                    return self._get_error_result(f"AI 분석 실패: {error_msg}")
    
    def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        시장 분석
        
        Args:
            market_data: 시장 데이터
        
        Returns:
            시장 분석 결과
        """
        if not self.is_initialized:
            if not self.initialize():
                return self._get_error_result("분석기 초기화 실패")
        
        start_time = time.time()
        
        try:
            # 프롬프트 생성
            prompt = self._create_market_analysis_prompt(market_data)
            
            # Gemini API 호출
            response = self.model.generate_content(prompt)
            
            # 응답 파싱
            result = self._parse_market_analysis_response(response.text)
            
            # 통계 업데이트
            elapsed_time = time.time() - start_time
            self.update_statistics(True, elapsed_time)
            
            logger.info(f"시장 분석 완료 (심리: {result['market_sentiment']})")
            
            return result
            
        except Exception as e:
            logger.error(f"시장 분석 중 오류: {e}")
            self.update_statistics(False)
            return self._get_error_result(str(e))
    
    def analyze_portfolio(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        포트폴리오 분석
        
        Args:
            portfolio_data: 포트폴리오 데이터
        
        Returns:
            포트폴리오 분석 결과
        """
        if not self.is_initialized:
            if not self.initialize():
                return self._get_error_result("분석기 초기화 실패")
        
        start_time = time.time()
        
        try:
            # 프롬프트 생성
            prompt = self._create_portfolio_analysis_prompt(portfolio_data)
            
            # Gemini API 호출
            response = self.model.generate_content(prompt)
            
            # 응답 파싱
            result = self._parse_portfolio_analysis_response(response.text)
            
            # 통계 업데이트
            elapsed_time = time.time() - start_time
            self.update_statistics(True, elapsed_time)
            
            logger.info("포트폴리오 분석 완료")
            
            return result
            
        except Exception as e:
            logger.error(f"포트폴리오 분석 중 오류: {e}")
            self.update_statistics(False)
            return self._get_error_result(str(e))
    
    # ==================== 프롬프트 생성 ====================

    def _create_market_analysis_prompt(self, market_data: Dict[str, Any]) -> str:
        """시장 분석 프롬프트 생성"""
        prompt = f"""
당신은 전문 시장 분석가입니다. 현재 시장 상황을 분석해주세요.

**시장 데이터:**
{self._format_market_data(market_data)}

**분석 요청:**
다음 형식으로 분석해주세요:

시장심리: [bullish/bearish/neutral 중 하나]
점수: [0~10점]
분석: [시장 상황 분석 3-5줄]
추천: [투자 전략 추천 2-3가지]
"""
        
        return prompt
    
    def _create_portfolio_analysis_prompt(self, portfolio_data: Dict[str, Any]) -> str:
        """포트폴리오 분석 프롬프트 생성"""
        prompt = f"""
당신은 포트폴리오 관리 전문가입니다. 다음 포트폴리오를 분석해주세요.

**포트폴리오:**
- 총 자산: {portfolio_data.get('total_assets', 0):,}원
- 현금 비중: {portfolio_data.get('cash_ratio', 0):.1f}%
- 종목 수: {portfolio_data.get('position_count', 0)}개
- 총 수익률: {portfolio_data.get('total_profit_loss_rate', 0):+.2f}%

**보유 종목:**
{self._format_holdings_data(portfolio_data.get('holdings', []))}

**분석 요청:**
포트폴리오의 강점, 약점, 개선사항을 분석해주세요.
"""
        
        return prompt
    
    # ==================== 응답 파싱 ====================
    
    def _parse_stock_analysis_response(
        self,
        response_text: str,
        stock_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """종목 분석 응답 파싱 - JSON 또는 텍스트 형식 모두 지원 (v6.1 강화)"""

        # v6.1: 더 강력한 JSON 파싱
        try:
            import re
            import json

            # Clean response text
            cleaned_text = response_text.strip()

            # Try multiple JSON extraction strategies
            json_str = None

            # Strategy 1: Extract from ```json code block
            json_match = re.search(r'```json\s*\n(.*?)\n```', cleaned_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                logger.debug("Found JSON in code block")

            # Strategy 2: Extract from ``` code block (without json)
            if not json_str:
                json_match = re.search(r'```\s*\n(.*?)\n```', cleaned_text, re.DOTALL)
                if json_match:
                    potential_json = json_match.group(1).strip()
                    if potential_json.startswith('{'):
                        json_str = potential_json
                        logger.debug("Found JSON in generic code block")

            # Strategy 3: Find largest {...} block
            if not json_str:
                json_blocks = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned_text, re.DOTALL)
                if json_blocks:
                    # Get the largest JSON block
                    json_str = max(json_blocks, key=len)
                    logger.debug("Found JSON block in text")

            # Strategy 4: Try parsing entire response as JSON
            if not json_str:
                if cleaned_text.startswith('{'):
                    json_str = cleaned_text
                    logger.debug("Entire response appears to be JSON")

            # Try parsing JSON
            if json_str:
                try:
                    # Clean common JSON issues
                    json_str = json_str.strip()
                    # Remove trailing commas
                    json_str = re.sub(r',\s*}', '}', json_str)
                    json_str = re.sub(r',\s*]', ']', json_str)

                    data = json.loads(json_str)

                    # Extract values from JSON response
                    signal_map = {
                        'STRONG_BUY': 'buy',
                        'BUY': 'buy',
                        'WEAK_BUY': 'buy',
                        'HOLD': 'hold',
                        'WEAK_SELL': 'sell',
                        'SELL': 'sell',
                        'STRONG_SELL': 'sell'
                    }

                    signal = signal_map.get(str(data.get('signal', 'HOLD')).upper(), 'hold')

                    # Extract detailed reasoning
                    reasons = []
                    if 'detailed_reasoning' in data:
                        reasons.append(data['detailed_reasoning'])
                    if 'key_insights' in data and isinstance(data.get('key_insights'), list):
                        reasons.extend(data['key_insights'])

                    # Extract warnings
                    warnings = data.get('warnings', [])
                    if isinstance(warnings, str):
                        warnings = [warnings]

                    # Extract trading plan
                    trading_plan = data.get('trading_plan', {})
                    entry_strategy = trading_plan.get('entry_strategy', '') if isinstance(trading_plan, dict) else ''

                    result = {
                        'score': 0,
                        'signal': signal,
                        'split_strategy': entry_strategy,
                        'confidence': data.get('confidence_level', 'Medium'),
                        'recommendation': signal,
                        'reasons': reasons if reasons else ['AI 분석 완료'],
                        'risks': warnings if isinstance(warnings, list) else [],
                        'target_price': int(stock_data.get('current_price', 0) * 1.1),
                        'stop_loss_price': int(stock_data.get('current_price', 0) * 0.95),
                        'analysis_text': cleaned_text,
                    }

                    logger.info(f"✅ JSON 응답 파싱 성공: {signal}")
                    return result

                except json.JSONDecodeError as e:
                    logger.warning(f"JSON 파싱 실패 (위치: {e.pos}), 텍스트 파싱으로 전환")
                except Exception as e:
                    logger.warning(f"JSON 처리 중 에러: {e}, 텍스트 파싱으로 전환")

        except Exception as e:
            logger.warning(f"JSON 추출 실패: {e}, 텍스트 파싱으로 전환")

        # ===== Fallback: 간단한 텍스트 파싱 =====
        logger.info("텍스트 파싱 모드로 전환")

        # 기본 신호 추출 (buy/sell/hold 키워드 찾기)
        text_lower = response_text.lower()
        signal = 'hold'  # 기본값

        if 'strong buy' in text_lower or 'strong_buy' in text_lower:
            signal = 'buy'
        elif 'buy' in text_lower and 'not' not in text_lower[:text_lower.find('buy')] if 'buy' in text_lower else False:
            signal = 'buy'
        elif 'sell' in text_lower:
            signal = 'sell'

        result = {
            'score': 0,
            'signal': signal,
            'split_strategy': '',
            'confidence': 'Medium',
            'recommendation': signal,
            'reasons': [response_text[:200] if len(response_text) > 200 else response_text],
            'risks': [],
            'target_price': int(stock_data.get('current_price', 0) * 1.1),
            'stop_loss_price': int(stock_data.get('current_price', 0) * 0.95),
            'analysis_text': response_text,
        }

        logger.info(f"텍스트 파싱 완료: {signal}")
        return result
    
    def _parse_market_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """시장 분석 응답 파싱"""
        result = {
            'market_sentiment': 'neutral',
            'market_score': 5.0,
            'analysis': response_text,
            'recommendations': [],
        }
        
        # 간단한 키워드 기반 파싱
        text_lower = response_text.lower()
        
        if 'bullish' in text_lower or '상승' in response_text:
            result['market_sentiment'] = 'bullish'
            result['market_score'] = 7.0
        elif 'bearish' in text_lower or '하락' in response_text:
            result['market_sentiment'] = 'bearish'
            result['market_score'] = 3.0
        
        return result
    
    def _parse_portfolio_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """포트폴리오 분석 응답 파싱"""
        return {
            'analysis': response_text,
            'strengths': [],
            'weaknesses': [],
            'recommendations': [],
        }
    
    # ==================== 유틸리티 ====================
    
    def _format_technical_data(self, technical: Dict[str, Any]) -> str:
        """기술적 지표 포맷팅"""
        if not technical:
            return "기술적 지표 없음"
        
        return f"""
- 5일 이동평균: {technical.get('ma5', 0):,.0f}원
- 20일 이동평균: {technical.get('ma20', 0):,.0f}원
- RSI(14): {technical.get('rsi', 50):.1f}
- 가격 위치: {technical.get('price_position', 0.5)*100:.1f}%
"""
    
    def _format_investor_data(self, investor: Dict[str, Any]) -> str:
        """투자자 동향 포맷팅"""
        if not investor:
            return "투자자 동향 없음"
        
        return f"""
- 외국인 순매수: {investor.get('foreign_net', 0):,}주
- 기관 순매수: {investor.get('institution_net', 0):,}주
"""
    
    def _format_market_data(self, market_data: Dict[str, Any]) -> str:
        """시장 데이터 포맷팅"""
        return str(market_data)
    
    def _format_holdings_data(self, holdings: list) -> str:
        """보유 종목 포맷팅"""
        if not holdings:
            return "보유 종목 없음"
        
        text = ""
        for h in holdings[:5]:  # 최대 5개만
            text += f"- {h.get('stock_name', '')}: {h.get('profit_loss_rate', 0):+.2f}%\n"
        
        return text
    
    def _get_error_result(self, error_msg: str) -> Dict[str, Any]:
        """에러 결과 반환"""
        return {
            'error': True,
            'error_message': error_msg,
            'score': 5.0,
            'signal': 'hold',
            'confidence': 'Low',
            'recommendation': '분석 실패',
            'reasons': [error_msg],
            'risks': [],
        }


__all__ = ['GeminiAnalyzer']