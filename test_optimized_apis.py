#!/usr/bin/env python3
"""
test_optimized_apis.py
최적화된 API + 실패 API 전체 테스트 및 실패 원인 분석
"""
import json
import sys
from pathlib import Path
from datetime import datetime, time
from collections import defaultdict

# core 모듈에서 KiwoomRESTClient import
try:
    from core.rest_client import KiwoomRESTClient
except ImportError:
    print("❌ core 모듈을 찾을 수 없습니다. core/rest_client.py 파일이 있는지 확인하세요.")
    sys.exit(1)

def check_time_allowed():
    """실행 가능 시간 확인 (8:00-20:00)"""
    now = datetime.now().time()
    start_time = time(8, 0)   # 08:00
    end_time = time(20, 0)     # 20:00
    return start_time <= now <= end_time, now

def load_test_data():
    """테스트 데이터 로드"""

    # 최적화된 API (성공)
    with open('optimized_api_calls.json', 'r', encoding='utf-8') as f:
        optimized = json.load(f)

    # 전체 API (실패한 것 포함)
    with open('all_394_api_calls.json', 'r', encoding='utf-8') as f:
        all_apis = json.load(f)

    return optimized, all_apis

def categorize_apis(optimized, all_apis):
    """API 분류: 성공 vs 실패"""

    success_apis = set(optimized['optimized_apis'].keys())
    all_api_ids = set(all_apis.keys())
    failed_apis = all_api_ids - success_apis

    # 실패 API 정보 추출
    failed_api_info = {}
    for api_id in failed_apis:
        failed_api_info[api_id] = all_apis[api_id]

    return success_apis, failed_api_info

def test_api_call(client, api_id, api_name, path, body):
    """단일 API 호출 테스트"""

    try:
        result = client.request(api_id, body, path)

        if result is None:
            return {
                'status': 'api_error',
                'return_code': -1,
                'return_msg': 'API 응답 없음 (None)',
                'has_data': False,
                'data_items': 0,
                'data_keys': [],
                'full_response': {}
            }

        # 결과 분석
        return_code = result.get('return_code', -1)
        return_msg = result.get('return_msg', '메시지 없음')

        # 데이터 확인 (return_code, return_msg 제외한 실제 데이터)
        data_keys = [k for k in result.keys() if k not in ['return_code', 'return_msg']]
        has_data = len(data_keys) > 0

        # 상세 데이터 분석
        data_items = 0
        if has_data:
            for key in data_keys:
                value = result[key]
                if isinstance(value, list):
                    data_items += len(value)
                elif value:  # None이나 빈 값이 아니면
                    data_items += 1

        return {
            'status': 'success' if (return_code == 0 and has_data and data_items > 0) else
                     'no_data' if return_code == 0 else 'api_error',
            'return_code': return_code,
            'return_msg': return_msg,
            'has_data': has_data,
            'data_items': data_items,
            'data_keys': data_keys,
            'full_response': result
        }

    except Exception as e:
        return {
            'status': 'exception',
            'error': str(e),
            'error_type': type(e).__name__
        }

def analyze_failure_patterns(failed_results):
    """실패 패턴 분석"""

    patterns = {
        'no_data': defaultdict(list),      # return_code=0 이지만 데이터 없음
        'api_error': defaultdict(list),     # API 오류
        'exception': defaultdict(list),     # 예외 발생
        'by_path': defaultdict(list),       # Path별 분류
        'by_msg': defaultdict(list)         # 오류 메시지별 분류
    }

    for result in failed_results:
        api_id = result['api_id']
        status = result['status']
        path = result['path']

        # 상태별 분류
        if status in patterns:
            patterns[status][api_id].append(result)

        # Path별 분류
        patterns['by_path'][path].append(result)

        # 메시지별 분류 (api_error인 경우)
        if status == 'api_error':
            msg = result.get('return_msg', 'Unknown')
            patterns['by_msg'][msg].append(result)
        elif status == 'no_data':
            patterns['by_msg']['데이터 없음 (return_code=0)'].append(result)

    return patterns

