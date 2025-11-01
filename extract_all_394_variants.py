#!/usr/bin/env python3
# extract_all_394_variants.py - 로그에서 394개 전체 Variant 추출

import re
import json
from pathlib import Path

def parse_all_variants_from_log(log_path):
    """로그 파일에서 394개 모든 Variant 추출 (성공+실패+데이터없음)"""

    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()

    all_records = []

    # 1. 성공 (데이터 확인) - 347개
    success_pattern = r'\[INFO\] ✅ 성공 \(데이터 확인\) \[(\w+) Var (\d+)/(\d+)\] ([^\|]+) \| 성공 \(Path: (\w+)\)'
    for match in re.finditer(success_pattern, log_content):
        all_records.append({
            'api_id': match.group(1),
            'variant_idx': int(match.group(2)),
            'total_variants': int(match.group(3)),
            'api_name': match.group(4).strip(),
            'path': match.group(5),
            'status': 'success'
        })

    # 2. 성공 (데이터 없음) - 10개
    no_data_pattern = r'\[WARNING\] ⚠️ 성공 \(데이터 없음\) \[(\w+) Var (\d+)/(\d+)\] ([^\|]+) \|.*?\(Path: (\w+)\)'
    for match in re.finditer(no_data_pattern, log_content):
        all_records.append({
            'api_id': match.group(1),
            'variant_idx': int(match.group(2)),
            'total_variants': int(match.group(3)),
            'api_name': match.group(4).strip(),
            'path': match.group(5),
            'status': 'no_data'
        })

    # 3. 실패 (API 오류) - 대부분
    api_error_pattern = r'\[ERROR\] ❌ 실패 \(API 오류\) \[(\w+) Var (\d+)/(\d+)\] ([^\|]+) \|.*?\(Path: (\w+)\)'
    for match in re.finditer(api_error_pattern, log_content):
        all_records.append({
            'api_id': match.group(1),
            'variant_idx': int(match.group(2)),
            'total_variants': int(match.group(3)),
            'api_name': match.group(4).strip(),
            'path': match.group(5),
            'status': 'api_error'
        })

    # 4. 실패 (경로 오류)
    path_error_pattern = r'\[ERROR\] ❌ 실패 \(경로 오류\) \[(\w+) Var (\d+)/(\d+)\] ([^\|]+) \|.*?\(Path: (\w+)\)'
    for match in re.finditer(path_error_pattern, log_content):
        all_records.append({
            'api_id': match.group(1),
            'variant_idx': int(match.group(2)),
            'total_variants': int(match.group(3)),
            'api_name': match.group(4).strip(),
            'path': match.group(5),
            'status': 'path_error'
        })

    # 5. 실패 (내부 예외)
    exception_pattern = r'\[CRITICAL\] ❌ 실패 \(내부 예외\) \[(\w+) Var (\d+)/(\d+)\] ([^\|]+) \|.*?\(Path: (\w+)\)'
    for match in re.finditer(exception_pattern, log_content):
        all_records.append({
            'api_id': match.group(1),
            'variant_idx': int(match.group(2)),
            'total_variants': int(match.group(3)),
            'api_name': match.group(4).strip(),
            'path': match.group(5),
            'status': 'exception'
        })

    print(f"추출된 레코드: {len(all_records)}개")

    # 상태별 집계
    status_count = {}
    for record in all_records:
        status = record['status']
        status_count[status] = status_count.get(status, 0) + 1

    print(f"  - 성공: {status_count.get('success', 0)}개")
    print(f"  - 데이터없음: {status_count.get('no_data', 0)}개")
    print(f"  - API오류: {status_count.get('api_error', 0)}개")
    print(f"  - 경로오류: {status_count.get('path_error', 0)}개")
    print(f"  - 내부예외: {status_count.get('exception', 0)}개")

    return all_records

