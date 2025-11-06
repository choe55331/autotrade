# Config 디렉토리

이 디렉토리에는 AutoTrade Pro의 설정 파일들이 있습니다.

## ⚠️ 중요 안내

**config.yaml, credentials.yaml 등의 실제 설정 파일은 git에 커밋되지 않습니다.**

이 파일들에는 API 키, 계좌 번호 등 민감한 정보가 포함되어 있으므로
`.gitignore`에 등록되어 있습니다.

## 첫 설정 방법

### 1. config.yaml 생성

```bash
# config 디렉토리로 이동
cd config

# 예시 파일을 복사하여 실제 설정 파일 생성
cp config.example.yaml config.yaml
```

### 2. config.yaml 수정

`config.yaml` 파일을 열어서 다음 항목들을 **실제 값**으로 수정하세요:

#### 필수 수정 항목:

**API 키는 별도의 credentials 파일에서 관리됩니다!**

다음 항목들은 **절대 변경하지 마세요** (고정값):

```yaml
api:
  kiwoom:
    # ⚠️ 변경 금지 - 고정값
    base_url: "https://openapi.koreainvestment.com:9443"
    websocket_url: "wss://openapi.koreainvestment.com:9443/ws"

ai:
  gemini:
    # ⚠️ 변경 금지 - 고정값
    model: "gemini-2.5-flash"
```

#### 선택 수정 항목:

텔레그램 알림을 사용하려면:

```yaml
notification:
  telegram:
    enabled: true
    bot_token: "여기에_봇_토큰_입력"
    chat_id: "여기에_채팅ID_입력"
```

### 3. 다른 설정 파일들

다른 YAML 파일들은 자동으로 생성되거나 기본값이 사용됩니다:

- `features_config.yaml` - 기능별 설정 (자동 생성)
- `unified_settings.yaml` - 통합 설정 (자동 생성)
- `settings.yaml` - 일반 설정 (자동 생성)

## 파일 구조

```
config/
├── README.md                    (이 파일)
├── config.example.yaml          (예시 파일 - git에 포함)
├── config.yaml                  (실제 설정 - git에서 제외)
├── features_config.yaml         (자동 생성 - git에서 제외)
├── unified_settings.yaml        (자동 생성 - git에서 제외)
└── settings.yaml                (자동 생성 - git에서 제외)
```

## 주의사항

### ✅ 해야 할 것:
- `config.example.yaml`을 참고하여 `config.yaml` 생성
- 실제 API 키와 계정 정보 입력
- config 파일을 안전한 곳에 백업

### ❌ 하지 말아야 할 것:
- `config.yaml`을 git에 커밋 (자동으로 차단됨)
- API 키를 공개 저장소에 업로드
- 고정값(base_url, model 등)을 임의로 변경

## 문제 해결

### config.yaml이 없다고 나오는 경우

```bash
cd config
cp config.example.yaml config.yaml
# 그 다음 config.yaml 파일을 편집하여 실제 값 입력
```

### 설정이 계속 초기화되는 경우

config.yaml이 .gitignore에 등록되어 있는지 확인:

```bash
git check-ignore config/config.yaml
# 출력: config/config.yaml (정상)
```

### git이 config.yaml 변경을 추적하는 경우

```bash
# git tracking 제거
git rm --cached config/config.yaml

# 확인
git status
# config.yaml이 나타나지 않아야 함
```

## 보안 권장사항

1. **config.yaml을 절대 공유하지 마세요**
2. 백업 시 암호화된 저장소 사용
3. API 키가 노출되었다면 즉시 재발급
4. 주기적으로 API 키 교체 (3개월마다)

## 지원

문제가 있다면:
1. 먼저 이 README를 다시 읽어보세요
2. config.example.yaml과 비교해보세요
3. 그래도 안되면 GitHub Issues에 문의