def run_comprehensive_test(force=False):
    """종합 테스트 실행"""

    print("="*80)
    print("최적화된 API + 실패 API 종합 테스트")
    print("="*80)

    # 시간 체크
    allowed, current_time = check_time_allowed()
    print(f"\n⏰ 실행 가능 시간: 08:00~20:00 (현재: {current_time.strftime('%H:%M')})")

    if not allowed and not force:
        print("❌ 현재는 테스트 실행 시간이 아닙니다.")
        print("   프로그램은 오전 8시부터 오후 8시까지 실행 가능합니다.")
        print("\n💡 강제 실행하려면: python3 test_optimized_apis.py --force")
        return

    if not allowed and force:
        print("⚠️  시간대를 벗어났지만 강제 실행 모드로 진행합니다.")

    print("✅ 테스트 시작\n")

    # 데이터 로드
    print("[1] 데이터 로드 중...")
    optimized, all_apis = load_test_data()
    success_apis, failed_api_info = categorize_apis(optimized, all_apis)

    total_success_apis = len(success_apis)
    total_failed_apis = len(failed_api_info)

    print(f"  ✅ 최적화된 API: {total_success_apis}개")
    print(f"  ❌ 실패 API: {total_failed_apis}개")
    print(f"  📊 총 테스트: {total_success_apis + total_failed_apis}개")

    # KiwoomRESTClient 초기화
    print("\n[2] Kiwoom API 클라이언트 초기화...")
    try:
        client = KiwoomRESTClient()
        print("  ✅ 초기화 완료")
    except Exception as e:
        print(f"  ❌ 초기화 실패: {e}")
        return

    # 테스트 결과 저장
    results = {
        'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'success_api_results': [],
        'failed_api_results': [],
        'statistics': {}
    }

    # ================================================================================
    # [3] 성공 API 재검증
    # ================================================================================
    print("\n[3] 최적화된 API 재검증 중...")
    print("-"*80)

    success_stats = {
        'still_success': 0,
        'changed_to_no_data': 0,
        'changed_to_error': 0,
        'total_variants': 0
    }

    for api_id in success_apis:
        api_info = optimized['optimized_apis'][api_id]
        api_name = api_info['api_name']

        for call in api_info['optimized_calls']:
            variant_idx = call['variant_idx']
            path = call['path']
            body = call['body']

            success_stats['total_variants'] += 1

            print(f"  테스트 중 [{api_id} Var {variant_idx}] {api_name[:30]:30s} ", end='', flush=True)

            test_result = test_api_call(client, api_id, api_name, path, body)

            result_entry = {
                'api_id': api_id,
                'api_name': api_name,
                'variant_idx': variant_idx,
                'path': path,
                'body': body,
                'original_status': 'success',
                **test_result
            }

            results['success_api_results'].append(result_entry)

            # 상태 출력
            if test_result['status'] == 'success':
                print(f"✅ SUCCESS ({test_result['data_items']}개)")
                success_stats['still_success'] += 1
            elif test_result['status'] == 'no_data':
                print(f"⚠️  NO_DATA")
                success_stats['changed_to_no_data'] += 1
            else:
                print(f"❌ ERROR: {test_result.get('return_msg', 'Unknown')}")
                success_stats['changed_to_error'] += 1

    # ================================================================================
    # [4] 실패 API 재시도 및 상세 분석
    # ================================================================================
    print("\n[4] 실패 API 재시도 및 원인 분석...")
    print("-"*80)

    failed_stats = {
        'still_failed': 0,
        'now_success': 0,
        'now_no_data': 0,
        'total_variants': 0
    }

    for api_id, api_info in failed_api_info.items():
        api_name = api_info['api_name']

        print(f"\n  [{api_id}] {api_name}")

        for call in api_info['all_calls']:
            variant_idx = call['variant_idx']
            path = call['path']
            body = call['body']
            original_status = call['status']

            failed_stats['total_variants'] += 1

            print(f"    Var {variant_idx} (원본: {original_status:10s}): ", end='', flush=True)

            test_result = test_api_call(client, api_id, api_name, path, body)

            result_entry = {
                'api_id': api_id,
                'api_name': api_name,
                'variant_idx': variant_idx,
                'path': path,
                'body': body,
                'original_status': original_status,
                **test_result
            }

            results['failed_api_results'].append(result_entry)

            # 상태 출력 및 통계
            if test_result['status'] == 'success':
                print(f"✅ SUCCESS! ({test_result['data_items']}개) - 상태 개선!")
                failed_stats['now_success'] += 1
            elif test_result['status'] == 'no_data':
                print(f"⚠️  NO_DATA - {test_result.get('return_msg', '')}")
                failed_stats['now_no_data'] += 1
            else:
                print(f"❌ {test_result.get('return_msg', test_result.get('error', 'Unknown'))}")
                failed_stats['still_failed'] += 1

            # 파라미터와 응답 상세 출력 (디버깅용)
            if test_result['status'] != 'success':
                print(f"       Path: {path}")
                print(f"       Body: {json.dumps(body, ensure_ascii=False)}")
                if test_result['status'] == 'no_data':
                    print(f"       Return Code: {test_result['return_code']}")
                    print(f"       Data Keys: {test_result.get('data_keys', [])}")

    # ================================================================================
    # [5] 통계 및 분석
    # ================================================================================
    print("\n" + "="*80)
    print("📊 테스트 결과 통계")
    print("="*80)

    print(f"\n✅ 최적화된 API 재검증 ({success_stats['total_variants']}개 variant)")
    print(f"  - 여전히 성공: {success_stats['still_success']}개 ({success_stats['still_success']/success_stats['total_variants']*100:.1f}%)")
    print(f"  - no_data로 변경: {success_stats['changed_to_no_data']}개")
    print(f"  - 오류로 변경: {success_stats['changed_to_error']}개")

    print(f"\n❌ 실패 API 재시도 ({failed_stats['total_variants']}개 variant)")
    print(f"  - 성공으로 개선: {failed_stats['now_success']}개")
    print(f"  - no_data: {failed_stats['now_no_data']}개")
    print(f"  - 여전히 실패: {failed_stats['still_failed']}개")

    results['statistics'] = {
        'success_apis': success_stats,
        'failed_apis': failed_stats
    }

    # 실패 패턴 분석
    patterns = analyze_failure_patterns(results['failed_api_results'])

    print("\n" + "="*80)
    print("🔍 실패 원인 분석")
    print("="*80)

    # Path별 실패
    print("\n📂 Path별 실패 분포:")
    for path, failures in sorted(patterns['by_path'].items()):
        failed_count = len([f for f in failures if f['status'] != 'success'])
        if failed_count > 0:
            print(f"  {path:15s}: {failed_count}개 실패")

    # 메시지별 실패
    print("\n💬 오류 메시지별 분포:")
    for msg, failures in sorted(patterns['by_msg'].items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {msg:50s}: {len(failures)}개")

    # API별 실패 원인 추정
    print("\n🔬 API별 실패 원인 추정:")

    failure_analysis = analyze_api_failures(results['failed_api_results'])
    for api_id, analysis in sorted(failure_analysis.items()):
        if analysis['all_failed']:
            print(f"\n  [{api_id}] {analysis['api_name']}")
            print(f"    Path: {analysis['path']}")
            print(f"    추정 원인: {analysis['suspected_reason']}")
            print(f"    상세: {analysis['details']}")

    # 결과 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_file = f'comprehensive_test_results_{timestamp}.json'

    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "="*80)
    print(f"💾 테스트 결과 저장: {result_file}")
    print("="*80)

    # 실패 분석 보고서 생성
    generate_failure_report(results, patterns, failure_analysis)

