"""
Ultimate Syntax Error Fixer
모든 Python 문법 오류를 완벽하게 수정
"""

import re
from pathlib import Path
import py_compile


def fix_all_syntax_issues(file_path: Path) -> bool:
    """모든 문법 오류를 수정"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            return False

        original_content = content
        lines = content.splitlines(keepends=True)

        i = 0
        first_code_line = None

        while i < min(30, len(lines)):
            stripped = lines[i].strip()
            if stripped and not stripped.startswith('#'):
                if not stripped.startswith(('"""', "'''", 'import', 'from', '__')):
                    if first_code_line is None:
                        first_code_line = i

                    if not any(c in stripped for c in ['=', '(', ')', 'def ', 'class ', '@', 'if ', 'return', 'raise']):
                        i += 1
                        continue
                else:
                    break
            i += 1

        if first_code_line is not None:
            docstring_end = first_code_line
            for j in range(first_code_line, min(first_code_line + 20, len(lines))):
                stripped = lines[j].strip()
                if stripped.startswith(('import', 'from', 'def ', 'class ', '__', '@')):
                    docstring_end = j
                    break
                if stripped and not any(c in stripped for c in ['=', '(', ')', 'return', 'raise']):
                    docstring_end = j + 1

            if docstring_end > first_code_line:
                docstring_lines = []
                for j in range(first_code_line, docstring_end):
                    if lines[j].strip():
                        docstring_lines.append(lines[j])

                if docstring_lines:
                    new_lines = lines[:first_code_line]
                    new_lines.append('"""\n')
                    new_lines.extend(docstring_lines)
                    new_lines.append('"""\n')
                    new_lines.extend(lines[docstring_end:])
                    lines = new_lines

        content_str = ''.join(lines)

        content_str = re.sub(
            r'(["\'])\s*\n(?!\s*\1)',
            r'\1\n',
            content_str,
            flags=re.MULTILINE
        )

        content_str = re.sub(
            r'(print\(f?["\'](?:[^"\'\\]|\\.)*)\n(?!["\'])',
            r'\1...\2\n',
            content_str
        )

        content_str = re.sub(
            r'(\w+\s*=\s*["\'])([^"\']*)\n(?!["\'])',
            r'\1\2\1\n',
            content_str
        )

        def fix_fstring_format(match):
            text = match.group(0)
            if ':.0f}' in text or ':.1f}' in text or ':.2f}' in text:
                return text
            text = re.sub(r':\.(\d+)f', r':.\1f', text)
            text = re.sub(r':\+\.(\d+)f', r':+.\1f', text)
            return text

        content_str = re.sub(
            r'f["\'](?:[^"\'\\]|\\.)*["\']',
            fix_fstring_format,
            content_str
        )

        content_str = re.sub(
            r'\b0([0-9]{5,})\b',
            r'\1',
            content_str
        )

        content_str = re.sub(
            r'([0-9]{2}):([0-9]{2})\b',
            r'\1h\2',
            content_str
        )

        lines = content_str.splitlines(keepends=True)

        i = 0
        in_string = False
        string_char = None

        while i < len(lines):
            line = lines[i]

            for match in re.finditer(r'(""")|(\'\'\')|(["' + "'])", line):
                quote = match.group(0)
                if quote in ('"""', "'''"):
                    if not in_string:
                        in_string = True
                        string_char = quote
                    elif string_char == quote:
                        in_string = False
                        string_char = None

            if in_string and i == len(lines) - 1:
                lines.append(f'{string_char}\n')

            i += 1

        content_str = ''.join(lines)

        if content_str != original_content:
            try:
                py_compile.compile(file_path, doraise=True)
                return False
            except:
                pass

            try:
                compile(content_str, str(file_path), 'exec')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content_str)
                return True
            except SyntaxError:
                pass

        return False

    except Exception:
        return False


def main():
    """메인 함수"""
    base_dir = Path(__file__).parent.parent
    fixed_count = 0
    checked = 0
    failed = []

    print("🔧 최종 문법 오류 수정...")
    print("=" * 70)

    for py_file in base_dir.rglob("*.py"):
        if 'venv' in str(py_file) or '.git' in str(py_file):
            continue

        checked += 1

        try:
            py_compile.compile(str(py_file), doraise=True)
        except:
            if fix_all_syntax_issues(py_file):
                print(f"✓ {py_file.relative_to(base_dir)}")
                fixed_count += 1
            else:
                try:
                    py_compile.compile(str(py_file), doraise=True)
                except Exception as e:
                    failed.append((py_file, str(e)))

    print("=" * 70)
    print(f"✅ {checked}개 파일 검사, {fixed_count}개 파일 수정")

    if failed:
        print(f"\n⚠️  {len(failed)}개 파일 수정 실패 (수동 수정 필요):")
        for path, error in failed[:10]:
            print(f"  - {path.relative_to(base_dir)}")


if __name__ == '__main__':
    main()
