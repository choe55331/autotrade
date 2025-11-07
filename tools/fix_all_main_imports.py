#!/usr/bin/env python3
"""main.py가 import하는 모든 파일의 syntax 에러 일괄 수정"""
import re
from pathlib import Path

def fix_docstrings(content):
    """docstring 문제 수정"""
    # 1. 이모지 제거
    content = content.replace('[STAR]', '[STAR]')
    content = content.replace('[WARNING]️', 'WARNING')
    content = content.replace('[OK]', '[OK]')
    content = content.replace('[X]', '[ERROR]')

    # 2. 함수 정의 후 한글 텍스트 (docstring 없음)
    content = re.sub(
        r'(\n    def [^\n]+:\n)(        )([가-힣A-Z][^\n]+)\n(        )(Args:|Returns:|[a-z_]+\s*=)',
        r'\1\2"""\n\2\3\n\2"""\n\4\5',
        content
    )

    # 3. Args: 있는데 opening """ 없음
    """
    content = re.sub(
        r'(\n    def [^\n]+:\n)(        )([가-힣A-Z][^\n]+\n(?:        [^\n]*\n)*?)(        )(Args:)',
        r'\1\2"""\n\2\3\2\5',
        content
    )

    # 4. Returns: 뒤에 closing """ 없음
    content = re.sub(
        r'(Returns:\n(?:            [^\n]+\n)+)(        )([a-z_]+\s*=|if |return |try:)',
        r'\1        """\n\2\3',
        content
    )

    # 5. Args: 뒤에 closing """ 없음
    content = re.sub(
        r'(Args:\n(?:            [^\n]+\n)+)(        )([a-z_]+\s*=|if |return |try:)',
        r'\1        """\n\2\3',
        content
    )

    # 6. 단순 docstring (한 줄)
    """
    content = re.sub(
        r'(\n    def [^\n]+:\n)(        )([가-힣A-Z][^\n]+)\n(        )([a-z_]+\s*=|if |return |try:)',
        r'\1\2"""\3"""\n\4\5',
        content
    )

    return content

def remove_standalone_quotes(content):
    """standalone triple quotes 제거"""
    lines = content.split('\n')
    cleaned = []

    for i, line in enumerate(lines):
        # standalone """ 체크
        """
        if re.match(r'^\s+"""\s*$', line):
            # 이전 줄이 함수/클래스 정의가 아니고
            """
            if i > 0 and not lines[i-1].strip().endswith(':'):
                # 다음 줄이 코드이면 제거
                if i + 1 < len(lines):
                    next_line = lines[i+1].strip()
                    if next_line and re.match(r'^(if |elif |for |while |return |[a-z_]+\s*=)', next_line):
                        continue  # 이 줄 건너뛰기

        cleaned.append(line)

    return '\n'.join(cleaned)

# 수정할 파일 목록
files = [
    'research/screener.py',
    'research/strategy_manager.py',
    'strategy/scoring_system.py',
    'virtual_trading/virtual_trader.py',
    'virtual_trading/trade_logger.py'
]

fixed_count = 0
for filepath in files:
    path = Path(filepath)
    if not path.exists():
        print(f"[WARNING]️  파일 없음: {filepath}")
        continue

    try:
        with open(path, 'r', encoding='utf-8') as f:
            original = f.read()

        # 수정 적용
        content = fix_docstrings(original)
        content = remove_standalone_quotes(content)

        if content != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ {filepath}")
            fixed_count += 1
        else:
            print(f"○ {filepath} (변경 없음)")

    except Exception as e:
        print(f"✗ {filepath}: {e}")

print(f"\n[OK] {fixed_count}개 파일 수정 완료")
