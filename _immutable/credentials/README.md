# 🔐 API 키 및 민감정보 보호 설정

이 폴더는 **절대 변경되면 안 되는** API 키와 민감정보를 안전하게 보관합니다.

## 📋 설정 방법

### ✅ 권장: 자동 설정 스크립트 사용

프로젝트 루트에서 다음 명령어를 실행하세요:

```bash
python setup_secrets.py
```

스크립트가 다음을 자동으로 처리합니다:
- 안전한 입력 방식으로 API 키 수집
- secrets.json 파일 생성
- 파일 권한을 읽기 전용(400)으로 설정

### 🔧 수동 설정

1. **템플릿 복사**
   ```bash
   cp _immutable/credentials/secrets.example.json _immutable/credentials/secrets.json
   ```

2. **API 키 입력**
   ```bash
   # 편집기로 열기
   nano _immutable/credentials/secrets.json
   # 또는
   vim _immutable/credentials/secrets.json
   ```

3. **읽기 전용으로 보호**
   ```bash
   chmod 400 _immutable/credentials/secrets.json
   ```

## 🔑 필수 설정 항목

secrets.json에는 다음 항목들이 **반드시** 포함되어야 합니다:

### 1. 키움증권 REST API
- `base_url`: REST API URL (예: https://api.kiwoom.com)
- `appkey`: 앱키
- `secretkey`: 시크릿키
- `account_number`: 계좌번호 (형식: 12345678-01)

### 2. 키움증권 WebSocket
- `url`: WebSocket URL (예: wss://api.kiwoom.com:10000/api/dostk/websocket)

### 3. Google Gemini API
- `api_key`: Gemini API 키
- `model_name`: 모델명 (예: gemini-2.5-flash)

### 4. Telegram (선택사항)
- `bot_token`: 텔레그램 봇 토큰
- `chat_id`: 텔레그램 채팅 ID

## ⚠️ 중요 보안 수칙

### ✅ 해야 할 것
- secrets.json 파일을 읽기 전용(chmod 400)으로 설정
- 파일을 정기적으로 백업 (안전한 곳에)
- API 키가 유출되었다면 즉시 재발급

### ❌ 하지 말아야 할 것
- **절대 git에 커밋하지 마세요!** (이미 .gitignore에 추가됨)
- 다른 사람과 공유하지 마세요
- 코드에 하드코딩하지 마세요
- 공개 저장소에 업로드하지 마세요

## 🔄 설정 수정 방법

파일이 읽기 전용으로 보호되어 있어 직접 수정이 불가능합니다.

### 방법 1: setup_secrets.py 다시 실행 (권장)
```bash
python setup_secrets.py
```

### 방법 2: 수동 수정
```bash
# 1. 쓰기 권한 부여
chmod 600 _immutable/credentials/secrets.json

# 2. 편집
nano _immutable/credentials/secrets.json

# 3. 다시 읽기 전용으로 설정
chmod 400 _immutable/credentials/secrets.json
```

## 🔍 파일 상태 확인

```bash
# 파일 존재 여부 확인
ls -la _immutable/credentials/secrets.json

# 파일 권한 확인 (400이어야 함)
stat -c "%a %n" _immutable/credentials/secrets.json
```

## 🆘 문제 해결

### secrets.json 파일이 없다는 오류
```
❌ secrets.json 파일이 없습니다!
```

**해결 방법:**
```bash
python setup_secrets.py
```

### 권한 오류
```
Permission denied: secrets.json
```

**해결 방법:**
```bash
# 쓰기 권한 임시 부여
chmod 600 _immutable/credentials/secrets.json

# 작업 후 다시 읽기 전용으로
chmod 400 _immutable/credentials/secrets.json
```

### API 키가 자꾸 변경되는 문제
이 설정을 사용하면 **secrets.json이 절대 수정되지 않습니다**:
- 파일이 읽기 전용(400)으로 보호됨
- 코드에 하드코딩된 기본값이 없음
- secrets.json이 없으면 프로그램이 시작되지 않음

## 📚 관련 파일

- `secrets.json` - 실제 API 키 (git에서 제외, 읽기 전용)
- `secrets.example.json` - 템플릿 파일 (git에 포함)
- `../../config/credentials.py` - 이 파일을 로드하는 코드
- `../../setup_secrets.py` - 설정 도우미 스크립트

## 📞 지원

문제가 계속되면:
1. 파일 권한 확인: `ls -la _immutable/credentials/secrets.json`
2. JSON 유효성 검증: `python -m json.tool _immutable/credentials/secrets.json`
3. 로그 확인: 프로그램 실행 시 표시되는 오류 메시지
