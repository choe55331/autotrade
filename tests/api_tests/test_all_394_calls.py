test_all_394_calls.py
로그에서 추출한 394개 API 호출 모두 테스트

실행 시간: 오전 8시 ~ 오후 8시 (12시간)
- 장 시작 전: 8:00-9:00 (일부 API 테스트 가능)
- 장중: 9:00-15:30 (대부분 API 테스트 가능)
- 장 마감 후: 15:30-20:00 (일부 API 테스트 가능)
import os
import sys
import requests
import json
from datetime import datetime, time
from pathlib import Path
import time as time_module

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import get_credentials

class All394APITester:
    def __init__(self):
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
                    return True
            return False
        except Exception as e:
            print(f"토큰 발급 실패: {e}")
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

    def test_single_call(self, api_id, api_name, variant_idx, path, body, original_status):
        """단일 API 호출 테스트"""
        response = self.request(api_id, body, path)

        result = {
            "api_id": api_id,
            "api_name": api_name,
            "variant_idx": variant_idx,
            "path": path,
            "body": body,
            "original_status": original_status,
            "return_code": response.get('return_code'),
            "return_msg": response.get('return_msg', ''),
            "current_status": "unknown"
        }

        if response.get('return_code') == 0:
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
                result["current_status"] = "success"
            else:
                result["current_status"] = "no_data"
        elif response.get('return_code') == 20:
            result["current_status"] = "no_data"
        else:
            result["current_status"] = "error"

        return result

    def run_all_394_tests(self):
        """394개 전체 API 호출 테스트"""
        api_file = Path("all_394_api_calls.json")
        if not api_file.exists():
            print(f"❌ {api_file} 파일이 없습니다.")
            print("먼저 extract_all_394_variants.py를 실행하세요.")
            return

        with open(api_file, 'r', encoding='utf-8') as f:
            all_api_calls = json.load(f)

        total_calls = sum(len(info['all_calls']) for info in all_api_calls.values())
        print(f"\n총 {len(all_api_calls)}개 API, {total_calls}개 호출 테스트 시작\n")

        success_count = 0
        no_data_count = 0
        error_count = 0

        changed_to_success = 0
        stayed_success = 0
        changed_to_error = 0

        test_num = 0

        for api_id, info in all_api_calls.items():
            api_name = info['api_name']
            all_calls = info['all_calls']

            print(f"[{api_id}] {api_name} - {len(all_calls)}개 호출")

            for call in all_calls:
                test_num += 1
                variant_idx = call['variant_idx']
                path = call['path']
                body = call['body']
                original_status = call['status']

                result = self.test_single_call(api_id, api_name, variant_idx, path, body, original_status)
                self.results.append(result)

                current_status = result["current_status"]

                status_symbol = {
                    "success": "✅",
                    "no_data": "⚠️",
                    "error": "❌"
                }.get(current_status, "❓")

                data_info = ""
                if current_status == "success":
                    data_info = f" ({result.get('data_count', 0)}개)"
                    success_count += 1

                    if original_status == "success":
                        stayed_success += 1
                    else:
                        changed_to_success += 1
                        data_info += f" [원래:{original_status}→성공!]"

                elif current_status == "no_data":
                    no_data_count += 1
                else:
                    data_info = f" - {result['return_msg'][:50]}"
                    error_count += 1

                    if original_status == "success":
                        changed_to_error += 1
                        data_info += " [원래:성공→실패]"

                print(f"  {status_symbol} Var {variant_idx}: {current_status}{data_info}")

                time_module.sleep(0.05)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"all_394_test_results_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print("\n" + "="*80)
        print("📊 테스트 결과 요약")
        print("="*80)
        print(f"총 테스트: {total_calls}개")
        print(f"  ✅ 성공 (데이터 확인): {success_count}개 ({success_count/total_calls*100:.1f}%)")
        print(f"  ⚠️  성공 (데이터 없음): {no_data_count}개 ({no_data_count/total_calls*100:.1f}%)")
        print(f"  ❌ 실패: {error_count}개 ({error_count/total_calls*100:.1f}%)")
        print()
        print("상태 변경:")
        print(f"  ✅ 성공 유지: {stayed_success}개")
        print(f"  🎉 실패→성공 변경: {changed_to_success}개")
        print(f"  ⚠️  성공→실패 변경: {changed_to_error}개")
        print("="*80)
        print(f"\n💾 결과 저장: {output_file}")


def check_time_allowed():
    """현재 시간이 실행 가능 시간인지 확인 (8:00~20:00)"""
    now = datetime.now().time()
    start_time = time(8, 0)
    end_time = time(20, 0)

    if start_time <= now <= end_time:
        return True, "실행 가능 시간대입니다."
    else:
        return False, f"실행 가능 시간: 08:00~20:00 (현재: {now.strftime('%H:%M')})"


def main():
    print("="*80)
    print("394개 전체 API 호출 테스트")
    print("="*80)

    allowed, msg = check_time_allowed()
    if not allowed:
        print(f"\n⏰ {msg}")
        print("프로그램은 오전 8시부터 오후 8시까지 실행 가능합니다.")
        sys.exit(0)

    print(f"⏰ {msg}")

    tester = All394APITester()

    print("\n[1] 토큰 발급")
    if not tester.get_token():
        print("❌ 토큰 발급 실패")
        print("\n가능한 원인:")
        print("  - API 키/시크릿키 오류")
        print("  - 네트워크 연결 오류")
        print("  - 키움 API 서버 점검")
        sys.exit(1)
    print("✅ 토큰 발급 성공")

    print("\n[2] 394개 API 호출 테스트 시작")
    print("(약 20분 소요 예상 - 394개 × 0.05초 간격)")

    start_time = datetime.now()
    tester.run_all_394_tests()
    end_time = datetime.now()

    elapsed = (end_time - start_time).total_seconds()
    print(f"\n⏱️  총 소요 시간: {elapsed:.1f}초 ({elapsed/60:.1f}분)")

    print("\n" + "="*80)
    print("✅ 전체 테스트 완료!")
    print("="*80)


if __name__ == "__main__":
    main()
