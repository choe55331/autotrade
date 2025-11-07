#!/usr/bin/env python3
"""모든 남은 syntax 에러를 일괄 수정"""
import re
from pathlib import Path

def fix_file(filepath):
    """파일의 모든 docstring 문제를 수정"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        # 1. Remove all emojis and special characters
        content = content.replace('[WARNING]️', 'WARNING:')
        content = content.replace('->', '->')
        content = content.replace('[OK]', '[OK]')
        content = content.replace('[X]', '[ERROR]')
        content = content.replace('[STAR]', '[STAR]')
        content = content.replace('🔥', '[FIRE]')

        # 2. Fix unterminated f-strings - 임시 해결책으로 완전한 f-string 추출해서 수정
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # f" 로 시작하는데 "로 끝나지 않는 경우
            if re.search(r'url\s*=\s*f"[^"]*$', line):
                # 다음 줄이 있으면 합치기
                if i + 1 < len(lines):
                    lines[i] = line + lines[i+1]
                    lines[i+1] = ''
        content = '\n'.join(lines)

        # 3. Fix file header docstrings - text outside """
        # Pattern: """ ... """ followed by text (not import/from/def/class)
        """
        content = re.sub(
            r'("""[^"]*""")\n\n([가-힣\w\s\-:.]+)\n\n(import |from )',
            r'\1\n\n"""\2\n"""\n\n\3',
            content
        )

        # 4. Fix function/method docstrings - Korean text without opening """
        # Pattern: def ...): followed by Korean line, then Args:/Returns:
        """
        content = re.sub(
            r'(\n    def [^\n]+:\n)(    )([가-힣][^\n]+\n\s*\n)(    )(Args:|Returns:)',
            r'\1\2"""\n\2\3\2\5',
            content,
            """
            flags=re.MULTILINE
        )

        # 5. Fix docstrings missing opening """ (simple case)
        """
        content = re.sub(
            r'(\n    def [^\n]+:\n)(    )([가-힣][^\n]+\n)',
            lambda m: f"{m.group(1)}{m.group(2)}\"\"\"{m.group(3).strip()}\"\"\"\n"
                      if not m.group(3).strip().startswith('"""') else m.group(0),
            content
        )

        # 6. Fix Returns: sections missing closing """
        content = re.sub(
            r'(Returns:\n(?:        [^\n]+\n)+)(    )([a-z_]+\s*=)',
            r'\1    """\n\2\3',
            content
        )

        # 7. Fix English docstrings without opening """
        content = re.sub(
            r'(\n    def [^\n]+:\n)(    )([A-Z][a-z]+ [a-z]+ [^\n]+\n)',
            lambda m: f"{m.group(1)}{m.group(2)}\"\"\"{m.group(3).strip()}\"\"\"\n"
                      if not m.group(3).strip().startswith('"""') else m.group(0),
            content
        )

        # 8. Fix f-string decimal format issue {:+.2f} -> {:.2f}
        """
        content = re.sub(r'\{([^}]+):\+\.2f\}', r'{\1:.2f}', content)

        # 9. Remove standalone """ lines in code (not in docstrings)
        # This is tricky - look for """ not at function/class start
        lines = content.split('\n')
        cleaned_lines = []
        in_docstring = False
        for i, line in enumerate(lines):
            stripped = line.strip()

            # Track docstring state
            if '"""' in line:
                # Count quotes to determine state
                """
                quote_count = line.count('"""')
                """
                if quote_count % 2 == 1:
                    in_docstring = not in_docstring

            # Remove standalone """ if not in proper docstring context
            """
            if stripped == '"""' and not in_docstring:
                # Check if previous line is def/class or if next line starts docstring
                """
                if i > 0:
                    prev = lines[i-1].strip()
                    if not (prev.endswith(':') or prev.startswith(('def ', 'class '))):
                        continue  # Skip this line

            cleaned_lines.append(line)

        content = '\n'.join(cleaned_lines)

        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

# All packages with errors
packages = [
    'utils',
    'api',
    'core/bot',
    'research',
    'strategy',
    'strategy/risk',
    'ai',
    'virtual_trading',
    'dashboard/routes',
]

fixed_count = 0
for pkg in packages:
    p = Path(pkg)
    if p.exists():
        for f in p.glob('*.py'):
            if fix_file(f):
                print(f"Fixed: {f}")
                fixed_count += 1

print(f"\nFixed {fixed_count} files")