def analyze_api_failures(failed_results):
    """API별 실패 원인 분석"""

    api_analysis = {}

    # API별로 그룹화
    by_api = defaultdict(list)
    for result in failed_results:
        by_api[result['api_id']].append(result)

    for api_id, results in by_api.items():
        if not results:
            continue

        first = results[0]
        api_name = first['api_name']
        path = first['path']

        # 모든 variant가 실패했는지 확인
        all_failed = all(r['status'] != 'success' for r in results)

        # 실패 원인 추정
        suspected_reason = "알 수 없음"
        details = ""

        # Path 기반 분석
        if path == 'gold':
            suspected_reason = "금현물 계좌 미보유"
            details = "금현물 거래 계좌가 없으면 데이터를 조회할 수 없습니다."

        elif api_id in ['ka10075', 'ka10076', 'ka10088']:
            suspected_reason = "미체결/체결 주문 없음"
            details = "현재 미체결 또는 체결된 주문이 없어서 데이터가 없습니다."

        elif api_id == 'kt00009':
            suspected_reason = "당일 주문 내역 없음"
            details = "당일 주문/체결 내역이 없으면 조회되지 않습니다."

        elif api_id == 'kt00012':
            suspected_reason = "신용거래 미사용"
            details = "신용거래를 하지 않으면 신용보증금율 데이터가 없습니다."

        elif api_id == 'ka10010':
            suspected_reason = "파라미터 오류 가능성"
            details = "업종코드나 다른 필수 파라미터가 잘못되었을 수 있습니다."

        elif 'no_data' in [r['status'] for r in results]:
            suspected_reason = "계좌/거래 데이터 없음"
            details = "해당 조건에 맞는 데이터가 계좌에 없습니다."

        # return_msg 분석
        msgs = [r.get('return_msg', '') for r in results if r.get('return_msg')]
        if msgs:
            common_msg = max(set(msgs), key=msgs.count)
            if '권한' in common_msg or '허용' in common_msg:
                suspected_reason = "API 권한 없음"
                details = f"해당 API 사용 권한이 없을 수 있습니다: {common_msg}"
            elif '조회기간' in common_msg or '날짜' in common_msg:
                suspected_reason = "조회 기간 오류"
                details = f"조회 기간 설정에 문제가 있습니다: {common_msg}"

        api_analysis[api_id] = {
            'api_name': api_name,
            'path': path,
            'total_variants': len(results),
            'all_failed': all_failed,
            'suspected_reason': suspected_reason,
            'details': details,
            'sample_response': results[0].get('full_response', {})
        }

    return api_analysis

