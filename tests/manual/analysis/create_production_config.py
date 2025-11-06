"""
create_production_config.py
프로덕션 환경용 최적화된 API 설정 파일 생성
"""
import json
from pathlib import Path
from datetime import datetime

def create_production_config():
    """프로덕션용 API 설정 생성"""

    with open('optimized_api_calls.json', 'r', encoding='utf-8') as f:
        optimized = json.load(f)

    optimized_apis = optimized['optimized_apis']
    stats = optimized['metadata']['stats']

    production_config = {
        'version': '1.0',
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'description': '검증된 Kiwoom REST API 호출 목록 - 프로덕션 환경용',
        'total_apis': len(optimized_apis),
        'total_variants': stats['total_success_variants'] + stats['partial_success_variants'],
        'verification_status': 'All API calls verified with actual data responses',

        'apis': {}
    }

    categories = {
        'account': [],
        'market': [],
        'order': [],
        'stock_info': [],
        'ranking': [],
        'theme': [],
        'elw': [],
        'etf': [],
        'gold': [],
        'other': []
    }

    path_to_category = {
        'acnt': 'account',
        'market': 'market',
        'chart': 'market',
        'order': 'order',
        'stkinfo': 'stock_info',
        'rkinfo': 'ranking',
        'thme': 'theme',
        'elw': 'elw',
        'etf': 'etf',
        'gold': 'gold'
    }

    for api_id, info in optimized_apis.items():
        api_config = {
            'id': api_id,
            'name': info['api_name'],
            'type': info['optimization_type'],
            'variants': []
        }

        for call in info['optimized_calls']:
            variant = {
                'index': call['variant_idx'],
                'path': call['path'],
                'parameters': call['body'],
                'verified': True,
                'status': 'success'
            }
            api_config['variants'].append(variant)

        first_path = info['optimized_calls'][0]['path']
        category = path_to_category.get(first_path, 'other')
        categories[category].append(api_config)

        production_config['apis'][api_id] = api_config

    production_config['categories'] = {}
    for cat_name, apis in categories.items():
        if apis:
            production_config['categories'][cat_name] = {
                'count': len(apis),
                'api_ids': [api['id'] for api in apis]
            }

    config_file = 'production_api_config.json'
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(production_config, f, ensure_ascii=False, indent=2)

    print("="*80)
    print("📦 프로덕션 API 설정 생성")
    print("="*80)
    print(f"\n총 {len(optimized_apis)}개 API, {production_config['total_variants']}개 variant\n")

    for cat_name, cat_info in production_config['categories'].items():
        count = cat_info['count']
        print(f"  {cat_name:15s}: {count:3d}개 API")

    print("\n" + "="*80)
    print(f"💾 저장: {config_file}")
    print("="*80)

    create_usage_examples(production_config)

    return production_config

def create_usage_examples(config):
    """사용 예제 생성"""

    examples = {
        'description': 'Kiwoom REST API 사용 예제',
        'base_url': 'https://api.kiwoom.com',
        'authentication': {
            'method': 'Bearer Token',
            'header': 'authorization: Bearer {token}'
        },
        'examples': []
    }

    example_categories = ['account', 'market', 'stock_info']

    for category in example_categories:
        cat_apis = config['categories'].get(category, {}).get('api_ids', [])
        if cat_apis:
            api_id = cat_apis[0]
            api_info = config['apis'][api_id]

            if api_info['variants']:
                variant = api_info['variants'][0]

                example = {
                    'category': category,
                    'api_id': api_id,
                    'api_name': api_info['name'],
                    'request': {
                        'method': 'POST',
                        'url': f"https://api.kiwoom.com/api/dostk/{variant['path']}",
                        'headers': {
                            'Content-Type': 'application/json; charset=utf-8',
                            'authorization': 'Bearer {your_token}',
                            'api-id': api_id
                        },
                        'body': variant['parameters']
                    },
                    'description': f"Variant {variant['index']} - 검증된 호출"
                }

                examples['examples'].append(example)

    example_file = 'api_usage_examples.json'
    with open(example_file, 'w', encoding='utf-8') as f:
        json.dump(examples, f, ensure_ascii=False, indent=2)

    print(f"📖 사용 예제: {example_file}")

