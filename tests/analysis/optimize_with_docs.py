#!/usr/bin/env python3
"""
optimize_with_docs.py
kiwoom_docs 문서를 분석하여 실패 API 최적화 및 새 API 발견
"""
import json
import re
from pathlib import Path
from collections import defaultdict

def analyze_test_results():
    """테스트 결과 분석 - 부분 실패 API 찾기"""

    # all_394_api_calls.json 사용 (원본 로그 데이터)
    api_calls_file = Path('all_394_api_calls.json')
    if not api_calls_file.exists():
        print("❌ all_394_api_calls.json 파일이 없습니다.")
        return None, None, None

    with open(api_calls_file, 'r', encoding='utf-8') as f:
        all_api_calls = json.load(f)

    # API별로 그룹화 및 분류
    partial_fail = {}  # 일부만 성공
    total_fail = {}    # 전부 실패
    total_success = {} # 전부 성공

    for api_id, info in all_api_calls.items():
        api_name = info['api_name']
        all_calls = info['all_calls']

        # variants를 결과 형식으로 변환
        variants = []
        for call in all_calls:
            variants.append({
                'api_id': api_id,
                'api_name': api_name,
                'variant_idx': call['variant_idx'],
                'path': call['path'],
                'body': call['body'],
                'current_status': 'success' if call['status'] == 'success' else 'no_data' if call['status'] == 'no_data' else 'error',
                'return_msg': 'Original log status: ' + call['status']
            })

        success_count = sum(1 for v in variants if v['current_status'] == 'success')
        total_count = len(variants)

        if success_count == 0:
            total_fail[api_id] = variants
        elif success_count < total_count:
            partial_fail[api_id] = variants
        else:
            total_success[api_id] = variants

    return partial_fail, total_fail, total_success

def parse_api_docs():
    """kiwoom_docs 문서에서 API 정보 추출"""

    docs_dir = Path('kiwoom_docs')
    if not docs_dir.exists():
        print("❌ kiwoom_docs 폴더가 없습니다.")
        return {}

    api_info = {}

    # 모든 마크다운 파일 읽기
    for md_file in docs_dir.glob('*.md'):
        if md_file.name == '시세_backup.md':
            continue

        print(f"  📄 {md_file.name} 파싱 중...")

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # API ID 패턴: **일자별종목별실현손익요청_일자** (ka10072) 또는 #### 일자별종목별실현손익요청_일자 (ka10072)
        # 패턴 1: 마크다운 헤더 형식
        api_pattern1 = r'#+\s*([^\(]+?)\s*\(([kK][atATxX]\d{5})\)'
        # 패턴 2: 볼드 텍스트 형식
        api_pattern2 = r'\*\*([^\*]+?)\*\*\s*\(([kK][atATxX]\d{5})\)'

        for match in re.finditer(api_pattern1, content):
            api_name = match.group(1).strip()
            api_id = match.group(2).lower()

            if api_id not in api_info:
                api_info[api_id] = {
                    'name': api_name,
                    'doc_file': md_file.name,
                    'examples': [],
                    'parameters': []
                }

        for match in re.finditer(api_pattern2, content):
            api_name = match.group(1).strip()
            api_id = match.group(2).lower()

            if api_id not in api_info:
                api_info[api_id] = {
                    'name': api_name,
                    'doc_file': md_file.name,
                    'examples': [],
                    'parameters': []
                }

    print(f"\n✅ 문서에서 {len(api_info)}개 API 발견")
    return api_info

def extract_parameters_from_doc(api_id, doc_file):
    """문서에서 특정 API의 파라미터 예제 추출"""

    doc_path = Path('kiwoom_docs') / doc_file
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # API 섹션 찾기 - 패턴: #### 일자별종목별실현손익요청_일자 (ka10072) 또는 ## 일자별종목별실현손익요청_기간 (ka10073)
    api_pattern = rf'#+\s*[^\(]+?\s*\({api_id}\)'
    match = re.search(api_pattern, content, re.IGNORECASE)

    if not match:
        return []

    # 해당 섹션의 시작 위치
    section_start = match.end()

    # 다음 API 섹션까지 (또는 파일 끝까지) - 패턴: #### API명 (ka10072) 형식
    next_api = re.search(r'\n#+\s*[^\(]+?\s*\([kK][atATxX]\d{5}\)', content[section_start:])
    if next_api:
        section_end = section_start + next_api.start()
    else:
        section_end = len(content)

    section = content[section_start:section_end]

    # JSON 파라미터 추출
    json_pattern = r'\{[^{}]*\}'
    params = []

    for json_match in re.finditer(json_pattern, section):
        try:
            param = json.loads(json_match.group())
            params.append(param)
        except:
            pass

    return params

def find_new_apis(api_info, tested_apis):
    """문서에는 있지만 테스트 안 한 API 찾기"""

    doc_apis = set(api_info.keys())
    tested = set(tested_apis)

    new_apis = doc_apis - tested
    return new_apis

