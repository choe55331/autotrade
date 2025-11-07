#!/usr/bin/env python3
"""복잡한 docstring을 간단하게 만들어서 syntax 에러 제거"""
import re
from pathlib import Path

def simplify_docstrings(filepath):
    """파일의 모든 복잡한 docstring을 제거/단순화"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. 이모지 제거
    content = content.replace('⭐', '[STAR]')
    content = content.replace('⚠️', 'WARNING')
    content = content.replace('✅', '[OK]')
    content = content.replace('❌', '[ERROR]')

    # 2. 모든 standalone """ 제거
    lines = content.split('\n')
    cleaned = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # standalone """ 체크 (들여쓰기 + """ + 빈 줄)
        if re.match(r'^\s+"""\s*$', line):
            # 다음 줄이 코드이면 제거
            if i + 1 < len(lines):
                next_line = lines[i+1].strip()
                if next_line and not next_line.startswith('"""') and \
                   not next_line.startswith(('#', 'def ', 'class ')):
                    # 이전 줄이 함수 정의가 아니면 제거
                    if i > 0:
                        prev_line = lines[i-1].strip()
                        if not prev_line.endswith(':'):
                            i += 1
                            continue

        cleaned.append(line)
        i += 1

    content = '\n'.join(cleaned)

    # 3. 복잡한 multi-line docstring을 간단한 한 줄로 교체
    # Pattern: """로 시작하는 multi-line docstring
    # """...\n...Args:...\n...Returns:...\n...""" -> """Simple docstring"""

    def simplify_multiline(match):
        """복잡한 docstring을 한 줄로 압축"""
        indent = match.group(1)
        # 첫 줄의 한글/영어 텍스트만 추출
        first_line = match.group(2).strip()
        if first_line:
            # 특수문자 제거하고 첫 30자만
            first_line = first_line.split('\n')[0][:50]
            return f'{indent}"""{first_line}"""'
        else:
            return f'{indent}"""Method"""'

    # Args/Returns 있는 복잡한 docstring 제거
    content = re.sub(
        r'(\n        )"""\n        ([^\n]*)\n(?:.*?Args:.*?)?(?:.*?Returns:.*?)?        """',
        simplify_multiline,
        content,
        flags=re.DOTALL
    )

    # 4. 함수 정의 후 한글 텍스트만 있는 경우 (docstring 없음) -> pass 추가
    content = re.sub(
        r'(\n    def [^\n]+:\n)(        )([가-힣A-Z][^\n]+)\n(        )([a-z_]+\s*=)',
        r'\1\2# \3\n\4\5',
        content
    )

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# 5개 파일 처리
files = [
    'research/screener.py',
    'research/strategy_manager.py',
    'strategy/scoring_system.py',
    'virtual_trading/virtual_trader.py',
    'virtual_trading/trade_logger.py'
]

print("복잡한 docstring 제거 중...")
for filepath in files:
    path = Path(filepath)
    if path.exists():
        if simplify_docstrings(filepath):
            print(f"✓ {filepath}")
        else:
            print(f"○ {filepath}")

print("\n완료!")
