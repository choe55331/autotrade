"""
Automatic Syntax Error Fixer
문법 오류 자동 수정
"""

import re
from pathlib import Path


def fix_unterminated_fstring(file_path: Path) -> int:
    """잘린 f-string 수정"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content
        fixes = 0

        pattern = r'(print\(f"[^"]*)\n'
        matches = list(re.finditer(pattern, content))

        for match in reversed(matches):
            start = match.start()
            end = match.end()
            line_content = match.group(1)

            if not line_content.endswith('"'):
                fixed = line_content + '")\n'
                content = content[:start] + fixed + content[end:]
                fixes += 1

        pattern = r'(logger\.(info|debug|warning|error)\(f"[^"]*)\n'
        matches = list(re.finditer(pattern, content))

        for match in reversed(matches):
            start = match.start()
            end = match.end()
            line_content = match.group(0).rstrip('\n')

            if not line_content.endswith('"'):
                fixed = line_content + '")\n'
                content = content[:start] + fixed + content[end:]
                fixes += 1

        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        return fixes

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return 0


def fix_unterminated_triple_string(file_path: Path) -> int:
    """잘린 triple-quoted string 수정"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        fixes = 0
        in_triple = False
        triple_start = -1

        for i, line in enumerate(lines):
            if '"""' in line:
            """
                count = line.count('"""')
                """
                if count == 1:
                    if not in_triple:
                        in_triple = True
                        triple_start = i
                    else:
                        in_triple = False
                        triple_start = -1
                elif count == 2:
                    in_triple = False
                    triple_start = -1

        if in_triple and triple_start >= 0:
            for i in range(len(lines) - 1, triple_start, -1):
                if lines[i].strip() and not lines[i].strip().startswith('#'):
                    lines[i] = lines[i].rstrip() + '\n"""\n'
                    """
                    fixes += 1
                    break

        if fixes > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

        return fixes

    except Exception as e:
        return 0


def main():
    """Main function"""
    base_dir = Path(__file__).parent.parent
    total_fixes = 0

    print("🔧 문법 오류 자동 수정 시작...")
    print("=" * 60)

    priority_files = [
        'main.py',
        'core/**/*.py',
        'api/**/*.py',
        'strategy/**/*.py',
        'dashboard/**/*.py',
    ]

    for pattern in priority_files:
        for py_file in base_dir.glob(pattern):
            if py_file.is_file():
                fixes = fix_unterminated_fstring(py_file)
                fixes += fix_unterminated_triple_string(py_file)

                if fixes > 0:
                    print(f"✓ {py_file.relative_to(base_dir)}: {fixes} fixes")
                    total_fixes += fixes

    print("=" * 60)
    print(f"[OK] 총 {total_fixes}개 수정 완료")


if __name__ == '__main__':
    main()
