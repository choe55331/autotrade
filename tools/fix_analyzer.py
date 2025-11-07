#!/usr/bin/env python3
"""analyzer.py 전용 docstring 수정 스크립트"""
import re
from pathlib import Path

def fix_analyzer():
    """analyzer.py의 모든 docstring 문제를 수정"""
    filepath = Path('research/analyzer.py')

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 패턴 1: 함수 정의 후 한글로 시작하는 docstring (Returns: 있는 경우)
    content = re.sub(
        r'(def [^:]+:\n)(    )([가-힣][^\n]+\n(?:.*?\n)*?)(    )(Returns:)',
        lambda m: f"{m.group(1)}{m.group(2)}\"\"\"{m.group(3)}{m.group(4)}{m.group(5)}",
        content,
        flags=re.MULTILINE
    )

    # 패턴 2: 함수 정의 후 한글로 시작하는 docstring (Args: 있는 경우)
    content = re.sub(
        r'(def [^:]+:\n)(    )([가-힣][^\n]+\n(?:\s*\n)?)(    )(Args:)',
        lambda m: f"{m.group(1)}{m.group(2)}\"\"\"{m.group(3)}{m.group(4)}{m.group(5)}",
        content,
        flags=re.MULTILINE
    )

    # 패턴 3: Returns 섹션 후 닫는 """ 추가 (코드가 바로 시작하는 경우)
    content = re.sub(
        r'(Returns:\n(?:        [^\n]+\n)+)(    )([a-z_]+\s*=)',
        r'\1    """\n\2\3',
        content
    )

    # 패턴 4: Args 섹션만 있고 바로 코드 시작하는 경우
    content = re.sub(
        r'(Args:\n(?:        [^\n]+\n)+)(    )([a-z_]+\s*=)',
        r'\1    """\n\2\3',
        content
    )

    # 패턴 5: 단순 docstring (Args/Returns 없이 바로 코드)
    content = re.sub(
        r'(def [^:]+:\n)(    )([가-힣][^\n]+)\n(    )([a-z_]+\s*=)',
        r'\1\2"""\3"""\n\4\5',
        content
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Fixed: {filepath}")

if __name__ == '__main__':
    fix_analyzer()
