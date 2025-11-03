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

    # 종목 분석 프롬프트 템플릿
    STOCK_ANALYSIS_PROMPT_TEMPLATE = """[종목 정보]
종목명: {stock_name} ({stock_code})
현재가: {current_price:,}원 (등락률: {change_rate:+.2f}%)
거래량: {volume:,}주
종합 점수: {score}/440점 ({percentage:.1f}%)

[10가지 세부 점수]
{score_breakdown_detailed}

[투자자 동향]
기관 순매수: {institutional_net_buy:,}원
외국인 순매수: {foreign_net_buy:,}원
매수호가강도: {bid_ask_ratio:.2f}

[현재 포트폴리오]
{portfolio_info}

[분석 요청]
위 데이터를 종합하여 다음을 분석해주세요:

1. 종합 점수 {percentage:.1f}%의 타당성 (10가지 세부 점수 고려)
2. 투자자 동향이 보여주는 시그널
3. 단기 급등 vs 추세 전환 판단
4. 주요 리스크 요인

[응답 형식]
관심도: [높음/보통]
분할매수: [높음이면 구체적으로 3단계로 제시]
  예시) 1차 40% 현재가, 2차 30% -2%, 3차 20% -4%
근거: [2-3줄, 점수와 투자자 동향 언급]
경고: [1-2줄, 구체적 리스크]
"""

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
        """종목 분석 응답 파싱 - 관심도, 분할매수, 근거, 경고 추출"""
        lines = response_text.split('\n')

        # 관심도 찾기 (높음 → buy, 보통 → hold)
        signal = 'hold'  # 기본값
        for line in lines:
            line_lower = line.lower()
            if '관심도:' in line or '관심도 :' in line:
                if '높음' in line:
                    signal = 'buy'
                break
            # 영어/이전 형식도 지원 (fallback)
            if '평가:' in line or 'rating:' in line_lower:
                if '긍정' in line or 'positive' in line_lower or '높음' in line:
                    signal = 'buy'
                break

        # 분할매수 전략 찾기 (여러 줄 가능)
        split_strategy_lines = []
        in_split_section = False
        for line in lines:
            if '분할매수:' in line or '분할매수 :' in line:
                in_split_section = True
                # 첫 줄의 콜론 뒤 내용도 추가
                if ':' in line:
                    first_part = line.split(':', 1)[1].strip()
                    if first_part:
                        split_strategy_lines.append(first_part)
                continue
            if in_split_section:
                # 다음 필드가 나오면 중단
                if '근거:' in line or '경고:' in line or line.strip().startswith('['):
                    break
                # 공백이 아닌 줄만 추가
                if line.strip():
                    split_strategy_lines.append(line.strip())

        split_strategy = '\n'.join(split_strategy_lines) if split_strategy_lines else ''

        # 근거 찾기 (여러 줄 가능)
        reason_lines = []
        in_reason_section = False
        for line in lines:
            if '근거:' in line or '근거 :' in line or '이유:' in line:
                in_reason_section = True
                # 첫 줄의 콜론 뒤 내용도 추가
                if ':' in line:
                    first_part = line.split(':', 1)[1].strip()
                    if first_part:
                        reason_lines.append(first_part)
                continue
            if in_reason_section:
                # 다음 필드가 나오면 중단
                if '경고:' in line or line.strip().startswith('['):
                    break
                # 공백이 아닌 줄만 추가
                if line.strip():
                    reason_lines.append(line.strip())

        reason = ' '.join(reason_lines) if reason_lines else ''

        # 경고 찾기 (여러 줄 가능)
        warning_lines = []
        in_warning_section = False
        for line in lines:
            if '경고:' in line or '경고 :' in line:
                in_warning_section = True
                # 첫 줄의 콜론 뒤 내용도 추가
                if ':' in line:
                    first_part = line.split(':', 1)[1].strip()
                    if first_part:
                        warning_lines.append(first_part)
                continue
            if in_warning_section:
                # 다음 필드가 나오면 중단
                if line.strip().startswith('['):
                    break
                # 공백이 아닌 줄만 추가
                if line.strip():
                    warning_lines.append(line.strip())

        warning = ' '.join(warning_lines) if warning_lines else ''

        result = {
            'score': 0,  # AI는 점수 안 줌 (scoring_system이 계산)
            'signal': signal,
            'split_strategy': split_strategy,
            'confidence': 'Medium',
            'recommendation': signal,
            'reasons': [reason or response_text.strip()],
            'risks': [warning] if warning else [],
            'target_price': int(stock_data.get('current_price', 0) * 1.1),
            'stop_loss_price': int(stock_data.get('current_price', 0) * 0.95),
            'analysis_text': response_text,
        }

        logger.debug(f"AI 결정: {signal}, 분할매수: {split_strategy[:50]}..., 경고: {warning[:30] if warning else 'N/A'}")

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