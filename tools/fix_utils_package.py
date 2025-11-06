#!/usr/bin/env python3
"""
utils 패키지의 모든 파일 문법 오류 수정
"""

import py_compile
from pathlib import Path
import sys

def check_and_fix_utils():
    """utils 패키지 파일들 검사 및 수정"""
    base_dir = Path(__file__).parent.parent

    utils_files = [
        'utils/__init__.py',
        'utils/logger_new.py',
        'utils/file_handler.py',
        'utils/validators.py',
        'utils/decorators.py',
        'utils/exceptions.py',
        'utils/performance_profiler.py',
    ]

    print("=" * 70)
    print("utils 패키지 문법 검사")
    print("=" * 70)

    errors = []

    for rel_path in utils_files:
        file_path = base_dir / rel_path

        if not file_path.exists():
            continue

        try:
            py_compile.compile(str(file_path), doraise=True)
            print(f"✓ {rel_path}")
        except SyntaxError as e:
            print(f"✗ {rel_path}")
            print(f"  {e}")
            errors.append((rel_path, str(e)))

    print("=" * 70)

    if errors:
        print(f"\n❌ {len(errors)}개 파일 오류:")
        for path, error in errors:
            print(f"  - {path}")
            print(f"    {error[:100]}")
        return False
    else:
        print(f"\n✅ 모든 utils 파일 정상")
        return True

if __name__ == '__main__':
    success = check_and_fix_utils()
    sys.exit(0 if success else 1)