def optimize_partial_failures(partial_fail, api_info):
    """부분 실패 API 최적화"""

    print("\n" + "="*80)
    print("🔧 부분 실패 API 최적화 (일부 Variant만 성공)")
    print("="*80)

    optimizations = {}

    for api_id, variants in partial_fail.items():
        api_name = variants[0]['api_name']
        success_vars = [v for v in variants if v['current_status'] == 'success']
        fail_vars = [v for v in variants if v['current_status'] != 'success']

        print(f"\n[{api_id}] {api_name}")
        print(f"  성공: {len(success_vars)}개, 실패: {len(fail_vars)}개")

        # 문서에서 파라미터 예제 찾기
        if api_id in api_info:
            doc_params = extract_parameters_from_doc(api_id, api_info[api_id]['doc_file'])

            if doc_params:
                print(f"  📚 문서에서 {len(doc_params)}개 예제 발견")

                # 실패한 variant와 문서 예제 비교
                for i, fail_var in enumerate(fail_vars):
                    print(f"\n  ❌ Var {fail_var['variant_idx']}: {fail_var['return_msg'][:50]}")
                    print(f"     현재 파라미터: {fail_var['body']}")

                    # 문서 예제와 비교
                    if i < len(doc_params):
                        print(f"     📖 문서 예제: {doc_params[i]}")

                        optimizations[f"{api_id}_var{fail_var['variant_idx']}"] = {
                            'api_id': api_id,
                            'api_name': api_name,
                            'variant_idx': fail_var['variant_idx'],
                            'current_params': fail_var['body'],
                            'suggested_params': doc_params[i],
                            'path': fail_var['path']
                        }

        # 성공한 variant 패턴 분석
        if success_vars:
            print(f"\n  ✅ 성공한 Variant 패턴:")
            for succ in success_vars[:2]:  # 처음 2개만
                print(f"     Var {succ['variant_idx']}: {succ['body']}")

    return optimizations

def optimize_total_failures(total_fail, api_info):
    """전체 실패 API 최적화"""

    print("\n" + "="*80)
    print("🔧 전체 실패 API 최적화 (모든 Variant 실패)")
    print("="*80)

    optimizations = {}

    for api_id, variants in total_fail.items():
        api_name = variants[0]['api_name']

        print(f"\n[{api_id}] {api_name} - {len(variants)}개 variant 모두 실패")

        # 실패 원인 분석
        error_msgs = [v['return_msg'] for v in variants]
        common_error = max(set(error_msgs), key=error_msgs.count)
        print(f"  주 오류: {common_error[:80]}")

        # 문서에서 해결책 찾기
        if api_id in api_info:
            doc_params = extract_parameters_from_doc(api_id, api_info[api_id]['doc_file'])

            if doc_params:
                print(f"  📚 문서 예제 {len(doc_params)}개 발견")
                print(f"     추천 파라미터: {doc_params[0]}")

                optimizations[api_id] = {
                    'api_id': api_id,
                    'api_name': api_name,
                    'current_params': variants[0]['body'],
                    'suggested_params': doc_params,
                    'path': variants[0]['path'],
                    'reason': '문서 기반 최적화'
                }
        else:
            print(f"  ⚠️  문서에 정보 없음")

    return optimizations

def main():
    print("="*80)
    print("📚 kiwoom_docs 기반 API 최적화")
    print("="*80)

    # 1. 테스트 결과 분석
    print("\n[1] 테스트 결과 분석...")
    partial_fail, total_fail, total_success = analyze_test_results()

    if partial_fail is None:
        return

    print(f"  ✅ 전체 성공: {len(total_success)}개 API")
    print(f"  ⚠️  부분 실패: {len(partial_fail)}개 API (일부 variant만 성공)")
    print(f"  ❌ 전체 실패: {len(total_fail)}개 API (모든 variant 실패)")

    # 2. 문서 파싱
    print("\n[2] kiwoom_docs 문서 파싱...")
    api_info = parse_api_docs()

    # 3. 새 API 발견
    print("\n[3] 새 API 발견...")
    all_tested = set(total_success.keys()) | set(partial_fail.keys()) | set(total_fail.keys())
    new_apis = find_new_apis(api_info, all_tested)

    print(f"  🆕 문서에만 있는 API: {len(new_apis)}개")
    if new_apis:
        print("\n  새 API 목록:")
        for api_id in sorted(new_apis)[:20]:  # 처음 20개만
            print(f"    - {api_id}: {api_info[api_id]['name']}")

    # 4. 부분 실패 최적화
    partial_opts = optimize_partial_failures(partial_fail, api_info)

    # 5. 전체 실패 최적화
    total_opts = optimize_total_failures(total_fail, api_info)

    # 6. 최적화 제안 저장
    all_optimizations = {
        'partial_failures': partial_opts,
        'total_failures': total_opts,
        'new_apis': {api_id: api_info[api_id] for api_id in new_apis} if new_apis else {}
    }

    output_file = 'api_optimizations.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_optimizations, f, ensure_ascii=False, indent=2)

    print("\n" + "="*80)
    print("📊 최적화 요약")
    print("="*80)
    print(f"  부분 실패 최적화: {len(partial_opts)}개")
    print(f"  전체 실패 최적화: {len(total_opts)}개")
    print(f"  새 API 발견: {len(new_apis) if new_apis else 0}개")
    print(f"\n💾 최적화 제안 저장: {output_file}")

    # 7. 최종 통계
    print("\n" + "="*80)
    print("📈 최종 통계")
    print("="*80)
    print(f"  현재 성공: {len(total_success)}개 API")
    print(f"  최적화 가능: {len(partial_opts) + len(total_opts)}개")
    print(f"  잠재적 성공: {len(total_success) + len(partial_opts) + len(total_opts)}개")
    print(f"  신규 추가 가능: {len(new_apis) if new_apis else 0}개")
    print(f"\n  최대 달성 가능: {len(total_success) + len(partial_opts) + len(total_opts) + (len(new_apis) if new_apis else 0)}개 API")

if __name__ == "__main__":
    main()
