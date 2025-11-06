import re
import sys
from pathlib import Path

def remove_comments_from_file(file_path: Path) -> tuple[str, int]:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    in_docstring = False
    docstring_char = None
    prev_line_def = False
    removed_count = 0

    for i, line in enumerate(lines):
        stripped = line.lstrip()

        if in_docstring:
            new_lines.append(line)
            if docstring_char in stripped and not stripped.startswith(docstring_char):
                if stripped.count(docstring_char) >= 2:
                    in_docstring = False
            elif stripped.endswith(docstring_char + '\n') or stripped.endswith(docstring_char):
                in_docstring = False
            continue

        if stripped.startswith('"""') or stripped.startswith("'''"):
            docstring_char = '"""' if stripped.startswith('"""') else "'''"
            if prev_line_def or (i > 0 and ('def ' in lines[i-1] or 'class ' in lines[i-1])):
                new_lines.append(line)
                if stripped.count(docstring_char) < 2:
                    in_docstring = True
                continue
            else:
                removed_count += 1
                continue

        if stripped.startswith('#'):
            removed_count += 1
            continue

        if '#' in line and not ('"#"' in line or "'#'" in line):
            code_part = line.split('#')[0].rstrip()
            if code_part:
                new_lines.append(code_part + '\n')
            else:
                removed_count += 1
            continue

        new_lines.append(line)
        prev_line_def = 'def ' in stripped or 'class ' in stripped

    return ''.join(new_lines), removed_count

def process_directory(directory: Path, extensions: list = ['.py']):
    total_removed = 0
    files_processed = 0

    for ext in extensions:
        for file_path in directory.rglob(f'*{ext}'):
            if any(skip in str(file_path) for skip in ['.git', '__pycache__', 'venv', 'env', 'node_modules']):
                continue

            try:
                new_content, removed = remove_comments_from_file(file_path)

                if removed > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                    print(f"✅ {file_path.relative_to(directory)}: {removed}개 주석 제거")
                    total_removed += removed
                    files_processed += 1

            except Exception as e:
                print(f"❌ {file_path}: {e}")

    return files_processed, total_removed

if __name__ == '__main__':
    root = Path('/home/user/autotrade')

    print("🔧 주석 제거 시작...")
    print("="*60)

    files, comments = process_directory(root)

    print("="*60)
    print(f"✅ 완료: {files}개 파일, {comments}개 주석 제거")
