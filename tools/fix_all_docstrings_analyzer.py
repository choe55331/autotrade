#!/usr/bin/env python3
"""analyzer.py의 모든 docstring 문제를 완벽하게 수정"""
import re

with open('research/analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

original_content = content

# 1. 함수 정의 후 바로 한글/영어 텍스트가 나오는 경우 (docstring 없음)
# Pattern: def ...): \n    한글텍스트 \n    (Args:|Returns:|code)
pattern1 = r'(\n    def [^\n]+:\n)(        )([가-힣A-Z][^\n]+)\n(        )(Args:|Returns:|[a-z_]+\s*=)'
content = re.sub(
    pattern1,
    r'\1\2"""\n\2\3\n\2"""\n\4\5',
    content
)

# 2. Args:나 Returns: 섹션이 있는데 opening """ 없는 경우
pattern2 = r'(\n    def [^\n]+:\n)(        )([가-힣A-Z][^\n]+\n(?:        [^\n]*\n)*?)(        )(Args:)'
content = re.sub(
    pattern2,
    r'\1\2"""\n\2\3\2\5',
    content
)

# 3. Returns: 섹션 뒤에 closing """ 없는 경우
pattern3 = r'(Returns:\n(?:            [^\n]+\n)+)(        )([a-z_]+\s*=|if |return )'
content = re.sub(
    pattern3,
    r'\1        """\n\2\3',
    content
)

# 4. Args: 섹션 뒤에 closing """ 없는 경우 (Returns 없음)
pattern4 = r'(Args:\n(?:            [^\n]+\n)+)(        )([a-z_]+\s*=|if |return )'
content = re.sub(
    pattern4,
    r'\1        """\n\2\3',
    content
)

# 5. 단순 docstring (한 줄) - opening/closing """ 모두 없음
pattern5 = r'(\n    def [^\n]+:\n)(        )([가-힣A-Z][^\n]+)\n(        )([a-z_]+\s*=|if |return )'
content = re.sub(
    pattern5,
    r'\1\2"""\3"""\n\4\5',
    content
)

# 파일 저장
if content != original_content:
    with open('research/analyzer.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Docstring 패턴 수정 완료")
else:
    print("변경사항 없음")
