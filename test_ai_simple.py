"""
간단한 AI 분석 테스트
기존 GeminiAnalyzer를 사용하여 테스트
"""

import sys
import os
import json

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai.gemini_analyzer import GeminiAnalyzer


def test_simple_prompt():
    """간단한 프롬프트 테스트"""
    print("=" * 80)
    print("테스트 1: 간단한 프롬프트")
    print("=" * 80)

    analyzer = GeminiAnalyzer()

    # 초기화
    if not analyzer.initialize():
        print("❌ Gemini 초기화 실패")
        return False

    # 간단한 프롬프트
    simple_prompt = """주식을 분석하고 JSON으로 답변하세요.

종목: 삼성전자 (005930)
현재가: 70,000원
등락률: +2.5%
점수: 300점

다음 JSON 형식으로만 답변하세요:
```json
{
  "signal": "BUY",
  "score": 8.0,
  "confidence_level": "High",
  "reasoning": "간단한 분석 이유 한 줄"
}
```

반드시 JSON만 출력하고 다른 설명은 하지 마세요.
"""

    print(f"\n📝 프롬프트:\n{simple_prompt}")
    print("\n⏳ AI 응답 대기 중...")

    try:
        # Gemini API 직접 호출
        response = analyzer.model.generate_content(simple_prompt)
        response_text = response.text

        print(f"\n✅ 응답 받음 ({len(response_text)} chars):")
        print("-" * 80)
        print(response_text)
        print("-" * 80)

        # JSON 파싱 시도
        parsed = try_parse_json(response_text)
        if parsed:
            print("\n✅ JSON 파싱 성공!")
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
            return True
        else:
            print("\n❌ JSON 파싱 실패")
            return False

    except Exception as e:
        print(f"\n❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_minimal_prompt():
    """최소한의 프롬프트"""
    print("\n" + "=" * 80)
    print("테스트 2: 최소한의 프롬프트")
    print("=" * 80)

    analyzer = GeminiAnalyzer()
    if not analyzer.initialize():
        return False

    minimal_prompt = """삼성전자 70000원

JSON:
{"signal": "BUY", "score": 8}
"""

    print(f"\n📝 프롬프트:\n{minimal_prompt}")
    print("\n⏳ AI 응답 대기 중...")

    try:
        response = analyzer.model.generate_content(minimal_prompt)
        response_text = response.text

        print(f"\n✅ 응답 받음:")
        print(response_text[:500])

        parsed = try_parse_json(response_text)
        if parsed:
            print("\n✅ JSON 파싱 성공!")
            return True
        else:
            print("\n❌ JSON 파싱 실패")
            return False

    except Exception as e:
        print(f"\n❌ 에러: {e}")
        return False


def test_current_analyzer():
    """현재 analyzer의 analyze_stock 메서드 테스트"""
    print("\n" + "=" * 80)
    print("테스트 3: 현재 GeminiAnalyzer.analyze_stock() 메서드")
    print("=" * 80)

    analyzer = GeminiAnalyzer()
    if not analyzer.initialize():
        return False

    # 테스트 데이터
    stock_data = {
        'stock_code': '005930',
        'stock_name': '삼성전자',
        'current_price': 70000,
        'change_rate': 2.5,
        'volume': 15000000,
        'institutional_net_buy': 50000000,
        'foreign_net_buy': 30000000,
        'bid_ask_ratio': 1.2
    }

    score_info = {
        'score': 300,
        'max_score': 440,
        'percentage': 68.2,
        'breakdown': {
            '기관순매수': 40,
            '외국인순매수': 30,
            '거래량': 35,
        }
    }

    print("\n📊 테스트 데이터:")
    print(f"  종목: {stock_data['stock_name']} ({stock_data['stock_code']})")
    print(f"  현재가: {stock_data['current_price']:,}원")
    print(f"  점수: {score_info['score']}/440")

    print("\n⏳ AI 분석 중...")

    try:
        result = analyzer.analyze_stock(
            stock_data=stock_data,
            score_info=score_info
        )

        if result and result.get('signal'):
            print("\n✅ 분석 성공!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return True
        else:
            print("\n❌ 분석 실패")
            print(f"결과: {result}")
            return False

    except Exception as e:
        print(f"\n❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return False


def try_parse_json(text):
    """다양한 방법으로 JSON 파싱 시도"""
    import re

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

    # 방법 3: 첫 { 부터 마지막 } 까지
    try:
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            json_str = text[start:end+1]
            return json.loads(json_str)
    except:
        pass

    # 방법 4: 정규식으로 JSON 객체 추출
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


def main():
    print("🔬 AI 분석 간단 테스트")
    print("=" * 80)

    # API 키 확인
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("설정: export GEMINI_API_KEY='your-api-key'")
        return

    print(f"✅ API 키 확인: {api_key[:10]}...{api_key[-5:]}")

    # 테스트 실행
    results = []

    print("\n" + "🚀" * 40)
    print("테스트 시작")
    print("🚀" * 40)

    # 테스트 1
    try:
        result = test_simple_prompt()
        results.append(("간단한 프롬프트", result))
    except Exception as e:
        print(f"테스트 1 예외: {e}")
        results.append(("간단한 프롬프트", False))

    input("\n다음 테스트를 실행하려면 Enter...")

    # 테스트 2
    try:
        result = test_minimal_prompt()
        results.append(("최소 프롬프트", result))
    except Exception as e:
        print(f"테스트 2 예외: {e}")
        results.append(("최소 프롬프트", False))

    input("\n다음 테스트를 실행하려면 Enter...")

    # 테스트 3
    try:
        result = test_current_analyzer()
        results.append(("현재 analyze_stock", result))
    except Exception as e:
        print(f"테스트 3 예외: {e}")
        results.append(("현재 analyze_stock", False))

    # 결과 요약
    print("\n" + "=" * 80)
    print("📊 최종 결과")
    print("=" * 80)

    for test_name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{status}: {test_name}")

    success_count = sum(1 for _, s in results if s)
    print(f"\n총 {success_count}/{len(results)} 테스트 성공")

    if success_count > 0:
        print("\n💡 권장 사항: 성공한 테스트의 프롬프트 방식을 실제 코드에 적용하세요.")
    else:
        print("\n⚠️ 모든 테스트 실패: Gemini API 키 또는 네트워크를 확인하세요.")


if __name__ == '__main__':
    main()
