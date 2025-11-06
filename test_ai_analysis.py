"""
AI 분석 테스트 스크립트
다양한 프롬프트와 파싱 방법을 시도하여 성공 조건을 찾습니다.
"""

import os
import sys
import json
import re
from datetime import datetime

# 환경 변수 설정
os.environ.setdefault('GEMINI_API_KEY', os.getenv('GEMINI_API_KEY', ''))

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    print("❌ google-generativeai 패키지가 설치되지 않았습니다.")
    print("설치: pip install google-generativeai")
    sys.exit(1)


class AIAnalysisTester:
    """AI 분석 테스트"""

    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            print("❌ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
            sys.exit(1)

        genai.configure(api_key=self.api_key)
        print(f"✅ Gemini API 초기화 완료")

        # 테스트용 샘플 데이터
        self.sample_stock_data = {
            'stock_code': '005930',
            'stock_name': '삼성전자',
            'current_price': 70000,
            'change_rate': 2.5,
            'volume': 15000000,
            'score': 300,
            'institutional_net_buy': 50000000,
            'foreign_net_buy': 30000000,
            'bid_ask_ratio': 1.2
        }

    def test_1_simple_json(self):
        """테스트 1: 가장 간단한 JSON 요청"""
        print("\n" + "="*80)
        print("테스트 1: 가장 간단한 JSON 요청")
        print("="*80)

        prompt = """다음 주식을 분석하고 JSON으로 답변하세요.

종목: 삼성전자 (005930)
현재가: 70,000원
등락률: +2.5%

JSON 형식으로만 답변:
{
  "signal": "buy",
  "confidence": 0.8,
  "reason": "간단한 이유"
}
"""

        return self._try_analysis(prompt, "gemini-pro")

    def test_2_with_markdown(self):
        """테스트 2: 마크다운 코드 블록으로 감싸기"""
        print("\n" + "="*80)
        print("테스트 2: 마크다운 코드 블록 요청")
        print("="*80)

        prompt = """다음 주식을 분석하세요.

종목: 삼성전자 (005930)
현재가: 70,000원

아래 형식으로 답변하세요:

```json
{
  "signal": "buy",
  "confidence": 0.8,
  "reason": "분석 이유"
}
```
"""

        return self._try_analysis(prompt, "gemini-pro")

    def test_3_structured_output(self):
        """테스트 3: 구조화된 출력 요청"""
        print("\n" + "="*80)
        print("테스트 3: 구조화된 JSON 스키마")
        print("="*80)

        prompt = """주식 분석 요청:
- 종목: 삼성전자 (005930)
- 현재가: 70,000원
- 점수: 300점

다음 JSON 스키마를 정확히 따라주세요:

{
  "signal": "buy" | "hold" | "sell",
  "confidence": 0.0-1.0,
  "score": 0-10,
  "analysis": {
    "strengths": ["강점1", "강점2"],
    "weaknesses": ["약점1"],
    "recommendation": "추천사항"
  }
}

반드시 유효한 JSON만 출력하세요. 설명은 제외하고 JSON만 출력하세요.
"""

        return self._try_analysis(prompt, "gemini-pro")

    def test_4_gemini_15(self):
        """테스트 4: Gemini 1.5 모델 사용"""
        print("\n" + "="*80)
        print("테스트 4: Gemini 1.5 Pro 모델")
        print("="*80)

        prompt = """간단한 주식 분석:

삼성전자 (005930) - 70,000원

JSON으로 답변:
{"signal": "buy", "reason": "이유"}
"""

        return self._try_analysis(prompt, "gemini-1.5-pro-latest")

    def test_5_gemini_flash(self):
        """테스트 5: Gemini Flash 모델 (빠른 모델)"""
        print("\n" + "="*80)
        print("테스트 5: Gemini 1.5 Flash 모델 (고속)")
        print("="*80)

        prompt = """주식 분석 (JSON만 출력):

{"stock": "삼성전자", "price": 70000}

출력 형식:
{"signal": "buy", "confidence": 0.8}
"""

        return self._try_analysis(prompt, "gemini-1.5-flash-latest")

    def test_6_temperature_zero(self):
        """테스트 6: Temperature=0 (결정론적)"""
        print("\n" + "="*80)
        print("테스트 6: Temperature=0 (결정론적 응답)")
        print("="*80)

        prompt = """주식: 삼성전자 70,000원

JSON 응답:
{
  "signal": "buy",
  "score": 7.5
}
"""

        return self._try_analysis(prompt, "gemini-pro", temperature=0.0)

    def test_7_minimal_prompt(self):
        """테스트 7: 최소한의 프롬프트"""
        print("\n" + "="*80)
        print("테스트 7: 극도로 간단한 프롬프트")
        print("="*80)

        prompt = """삼성전자 분석:
{"signal": "buy"}
"""

        return self._try_analysis(prompt, "gemini-pro")

    def test_8_korean_only(self):
        """테스트 8: 한국어만 사용"""
        print("\n" + "="*80)
        print("테스트 8: 순수 한국어 프롬프트")
        print("="*80)

        prompt = """삼성전자 주식을 분석해주세요.
현재가: 70,000원

다음 형식으로만 답변:
{
  "신호": "매수",
  "신뢰도": 0.8,
  "이유": "분석 이유"
}
"""

        return self._try_analysis(prompt, "gemini-pro")

    def test_9_step_by_step(self):
        """테스트 9: 단계별 분석 요청"""
        print("\n" + "="*80)
        print("테스트 9: 단계별 분석 (Chain of Thought)")
        print("="*80)

        prompt = """삼성전자 (70,000원) 분석:

1단계: 가격 분석
2단계: 신호 결정
3단계: JSON 출력

최종 JSON만 출력:
{"signal": "buy", "confidence": 0.8}
"""

        return self._try_analysis(prompt, "gemini-pro")

    def test_10_with_example(self):
        """테스트 10: 예시와 함께 요청"""
        print("\n" + "="*80)
        print("테스트 10: Few-shot Learning (예시 제공)")
        print("="*80)

        prompt = """주식 분석 예시:

입력: 현대차 50,000원
출력: {"signal": "buy", "score": 8.0}

입력: LG전자 90,000원
출력: {"signal": "hold", "score": 6.5}

이제 분석:
입력: 삼성전자 70,000원
출력:"""

        return self._try_analysis(prompt, "gemini-pro")

    def _try_analysis(self, prompt, model_name, temperature=0.7):
        """실제 분석 시도"""
        try:
            print(f"\n📝 프롬프트 ({len(prompt)} chars):")
            print("-" * 80)
            print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
            print("-" * 80)

            # 모델 생성
            model = genai.GenerativeModel(model_name)

            # 생성 설정
            generation_config = {
                'temperature': temperature,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 2048,
            }

            # 응답 생성
            print(f"\n⏳ {model_name} 응답 대기 중...")
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )

            response_text = response.text
            print(f"\n✅ 응답 받음 ({len(response_text)} chars)")
            print("-" * 80)
            print(response_text)
            print("-" * 80)

            # JSON 파싱 시도 (다양한 방법)
            parsed_data = self._try_parse_json(response_text)

            if parsed_data:
                print(f"\n✅ JSON 파싱 성공!")
                print(json.dumps(parsed_data, indent=2, ensure_ascii=False))
                return True, parsed_data
            else:
                print(f"\n❌ JSON 파싱 실패")
                return False, None

        except Exception as e:
            print(f"\n❌ 에러 발생: {e}")
            return False, None

    def _try_parse_json(self, text):
        """다양한 JSON 파싱 방법 시도"""

        # 방법 1: 직접 파싱
        try:
            return json.loads(text)
        except:
            pass

        # 방법 2: 코드 블록 추출
        try:
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
        except:
            pass

        # 방법 3: 첫 번째 { 부터 마지막 } 까지
        try:
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = text[start:end+1]
                return json.loads(json_str)
        except:
            pass

        # 방법 4: 줄바꿈 제거 후 재시도
        try:
            cleaned = text.strip().replace('\n', ' ')
            return json.loads(cleaned)
        except:
            pass

        # 방법 5: 정규식으로 JSON 객체 추출
        try:
            pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                for match in matches:
                    try:
                        return json.loads(match)
                    except:
                        continue
        except:
            pass

        return None

    def run_all_tests(self):
        """모든 테스트 실행"""
        print("\n" + "🚀" * 40)
        print("AI 분석 종합 테스트 시작")
        print("🚀" * 40)

        tests = [
            self.test_1_simple_json,
            self.test_2_with_markdown,
            self.test_3_structured_output,
            self.test_4_gemini_15,
            self.test_5_gemini_flash,
            self.test_6_temperature_zero,
            self.test_7_minimal_prompt,
            self.test_8_korean_only,
            self.test_9_step_by_step,
            self.test_10_with_example,
        ]

        results = []

        for i, test_func in enumerate(tests, 1):
            try:
                success, data = test_func()
                results.append({
                    'test': test_func.__doc__,
                    'success': success,
                    'data': data
                })

                if success:
                    print(f"\n✅ 테스트 {i} 성공!")
                else:
                    print(f"\n❌ 테스트 {i} 실패")

            except Exception as e:
                print(f"\n❌ 테스트 {i} 예외 발생: {e}")
                results.append({
                    'test': test_func.__doc__,
                    'success': False,
                    'error': str(e)
                })

            print("\n" + "-" * 80)
            input("다음 테스트를 실행하려면 Enter를 누르세요...")

        # 최종 결과 요약
        print("\n" + "=" * 80)
        print("📊 최종 결과 요약")
        print("=" * 80)

        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)

        print(f"\n성공: {success_count}/{total_count}")
        print(f"실패: {total_count - success_count}/{total_count}")

        print("\n✅ 성공한 테스트:")
        for i, result in enumerate(results, 1):
            if result['success']:
                print(f"  {i}. {result['test']}")

        print("\n❌ 실패한 테스트:")
        for i, result in enumerate(results, 1):
            if not result['success']:
                print(f"  {i}. {result['test']}")

        # 권장 방법 출력
        if success_count > 0:
            print("\n" + "=" * 80)
            print("💡 권장 방법")
            print("=" * 80)

            for i, result in enumerate(results, 1):
                if result['success']:
                    print(f"\n테스트 {i}가 성공했습니다!")
                    print(f"이 방법을 실제 코드에 적용하세요.")
                    break


