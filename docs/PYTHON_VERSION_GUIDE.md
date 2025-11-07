# Python 버전 가이드

## ⚠️ Python 3.13 호환성 문제

Python 3.13.9를 사용 중이시군요. 하지만 koapy 라이브러리가 Python 3.13과 호환되지 않습니다.

### 문제 원인

```
AttributeError: module 'configparser' has no attribute 'SafeConfigParser'
```

- Python 3.12+에서 `SafeConfigParser` 제거됨
- koapy의 의존성 `trading-calendars`가 오래된 코드 사용
- Python 3.13은 너무 최신이어서 많은 패키지 미지원

---

## ✅ 해결책

### 방법 1: Python 3.11 사용 (강력 권장)

Python 3.11은 안정적이고 대부분의 패키지가 지원합니다.

#### 1-1. Python 3.11 설치

**다운로드:**
- https://www.python.org/downloads/release/python-3119/
- Windows: "Windows installer (64-bit)" 다운로드

**설치 시 주의:**
- ✅ "Add Python 3.11 to PATH" 체크
- ✅ "Install for all users" (선택사항)

#### 1-2. 가상환경 생성

```cmd
# 프로젝트 디렉토리로 이동
cd C:\Users\USER\Desktop\autotrade

# Python 3.11로 가상환경 생성
py -3.11 -m venv venv311

# 또는 (python3.11이 PATH에 있는 경우)
python3.11 -m venv venv311

# 가상환경 활성화
venv311\Scripts\activate

# Python 버전 확인 (3.11.x여야 함)
python --version
```

#### 1-3. 패키지 설치

```cmd
# 가상환경 활성화 상태에서
pip install --upgrade pip

# koapy 설치
pip install koapy

# 추가 패키지 (필요 시)
pip install fastapi uvicorn pandas
```

#### 1-4. 테스트

```cmd
python tests/manual/test_koapy_simple.py
```

---

### 방법 2: Conda 환경 사용 (추천 대안)

Conda를 사용하면 버전 관리가 더 쉽습니다.

#### 2-1. Anaconda/Miniconda 설치

**다운로드:**
- Miniconda (가벼움): https://docs.conda.io/en/latest/miniconda.html
- Anaconda (전체): https://www.anaconda.com/download

#### 2-2. Conda 환경 생성

```cmd
# Python 3.11 환경 생성
conda create -n autotrade python=3.11

# 환경 활성화
conda activate autotrade

# Python 버전 확인
python --version  # 3.11.x

# koapy 설치
pip install koapy
```

#### 2-3. 환경 관리

```cmd
# 환경 목록 보기
conda env list

# 환경 활성화
conda activate autotrade

# 환경 비활성화
conda deactivate

# 환경 삭제 (필요시)
conda env remove -n autotrade
```

---

### 방법 3: pyenv 사용 (Linux/Mac 스타일)

Windows에서 pyenv-win 사용:

```cmd
# pyenv-win 설치 (PowerShell 관리자 권한)
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"

# Python 3.11 설치
pyenv install 3.11.9

# 전역 버전 설정
pyenv global 3.11.9

# 로컬 버전 설정 (프로젝트별)
cd C:\Users\USER\Desktop\autotrade
pyenv local 3.11.9
```

---

## 🔄 기존 Python 3.13 유지하면서 3.11 추가

Python 3.13을 삭제할 필요 없습니다. 여러 버전을 동시에 사용할 수 있습니다.

### Windows에서 여러 Python 버전 사용

```cmd
# Python 3.13 (기본)
python --version
# Python 3.13.9

# Python 3.11 (py launcher 사용)
py -3.11 --version
# Python 3.11.9

# 프로젝트별로 가상환경 분리
py -3.11 -m venv venv311  # autotrade용 (3.11)
py -3.13 -m venv venv313  # 다른 프로젝트용 (3.13)
```

---

## 📊 Python 버전 호환성 표

| 패키지 | 3.9 | 3.10 | 3.11 | 3.12 | 3.13 |
|--------|-----|------|------|------|------|
| koapy | ✅ | ✅ | ✅ | ⚠️ | ❌ |
| pywin32 | ✅ | ✅ | ✅ | ✅ | ✅ |
| pandas | ✅ | ✅ | ✅ | ✅ | ✅ |
| fastapi | ✅ | ✅ | ✅ | ✅ | ✅ |
| trading-calendars | ✅ | ✅ | ✅ | ❌ | ❌ |

**권장: Python 3.11**
- 안정적
- 대부분의 패키지 지원
- 성능 개선 (3.10 대비 10-60% 빠름)

---

## 🚀 빠른 시작 (요약)

### Windows 사용자

```cmd
# 1. Python 3.11 설치
https://www.python.org/downloads/release/python-3119/

# 2. 프로젝트 디렉토리로 이동
cd C:\Users\USER\Desktop\autotrade

# 3. 가상환경 생성 (3.11)
py -3.11 -m venv venv311

# 4. 가상환경 활성화
venv311\Scripts\activate

# 5. 패키지 설치
pip install koapy fastapi uvicorn pandas

# 6. 테스트
python tests/manual/test_koapy_simple.py
```

---

## ❓ FAQ

### Q: Python 3.13을 삭제해야 하나요?

**A:** 아니요! 여러 버전을 동시에 사용할 수 있습니다.

```cmd
# py launcher로 버전 선택
py -3.11 script.py  # 3.11 사용
py -3.13 script.py  # 3.13 사용
```

### Q: VSCode에서 Python 버전 선택은?

**A:**
1. Ctrl+Shift+P
2. "Python: Select Interpreter"
3. venv311\Scripts\python.exe 선택

### Q: PyCharm에서는?

**A:**
1. File → Settings → Project → Python Interpreter
2. Add Interpreter → Virtualenv Environment
3. venv311 경로 선택

### Q: 나중에 Python 3.13으로 돌아가려면?

**A:**
```cmd
# 3.13 가상환경으로 전환
deactivate  # 현재 환경 비활성화
venv313\Scripts\activate  # 3.13 환경 활성화
```

### Q: koapy가 3.13을 지원하게 되면?

**A:** 그때 업그레이드하면 됩니다:
```cmd
# 3.13 가상환경에서
pip install --upgrade koapy
```

---

## 🎯 다음 단계

Python 3.11 설치 후:

1. ✅ 가상환경 생성 및 활성화
2. ✅ koapy 설치
3. ✅ 테스트 실행
   ```cmd
   python tests/manual/test_koapy_simple.py
   ```
4. ✅ 통합 예제 실행
   ```cmd
   python examples/unified_main_example.py
   ```

---

## 📚 참고 자료

- Python 공식 다운로드: https://www.python.org/downloads/
- Python 버전별 변경사항: https://docs.python.org/3/whatsnew/
- koapy GitHub: https://github.com/elbakramer/koapy
- venv 공식 문서: https://docs.python.org/3/library/venv.html
- Conda 문서: https://docs.conda.io/
