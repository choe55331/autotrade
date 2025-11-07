#!/usr/bin/env python3
"""
모든 Python 파일의 문법 오류를 자동으로 수정
"""

import re
from pathlib import Path
import py_compile
import sys

def fix_file_completely(file_path: Path) -> bool:
    """파일의 모든 문법 오류를 수정"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        lines = content.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if i == 0 and stripped.startswith('"""'):
                pass
            elif i < 50 and not stripped.startswith(('"""', "'''", '#', 'import', 'from', 'def ', 'class ', '__', '@', 'if ', 'try:', 'except')):
                if stripped and not any(c in stripped for c in ['=', '(', ')', '[', ']', '{', '}', 'return', 'raise']):
                    end_idx = i
                    for j in range(i, min(i + 30, len(lines))):
                        next_stripped = lines[j].strip()
                        if next_stripped.startswith(('import', 'from', 'def ', 'class ', '__', '@', 'if ', 'try:')):
                            end_idx = j
                            break
                        if next_stripped and any(c in next_stripped for c in ['=', 'return', 'raise']):
                            end_idx = j
                            break

                    if end_idx > i:
                        header_lines = []
                        for j in range(i, end_idx):
                            if lines[j].strip():
                                header_lines.append(lines[j])

                        if header_lines:
                            new_lines = lines[:i]
                            new_lines.append('"""')
                            new_lines.extend(header_lines)
                            new_lines.append('"""')
                            new_lines.append('')
                            new_lines.extend(lines[end_idx:])
                            lines = new_lines
                            i = end_idx + 3
                            continue

            if stripped.startswith(('def ', 'async def ')):
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith('"""') and not next_line.startswith('#'):
                    """
                        if not any(kw in next_line for kw in ['return', 'if ', 'for ', 'while ', 'self.', 'print(', 'logger.', ' = ']):
                            j = i + 1
                            doc_lines = []

                            while j < len(lines) and j < i + 30:
                                check = lines[j].strip()

                                if not check:
                                    j += 1
                                    continue

                                if check.startswith('"""') or any(kw in check for kw in ['def ', 'if ', 'return ', 'self.', 'print(', 'logger.', ' = ', 'for ', 'while ', 'try:']):
                                    break

                                doc_lines.append(lines[j])
                                """
                                j += 1

                            if doc_lines:
                                indent = len(lines[i]) - len(lines[i].lstrip())
                                indent_str = ' ' * (indent + 4)

                                new_lines = lines[:i+1]
                                new_lines.append(indent_str + '"""')
                                new_lines.extend(doc_lines)
                                new_lines.append(indent_str + '"""')
                                new_lines.extend(lines[j:])

                                lines = new_lines
                                i = j + 3
                                continue

            i += 1

        content = '\n'.join(lines)

        content = re.sub(r'^\s*[[WARNING]️[X][OK]🔧🔌[CHART]📤📥⏳✓[TARGET]🐂🐻📩🔄->].*\n', '', content, flags=re.MULTILINE)

        if content != original:
            try:
                compile(content, str(file_path), 'exec')

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            except:
                return False

        return False

    except Exception as e:
        return False

def main():
    """메인 함수"""
    base_dir = Path(__file__).parent.parent

    print("=" * 70)
    print("전체 Python 파일 문법 오류 일괄 수정")
    print("=" * 70)

    core_files = [
        'utils/logger_new.py',
        'core/websocket_client.py',
    ]

    fixed_count = 0

    for rel_path in core_files:
        file_path = base_dir / rel_path

        if not file_path.exists():
            continue

        try:
            py_compile.compile(str(file_path), doraise=True)
            print(f"✓ {rel_path}")
        except:
            print(f"✗ {rel_path} - 수정 시도...")

            if fix_file_completely(file_path):
                try:
                    py_compile.compile(str(file_path), doraise=True)
                    print(f"  ✓ 수정 완료")
                    fixed_count += 1
                except Exception as e:
                    print(f"  ✗ 수정 실패: {e}")
            else:
                print(f"  ✗ 수정 불가")

    print("=" * 70)
    print(f"[OK] {fixed_count}개 파일 수정 완료")

    return fixed_count > 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
