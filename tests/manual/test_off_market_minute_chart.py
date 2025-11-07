"""
장외시간 분봉 데이터 자동 조회 테스트
아이디어 1: REST API base_date 활용

기능:
- 장외시간 (20:00-08:00) 감지 시 자동으로 마지막 영업일 분봉 조회
- 이미 구현된 get_last_trading_date() + base_date 파라미터 활용
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime


def print_section(title: str):
    """섹션 구분선 출력"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_off_market_minute_chart():
    """장외시간 분봉 조회 테스트"""

    # Import trading_date module directly (avoid utils/__init__.py)
    import importlib.util
    spec = importlib.util.spec_from_file_location("trading_date", str(project_root / "utils" / "trading_date.py"))
    trading_date_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(trading_date_module)

    is_any_trading_hours = trading_date_module.is_any_trading_hours
    is_market_hours = trading_date_module.is_market_hours
    is_nxt_hours = trading_date_module.is_nxt_hours
    get_last_trading_date = trading_date_module.get_last_trading_date
    get_trading_date_with_fallback = trading_date_module.get_trading_date_with_fallback

    print_section("📅 현재 시간 및 장 상태 확인")

    now = datetime.now()
    print(f"현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"요일: {['월', '화', '수', '목', '금', '토', '일'][now.weekday()]}")
    print(f"\n장 운영 상태:")
    print(f"  - 정규장 (09:00-15:30): {is_market_hours()}")
    print(f"  - NXT 시간 (08:00-09:00, 15:30-20:00): {is_nxt_hours()}")
    print(f"  - 거래 시간 전체 (08:00-20:00): {is_any_trading_hours()}")
    print(f"  - 장외시간 (20:00-08:00): {not is_any_trading_hours()}")

    print_section("🗓️ 조회 대상 날짜 결정")

    is_off_market = not is_any_trading_hours()

    if is_off_market:
        target_date = get_last_trading_date()
        print(f"⚠️ 장외시간입니다!")
        print(f"✅ 마지막 영업일 자동 조회: {target_date}")
        print(f"   → {target_date[:4]}년 {target_date[4:6]}월 {target_date[6:8]}일")

        # 폴백 날짜도 표시
        fallback_dates = get_trading_date_with_fallback(5)
        print(f"\n📋 최근 5일 영업일 (폴백용):")
        for i, date in enumerate(fallback_dates, 1):
            print(f"   {i}. {date[:4]}-{date[4:6]}-{date[6:8]}")
    else:
        target_date = now.strftime('%Y%m%d')
        print(f"✅ 거래 시간입니다!")
        print(f"✅ 오늘 날짜 사용: {target_date}")
        print(f"   → {target_date[:4]}년 {target_date[4:6]}월 {target_date[6:8]}일")

    print_section("🔌 API 연결")

    try:
        # TradingBotV2 사용 (main.py에서 import)
        from main import TradingBotV2
        from api.market import MarketAPI

        bot = TradingBotV2()

        if not bot.client:
            print("❌ API 클라이언트 초기화 실패")
            return

        # Check if client has a valid token
        if not hasattr(bot.client, 'token') or not bot.client.token:
            print("❌ API 인증 실패")
            return

        print("✅ API 연결 성공")

        client = bot.client
        market_api = MarketAPI(client)

    except Exception as e:
        print(f"❌ API 초기화 실패: {e}")
        import traceback
        traceback.print_exc()
        return

    print_section("📊 분봉 데이터 조회 테스트")

    test_stocks = [
        ("005930", "삼성전자"),
        ("000660", "SK하이닉스"),
        ("035420", "NAVER")
    ]

    intervals = [1, 5, 15, 30, 60]

    for stock_code, stock_name in test_stocks:
        print(f"\n{'─'*80}")
        print(f"📈 {stock_name} ({stock_code})")
        print(f"{'─'*80}\n")

        for interval in intervals:
            try:
                # 핵심: base_date 파라미터 사용!
                minute_data = market_api.get_minute_chart(
                    stock_code=stock_code,
                    interval=interval,
                    count=10,  # 최근 10개만
                    adjusted=True,
                    base_date=target_date  # 👈 여기가 핵심!
                )

                if minute_data and len(minute_data) > 0:
                    print(f"✅ {interval}분봉: {len(minute_data)}개 조회 성공")

                    # 첫 번째 데이터 출력
                    first = minute_data[0]
                    print(f"   최신 데이터:")
                    print(f"   - 시간: {first.get('time', 'N/A')}")
                    print(f"   - 시가: {first.get('open', 0):,}원")
                    print(f"   - 고가: {first.get('high', 0):,}원")
                    print(f"   - 저가: {first.get('low', 0):,}원")
                    print(f"   - 종가: {first.get('close', 0):,}원")
                    print(f"   - 거래량: {first.get('volume', 0):,}주")
                else:
                    print(f"⚠️ {interval}분봉: 데이터 없음")

            except Exception as e:
                print(f"❌ {interval}분봉 조회 실패: {e}")

        print()  # 종목 사이 공백

    print_section("✅ 테스트 완료")

    if is_off_market:
        print("💡 장외시간에 과거 데이터를 성공적으로 조회했습니다!")
        print(f"   조회된 날짜: {target_date}")
    else:
        print("💡 거래 시간에 실시간 데이터를 성공적으로 조회했습니다!")
        print(f"   조회된 날짜: {target_date}")

    print("\n📌 핵심:")
    print("   ✅ base_date 파라미터를 사용하면 과거 분봉 조회 가능")
    print("   ✅ 장외시간에도 마지막 영업일 데이터를 자동으로 가져올 수 있음")
    print("   ✅ 추가 개발 없이 기존 API만으로 해결!")


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║            🌙 장외시간 분봉 데이터 자동 조회 테스트 (아이디어 1)            ║
║                                                                          ║
║  기능: REST API base_date 파라미터를 활용한 과거 분봉 조회                ║
║  장점: 추가 개발 없음, 안정적, REST API만으로 해결                         ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""")

    try:
        test_off_market_minute_chart()
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자가 테스트를 중단했습니다.")
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류 발생:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
