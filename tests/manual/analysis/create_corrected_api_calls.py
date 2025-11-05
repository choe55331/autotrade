#!/usr/bin/env python3
"""
create_corrected_api_calls.py
실패 원인 분석을 바탕으로 파라미터를 수정한 API 호출 목록 생성
"""
import json
from pathlib import Path
from datetime import datetime, timedelta

def get_valid_dates():
    """유효한 날짜 생성 (거래일 기준)"""
    today = datetime.now()

    # 어제부터 일주일 전까지
    dates = {
        'today': today.strftime('%Y%m%d'),
        'yesterday': (today - timedelta(days=1)).strftime('%Y%m%d'),
        '3days_ago': (today - timedelta(days=3)).strftime('%Y%m%d'),
        'week_ago': (today - timedelta(days=7)).strftime('%Y%m%d'),
        'month_ago': (today - timedelta(days=30)).strftime('%Y%m%d'),
    }
    return dates

def get_valid_stock_codes():
    """실제 존재하는 종목코드 목록"""
    return {
        'samsung': '005930',      # 삼성전자
        'sk_hynix': '000660',     # SK하이닉스
        'naver': '035420',        # NAVER
        'kakao': '035720',        # 카카오
        'lg_chem': '051910',      # LG화학
        'samsung_bio': '207940',  # 삼성바이오로직스
        'hyundai_motor': '005380',# 현대차
        'kia': '000270',          # 기아
        'posco': '005490',        # POSCO홀딩스
        'celltrion': '068270',    # 셀트리온
    }

def fix_ka10010_params():
    """ka10010 (업종프로그램요청) 파라미터 수정

    문제: 업종코드처럼 보이는 "001", "201" 사용
    해결: 실제 종목코드로 변경
    """
    stocks = get_valid_stock_codes()

    return [
        {
            'variant_idx': 1,
            'path': 'sect',
            'body': {'stk_cd': stocks['samsung']},
            'status': 'pending',
            'fix_reason': '업종코드 "001"을 삼성전자 종목코드로 변경'
        },
        {
            'variant_idx': 2,
            'path': 'sect',
            'body': {'stk_cd': stocks['sk_hynix']},
            'status': 'pending',
            'fix_reason': '업종코드 "201"을 SK하이닉스 종목코드로 변경'
        },
        {
            'variant_idx': 3,
            'path': 'sect',
            'body': {'stk_cd': stocks['naver']},
            'status': 'pending',
            'fix_reason': '업종코드 "101"을 NAVER 종목코드로 변경'
        },
    ]

def fix_partial_failure_params(api_id, failed_variants):
    """부분 실패 API의 실패한 variant 파라미터 수정"""

    stocks = get_valid_stock_codes()
    dates = get_valid_dates()
    fixed = []

    for variant in failed_variants:
        variant_idx = variant['variant_idx']
        path = variant['path']
        body = variant['body'].copy()
        fix_reason = []

        # 종목코드 수정
        if 'stk_cd' in body:
            old_code = body['stk_cd']
            if old_code in ['000660', '066970', '071050']:
                # 문제있는 종목코드를 안정적인 것으로 변경
                body['stk_cd'] = stocks['samsung']
                fix_reason.append(f'종목코드 {old_code} → 005930 (삼성전자)')

        # 날짜 파라미터 수정 (최근 데이터 있을 확률 높은 날짜로)
        if 'strt_dt' in body:
            body['strt_dt'] = dates['week_ago']
            fix_reason.append(f'시작일자를 일주일 전으로 변경')

        if 'end_dt' in body:
            body['end_dt'] = dates['yesterday']
            fix_reason.append(f'종료일자를 어제로 변경')

        if 'ord_dt' in body:
            body['ord_dt'] = dates['yesterday']
            fix_reason.append(f'주문일자를 어제로 변경')

        if 'base_dt' in body:
            body['base_dt'] = dates['yesterday']
            fix_reason.append(f'기준일자를 어제로 변경')

        # ELW 관련 파라미터 수정
        if 'bsis_aset_cd' in body:
            old_code = body['bsis_aset_cd']
            if old_code in ['000660', '066970']:
                # ELW 기초자산코드를 KOSPI200으로 변경
                body['bsis_aset_cd'] = '201'
                fix_reason.append(f'기초자산코드 {old_code} → 201 (KOSPI200)')

        # 테마 파라미터 수정
        if api_id == 'ka90001':
            if 'qry_tp' in body and body['qry_tp'] == '1':
                # 테마명 조회는 성공한 variant 참고
                body['qry_tp'] = '0'
                fix_reason.append('qry_tp를 0 (전체조회)로 변경')

        fixed.append({
            'variant_idx': variant_idx,
            'path': path,
            'body': body,
            'status': 'corrected',
            'fix_reason': '; '.join(fix_reason) if fix_reason else '파라미터 최적화'
        })

    return fixed

