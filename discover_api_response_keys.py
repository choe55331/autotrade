#!/usr/bin/env python3
"""
API 응답 키 자동 탐색 스크립트

목적:
- successful_apis.json의 모든 API를 실제로 호출
- 각 API의 응답에서 실제 데이터가 있는 키를 찾음
- return_code: 0 + 실제 데이터 있음 = 진짜 성공
- 결과를 api_response_keys.json으로 저장

사용법:
    python discover_api_response_keys.py
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent))

from core.rest_client import KiwoomRESTClient
from config import get_credentials

class APIResponseKeyDiscovery:
    """API 응답 키 자동 탐색"""

    def __init__(self):
        self.client = None
        self.results = {}
        self.stats = {
            'total_apis': 0,
            'tested_apis': 0,
            'success_with_data': 0,
            'success_no_data': 0,
            'failed': 0,
        }

    def init_client(self) -> bool:
        """REST 클라이언트 초기화"""
        print("=" * 80)
        print("API 응답 키 자동 탐색 시작")
        print("=" * 80)
        print("\n1. REST 클라이언트 초기화 중...")

        try:
            self.client = KiwoomRESTClient()
            if self.client.token:
                print("✅ 클라이언트 초기화 성공\n")
                return True
            else:
                print("❌ 토큰 발급 실패\n")
                return False
        except Exception as e:
            print(f"❌ 초기화 실패: {e}\n")
            return False

    def load_successful_apis(self) -> Dict[str, Any]:
        """successful_apis.json 로드"""
        print("2. successful_apis.json 로드 중...")

        api_specs_path = Path(__file__).parent / '_immutable' / 'api_specs' / 'successful_apis.json'

        try:
            with open(api_specs_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # successful_apis.json 구조: {"metadata": {...}, "apis": {...}}
                apis = data.get('apis', {})
                print(f"✅ {len(apis)} 개 API 정의 로드 완료\n")
                return apis
        except Exception as e:
            print(f"❌ 로드 실패: {e}\n")
            return {}

    def discover_response_key(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """응답에서 데이터가 있는 키 찾기"""
        if not response or response.get('return_code') != 0:
            return None

        # 메타데이터 키 제외
        metadata_keys = {'return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key'}
        data_keys = [k for k in response.keys() if k not in metadata_keys]

        # 각 키의 데이터 확인
        result = {
            'data_keys': [],
            'total_items': 0,
            'key_details': {}
        }

        for key in data_keys:
            value = response.get(key)

            if isinstance(value, list):
                if len(value) > 0:
                    result['data_keys'].append(key)
                    result['total_items'] += len(value)
                    result['key_details'][key] = {
                        'type': 'list',
                        'count': len(value),
                        'sample_keys': list(value[0].keys()) if value and isinstance(value[0], dict) else []
                    }
            elif isinstance(value, dict):
                if value:  # 빈 dict가 아니면
                    result['data_keys'].append(key)
                    result['total_items'] += 1
                    result['key_details'][key] = {
                        'type': 'dict',
                        'keys': list(value.keys())
                    }
            elif value:  # 문자열이나 숫자 등
                result['data_keys'].append(key)
                result['total_items'] += 1
                result['key_details'][key] = {
                    'type': type(value).__name__,
                    'value': str(value)[:100]  # 처음 100자만
                }

        return result if result['data_keys'] else None

    def test_api(self, api_id: str, api_info: Dict[str, Any]) -> Dict[str, Any]:
        """단일 API 테스트"""
        result = {
            'api_id': api_id,
            'api_name': api_info.get('api_name', ''),
            'category': api_info.get('category', ''),
            'variants': []
        }

        calls = api_info.get('calls', [])

        for call in calls:
            if call.get('status') != 'success':
                continue  # 원래 성공한 것만 테스트

            variant_result = {
                'variant_idx': call.get('variant_idx'),
                'path': call.get('path'),
                'body': call.get('body'),
                'success': False,
                'has_data': False,
                'response_keys': None
            }

            try:
                # API 호출
                response = self.client.request(
                    api_id=api_id,
                    body=call.get('body', {}),
                    path=call.get('path', '')
                )

                # 응답 분석
                if response and response.get('return_code') == 0:
                    variant_result['success'] = True

                    # 응답 키 발견
                    key_info = self.discover_response_key(response)
                    if key_info and key_info['total_items'] > 0:
                        variant_result['has_data'] = True
                        variant_result['response_keys'] = key_info
                        self.stats['success_with_data'] += 1
                    else:
                        self.stats['success_no_data'] += 1
                else:
                    self.stats['failed'] += 1

            except Exception as e:
                variant_result['error'] = str(e)
                self.stats['failed'] += 1

            result['variants'].append(variant_result)

            # API 호출 제한 고려 (짧은 지연)
            time.sleep(0.05)

        return result

    def run_discovery(self, limit: int = None):
        """모든 API 탐색 실행"""
        apis = self.load_successful_apis()
        if not apis:
            return

        self.stats['total_apis'] = len(apis)

        print("3. API 응답 키 탐색 시작...")
        print(f"   총 {len(apis)}개 API 테스트 예정")
        if limit:
            print(f"   (처음 {limit}개만 테스트)\n")
        else:
            print()

        # 카테고리별로 분류
        by_category = {}

        tested_count = 0
        for api_id, api_info in apis.items():
            if limit and tested_count >= limit:
                break

            category = api_info.get('category', 'unknown')

            print(f"[{tested_count + 1}/{len(apis)}] {api_id} ({api_info.get('api_name', '')})...")

            result = self.test_api(api_id, api_info)

            # 카테고리별 저장
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(result)

            # 결과 요약 출력
            has_data_count = sum(1 for v in result['variants'] if v.get('has_data'))
            total_variants = len(result['variants'])

            if has_data_count > 0:
                print(f"   ✅ {has_data_count}/{total_variants} variants에서 데이터 확인")
            elif any(v.get('success') for v in result['variants']):
                print(f"   ⚠️  성공했지만 데이터 없음")
            else:
                print(f"   ❌ 실패")

            tested_count += 1
            self.stats['tested_apis'] += 1

        self.results = by_category

        # 통계 출력
        print("\n" + "=" * 80)
        print("탐색 완료!")
        print("=" * 80)
        print(f"총 API: {self.stats['total_apis']}")
        print(f"테스트: {self.stats['tested_apis']}")
        print(f"✅ 성공 (데이터 O): {self.stats['success_with_data']}")
        print(f"⚠️  성공 (데이터 X): {self.stats['success_no_data']}")
        print(f"❌ 실패: {self.stats['failed']}")
        print()

    def save_results(self):
        """결과 저장"""
        output_path = Path(__file__).parent / '_immutable' / 'api_specs' / 'api_response_keys.json'

        output_data = {
            'metadata': {
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'stats': self.stats,
                'description': 'API 응답 키 탐색 결과 - 실제 데이터가 있는 키만 기록'
            },
            'by_category': self.results
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 결과 저장 완료: {output_path}")
        print()

        # 주요 ranking API 결과 출력
        if 'ranking' in self.results:
            print("=" * 80)
            print("📊 Ranking API 응답 키 요약")
            print("=" * 80)

            for api in self.results['ranking']:
                api_id = api['api_id']
                api_name = api['api_name']

                for variant in api['variants']:
                    if variant.get('has_data'):
                        keys = variant['response_keys']['data_keys']
                        count = variant['response_keys']['total_items']
                        print(f"\n{api_id} - {api_name}")
                        print(f"  응답 키: {', '.join(keys)}")
                        print(f"  데이터 개수: {count}")
                        break


def main():
    """메인 함수"""
    discoverer = APIResponseKeyDiscovery()

    if not discoverer.init_client():
        print("클라이언트 초기화 실패. 종료합니다.")
        return 1

    # 모든 API 탐색 (또는 limit=10 으로 테스트)
    discoverer.run_discovery(limit=None)  # None = 전체, 숫자 = 제한

    # 결과 저장
    discoverer.save_results()

    return 0


if __name__ == '__main__':
    sys.exit(main())
