# Python 3.13에서 koapy 사용하기

Python 3.13을 유지하면서 koapy를 사용하는 여러 방법을 시도해봅니다.

---

## 방법 1: trading-calendars 대신 exchange-calendars 사용

`exchange-calendars`는 `trading-calendars`의 개선된 버전으로 Python 3.13을 지원합니다.

### 시도 1-A: exchange-calendars로 대체 설치

```cmd
# 1. exchange-calendars 먼저 설치 (Python 3.13 지원)
pip install exchange-calendars

# 2. koapy 설치 시 trading-calendars 제외
pip install koapy --no-deps

# 3. koapy의 다른 의존성 수동 설치
pip install grpcio grpcio-tools
pip install pyhocon
pip install tqdm
pip install tabulate
pip install deprecated
pip install psutil
pip install pycryptodomex
pip install Rx
pip install pandas
pip install pywin32
pip install PyQt5 PySide2
```

### 시도 1-B: requirements 파일로 제어

`requirements_koapy_313.txt` 생성:

```txt
# koapy의 의존성들 (trading-calendars 제외)
grpcio>=1.44.0
grpcio-tools>=1.44.0
pyhocon>=0.3.58
tqdm>=4.62.3
tabulate>=0.8.9
deprecated>=1.2.13
psutil>=5.9.0
pycryptodomex>=3.14.1
Rx>=3.1.1
pandas>=1.3.5
pywin32>=303
PyQt5>=5.15.6
PySide2>=5.15.2.1

# trading-calendars 대신 exchange-calendars
exchange-calendars>=4.0.0

# koapy (의존성 체크 없이)
koapy --no-deps
```

설치:
```cmd
pip install -r requirements_koapy_313.txt
```

---

## 방법 2: trading-calendars 패치 설치

Python 3.13 호환성 패치를 적용한 버전을 설치합니다.

### 패치 버전 설치 스크립트

`install_koapy_313.py` 생성:

```python
"""
Python 3.13에서 koapy 설치 헬퍼
trading-calendars의 SafeConfigParser 문제를 우회합니다.
"""
import subprocess
import sys
import os
from pathlib import Path

def patch_trading_calendars():
    """trading-calendars 소스 패치"""
    # pip로 소스 다운로드
    subprocess.run([
        sys.executable, "-m", "pip", "download",
        "--no-binary", ":all:",
        "--no-deps",
        "trading-calendars==2.1.1"
    ])

    # tar.gz 압축 해제
    import tarfile
    tar_file = Path("trading_calendars-2.1.1.tar.gz")
    if tar_file.exists():
        with tarfile.open(tar_file) as tar:
            tar.extractall()

    # versioneer.py 패치
    versioneer_path = Path("trading_calendars-2.1.1/versioneer.py")
    if versioneer_path.exists():
        content = versioneer_path.read_text()

        # SafeConfigParser → ConfigParser
        content = content.replace(
            "configparser.SafeConfigParser()",
            "configparser.ConfigParser()"
        )

        versioneer_path.write_text(content)

        print("✅ versioneer.py 패치 완료")

        # 패치된 버전 설치
        os.chdir("trading_calendars-2.1.1")
        subprocess.run([sys.executable, "setup.py", "install"])
        os.chdir("..")

        print("✅ trading-calendars 설치 완료")
        return True

    return False

def install_koapy():
    """koapy 및 의존성 설치"""
    print("📦 koapy 의존성 설치 중...")

    # trading-calendars 패치 설치
    if patch_trading_calendars():
        # koapy 설치 (의존성 체크 없이)
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "koapy", "--no-deps"
        ])

        # 나머지 의존성 설치
        deps = [
            "grpcio", "grpcio-tools", "pyhocon", "tqdm",
            "tabulate", "deprecated", "psutil", "pycryptodomex",
            "Rx", "pandas", "pywin32", "PyQt5", "PySide2"
        ]

        for dep in deps:
            print(f"설치 중: {dep}")
            subprocess.run([sys.executable, "-m", "pip", "install", dep])

        print("✅ koapy 설치 완료!")
        return True
    else:
        print("❌ trading-calendars 패치 실패")
        return False

if __name__ == "__main__":
    install_koapy()
```

실행:
```cmd
python install_koapy_313.py
```

---

## 방법 3: koapy 없이 직접 구현 (최후의 수단)

koapy의 핵심 기능만 직접 구현합니다.

### 3-A: 32비트 서버 직접 작성

`server_32bit.py` (32비트 Python에서 실행):

```python
"""
32비트 서버 - 키움 OCX 직접 제어
"""
from flask import Flask, jsonify, request
import win32com.client
import pythoncom

app = Flask(__name__)
ocx = None

@app.route('/connect', methods=['POST'])
def connect():
    global ocx
    pythoncom.CoInitialize()
    ocx = win32com.client.Dispatch("KHOPENAPI.KHOpenAPICtrl.1")
    ret = ocx.CommConnect()
    return jsonify({'success': ret == 0})

@app.route('/stock/<code>', methods=['GET'])
def get_stock(code):
    # OCX 메서드 호출
    name = ocx.GetMasterCodeName(code)
    price = ocx.GetMasterLastPrice(code)
    return jsonify({'code': code, 'name': name, 'price': price})

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
```

### 3-B: 64비트 클라이언트

`client_64bit.py` (64비트 Python에서 실행):

