#!/usr/bin/env python3
"""
모든 핵심 파일의 docstring 문제를 자동으로 수정
"""

import re
from pathlib import Path
import py_compile

def fix_docstring_issues(file_path: Path) -> bool:
    """파일의 docstring 문제를 자동으로 수정"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if i < len(lines) - 1:
                next_line = lines[i + 1].strip()

                if stripped.startswith('def ') or stripped.startswith('async def '):
                    if next_line and not next_line.startswith('"""') and not next_line.startswith('#') and not next_line.startswith('return') and not next_line.startswith('if ') and not next_line.startswith('for ') and not next_line.startswith('while ') and not next_line.startswith('try:') and ':' not in next_line:

"""
                        j = i + 1
                        docstring_lines = []

                        while j < len(lines) and j < i + 30:
                            check_line = lines[j].strip()
                            if not check_line:
                                j += 1
                                continue

                            if check_line.startswith('"""') or check_line.startswith('if ') or check_line.startswith('return ') or check_line.startswith('for ') or check_line.startswith('self.') or check_line.startswith('print(') or check_line.startswith('logger.') or '=' in check_line:
                                break

                            docstring_lines.append(lines[j])
                            """
                            j += 1

                        if docstring_lines:
                            indent = len(lines[i]) - len(lines[i].lstrip())
                            indent_str = ' ' * (indent + 4)

                            new_lines = lines[:i+1]
                            new_lines.append(indent_str + '"""')
                            new_lines.extend(docstring_lines)
                            new_lines.append(indent_str + '"""')
                            new_lines.extend(lines[j:])

                            lines = new_lines
                            i = j + 3
                            continue

            i += 1

        content = '\n'.join(lines)

        content = re.sub(r'^\s*[[WARNING]️[X][OK]🔧🔌[CHART]📤📥⏳✓[TARGET]🐂🐻📩🔄].*\n', '', content, flags=re.MULTILINE)

        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def main():
    """메인 함수"""
    base_dir = Path(__file__).parent.parent

    critical_files = [
        "config/__init__.py",
        "config/credentials.py",
        "config/manager.py",
        "config/settings.py",
        "config/trading_params.py",
        "config/config_manager.py",
        "config/unified_settings.py",
        "core/__init__.py",
        "core/websocket_manager.py",
        "core/rest_client.py",
        "core/websocket_client.py",
        "core/bot/trader.py",
        "core/bot/scanner.py",
        "strategy/__init__.py",
        "strategy/risk/__init__.py",
        "ai/gemini_analyzer.py",
        "ai/unified_analyzer.py",
        "ai/market_regime_classifier.py",
        "ai/advanced_backtester.py",
        "dashboard/app.py",
        "dashboard/__init__.py",
        "dashboard/routes/ai.py",
        "dashboard/routes/ai/__init__.py",
        "utils/__init__.py",
        "research/screener.py",
        "research/data_fetcher.py",
        "research/theme_analyzer.py",
        "research/analyzer.py",
        "research/deep_scan_utils.py",
        "research/scanner_pipeline.py",
        "research/quant_screener.py",
    ]

    print("=" * 70)
    print("핵심 파일 docstring 자동 수정 시작")
    print("=" * 70)

    fixed_count = 0
    error_count = 0

    for rel_path in critical_files:
        file_path = base_dir / rel_path

        if not file_path.exists():
            continue

        try:
            py_compile.compile(str(file_path), doraise=True)
            print(f"✓ {rel_path}")
        except SyntaxError:
            print(f"✗ {rel_path} - 수정 시도 중...")

            if fix_docstring_issues(file_path):
                try:
                    py_compile.compile(str(file_path), doraise=True)
                    print(f"  ✓ 수정 완료")
                    fixed_count += 1
                except SyntaxError as e:
                    print(f"  ✗ 수정 실패: {e}")
                    error_count += 1
            else:
                error_count += 1

    print("=" * 70)
    print(f"[OK] {fixed_count}개 파일 수정 완료")
    if error_count > 0:
        print(f"[X] {error_count}개 파일 수정 실패 (수동 확인 필요)")

    return error_count == 0

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
