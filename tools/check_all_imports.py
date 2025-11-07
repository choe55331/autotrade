#!/usr/bin/env python3
"""
main.py가 import하는 모든 파일을 찾아서 syntax 검증
"""
import subprocess
from pathlib import Path

# main.py가 직접/간접적으로 import하는 모든 패키지 디렉토리
packages = [
    'config',
    'utils',
    'api',
    'api/market',
    'core',
    'core/bot',
    'research',
    'strategy',
    'strategy/risk',
    'ai',
    'virtual_trading',
    'database',
    'dashboard',
    'dashboard/routes',
]

failed_files = []
total_files = 0

for package_dir in packages:
    package_path = Path(package_dir)
    if not package_path.exists():
        continue

    # 모든 .py 파일 찾기
    py_files = list(package_path.glob('*.py'))

    for py_file in py_files:
        total_files += 1
        result = subprocess.run(
            ['python', '-m', 'py_compile', str(py_file)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            error_lines = result.stderr.split('\n')
            # 에러 라인과 메시지 추출
            error_info = {
                'file': str(py_file),
                'error': '\n'.join(error_lines[0:4])
            }
            failed_files.append(error_info)
            print(f"✗ {py_file}")
        else:
            print(f"✓ {py_file}")

print()
print("="*70)
if failed_files:
    print(f"FAILED: {len(failed_files)}/{total_files} files have syntax errors")
    print("="*70)
    print()
    for item in failed_files:
        print(f"\n{item['file']}:")
        print(item['error'])
else:
    print(f"SUCCESS: All {total_files} files compile correctly!")
    print("="*70)
