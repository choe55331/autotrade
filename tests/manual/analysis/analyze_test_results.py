"""
comprehensive_api_debugger.py 결과 로그 분석 스크립트
"""
import re
import json
from collections import defaultdict, Counter

def parse_log_file(log_file_path):
    """로그 파일 파싱"""
    results = []

    with open(log_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    for line in lines:
        if '[OK] 성공 (데이터 확인)' in line:
            match = re.search(r'\[(\S+)\s+Var\s+(\d+)/(\d+)\]\s+(.+?)\s+\|', line)
            if match:
                results.append({
                    'api_id': match.group(1),
                    'variant': f"{match.group(2)}/{match.group(3)}",
                    'name': match.group(4),
                    'status': 'success'
                })

        elif '[WARNING]️ 성공 (데이터 없음)' in line:
            match = re.search(r'\[(\S+)\s+Var\s+(\d+)/(\d+)\]\s+(.+?)\s+\|', line)
            if match:
                results.append({
                    'api_id': match.group(1),
                    'variant': f"{match.group(2)}/{match.group(3)}",
                    'name': match.group(4),
                    'status': 'no_data'
                })

        elif '[X] 실패' in line:
            match = re.search(r'\[(\S+)\s+Var\s+(\d+)/(\d+)\]\s+(.+?)\s+\|', line)
            if match:
                failure_type = 'api_error'
                if 'API 오류' in line:
                    failure_type = 'api_error'
                elif '경로 오류' in line:
                    failure_type = 'path_error'
                elif '내부 예외' in line:
                    failure_type = 'exception'
                elif '준비 오류' in line:
                    failure_type = 'prepare_error'

                results.append({
                    'api_id': match.group(1),
                    'variant': f"{match.group(2)}/{match.group(3)}",
                    'name': match.group(4),
                    'status': failure_type
                })

    return results

def analyze_results(results):
    """결과 분석"""
    analysis = {
        'total_tests': len(results),
        'unique_apis': len(set(r['api_id'] for r in results)),
        'status_counts': Counter(r['status'] for r in results),
        'api_summary': defaultdict(lambda: {'total': 0, 'success': 0, 'no_data': 0, 'failed': 0}),
        'failed_apis': []
    }

    for result in results:
        api_id = result['api_id']
        status = result['status']

        analysis['api_summary'][api_id]['total'] += 1
        if status == 'success':
            analysis['api_summary'][api_id]['success'] += 1
        elif status == 'no_data':
            analysis['api_summary'][api_id]['no_data'] += 1
        else:
            analysis['api_summary'][api_id]['failed'] += 1
            if result not in analysis['failed_apis']:
                analysis['failed_apis'].append(result)

    return analysis

def generate_report(analysis, output_file='test_results_report.md'):
    """마크다운 리포트 생성"""
    report = []

    report.append("
    report.append(f"생성일시: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    report.append("
    report.append(f"- 총 테스트 수: {analysis['total_tests']}")
    report.append(f"- 테스트된 API 수: {analysis['unique_apis']}")
    report.append(f"\n
    report.append(f"- [OK] 성공 (데이터 확인): {analysis['status_counts']['success']}")
    report.append(f"- [WARNING]️ 성공 (데이터 없음): {analysis['status_counts']['no_data']}")
    report.append(f"- [X] API 오류: {analysis['status_counts']['api_error']}")
    report.append(f"- [X] 경로 오류: {analysis['status_counts']['path_error']}")
    report.append(f"- [X] 내부 예외: {analysis['status_counts']['exception']}")
    report.append(f"- [X] 준비 오류: {analysis['status_counts']['prepare_error']}")

    report.append(f"\n\n
    report.append("| API ID | 총 테스트 | 성공 | 데이터없음 | 실패 | 성공률 |")
    report.append("|--------|----------|------|-----------|------|--------|")

    for api_id in sorted(analysis['api_summary'].keys()):
        stats = analysis['api_summary'][api_id]
        success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
        report.append(
            f"| {api_id} | {stats['total']} | {stats['success']} | {stats['no_data']} | "
            f"{stats['failed']} | {success_rate:.1f}% |"
        )

    if analysis['failed_apis']:
        report.append(f"\n\n
        for fail in analysis['failed_apis'][:50]:
            report.append(f"- `{fail['api_id']}` (Var {fail['variant']}): {fail['name']} - {fail['status']}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

    print(f"\n[OK] 리포트 생성 완료: {output_file}")

    return '\n'.join(report)

def main():
    log_file = 'comprehensive_api_debugger.py 결과 로그.txt'

    print("📂 로그 파일 파싱 중...")
    results = parse_log_file(log_file)
    print(f"   - {len(results)}개 테스트 결과 발견")

    print("\n[CHART] 결과 분석 중...")
    analysis = analyze_results(results)

    print("\n📝 리포트 생성 중...")
    report = generate_report(analysis)

    json_output = {
        'analysis': {
            'total_tests': analysis['total_tests'],
            'unique_apis': analysis['unique_apis'],
            'status_counts': dict(analysis['status_counts']),
        },
        'api_summary': dict(analysis['api_summary']),
        'failed_apis': analysis['failed_apis']
    }

    with open('test_results_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)

    print("[OK] JSON 파일 저장 완료: test_results_analysis.json")

    print("\n" + "="*80)
    print("[CHART] 요약")
    print("="*80)
    print(f"총 테스트: {analysis['total_tests']}")
    print(f"API 수: {analysis['unique_apis']}")
    print(f"성공: {analysis['status_counts']['success']}")
    print(f"데이터없음: {analysis['status_counts']['no_data']}")
    print(f"실패: {sum(analysis['status_counts'][k] for k in analysis['status_counts'] if k not in ['success', 'no_data'])}")
    print("="*80)

if __name__ == '__main__':
    main()
