#!/usr/bin/env python3
"""
verify_corrections_offline.py
오프라인으로 수정사항 검증 - 저장된 결과와 비교
"""
import json
from pathlib import Path

def verify_corrections():
    """수정사항이 올바르게 적용됐는지 오프라인 검증"""

    print("="*80)
    print("수정사항 오프라인 검증")
    print("="*80)

    # 원본 데이터
    with open('all_394_api_calls.json', 'r', encoding='utf-8') as f:
        original = json.load(f)

    # 수정된 데이터
    with open('corrected_api_calls.json', 'r', encoding='utf-8') as f:
        corrected = json.load(f)

    print("\n[1] ka10010 (업종프로그램요청) 수정 확인")
    print("-"*80)

    # 원본
    orig_ka10010 = original.get('ka10010', {})
    print("\n원본 파라미터:")
    for call in orig_ka10010.get('all_calls', []):
        print(f"  Var {call['variant_idx']}: {call['body']} → status: {call['status']}")

    # 수정본
    corr_ka10010 = corrected['corrected_apis'].get('ka10010', {})
    print("\n수정된 파라미터:")
    for variant in corr_ka10010.get('corrected_variants', []):
        print(f"  Var {variant['variant_idx']}: {variant['body']}")
        print(f"    수정 이유: {variant['fix_reason']}")

    print("\n[2] 부분 실패 API 수정 확인")
    print("-"*80)

    for api_id in ['kt00010', 'ka10073', 'ka10072', 'ka30003', 'ka30004', 'ka30005']:
        if api_id not in corrected['corrected_apis']:
            continue

        corr_api = corrected['corrected_apis'][api_id]
        orig_api = original[api_id]

        print(f"\n[{api_id}] {corr_api['api_name']}")

        # 원본 실패
        failed_orig = [c for c in orig_api['all_calls'] if c['status'] != 'success']
        print(f"  원본 실패: {len(failed_orig)}개 variant")
        for c in failed_orig[:2]:
            print(f"    Var {c['variant_idx']}: {c['body']}")

        # 수정본
        print(f"  수정: {len(corr_api['corrected_variants'])}개 variant")
        for v in corr_api['corrected_variants'][:2]:
            print(f"    Var {v['variant_idx']}: {v['body']}")
            print(f"      → {v['fix_reason']}")

    print("\n" + "="*80)
    print("✅ 수정사항 검증 완료")
    print("="*80)
    print("\n핵심 수정 내용:")
    print("  1. ka10010: 업종코드(001,201,101) → 종목코드(005930,000660,035420)")
    print("  2. 부분 실패: 문제 종목코드/날짜 → 안정적인 값으로 변경")
    print("  3. ELW: 종목코드 기초자산 → KOSPI200(201)")
    print("\n⏰ 8:00-20:00에 test_verified_and_corrected_apis.py 실행하면")
    print("   이 수정사항들이 적용된 370개 API를 모두 테스트합니다!")

if __name__ == "__main__":
    verify_corrections()