def extract_variant_params():
    """account.py에서 Variant 파라미터 추출"""
    import sys
    sys.path.insert(0, '/home/user/autotrade')

    import account

    params = account.p_common.copy()
    params["stk_cd"] = params.get("placeholder_stk_kospi", "005930")
    params["ord_qty"] = "1"
    params["ord_uv"] = "0"
    params["start_dt"] = params.get("week_ago_str", "")
    params["end_dt"] = params.get("today_str", "")
    params["base_dt"] = params.get("today_str", "")

    api_variants = {}

    # 로그에 등장한 모든 API ID
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
        "ka10023", "ka10016", "ka10020", "ka10021", "ka10022", "ka10019",
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
        "kt50075", "ka10030"  # 누락된 것 추가
    ]

    for api_id in test_api_ids:
        func = account.get_api_definition(api_id)
        if not func:
            continue

        try:
            variants = func(params)
            if variants and isinstance(variants, list) and len(variants) > 0:
                api_variants[api_id] = variants
        except:
            pass

    return api_variants

def match_all_variants(all_records, api_variants):
    """모든 레코드를 variant와 매칭"""

    all_api_calls = {}

    for record in all_records:
        api_id = record['api_id']
        variant_idx = record['variant_idx']
        api_name = record['api_name']
        path = record['path']
        status = record['status']

        # variant 파라미터 가져오기
        if api_id in api_variants:
            variants = api_variants[api_id]

            if 0 < variant_idx <= len(variants):
                variant_path, variant_body = variants[variant_idx - 1]

                if api_id not in all_api_calls:
                    all_api_calls[api_id] = {
                        'api_name': api_name,
                        'total_variants': record['total_variants'],
                        'all_calls': []
                    }

                all_api_calls[api_id]['all_calls'].append({
                    'variant_idx': variant_idx,
                    'path': path,
                    'body': variant_body,
                    'status': status  # success, no_data, api_error 등
                })

    return all_api_calls

def main():
    print("=" * 80)
    print("로그에서 394개 전체 Variant 추출")
    print("=" * 80)

    log_path = "/home/user/autotrade/comprehensive_api_debugger.py 결과 로그.txt"

    # 1. 로그 파싱
    print("\n[1] 로그 파일 파싱...")
    all_records = parse_all_variants_from_log(log_path)

    if not all_records:
        print("❌ 레코드를 찾을 수 없습니다.")
        return

    # 2. account.py에서 variants 추출
    print("\n[2] account.py에서 Variant 파라미터 추출...")
    api_variants = extract_variant_params()
    print(f"    {len(api_variants)}개 API의 Variant 추출 완료")

    # 3. 매칭
    print("\n[3] 로그 기록과 Variant 매칭...")
    all_api_calls = match_all_variants(all_records, api_variants)

    total_calls = sum(len(info['all_calls']) for info in all_api_calls.values())
    print(f"    {len(all_api_calls)}개 API, 총 {total_calls}개 호출 매칭됨")

    # 4. 저장
    output_file = Path("all_394_api_calls.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_api_calls, f, ensure_ascii=False, indent=2)

    print(f"\n💾 저장 완료: {output_file}")

    # 5. 요약
    print("\n" + "=" * 80)
    print(f"전체 API 목록 ({len(all_api_calls)}개)")
    print("=" * 80)

    for api_id, info in sorted(all_api_calls.items()):
        success = len([c for c in info['all_calls'] if c['status'] == 'success'])
        no_data = len([c for c in info['all_calls'] if c['status'] == 'no_data'])
        error = len([c for c in info['all_calls'] if c['status'] in ['api_error', 'path_error', 'exception']])

        print(f"  {api_id}: {info['api_name']:<30} - {len(info['all_calls'])}개 (성공:{success}, 데이터없음:{no_data}, 실패:{error})")

    print("\n" + "=" * 80)
    print(f"총 {total_calls}개 API 호출 저장 완료!")
    print("=" * 80)

if __name__ == "__main__":
    main()
