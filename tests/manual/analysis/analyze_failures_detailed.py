analyze_failures_detailed.py
실패 API 집중 분석 - 로그 데이터와 문서 기반 원인 파악
import json
from pathlib import Path
from collections import defaultdict

def load_all_data():
    """모든 분석 데이터 로드"""

    with open('all_394_api_calls.json', 'r', encoding='utf-8') as f:
        all_apis = json.load(f)

    with open('optimized_api_calls.json', 'r', encoding='utf-8') as f:
        optimized = json.load(f)

    return all_apis, optimized

def analyze_failure_apis():
    """실패 API 상세 분석"""

    print("="*80)
    print("실패 API 집중 분석 보고서")
    print("="*80)

    all_apis, optimized = load_all_data()

    success_api_ids = set(optimized['optimized_apis'].keys())

    failure_analysis = {
        'total_fail': {},
        'partial_fail': {},
        'by_path': defaultdict(list),
        'by_pattern': defaultdict(list)
    }

    for api_id, info in all_apis.items():
        api_name = info['api_name']
        all_calls = info['all_calls']

        success_count = sum(1 for c in all_calls if c['status'] == 'success')
        no_data_count = sum(1 for c in all_calls if c['status'] == 'no_data')
        error_count = sum(1 for c in all_calls if c['status'] == 'api_error')
        total_count = len(all_calls)

        paths = list(set(c['path'] for c in all_calls))

        if success_count == 0:
            failure_analysis['total_fail'][api_id] = {
                'name': api_name,
                'paths': paths,
                'total_variants': total_count,
                'no_data': no_data_count,
                'api_error': error_count,
                'variants': all_calls
            }

            for path in paths:
                failure_analysis['by_path'][path].append(api_id)

        elif success_count < total_count:
            failed_variants = [c for c in all_calls if c['status'] != 'success']

            failure_analysis['partial_fail'][api_id] = {
                'name': api_name,
                'paths': paths,
                'total_variants': total_count,
                'success': success_count,
                'failed': total_count - success_count,
                'failed_variants': failed_variants
            }

    return failure_analysis

def deep_analyze_total_failures(total_fail):
    """전체 실패 API 심층 분석"""

    analyses = {}

    for api_id, info in total_fail.items():
        api_name = info['name']
        paths = info['paths']
        no_data = info['no_data']
        api_error = info['api_error']
        variants = info['variants']

        suspected_causes = []
        recommendations = []
        priority = "중"

        if 'gold' in paths or api_id.startswith('kt50'):
            suspected_causes.append("🏅 금현물 계좌 미보유")
            recommendations.append("금현물 거래 계좌 개설 필요")
            priority = "낮음"

        if '미체결' in api_name or '체결요청' in api_name:
            suspected_causes.append("📋 미체결/체결 주문 내역 없음")
            recommendations.append("실제 주문을 생성한 후 재테스트")
            priority = "중"

        if '주문체결현황' in api_name:
            suspected_causes.append("📊 당일 주문 내역 없음")
            recommendations.append("당일 주문이 있을 때 테스트")
            priority = "중"

        if '신용' in api_name:
            suspected_causes.append("💳 신용거래 미사용")
            recommendations.append("신용거래 계좌 활성화 또는 신용거래 실행 필요")
            priority = "낮음"

        if '업종프로그램' in api_name:
            suspected_causes.append("🔧 파라미터 오류 가능성")
            recommendations.append("업종코드 확인 및 문서 재검토")
            priority = "높음"

        if no_data == info['total_variants']:
            suspected_causes.append("📭 조회 조건에 맞는 데이터 없음 (return_code=0)")
            recommendations.append("다른 조건으로 재시도 또는 실제 데이터 생성 후 테스트")

        if api_error == info['total_variants']:
            suspected_causes.append("❌ API 호출 자체 오류 (return_code≠0)")
            recommendations.append("파라미터 검증, 문서 재확인, 또는 API 권한 확인")
            priority = "높음"

        if not suspected_causes:
            suspected_causes.append("❓ 원인 불명 - 추가 조사 필요")
            recommendations.append("키움 고객센터 문의 또는 상세 로그 확인")
            priority = "높음"

        analyses[api_id] = {
            'name': api_name,
            'paths': paths,
            'total_variants': info['total_variants'],
            'no_data_count': no_data,
            'api_error_count': api_error,
            'suspected_causes': suspected_causes,
            'recommendations': recommendations,
            'priority': priority,
            'variants_sample': variants[:2]
        }

    return analyses

