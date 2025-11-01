"""
테스트: 거래일 계산 로직 검증
"""
from utils.trading_date import (
    get_last_trading_date,
    get_trading_date_with_fallback,
    is_market_hours,
    is_after_market_hours
)
from datetime import datetime

print("="*60)
print("거래일 계산 테스트")
print("="*60)

# 현재 시간 정보
now = datetime.now()
print(f"\n현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"요일: {['월', '화', '수', '목', '금', '토', '일'][now.weekday()]}")

# 최근 거래일 계산
trading_date = get_last_trading_date()
print(f"\n최근 거래일: {trading_date}")

# 장 시간 확인
print(f"\n장 운영 시간: {is_market_hours()}")
print(f"장 마감 후: {is_after_market_hours()}")

# 폴백 날짜 리스트
fallback_dates = get_trading_date_with_fallback(5)
print(f"\n최근 5개 거래일:")
for i, date in enumerate(fallback_dates, 1):
    print(f"  {i}. {date}")

print("\n" + "="*60)
print("테스트 완료!")
print("="*60)
