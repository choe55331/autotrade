#!/usr/bin/env python3
"""
test_verified_and_corrected_apis_fixed.py
검증된 347개 + 수정된 23개 = 총 370개 API 테스트
test_all_394_calls.py와 동일한 방식 사용 (성공 확인됨)
"""
import os
import sys
import requests
import json
from datetime import datetime, time
from pathlib import Path
import time as time_module

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# credentials.py에서 API 키 로드
from config import get_credentials

class VerifiedCorrectedAPITester:
    def __init__(self):
        # secrets.json에서 설정 로드
        credentials = get_credentials()
        kiwoom_config = credentials.get_kiwoom_config()

        self.base_url = kiwoom_config['base_url']
        self.appkey = kiwoom_config['appkey']
        self.secretkey = kiwoom_config['secretkey']
        self.token = None
        self.results = []

    def get_token(self):
        """토큰 발급"""
        url = f"{self.base_url}/oauth2/token"
        payload = {
            "grant_type": "client_credentials",
            "appkey": self.appkey,
            "secretkey": self.secretkey
        }
        headers = {"content-type": "application/json;charset=UTF-8"}

        try:
            res = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
            if res.status_code == 200:
                token_data = res.json()
                self.token = token_data.get('token')
                if self.token:
                    print("✅ 토큰 발급 성공")
                    return True
            print(f"❌ 토큰 발급 실패: HTTP {res.status_code}")
            return False
        except Exception as e:
            print(f"❌ 토큰 발급 실패: {e}")
            return False

    def request(self, api_id, body, path):
        """API 호출"""
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.token}",
            "api-id": api_id
        }
        url = f"{self.base_url}/api/dostk/{path}"

        try:
            res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
            if res.status_code == 200:
                return res.json()
            else:
                return {"return_code": -1, "return_msg": f"HTTP {res.status_code}"}
        except Exception as e:
            return {"return_code": -999, "return_msg": str(e)}

    def validate_data(self, response):
        """엄격한 데이터 검증"""
        return_code = response.get('return_code')

        if return_code != 0:
            return False, 0, "return_code != 0"

        # 데이터 키 확인
        data_keys = [k for k in response.keys()
                     if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]

        if not data_keys:
            return False, 0, "no data keys"

        # 실제 데이터 확인
        data_count = 0
        for key in data_keys:
            value = response.get(key)
            if isinstance(value, list):
                if len(value) > 0:
                    data_count += len(value)
            elif value and value != '':
                data_count += 1

        if data_count > 0:
            return True, data_count, "success"
        else:
            return False, 0, "empty data"

    def test_single_call(self, api_id, api_name, variant_idx, path, body, original_status):
        """단일 API 호출 테스트"""
        response = self.request(api_id, body, path)

        # 데이터 검증
        is_success, data_count, validation_msg = self.validate_data(response)

        result = {
            "api_id": api_id,
            "api_name": api_name,
            "variant_idx": variant_idx,
            "path": path,
            "body": body,
            "original_status": original_status,
            "return_code": response.get('return_code'),
            "return_msg": response.get('return_msg', ''),
            "is_real_success": is_success,
            "data_count": data_count,
            "validation_msg": validation_msg
        }

        return result

    def run_test(self):
        """전체 테스트 실행"""
        print("="*80)
        print("검증된 + 수정된 API 전체 테스트 (370개)")
        print("="*80)

        # 데이터 로드
        print("\n[1] 데이터 로드 중...")
        with open('corrected_api_calls.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        verified_apis = data['verified_apis']
        corrected_apis = data['corrected_apis']

        print(f"  ✅ 검증된 API: {len(verified_apis)}개")
        print(f"  🔧 수정된 API: {len(corrected_apis)}개")

        # 토큰 발급
        print("\n[2] 토큰 발급 중...")
        if not self.get_token():
            print("❌ 토큰 발급 실패. 프로그램을 종료합니다.")
            return

        # 통계
        stats = {
            'verified': {'tested': 0, 'success': 0, 'no_data': 0, 'error': 0},
            'corrected': {'tested': 0, 'success': 0, 'no_data': 0, 'error': 0, 'improved': 0}
        }

        # ====================================================================
        # [3] 검증된 API 테스트
        # ====================================================================
        print("\n[3] 검증된 API 테스트 (347개)...")
        print("-"*80)

        for api_id, api_info in verified_apis.items():
            api_name = api_info['api_name']

            for call in api_info['optimized_calls']:
                variant_idx = call['variant_idx']
                path = call['path']
                body = call['body']

                stats['verified']['tested'] += 1

                print(f"  테스트 중 [{api_id} Var {variant_idx}] {api_name[:30]:30s} ", end='', flush=True)

                result = self.test_single_call(api_id, api_name, variant_idx, path, body, 'verified')
                self.results.append(result)

                if result['is_real_success']:
                    print(f"✅ SUCCESS ({result['data_count']}개)")
                    stats['verified']['success'] += 1
                elif result['return_code'] == 0:
                    print(f"⚠️  NO_DATA")
                    stats['verified']['no_data'] += 1
                else:
                    print(f"❌ ERROR: {result['return_msg'][:40]}")
                    stats['verified']['error'] += 1

        # ====================================================================
        # [4] 수정된 API 테스트
        # ====================================================================
        print("\n[4] 수정된 API 테스트 (23개)...")
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

                print(f"    Var {variant_idx}: {fix_reason[:50]:50s} ", end='', flush=True)

                result = self.test_single_call(api_id, api_name, variant_idx, path, body, original_status)
                self.results.append(result)

                if result['is_real_success']:
                    print(f"✅ SUCCESS! ({result['data_count']}개)")
                    stats['corrected']['success'] += 1
                    if original_status == 'total_fail':
                        stats['corrected']['improved'] += 1
                elif result['return_code'] == 0:
                    print(f"⚠️  NO_DATA")
                    stats['corrected']['no_data'] += 1
                else:
                    print(f"❌ ERROR: {result['return_msg'][:30]}")
                    stats['corrected']['error'] += 1

        # ====================================================================
        # [5] 통계 출력
        # ====================================================================
        print("\n" + "="*80)
        print("📊 테스트 결과 통계")
        print("="*80)

        total_tested = stats['verified']['tested'] + stats['corrected']['tested']
        total_success = stats['verified']['success'] + stats['corrected']['success']

        print(f"\n✅ 검증된 API ({stats['verified']['tested']}개)")
        print(f"  - 진짜 성공: {stats['verified']['success']}개 ({stats['verified']['success']/stats['verified']['tested']*100:.1f}%)")
        print(f"  - 데이터 없음: {stats['verified']['no_data']}개")
        print(f"  - 오류: {stats['verified']['error']}개")

        print(f"\n🔧 수정된 API ({stats['corrected']['tested']}개)")
        print(f"  - 진짜 성공: {stats['corrected']['success']}개")
        print(f"  - 데이터 없음: {stats['corrected']['no_data']}개")
        print(f"  - 오류: {stats['corrected']['error']}개")
        print(f"  🎉 실패→성공 개선: {stats['corrected']['improved']}개")

        print(f"\n📊 전체 결과")
        print(f"  총 테스트: {total_tested}개")
        print(f"  ✅ 성공: {total_success}개 ({total_success/total_tested*100:.1f}%)")

        # 결과 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = f'final_test_results_{timestamp}.json'

        output = {
            'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'statistics': stats,
            'results': self.results
        }

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"\n💾 결과 저장: {result_file}")
        print("="*80)

if __name__ == "__main__":
    tester = VerifiedCorrectedAPITester()
    tester.run_test()
