#!/usr/bin/env python3
"""
main.py가 import하는 모든 파일을 추적하고 문법 검사
"""

import sys
import ast
from pathlib import Path
import py_compile

def get_imports_from_file(file_path: Path) -> list:
    """파일에서 import하는 모든 모듈 추출"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports
    except:
        return []

def resolve_import_to_file(import_name: str, base_dir: Path) -> list:
    """import 이름을 실제 파일 경로로 변환"""
    files = []

    parts = import_name.split('.')

    path = base_dir
    for part in parts:
        path = path / part

    if path.with_suffix('.py').exists():
        files.append(path.with_suffix('.py'))

    init_file = path / '__init__.py'
    if init_file.exists():
        files.append(init_file)

    return files

def check_all_imports_from_main():
    """main.py부터 시작해서 모든 import 파일 검사"""
    base_dir = Path(__file__).parent.parent
    main_file = base_dir / 'main.py'

    checked = set()
    to_check = [main_file]
    errors = []

    print("=" * 70)
    print("main.py에서 import하는 모든 파일 문법 검사")
    print("=" * 70)

    while to_check:
        current_file = to_check.pop(0)

        if current_file in checked:
            continue

        checked.add(current_file)

        if not current_file.exists():
            continue

        rel_path = current_file.relative_to(base_dir)

        try:
            py_compile.compile(str(current_file), doraise=True)
            print(f"✓ {rel_path}")

            imports = get_imports_from_file(current_file)
            for imp in imports:
                if imp.startswith(('config', 'core', 'utils', 'strategy', 'ai', 'dashboard', 'research')):
                    import_files = resolve_import_to_file(imp, base_dir)
                    to_check.extend(import_files)

        except SyntaxError as e:
            print(f"✗ {rel_path}")
            print(f"  오류: {e}")
            errors.append((rel_path, str(e)))

    print("=" * 70)

    if errors:
        print(f"\n❌ {len(errors)}개 파일에 문법 오류:")
        for path, error in errors[:20]:
            print(f"  - {path}")
        return False
    else:
        print(f"\n✅ 모든 파일 문법 정상 ({len(checked)}개 검사)")
        return True

if __name__ == '__main__':
    success = check_all_imports_from_main()
    sys.exit(0 if success else 1)
