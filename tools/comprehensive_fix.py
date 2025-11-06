"""
Comprehensive Syntax Fixer
모든 Python 문법 오류를 포괄적으로 수정
"""

import re
from pathlib import Path
import ast


def fix_file(file_path: Path) -> bool:
    """파일의 모든 문법 오류 수정"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            return False

        original_lines = lines.copy()
        modified = False

        i = 0
        in_docstring = False
        docstring_quote = None

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if i < 10 and not in_docstring:
                if stripped and not stripped.startswith(('"""', "'''", '#', 'import', 'from', 'def ', 'class ', 'if ', '__', '@')):
                    if not any(keyword in stripped for keyword in ['=', '(', ')', '[', ']', '{', '}']):
                        end_idx = i
                        while end_idx < min(i + 20, len(lines)):
                            next_line = lines[end_idx].strip()
                            if next_line.startswith(('import', 'from', 'def ', 'class ', 'if ', '__', '@')):
                                break
                            if next_line and not next_line.startswith('#'):
                                end_idx += 1
                            else:
                                break

                        if end_idx > i:
                            docstring_lines = []
                            for j in range(i, end_idx):
                                if lines[j].strip():
                                    docstring_lines.append(lines[j].rstrip() + '\n')

                            if docstring_lines:
                                new_content = ['"""\n'] + docstring_lines + ['"""\n']
                                lines = lines[:i] + new_content + lines[end_idx:]
                                modified = True
                                i += len(new_content)
                                continue

            if '"""' in line or "'''" in line:
                quote = '"""' if '"""' in line else "'''"
                count = line.count(quote)

                if count == 1:
                    if not in_docstring:
                        in_docstring = True
                        docstring_quote = quote
                    else:
                        if quote == docstring_quote:
                            in_docstring = False
                            docstring_quote = None
                elif count >= 2:
                    pass

            if not in_docstring:
                if re.match(r'\s*(print|logger\.\w+)\(f"[^"]*$', line):
                    if not line.rstrip().endswith(('")', '"')):
                        lines[i] = line.rstrip() + '")\n'
                        modified = True

                if re.match(r'\s*print\(f?"""[^"]*$', line):
                    found_end = False
                    for j in range(i + 1, min(i + 50, len(lines))):
                        if '"""' in lines[j]:
                            found_end = True
                            break
                    if not found_end:
                        for j in range(min(i + 50, len(lines)) - 1, i, -1):
                            if lines[j].strip():
                                lines[j] = lines[j].rstrip() + '\n"""\n'
                                modified = True
                                break

            i += 1

        if in_docstring:
            for j in range(len(lines) - 1, 0, -1):
                if lines[j].strip():
                    lines[j] = lines[j].rstrip() + f'\n{docstring_quote}\n'
                    modified = True
                    break

        if modified:
            try:
                compile(''.join(lines), str(file_path), 'exec')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                return True
            except SyntaxError:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(original_lines)
                return False

        return False

    except Exception as e:
        return False


def main():
    """Main function"""
    base_dir = Path(__file__).parent.parent
    fixed_count = 0
    checked = 0

    print("🔧 포괄적 문법 오류 수정 시작...")
    print("=" * 60)

    priority_patterns = [
        '*.py',
        '*/__init__.py',
        'config/*.py',
        'core/*.py',
        'api/*.py',
        'strategy/*.py',
        'dashboard/*.py',
    ]

    processed = set()

    for pattern in priority_patterns:
        for py_file in base_dir.glob(pattern):
            if py_file in processed:
                continue
            if 'venv' in str(py_file) or '.git' in str(py_file):
                continue

            processed.add(py_file)
            checked += 1

            if fix_file(py_file):
                print(f"✓ {py_file.relative_to(base_dir)}")
                fixed_count += 1

    for py_file in base_dir.rglob("*.py"):
        if py_file in processed:
            continue
        if 'venv' in str(py_file) or '.git' in str(py_file):
            continue

        processed.add(py_file)
        checked += 1

        if fix_file(py_file):
            print(f"✓ {py_file.relative_to(base_dir)}")
            fixed_count += 1

    print("=" * 60)
    print(f"✅ {checked}개 파일 검사, {fixed_count}개 파일 수정")


if __name__ == '__main__':
    main()
