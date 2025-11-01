@echo off
REM 검증된 API 테스트 - 간단 버전 (화면에 안 보임, 파일로만 저장)

echo ============================================================
echo 검증된 API 370건 테스트 시작
echo ============================================================
echo.

REM 결과 디렉토리 생성
if not exist test_results mkdir test_results

REM 현재 시간으로 파일명 생성
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-3 delims=:. " %%a in ('echo %time%') do (set mytime=%%a%%b%%c)
set timestamp=%mydate%_%mytime%

REM 파일명 설정
set output_file=test_results\verified_api_test_%timestamp%.txt

echo 테스트 실행 중... (결과는 파일로만 저장됩니다)
echo 결과 파일: %output_file%
echo.

REM 테스트 실행 및 결과 저장
python test_verified_apis.py > %output_file% 2>&1

echo.
echo ============================================================
echo 테스트 완료!
echo 결과 저장: %output_file%
echo ============================================================
echo.

REM 결과 파일 열기
notepad %output_file%
