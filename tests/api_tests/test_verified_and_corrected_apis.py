test_verified_and_corrected_apis.py
검증된 API + 수정된 API 엄격한 데이터 검증 테스트

test_all_394_calls.py처럼 실제 데이터 수신 여부를 확인:
- return_code = 0
- 데이터 키 존재 (return_code, return_msg 제외)
- 데이터가 비어있지 않음
- LIST는 실제 아이템 포함
import json
import sys
from pathlib import Path
from datetime import datetime, time
from collections import defaultdict

try:
    from core.rest_client import KiwoomRESTClient
except ImportError:
    print("❌ core.rest_client 모듈을 찾을 수 없습니다.")
    sys.exit(1)

def check_time_allowed():
    """실행 가능 시간 확인 (8:00-20:00)"""
    now = datetime.now().time()
    start_time = time(8, 0)
    end_time = time(20, 0)
    return start_time <= now <= end_time, now

def validate_data_strictly(result):
    """엄격한 데이터 검증

    진짜 성공 조건:
    1. return_code = 0
    2. 데이터 키가 있음 (return_code, return_msg 제외)
    3. 데이터가 비어있지 않음
    4. LIST 타입은 실제 아이템 포함

    Returns:
        dict: {
            'is_real_success': bool,
            'return_code': int,
            'return_msg': str,
            'data_keys': list,
            'data_items_count': int,
            'validation_details': str
        }
    """

    if result is None:
        return {
            'is_real_success': False,
            'return_code': -1,
            'return_msg': 'API 응답 없음 (None)',
            'data_keys': [],
            'data_items_count': 0,
            'validation_details': '응답 자체가 None'
        }

    return_code = result.get('return_code', -1)
    return_msg = result.get('return_msg', 'Unknown')

    if return_code != 0:
        return {
            'is_real_success': False,
            'return_code': return_code,
            'return_msg': return_msg,
            'data_keys': [],
            'data_items_count': 0,
            'validation_details': f'return_code={return_code}'
        }

    data_keys = [k for k in result.keys() if k not in ['return_code', 'return_msg']]

    if len(data_keys) == 0:
        return {
            'is_real_success': False,
            'return_code': return_code,
            'return_msg': return_msg,
            'data_keys': [],
            'data_items_count': 0,
            'validation_details': '데이터 키 없음 (return_code=0이지만 no_data)'
        }

    data_items_count = 0
    empty_keys = []
    list_keys = []

    for key in data_keys:
        value = result[key]

        if value is None or value == '':
            empty_keys.append(key)
            continue

        if isinstance(value, list):
            list_keys.append(key)
            if len(value) > 0:
                data_items_count += len(value)
            else:
                empty_keys.append(f'{key}[]')
        elif isinstance(value, dict):
            if len(value) > 0:
                data_items_count += 1
            else:
                empty_keys.append(f'{key}{{}}')
        else:
            data_items_count += 1

    is_real_success = data_items_count > 0

    if is_real_success:
        details = f'{data_items_count}개 데이터 아이템'
        if list_keys:
            details += f' (LIST: {", ".join(list_keys)})'
    else:
        details = f'데이터 키는 있지만 모두 비어있음: {data_keys}'

    return {
        'is_real_success': is_real_success,
        'return_code': return_code,
        'return_msg': return_msg,
        'data_keys': data_keys,
        'data_items_count': data_items_count,
        'validation_details': details
    }

def test_api_call(client, api_id, api_name, path, body):
    """단일 API 호출 및 엄격한 검증"""

    try:
        result = client.request(api_id, body, path)
        validation = validate_data_strictly(result)

        return {
            'success': validation['is_real_success'],
            'return_code': validation['return_code'],
            'return_msg': validation['return_msg'],
            'data_keys': validation['data_keys'],
            'data_items_count': validation['data_items_count'],
            'validation_details': validation['validation_details'],
            'full_response': result if validation['is_real_success'] else None
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'return_code': -999,
            'return_msg': f'Exception: {str(e)}'
        }

