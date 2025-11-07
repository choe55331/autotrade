#!/usr/bin/env python3
"""모든 Python 파일의 syntax 에러를 자동으로 수정하는 스크립트"""

import os
import re
import sys
from pathlib import Path

def fix_docstring_issues(content, filepath):
    """Docstring 관련 문제 수정"""
    lines = content.split('\n')
    result = []
    in_docstring = False
    docstring_count = 0

    for i, line in enumerate(lines):
        # """ 카운트
        """
        if '"""' in line:
        """
            count = line.count('"""')
            """
            docstring_count += count
            if count % 2 == 1:
                in_docstring = not in_docstring

        # standalone """ 제거 (for, if, while 블록 내부)
        """
        stripped = line.strip()
        if stripped == '"""' and i > 0:
        """
            prev_line = lines[i-1].strip()
            if prev_line.startswith(('for ', 'if ', 'elif ', 'while ', 'try:', 'except', 'with ')):
                # standalone quote는 제거
                continue

        result.append(line)

        # docstring이 열려있고 다음 줄이 코드인 경우 closing quote 추가
        if in_docstring and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line and not next_line.startswith(('"""', '#', 'Args:', 'Returns:', 'Note:', 'Raises:', 'Example:', 'Yields:')):
                # 다음 줄이 코드인지 체크
                """
                if (next_line.startswith(('if ', 'for ', 'while ', 'return ', 'try:', 'except:', 'with ', 'def ', 'class ', 'import ', 'from '))
                    or '=' in next_line
                    or next_line.startswith(('self.', 'logger.', 'print('))):
                    indent = len(line) - len(line.lstrip())
                    result.append(' ' * indent + '"""')
                    """
                    in_docstring = False
                    docstring_count += 1

    return '\n'.join(result)

def fix_emoji_and_special_chars(content):
    """이모지 및 특수 문자 제거/변환"""
    replacements = {
        '[STAR]': '[STAR]',
        '[OK]': '[OK]',
        '[X]': '[X]',
        '[TARGET]': '[TARGET]',
        '->': '->',
        '[WARNING]': '[WARNING]',
        '[CHART]': '[CHART]',
        '[SEARCH]': '[SEARCH]',
        '[MONEY]': '[MONEY]',
        '[UP]': '[UP]',
        '[DOWN]': '[DOWN]',
    }

    for emoji, replacement in replacements.items():
        content = content.replace(emoji, replacement)

    return content

def fix_leading_zeros(content):
    """Leading zero 문제 수정 ("08":"00" 같은 시간은 문자열로)"""
    # 시간 패턴: 08:00, 09:30 등을 문자열로 변환
    # 하지만 이미 문자열 안에 있는 경우는 제외
    lines = content.split('\n')
    result = []

    for line in lines:
        # 주석이 아니고, 문자열이 아닌 경우만 처리
        if not line.strip().startswith('#'):
            # 0으로 시작하는 숫자 패턴 찾기 (이미 문자열 안에 있지 않은 경우)
            # 예: 08:00 -> "08:00", 09 -> "09"
            # 하지만 0x, 0o, 0b는 제외
            line = re.sub(r'(?<!["\'])(?<!0[xXoObB])\b(0[0-9]+)\b(?!["\'])', r'"\1"', line)

        result.append(line)

    return '\n'.join(result)

def fix_unterminated_strings(content, filepath):
    """종료되지 않은 문자열 수정 시도"""
    lines = content.split('\n')
    result = []

    for i, line in enumerate(lines):
        # f-string이나 일반 string이 닫히지 않은 경우
        # 간단한 휴리스틱: 따옴표 개수가 홀수이고 라인 끝에 따옴표가 없으면
        single_quotes = line.count("'") - line.count("\\'")
        double_quotes = line.count('"') - line.count('\\"')

        # docstring은 이미 처리했으므로 제외
        if '"""' not in line and "'''" not in line:
            # 홀수개의 따옴표가 있고 라인이 따옴표로 끝나지 않으면
            """
            if single_quotes % 2 == 1 and not line.rstrip().endswith("'"):
                line = line.rstrip() + "'"
            elif double_quotes % 2 == 1 and not line.rstrip().endswith('"'):
                line = line.rstrip() + '"'

        result.append(line)

    return '\n'.join(result)

def fix_file(filepath):
    """단일 파일 수정"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        # 1. 이모지 및 특수 문자 제거
        content = fix_emoji_and_special_chars(content)

        # 2. Docstring 문제 수정
        content = fix_docstring_issues(content, filepath)

        # 3. Leading zero 문제 수정
        content = fix_leading_zeros(content)

        # 4. 종료되지 않은 문자열 수정
        # content = fix_unterminated_strings(content, filepath)

        # 변경사항이 있으면 파일 저장
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

def main():
    """메인 함수"""
    # 현재 디렉토리의 모든 Python 파일 찾기
    python_files = []

    for root, dirs, files in os.walk('.'):
        # 제외할 디렉토리
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', '.venv']]

        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                python_files.append(filepath)

    print(f"Found {len(python_files)} Python files")

    fixed_count = 0
    for filepath in python_files:
        if fix_file(filepath):
            print(f"Fixed: {filepath}")
            fixed_count += 1

    print(f"\n총 {fixed_count}개 파일 수정 완료")

if __name__ == "__main__":
    main()
