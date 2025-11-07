
import json
from pathlib import Path
import datetime

def convert_test_results_to_verified():
    """테스트 결과를 검증된 API 호출 형식으로 변환"""

    results_file = Path("kiwoom_api_test_results.json")
    output_file = Path("verified_api_calls.json")

    if not results_file.exists():
        print(f"[X] {results_file} 파일이 없습니다.")
        return

    with open(results_file, 'r', encoding='utf-8') as f:
        test_results = json.load(f)

    verified_calls = {}

    for api_id, result in test_results.items():
        if result.get("status") == "success" and result.get("data_count", 0) > 0:
            request_body = result.get("request_body", {})

            path = "rkinfo"
            if api_id.startswith("kt"):
                path = "acnt"
            elif api_id.startswith("ka10"):
                path = "rkinfo"
            elif api_id.startswith("ka20"):
                path = "sect"
            elif api_id.startswith("ka90"):
                path = "rkinfo"

            verified_calls[api_id] = {
                "api_name": result.get("name", api_id),
                "success_count": 1,
                "total_variants": 1,
                "verified_calls": [
                    {
                        "path": path,
                        "body": request_body,
                        "data_count": result.get("data_count", 0)
                    }
                ],
                "last_tested": datetime.datetime.now().isoformat(),
                "note": "Converted from kiwoom_api_test_results.json"
            }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(verified_calls, f, ensure_ascii=False, indent=2)

    print(f"[OK] {len(verified_calls)}개 검증된 API 호출을 {output_file}에 저장했습니다.")
    print(f"\n검증된 API 목록:")
    for api_id, info in sorted(verified_calls.items()):
        print(f"  - {api_id}: {info['api_name']} (데이터 {info['verified_calls'][0]['data_count']}개)")

if __name__ == "__main__":
    convert_test_results_to_verified()
