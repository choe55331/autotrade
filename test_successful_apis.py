#!/usr/bin/env python3
"""
successful_apis.json 테스트 스크립트

이전에 성공했던 API들이 여전히 정상 작동하는지 검증합니다.
성공 기준: API 호출 성공 + 실제 데이터 수신

사용법:
    python test_successful_apis.py

결과:
    - 콘솔에 실시간 결과 출력
    - test_results/successful_apis_test_YYYYMMDD_HHMMSS.json 파일 생성
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.WARNING,  # WARNING 이상만 출력
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 색상 코드
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'
DIM = '\033[2m'


def print_header(text: str):
    """헤더 출력"""
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")


def print_success(text: str):
    """성공 메시지"""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text: str):
    """에러 메시지"""
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text: str):
    """경고 메시지"""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_info(text: str):
    """정보 메시지"""
    print(f"{CYAN}ℹ️  {text}{RESET}")


def print_progress(current: int, total: int, text: str):
    """진행률 출력"""
    percentage = (current / total * 100) if total > 0 else 0
    print(f"{DIM}[{current}/{total} - {percentage:.1f}%]{RESET} {text}")


class SuccessfulAPITester:
    """성공했던 API들을 재테스트하는 클래스"""

    def __init__(self):
        """초기화"""
        self.client = None
        self.api_specs = None
        self.results = {
            'metadata': {
                'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_apis': 0,
                'total_variants': 0,
                'tested_variants': 0,
                'successful_variants': 0,
                'failed_variants': 0,
                'success_rate': 0.0
            },
            'api_results': {},
            'failed_apis': []
        }

    def load_api_specs(self) -> bool:
        """successful_apis.json 로드"""
        try:
            api_specs_path = Path('_immutable/api_specs/successful_apis.json')

            if not api_specs_path.exists():
                print_error(f"파일을 찾을 수 없습니다: {api_specs_path}")
                return False

            with open(api_specs_path, 'r', encoding='utf-8') as f:
                self.api_specs = json.load(f)

            apis = self.api_specs.get('apis', {})
            total_apis = len(apis)
            total_variants = sum(
                len(api_data.get('calls', []))
                for api_data in apis.values()
            )

            self.results['metadata']['total_apis'] = total_apis
            self.results['metadata']['total_variants'] = total_variants

            print_success(f"API 스펙 로드 완료")
            print_info(f"총 API 개수: {total_apis}")
            print_info(f"총 Variant 개수: {total_variants}")

            return True

        except Exception as e:
            print_error(f"API 스펙 로드 실패: {e}")
            return False

    def init_client(self) -> bool:
        """KiwoomRESTClient 초기화"""
        try:
            from core.rest_client import KiwoomRESTClient

            print_info("Kiwoom REST Client 초기화 중...")
            self.client = KiwoomRESTClient()

            if not self.client.token:
                print_error("토큰 발급 실패")
                return False

            print_success("REST Client 초기화 완료")
            return True

        except Exception as e:
            print_error(f"Client 초기화 실패: {e}")
            import traceback
            traceback.print_exc()
            return False

    def check_response_has_data(self, response: Dict[str, Any]) -> bool:
        """
        응답에 실제 데이터가 있는지 확인

        성공 기준:
        1. return_code == 0
        2. 실제 데이터가 포함되어 있음

        Args:
            response: API 응답

        Returns:
            데이터가 있으면 True, 없으면 False
        """
        if not response:
            return False

        # return_code 확인
        if response.get('return_code') != 0:
            return False

        # 데이터 확인
        # 가능한 데이터 키들
        data_keys = ['output', 'output1', 'output2', 'pred_trde_qty_upper',
                     'pred_pre_flu_rt_upper', 'pred_trde_amt_upper']

        for key in data_keys:
            data = response.get(key)
            if data:
                # 리스트인 경우 빈 리스트가 아닌지 확인
                if isinstance(data, list):
                    if len(data) > 0:
                        return True
                # 딕셔너리인 경우 빈 딕셔너리가 아닌지 확인
                elif isinstance(data, dict):
                    if len(data) > 0:
                        return True
                # 그 외의 경우 값이 있으면 True
                else:
                    return True

        return False

    def test_api_variant(
        self,
        api_id: str,
        variant: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        API variant 테스트

        Args:
            api_id: API ID
            variant: variant 정보

        Returns:
            테스트 결과
        """
        result = {
            'variant_idx': variant.get('variant_idx', 0),
            'path': variant.get('path', ''),
            'status': 'unknown',
            'return_code': None,
            'return_msg': None,
            'has_data': False,
            'error': None
        }

        try:
            path = variant.get('path', '')
            body = variant.get('body', {})

            # API 호출
            response = self.client.request(
                api_id=api_id,
                body=body,
                path=path
            )

            if response:
                result['return_code'] = response.get('return_code')
                result['return_msg'] = response.get('return_msg', '')

                # 데이터 확인
                result['has_data'] = self.check_response_has_data(response)

                # 성공 여부 판단: return_code == 0 AND 데이터 있음
                if result['return_code'] == 0 and result['has_data']:
                    result['status'] = 'success'
                elif result['return_code'] == 0 and not result['has_data']:
                    result['status'] = 'no_data'
                else:
                    result['status'] = 'failed'
            else:
                result['status'] = 'failed'
                result['error'] = 'No response'

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)

        return result

    def test_api(self, api_id: str, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        API 테스트 (모든 variants)

        Args:
            api_id: API ID
            api_data: API 정보

        Returns:
            테스트 결과
        """
        api_name = api_data.get('api_name', 'Unknown')
        category = api_data.get('category', 'unknown')
        calls = api_data.get('calls', [])

        print(f"\n{BOLD}Testing {api_id}{RESET} - {api_name} ({category})")

        results = {
            'api_id': api_id,
            'api_name': api_name,
            'category': category,
            'total_variants': len(calls),
            'successful_variants': 0,
            'failed_variants': 0,
            'variants': []
        }

        for i, variant in enumerate(calls, 1):
            variant_idx = variant.get('variant_idx', i)

            # 테스트 실행
            variant_result = self.test_api_variant(api_id, variant)
            results['variants'].append(variant_result)

            # 통계 업데이트
            if variant_result['status'] == 'success':
                results['successful_variants'] += 1
                print(f"  {GREEN}✓{RESET} Variant {variant_idx}: Success")
            else:
                results['failed_variants'] += 1
                msg = variant_result.get('return_msg', variant_result.get('error', 'Unknown'))
                print(f"  {RED}✗{RESET} Variant {variant_idx}: Failed - {msg}")

        return results

    def run_tests(self):
        """모든 API 테스트 실행"""
        print_header("Successful APIs 테스트 시작")

        apis = self.api_specs.get('apis', {})
        total_apis = len(apis)

        current = 0
        for api_id, api_data in apis.items():
            current += 1
            print_progress(current, total_apis, f"Testing {api_id}")

            # API 테스트
            api_result = self.test_api(api_id, api_data)

            # 결과 저장
            self.results['api_results'][api_id] = api_result

            # 실패한 API 기록
            if api_result['failed_variants'] > 0:
                self.results['failed_apis'].append({
                    'api_id': api_id,
                    'api_name': api_result['api_name'],
                    'total_variants': api_result['total_variants'],
                    'failed_variants': api_result['failed_variants']
                })

            # 전체 통계 업데이트
            self.results['metadata']['tested_variants'] += api_result['total_variants']
            self.results['metadata']['successful_variants'] += api_result['successful_variants']
            self.results['metadata']['failed_variants'] += api_result['failed_variants']

        # 성공률 계산
        tested = self.results['metadata']['tested_variants']
        successful = self.results['metadata']['successful_variants']
        if tested > 0:
            self.results['metadata']['success_rate'] = (successful / tested) * 100

    def print_summary(self):
        """테스트 결과 요약 출력"""
        print_header("테스트 결과 요약")

        meta = self.results['metadata']

        print(f"{BOLD}전체 통계:{RESET}")
        print(f"  총 API: {meta['total_apis']}")
        print(f"  총 Variant: {meta['total_variants']}")
        print(f"  테스트 완료: {meta['tested_variants']}")
        print(f"  {GREEN}성공: {meta['successful_variants']}{RESET}")
        print(f"  {RED}실패: {meta['failed_variants']}{RESET}")
        print(f"  성공률: {GREEN if meta['success_rate'] >= 90 else YELLOW}{meta['success_rate']:.1f}%{RESET}")

        # 실패한 API 목록
        if self.results['failed_apis']:
            print(f"\n{BOLD}{RED}실패한 API 목록:{RESET}")
            for failed in self.results['failed_apis']:
                print(f"  • {failed['api_id']} - {failed['api_name']}: "
                      f"{failed['failed_variants']}/{failed['total_variants']} variants failed")

    def save_results(self):
        """결과를 파일로 저장"""
        try:
            # test_results 디렉토리 생성
            results_dir = Path('test_results')
            results_dir.mkdir(exist_ok=True)

            # 파일명 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"successful_apis_test_{timestamp}.json"
            filepath = results_dir / filename

            # 결과 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)

            print_success(f"결과 저장 완료: {filepath}")

        except Exception as e:
            print_error(f"결과 저장 실패: {e}")

    def run(self):
        """전체 테스트 실행"""
        # API 스펙 로드
        if not self.load_api_specs():
            return False

        # Client 초기화
        if not self.init_client():
            return False

        # 테스트 실행
        try:
            self.run_tests()
        except KeyboardInterrupt:
            print_warning("\n테스트가 중단되었습니다")
            return False
        except Exception as e:
            print_error(f"테스트 실행 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return False

        # 결과 출력
        self.print_summary()

        # 결과 저장
        self.save_results()

        return True


def main():
    """메인 함수"""
    tester = SuccessfulAPITester()
    success = tester.run()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
