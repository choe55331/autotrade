# CMD 출력 결과를 파일로 저장하기

## 방법 1: 간단한 방법 (화면에는 안 보임)

```cmd
python test_verified_apis.py > test_results\output.txt 2>&1
```

## 방법 2: 배치 파일 사용 (추천)

### 검증된 API 테스트
```cmd
run_verified_api_test.bat
```

### WebSocket 테스트
```cmd
run_websocket_test.bat
```

### main.py 실행
```cmd
run_main_save_output.bat
```

## 방법 3: PowerShell 사용 (화면에도 보이고 파일로도 저장)

```powershell
python test_verified_apis.py 2>&1 | Tee-Object -FilePath test_results\output.txt
```

## 결과 파일 위치

모든 결과는 `test_results\` 폴더에 저장됩니다:
- `verified_api_test_YYYYMMDD_HHMMSS.txt`
- `websocket_test_YYYYMMDD_HHMMSS.txt`
- `main_output_YYYYMMDD_HHMMSS.txt`

## Windows에서 tee가 없는 경우

배치 파일의 `tee` 명령이 작동하지 않으면:

1. **간단 버전 사용** (화면에 안 보임):
   ```cmd
   python test_verified_apis.py > output.txt 2>&1
   ```

2. **PowerShell로 실행** (화면에도 보임):
   ```cmd
   powershell -Command "python test_verified_apis.py 2>&1 | Tee-Object -FilePath output.txt"
   ```
