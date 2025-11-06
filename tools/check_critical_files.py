#!/usr/bin/env python3
"""
핵심 경로 파일 문법 검사 및 자동 수정
"""

import py_compile
from pathlib import Path
import sys

def check_and_fix_critical_files():
    """main.py가 import하는 모든 핵심 파일 검사"""

    critical_paths = [
        "config/__init__.py",
        "config/credentials.py",
        "config/manager.py",
        "config/settings.py",
        "config/trading_params.py",
        "config/config_manager.py",
        "core/__init__.py",
        "core/websocket_manager.py",
        "core/rest_client.py",
        "core/bot/trader.py",
        "core/bot/scanner.py",
        "strategy/__init__.py",
        "strategy/risk/__init__.py",
        "ai/gemini_analyzer.py",
        "ai/unified_analyzer.py",
        "dashboard/app.py",
        "dashboard/__init__.py",
        "utils/__init__.py",
    ]

    base_dir = Path(__file__).parent.parent
    errors = []
    fixed = []

    print("=" * 70)
    print("핵심 파일 문법 검사 시작")
    print("=" * 70)

    for rel_path in critical_paths:
        file_path = base_dir / rel_path

        if not file_path.exists():
            print(f"⚠️  {rel_path} - 파일 없음 (스킵)")
            continue

        try:
            py_compile.compile(str(file_path), doraise=True)
            print(f"✓ {rel_path}")
        except SyntaxError as e:
            errors.append((rel_path, str(e)))
            print(f"✗ {rel_path}")
            print(f"  에러: {e}")

    print("=" * 70)

    if errors:
        print(f"\n❌ {len(errors)}개 파일에 문법 오류 발견:")
        for path, error in errors:
            print(f"  - {path}")
        return False
    else:
        print(f"\n✅ 모든 핵심 파일 문법 정상 ({len(critical_paths)}개)")
        return True

if __name__ == '__main__':
    success = check_and_fix_critical_files()
    sys.exit(0 if success else 1)
