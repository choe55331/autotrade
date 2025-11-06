"""
Python Syntax Checker
모든 Python 파일의 문법 오류 검사
"""

import py_compile
import sys
from pathlib import Path


def check_file(file_path: Path) -> tuple[bool, str]:
    """파일 문법 검사"""
    try:
        py_compile.compile(str(file_path), doraise=True)
        return True, ""
    except py_compile.PyCompileError as e:
        return False, str(e)


def main():
    """Main function"""
    base_dir = Path(__file__).parent.parent
    errors = []
    checked = 0

    print("🔍 Python 문법 검사 시작...")
    print("=" * 60)

    for py_file in base_dir.rglob("*.py"):
        if 'venv' in str(py_file) or '.git' in str(py_file):
            continue

        checked += 1
        success, error = check_file(py_file)

        if not success:
            print(f"✗ {py_file}")
            print(f"  {error}")
            errors.append((py_file, error))

    print("=" * 60)

    if errors:
        print(f"❌ {len(errors)}개 파일에 문법 오류 발견 (총 {checked}개 검사)")
        sys.exit(1)
    else:
        print(f"✅ 모든 파일 문법 검사 통과 (총 {checked}개 파일)")
        sys.exit(0)


if __name__ == '__main__':
    main()
