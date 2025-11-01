@echo off
REM main.py 실행 결과 저장 - 간단 버전

echo ============================================================
echo AutoTrade Pro v2.0 실행 결과 저장
echo ============================================================
echo.

REM 결과 디렉토리 생성
if not exist test_results mkdir test_results

REM 현재 시간으로 파일명 생성
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-3 delims=:. " %%a in ('echo %time%') do (set mytime=%%a%%b%%c)
set timestamp=%mydate%_%mytime%

REM 파일명 설정
set output_file=test_results\main_output_%timestamp%.txt

echo 실행 중... (결과는 파일로만 저장됩니다)
echo 결과 파일: %output_file%
echo.
echo ⚠️  Ctrl+C를 눌러 중지할 수 있습니다
echo.

REM main.py 실행 및 결과 저장
python main.py > %output_file% 2>&1

echo.
echo ============================================================
echo 실행 완료!
echo 결과 저장: %output_file%
echo ============================================================
echo.

REM 결과 파일 열기
notepad %output_file%