def run_verification_test(force=False):
    """검증 및 수정된 API 테스트 실행"""

    print("="*80)
    print("검증된 + 수정된 API 엄격한 데이터 검증 테스트")
    print("="*80)

    allowed, current_time = check_time_allowed()
    print(f"\n⏰ 실행 가능 시간: 08:00~20:00 (현재: {current_time.strftime('%H:%M')})")

    if not allowed and not force:
        print("❌ 현재는 테스트 실행 시간이 아닙니다.")
        print("   프로그램은 오전 8시부터 오후 8시까지 실행 가능합니다.")
        print("\n💡 강제 실행하려면: python3 test_verified_and_corrected_apis.py --force")
        return

    if not allowed and force:
        print("⚠️  시간대를 벗어났지만 강제 실행 모드로 진행합니다.")

    print("✅ 테스트 시작\n")

    print("[1] 데이터 로드...")
    with open('corrected_api_calls.json', 'r', encoding='utf-8') as f:
        corrected_data = json.load(f)

    verified_apis = corrected_data['verified_apis']
    corrected_apis = corrected_data['corrected_apis']

    total_verified = corrected_data['metadata']['verified_variants']
    total_corrected = corrected_data['metadata']['corrections_made']

    print(f"  ✅ 검증된 API: {len(verified_apis)}개 ({total_verified}개 variant)")
    print(f"  🔧 수정된 API: {len(corrected_apis)}개 ({total_corrected}개 variant)")
    print(f"  📊 총 테스트: {total_verified + total_corrected}개 variant")

    print("\n[2] Kiwoom API 클라이언트 초기화...")
    try:
        client = KiwoomRESTClient()
        print("  ✅ 초기화 완료")
    except Exception as e:
        print(f"  ❌ 초기화 실패: {e}")
        return

    results = {
        'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'verified_results': [],
        'corrected_results': [],
        'statistics': {}
    }

    stats = {
        'verified': {'tested': 0, 'real_success': 0, 'no_data': 0, 'error': 0},
        'corrected': {'tested': 0, 'real_success': 0, 'no_data': 0, 'error': 0,
                     'improved_from_fail': 0, 'still_fail': 0}
    }

    print("\n[3] 검증된 API 전체 재확인 (347개 variant)...")
    print("-"*80)

    for api_id, api_info in verified_apis.items():
        api_name = api_info['api_name']

        for call in api_info['optimized_calls']:
            variant_idx = call['variant_idx']
            path = call['path']
            body = call['body']

            stats['verified']['tested'] += 1

            print(f"  테스트 중 [{api_id} Var {variant_idx}] {api_name[:30]:30s} ", end='', flush=True)

            test_result = test_api_call(client, api_id, api_name, path, body)

            result_entry = {
                'api_id': api_id,
                'api_name': api_name,
                'variant_idx': variant_idx,
                'path': path,
                'body': body,
                'original_status': 'verified',
                **test_result
            }

            results['verified_results'].append(result_entry)

            if test_result['success']:
                print(f"✅ SUCCESS ({test_result['data_items_count']}개)")
                stats['verified']['real_success'] += 1
            elif test_result.get('return_code') == 0:
                print(f"⚠️  NO_DATA")
                stats['verified']['no_data'] += 1
            else:
                print(f"❌ ERROR: {test_result.get('return_msg', 'Unknown')[:50]}")
                stats['verified']['error'] += 1

    print("\n[4] 수정된 API 테스트...")
    print("-"*80)

    for api_id, api_info in corrected_apis.items():
        api_name = api_info['api_name']
        original_status = api_info['original_status']

        print(f"\n  [{api_id}] {api_name} (원본: {original_status})")

        for variant in api_info['corrected_variants']:
            variant_idx = variant['variant_idx']
            path = variant['path']
            body = variant['body']
            fix_reason = variant.get('fix_reason', '')

            stats['corrected']['tested'] += 1

            print(f"    Var {variant_idx}: {fix_reason[:60]:60s} ", end='', flush=True)

            test_result = test_api_call(client, api_id, api_name, path, body)

            result_entry = {
                'api_id': api_id,
                'api_name': api_name,
                'variant_idx': variant_idx,
                'path': path,
                'body': body,
                'original_status': original_status,
                'fix_reason': fix_reason,
                **test_result
            }

            results['corrected_results'].append(result_entry)

            if test_result['success']:
                print(f"✅ SUCCESS! ({test_result['data_items_count']}개)")
                stats['corrected']['real_success'] += 1
                if original_status == 'total_fail':
                    stats['corrected']['improved_from_fail'] += 1
            elif test_result.get('return_code') == 0:
                print(f"⚠️  NO_DATA")
                stats['corrected']['no_data'] += 1
                stats['corrected']['still_fail'] += 1
            else:
                print(f"❌ ERROR")
                stats['corrected']['error'] += 1
                stats['corrected']['still_fail'] += 1

    print("\n" + "="*80)
    print("📊 테스트 결과 통계")
    print("="*80)

    print(f"\n✅ 검증된 API 재확인 ({stats['verified']['tested']}개 variant)")
    print(f"  - 진짜 성공: {stats['verified']['real_success']}개 ({stats['verified']['real_success']/stats['verified']['tested']*100:.1f}%)")
    print(f"  - 데이터 없음: {stats['verified']['no_data']}개 ({stats['verified']['no_data']/stats['verified']['tested']*100:.1f}%)")
    print(f"  - 오류: {stats['verified']['error']}개 ({stats['verified']['error']/stats['verified']['tested']*100:.1f}%)")

    print(f"\n🔧 수정된 API 테스트 ({stats['corrected']['tested']}개)")
    print(f"  - 진짜 성공: {stats['corrected']['real_success']}개")
    print(f"  - 데이터 없음: {stats['corrected']['no_data']}개")
    print(f"  - 오류: {stats['corrected']['error']}개")
    print(f"\n  🎉 실패→성공 개선: {stats['corrected']['improved_from_fail']}개")
    print(f"  ❌ 여전히 실패: {stats['corrected']['still_fail']}개")

    results['statistics'] = stats

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_file = f'verified_corrected_test_results_{timestamp}.json'

    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "="*80)
    print(f"💾 테스트 결과 저장: {result_file}")
    print("="*80)

    generate_detailed_report(results, stats)

