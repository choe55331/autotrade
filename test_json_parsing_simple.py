"""
JSON 파싱 문제 디버깅 스크립트
API 키 없이 다양한 응답 형식을 테스트
"""

import json
import re
from typing import Dict, Any, Tuple, Optional


def parse_strategy_1_original(response_text: str) -> Tuple[bool, Optional[Dict], str]:
    """
    원본 gemini_analyzer.py의 파싱 로직 재현
    """
    try:
        import json
        import re

        cleaned_text = response_text.strip()
        json_str = None

        json_match = re.search(r'```json\s*\n(.*?)\n```', cleaned_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)

        if not json_str:
            json_match = re.search(r'```\s*\n(.*?)\n```', cleaned_text, re.DOTALL)
            if json_match:
                potential_json = json_match.group(1).strip()
                if potential_json.startswith('{'):
                    json_str = potential_json

        if not json_str:
            pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'
            json_blocks = re.findall(pattern, cleaned_text, re.DOTALL)

            if not json_blocks:
                first_brace = cleaned_text.find('{')
                last_brace = cleaned_text.rfind('}')
                if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                    json_str = cleaned_text[first_brace:last_brace+1]
            elif json_blocks:
                json_str = max(json_blocks, key=len)

        if not json_str:
            if cleaned_text.startswith('{'):
                json_str = cleaned_text

        if json_str:
            json_str = json_str.strip()
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)

            data = json.loads(json_str)
            return True, data, "Success"
        else:
            return False, None, "No JSON found in response"

    except json.JSONDecodeError as e:
        return False, None, f"JSON parse error: {str(e)}"
    except Exception as e:
        return False, None, f"Error: {str(e)}"


def parse_strategy_2_robust(response_text: str) -> Tuple[bool, Optional[Dict], str]:
    """
    개선된 파싱 로직 - 더 견고함
    """
    try:
        cleaned = response_text.strip()

        cleaned = re.sub(r'```json\s*', '', cleaned)
        cleaned = re.sub(r'```\s*', '', cleaned)

        first_brace = cleaned.find('{')
        last_brace = cleaned.rfind('}')

        if first_brace == -1 or last_brace == -1:
            return False, None, "No JSON braces found"

        json_str = cleaned[first_brace:last_brace+1]

        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

        data = json.loads(json_str)

        if 'signal' not in data:
            return False, None, "Missing 'signal' field in JSON"

        return True, data, "Robust parsing successful"

    except json.JSONDecodeError as e:
        error_context = response_text[max(0, e.pos-50):min(len(response_text), e.pos+50)]
        return False, None, f"JSON error at pos {e.pos}: {e.msg}\nContext: ...{error_context}..."
    except Exception as e:
        return False, None, f"Unexpected error: {type(e).__name__}: {str(e)}"


def parse_strategy_3_lenient(response_text: str) -> Tuple[bool, Optional[Dict], str]:
    """
    매우 관대한 파싱 - 불완전한 JSON도 처리 시도
    """
    try:
        cleaned = response_text.strip()

        first_brace = cleaned.find('{')
        if first_brace == -1:
            return False, None, "No opening brace found"

        possible_jsons = []
        pos = first_brace
        while True:
            next_brace = cleaned.find('}', pos + 1)
            if next_brace == -1:
                break

            candidate = cleaned[first_brace:next_brace+1]
            candidate = re.sub(r',(\s*[}\]])', r'\1', candidate)

            try:
                data = json.loads(candidate)
                if 'signal' in data:
                    possible_jsons.append((len(candidate), data))
            except:
                pass

            pos = next_brace

        if possible_jsons:
            longest = max(possible_jsons, key=lambda x: x[0])
            return True, longest[1], f"Lenient parsing successful (found {len(possible_jsons)} candidates)"

        return False, None, "No valid JSON with 'signal' field found"

    except Exception as e:
        return False, None, f"Lenient parsing error: {str(e)}"


