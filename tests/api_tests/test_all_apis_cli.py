"""
comprehensive_api_debugger.py의 GUI 없는 CLI 버전
모든 Kiwoom REST API를 자동으로 테스트하고 결과를 저장합니다.
"""
import sys
import logging
import json
import datetime
import traceback
import time
from typing import Dict, Any, List, Tuple

try:
    from core.rest_client import KiwoomRESTClient
    import config
    from api import account
except ImportError as e:
    print(f"오류: 필수 모듈(core.rest_client, config, api.account)을 찾을 수 없습니다. {e}")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("CLI-Tester")

class APITesterCLI:
    """CLI 기반 API 테스터"""

    def __init__(self):
        self.api_client = None
        self.client_init_success = False
        self.test_results = []
        self.total_tests = 0
        self.total_variants = 0

        self.api_categories = {
            "계좌": ["kt00005", "kt00018", "ka10085", "ka10075", "ka10076", "kt00001", "kt00004", "kt00010", "kt00011", "kt00012", "kt00013", "ka10077", "ka10074", "ka10073", "ka10072", "ka01690", "kt00007", "kt00009", "kt00015", "kt00017", "kt00002", "kt00003", "kt00008", "kt00016", "ka10088", "ka10170"],
            "기본시세": ["ka10001", "ka10004", "ka10003", "ka10007", "ka10087", "ka10006", "ka10005"],
            "상세시세/분석": ["ka10059", "ka10061", "ka10015", "ka10043", "ka10002", "ka10013", "ka10025", "ka10026", "ka10045", "ka10046", "ka10047", "ka10052", "ka10054", "ka10055", "ka10063", "ka10066", "ka10078", "ka10086", "ka10095", "ka10099", "ka10100", "ka10101", "ka10102", "ka10084"],
            "차트": ["ka10079", "ka10080", "ka10081", "ka10082", "ka10083", "ka10094", "ka10060", "ka10064"],
            "기본순위": ["ka10027", "ka10017", "ka10032", "ka10031", "ka10023", "ka10016", "ka00198"],
            "상세순위": ["ka10020", "ka10021", "ka10022", "ka10019", "ka10028", "ka10018", "ka10029", "ka10033", "ka10098"],
            "업종/테마": ["ka20001", "ka20002", "ka20003", "ka20009", "ka10010", "ka10051", "ka90001", "ka90002"],
            "수급/대차": ["ka10008", "ka10009", "ka10131", "ka10034", "ka10035", "ka10036", "ka10037", "ka10038", "ka10039", "ka10040", "ka10042", "ka10053", "ka10058", "ka10062", "ka10065", "ka90009", "ka90004", "ka90005", "ka90007", "ka90008", "ka90013", "ka10014", "ka10068", "ka10069", "ka20068", "ka90012"],
            "ELW/ETF/금": ["ka10048", "ka10050", "ka30001", "ka30002", "ka30003", "ka30004", "ka30005", "ka30009", "ka30010", "ka30011", "ka30012", "ka40001", "ka40002", "ka40003", "ka40004", "ka40006", "ka40007", "ka40008", "ka40009", "ka40010", "ka50010", "ka50012", "ka50087", "ka50100", "ka50101", "ka52301", "kt50020", "kt50021", "kt50030", "kt50031", "kt50032", "kt50075"],
        }

        self.exclude_api_ids = {
            "kt10000", "kt10001", "kt10002", "kt10003", "kt10006", "kt10007", "kt10008", "kt10009",
            "kt50000", "kt50001", "kt50002", "kt50003",
            "ka10171", "ka10172", "ka10173", "ka10174",
            "00", "04", "0A", "0B", "0C", "0D", "0E", "0F", "0G", "0H", "OI", "OJ", "OU", "0g", "Om", "Os", "Ou", "Ow", "1h"
        }

    def init_api_client(self):
        """API 클라이언트 초기화"""
        logger.info("API 클라이언트 초기화 시작...")
        try:
            self.api_client = KiwoomRESTClient()

            if self.api_client.token and self.api_client.last_error_msg is None:
                logger.info("✅ API 클라이언트 준비 완료")
                self.client_init_success = True
                return True
            else:
                err_msg = getattr(self.api_client, 'last_error_msg', "알 수 없는 토큰 오류")
                logger.error(f"❌ API 클라이언트 초기화 실패: {err_msg}")
                return False
        except Exception as e:
            logger.critical(f"❌ API 클라이언트 초기화 중 치명적 오류: {e}")
            logger.debug(traceback.format_exc())
            return False

    def get_common_params(self) -> Dict[str, str]:
        """공통 파라미터 생성 (account.py 기반)"""
        params = account.p_common.copy()

        today = datetime.date.today()
        params["today_str"] = today.strftime("%Y%m%d")
        params["start_dt"] = (today - datetime.timedelta(days=7)).strftime("%Y%m%d")
        params["end_dt"] = today.strftime("%Y%m%d")
        params["base_dt"] = params["end_dt"]

        if 'one_day_ago_str' not in params:
            params['one_day_ago_str'] = (today - datetime.timedelta(days=1)).strftime('%Y%m%d')

        return params

    def test_single_api(self, api_id: str, common_params: Dict[str, str]) -> List[Dict]:
        """단일 API 테스트"""
        results = []

        try:
            func = account.get_api_definition(api_id)
            if not func:
                logger.warning(f"⚪ '{api_id}' 정의 없음 - 건너뜀")
                return [{"api_id": api_id, "status": "skipped", "reason": "정의 없음"}]

            variants = func(common_params)
            if not variants:
                logger.debug(f"⚪ '{api_id}' 빈 정의 - 건너뜀")
                return [{"api_id": api_id, "status": "skipped", "reason": "빈 정의 (WS/실시간 등)"}]

            if not isinstance(variants, list):
                logger.error(f"❌ '{api_id}' Variants가 리스트가 아님")
                return [{"api_id": api_id, "status": "error", "reason": "Variants 타입 오류"}]

        except Exception as e:
            logger.error(f"❌ '{api_id}' Variant 생성 오류: {e}")
            return [{"api_id": api_id, "status": "error", "reason": f"Variant 생성 오류: {e}"}]

        logger.info(f"  -> '{api_id}' 테스트 시작 ({len(variants)} variants)")

        for idx, (path_prefix, body) in enumerate(variants):
            variant_idx = idx + 1
            result = {
                "api_id": api_id,
                "variant_idx": variant_idx,
                "total_variants": len(variants),
                "path": path_prefix,
                "body": body,
                "status": "unknown",
                "return_code": None,
                "return_msg": None,
                "data_keys": [],
                "data_count": 0,
                "timestamp": datetime.datetime.now().isoformat()
            }

            try:
                response = self.api_client.request(
                    api_id=api_id,
                    body=body,
                    path_prefix=path_prefix
                )

                if isinstance(response, dict):
                    rc = response.get('return_code')
                    rm = response.get('return_msg', '')
                    result["return_code"] = rc
                    result["return_msg"] = rm

                    data_keys = [k for k in response.keys() if k not in ['return_code', 'return_msg', 'api-id', 'cont-yn', 'next-key']]
                    result["data_keys"] = data_keys

                    for key in data_keys:
                        val = response.get(key)
                        if isinstance(val, list):
                            result["data_count"] += len(val)

                    if rc == 0:
                        if result["data_count"] > 0 or any(response.get(k) for k in data_keys):
                            result["status"] = "success"
                            logger.info(f"    ✅ Var {variant_idx}/{len(variants)} 성공 (데이터: {result['data_count']})")
                        else:
                            result["status"] = "no_data"
                            logger.warning(f"    ⚠️ Var {variant_idx}/{len(variants)} 성공 (데이터 없음)")
                    elif rc == 20:
                        result["status"] = "no_data"
                        logger.warning(f"    ⚠️ Var {variant_idx}/{len(variants)} 데이터 없음: {rm}")
                    else:
                        result["status"] = "api_error"
                        logger.error(f"    ❌ Var {variant_idx}/{len(variants)} API 오류 (Code {rc}): {rm}")
                else:
                    result["status"] = "error"
                    result["return_msg"] = f"예상치 못한 응답 타입: {type(response)}"
                    logger.error(f"    ❌ Var {variant_idx}/{len(variants)} 응답 타입 오류")

            except Exception as e:
                result["status"] = "exception"
                result["return_msg"] = f"예외 발생: {e}"
                logger.error(f"    ❌ Var {variant_idx}/{len(variants)} 예외: {e}")

            results.append(result)
            time.sleep(0.05)

        return results

    def run_all_tests(self):
        """모든 API 테스트 실행"""
        if not self.client_init_success:
            logger.error("API 클라이언트가 준비되지 않았습니다.")
            return

        logger.info("="*80)
        logger.info("🚀 모든 조회 API 테스트 시작")
        logger.info("="*80)

        common_params = self.get_common_params()

        for category, api_ids in self.api_categories.items():
            logger.info(f"\n📁 카테고리: {category}")
            logger.info("-"*80)

            for api_id in api_ids:
                if api_id in self.exclude_api_ids:
                    logger.debug(f"  ⚪ '{api_id}' 건너뜀 (주문/WS/실시간 API)")
                    self.test_results.append({
                        "api_id": api_id,
                        "category": category,
                        "status": "skipped",
                        "reason": "자동 실행 제외 (주문/WS/실시간)"
                    })
                    continue

                results = self.test_single_api(api_id, common_params)
                for result in results:
                    result["category"] = category
                    self.test_results.append(result)

                time.sleep(0.1)

        logger.info("\n" + "="*80)
        logger.info("✅ 모든 테스트 완료")
        logger.info("="*80)

    def generate_summary(self) -> Dict:
        """테스트 결과 요약 생성"""
        summary = {
            "timestamp": datetime.datetime.now().isoformat(),
            "total_apis": len(set(r["api_id"] for r in self.test_results)),
            "total_variants": len([r for r in self.test_results if r.get("variant_idx")]),
            "stats": {
                "success": 0,
                "no_data": 0,
                "api_error": 0,
                "exception": 0,
                "skipped": 0,
                "error": 0
            },
            "by_category": {}
        }

        for result in self.test_results:
            status = result.get("status", "unknown")
            if status in summary["stats"]:
                summary["stats"][status] += 1

            category = result.get("category", "Unknown")
            if category not in summary["by_category"]:
                summary["by_category"][category] = {
                    "total": 0,
                    "success": 0,
                    "no_data": 0,
                    "failed": 0,
                    "skipped": 0
                }

            summary["by_category"][category]["total"] += 1
            if status == "success":
                summary["by_category"][category]["success"] += 1
            elif status == "no_data":
                summary["by_category"][category]["no_data"] += 1
            elif status == "skipped":
                summary["by_category"][category]["skipped"] += 1
            else:
                summary["by_category"][category]["failed"] += 1

        return summary

    def save_results(self, output_file: str = "api_test_results.json"):
        """결과를 JSON 파일로 저장"""
        output = {
            "summary": self.generate_summary(),
            "results": self.test_results
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        logger.info(f"\n📝 결과 저장 완료: {output_file}")

    def print_summary(self):
        """요약 출력"""
        summary = self.generate_summary()

        logger.info("\n" + "="*80)
        logger.info("📊 테스트 결과 요약")
        logger.info("="*80)
        logger.info(f"총 API 수: {summary['total_apis']}")
        logger.info(f"총 Variant 수: {summary['total_variants']}")
        logger.info(f"\n상태별:")
        logger.info(f"  ✅ 성공 (데이터 확인): {summary['stats']['success']}")
        logger.info(f"  ⚠️  성공 (데이터 없음): {summary['stats']['no_data']}")
        logger.info(f"  ❌ API 오류: {summary['stats']['api_error']}")
        logger.info(f"  ❌ 예외 발생: {summary['stats']['exception']}")
        logger.info(f"  ❌ 기타 오류: {summary['stats']['error']}")
        logger.info(f"  ⚪ 건너뜀: {summary['stats']['skipped']}")

        logger.info(f"\n카테고리별:")
        for category, stats in summary['by_category'].items():
            logger.info(f"  {category}:")
            logger.info(f"    총: {stats['total']}, 성공: {stats['success']}, 데이터없음: {stats['no_data']}, 실패: {stats['failed']}, 건너뜀: {stats['skipped']}")

        logger.info("="*80)


def main():
    """메인 실행"""
    logger.info("CLI 기반 Kiwoom REST API 전체 테스트 시작")
    logger.info("="*80)

    tester = APITesterCLI()

    if not tester.init_api_client():
        logger.error("API 클라이언트 초기화 실패. 종료합니다.")
        sys.exit(1)

    tester.run_all_tests()

    tester.print_summary()

    output_file = f"api_test_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    tester.save_results(output_file)

    logger.info("\n✅ 모든 작업 완료!")


if __name__ == "__main__":
    main()
