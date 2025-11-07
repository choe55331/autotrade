import logging
import time
from typing import Dict, Any, Optional
from .base_analyzer import BaseAnalyzer

try:
    from .prompts.stock_analysis import create_enhanced_prompt
    USE_ENHANCED_PROMPT = True
except ImportError:
    USE_ENHANCED_PROMPT = False

logger = logging.getLogger(__name__)


class GeminiAnalyzer(BaseAnalyzer):
    """
    Google Gemini AI 분석기

    Gemini API를 사용한 종목/시장 분석
    

"""
    STOCK_ANALYSIS_PROMPT_TEMPLATE_SIMPLE = """

당신은 전문 트레이더입니다. 다음 종목을 분석하여 **반드시 JSON 형식으로만** 응답하세요.

- 종목: {stock_name} ({stock_code})
- 현재가: {current_price:,}원
- 등락률: {change_rate:+.2f}%
- 거래량: {volume:,}주

- 종합 점수: {score}/{percentage:.1f}%
- 세부 점수:
{score_breakdown_detailed}

- 기관 순매수: {institutional_net_buy:,}원
- 외국인 순매수: {foreign_net_buy:,}원
- 매수호가 비율: {bid_ask_ratio:.2f}

{portfolio_info}

---

**중요: 반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트는 포함하지 마세요.**

```json
{{
  "signal": "buy" 또는 "hold" 또는 "sell",
  "confidence_level": "Very High" 또는 "High" 또는 "Medium" 또는 "Low",
  "overall_score": 0.0~10.0 사이의 숫자,
  "reasons": ["이유1", "이유2", "이유3"],
  "risks": ["리스크1", "리스크2"],
  "detailed_reasoning": "상세 분석 (3-5문장)"
}}
```"""

    STOCK_ANALYSIS_PROMPT_TEMPLATE_COMPLEX = """

당신은 20년 이상의 경력을 가진 퀀트 헤지펀드 매니저이자 리스크 관리 전문가입니다.
다음 한국 주식에 대한 심층 분석을 수행해주세요.

**종목**: {stock_name} ({stock_code})
**현재가**: {current_price:,}원
**등락률**: {change_rate:+.2f}%
**거래량**: {volume:,}주

**종합 점수**: {score}/440점 ({percentage:.1f}%)

{score_breakdown_detailed}

**점수 해석 가이드**:
- 350점 이상 (80%+): S등급 - 매우 강력한 매수 신호
- 300-349점 (68-79%): A등급 - 강력한 매수 신호
- 250-299점 (57-68%): B등급 - 긍정적 신호
- 200-249점 (45-56%): C등급 - 중립
- 200점 미만 (45%-): D/F등급 - 부정적 신호

**기관 순매수**: {institutional_net_buy:,}원
**외국인 순매수**: {foreign_net_buy:,}원
**매수호가 강도**: {bid_ask_ratio:.2f}

**투자자 흐름 해석**:
"""
- 외국인+기관 동시 순매수 = 강력한 상승 신호
- 외국인 순매도 + 개인 순매수 = 경고 신호
- 매수호가강도 > 1.5 = 강한 매수세
- 매수호가강도 < 0.7 = 강한 매도세

{portfolio_info}

---


- 10가지 세부 점수를 개별적으로 평가
- 각 점수가 실제 시장 상황과 부합하는지 검증
- 과대평가되었거나 과소평가된 지표 식별
- 점수의 신뢰도 평가 (0-100%)

- 기관/외국인 매매 패턴 해석
- 개인 vs 기관/외국인 포지션 비교
- 누적 매수/매도 흐름 분석
- 스마트머니가 보내는 신호 해독

- 단기 급등 vs 추세 전환 vs 조정 후 재상승 구분
- 현재 모멘텀의 지속 가능성 평가
- 과매수/과매도 상태 판단
- 변동성 분석 및 예상 가격 범위

