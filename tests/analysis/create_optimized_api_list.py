#!/usr/bin/env python3
"""
create_optimized_api_list.py
최적화된 최종 API 목록 생성:
1. 완전 성공 API (모든 variant 성공)
2. 부분 성공 API (성공한 variant만 포함)
3. 문서 기반 최적화 제안
4. 신규 API (문서에서 발견)
"""
import json
from pathlib import Path
from collections import defaultdict

def load_test_results():
    """테스트 결과 로드"""
    api_calls_file = Path('all_394_api_calls.json')
    with open(api_calls_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_optimizations():
    """최적화 제안 로드"""
    opt_file = Path('api_optimizations.json')
    with open(opt_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_and_optimize():
    """API 분석 및 최적화"""

    # 데이터 로드
    all_api_calls = load_test_results()
    optimizations = load_optimizations()

    # 최적화된 API 목록
    optimized_apis = {}

    # 통계
    stats = {
        'total_success_apis': 0,
        'total_success_variants': 0,
        'partial_apis': 0,
        'partial_success_variants': 0,
        'partial_removed_variants': 0,
        'total_fail_apis': 0,
        'new_apis': 0
    }

    print("="*80)
    print("최적화된 API 목록 생성")
    print("="*80)

    # API별 분석
    for api_id, info in all_api_calls.items():
        api_name = info['api_name']
        all_calls = info['all_calls']

        # 성공한 variant만 필터링
        success_calls = [
            call for call in all_calls
            if call['status'] == 'success'
        ]

        # 실패/no_data variant 수
        failed_count = len(all_calls) - len(success_calls)

        if len(success_calls) == 0:
            # 모든 variant 실패 - 제외
            stats['total_fail_apis'] += 1
            continue

        if len(success_calls) == len(all_calls):
            # 모든 variant 성공
            stats['total_success_apis'] += 1
            stats['total_success_variants'] += len(success_calls)
        else:
            # 일부 variant만 성공
            stats['partial_apis'] += 1
            stats['partial_success_variants'] += len(success_calls)
            stats['partial_removed_variants'] += failed_count

        # 성공한 호출만 저장
        optimized_apis[api_id] = {
            'api_name': api_name,
            'total_variants': len(success_calls),
            'optimized_calls': success_calls,
            'optimization_type': 'full_success' if len(success_calls) == len(all_calls) else 'partial_success',
            'removed_variants': failed_count
        }

    # 부분 실패 API 상세 로그
    print("\n🔧 부분 성공 API (실패 variant 제거)")
    print("-"*80)

    for api_id, info in optimized_apis.items():
        if info['optimization_type'] == 'partial_success':
            removed = info['removed_variants']
            kept = info['total_variants']
            print(f"[{api_id}] {info['api_name']}")
            print(f"  ✅ 유지: {kept}개 variant")
            print(f"  ❌ 제거: {removed}개 variant (no_data/실패)")

            # variant별 상세
            for call in info['optimized_calls']:
                print(f"     ✓ Var {call['variant_idx']}: {call['path']}")

    # 신규 API 추가
    new_apis = optimizations.get('new_apis', {})
    stats['new_apis'] = len(new_apis)

    # 결과 저장
    output = {
        'metadata': {
            'description': '최적화된 Kiwoom REST API 목록 - 검증된 성공 호출만 포함',
            'stats': stats,
            'optimization_rules': [
                '1. 모든 variant가 성공한 API: 모두 포함',
                '2. 일부 variant만 성공: 성공한 것만 포함, 실패는 제거',
                '3. 모든 variant 실패: 전체 제외',
                '4. status=success만 포함 (no_data, api_error 제외)'
            ]
        },
        'optimized_apis': optimized_apis,
        'new_apis_from_docs': new_apis,
        'optimization_suggestions': {
            'partial_failures': optimizations.get('partial_failures', {}),
            'total_failures': optimizations.get('total_failures', {})
        }
    }

    output_file = 'optimized_api_calls.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 통계 출력
    print("\n" + "="*80)
    print("📊 최적화 통계")
    print("="*80)
    print(f"완전 성공 API: {stats['total_success_apis']}개 ({stats['total_success_variants']}개 variant)")
    print(f"부분 성공 API: {stats['partial_apis']}개")
    print(f"  - 유지된 variant: {stats['partial_success_variants']}개")
    print(f"  - 제거된 variant: {stats['partial_removed_variants']}개")
    print(f"전체 실패 API (제외): {stats['total_fail_apis']}개")
    print(f"신규 API (문서 발견): {stats['new_apis']}개")
    print()
    print(f"최종 API 수: {len(optimized_apis)}개")
    print(f"최종 총 variant 수: {stats['total_success_variants'] + stats['partial_success_variants']}개")
    print("="*80)
    print(f"\n💾 저장 완료: {output_file}")

    # 간단한 사용 목록도 생성
    simple_list = {}
    for api_id, info in optimized_apis.items():
        simple_list[api_id] = {
            'name': info['api_name'],
            'variants': [
                {
                    'variant': call['variant_idx'],
                    'path': call['path'],
                    'body': call['body']
                }
                for call in info['optimized_calls']
            ]
        }

    simple_file = 'optimized_api_calls_simple.json'
    with open(simple_file, 'w', encoding='utf-8') as f:
        json.dump(simple_list, f, ensure_ascii=False, indent=2)

    print(f"💾 간소화 버전: {simple_file}")

    return optimized_apis, stats

if __name__ == "__main__":
    analyze_and_optimize()