def deep_analyze_partial_failures(partial_fail):
    """부분 실패 API 심층 분석"""

    analyses = {}

    for api_id, info in partial_fail.items():
        api_name = info['name']
        success = info['success']
        failed = info['failed']
        failed_variants = info['failed_variants']

        insights = []

        failed_params = [v['body'] for v in failed_variants]

        date_params = ['strt_dt', 'end_dt', 'ord_dt', 'base_dt']
        has_date_params = any(
            any(param in params for param in date_params)
            for params in failed_params
        )

        if has_date_params:
            insights.append("📅 실패한 variant들이 날짜 파라미터 포함")
            insights.append("   → 조회 기간에 데이터가 없거나 과거 날짜 조회 제한 가능성")

        if any('stk_cd' in params for params in failed_params):
            stock_codes = [params.get('stk_cd') for params in failed_params if 'stk_cd' in params]
            if stock_codes:
                insights.append(f"🏢 실패한 종목코드: {', '.join(set(stock_codes))}")
                insights.append("   → 해당 종목에 데이터가 없거나 종목코드 오류 가능성")

        success_variant_count = success
        if failed > success_variant_count:
            insights.append(f"⚖️  성공({success}) < 실패({failed}) - 대부분 variant 실패")
            insights.append("   → 특정 조건만 데이터 존재, 파라미터 재검토 필요")
        else:
            insights.append(f"⚖️  성공({success}) > 실패({failed}) - 일부 variant만 실패")
            insights.append("   → 실패한 조건의 데이터가 없거나 파라미터 오류")

        analyses[api_id] = {
            'name': api_name,
            'success_count': success,
            'failed_count': failed,
            'insights': insights,
            'failed_variants_sample': failed_variants[:2]
        }

    return analyses