def create_summary_report():
    """최종 요약 보고서 생성"""

    with open('optimized_api_calls.json', 'r', encoding='utf-8') as f:
        optimized = json.load(f)

    stats = optimized['metadata']['stats']
    apis = optimized['optimized_apis']
    new_apis = optimized['new_apis_from_docs']

    report = []
    report.append("="*80)
    report.append("Kiwoom REST API 최적화 최종 보고서")
    report.append("="*80)
    report.append(f"\n생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    report.append("1️⃣ 테스트 개요")
    report.append("-"*80)
    report.append(f"  • 원본 로그: comprehensive_api_debugger.py 결과 (394개 API 호출)")
    report.append(f"  • 테스트 결과:")
    report.append(f"    - 데이터 수신 성공: 347개 호출")
    report.append(f"    - 데이터 없음/실패: 47개 호출")

    report.append("\n2️⃣ 최적화 결과")
    report.append("-"*80)
    report.append(f"  ✅ 완전 성공 API: {stats['total_success_apis']}개")
    report.append(f"     - 모든 variant가 데이터 수신 성공")
    report.append(f"     - 총 {stats['total_success_variants']}개 variant")

    report.append(f"\n  ⚠️  부분 성공 API: {stats['partial_apis']}개")
    report.append(f"     - 일부 variant만 성공, 실패한 것은 제거")
    report.append(f"     - 유지: {stats['partial_success_variants']}개 variant")
    report.append(f"     - 제거: {stats['partial_removed_variants']}개 variant (no_data/실패)")

    report.append(f"\n  ❌ 전체 실패 API: {stats['total_fail_apis']}개")
    report.append(f"     - 모든 variant 실패 → 목록에서 제외")

    report.append(f"\n  🆕 신규 발견 API: {stats['new_apis']}개")
    report.append(f"     - kiwoom_docs 문서에서 발견")
    report.append(f"     - 아직 테스트 안 함 (향후 테스트 필요)")

    report.append("\n3️⃣ 최종 결과")
    report.append("-"*80)
    report.append(f"  📦 최종 API 수: {len(apis)}개")
    report.append(f"  📊 총 검증된 호출: {stats['total_success_variants'] + stats['partial_success_variants']}개")
    report.append(f"  ✅ 모두 실제 데이터 수신 확인됨")

    report.append("\n4️⃣ 부분 성공 API 상세 (실패 variant 제거)")
    report.append("-"*80)

    partial_apis = [
        (api_id, info) for api_id, info in apis.items()
        if info['optimization_type'] == 'partial_success'
    ]

    for api_id, info in sorted(partial_apis):
        kept_vars = [c['variant_idx'] for c in info['optimized_calls']]
        removed = info['removed_variants']

        report.append(f"\n  [{api_id}] {info['api_name']}")
        report.append(f"    ✅ 유지된 variant: {', '.join(f'Var {v}' for v in kept_vars)}")
        report.append(f"    ❌ 제거된 variant: {removed}개 (no_data 또는 API 오류)")

    report.append("\n5️⃣ 생성된 파일")
    report.append("-"*80)
    report.append("  • optimized_api_calls.json          - 전체 최적화 데이터")
    report.append("  • optimized_api_calls_simple.json   - 간소화 버전")
    report.append("  • production_api_config.json        - 프로덕션 설정")
    report.append("  • api_usage_examples.json           - 사용 예제")
    report.append("  • api_optimization_report.txt       - 본 보고서")

    report.append("\n6️⃣ 권장 사항")
    report.append("-"*80)
    report.append("  1. production_api_config.json을 프로덕션 환경에 배포")
    report.append("  2. 신규 발견 28개 API는 8:00-20:00 시간대에 테스트 진행")
    report.append("  3. 부분 성공 API는 성공한 variant만 사용")
    report.append("  4. 전체 실패 12개 API는 추후 파라미터 재검토 필요")

    report.append("\n" + "="*80)
    report.append("보고서 끝")
    report.append("="*80)

    report_text = "\n".join(report)

    report_file = 'api_optimization_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(report_text)
    print(f"\n📄 보고서 저장: {report_file}")

if __name__ == "__main__":
    create_production_config()
    print()
    create_summary_report()