```python
"""
64비트 클라이언트 - 32비트 서버와 통신
"""
import requests

BASE_URL = "http://localhost:5000"

def connect():
    response = requests.post(f"{BASE_URL}/connect")
    return response.json()

def get_stock(code):
    response = requests.get(f"{BASE_URL}/stock/{code}")
    return response.json()

if __name__ == '__main__':
    # 연결
    result = connect()
    print(f"연결: {result}")

    # 주식 정보 조회
    stock = get_stock('005930')
    print(f"삼성전자: {stock}")
```

사용법:
```cmd
# 1. 32비트 Python으로 서버 실행
python32 server_32bit.py

# 2. 64비트 Python으로 클라이언트 실행 (새 터미널)
python client_64bit.py
```

---

## 방법 4: Conda 환경 분리 (가장 실용적)

Python 3.13 메인 환경 유지하면서 koapy용 3.11 환경 생성:

```cmd
# 1. 메인 환경은 Python 3.13 유지
python --version  # 3.13.9

# 2. koapy용 Conda 환경 생성 (3.11)
conda create -n koapy311 python=3.11
conda activate koapy311
pip install koapy

# 3. 사용할 때만 koapy311 활성화
conda activate koapy311
python your_script.py

# 4. 평소에는 3.13 사용
conda deactivate
python --version  # 3.13.9
```

**장점:**
- Python 3.13 유지
- koapy 사용 시에만 3.11로 전환
- 환경 간 완전 분리
- 명령어 하나로 전환

---

## 방법 5: Docker 사용 (고급)

Docker로 32비트 서버를 컨테이너로 실행:

`Dockerfile.koapy`:
```dockerfile
FROM python:3.11-windowsservercore

WORKDIR /app

RUN pip install koapy

EXPOSE 5943

CMD ["koapy", "serve"]
```

사용:
```cmd
# 1. 이미지 빌드
docker build -t koapy-server -f Dockerfile.koapy .

# 2. 컨테이너 실행
docker run -d -p 5943:5943 koapy-server

# 3. 64비트 Python에서 접속
python client.py  # localhost:5943로 연결
```

---

## 🎯 권장 순서

### 우선 시도 (쉬운 순서):

1. **방법 1-A: exchange-calendars 대체**
   ```cmd
   pip install exchange-calendars
   pip install koapy --no-deps
   pip install grpcio grpcio-tools pyhocon tqdm tabulate deprecated psutil pycryptodomex Rx pandas pywin32 PyQt5
   ```

2. **방법 4: Conda 환경 분리** (가장 안정적)
   ```cmd
   conda create -n koapy311 python=3.11
   conda activate koapy311
   pip install koapy
   ```

3. **방법 2: trading-calendars 패치**
   ```cmd
   python install_koapy_313.py
   ```

### 확인 방법:

각 방법 시도 후:
```cmd
python -c "import koapy; print('✅ koapy 로드 성공!')"
```

---

## ❓ FAQ

### Q: 어느 방법이 가장 좋나요?

**A:**
- **가장 쉬움**: 방법 4 (Conda 환경)
- **가장 깔끔**: 방법 1 (exchange-calendars)
- **가장 안정적**: 방법 4 (Conda)

### Q: Python 3.13을 꼭 써야 하나요?

**A:** 특별한 이유가 없다면 3.11 추천:
- koapy뿐만 아니라 많은 패키지가 3.13 미지원
- 3.11이 충분히 빠르고 안정적
- 3.13의 새 기능이 꼭 필요한 경우만 고집

### Q: Conda 없이 venv로 불가능한가요?

**A:** 가능합니다:
```cmd
# 3.11 설치 후
py -3.11 -m venv venv311
venv311\Scripts\activate
pip install koapy

# 사용 시
venv311\Scripts\activate  # koapy 사용
deactivate  # 3.13으로 복귀
```

---

## 🧪 테스트 스크립트

각 방법 시도 후 실행:

`test_koapy_import.py`:
```python
"""koapy 로드 테스트"""
import sys
import struct

print(f"Python 버전: {sys.version}")
print(f"Python 비트: {struct.calcsize('P') * 8}-bit")
print()

try:
    import koapy
    print("✅ koapy 로드 성공!")

    from koapy import KiwoomOpenApiPlusEntrypoint
    print("✅ KiwoomOpenApiPlusEntrypoint 로드 성공!")

    print("\n모든 테스트 통과! 🎉")

except ImportError as e:
    print(f"❌ 로드 실패: {e}")
except Exception as e:
    print(f"❌ 오류: {e}")
```

---

## 📊 방법 비교

| 방법 | 난이도 | 안정성 | Python 3.13 유지 | 권장도 |
|------|--------|--------|------------------|--------|
| 1. exchange-calendars | 중 | 중 | ✅ | ⭐⭐⭐ |
| 2. trading-calendars 패치 | 고 | 중 | ✅ | ⭐⭐ |
| 3. 직접 구현 | 최고 | 중 | ✅ | ⭐ |
| 4. Conda 환경 | 하 | 최고 | ✅ | ⭐⭐⭐⭐⭐ |
| 5. Docker | 고 | 고 | ✅ | ⭐⭐⭐ |

**최종 권장: 방법 4 (Conda 환경)**
- 가장 쉽고 안정적
- Python 3.13 유지
- 명령어 하나로 전환