def generate_failure_report(results, patterns, failure_analysis):
    """실패 분석 보고서 생성"""

    report_lines = []
    report_lines.append("="*80)
    report_lines.append("실패 API 상세 분석 보고서")
    report_lines.append("="*80)
    report_lines.append(f"\n생성일시: {results['test_time']}\n")

    failed_results = results['failed_api_results']
    still_failed = [r for r in failed_results if r['status'] != 'success']

    report_lines.append(f"총 실패 API 테스트: {len(failed_results)}개 variant")
    report_lines.append(f"여전히 실패: {len(still_failed)}개")

    report_lines.append("\n" + "="*80)
    report_lines.append("API별 실패 원인 및 해결 방안")
    report_lines.append("="*80)

    for api_id, analysis in sorted(failure_analysis.items()):
        if analysis['all_failed']:
            report_lines.append(f"\n[{api_id}] {analysis['api_name']}")
            report_lines.append(f"  Path: {analysis['path']}")
            report_lines.append(f"  Variants: {analysis['total_variants']}개")
            report_lines.append(f"  추정 원인: {analysis['suspected_reason']}")
            report_lines.append(f"  상세 설명: {analysis['details']}")

            # 해결 방안
            if 'gold' in analysis['path']:
                report_lines.append("  해결 방안: 금현물 계좌 개설 필요")
            elif '미체결' in analysis['api_name'] or '체결' in analysis['api_name']:
                report_lines.append("  해결 방안: 실제 주문을 생성한 후 테스트")
            elif '신용' in analysis['api_name']:
                report_lines.append("  해결 방안: 신용거래 계좌 개설 또는 신용거래 실행 필요")
            else:
                report_lines.append("  해결 방안: 파라미터 재검토 또는 계좌 데이터 확인")

    report_lines.append("\n" + "="*80)
    report_lines.append("실패 패턴 요약")
    report_lines.append("="*80)

    report_lines.append("\n📂 Path별 실패:")
    for path, failures in sorted(patterns['by_path'].items()):
        failed_count = len([f for f in failures if f['status'] != 'success'])
        if failed_count > 0:
            report_lines.append(f"  {path:15s}: {failed_count}개")

    report_lines.append("\n💬 오류 메시지별:")
    for msg, failures in sorted(patterns['by_msg'].items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        report_lines.append(f"  {msg:50s}: {len(failures)}개")

    report_lines.append("\n" + "="*80)
    report_lines.append("권장 사항")
    report_lines.append("="*80)
    report_lines.append("1. 금현물 API (kt50xxx): 금현물 계좌 개설 후 재시도")
    report_lines.append("2. 미체결/체결 API: 실제 주문 생성 후 테스트")
    report_lines.append("3. 신용 관련 API: 신용거래 계좌 활성화 필요")
    report_lines.append("4. 데이터 없음 API: 해당 조건의 실제 데이터 생성 후 재시도")
    report_lines.append("5. 파라미터 오류 가능 API: 키움 문서 재확인 및 파라미터 수정")

    report_text = "\n".join(report_lines)

    # 파일 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f'failure_analysis_report_{timestamp}.txt'

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"\n📄 실패 분석 보고서: {report_file}")

    # 화면 출력
    print("\n" + report_text)

if __name__ == "__main__":
    force = '--force' in sys.argv or '-f' in sys.argv
    run_comprehensive_test(force=force)