def generate_detailed_report(results, stats):
    """상세 리포트 생성"""

    report_lines = []
    report_lines.append("="*80)
    report_lines.append("검증 및 수정 API 테스트 상세 리포트")
    report_lines.append("="*80)
    report_lines.append(f"\n생성일시: {results['test_time']}\n")

    report_lines.append("🎉 파라미터 수정으로 성공한 API")
    report_lines.append("-"*80)

    improved = [r for r in results['corrected_results']
                if r['success'] and r['original_status'] == 'total_fail']

    if improved:
        for r in improved:
            report_lines.append(f"\n[{r['api_id']}] {r['api_name']}")
            report_lines.append(f"  Variant {r['variant_idx']}")
            report_lines.append(f"  수정: {r['fix_reason']}")
            report_lines.append(f"  결과: ✅ {r['data_items_count']}개 데이터 수신")
            report_lines.append(f"  상세: {r['validation_details']}")
    else:
        report_lines.append("(없음)")

    report_lines.append("\n\n❌ 파라미터 수정 후에도 실패")
    report_lines.append("-"*80)

    still_fail = [r for r in results['corrected_results'] if not r['success']]

    if still_fail:
        for r in still_fail:
            report_lines.append(f"\n[{r['api_id']}] {r['api_name']}")
            report_lines.append(f"  Variant {r['variant_idx']}")
            report_lines.append(f"  수정: {r['fix_reason']}")
            report_lines.append(f"  실패 원인: {r.get('return_msg', 'Unknown')}")
    else:
        report_lines.append("(없음)")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f'verified_corrected_report_{timestamp}.txt'

    report_text = "\n".join(report_lines)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"\n📄 상세 리포트: {report_file}")

if __name__ == "__main__":
    force = '--force' in sys.argv or '-f' in sys.argv
    run_verification_test(force=force)