def main():
    """메인 함수"""
    tester = AIAnalysisTester()

    print("AI 분석 테스트 프로그램")
    print("=" * 80)
    print("1. 모든 테스트 실행")
    print("2. 개별 테스트 선택")
    print("=" * 80)

    choice = input("선택 (1/2): ").strip()

    if choice == '1':
        tester.run_all_tests()
    else:
        print("\n개별 테스트:")
        print("1. 간단한 JSON")
        print("2. 마크다운 코드 블록")
        print("3. 구조화된 출력")
        print("4. Gemini 1.5")
        print("5. Gemini Flash")
        print("6. Temperature=0")
        print("7. 최소 프롬프트")
        print("8. 한국어만")
        print("9. 단계별 분석")
        print("10. Few-shot Learning")

        test_num = input("\n테스트 번호 선택: ").strip()

        test_map = {
            '1': tester.test_1_simple_json,
            '2': tester.test_2_with_markdown,
            '3': tester.test_3_structured_output,
            '4': tester.test_4_gemini_15,
            '5': tester.test_5_gemini_flash,
            '6': tester.test_6_temperature_zero,
            '7': tester.test_7_minimal_prompt,
            '8': tester.test_8_korean_only,
            '9': tester.test_9_step_by_step,
            '10': tester.test_10_with_example,
        }

        if test_num in test_map:
            test_map[test_num]()
        else:
            print("잘못된 선택입니다.")


if __name__ == '__main__':
    main()
