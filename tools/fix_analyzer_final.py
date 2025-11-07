#!/usr/bin/env python3
"""analyzer.py의 모든 standalone triple quotes 제거"""
import re

with open('research/analyzer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

cleaned = []
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()

    # standalone """ 또는 " 만 있는 줄인지 확인
    if re.match(r'^\s+"""\s*$', line):
        # 이전 줄 확인
        if i > 0:
            prev_stripped = lines[i - 1].strip()
            # 이전 줄이 함수/클래스 정의가 아니면 제거
            if not prev_stripped.endswith(':'):
                i += 1
                continue  # 이 줄 건너뛰기 (제거)

        # 다음 줄 확인
        if i + 1 < len(lines):
            next_stripped = lines[i + 1].strip()
            # 다음 줄이 코드 (if, for, return, 변수 등)이면 제거
            if next_stripped and not next_stripped.startswith('"""'):
                if re.match(r'^(if |elif |for |while |return |[a-z_]+\s*=)', next_stripped):
                    i += 1
                    continue  # 이 줄 건너뛰기 (제거)

    cleaned.append(line)
    i += 1

# 파일 저장
with open('research/analyzer.py', 'w', encoding='utf-8') as f:
    f.writelines(cleaned)

print(f"✓ {len(lines) - len(cleaned)} 줄의 standalone triple quotes 제거")
print(f"✓ 원본: {len(lines)}줄 → 수정: {len(cleaned)}줄")
