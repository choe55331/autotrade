키움 순위 API 전체 테스트 및 응답 구조 문서화

23개 순위 API를 모두 테스트하고 응답 구조를 JSON 파일로 저장합니다.
import os
import sys
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import get_credentials

class KiwoomAPITester:
    def __init__(self):
        credentials = get_credentials()
        kiwoom_config = credentials.get_kiwoom_config()

        self.base_url = kiwoom_config['base_url']
        self.appkey = kiwoom_config['appkey']
        self.secretkey = kiwoom_config['secretkey']
        self.token = None
        self.results = {}

    def get_token(self):
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

    def request(self, api_id, body):
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.token}",
            "api-id": api_id
        }
        url = f"{self.base_url}/api/dostk/rkinfo"

        try:
            res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return None

    def test_api(self, api_id, name, body):
        """API 테스트 및 결과 저장"""
        print(f"  테스트: {api_id} - {name}")
        response = self.request(api_id, body)

        if response and response.get('return_code') == 0:
            keys = list(response.keys())
            data_keys = [k for k in keys if k not in ['return_code', 'return_msg']]

            data_count = 0
            data_key = None
            sample_data = None

            for key in data_keys:
                value = response.get(key)
                if isinstance(value, list) and len(value) > 0:
                    data_count = len(value)
                    data_key = key
                    sample_data = value[0]
                    break

            result = {
                "api_id": api_id,
                "name": name,
                "status": "success",
                "return_code": response.get('return_code'),
                "return_msg": response.get('return_msg'),
                "response_keys": keys,
                "data_key": data_key,
                "data_count": data_count,
                "sample_data": sample_data,
                "request_body": body
            }

            print(f"    ✅ 성공: {data_count}개 데이터 (키: {data_key})")
        else:
            result = {
                "api_id": api_id,
                "name": name,
                "status": "failed",
                "return_code": response.get('return_code') if response else None,
                "return_msg": response.get('return_msg') if response else "No response",
                "request_body": body
            }
            print(f"    ❌ 실패: {result['return_msg']}")

        self.results[api_id] = result
        return result