def generate_detailed_report():
    """상세 분석 보고서 생성"""

    failure_analysis = analyze_failure_apis()
    total_fail = failure_analysis['total_fail']
    partial_fail = failure_analysis['partial_fail']

    total_analyses = deep_analyze_total_failures(total_fail)
    partial_analyses = deep_analyze_partial_failures(partial_fail)

    report = []
    report.append("="*80)
    report.append("실패 API 집중 분석 보고서")
    report.append("="*80)
    report.append("\n📊 분석 개요")
    report.append("-"*80)
    report.append(f"전체 실패 API: {len(total_fail)}개 (모든 variant 실패)")
    report.append(f"부분 실패 API: {len(partial_fail)}개 (일부 variant 실패)")

    report.append("\n" + "="*80)
    report.append("1️⃣ 전체 실패 API 상세 분석 (12개)")
    report.append("="*80)

    priority_order = {"높음": 1, "중": 2, "낮음": 3}
    sorted_analyses = sorted(
        total_analyses.items(),
        key=lambda x: (priority_order[x[1]['priority']], x[0])
    )

    for api_id, analysis in sorted_analyses:
        report.append(f"\n┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        report.append(f"┃ [{api_id}] {analysis['name']}")
        report.append(f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        report.append(f"  📍 Path: {', '.join(analysis['paths'])}")
        report.append(f"  📊 Variants: {analysis['total_variants']}개 (no_data: {analysis['no_data_count']}, api_error: {analysis['api_error_count']})")
        report.append(f"  🎯 우선순위: {analysis['priority']}")

        report.append(f"\n  🔍 추정 원인:")
        for cause in analysis['suspected_causes']:
            report.append(f"     {cause}")

        report.append(f"\n  💡 해결 방안:")
        for rec in analysis['recommendations']:
            report.append(f"     {rec}")

        if analysis['variants_sample']:
            report.append(f"\n  📋 샘플 Variant (1개):")
            sample = analysis['variants_sample'][0]
            report.append(f"     Variant {sample['variant_idx']}: status={sample['status']}")
            report.append(f"     Parameters: {json.dumps(sample['body'], ensure_ascii=False)}")

    report.append("\n" + "="*80)
    report.append("2️⃣ 부분 실패 API 상세 분석 (11개)")
    report.append("="*80)

    for api_id, analysis in sorted(partial_analyses.items()):
        report.append(f"\n┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        report.append(f"┃ [{api_id}] {analysis['name']}")
        report.append(f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        report.append(f"  ✅ 성공: {analysis['success_count']}개 variant")
        report.append(f"  ❌ 실패: {analysis['failed_count']}개 variant")

        report.append(f"\n  🔍 패턴 분석:")
        for insight in analysis['insights']:
            report.append(f"     {insight}")

        if analysis['failed_variants_sample']:
            report.append(f"\n  📋 실패한 Variant 샘플:")
            for variant in analysis['failed_variants_sample']:
                report.append(f"     Variant {variant['variant_idx']}: status={variant['status']}")
                report.append(f"     Parameters: {json.dumps(variant['body'], ensure_ascii=False)}")

    report.append("\n" + "="*80)
    report.append("3️⃣ Path별 실패 분포")
    report.append("="*80)

    path_failures = failure_analysis['by_path']
    for path, api_ids in sorted(path_failures.items(), key=lambda x: len(x[1]), reverse=True):
        report.append(f"\n  📂 {path:15s}: {len(api_ids)}개 API 실패")
        for api_id in sorted(api_ids):
            api_name = total_fail[api_id]['name']
            report.append(f"     - [{api_id}] {api_name}")

    report.append("\n" + "="*80)
    report.append("4️⃣ 우선순위별 처리 가이드")
    report.append("="*80)

    high_priority = [api_id for api_id, a in total_analyses.items() if a['priority'] == "높음"]
    medium_priority = [api_id for api_id, a in total_analyses.items() if a['priority'] == "중"]
    low_priority = [api_id for api_id, a in total_analyses.items() if a['priority'] == "낮음"]

    report.append(f"\n  🔴 높음 ({len(high_priority)}개) - 즉시 처리 필요")
    for api_id in high_priority:
        report.append(f"     [{api_id}] {total_analyses[api_id]['name']}")
        report.append(f"     → {total_analyses[api_id]['recommendations'][0]}")

    report.append(f"\n  🟡 중 ({len(medium_priority)}개) - 조건 충족 시 재테스트")
    for api_id in medium_priority:
        report.append(f"     [{api_id}] {total_analyses[api_id]['name']}")

    report.append(f"\n  🟢 낮음 ({len(low_priority)}개) - 필요 시 처리")
    for api_id in low_priority:
        report.append(f"     [{api_id}] {total_analyses[api_id]['name']}")

    report.append("\n" + "="*80)
    report.append("5️⃣ 종합 권장 사항")
    report.append("="*80)

    report.append("\n  ✅ 즉시 실행 가능:")
    report.append("     1. production_api_config.json의 검증된 347개 호출 사용")
    report.append("     2. 부분 실패 API는 성공한 variant만 사용")
    report.append("     3. 8:00-20:00 시간대에만 API 호출")

    report.append("\n  🔧 추가 조치 필요:")
    report.append("     1. 업종프로그램요청 (ka10010): 파라미터 재검토 필요 [우선순위: 높음]")
    report.append("     2. 미체결/체결 API: 실제 주문 생성 후 재테스트 [우선순위: 중]")
    report.append("     3. 금현물 API: 금현물 계좌 개설 [우선순위: 낮음]")

    report.append("\n  📝 개발 팁:")
    report.append("     1. 에러 로그에 return_code와 return_msg 항상 기록")
    report.append("     2. no_data (return_code=0)와 api_error 구분하여 처리")
    report.append("     3. 부분 실패 API는 성공 패턴을 기반으로 파라미터 최적화")

    report.append("\n  ⏰ 테스트 가이드:")
    report.append("     1. 전체 테스트: 장 시작 전 (8:00-9:00) 또는 장 마감 후 (15:30-20:00)")
    report.append("     2. 주문 관련 API: 실제 주문 후 즉시 테스트")
    report.append("     3. 일별 데이터 API: 전일 데이터가 있는 시점 테스트")

    report.append("\n" + "="*80)
    report.append("보고서 끝")
    report.append("="*80)

    return "\n".join(report), {
        'total_failures': total_analyses,
        'partial_failures': partial_analyses,
        'path_distribution': dict(path_failures)
    }

def main():
    """메인 실행"""

    report_text, analysis_data = generate_detailed_report()

    print(report_text)

    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    report_file = f'failure_detailed_analysis_{timestamp}.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    json_file = f'failure_detailed_analysis_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, ensure_ascii=False, indent=2)

    print(f"\n📄 보고서 저장: {report_file}")
    print(f"📄 JSON 데이터: {json_file}")

if __name__ == "__main__":
    main()
