#!/usr/bin/env python3
"""main.py import 파일들 강력 수정 - analyzer.py에서 성공한 방법 사용"""
import re
from pathlib import Path

def aggressive_fix(filepath):
    """파일 읽고 강력하게 수정"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. 이모지 제거
    content = content.replace('⭐', '[STAR]')
    content = content.replace('⚠️', 'WARNING')
    content = content.replace('✅', '[OK]')
    content = content.replace('❌', '[ERROR]')

    # 2. 줄 단위로 처리
    lines = content.split('\n')
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # def 다음 줄이 한글/영어 텍스트인 경우
        if i > 0 and re.match(r'^\s+def \w+', lines[i-1]):
            # 현재 줄이 한글/영어로 시작하고 """ 없으면
            if re.match(r'^\s+[가-힣A-Z]', line) and '"""' not in line:
                # 이 줄 앞에 """ 추가
                indent = len(line) - len(line.lstrip())
                line = ' ' * indent + '"""' + line.lstrip()

                # 다음 줄들을 찾아서 닫는 """ 위치 결정
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    # Args:, Returns:, 또는 코드 시작하면 닫기
                    if next_line.startswith(('Args:', 'Returns:')) or \
                       (next_line and re.match(r'^[a-z_]+\s*=|^if |^return |^try:', next_line)):
                        # j-1 위치 또는 j 위치에 """ 삽입 필요
                        break
                    j += 1

        result_lines.append(line)
        i += 1

    content = '\n'.join(result_lines)

    # 3. standalone """ 제거 (코드 블록 안)
    lines = content.split('\n')
    cleaned = []
    for i, line in enumerate(lines):
        if re.match(r'^\s+"""\s*$', line):
            # 다음 줄이 코드면 제거
            if i + 1 < len(lines):
                next_stripped = lines[i+1].strip()
                if next_stripped and re.match(r'^(if |elif |for |return |[a-z_]+\s*=)', next_stripped):
                    continue
        cleaned.append(line)

    content = '\n'.join(cleaned)

    # 4. 강제로 주요 패턴 수정
    # "def xxx():\n    한글텍스트" → "def xxx():\n    """한글텍스트""""
    content = re.sub(
        r'(\n    def [^:]+:\n)(        )([가-힣][^\n]+)\n(        )([a-z_]+\s*=)',
        r'\1\2"""\3"""\n\4\5',
        content
    )

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# 파일 목록
files = [
    'research/screener.py',
    'research/strategy_manager.py',
    'strategy/scoring_system.py',
    'virtual_trading/virtual_trader.py',
    'virtual_trading/trade_logger.py'
]

fixed = []
for f in files:
    if Path(f).exists():
        if aggressive_fix(f):
            print(f"✓ {f}")
            fixed.append(f)
        else:
            print(f"○ {f}")

print(f"\n수정: {len(fixed)}개")
