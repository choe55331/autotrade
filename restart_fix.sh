#!/bin/bash
# AutoTrade 재시작 스크립트 (v5.5+)
# 모든 설정 적용을 위해 완전 재시작
#
# v5.5 변경사항:
# - 대시보드가 main.py에 통합됨 (별도 프로세스 불필요)
# - app_apple.py 제거 (모듈화된 dashboard/app.py 사용)

echo "================================"
echo "🔄 AutoTrade 재시작 중..."
echo "================================"

# 1. 실행 중인 Python 프로세스 찾기
echo ""
echo "1️⃣ 실행 중인 프로세스 확인..."
ps aux | grep "python.*main\.py" | grep -v grep

# 2. main.py 프로세스 종료 (대시보드 포함)
echo ""
echo "2️⃣ main.py 프로세스 종료 중..."
pkill -f "python.*main\.py" 2>/dev/null || echo "   main.py 프로세스 없음"

# 3. 잠시 대기
sleep 2

# 4. 프로세스 종료 확인
echo ""
echo "3️⃣ 종료 확인..."
if ps aux | grep "python.*main\.py" | grep -v grep > /dev/null; then
    echo "   ⚠️ 일부 프로세스가 아직 실행 중입니다. 강제 종료..."
    pkill -9 -f "python.*main\.py" 2>/dev/null
    sleep 1
else
    echo "   ✅ 모든 프로세스 종료됨"
fi

echo ""
echo "================================"
echo "✅ 재시작 준비 완료!"
echo "================================"
echo ""
echo "다음 명령어로 재시작하세요:"
echo ""
echo "  python main.py"
echo ""
echo "  (대시보드가 자동으로 시작됩니다: http://localhost:5000)"
echo ""
echo "예상 로그 확인사항:"
echo "  ✅ AutoTrade Pro 시작"
echo "  ✅ 웹 대시보드 시작 중..."
echo "  ✅ 대시보드 URL: http://0.0.0.0:5000"
echo "  ✅ 💰 초기 자본금: XXX원"
echo ""
