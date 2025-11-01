# 🚀 AutoTrade Pro 설정 가이드

AutoTrade Pro를 처음 실행하기 위한 설정 가이드입니다.

---

## 📋 목차

1. [필수 설정](#필수-설정)
2. [선택 설정](#선택-설정)
3. [실행 방법](#실행-방법)
4. [문제 해결](#문제-해결)

---

## 🔧 필수 설정

### 1️⃣ API 키 설정 (필수)

**⚠️ 가장 중요한 단계입니다!**

```bash
python setup_secrets.py
```

이 스크립트를 실행하면 다음 정보를 입력받습니다:

#### 입력 항목:
1. **키움증권 REST API**
   - REST API URL (기본값: https://api.kiwoom.com)
   - 앱키 (App Key)
   - 시크릿키 (Secret Key)
   - 계좌번호 (형식: 12345678-01)

2. **키움증권 WebSocket**
   - WebSocket URL (기본값: wss://api.kiwoom.com:10000/api/dostk/websocket)

3. **Google Gemini API**
   - Gemini API Key
   - 모델명 (기본값: gemini-2.5-flash)

4. **Telegram Bot (선택)**
   - Bot Token
   - Chat ID

**완료 후:**
- `_immutable/credentials/secrets.json` 파일이 생성됩니다
- 파일은 자동으로 읽기 전용(chmod 400)으로 보호됩니다
- **절대 git에 커밋되지 않습니다** (.gitignore에 포함됨)

---

### 2️⃣ config.yaml 설정 (자동 완료)

프로그램을 처음 실행하면 자동으로 생성됩니다.

**수동으로 생성하려면:**
```bash
cp config/config.example.yaml config/config.yaml
```

**config.yaml 파일의 특징:**
- 트레이딩 전략, 리스크 관리 등 설정
- API 키는 포함되지 않음 (secrets.json에서 자동 로드)
- git에 커밋되지 않음 (.gitignore에 포함)

---

## 🎨 선택 설정

### Telegram 알림 활성화

`setup_secrets.py` 실행 시 Telegram 정보를 입력하면 자동으로 활성화됩니다.

또는 `config.yaml`에서 수동 설정:

```yaml
notification:
  telegram:
    enabled: true  # false → true로 변경
```

---

## ▶️ 실행 방법

### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 프로그램 실행

```bash
python main.py
```

### 3. 대시보드 접속

브라우저에서 http://localhost:5000 접속

---

## 🔍 파일 구조

```
autotrade/
├── setup_secrets.py                    # API 키 설정 스크립트
├── main.py                             # 메인 실행 파일
├── config/
│   ├── config.example.yaml             # 설정 템플릿 (git에 포함)
│   └── config.yaml                     # 실제 설정 (git에서 제외)
└── _immutable/
    └── credentials/
        ├── secrets.example.json        # API 키 템플릿 (git에 포함)
        ├── secrets.json                # 실제 API 키 (git에서 제외, 읽기 전용)
        └── README.md                   # API 키 설명서
```

---

## 🛠️ 문제 해결

### ❌ `secrets.json 파일이 없습니다!`

**해결방법:**
```bash
python setup_secrets.py
```

---

### ❌ `config.yaml을 찾을 수 없습니다`

**해결방법:**
```bash
cp config/config.example.yaml config/config.yaml
```

---

### ❌ `복사 붙여넣기가 안 돼요`

**해결방법:**
- setup_secrets.py는 복사 붙여넣기를 지원합니다
- Ctrl+V (Windows/Linux) 또는 Cmd+V (Mac) 사용
- 터미널에서 우클릭 → 붙여넣기도 가능

---

### ❌ `API 키를 수정하고 싶어요`

**해결방법:**

#### 방법 1: setup_secrets.py 다시 실행 (권장)
```bash
python setup_secrets.py
```

#### 방법 2: 수동 수정
```bash
# 1. 쓰기 권한 부여
chmod 600 _immutable/credentials/secrets.json

# 2. 편집
nano _immutable/credentials/secrets.json

# 3. 다시 읽기 전용으로
chmod 400 _immutable/credentials/secrets.json
```

---

### ❌ `Telegram 알림이 안 와요`

**확인사항:**
1. `setup_secrets.py`에서 Bot Token과 Chat ID를 정확히 입력했는지 확인
2. Telegram Bot이 활성화되어 있는지 확인
3. Chat ID가 올바른지 확인 (숫자여야 함)

**재설정:**
```bash
python setup_secrets.py
```

---

## 📞 추가 도움

- API 키 관련: `_immutable/credentials/README.md` 참고
- 전체 설정: `config/config.example.yaml` 주석 참고
- 문제 보고: GitHub Issues

---

## 🔒 보안 주의사항

### ✅ 안전한 파일 (git에 포함 안 됨)
- `_immutable/credentials/secrets.json` - API 키
- `config/config.yaml` - 개인 설정

### ⚠️ 절대 하지 마세요
- secrets.json을 git에 커밋
- API 키를 코드에 하드코딩
- secrets.json을 다른 사람과 공유
- 공개 저장소에 업로드

### 🛡️ 자동 보호 기능
- secrets.json은 자동으로 chmod 400 (읽기 전용)
- .gitignore로 git 커밋 차단
- AI도 수정 불가능

---

**설정이 완료되었으면 `python main.py`를 실행하세요!** 🚀
