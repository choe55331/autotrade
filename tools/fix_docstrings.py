"""
Fix docstring syntax errors in Python files
"""

import os
import re
from pathlib import Path


def fix_file_docstring(file_path: Path) -> bool:
    """Fix docstring at the beginning of a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if len(lines) < 3:
            return False

        first_line = lines[0].strip()
        second_line = lines[1].strip() if len(lines) > 1 else ''
        third_line = lines[2].strip() if len(lines) > 2 else ''

        if first_line and not first_line.startswith(('"""', "'''", '#', 'import', 'from', 'def ', 'class ')):
        """
            if (not first_line.startswith('"""') and
                not first_line.startswith("'''") and
                not first_line.startswith('#')):

"""
                docstring_lines = [first_line]
                idx = 1

                while idx < len(lines) and idx < 10:
                    line = lines[idx].strip()
                    if line and not line.startswith(('import', 'from', 'def ', 'class ', 'if ', '__')):
                        docstring_lines.append(lines[idx].rstrip())
                        idx += 1
                    else:
                        break

                if len(docstring_lines) > 0:
                    new_lines = ['"""\n']
                    new_lines.extend(line if line.endswith('\n') else line + '\n' for line in docstring_lines)
                    new_lines.append('"""\n')
                    new_lines.extend(lines[idx:])

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)

                    print(f"✓ Fixed: {file_path}")
                    return True

        return False

    except Exception as e:
        print(f"✗ Error fixing {file_path}: {e}")
        return False


def main():
    """Main function"""
    base_dir = Path(__file__).parent.parent
    fixed_count = 0

    print("🔧 Fixing docstring syntax errors...")
    print("=" * 60)

    for py_file in base_dir.rglob("*.py"):
        if 'venv' in str(py_file) or '.git' in str(py_file):
            continue

        if fix_file_docstring(py_file):
            fixed_count += 1

    print("=" * 60)
    print(f"[OK] Fixed {fixed_count} files")


if __name__ == '__main__':
    main()
