# Immutable Configuration Directory

이 디렉토리는 **검증되고 안정적인 설정**을 저장하는 곳입니다.

⚠️ **중요**: 이 폴더의 파일들은 함부로 수정하지 마세요!

## 📂 폴더 구조

```
_immutable/
├── api_specs/          # 검증된 API 사양 (93.5% 성공률)
│   ├── successful_apis.json         # 성공한 346개 API 목록
│   ├── apis_by_category.json        # 카테고리별 API 분류
│   └── api_usage_guide.md            # API 사용 가이드
│
├── credentials/        # 인증 정보 (gitignore됨)
│   └── secrets.json    # API 키, 계좌번호 등
│
└── README.md           # 이 파일
```

## 🎯 목적

### 1. **API 사양 안정화**
- 370개 API 테스트 후 346개 성공 (93.5% 성공률)
- 검증된 파라미터만 저장
- 실패한 API는 제외

### 2. **중앙 집중식 설정 관리**
- 모든 모듈(대시보드, 리서치, 전략)이 이 설정을 참조
- 일관성 보장
- 유지보수 용이

### 3. **보안 강화**
- credentials 폴더는 .gitignore에 추가
- 민감한 정보 분리

## 🔒 보안 정책

### gitignore 설정
```gitignore
# Immutable credentials (NEVER commit!)
_immutable/credentials/secrets.json
_immutable/credentials/*.key
_immutable/credentials/*.pem
```

### 파일 권한 (Linux/Mac)
```bash
chmod 600 _immutable/credentials/secrets.json  # Owner read/write only
chmod 700 _immutable/credentials/               # Owner access only
```

## 📊 성능 데이터

### 테스트 결과 (2025-11-01)
- **총 테스트**: 370개 API 호출
- **성공**: 346개 (93.5%)
- **데이터 없음**: 20개
- **오류**: 4개

### 개선 사항
- ka10010: 업종코드 → 종목코드 수정 (3개 variant 성공)
- 부분 실패 API: 파라미터 최적화 (12개 추가 성공)

## 🚀 사용 방법

### Python에서 사용
```python
from config.api_loader import load_successful_apis, get_api_by_category

# 성공한 모든 API 로드
apis = load_successful_apis()

# 카테고리별 API 가져오기
account_apis = get_api_by_category('account')
market_apis = get_api_by_category('market')
ranking_apis = get_api_by_category('ranking')
```

### Dashboard에서 사용
```python
from _immutable.api_specs import SUCCESSFUL_APIS

# API 호출
result = client.call_api(
    api_id=SUCCESSFUL_APIS['kt00005']['api_id'],
    body=SUCCESSFUL_APIS['kt00005']['optimized_calls'][0]['body'],
    path=SUCCESSFUL_APIS['kt00005']['optimized_calls'][0]['path']
)
```

## 📝 변경 이력

### 2025-11-01 - 초기 생성
- 370개 API 테스트 완료
- 346개 성공 API 저장
- 카테고리 분류 완료
- credentials 분리

## ⚙️ 유지보수 규칙

### ✅ 허용되는 작업
- API 사용 통계 업데이트
- 문서화 개선
- 새로운 성공 API 추가 (테스트 후)

### ❌ 금지되는 작업
- 검증되지 않은 API 추가
- 성공한 API의 파라미터 임의 수정
- credentials 파일 버전 관리 추가

## 📞 문의

API 설정 관련 문의:
- 파일: config/api_loader.py
- 문서: API_USAGE_GUIDE.md
