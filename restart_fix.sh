#!/bin/bash
# AutoTrade 재시작 스크립트
# 모든 설정 적용을 위해 완전 재시작

echo "================================"
echo "🔄 AutoTrade 재시작 중..."
echo "================================"

# 1. 실행 중인 Python 프로세스 찾기
echo ""
echo "1️⃣ 실행 중인 프로세스 확인..."
ps aux | grep -E "(main\.py|app_apple\.py)" | grep -v grep

# 2. main.py 프로세스 종료
echo ""
echo "2️⃣ main.py 프로세스 종료..."
pkill -f "python.*main\.py" 2>/dev/null || echo "   main.py 프로세스 없음"

# 3. dashboard 프로세스 종료
echo ""
echo "3️⃣ dashboard 프로세스 종료..."
pkill -f "python.*app_apple\.py" 2>/dev/null || echo "   dashboard 프로세스 없음"

# 4. 잠시 대기
sleep 2

# 5. 프로세스 종료 확인
echo ""
echo "4️⃣ 종료 확인..."
if ps aux | grep -E "(main\.py|app_apple\.py)" | grep -v grep > /dev/null; then
    echo "   ⚠️ 일부 프로세스가 아직 실행 중입니다. 강제 종료..."
    pkill -9 -f "python.*main\.py" 2>/dev/null
    pkill -9 -f "python.*app_apple\.py" 2>/dev/null
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
echo "  1. main.py 시작:"
echo "     python main.py"
echo ""
echo "  2. dashboard 시작 (별도 터미널):"
echo "     python dashboard/app_apple.py"
echo ""
echo "예상 로그 확인사항:"
echo "  ✅ [DEBUG 체결강도] XXX: min_value=50 (하드코딩)"
echo "  ✅ [DEBUG 프로그램] XXX: min_net_buy=100000 (하드코딩)"
echo "  ✅ 💰 초기 자본금: XXX원 (주문가능: XXX, 총평가: XXX)"
echo ""
