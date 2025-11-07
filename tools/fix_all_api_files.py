#!/usr/bin/env python3
"""
API 파일들의 docstring 문제를 일괄 수정
"""
import re
from pathlib import Path

def fix_api_file(filepath):
    """API 파일의 docstring 문제 수정"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. 파일 헤더의 emoji 제거 및 docstring 닫기
    content = re.sub(
        r'("""\n.*?)\n    ⚠️(.*?\n)("""\n)',
        r'\1\n    WARNING:\2\3',
        content,
        flags=re.DOTALL
    )

    # 2. 함수 정의 후 docstring이 없는 경우들을 수정
    # 패턴: def func(...):
    #           설명 (← 이게 docstring 밖에 있음)
    #
    #           Args:
    lines = content.split('\n')
    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        fixed_lines.append(line)

        # 함수 정의 찾기 (def로 시작)
        if re.match(r'^    def \w+\(', line):
            # 함수 시그니처가 끝날 때까지 찾기
            j = i + 1
            while j < len(lines) and not lines[j].rstrip().endswith(':'):
                fixed_lines.append(lines[j])
                j += 1

            if j < len(lines):
                # ): 또는 ) -> Type: 라인
                fixed_lines.append(lines[j])
                j += 1

                # 다음 라인 확인
                if j < len(lines):
                    next_line = lines[j]

                    # docstring이 없고 한글/영문 설명이 바로 나오는 경우
                    if (next_line.strip() and
                        not next_line.strip().startswith('"""') and
                        not next_line.strip().startswith('#') and
                        not next_line.strip().startswith('try:') and
                        not next_line.strip().startswith('return') and
                        not next_line.strip().startswith('if ') and
                        not next_line.strip().startswith('self.')):

                        # 설명이 시작되는 부분 찾기
                        if re.match(r'\s+[가-힣a-zA-Z]', next_line):
                            # docstring 시작 추가
                            indent = len(next_line) - len(next_line.lstrip())
                            fixed_lines.append(' ' * indent + '"""')

                            # docstring 내용 추가하면서 끝나는 지점 찾기
                            while j < len(lines):
                                fixed_lines.append(lines[j])
                                j += 1

                                # 다음 라인이 코드 시작이면 docstring 닫기
                                if j < len(lines):
                                    peek = lines[j].strip()
                                    if (peek.startswith('try:') or
                                        peek.startswith('return') or
                                        peek.startswith('if ') or
                                        peek.startswith('self.') or
                                        peek.startswith('for ') or
                                        peek.startswith('while ') or
                                        peek.startswith('with ') or
                                        peek.startswith('logger.') or
                                        (peek and not peek[0].isalpha() and not peek.startswith('Args:') and not peek.startswith('Returns:'))):
                                        # docstring 닫기
                                        indent = len(lines[j]) - len(lines[j].lstrip())
                                        fixed_lines.append(' ' * indent + '"""')
                                        break

                            i = j - 1
                        else:
                            i = j - 1
                    else:
                        i = j - 1
                else:
                    i = j - 1
            else:
                i = j - 1

        i += 1

    content = '\n'.join(fixed_lines)

    # 3. 중복된 """ 제거
    content = re.sub(r'(\s+""")\n\s+"""', r'\1', content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


if __name__ == '__main__':
    api_files = [
        'api/account.py',
        'api/market.py',
        'api/order.py',
        'api/realtime.py',
        'api/condition_api.py',
        'api/theme_api.py',
        'api/short_selling_api.py',
    ]

    for filepath in api_files:
        if fix_api_file(filepath):
            print(f"✓ Fixed: {filepath}")
        else:
            print(f"  No changes: {filepath}")
