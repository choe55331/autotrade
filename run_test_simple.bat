#!/bin/bash
# 간단한 출력 리다이렉션 스크립트 (tee 없이)

# 검증된 API 테스트
echo "검증된 API 테스트 결과를 파일로 저장합니다..."
python test_verified_apis.py > test_results/verified_api_test.txt 2>&1
echo "저장 완료: test_results/verified_api_test.txt"