**주요 리스크 요인**:
- 기술적 리스크 (저항선, 지지선 이탈 가능성)
- 펀더멘털 리스크 (밸류에이션, 업종 리스크)
- 시장 리스크 (전체 시장 약세, 변동성 확대)
- 유동성 리스크
- 이벤트 리스크 (실적 발표, 규제 등)

**예상 시나리오**:
- 🐂 Bull Case (확률 ___%): [상승 시나리오]
-  Base Case (확률 ___%): [기본 시나리오]
- 🐻 Bear Case (확률 ___%): [하락 시나리오]

**진입 전략**:
- 즉시 매수 vs 대기 vs 분할 매수
- 최적 진입 가격 및 타이밍
- 포지션 크기 권장 (포트폴리오 대비 %)

**리스크 관리**:
- 손절가 설정 (가격 및 근거)
- 익절 목표가 (1차, 2차, 3차)
- 최대 보유 기간
- 손익비 (Risk-Reward Ratio)

- 수익 확률: ___%
- 손실 확률: ___%
- 기대 수익률: ___% (확률 가중 평균)
- 최대 손실 예상: ___%

**시장 변동에 대한 민감도**:
- KOSPI ±1% 변동 시 예상 가격 변화: 베타 계수 기반 추정
- 거래량 급증/급감 시 가격 영향
- 외환(달러) 변동 영향 (수출/수입 업종)
- 금리 변동 민감도

**Delta (가격 민감도)**:
- 단기 저항선까지 거리: ___원 (___%)
- 단기 지지선까지 거리: ___원 (___%)
- 손익분기점 분석

- 호가창 분석: 매수/매도 벽 위치 및 강도
- 체결강도 분석: 시장가 vs 호가 체결 비율
- 틱(Tick) 방향성: 상승틱 vs 하락틱 비율
- 유동성 분석: 스프레드, 주문 깊이
- 내부자 거래 의심 신호 (급격한 거래 패턴 변화)

- 업종 평균 대비 상대 강도
- 주요 경쟁사 대비 모멘텀
- 시장 레짐: 강세장/약세장/횡보장
- 섹터 로테이션 관점에서의 위치

- 개인 투자자 패닉 매수/매도 징후
- 기관의 분산 매수/매도 패턴
- 뉴스 및 공시 임팩트 평가
- 소셜 미디어 센티먼트 (가능한 경우)