TEST_CASES = [
    {
        'name': 'Normal JSON',
        'response': '''```json
{
  "signal": "buy",
  "confidence": 0.8,
  "reasons": ["Good momentum"]
}
```''',
        'expected_signal': 'buy'
    },

    {
        'name': 'JSON without code block',
        'response': '''{
  "signal": "hold",
  "confidence": 0.5
}''',
        'expected_signal': 'hold'
    },

    {
        'name': 'JSON with surrounding text',
        'response': '''Here is my analysis:

{
  "signal": "sell",
  "confidence": 0.9,
  "reasons": ["Overbought"]
}

This is based on technical indicators.''',
        'expected_signal': 'sell'
    },

    {
        'name': 'JSON with trailing comma',
        'response': '''{
  "signal": "buy",
  "confidence": 0.7,
}''',
        'expected_signal': 'buy'
    },

    {
        'name': 'JSON with newline issues',
        'response': '''
{
  "signal": "buy",
  "confidence": 0.8
}''',
        'expected_signal': 'buy'
    },

    {
        'name': 'Nested JSON',
        'response': '''{
  "signal": "buy",
  "confidence": 0.8,
  "details": {
    "reason": "Strong trend",
    "score": 85
  }
}''',
        'expected_signal': 'buy'
    },

    {
        'name': 'Problematic quote issues',
        'response': '''{
  "signal": "buy",
  "confidence": 0.8,
  "reasons": ["Strong momentum", "High volume"],
}''',
        'expected_signal': 'buy'
    },

    {
        'name': 'Real error case with newline before signal',
        'response': '''{
 "signal": "buy",
  "confidence": 0.8
}''',
        'expected_signal': 'buy'
    },

    {
        'name': 'Minimal JSON',
        'response': '''{"signal": "hold"}''',
        'expected_signal': 'hold'
    },

    {
        'name': 'Complex realistic JSON',
        'response': '''```json
{
  "signal": "buy",
  "confidence": 0.85,
  "reasons": [
    "Strong upward momentum with 2.5% gain",
    "High trading volume indicating interest",
    "Price above key moving averages"
  ],
  "risks": [
    "Market volatility",
    "Potential resistance at 72,"000" KRW"
  ],
  "target_price": 75000,
  "stop_loss": 67000
}
```''',
        'expected_signal': 'buy'
    },
]


def run_tests():
    """모든 테스트 케이스 실행"""

    print("="*80)
    print("JSON 파싱 전략 테스트")
    print("="*80)

    strategies = [
        ('Original', parse_strategy_1_original),
        ('Robust', parse_strategy_2_robust),
        ('Lenient', parse_strategy_3_lenient),
    ]

    results = {name: {'success': 0, 'fail': 0} for name, _ in strategies}

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{'='*80}")
        print(f"테스트 케이스")
        print(f"{'='*80}")
        print(f"응답 샘플:\n{test_case['response'][:100]}...")
        print(f"예상 신호: {test_case['expected_signal']}")
        print()

        for strategy_name, strategy_func in strategies:
            success, data, msg = strategy_func(test_case['response'])

            if success and data and data.get('signal') == test_case['expected_signal']:
                print(f"  [OK] {strategy_name:12} - SUCCESS: {msg}")
                results[strategy_name]['success'] += 1
            else:
                print(f"  [X] {strategy_name:12} - FAILED: {msg}")
                results[strategy_name]['fail'] += 1

    print(f"\n\n{'='*80}")
    print("[CHART] 결과 요약")
    print(f"{'='*80}")

    for strategy_name, counts in results.items():
        total = counts['success'] + counts['fail']
        success_rate = counts['success'] / total * 100 if total > 0 else 0
        print(f"\n{strategy_name}:")
        print(f"  성공: {counts['success']}/{total} ({success_rate:.1f}%)")
        print(f"  실패: {counts['fail']}/{total}")

    best_strategy = max(results.items(), key=lambda x: x[1]['success'])
    print(f"\n🏆 최고 전략: {best_strategy[0]} (성공률: {best_strategy[1]['success']}/{len(TEST_CASES)})")

    print(f"\n💡 추천사항:")
    if best_strategy[1]['success'] == len(TEST_CASES):
        print(f"  {best_strategy[0]} 전략이 모든 테스트를 통과했습니다!")
        print(f"  이 전략을 gemini_analyzer.py에 적용하세요.")
    else:
        print(f"  {best_strategy[0]} 전략이 가장 좋지만, 여전히 일부 케이스에서 실패합니다.")
        print(f"  실패한 케이스를 분석하여 전략을 개선하세요.")


if __name__ == '__main__':
    run_tests()

    print(f"\n\n{'='*80}")
    print("[SEARCH] 에러 케이스 상세 분석")
    print(f"{'='*80}")

    error_response = '''{
 "signal": "buy"
}'''

    print(f"\n보고된 에러 형식 테스트:")
    print(f"응답: {repr(error_response)}")

    for strategy_name, strategy_func in [
        ('Original', parse_strategy_1_original),
        ('Robust', parse_strategy_2_robust),
        ('Lenient', parse_strategy_3_lenient),
    ]:
        success, data, msg = strategy_func(error_response)
        print(f"\n{strategy_name}:")
        print(f"  성공: {success}")
        print(f"  메시지: {msg}")
        if data:
            print(f"  데이터: {data}")
