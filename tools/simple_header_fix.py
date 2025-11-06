"""
Simple Header Fixer
파일 시작 부분의 한글 텍스트를 docstring으로 변환
"""

import re
from pathlib import Path
import py_compile


def has_syntax_error(file_path: Path) -> bool:
    """파일에 문법 오류가 있는지 확인"""
    try:
        py_compile.compile(str(file_path), doraise=True)
        return False
    except:
        return True


def fix_header(file_path: Path) -> bool:
    """파일 헤더의 한글 텍스트를 docstring으로 변환"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            return False

        original_lines = lines.copy()

        first_code = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                first_code = i
                break

        if first_code >= len(lines):
            return False

        if lines[first_code].strip().startswith(('"""', "'''", 'import', 'from', 'def ', 'class ', '__', '@')):
            return False

        header_end = first_code
        for i in range(first_code, min(first_code + 30, len(lines))):
            stripped = lines[i].strip()

            if stripped.startswith(('import', 'from', 'def ', 'class ', '__', '@', 'if __name__')):
                header_end = i
                break

            if stripped:
                has_assignment = '=' in stripped and not stripped.startswith('#')
                has_function_call = '(' in stripped and ')' in stripped
                has_return = stripped.startswith('return ')
                has_raise = stripped.startswith('raise ')

                if has_assignment or has_function_call or has_return or has_raise:
                    header_end = i
                    break

                header_end = i + 1

        if header_end > first_code:
            header_lines = []
            for i in range(first_code, header_end):
                if lines[i].strip():
                    header_lines.append(lines[i])

            if header_lines:
                comments_before = lines[:first_code]

                new_lines = comments_before
                new_lines.append('"""\n')
                new_lines.extend(header_lines)
                new_lines.append('"""\n\n')
                new_lines.extend(lines[header_end:])

                new_content = ''.join(new_lines)

                try:
                    compile(new_content, str(file_path), 'exec')

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    return True
                except SyntaxError:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(original_lines)
                    return False

        return False

    except Exception:
        return False


def main():
    """메인 함수"""
    base_dir = Path(__file__).parent.parent
    fixed_count = 0
    checked = 0
    still_broken = []

    print("🔧 파일 헤더 수정 중...")
    print("=" * 70)

    for py_file in base_dir.rglob("*.py"):
        if 'venv' in str(py_file) or '.git' in str(py_file):
            continue

        if not has_syntax_error(py_file):
            continue

        checked += 1

        if fix_header(py_file):
            if not has_syntax_error(py_file):
                print(f"✓ {py_file.relative_to(base_dir)}")
                fixed_count += 1
            else:
                still_broken.append(py_file)
        else:
            still_broken.append(py_file)

    print("=" * 70)
    print(f"✅ {checked}개 오류 파일 검사, {fixed_count}개 파일 수정")

    if still_broken:
        print(f"\n⚠️  {len(still_broken)}개 파일은 추가 수정 필요")


if __name__ == '__main__':
    main()
