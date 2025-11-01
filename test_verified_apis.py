#!/usr/bin/env python3
"""
검증된 API 370건 테스트 (독립 실행)

_immutable/api_specs/successful_apis.json의 검증된 API 호출
"""
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from config import get_credentials
from core.rest_client import KiwoomRESTClient


class VerifiedAPITester:
    def __init__(self):
        self.client = KiwoomRESTClient()
        self.results = []
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'error': 0
        }

    def load_verified_apis(self):
        """검증된 API 로드"""
        json_path = Path(__file__).parent / '_immutable/api_specs/successful_apis.json'

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data['apis']

    def test_single_api(self, api_id, api_name, variant_idx, path, body):
        """단일 API 테스트"""
        print(f"  [{variant_idx}] {api_name} ({api_id})...", end=' ')

        try:
            # API 호출
            response = self.client.request(api_id, body, path)

            if response is None:
                print("❌ 응답 없음")
                self.stats['error'] += 1
                return {'status': 'error', 'msg': '응답 없음'}

            return_code = response.get('return_code')

            # 성공 판단
            if return_code == 0:
                # 데이터 확인
                data_keys = [k for k in response.keys()
                           if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]

                has_data = False
                data_count = 0

                for key in data_keys:
                    value = response.get(key)
                    if isinstance(value, list) and len(value) > 0:
                        has_data = True
                        data_count = len(value)
                        break

                if has_data:
                    print(f"✅ 성공 ({data_count}건)")
                    self.stats['success'] += 1
                    return {'status': 'success', 'data_count': data_count}
                else:
                    print("⚠️ 성공 (데이터 없음)")
                    self.stats['success'] += 1
                    return {'status': 'success_no_data'}

            elif return_code == 20:
                # 업무 메시지 (성공으로 간주)
                msg = response.get('return_msg', '')
                print(f"⚠️ 업무메시지: {msg[:30]}")
                self.stats['success'] += 1
                return {'status': 'warning', 'msg': msg}

            else:
                # 실패
                msg = response.get('return_msg', '알 수 없는 오류')
                print(f"❌ 실패: {msg[:30]}")
                self.stats['failed'] += 1
                return {'status': 'failed', 'msg': msg}

        except Exception as e:
            print(f"❌ 예외: {str(e)[:30]}")
            self.stats['error'] += 1
            return {'status': 'exception', 'msg': str(e)}

    def run_all_tests(self):
        """모든 API 테스트 실행"""
        print("=" * 80)
        print("검증된 API 370건 테스트 시작")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 검증된 API 로드
        verified_apis = self.load_verified_apis()

        # 각 API 테스트
        for api_id, api_info in verified_apis.items():
            api_name = api_info['api_name']
            category = api_info['category']
            calls = api_info['calls']

            print(f"\n[{api_id}] {api_name} ({category}) - {len(calls)}개 variant")

            for call in calls:
                variant_idx = call['variant_idx']
                path = call['path']
                body = call['body']

                self.stats['total'] += 1

                result = self.test_single_api(api_id, api_name, variant_idx, path, body)
                self.results.append({
                    'api_id': api_id,
                    'api_name': api_name,
                    'variant_idx': variant_idx,
                    'result': result
                })

                # API 속도 제한
                time.sleep(0.3)

        # 결과 출력
        self.print_summary()

    def print_summary(self):
        """결과 요약 출력"""
        print("\n" + "=" * 80)
        print("테스트 결과 요약")
        print("=" * 80)
        print(f"총 테스트: {self.stats['total']}건")
        print(f"✅ 성공: {self.stats['success']}건 ({self.stats['success']/self.stats['total']*100:.1f}%)")
        print(f"❌ 실패: {self.stats['failed']}건")
        print(f"⚠️ 오류: {self.stats['error']}건")
        print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)


if __name__ == "__main__":
    tester = VerifiedAPITester()
    tester.run_all_tests()
