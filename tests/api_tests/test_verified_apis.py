#!/usr/bin/env python3
"""
test_verified_apis.py
검증된 347개 API 호출을 실제로 재테스트
"""
import os
import sys
import requests
import json
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# credentials.py에서 API 키 로드
from config import get_credentials

class VerifiedAPITester:
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

        res = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        if res.status_code == 200:
            token_data = res.json()
            self.token = token_data.get('token')
            return True
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

    def test_verified_call(self, api_id, api_name, variant_idx, path, body):
        """검증된 호출 테스트"""
        response = self.request(api_id, body, path)

        result = {
            "api_id": api_id,
            "api_name": api_name,
            "variant_idx": variant_idx,
            "path": path,
            "body": body,
            "return_code": response.get('return_code'),
            "return_msg": response.get('return_msg', ''),
            "status": "unknown"
        }

        if response.get('return_code') == 0:
            # 데이터 확인
            keys = [k for k in response.keys() if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]
            data_count = 0
            data_key = None

            for key in keys:
                value = response.get(key)
                if isinstance(value, list) and len(value) > 0:
                    data_count = len(value)
                    data_key = key
                    break

            result["data_count"] = data_count
            result["data_key"] = data_key

            if data_count > 0:
                result["status"] = "success"
            else:
                result["status"] = "no_data"
        elif response.get('return_code') == 20:
            result["status"] = "no_data"
        else:
            result["status"] = "error"

        return result

    def run_all_verified_tests(self):
        """모든 검증된 API 호출 테스트"""
        # verified_api_calls.json 로드
        verified_file = Path("verified_api_calls.json")
        if not verified_file.exists():
            print(f"❌ {verified_file} 파일이 없습니다.")
            return

        with open(verified_file, 'r', encoding='utf-8') as f:
            verified_calls = json.load(f)

        total_calls = sum(len(info['verified_calls']) for info in verified_calls.values())
        print(f"\n총 {len(verified_calls)}개 API, {total_calls}개 검증된 호출 테스트 시작\n")

        success_count = 0
        no_data_count = 0
        error_count = 0
        test_num = 0

        for api_id, info in verified_calls.items():
            api_name = info['api_name']
            verified_items = info['verified_calls']

            print(f"[{api_id}] {api_name} - {len(verified_items)}개 호출")

            for item in verified_items:
                test_num += 1
                variant_idx = item['variant_idx']
                path = item['path']
                body = item['body']

                result = self.test_verified_call(api_id, api_name, variant_idx, path, body)
                self.results.append(result)

                status_symbol = {
                    "success": "✅",
                    "no_data": "⚠️",
                    "error": "❌"
                }.get(result["status"], "❓")

                data_info = ""
                if result["status"] == "success":
                    data_info = f" ({result['data_count']}개)"
                    success_count += 1
                elif result["status"] == "no_data":
                    no_data_count += 1
                else:
                    data_info = f" - {result['return_msg'][:50]}"
                    error_count += 1

                print(f"  {status_symbol} Var {variant_idx}: {result['status']}{data_info}")

        # 결과 저장
        output_file = f"verified_api_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print("\n" + "="*80)
        print("테스트 결과 요약")
        print("="*80)
        print(f"총 테스트: {total_calls}개")
        print(f"  ✅ 성공 (데이터 확인): {success_count}개 ({success_count/total_calls*100:.1f}%)")
        print(f"  ⚠️  성공 (데이터 없음): {no_data_count}개 ({no_data_count/total_calls*100:.1f}%)")
        print(f"  ❌ 실패: {error_count}개 ({error_count/total_calls*100:.1f}%)")
        print("="*80)
        print(f"\n💾 결과 저장: {output_file}")


def main():
    print("="*80)
    print("검증된 API 호출 재테스트")
    print("="*80)

    tester = VerifiedAPITester()

    print("\n[1] 토큰 발급")
    if not tester.get_token():
        print("❌ 토큰 발급 실패")
        sys.exit(1)
    print("✅ 토큰 발급 성공")

    print("\n[2] 검증된 API 테스트 시작")
    tester.run_all_verified_tests()

    print("\n" + "="*80)
    print("테스트 완료!")
    print("="*80)


if __name__ == "__main__":
    main()
