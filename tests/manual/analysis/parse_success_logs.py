
import re
import json
from pathlib import Path

def parse_log_file(log_path):
    """로그 파일을 파싱하여 성공한 API 호출 정보 추출"""

    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()

    success_pattern = r'\[INFO\] ✅ 성공 \(데이터 확인\) \[(\w+) Var (\d+)/(\d+)\] ([^\|]+) \| 성공 \(Path: (\w+)\)'

    success_records = []

    for match in re.finditer(success_pattern, log_content):
        api_id = match.group(1)
        variant_idx = int(match.group(2))
        total_variants = int(match.group(3))
        api_name = match.group(4).strip()
        path = match.group(5)

        success_records.append({
            'api_id': api_id,
            'api_name': api_name,
            'variant_idx': variant_idx,
            'total_variants': total_variants,
            'path': path
        })

    print(f"✅ 성공 패턴 {len(success_records)}개 발견")
    return success_records

def extract_variant_params_from_account():
    """account.py에서 각 API의 Variant 파라미터 추출"""
    import sys
    sys.path.insert(0, '/home/user/autotrade')

    try:
        import account
    except ImportError as e:
        print(f"❌ account.py 로드 실패: {e}")
        import traceback
        traceback.print_exc()
        return {}

    params = account.p_common.copy()
    params["stk_cd"] = params.get("placeholder_stk_kospi", "005930")
    params["ord_qty"] = "1"
    params["ord_uv"] = "0"
    params["start_dt"] = params.get("week_ago_str", "")
    params["end_dt"] = params.get("today_str", "")
    params["base_dt"] = params.get("today_str", "")

    api_variants = {}

    test_api_ids = [
        "kt00005", "kt00018", "ka10085", "ka10075", "ka10076", "kt00001", "kt00004",
        "kt00010", "kt00011", "kt00012", "kt00013", "ka10077", "ka10074", "ka10073",
        "ka10072", "ka01690", "kt00007", "kt00009", "kt00015", "kt00017", "kt00002",
        "kt00003", "kt00008", "kt00016", "ka10088", "ka10170", "ka00198", "ka10001",
        "ka10004", "ka10003", "ka10007", "ka10087", "ka10006", "ka10005", "ka10059",
        "ka10061", "ka10015", "ka10043", "ka10002", "ka10013", "ka10025", "ka10026",
        "ka10045", "ka10046", "ka10047", "ka10052", "ka10054", "ka10055", "ka10063",
        "ka10066", "ka10078", "ka10086", "ka10095", "ka10099", "ka10100", "ka10101",
        "ka10102", "ka10084", "ka10079", "ka10080", "ka10081", "ka10082", "ka10083",
        "ka10094", "ka10060", "ka10064", "ka10027", "ka10017", "ka10032", "ka10031",
        "ka10023", "ka10016", "ka00198", "ka10020", "ka10021", "ka10022", "ka10019",
        "ka10028", "ka10018", "ka10029", "ka10033", "ka10098", "ka20001", "ka20002",
        "ka20003", "ka20009", "ka10010", "ka10051", "ka90001", "ka90002", "ka10008",
        "ka10009", "ka10131", "ka10034", "ka10035", "ka10036", "ka10037", "ka10038",
        "ka10039", "ka10040", "ka10042", "ka10053", "ka10058", "ka10062", "ka10065",
        "ka90009", "ka90004", "ka90005", "ka90007", "ka90008", "ka90013", "ka10014",
        "ka10068", "ka10069", "ka20068", "ka90012", "ka10048", "ka10050", "ka30001",
        "ka30002", "ka30003", "ka30004", "ka30005", "ka30009", "ka30010", "ka30011",
        "ka30012", "ka40001", "ka40002", "ka40003", "ka40004", "ka40006", "ka40007",
        "ka40008", "ka40009", "ka40010", "ka50010", "ka50012", "ka50087", "ka50100",
        "ka50101", "ka52301", "kt50020", "kt50021", "kt50030", "kt50031", "kt50032",
        "kt50075"
    ]

    for api_id in test_api_ids:
        func = account.get_api_definition(api_id)
        if not func or func is None:
            continue

        try:
            variants = func(params)
            if variants and isinstance(variants, list) and len(variants) > 0:
                api_variants[api_id] = variants
        except Exception as e:
            pass

    return api_variants

def match_variants_with_logs(success_records, api_variants):
    """로그의 성공 기록과 account.py의 variant를 매칭"""

    verified_calls = {}

    for record in success_records:
        api_id = record['api_id']
        variant_idx = record['variant_idx']
        api_name = record['api_name']
        path = record['path']

        if api_id in api_variants:
            variants = api_variants[api_id]

            if 0 < variant_idx <= len(variants):
                variant_path, variant_body = variants[variant_idx - 1]

                if api_id not in verified_calls:
                    verified_calls[api_id] = {
                        'api_name': api_name,
                        'success_count': 0,
                        'total_variants': record['total_variants'],
                        'verified_calls': []
                    }

                verified_calls[api_id]['verified_calls'].append({
                    'variant_idx': variant_idx,
                    'path': path,
                    'body': variant_body
                })
                verified_calls[api_id]['success_count'] += 1

    return verified_calls

def main():
    print("=" * 80)
    print("로그 파일에서 성공한 API 추출")
    print("=" * 80)

    log_path = "/home/user/autotrade/comprehensive_api_debugger.py 결과 로그.txt"

    print("\n[1] 로그 파일 파싱...")
    success_records = parse_log_file(log_path)

    if not success_records:
        print("❌ 성공 기록을 찾을 수 없습니다.")
        return

    print(f"    성공 기록 {len(success_records)}개 발견")

    api_success_count = {}
    for record in success_records:
        api_id = record['api_id']
        api_success_count[api_id] = api_success_count.get(api_id, 0) + 1

    print(f"    고유 API 수: {len(api_success_count)}개")

    print("\n[2] account.py에서 Variant 파라미터 추출...")
    api_variants = extract_variant_params_from_account()
    print(f"    {len(api_variants)}개 API의 Variant 추출 완료")

    print("\n[3] 로그 기록과 Variant 매칭...")
    verified_calls = match_variants_with_logs(success_records, api_variants)

    total_verified = sum(info['success_count'] for info in verified_calls.values())
    print(f"    {len(verified_calls)}개 API, 총 {total_verified}개 검증된 호출")

    output_file = Path("verified_api_calls_full.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(verified_calls, f, ensure_ascii=False, indent=2)

    print(f"\n💾 저장 완료: {output_file}")

    print("\n" + "=" * 80)
    print(f"검증된 API 목록 ({len(verified_calls)}개)")
    print("=" * 80)

    for api_id, info in sorted(verified_calls.items()):
        print(f"  {api_id}: {info['api_name']:<30} - {info['success_count']}개 성공")

    print("\n" + "=" * 80)
    print(f"총 {total_verified}개 검증된 API 호출 저장 완료!")
    print("=" * 80)

if __name__ == "__main__":
    main()
