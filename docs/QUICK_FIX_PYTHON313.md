# Python 3.13 → 3.11 빠른 전환 가이드

## 🎯 5분 안에 해결하기

### 1단계: Python 3.11 다운로드 및 설치

**다운로드 링크:**
https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

**설치 시 반드시 체크:**
- ✅ **Add Python 3.11 to PATH**
- ✅ Install for all users (선택사항)

설치 완료 후 새 CMD 창 열기

---

### 2단계: 가상환경 생성

```cmd
# 프로젝트 디렉토리로 이동
cd C:\Users\USER\Desktop\autotrade

# Python 3.11로 가상환경 생성
py -3.11 -m venv venv311

# 가상환경 활성화
venv311\Scripts\activate

# 확인 (3.11.x로 표시되어야 함)
python --version
```

---

### 3단계: koapy 설치

```cmd
# 가상환경 활성화 상태에서
pip install --upgrade pip
pip install koapy
```

설치 완료! 이제 koapy가 작동합니다.

---

### 4단계: 테스트

```cmd
# 간단한 테스트
python tests/manual/test_koapy_simple.py
```

성공하면 로그인창이 나타납니다!

---

## 🔄 일상 사용법

### 매번 작업 시작할 때:

```cmd
# 프로젝트 디렉토리로 이동
cd C:\Users\USER\Desktop\autotrade

# 가상환경 활성화
venv311\Scripts\activate

# 이제 Python 3.11 환경에서 작업
python your_script.py
```

### VSCode에서 사용:

1. VSCode에서 프로젝트 열기
2. `Ctrl+Shift+P`
3. "Python: Select Interpreter" 입력
4. `.\venv311\Scripts\python.exe` 선택
5. 완료!

---

## ⚡ 더 빠른 방법: 배치 파일

`start_env.bat` 파일 생성:

```batch
@echo off
cd /d C:\Users\USER\Desktop\autotrade
call venv311\Scripts\activate
echo.
echo ✅ Python 3.11 환경 활성화 완료!
echo.
echo 사용 가능한 명령:
echo   python tests/manual/test_koapy_simple.py
echo   python examples/unified_main_example.py
echo.
cmd /k
```

사용법:
- `start_env.bat` 더블클릭
- 자동으로 환경 활성화됨

---

## 💡 문제 해결

### "py -3.11"이 작동하지 않으면?

Python 3.11이 PATH에 등록되지 않았을 수 있습니다.

**해결책 1: 전체 경로 사용**
```cmd
"C:\Program Files\Python311\python.exe" -m venv venv311
```

**해결책 2: Python 재설치**
- Python 3.11 재설치
- "Add to PATH" 반드시 체크

### 가상환경 활성화가 안 되면?

PowerShell 실행 정책 문제일 수 있습니다.

**해결책: CMD 사용**
```cmd
# PowerShell 대신 CMD 사용
cmd

# 가상환경 활성화
venv311\Scripts\activate
```

또는 PowerShell 정책 변경 (관리자 권한):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🎉 완료!

이제 Python 3.11 환경에서 koapy를 사용할 수 있습니다.

다음 단계:
1. ✅ `python tests/manual/test_koapy_simple.py` 실행
2. ✅ `python examples/unified_main_example.py` 실행
3. ✅ 실제 프로젝트에 통합

---

## 📌 참고

- Python 3.13은 그대로 두세요 (삭제 불필요)
- 다른 프로젝트에서는 Python 3.13 계속 사용 가능
- autotrade 프로젝트만 3.11 가상환경 사용
