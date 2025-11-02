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
            self.model_name = model_name or GEMINI_MODEL_NAME
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
        analysis_type: str = 'comprehensive'
    ) -> Dict[str, Any]:
        """
        종목 분석

        Args:
            stock_data: 종목 데이터
            analysis_type: 분석 유형

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
                print(f"        [시도 {attempt + 1}/{max_retries}] 프롬프트 생성 중...")
                # 프롬프트 생성
                prompt = self._create_stock_analysis_prompt(stock_data, analysis_type)
                print(f"        [시도 {attempt + 1}/{max_retries}] Gemini API 호출 중... (타임아웃: 30초)")

                # Gemini API 호출 (타임아웃 30초)
                import google.generativeai as genai

                # 생성 설정 (타임아웃 및 안정성 설정)
                generation_config = genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                )

                api_start = time.time()
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    request_options={'timeout': 30}  # 30초 타임아웃
                )
                api_elapsed = time.time() - api_start
                print(f"        [시도 {attempt + 1}/{max_retries}] Gemini API 응답 완료 ({api_elapsed:.2f}초)")

                # 응답 파싱
                print(f"        [시도 {attempt + 1}/{max_retries}] 응답 파싱 중...")
                result = self._parse_stock_analysis_response(response.text, stock_data)
                print(f"        [시도 {attempt + 1}/{max_retries}] 파싱 완료: score={result.get('score')}, signal={result.get('signal')}")

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
                print(f"        [시도 {attempt + 1}/{max_retries}] ❌ 에러 발생: {error_msg}")
                import traceback
                traceback.print_exc()
                logger.warning(f"종목 분석 시도 {attempt + 1}/{max_retries} 실패: {error_msg}")

                # 마지막 시도가 아니면 재시도
                if attempt < max_retries - 1:
                    print(f"        {retry_delay}초 후 재시도...")
                    logger.info(f"{retry_delay}초 후 재시도...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 지수 백오프
                else:
                    # 모든 시도 실패
                    print(f"        ❌ 모든 시도 실패: {error_msg}")
                    logger.error(f"종목 분석 최종 실패: {error_msg}")
                    self.update_statistics(False)
                    return self._get_error_result(f"최대 재시도 초과: {error_msg}")
    
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
    
    def _create_stock_analysis_prompt(
        self,
        stock_data: Dict[str, Any],
        analysis_type: str
    ) -> str:
        """종목 분석 프롬프트 생성"""
        stock_code = stock_data.get('stock_code', '')
        stock_name = stock_data.get('stock_name', '')
        current_price = stock_data.get('current_price', 0)
        change_rate = stock_data.get('change_rate', 0)
        volume = stock_data.get('volume', 0)
        
        prompt = f"""
당신은 전문 주식 애널리스트입니다. 다음 종목을 분석해주세요.

**종목 정보:**
- 종목코드: {stock_code}
- 종목명: {stock_name}
- 현재가: {current_price:,}원
- 등락률: {change_rate:+.2f}%
- 거래량: {volume:,}주

**기술적 지표:**
{self._format_technical_data(stock_data.get('technical', {}))}

**투자자 동향:**
{self._format_investor_data(stock_data.get('investor', {}))}

**분석 요청:**
다음 형식으로 분석 결과를 제공해주세요:

점수: [0~10점 사이의 투자 점수]
신호: [buy/sell/hold 중 하나]
신뢰도: [Low/Medium/High 중 하나]
추천: [한 줄 추천 문구]
이유: [매수/매도/보유 이유 3가지, 각각 한 줄로]
리스크: [주요 리스크 2가지, 각각 한 줄로]
목표가: [예상 목표가격]
손절가: [권장 손절가격]
"""
        
        return prompt
    
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
        """종목 분석 응답 파싱"""
        # 간단한 파싱 (실제로는 더 정교한 파싱 필요)
        lines = response_text.strip().split('\n')
        
        result = {
            'score': 7.0,
            'signal': 'hold',
            'confidence': 'Medium',
            'recommendation': '보유 추천',
            'reasons': [],
            'risks': [],
            'target_price': int(stock_data.get('current_price', 0) * 1.1),
            'stop_loss_price': int(stock_data.get('current_price', 0) * 0.95),
            'analysis_text': response_text,
        }
        
        # 키워드 기반 파싱
        for line in lines:
            line_lower = line.lower()
            
            if '점수:' in line or 'score:' in line_lower:
                try:
                    score = float(''.join(filter(str.isdigit, line.split(':')[1][:3])))
                    result['score'] = min(max(score, 0), 10)
                except:
                    pass
            
            elif '신호:' in line or 'signal:' in line_lower:
                if 'buy' in line_lower or '매수' in line:
                    result['signal'] = 'buy'
                elif 'sell' in line_lower or '매도' in line:
                    result['signal'] = 'sell'
            
            elif '신뢰도:' in line or 'confidence:' in line_lower:
                if 'high' in line_lower or '높음' in line:
                    result['confidence'] = 'High'
                elif 'low' in line_lower or '낮음' in line:
                    result['confidence'] = 'Low'
        
        logger.debug(f"분석 결과 파싱: 점수={result['score']}, 신호={result['signal']}")
        
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