TEST_CASES = [
    ("ka10020", "호가잔량상위요청", {
        "mrkt_tp": "0", "sort_tp": "0", "trde_qty_tp": "0",
        "stk_cnd": "0", "crd_cnd": "0", "stex_tp": "1"
    }),
    ("ka10021", "호가잔량급증요청", {
        "mrkt_tp": "0", "trde_tp": "0", "sort_tp": "0",
        "trde_qty_tp": "0", "stk_cnd": "0", "stex_tp": "1", "tm_tp": "10"
    }),
    ("ka10022", "잔량율급증요청", {
        "mrkt_tp": "0", "rt_tp": "0", "trde_qty_tp": "0",
        "stk_cnd": "0", "stex_tp": "1", "tm_tp": "10"
    }),
    ("ka10023", "거래량급증요청", {
        "mrkt_tp": "0", "sort_tp": "0", "tm_tp": "0",
        "trde_qty_tp": "0", "stk_cnd": "0", "pric_tp": "0",
        "stex_tp": "1", "tm": "10"
    }),
    ("ka10027", "전일대비등락률상위요청", {
        "mrkt_tp": "0", "sort_tp": "0", "trde_qty_cnd": "0",
        "stk_cnd": "0", "crd_cnd": "0", "updown_incls": "1",
        "pric_cnd": "0", "trde_prica_cnd": "0", "stex_tp": "1"
    }),
    ("ka10029", "예상체결등락률상위요청", {
        "mrkt_tp": "0", "sort_tp": "0", "trde_qty_cnd": "0",
        "stk_cnd": "0", "crd_cnd": "0", "pric_cnd": "0", "stex_tp": "1"
    }),
    ("ka10030", "당일거래량상위요청", {
        "mrkt_tp": "0", "sort_tp": "0", "mang_stk_incls": "0",
        "crd_tp": "0", "trde_qty_tp": "0", "pric_tp": "0",
        "trde_prica_tp": "0", "mrkt_open_tp": "0", "stex_tp": "1"
    }),
    ("ka10031", "전일거래량상위요청", {
        "mrkt_tp": "0", "qry_tp": "0", "stex_tp": "1",
        "rank_strt": "1", "rank_end": "20"
    }),
    ("ka10032", "거래대금상위요청", {
        "mrkt_tp": "0", "mang_stk_incls": "0", "stex_tp": "1"
    }),
    ("ka10033", "신용비율상위요청", {
        "mrkt_tp": "0", "trde_qty_tp": "0", "stk_cnd": "0",
        "updown_incls": "1", "crd_cnd": "0", "stex_tp": "1"
    }),
    ("ka10034", "외인기간별매매상위요청", {
        "mrkt_tp": "0", "trde_tp": "0", "stex_tp": "1", "dt": "1"
    }),
    ("ka10035", "외인연속순매매상위요청", {
        "mrkt_tp": "0", "trde_tp": "0", "stex_tp": "1", "base_dt_tp": "3"
    }),
    ("ka10036", "외인한도소진율증가상위", {
        "mrkt_tp": "0", "stex_tp": "1", "dt": "1"
    }),
    ("ka10037", "외국계창구매매상위요청", {
        "mrkt_tp": "0", "trde_tp": "0", "sort_tp": "0",
        "stex_tp": "1", "dt": "1"
    }),
    ("ka10038", "종목별증권사순위요청", {
        "qry_tp": "0", "stk_cd": "005930",
        "strt_dt": (datetime.now() - timedelta(days=7)).strftime("%Y%m%d"),
        "end_dt": datetime.now().strftime("%Y%m%d"), "dt": "0"
    }),
    ("ka10039", "증권사별매매상위요청", {
        "trde_qty_tp": "0", "trde_tp": "0", "stex_tp": "1",
        "mmcm_cd": "", "dt": "1"
    }),
    ("ka10040", "당일주요거래원요청", {
        "stk_cd": "005930"
    }),
    ("ka10042", "순매수거래원순위요청", {
        "qry_dt_tp": "0", "pot_tp": "0", "sort_base": "0", "stk_cd": ""
    }),
    ("ka10053", "당일상위이탈원요청", {
        "stk_cd": "005930"
    }),
    ("ka10062", "동일순매매순위요청", {
        "mrkt_tp": "0", "trde_tp": "0", "sort_cnd": "0",
        "unit_tp": "0", "stex_tp": "1",
        "strt_dt": (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
    }),
    ("ka10065", "장중투자자별매매상위요청", {
        "mrkt_tp": "0", "trde_tp": "0", "orgn_tp": "0"
    }),
    ("ka10098", "시간외단일가등락율순위요청", {
        "mrkt_tp": "0", "sort_base": "0", "stk_cnd": "0",
        "trde_qty_cnd": "0", "crd_cnd": "0", "trde_prica": "0"
    }),
    ("ka90009", "외국인기관매매상위요청", {
        "mrkt_tp": "0", "amt_qty_tp": "0", "qry_dt_tp": "0", "stex_tp": "1"
    }),
]

print("="*70)
print("키움 순위 API 전체 테스트")
print("="*70)

tester = KiwoomAPITester()
print("\n[1] 토큰 발급")
if not tester.get_token():
    print("❌ 토큰 발급 실패")
    sys.exit(1)
print("✅ 토큰 발급 성공\n")

print("[2] API 테스트 시작")
for api_id, name, body in TEST_CASES:
    tester.test_api(api_id, name, body)

print("\n" + "="*70)
print("테스트 결과 요약")
print("="*70)

success_count = sum(1 for r in tester.results.values() if r['status'] == 'success')
failed_count = len(tester.results) - success_count

print(f"\n총 {len(tester.results)}개 API 테스트")
print(f"  ✅ 성공: {success_count}개")
print(f"  ❌ 실패: {failed_count}개")

print(f"\n📋 데이터 키 요약:")
for api_id, result in tester.results.items():
    if result['status'] == 'success' and result['data_key']:
        print(f"  {api_id}: '{result['data_key']}' ({result['data_count']}개)")

output_file = "kiwoom_api_test_results.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(tester.results, f, indent=2, ensure_ascii=False)

print(f"\n💾 전체 결과 저장: {output_file}")

spec_file = "kiwoom_api_response_spec.json"
spec = {}
for api_id, result in tester.results.items():
    if result['status'] == 'success':
        spec[api_id] = {
            "name": result['name'],
            "data_key": result['data_key'],
            "response_keys": result['response_keys'],
            "sample_fields": list(result['sample_data'].keys()) if result['sample_data'] else []
        }

with open(spec_file, 'w', encoding='utf-8') as f:
    json.dump(spec, f, indent=2, ensure_ascii=False)

print(f"💾 응답 구조 명세 저장: {spec_file}")

print("\n" + "="*70)
print("테스트 완료!")
print("="*70)
