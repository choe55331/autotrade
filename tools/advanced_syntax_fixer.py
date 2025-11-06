"""
Advanced Syntax Fixer v2.0
복잡한 Python 문법 오류를 자동으로 수정
"""

import re
from pathlib import Path
import ast


def fix_advanced_syntax(file_path: Path) -> bool:
    """고급 문법 오류 수정"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines(keepends=True)

        if not lines:
            return False

        original_content = content
        modified = False

        lines_str = ''.join(lines)

        lines_str = re.sub(
            r'(\d{2,3}:\d{2})',
            lambda m: m.group(1).replace(':', 'h'),
            lines_str
        )

        lines_str = re.sub(
            r'\b0(\d{5,6})\b',
            r'\1',
            lines_str
        )

        lines_str = re.sub(
            r'(:\s*\.\d+f})',
            r':.1f}',
            lines_str
        )

        lines_str = re.sub(
            r'(["\'])([^"\']*$)',
            lambda m: m.group(1) + '...' + m.group(1) if len(m.group(2)) > 50 else m.group(0),
            lines_str,
            flags=re.MULTILINE
        )

        if lines_str != content:
            modified = True
            content = lines_str
            lines = content.splitlines(keepends=True)

        i = 0
        in_docstring = False
        docstring_quote = None

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if i < 15 and not in_docstring:
                if stripped and not stripped.startswith(('"""', "'''", '#', 'import', 'from', 'def ', 'class ', 'if ', '__', '@', 'try:', 'except')):
                    if not any(kw in stripped for kw in ['=', '(', ')', '[', ']', '{', '}', 'return', 'raise']):
                        end_idx = i
                        while end_idx < min(i + 25, len(lines)):
                            next_line = lines[end_idx].strip()
                            if next_line.startswith(('import', 'from', 'def ', 'class ', 'if ', '__', '@', 'try:')):
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
                if re.match(r'\s*(print|logger\.\w+)\(f"""[^"]*$', line):
                    found_end = False
                    for j in range(i + 1, min(i + 100, len(lines))):
                        if '"""' in lines[j]:
                            found_end = True
                            break
                    if not found_end:
                        for j in range(min(i + 100, len(lines)) - 1, i, -1):
                            if lines[j].strip() and not lines[j].strip().startswith('#'):
                                lines[j] = lines[j].rstrip() + '\n""")\n'
                                modified = True
                                break

                if re.match(r'\s*(print|logger\.\w+)\(f"[^"]*$', line):
                    if not line.rstrip().endswith(('")','"\)')):
                        lines[i] = line.rstrip() + '...")\\n'
                        modified = True

                if re.match(r'\s*["\'][^"\']*$', line) and i > 0:
                    if not lines[i-1].strip().endswith(('=', '+', '(', ',')):
                        quote = '"' if '"' in line else "'"
                        lines[i] = line.rstrip() + quote + '\n'
                        modified = True

            i += 1

        if in_docstring and docstring_quote:
            for j in range(len(lines) - 1, 0, -1):
                if lines[j].strip():
                    lines[j] = lines[j].rstrip() + f'\n{docstring_quote}\n'
                    modified = True
                    break

        if modified:
            new_content = ''.join(lines)
            try:
                compile(new_content, str(file_path), 'exec')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
            except SyntaxError:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                return False

        return False

    except Exception:
        return False


def main():
    """메인 함수"""
    base_dir = Path(__file__).parent.parent
    fixed_count = 0
    checked = 0

    print("🔧 고급 문법 오류 수정 시작...")
    print("=" * 60)

    for py_file in base_dir.rglob("*.py"):
        if 'venv' in str(py_file) or '.git' in str(py_file):
            continue

        checked += 1

        if fix_advanced_syntax(py_file):
            print(f"✓ {py_file.relative_to(base_dir)}")
            fixed_count += 1

    print("=" * 60)
    print(f"✅ {checked}개 파일 검사, {fixed_count}개 파일 수정")


if __name__ == '__main__':
    main()
