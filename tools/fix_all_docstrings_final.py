#!/usr/bin/env python3
"""모든 Python 파일의 docstring syntax 에러를 한 번에 수정"""

import re
from pathlib import Path
import subprocess

def fix_file(filepath):
    """파일의 모든 docstring 문제를 수정"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # 1. 모든 emoji와 특수문자 제거
        replacements = {
            '⚠️': 'WARNING:',
            '→': '->',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '🔥': '',
            '📊': '',
            '💰': '',
            '📈': '',
            '📉': '',
        }
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # 2. 파일 헤더 docstring 수정 (첫 번째 """ """ 쌍)
        lines = content.split('\n')
        quote_count = 0
        first_docstring_end = -1
        
        for i in range(min(40, len(lines))):
            quote_count += lines[i].count('"""')
            if quote_count >= 2:
                first_docstring_end = i
                break
        
        # docstring 다음에 텍스트가 있으면 docstring 안으로
        if 0 < first_docstring_end < len(lines) - 1:
            next_idx = first_docstring_end + 1
            while next_idx < len(lines) and not lines[next_idx].strip():
                next_idx += 1
            
            if next_idx < len(lines):
                next_line = lines[next_idx]
                if (next_line.strip() and 
                    not next_line.strip().startswith(('import ', 'from ', 'def ', 'class ', '#', '"""'))):
                    # docstring 끝 제거
                    lines[first_docstring_end] = re.sub(r'""".*$', '', lines[first_docstring_end])
                    
                    # import/from/def/class 찾을 때까지
                    j = next_idx
                    while j < len(lines) and j < 60:
                        if lines[j].strip().startswith(('import ', 'from ', 'def ', 'class ')):
                            lines.insert(j, '"""')
                            break
                        j += 1
        
        content = '\n'.join(lines)
        
        # 3. 함수 정의 후 docstring 없는 경우 (패턴 매칭)
        # ) -> Type:\n        한글텍스트
        content = re.sub(
            r'(\) -> [^\n:]+:\n)(    +)([가-힣a-zA-Z][^\n]*\n)',
            r'\1\2"""\n\2\3',
            content
        )
        
        # ):\n        한글텍스트
        content = re.sub(
            r'(\):\n)(    +)([가-힣a-zA-Z][^\n]*\n)',
            r'\1\2"""\n\2\3',
            content
        )
        
        # 4. Returns/Note 후 """ 닫기
        # Returns:\n ... \n        코드
        content = re.sub(
            r'(        Returns:\n(?:            [^\n]*\n)+)(        )(try:|if |return |self\.|logger\.|result |body |for |while |def |class |[a-z_]+ = )',
            r'\1        """\n\2\3',
            content
        )
        
        # Note:\n ... \n        코드
        content = re.sub(
            r'(        Note:\n(?:            [^\n]*\n)+)(        )(try:|if |return |self\.|logger\.|result )',
            r'\1        """\n\2\3',
            content
        )
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"ERROR fixing {filepath}: {e}")
        return False

# 모든 패키지 디렉토리
packages = [
    'research',
    'strategy',
    'ai',
    'virtual_trading',
    'dashboard',
    'dashboard/routes',
    'core/bot',
]

fixed = 0
total = 0

for package_dir in packages:
    package_path = Path(package_dir)
    if not package_path.exists():
        continue
    
    for py_file in package_path.glob('*.py'):
        total += 1
        if fix_file(py_file):
            print(f"✓ Fixed: {py_file}")
            fixed += 1

print(f"\n{'='*70}")
print(f"Fixed {fixed}/{total} files")
print(f"{'='*70}")
