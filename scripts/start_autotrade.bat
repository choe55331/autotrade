@echo off
REM 자동매매 봇 시작 스크립트

echo ========================================
echo 자동매매 봇 시작
echo ========================================
echo.

REM Python 버전 확인
python --version
if errorlevel 1 (
    echo [ERROR] Python이 설치되지 않았거나 PATH에 등록되지 않았습니다.
    pause
    exit /b 1
)

echo.
echo [INFO] 가상환경 활성화 중...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [OK] 가상환경 활성화 완료
) else (
    echo [WARNING] 가상환경이 없습니다. 전역 Python 사용
)

echo.
echo [INFO] 필수 패키지 확인 중...
pip list | findstr /C:"requests" >nul
if errorlevel 1 (
    echo [WARNING] 필수 패키지가 설치되지 않았습니다.
    echo [INFO] pip install -r requirements.txt 실행 필요
    pause
)

echo.
echo [INFO] 자동매매 봇 실행 중...
echo [INFO] 대시보드: http://localhost:5000
echo [INFO] 종료하려면 Ctrl+C를 누르세요
echo.

python main.py

echo.
echo ========================================
echo 자동매매 봇 종료됨
echo ========================================
pause