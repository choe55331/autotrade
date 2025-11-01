@echo off
REM 검증된 API 테스트 실행 및 결과 저장

echo ============================================================
echo 검증된 API 370건 테스트 시작
echo ============================================================
echo.
echo 결과 파일: test_results\verified_api_test_result.txt
echo.

REM 결과 디렉토리 생성
if not exist test_results mkdir test_results

REM 현재 시간으로 파일명 생성
set timestamp=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%

REM 파일명 설정
set output_file=test_results\verified_api_test_%timestamp%.txt

REM 테스트 실행 및 결과 저장 (화면에도 출력)
python test_verified_apis.py 2>&1 | tee %output_file%

echo.
echo ============================================================
echo 테스트 완료!
echo 결과 저장: %output_file%
echo ============================================================

pause
