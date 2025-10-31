# Windows 설치 가이드 - AutoTrade Pro v2.0

## ⚠️ 사전 요구사항

### 1. Python 설치
- **Python 3.10 이상** 필수
- 공식 사이트: https://www.python.org/downloads/
- 설치 시 **"Add Python to PATH"** 체크 필수!

### 2. Python 버전 확인
```cmd
python --version
```
출력 예시: `Python 3.10.11` 또는 `Python 3.11.x`

## 🚀 설치 방법

### 단계 1: 프로젝트 다운로드
```cmd
cd C:\Users\USER\Desktop
git clone https://github.com/your-repo/autotrade.git
cd autotrade
```

### 단계 2: 가상환경 생성 (권장)
```cmd
python -m venv venv
venv\Scripts\activate
```

### 단계 3: 패키지 설치

#### 방법 A: 한 번에 설치 (권장)
```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

#### 방법 B: 단계별 설치 (A가 실패할 경우)

```cmd
# 1. 기본 패키지
pip install requests urllib3
pip install python-dotenv PyYAML
pip install colorlog loguru
pip install pytz python-dateutil

# 2. 데이터 처리 (최신 버전 - pre-built wheels)
pip install --upgrade numpy pandas

# 3. 웹 프레임워크
pip install Flask Werkzeug
pip install flask-socketio python-socketio

# 4. 데이터베이스
pip install SQLAlchemy

# 5. WebSocket
pip install websocket-client

# 6. AI 분석
pip install google-generativeai
```

### 단계 4: 환경 변수 설정

`.env` 파일 생성 (프로젝트 루트에):
```env
# Kiwoom API
KIWOOM_APP_KEY=your_app_key_here
KIWOOM_APP_SECRET=your_app_secret_here
KIWOOM_ACCOUNT_NO=your_account_number

# AI API Keys
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional
ANTHROPIC_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_gpt4_api_key
```

### 단계 5: 설정 파일 확인
`config/config.yaml` 파일을 열어 필요한 설정 조정

### 단계 6: 실행
```cmd
python main.py
```

## 🐛 문제 해결

### 문제 1: "pip is not recognized"
**해결책**: Python 재설치 시 "Add Python to PATH" 체크

또는 수동으로 PATH 추가:
1. 시스템 속성 → 환경 변수
2. Path에 Python 경로 추가 (예: `C:\Python310\Scripts`)

### 문제 2: pandas 설치 실패 (metadata-generation-failed)
**원인**: Visual Studio Build Tools 부재

**해결책 A**: 최신 pandas 사용 (pre-built wheel)
```cmd
pip install --upgrade pip
pip install pandas>=2.2.0
```

**해결책 B**: Visual Studio Build Tools 설치
1. https://visualstudio.microsoft.com/ko/downloads/
2. "Build Tools for Visual Studio" 다운로드
3. "C++ 빌드 도구" 선택하여 설치

**해결책 C**: Anaconda 사용
```cmd
# Anaconda 설치 후
conda install pandas numpy
pip install -r requirements.txt
```

### 문제 3: "No module named 'ta'"
**해결책**: ta 패키지는 선택사항입니다.

기술적 분석이 필요한 경우:
```cmd
pip install ta
```

또는 대체 패키지:
```cmd
pip install pandas-ta
```

### 문제 4: Flask-SocketIO 설치 오류
**해결책**:
```cmd
pip install --upgrade pip setuptools wheel
pip install flask-socketio python-socketio
```

### 문제 5: SQLAlchemy 버전 충돌
**해결책**:
```cmd
pip uninstall SQLAlchemy
pip install SQLAlchemy>=2.0.0
```

## ✅ 설치 검증

설치가 잘 되었는지 확인:

```cmd
python -c "import pandas; print(pandas.__version__)"
python -c "import flask; print(flask.__version__)"
python -c "import yaml; print('PyYAML OK')"
python -c "from loguru import logger; print('Loguru OK')"
python -c "from sqlalchemy import __version__; print(__version__)"
```

모든 명령이 에러 없이 출력되면 성공!

## 🎯 최소 요구사항 (필수 패키지만)

시스템을 최소한으로 실행하려면:

```cmd
pip install requests pandas numpy Flask PyYAML loguru SQLAlchemy python-dotenv
```

## 📦 선택적 패키지

### AI 분석 기능 사용 시:
```cmd
pip install google-generativeai
```

### WebSocket 실시간 기능 사용 시:
```cmd
pip install flask-socketio python-socketio websocket-client
```

### 기술적 분석 사용 시:
```cmd
pip install ta
```

## 🔧 Python 버전별 권장사항

| Python 버전 | 권장 여부 | 비고 |
|-------------|-----------|------|
| 3.12.x | ⚠️ 주의 | 일부 패키지 호환성 문제 |
| 3.11.x | ✅ 권장 | 최적 성능 |
| 3.10.x | ✅ 권장 | 안정적 |
| 3.9.x | ⚠️ 주의 | 일부 기능 제한 |
| 3.8.x 이하 | ❌ 비권장 | 미지원 |

## 💡 팁

### 가상환경 사용 권장
```cmd
# 가상환경 생성
python -m venv venv

# 활성화
venv\Scripts\activate

# 비활성화 (나중에)
deactivate
```

### pip 업그레이드
```cmd
python -m pip install --upgrade pip
```

### 캐시 없이 재설치
```cmd
pip install --no-cache-dir -r requirements.txt
```

### 특정 패키지만 재설치
```cmd
pip uninstall pandas
pip install pandas>=2.2.0
```

## 🆘 여전히 문제가 있다면?

1. **Python 버전 확인**: `python --version`
2. **pip 버전 확인**: `pip --version`
3. **에러 메시지 전체 복사**
4. **GitHub Issues에 문의**

## 📞 추가 도움말

- Python 공식 문서: https://docs.python.org/ko/3/
- pip 문서: https://pip.pypa.io/en/stable/
- pandas 설치 가이드: https://pandas.pydata.org/docs/getting_started/install.html

---

**설치 완료 후 `python main.py`로 시스템을 시작하세요!** 🚀
