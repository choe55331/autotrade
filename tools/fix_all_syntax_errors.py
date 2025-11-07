#!/usr/bin/env python3
"""모든 syntax 에러를 일괄 수정"""
import re
from pathlib import Path

def fix_file(filepath):
    """파일의 일반적인 syntax 에러 수정"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # 1. emoji 제거
        content = content.replace('⚠️', 'WARNING:')
        content = content.replace('→', '->')
        content = content.replace('✅', '[OK]')
        content = content.replace('❌', '[ERROR]')
        
        # 2. 파일 헤더에서 docstring 밖의 텍스트 찾아서 안으로 이동
        # 간단한 방법: 첫 """ """ 쌍 다음에 바로 텍스트가 있으면 그것도 docstring에 포함
        lines = content.split('\n')
        
        # 첫 docstring 끝 찾기
        in_first_docstring = False
        first_docstring_end = -1
        quote_count = 0
        
        for i, line in enumerate(lines[:30]):
            quote_count += line.count('"""')
            if quote_count >= 2:
                first_docstring_end = i
                break
        
        # docstring 다음 줄이 텍스트인 경우
        if 0 < first_docstring_end < len(lines) - 1:
            next_idx = first_docstring_end + 1
            # 빈 줄 건너뛰기
            while next_idx < len(lines) and not lines[next_idx].strip():
                next_idx += 1
            
            if next_idx < len(lines):
                next_line = lines[next_idx]
                # import/from/def/class가 아닌 텍스트가 있으면
                if (next_line.strip() and
                    not next_line.strip().startswith(('import ', 'from ', 'def ', 'class ', '#'))):
                    # 이전 docstring의 """ 제거하고 나중에 추가
                    lines[first_docstring_end] = lines[first_docstring_end].replace('"""', '', 1)
                    
                    # import나 def를 찾을 때까지 진행
                    j = next_idx
                    while j < len(lines) and j < 50:
                        if lines[j].strip().startswith(('import ', 'from ', 'def ', 'class ')):
                            # 이 앞에 """ 추가
                            lines.insert(j, '"""')
                            break
                        j += 1
        
        content = '\n'.join(lines)
        
        # 3. 함수 정의 후 docstring 없는 경우
        content = re.sub(
            r'(\) -> [^:]+:\n)(    )([가-힣][^\n]+\n\n    Args:)',
            r'\1\2"""\n\2\3',
            content
        )
        
        content = re.sub(
            r'(\):\n)(    )([가-힣][^\n]+\n\n    Args:)',
            r'\1\2"""\n\2\3',
            content
        )
        
        # 4. Returns 후 """ 닫기
        content = re.sub(
            r'(    Returns:\n        [^\n]+\n)(    )((?:try|if |return |self\.))',
            r'\1    """\n\2\3',
            content
        )
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error: {filepath}: {e}")
        return False

# 실행
packages = ['api/market', 'utils', 'core/bot', 'research', 'strategy', 'ai', 'virtual_trading', 'dashboard', 'dashboard/routes']
fixed = 0
for pkg in packages:
    p = Path(pkg)
    if p.exists():
        for f in p.glob('*.py'):
            if fix_file(f):
                print(f"Fixed: {f}")
                fixed += 1
print(f"\nFixed {fixed} files")
