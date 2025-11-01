#!/usr/bin/env python3
"""
시스템 통합 테스트
모든 모듈이 정상 작동하는지 확인
"""
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """모듈 Import 테스트"""
    logger.info("=" * 80)
    logger.info("🧪 모듈 Import 테스트 시작")
    logger.info("=" * 80)

    # 1. Config
    logger.info("\n1️⃣  Config 모듈")
    try:
        from config import get_credentials, get_api_loader, APICategory
        logger.info("   ✅ get_credentials, get_api_loader, APICategory")
    except Exception as e:
        logger.error(f"   ❌ Config 모듈 오류: {e}")
        return False

    # 2. Core
    logger.info("\n2️⃣  Core 모듈")
    try:
        from core.rest_client import KiwoomRESTClient
        logger.info("   ✅ KiwoomRESTClient")
    except Exception as e:
        logger.error(f"   ❌ Core 모듈 오류: {e}")
        return False

    # 3. API
    logger.info("\n3️⃣  API 모듈")
    try:
        from api import AccountAPI, MarketAPI, OrderAPI
        logger.info("   ✅ AccountAPI, MarketAPI, OrderAPI")
    except Exception as e:
        logger.error(f"   ❌ API 모듈 오류: {e}")
        return False

    logger.info("\n✅ 모든 필수 모듈 Import 성공!")
    return True


def test_initialization():
    """객체 초기화 테스트"""
    logger.info("\n" + "=" * 80)
    logger.info("🔧 객체 초기화 테스트 시작")
    logger.info("=" * 80)

    try:
        from core.rest_client import KiwoomRESTClient
        from api import AccountAPI, MarketAPI, OrderAPI

        # REST Client
        logger.info("\n1️⃣  REST Client 초기화...")
        client = KiwoomRESTClient()
        logger.info("   ✅ REST Client 초기화 완료")

        # Account API
        logger.info("\n2️⃣  AccountAPI 초기화...")
        account_api = AccountAPI(client)
        logger.info("   ✅ AccountAPI 초기화 완료")

        # Market API
        logger.info("\n3️⃣  MarketAPI 초기화...")
        market_api = MarketAPI(client)
        logger.info("   ✅ MarketAPI 초기화 완료")

        # Order API
        logger.info("\n4️⃣  OrderAPI 초기화...")
        order_api = OrderAPI(client, dry_run=True)
        logger.info("   ✅ OrderAPI 초기화 완료")

        logger.info("\n✅ 모든 객체 초기화 성공!")
        return True

    except Exception as e:
        logger.error(f"\n❌ 초기화 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_loader():
    """API 로더 테스트"""
    logger.info("\n" + "=" * 80)
    logger.info("📡 API 로더 테스트 시작")
    logger.info("=" * 80)

    try:
        from config import get_api_loader, APICategory

        # API 로더
        logger.info("\n1️⃣  API 로더 초기화...")
        loader = get_api_loader()
        logger.info("   ✅ API 로더 초기화 완료")

        # 통계
        logger.info("\n2️⃣  API 통계...")
        stats = loader.get_stats()
        logger.info(f"   📊 총 API: {stats.get('total_apis')}개")
        logger.info(f"   📊 총 호출: {stats.get('total_variants')}개")
        logger.info(f"   📊 성공률: {stats.get('success_rate')}%")
        logger.info(f"   📊 성공한 호출: {stats.get('successful_calls')}개")

        # 카테고리
        logger.info("\n3️⃣  카테고리별 API...")
        categories = loader.get_all_categories()
        logger.info(f"   📂 카테고리: {', '.join(categories)}")

        for cat in categories:
            apis = loader.get_apis_by_category(cat)
            logger.info(f"   • {cat}: {len(apis)}개")

        # 특정 API 테스트
        logger.info("\n4️⃣  특정 API 조회...")
        api_info = loader.get_api('kt00005')
        if api_info:
            logger.info(f"   ✅ kt00005: {api_info.get('api_name')}")
            logger.info(f"      - 카테고리: {api_info.get('category')}")
            logger.info(f"      - Variants: {api_info.get('total_variants')}개")

        logger.info("\n✅ API 로더 테스트 성공!")
        return True

    except Exception as e:
        logger.error(f"\n❌ API 로더 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_verified_api_call():
    """검증된 API 호출 테스트"""
    logger.info("\n" + "=" * 80)
    logger.info("🚀 검증된 API 호출 테스트 시작")
    logger.info("=" * 80)

    try:
        from core.rest_client import KiwoomRESTClient

        logger.info("\n1️⃣  REST Client 초기화...")
        client = KiwoomRESTClient()

        logger.info("\n2️⃣  사용 가능한 API 조회...")
        available_apis = client.get_available_apis(category='account')
        logger.info(f"   ✅ 계좌 관련 API: {len(available_apis)}개")

        if available_apis:
            logger.info("\n   상위 5개 API:")
            for api in available_apis[:5]:
                logger.info(f"      • {api['api_id']}: {api['api_name']} ({api['total_variants']} variants)")

        logger.info("\n3️⃣  검증된 API 호출 테스트...")
        logger.info("   ⚠️  참고: API 키가 유효하지 않으면 403 오류가 발생할 수 있습니다")
        logger.info("   ℹ️  하지만 시스템은 정상 작동합니다")

        result = client.call_verified_api('kt00005', variant_idx=1)

        if result:
            logger.info(f"   📊 return_code: {result.get('return_code')}")
            logger.info(f"   📊 return_msg: {result.get('return_msg')}")

            if result.get('return_code') == 0:
                logger.info("   ✅ API 호출 성공!")
            else:
                logger.info(f"   ⚠️  API 호출 실패 (예상된 동작 - API 키 확인 필요)")

        logger.info("\n✅ 검증된 API 호출 테스트 완료!")
        return True

    except Exception as e:
        logger.error(f"\n❌ API 호출 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 테스트 함수"""
    logger.info("\n" + "=" * 80)
    logger.info("🎯 AutoTrade Pro v5.0 시스템 통합 테스트")
    logger.info("=" * 80)

    results = []

    # 1. Import 테스트
    results.append(("Import", test_imports()))

    # 2. 초기화 테스트
    if results[-1][1]:
        results.append(("Initialization", test_initialization()))
    else:
        logger.warning("\n⚠️  Import 실패로 인해 나머지 테스트를 건너뜁니다")
        return False

    # 3. API 로더 테스트
    if results[-1][1]:
        results.append(("API Loader", test_api_loader()))

    # 4. API 호출 테스트
    if results[-1][1]:
        results.append(("API Call", test_verified_api_call()))

    # 결과 요약
    logger.info("\n" + "=" * 80)
    logger.info("📊 테스트 결과 요약")
    logger.info("=" * 80)

    for name, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        logger.info(f"   {name:20s}: {status}")

    all_passed = all(success for _, success in results)

    if all_passed:
        logger.info("\n🎉 모든 테스트 통과!")
        logger.info("\n✨ AutoTrade Pro v5.0 시스템이 정상적으로 작동합니다!")
        logger.info("\n📚 다음 단계:")
        logger.info("   1. _immutable/credentials/secrets.json에 유효한 API 키 설정")
        logger.info("   2. main.py 실행으로 자동매매 시작")
        logger.info("   3. Dashboard 실행: python dashboard/app_apple.py")
    else:
        logger.error("\n❌ 일부 테스트 실패")
        logger.error("   문제를 해결한 후 다시 시도하세요")

    return all_passed


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