def create_corrected_api_calls():
    """수정된 API 호출 목록 생성"""

    print("="*80)
    print("파라미터 수정 기반 API 호출 목록 생성")
    print("="*80)

    # 원본 데이터 로드
    with open('all_394_api_calls.json', 'r', encoding='utf-8') as f:
        original_calls = json.load(f)

    with open('optimized_api_calls.json', 'r', encoding='utf-8') as f:
        optimized = json.load(f)

    # 수정된 API 목록
    corrected_apis = {}
    corrections_made = 0

    # 1. ka10010 수정
    print("\n[1] ka10010 (업종프로그램요청) 파라미터 수정...")
    fixed_ka10010 = fix_ka10010_params()

    corrected_apis['ka10010'] = {
        'api_name': '업종프로그램요청',
        'original_status': 'total_fail',
        'corrected_variants': fixed_ka10010
    }
    corrections_made += len(fixed_ka10010)

    for variant in fixed_ka10010:
        print(f"  Var {variant['variant_idx']}: {variant['fix_reason']}")

    # 2. 부분 실패 API 수정
    print("\n[2] 부분 실패 API 파라미터 수정...")

    partial_fail_apis = {
        'kt00010': '주문인출가능금액요청',
        'ka10073': '일자별종목별실현손익요청_기간',
        'ka10072': '일자별종목별실현손익요청_일자',
        'kt00007': '계좌별주문체결내역상세요청',
        'ka10064': '장중투자자별매매차트요청',
        'ka10021': '호가잔량급증요청',
        'ka90001': '테마그룹별요청',
        'ka30003': 'ELWLP보유일별추이요청',
        'ka30004': 'ELW괴리율요청',
        'ka30005': 'ELW조건검색요청',
        'ka10054': '변동성완화장치',
    }

    for api_id, api_name in partial_fail_apis.items():
        original_api = original_calls.get(api_id)
        if not original_api:
            continue

        # 실패한 variant 찾기
        failed_variants = [
            call for call in original_api['all_calls']
            if call['status'] != 'success'
        ]

        if failed_variants:
            print(f"\n  [{api_id}] {api_name}")
            print(f"    실패 variant: {len(failed_variants)}개")

            fixed_variants = fix_partial_failure_params(api_id, failed_variants)

            corrected_apis[api_id] = {
                'api_name': api_name,
                'original_status': 'partial_fail',
                'failed_count': len(failed_variants),
                'corrected_variants': fixed_variants
            }
            corrections_made += len(fixed_variants)

            for variant in fixed_variants[:2]:  # 처음 2개만 표시
                print(f"    Var {variant['variant_idx']}: {variant['fix_reason']}")

    # 3. 검증된 API는 그대로 유지
    verified_count = len(optimized['optimized_apis'])
    verified_variants = optimized['metadata']['stats']['total_success_variants'] + \
                       optimized['metadata']['stats']['partial_success_variants']

    # 결과 저장
    output = {
        'metadata': {
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'description': '파라미터 수정을 적용한 API 호출 목록',
            'verified_apis': verified_count,
            'verified_variants': verified_variants,
            'corrected_apis': len(corrected_apis),
            'corrections_made': corrections_made,
            'total_test_targets': verified_variants + corrections_made
        },
        'verified_apis': optimized['optimized_apis'],
        'corrected_apis': corrected_apis,
        'correction_summary': {
            'ka10010': '업종코드 → 실제 종목코드로 변경',
            'partial_failures': '실패 종목코드, 날짜 파라미터 최적화',
            'dates_updated': get_valid_dates(),
            'stock_codes_used': get_valid_stock_codes()
        }
    }

    output_file = 'corrected_api_calls.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 통계 출력
    print("\n" + "="*80)
    print("📊 수정 완료 통계")
    print("="*80)
    print(f"✅ 검증된 API: {verified_count}개 ({verified_variants}개 variant)")
    print(f"🔧 수정된 API: {len(corrected_apis)}개 ({corrections_made}개 variant)")
    print(f"📊 총 테스트 대상: {verified_variants + corrections_made}개 variant")
    print(f"\n💾 저장 완료: {output_file}")
    print("="*80)

    return output

if __name__ == "__main__":
    create_corrected_api_calls()
