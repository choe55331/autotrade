#!/bin/bash
# 대시보드 이슈 원클릭 테스트 스크립트

echo "🚀 대시보드 테스트 시작..."
echo ""

cd "$(dirname "$0")"

python3 test_dashboard.py

exit $?