---


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

  "sensitivity_analysis": {
    "market_beta": <number, e.g., 1.2 means 20% more volatile than market>,
    "support_distance_pct": <number, % distance to nearest support>,
    "resistance_distance_pct": <number, % distance to nearest resistance>,
    "key_price_levels": {
      "strong_support": [price1, price2],
      "weak_support": [price1, price2],
      "weak_resistance": [price1, price2],
      "strong_resistance": [price1, price2]
    }
  },

  "market_microstructure": {
    "bid_ask_spread_pct": <number>,
    "order_book_imbalance": "Strong Buy" | "Buy" | "Neutral" | "Sell" | "Strong Sell",
    "tick_direction": <-100 to +100, negative=down ticks, positive=up ticks>,
    "liquidity_score": <0-100>,
    "unusual_activity_detected": true | false,
    "unusual_activity_description": "..."
  },

  "correlation_analysis": {
    "sector_relative_strength": <-100 to +100>,
    "market_regime": "Bull Market" | "Bear Market" | "Sideways Market" | "Transitioning",
    "sector_rotation_signal": "Sector In" | "Sector Out" | "Neutral",
    "peer_comparison": {
      "rank": <1-10>,
      "top_peer": "company name",
      "momentum_vs_peers": "Leading" | "Inline" | "Lagging"
    }
  },

  "behavioral_analysis": {
    "retail_sentiment": "Panic Buy" | "Euphoria" | "FOMO" | "Neutral" | "Fear" | "Panic Sell",
    "institutional_pattern": "Accumulation" | "Distribution" | "Neutral",
    "news_impact_score": <0-100>,
    "social_sentiment": "Very Positive" | "Positive" | "Neutral" | "Negative" | "Very Negative"
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
    "Most critical insight
    "Most critical insight
    "Most critical insight
  ],

  "warnings": [
    "Critical warning
    "Critical warning
  ],

  "detailed_reasoning": "<3-5 paragraph comprehensive analysis covering all aspects>",

  "analyst_conviction": "Very High" | "High" | "Medium" | "Low" | "Very Low"
}
```


1. **Be Brutally Honest**: Don't sugarcoat risks or force a bullish view
2. **Probabilistic Thinking**: Express everything in probabilities, not certainties
3. **Risk-First Mindset**: Always assess downside before upside
4. **Contrarian Awareness**: Question if the market is overreacting or underreacting
5. **Evidence-Based**: Root all conclusions in the actual data provided
6. **Actionable**: Provide specific, executable trading recommendations
7. **Intellectual Honesty**: If signals are mixed or data insufficient, say "HOLD - Insufficient Edge"

**특히 중요**: 점수가 높다고 무조건 매수 추천하지 말 것. 스마트머니 흐름과 가격 액션을 종합적으로 고려할 것."""

"""
    def __init__(self, api_key: str = None, model_name: str = None, enable_cross_check: bool = False):
        """
        Gemini 분석기 초기화

        Args:
            api_key: Gemini API 키
            model_name: 모델 이름 (기본: gemini-2.5-flash)
            enable_cross_check: 크로스 체크 활성화 (2.0 vs 2.5 비교)
        """
        super().__init__("GeminiAnalyzer")

        if api_key is None:
            from config import GEMINI_API_KEY, GEMINI_MODEL_NAME, GEMINI_ENABLE_CROSS_CHECK
            self.api_key = GEMINI_API_KEY
            self.model_name = model_name or GEMINI_MODEL_NAME or 'gemini-2.5-flash'
            if enable_cross_check is False and GEMINI_ENABLE_CROSS_CHECK:
                enable_cross_check = GEMINI_ENABLE_CROSS_CHECK
        else:
            self.api_key = api_key
            self.model_name = model_name or 'gemini-2.5-flash'

        self.model = None

        self.enable_cross_check = enable_cross_check
        self.model_2_0 = None
        self.model_2_5 = None

        self._analysis_cache = {}
        self._cache_ttl = 300

        cross_check_status = "크로스체크 활성화" if enable_cross_check else "단일 모델"
        logger.info(f"GeminiAnalyzer 초기화 (모델: {self.model_name}, {cross_check_status})")
    
    def initialize(self) -> bool:
        """
        Gemini API 초기화

        Returns:
            초기화 성공 여부
        """
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)

            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"기본 모델 초기화: {self.model_name}")

            if self.enable_cross_check:
                try:
                    self.model_2_0 = genai.GenerativeModel('gemini-2.0-flash-exp')
                    logger.info("크로스체크 모델 초기화: gemini-2.0-flash-exp")
                except Exception as e:
                    logger.warning(f"2.0 모델 초기화 실패: {e}")

                try:
                    self.model_2_5 = genai.GenerativeModel('gemini-2.5-flash')
                    logger.info("크로스체크 모델 초기화: gemini-2.5-flash")
                except Exception as e:
                    logger.warning(f"2.5 모델 초기화 실패: {e}")

                if not self.model_2_0 and not self.model_2_5:
                    logger.error("크로스체크 모델 초기화 모두 실패")
                    return False

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
        if not self.is_initialized:
            if not self.initialize():
                return self._get_error_result("분석기 초기화 실패")

"""
        is_valid, msg = self.validate_stock_data(stock_data)
        if not is_valid:
            return self._get_error_result(msg)

        stock_code = stock_data.get('stock_code', '')
        score = score_info.get('score', 0) if score_info else 0
        cache_key = f"{stock_code}_{int(score)}"

        if self.enable_cross_check:
            cache_key += "_crosscheck"

        if cache_key in self._analysis_cache:
            cached_entry = self._analysis_cache[cache_key]
            cached_time = cached_entry['timestamp']
            cached_result = cached_entry['result']

            if (time.time() - cached_time) < self._cache_ttl:
                logger.info(f"AI 분석 캐시 히트: {stock_code} (캐시 유효시간: {int(self._cache_ttl - (time.time() - cached_time))}초)")
                print(f"   💾 AI 분석 캐시 사용 (캐시 유효: {int(self._cache_ttl - (time.time() - cached_time))}초)")
                return cached_result
            else:
                del self._analysis_cache[cache_key]
                logger.info(f"AI 분석 캐시 만료: {stock_code}")

        start_time = time.time()

        if self.enable_cross_check and self.model_2_0 and self.model_2_5:
            logger.info(f"🔀 크로스체크 분석 시작: {stock_code}")
            print(f"   🔀 AI 크로스체크 분석 (2.0 vs 2.5)")

            if score_info:
                score = score_info.get('score', 0)
                percentage = score_info.get('percentage', 0)
                breakdown = score_info.get('breakdown', {})
                score_breakdown_detailed = "\n".join([
                    f"  {k}: {v:.1f}점" for k, v in breakdown.items() if v >= 0
                ])
            else:
                score = 0
                percentage = 0
                score_breakdown_detailed = "  점수 정보 없음"

            portfolio_text = portfolio_info or "보유 종목 없음"
            institutional_net_buy = stock_data.get('institutional_net_buy', 0)
            foreign_net_buy = stock_data.get('foreign_net_buy', 0)
            bid_ask_ratio = stock_data.get('bid_ask_ratio', 1.0)

            prompt = self.STOCK_ANALYSIS_PROMPT_TEMPLATE_SIMPLE.format(
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

            result_2_0 = self._analyze_with_single_model(
                self.model_2_0,
                'gemini-2.0-flash-exp',
                prompt,
                stock_data
            )

            result_2_5 = self._analyze_with_single_model(
                self.model_2_5,
                'gemini-2.5-flash',
                prompt,
                stock_data
            )

            result = self._cross_check_results(result_2_0, result_2_5)

            self._analysis_cache[cache_key] = {
                'timestamp': time.time(),
                'result': result
            }

            elapsed_time = time.time() - start_time
            self.update_statistics(True, elapsed_time)

            if 'cross_check' in result:
                cc = result['cross_check']
                if cc.get('agreement'):
                    print(f"   [OK] 크로스체크 일치: {result['signal']} (신뢰도: {result['confidence']})")
                else:
                """
                    print(f"   WARNING: 크로스체크 불일치 -> 보수적 선택: {result['signal']}")

            logger.info(
                f"크로스체크 분석 완료: {stock_code} "
                f"(신호: {result['signal']}, 신뢰도: {result['confidence']})"
            )

            return result

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
            """
                if score_info:
                    score = score_info.get('score', 0)
                    percentage = score_info.get('percentage', 0)
                    breakdown = score_info.get('breakdown', {})
                    score_breakdown_detailed = "\n".join([
                        f"  {k}: {v:.1f}점" for k, v in breakdown.items() if v >= 0
                    ])
                else:
                    score = 0
                    percentage = 0
                    score_breakdown_detailed = "  점수 정보 없음"

                portfolio_text = portfolio_info or "보유 종목 없음"

                institutional_net_buy = stock_data.get('institutional_net_buy', 0)
                foreign_net_buy = stock_data.get('foreign_net_buy', 0)
                bid_ask_ratio = stock_data.get('bid_ask_ratio', 1.0)

                prompt = self.STOCK_ANALYSIS_PROMPT_TEMPLATE_SIMPLE.format(
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

                try:
                    response = self.model.generate_content(
                        prompt,
                        request_options={'timeout': 30}
                    )
                except Exception as timeout_error:
                    raise ValueError(f"Gemini API timeout or error: {timeout_error}")

                if not response.candidates:
                    raise ValueError("Gemini API returned no candidates")

                candidate = response.candidates[0]
                finish_reason = candidate.finish_reason

                if finish_reason != 1:
                    reason_map = {2: "SAFETY", 3: "MAX_TOKENS", 4: "RECITATION", 5: "OTHER"}
                    reason_name = reason_map.get(finish_reason, f"UNKNOWN({finish_reason})")
                    raise ValueError(f"Gemini blocked: {reason_name}")

                if not hasattr(response, 'text'):
                    raise ValueError("Gemini API response has no 'text' attribute")

"""
                response_text = response.text
                if not response_text or len(response_text.strip()) == 0:
                    raise ValueError("Gemini API returned empty response")

                logger.debug(f"Gemini 응답 길이: {len(response_text)} chars")

                result = self._parse_stock_analysis_response(response_text, stock_data)

                self._analysis_cache[cache_key] = {
                    'timestamp': time.time(),
                    'result': result
                }
                logger.info(f"AI 분석 결과 캐시 저장: {stock_code} (TTL: {self._cache_ttl}초)")

                elapsed_time = time.time() - start_time
                self.update_statistics(True, elapsed_time)

                logger.info(
                    f"종목 분석 완료: {stock_data.get('stock_code')} "
                    f"(점수: {result['score']}, 신호: {result['signal']})"
                )

                return result

            except Exception as e:
                error_msg = str(e)

                if attempt < max_retries - 1:
                    logger.warning(f"AI 분석 실패 (시도 {attempt+1}/{max_retries}), {retry_delay}초 후 재시도: {error_msg}")
                    print(f"   WARNING: AI 응답 지연 또는 에러 (시도 {attempt+1}/{max_retries}), {retry_delay}초 후 재시도...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"AI 분석 최종 실패 ({max_retries}회 시도): {error_msg}")
                    print(f"   [ERROR] AI 분석 최종 실패: {error_msg}")
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
        
        """
        start_time = time.time()
        
        try:
            prompt = self._create_market_analysis_prompt(market_data)
            
            response = self.model.generate_content(prompt)
            
            result = self._parse_market_analysis_response(response.text)
            
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
        
        """
        start_time = time.time()
        
        try:
            prompt = self._create_portfolio_analysis_prompt(portfolio_data)
            
            response = self.model.generate_content(prompt)
            
            result = self._parse_portfolio_analysis_response(response.text)
            
            elapsed_time = time.time() - start_time
            self.update_statistics(True, elapsed_time)
            
            logger.info("포트폴리오 분석 완료")
            
            return result
            
        except Exception as e:
            logger.error(f"포트폴리오 분석 중 오류: {e}")
            self.update_statistics(False)
            return self._get_error_result(str(e))
    

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
    
    
    def _parse_stock_analysis_response(
        self,
        response_text: str,
        stock_data: Dict[str, Any]
    ) -> Dict[str, Any]:

        if not response_text:
            logger.error("빈 응답 텍스트를 받았습니다")
            raise ValueError("Empty response text")

        preview_len = min(300, len(response_text))
        logger.debug(f"응답 미리보기 ({preview_len}/{len(response_text)} chars): {response_text[:preview_len]}")

        try:
            import re
            import json

            cleaned_text = response_text.strip()

            json_str = None

            json_match = re.search(r'```json\s*\n(.*?)\n```', cleaned_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                logger.debug("Found JSON in code block")

            if not json_str:
                json_match = re.search(r'```\s*\n(.*?)\n```', cleaned_text, re.DOTALL)
                if json_match:
                    potential_json = json_match.group(1).strip()
                    if potential_json.startswith('{'):
                        json_str = potential_json
                        """
                        logger.debug("Found JSON in generic code block")

            if not json_str:
                pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'
                json_blocks = re.findall(pattern, cleaned_text, re.DOTALL)

                if not json_blocks:
                    first_brace = cleaned_text.find('{')
                    last_brace = cleaned_text.rfind('}')
                    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                        json_str = cleaned_text[first_brace:last_brace+1]
                        logger.debug("Extracted JSON from first { to last }")
                elif json_blocks:
                    json_str = max(json_blocks, key=len)
                    logger.debug("Found JSON block in text")

            if not json_str:
                if cleaned_text.startswith('{'):
                    json_str = cleaned_text
                    """
                    logger.debug("Entire response appears to be JSON")

            if json_str:
                try:
                    json_str = json_str.strip()
                    json_str = re.sub(r',\s*}', '}', json_str)
                    json_str = re.sub(r',\s*]', ']', json_str)

                    data = json.loads(json_str)

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

                    reasons = []
                    if 'detailed_reasoning' in data:
                        reasons.append(data['detailed_reasoning'])
                    if 'key_insights' in data and isinstance(data.get('key_insights'), list):
                        reasons.extend(data['key_insights'])

"""
                    warnings = data.get('warnings', [])
                    if isinstance(warnings, str):
                        warnings = [warnings]

"""
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

                    logger.info(f"[OK] JSON 응답 파싱 성공: {signal}")
                    return result

                except json.JSONDecodeError as e:
                    logger.warning(f"JSON 파싱 실패 (위치: {e.pos}, 메시지: {e.msg}), 텍스트 파싱으로 전환")
                    if json_str:
                        error_context = json_str[max(0, e.pos-50):min(len(json_str), e.pos+50)]
                        logger.warning(f"에러 컨텍스트: ...{error_context}...")
                        logger.warning(f"JSON 문자열 샘플 (처음 200자): {json_str[:200]}")
                    else:
                        logger.warning("JSON 문자열이 None입니다")
                except Exception as e:
                    logger.warning(f"JSON 처리 중 예외: {type(e).__name__}: {e}, 텍스트 파싱으로 전환")
                    if json_str:
                        logger.warning(f"JSON 문자열 샘플: {json_str[:200]}")
                    else:
                        logger.warning("JSON 문자열이 None입니다")

        except Exception as e:
            logger.warning(f"JSON 추출 중 예외 발생: {type(e).__name__}: {e}, 텍스트 파싱으로 전환")
            logger.debug(f"원본 응답 (처음 500자): {response_text[:500]}")

        logger.info("텍스트 파싱 모드로 전환")

        text_lower = response_text.lower()
        signal = 'hold'

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
        for h in holdings[:5]:
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


    def _analyze_with_single_model(
        self,
        model,
        model_name: str,
        prompt: str,
        stock_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        단일 모델로 분석 수행

        Args:
            model: Gemini 모델 인스턴스
            model_name: 모델 이름 (로깅용)
            prompt: 분석 프롬프트
            stock_data: 종목 데이터

        Returns:
            분석 결과 또는 None (실패시)
        """
        try:
            logger.info(f"[{model_name}] 분석 시작")

            response = model.generate_content(
                prompt,
                request_options={'timeout': 30}
            )

            if not response.candidates:
                logger.warning(f"[{model_name}] No candidates")
                return None

            candidate = response.candidates[0]
            finish_reason = candidate.finish_reason

            if finish_reason != 1:
                reason_map = {2: "SAFETY", 3: "MAX_TOKENS", 4: "RECITATION", 5: "OTHER"}
                reason_name = reason_map.get(finish_reason, f"UNKNOWN({finish_reason})")
                logger.warning(f"[{model_name}] Blocked: {reason_name}")
                return None

            if not hasattr(response, 'text'):
                logger.warning(f"[{model_name}] No text attribute")
                """
                return None

            response_text = response.text
            if not response_text or len(response_text.strip()) == 0:
                logger.warning(f"[{model_name}] Empty response")
                return None

            result = self._parse_stock_analysis_response(response_text, stock_data)
            result['model_name'] = model_name
            logger.info(f"[{model_name}] 분석 완료: {result['signal']}")

            return result

        except Exception as e:
            logger.error(f"[{model_name}] 분석 실패: {e}")
            return None

    def _cross_check_results(
        self,
        result_2_0: Optional[Dict[str, Any]],
        result_2_5: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        두 모델의 결과를 크로스 체크하여 최종 결과 생성

        Args:
            result_2_0: 2.0 모델 결과
            result_2_5: 2.5 모델 결과

        Returns:
            통합 분석 결과
        """
        if not result_2_0 and not result_2_5:
            logger.error("크로스체크: 모든 모델 실패")
            return self._get_error_result("모든 모델 분석 실패")

        if not result_2_0:
            logger.warning("크로스체크: 2.0 실패, 2.5만 사용")
            result_2_5['cross_check'] = {
                'enabled': True,
                'model_2_0_failed': True,
                'model_2_5_signal': result_2_5['signal'],
                'agreement': 'N/A'
            }
            return result_2_5

        if not result_2_5:
            logger.warning("크로스체크: 2.5 실패, 2.0만 사용")
            result_2_0['cross_check'] = {
                'enabled': True,
                'model_2_0_signal': result_2_0['signal'],
                'model_2_5_failed': True,
                'agreement': 'N/A'
            }
            return result_2_0

        signal_2_0 = result_2_0['signal']
        signal_2_5 = result_2_5['signal']

        logger.info(f"크로스체크: 2.0={signal_2_0}, 2.5={signal_2_5}")

        signals_match = (signal_2_0 == signal_2_5)

        if signals_match:
            logger.info(f"[OK] 크로스체크 일치: {signal_2_0}")
            final_result = result_2_5.copy()

            confidence_map = {
                'Low': 'Medium',
                'Medium': 'High',
                'High': 'Very High',
                'Very High': 'Very High'
            }
            original_confidence = final_result.get('confidence', 'Medium')
            final_result['confidence'] = confidence_map.get(original_confidence, 'High')

            final_result['cross_check'] = {
                'enabled': True,
                'model_2_0_signal': signal_2_0,
                'model_2_5_signal': signal_2_5,
                'agreement': True,
                'original_confidence': original_confidence,
                'boosted_confidence': final_result['confidence']
            }

        else:
            logger.warning(f"WARNING: 크로스체크 불일치: 2.0={signal_2_0}, 2.5={signal_2_5}")

            signal_priority = {'sell': 0, 'hold': 1, 'buy': 2}
            priority_2_0 = signal_priority.get(signal_2_0, 1)
            priority_2_5 = signal_priority.get(signal_2_5, 1)

            if 'hold' in [signal_2_0, signal_2_5]:
                final_signal = 'hold'
                chosen_model = '보수적 선택'
            elif priority_2_0 < priority_2_5:
                final_signal = signal_2_0
                chosen_model = '2.0'
            else:
                final_signal = signal_2_5
                chosen_model = '2.5'

            logger.info(f"최종 신호: {final_signal} (선택: {chosen_model})")

            final_result = result_2_5.copy()
            final_result['signal'] = final_signal
            final_result['recommendation'] = final_signal
            final_result['confidence'] = 'Medium'

            reasons_combined = []
            if result_2_0.get('reasons'):
                reasons_combined.append(f"[2.0] " + "; ".join(result_2_0['reasons'][:2]))
                """
            if result_2_5.get('reasons'):
                reasons_combined.append(f"[2.5] " + "; ".join(result_2_5['reasons'][:2]))
                """
            final_result['reasons'] = reasons_combined

            final_result['cross_check'] = {
                'enabled': True,
                'model_2_0_signal': signal_2_0,
                'model_2_5_signal': signal_2_5,
                'agreement': False,
                'final_signal': final_signal,
                'reason': f'불일치로 보수적 선택 ({chosen_model})'
            }

        return final_result


__all__ = ['GeminiAnalyzer']