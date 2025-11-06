"""
Batch Syntax Fixer
대량 문법 오류 패턴을 자동으로 수정
"""

import re
from pathlib import Path
import py_compile
import sys


def fix_unterminated_strings(file_path: Path) -> bool:
    """미종료 문자열 수정"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        lines = content.splitlines()

        modified = False

        for i in range(len(lines)):
            line = lines[i]

            if re.search(r"=\s*['\"]$", line.strip()):
                lines[i] = line + "'  \n" if line.strip().endswith("'") else line + '"  \n'
                modified = True

            if re.search(r"print\(f?['\"]$", line.strip()):
                quote = "'" if "'" in line else '"'
                lines[i] = line + quote + ')\n'
                modified = True

            if re.search(r"logger\.\w+\(f?['\"]$", line.strip()):
                quote = "'" if "'" in line else '"'
                lines[i] = line + quote + ')\n'
                modified = True

        if modified:
            new_content = '\n'.join(lines) + '\n' if lines else ''

            try:
                compile(new_content, str(file_path), 'exec')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
            except SyntaxError:
                return False

        return False

    except Exception:
        return False


def wrap_header_in_docstring(file_path: Path) -> bool:
    """파일 시작 부분의 텍스트를 docstring으로 감싸기"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.splitlines()

        if not lines:
            return False

        original_content = content

        start_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                start_idx = i
                break

        if start_idx >= len(lines):
            return False

        first_line = lines[start_idx].strip()

        if first_line.startswith(('"""', "'''", 'import', 'from', 'def ', 'class ', '__', '@')):
            return False

        code_keywords = ['=', 'return', 'raise', 'if ', 'for ', 'while ', 'try:', 'except', 'with ']
        if any(kw in first_line for kw in code_keywords):
            return False

        end_idx = start_idx
        for i in range(start_idx, min(start_idx + 30, len(lines))):
            stripped = lines[i].strip()

            if stripped.startswith(('import', 'from', 'def ', 'class ', '__', '@')):
                end_idx = i
                break

            if any(kw in stripped for kw in code_keywords):
                end_idx = i
                break

            if stripped:
                end_idx = i + 1

        if end_idx > start_idx:
            header_content = []
            for i in range(start_idx, end_idx):
                if lines[i].strip():
                    header_content.append(lines[i])

            if header_content:
                new_lines = lines[:start_idx]
                new_lines.append('"""')
                new_lines.extend(header_content)
                new_lines.append('"""')
                new_lines.append('')
                new_lines.extend(lines[end_idx:])

                new_content = '\n'.join(new_lines) + '\n' if new_lines else ''

                try:
                    compile(new_content, str(file_path), 'exec')
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    return True
                except SyntaxError:
                    return False

        return False

    except Exception:
        return False


def fix_unterminated_triple_quotes(file_path: Path) -> bool:
    """미종료 삼중 따옴표 수정"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.splitlines()

        if not lines:
            return False

        original_content = content

        quote_stack = []
        modified = False

        for i, line in enumerate(lines):
            for match in re.finditer(r'("""|\'\'\')', line):
                quote = match.group(0)
                if quote_stack and quote_stack[-1] == quote:
                    quote_stack.pop()
                else:
                    quote_stack.append((quote, i))

        if quote_stack:
            for quote, line_idx in reversed(quote_stack):
                if line_idx < len(lines):
                    lines[line_idx] = lines[line_idx] + '\n' + quote
                    modified = True

        if modified:
            new_content = '\n'.join(lines) + '\n' if lines else ''

            try:
                compile(new_content, str(file_path), 'exec')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
            except SyntaxError:
                return False

        return False

    except Exception:
        return False


def main():
    """메인 함수"""
    base_dir = Path(__file__).parent.parent

    print("🔧 일괄 문법 오류 수정 시작...")
    print("=" * 70)

    error_files = []
    for py_file in base_dir.rglob("*.py"):
        if 'venv' in str(py_file) or '.git' in str(py_file):
            continue

        try:
            py_compile.compile(str(py_file), doraise=True)
        except:
            error_files.append(py_file)

    print(f"📋 {len(error_files)}개 오류 파일 발견\n")

    fixed_count = 0

    for py_file in error_files:
        fixed = False

        if fix_unterminated_strings(py_file):
            fixed = True
        elif fix_unterminated_triple_quotes(py_file):
            fixed = True
        elif wrap_header_in_docstring(py_file):
            fixed = True

        if fixed:
            try:
                py_compile.compile(str(py_file), doraise=True)
                print(f"✓ {py_file.relative_to(base_dir)}")
                fixed_count += 1
            except:
                pass

    print("=" * 70)
    print(f"✅ {fixed_count}개 파일 수정 완료")

    remaining_errors = 0
    for py_file in error_files:
        try:
            py_compile.compile(str(py_file), doraise=True)
        except:
            remaining_errors += 1

    print(f"📊 남은 오류: {remaining_errors}개 파일")


if __name__ == '__main__':
    main()
