# Tests Directory

테스트 및 분석 스크립트 모음

## 📂 구조

```
tests/
├── api_tests/         # API 테스트 스크립트
├── analysis/          # 분석 및 디버깅 스크립트  
├── integration/       # 통합 테스트
├── archived/          # 사용하지 않는 테스트 (보관용)
└── README.md          # 이 파일
```

## 🧪 API 테스트

**최신 검증된 테스트**: `api_tests/test_verified_and_corrected_apis_fixed.py`
- 346/370 API 성공 (93.5%)
- 2025-11-01 검증 완료

## 📊 분석 도구

- `analysis/analyze_test_results.py` - 테스트 결과 분석
- `analysis/create_corrected_api_calls.py` - API 파라미터 수정

## 🔧 사용법

```bash
# 최신 API 테스트 실행
python tests/api_tests/test_verified_and_corrected_apis_fixed.py

# 테스트 결과 분석
python tests/analysis/analyze_test_results.py
```
